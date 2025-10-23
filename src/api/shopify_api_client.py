"""
Shopify GraphQL API Client for Product Upload System
Handles product creation, image uploads, and inventory management using GraphQL
"""

import requests
import logging
import time
import json
from typing import Dict, List, Optional, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ShopifyAPIClient:
    def __init__(self, shop_url: str, api_key: str, api_password: str):
        """
        Initialize Shopify GraphQL API client
        
        Args:
            shop_url (str): Shopify shop URL (e.g., 'your-shop.myshopify.com')
            api_key (str): Shopify API key
            api_password (str): Shopify API password
        """
        self.shop_url = shop_url.rstrip('/')
        self.api_key = api_key
        self.api_password = api_password
        self.graphql_url = f"https://{self.shop_url}/admin/api/2025-10/graphql.json"
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting for GraphQL
        self.rate_limit_remaining = 1000
        self.rate_limit_reset_time = 0
        
    def _make_graphql_request(self, query: str, variables: Optional[Dict] = None) -> Tuple[bool, Optional[Dict]]:
        """
        Make GraphQL API request with rate limiting and error handling
        
        Args:
            query (str): GraphQL query string
            variables (Optional[Dict]): GraphQL variables
            
        Returns:
            Tuple[bool, Optional[Dict]]: (success, response_data)
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Shopify-Access-Token': self.api_password
        }
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            # Check rate limiting
            self._check_rate_limit()
            
            # Make request
            response = requests.post(
                self.graphql_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Update rate limit info
            self._update_rate_limit_info(response.headers)
            
            # Handle response
            if response.status_code in [200, 201, 202]:
                response_data = response.json()
                
                # Check for GraphQL errors
                if 'errors' in response_data:
                    self.logger.error(f"GraphQL errors: {response_data['errors']}")
                    return False, response_data
                
                return True, response_data
            elif response.status_code == 429:  # Rate limited
                self.logger.warning("Rate limited. Waiting before retry...")
                time.sleep(2)
                return self._make_graphql_request(query, variables)
            else:
                self.logger.error(f"GraphQL request failed: {response.status_code} - {response.text}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GraphQL request error: {str(e)}")
            return False, None
    
    def _check_rate_limit(self):
        """Check and handle rate limiting"""
        current_time = time.time()
        if current_time < self.rate_limit_reset_time:
            wait_time = self.rate_limit_reset_time - current_time
            self.logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
    
    def _update_rate_limit_info(self, headers: Dict):
        """Update rate limit information from response headers"""
        if 'X-Shopify-Shop-Api-Call-Limit' in headers:
            self.rate_limit_remaining = int(headers['X-Shopify-Shop-Api-Call-Limit'].split('/')[0])
        if 'X-RateLimit-Reset' in headers:
            self.rate_limit_reset_time = int(headers['X-RateLimit-Reset'])
    
    def create_product(self, product_data: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Create a product in Shopify using GraphQL
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            Tuple[bool, Optional[Dict]]: (success, product_response)
        """
        try:
            # Prepare GraphQL mutation
            mutation = self._create_product_mutation()
            variables = self._prepare_product_variables(product_data)
            
            # Create product
            success, response = self._make_graphql_request(mutation, variables)
            
            if success and response:
                product_id = response['data']['productCreate']['product']['id']
                self.logger.info(f"Created product {product_data.get('sku', 'unknown')} with ID: {product_id}")
                
                # Handle images if provided
                if product_data.get('image_links'):
                    self._upload_product_images_graphql(product_id, product_data['image_links'])
                
                return True, response
            else:
                self.logger.error(f"Failed to create product {product_data.get('sku', 'unknown')}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"Error creating product {product_data.get('sku', 'unknown')}: {str(e)}")
            return False, None
    
    def _create_product_mutation(self) -> str:
        """Create GraphQL mutation for product creation"""
        return """
        mutation productCreate($input: ProductInput!) {
            productCreate(input: $input) {
                product {
                    id
                    title
                    handle
                    status
                    vendor
                    productType
                    createdAt
                    updatedAt
                    variants(first: 1) {
                        edges {
                            node {
                                id
                                sku
                                price
                                inventoryQuantity
                            }
                        }
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
    
    def _prepare_product_variables(self, product_data: Dict) -> Dict:
        """
        Prepare product data for GraphQL mutation
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            Dict: GraphQL variables
        """
        # Extract basic product information
        title = product_data.get('title', '')
        body_html = product_data.get('body_html', '')
        vendor = product_data.get('brand', '')
        product_type = product_data.get('category', '')
        price = str(product_data.get('price', '0'))
        sku = product_data.get('sku', '')
        quantity = int(product_data.get('quantity', 0))
        
        # Create variant
        variant = {
            'sku': sku,
            'price': price,
            'inventoryQuantity': quantity,
            'inventoryManagement': 'SHOPIFY',
            'inventoryPolicy': 'DENY'
        }
        
        # Add weight if available
        if product_data.get('weight'):
            variant['weight'] = float(product_data['weight'])
        
        # Create product input
        product_input = {
            'title': title,
            'descriptionHtml': body_html,
            'vendor': vendor,
            'productType': product_type,
            'variants': [variant],
            'status': 'ACTIVE',
            'published': True
        }
        
        # Add tags if available
        if product_data.get('tags'):
            product_input['tags'] = product_data['tags']
        
        # Add metafields if available
        metafields = []
        if product_data.get('features'):
            metafields.append({
                'namespace': 'custom',
                'key': 'features',
                'value': product_data['features'],
                'type': 'single_line_text_field'
            })
        if product_data.get('material'):
            metafields.append({
                'namespace': 'custom',
                'key': 'material',
                'value': product_data['material'],
                'type': 'single_line_text_field'
            })
        
        if metafields:
            product_input['metafields'] = metafields
        
        return {'input': product_input}
    
    def _upload_product_images_graphql(self, product_id: str, image_links: str) -> bool:
        """
        Upload images for a product using GraphQL
        
        Args:
            product_id (str): Shopify product ID
            image_links (str): Comma-separated image URLs
            
        Returns:
            bool: Success status
        """
        try:
            if not image_links or not image_links.strip():
                return True
            
            # Split image links
            image_urls = [url.strip() for url in image_links.split(',') if url.strip()]
            
            for i, image_url in enumerate(image_urls):
                if not image_url:
                    continue
                
                # Prepare image mutation
                mutation = """
                mutation productImageCreate($productId: ID!, $image: ImageInput!) {
                    productImageCreate(productId: $productId, image: $image) {
                        image {
                            id
                            url
                            altText
                        }
                        userErrors {
                            field
                            message
                        }
                    }
                }
                """
                
                variables = {
                    'productId': f"gid://shopify/Product/{product_id}",
                    'image': {
                        'src': image_url,
                        'altText': f"Product image {i+1}"
                    }
                }
                
                # Upload image
                success, response = self._make_graphql_request(mutation, variables)
                
                if success:
                    self.logger.info(f"Uploaded image {i+1} for product {product_id}")
                else:
                    self.logger.warning(f"Failed to upload image {i+1} for product {product_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error uploading images for product {product_id}: {str(e)}")
            return False
    
    def update_inventory(self, product_id: str, variant_id: str, quantity: int) -> bool:
        """
        Update inventory for a product variant using GraphQL
        
        Args:
            product_id (str): Shopify product ID
            variant_id (str): Shopify variant ID
            quantity (int): New inventory quantity
            
        Returns:
            bool: Success status
        """
        try:
            mutation = """
            mutation inventoryAdjustQuantities($input: InventoryAdjustQuantitiesInput!) {
                inventoryAdjustQuantities(input: $input) {
                    inventoryAdjustmentGroup {
                        id
                        reason
                        referenceDocumentUri
                        changes {
                            name
                            delta
                            item {
                                id
                                sku
                            }
                        }
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
            """
            
            variables = {
                'input': {
                    'reason': 'correction',
                    'name': f"Inventory adjustment for product {product_id}",
                    'changes': [{
                        'delta': quantity,
                        'inventoryItemId': f"gid://shopify/InventoryItem/{variant_id}"
                    }]
                }
            }
            
            success, response = self._make_graphql_request(mutation, variables)
            
            if success:
                self.logger.info(f"Updated inventory for product {product_id} to {quantity}")
                return True
            else:
                self.logger.error(f"Failed to update inventory for product {product_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating inventory for product {product_id}: {str(e)}")
            return False
    
    def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        """
        Get product by SKU using GraphQL
        
        Args:
            sku (str): Product SKU
            
        Returns:
            Optional[Dict]: Product data or None if not found
        """
        try:
            query = """
            query getProductBySku($sku: String!) {
                products(first: 1, query: $sku) {
                    edges {
                        node {
                            id
                            title
                            handle
                            status
                            vendor
                            productType
                            variants(first: 1) {
                                edges {
                                    node {
                                        id
                                        sku
                                        price
                                        inventoryQuantity
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            
            variables = {'sku': f"sku:{sku}"}
            success, response = self._make_graphql_request(query, variables)
            
            if success and response.get('data', {}).get('products', {}).get('edges'):
                return response['data']['products']['edges'][0]['node']
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting product by SKU {sku}: {str(e)}")
            return None
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product using GraphQL
        
        Args:
            product_id (str): Shopify product ID
            
        Returns:
            bool: Success status
        """
        try:
            mutation = """
            mutation productDelete($input: ProductDeleteInput!) {
                productDelete(input: $input) {
                    deletedProductId
                    userErrors {
                        field
                        message
                    }
                }
            }
            """
            
            variables = {
                'input': {
                    'id': f"gid://shopify/Product/{product_id}"
                }
            }
            
            success, response = self._make_graphql_request(mutation, variables)
            
            if success:
                self.logger.info(f"Deleted product {product_id}")
                return True
            else:
                self.logger.error(f"Failed to delete product {product_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting product {product_id}: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test GraphQL API connection
        
        Returns:
            bool: Connection success status
        """
        try:
            query = """
            query {
                shop {
                    id
                    name
                    email
                    domain
                    currencyCode
                }
            }
            """
            
            success, response = self._make_graphql_request(query)
            
            if success and response:
                shop_name = response.get('data', {}).get('shop', {}).get('name', 'Unknown')
                self.logger.info(f"Successfully connected to shop: {shop_name}")
                return True
            else:
                self.logger.error("Failed to connect to Shopify GraphQL API")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def batch_create_products(self, products_data: List[Dict]) -> Dict[str, Dict]:
        """
        Create multiple products in batches using GraphQL
        
        Args:
            products_data (List[Dict]): List of product data dictionaries
            
        Returns:
            Dict[str, Dict]: Results dictionary with SKU as key and result info as value
        """
        results = {}
        
        for product_data in products_data:
            sku = product_data.get('sku', 'unknown')
            
            try:
                success, response = self.create_product(product_data)
                
                if success:
                    product_id = response['data']['productCreate']['product']['id']
                    results[sku] = {
                        'status': 'success',
                        'product_id': product_id,
                        'message': 'Product created successfully'
                    }
                else:
                    results[sku] = {
                        'status': 'failed',
                        'product_id': None,
                        'message': 'Failed to create product'
                    }
                    
            except Exception as e:
                results[sku] = {
                    'status': 'error',
                    'product_id': None,
                    'message': f'Error: {str(e)}'
                }
                self.logger.error(f"Error processing product {sku}: {str(e)}")
        
        return results