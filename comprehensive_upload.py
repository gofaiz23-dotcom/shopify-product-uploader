#!/usr/bin/env python3
"""
Comprehensive Product Upload Script
Uploads products from CSV files to Shopify with ALL fields using GraphQL API
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.shopify_api_client import ShopifyAPIClient
from src.config.config_manager import ConfigManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/comprehensive_upload.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_product_data(items_file, stock_file, images_file):
    """Load product data from CSV files"""
    
    logger.info(f"Loading data from {items_file}")
    items_df = pd.read_csv(items_file)
    
    logger.info(f"Loading data from {stock_file}")
    stock_df = pd.read_csv(stock_file)
    
    logger.info(f"Loading data from {images_file}")
    images_df = pd.read_csv(images_file)
    
    # Merge all dataframes on SKU
    products_df = items_df.merge(stock_df, on='SKU', how='left')
    products_df = products_df.merge(images_df, on='SKU', how='left')
    
    # Fill missing values
    products_df['Quantity'] = products_df['Quantity'].fillna(0).astype(int)
    products_df['Image Links'] = products_df['Image Links'].fillna('')
    products_df['Features'] = products_df['Features'].fillna('')
    products_df['Material'] = products_df['Material'].fillna('')
    
    return products_df

def prepare_product_data(row):
    """Prepare comprehensive product data from CSV row"""
    
    # Basic product information
    product_data = {
        'sku': row.get('SKU', ''),
        'title': row.get('Title', 'Unknown Product'),
        'price': float(row.get('Price', 0)),
        'category': row.get('Category', 'General'),
        'brand': row.get('Brand', 'Unknown Brand'),
        'quantity': int(row.get('Quantity', 0)),
        'image_links': row.get('Image Links', ''),
        'features': row.get('Features', ''),
        'material': row.get('Material', ''),
    }
    
    # Create comprehensive description
    description = f"<h2>{product_data['title']}</h2>"
    description += f"<p><strong>Brand:</strong> {product_data['brand']}</p>"
    description += f"<p><strong>Category:</strong> {product_data['category']}</p>"
    
    if product_data['features']:
        description += f"<h3>Features</h3><ul>"
        for feature in product_data['features'].split(','):
            description += f"<li>{feature.strip()}</li>"
        description += "</ul>"
    
    if product_data['material']:
        description += f"<h3>Materials</h3><p>{product_data['material']}</p>"
    
    product_data['body_html'] = description
    
    # Create tags from category, brand, and features
    tags = [product_data['category'], product_data['brand']]
    if product_data['features']:
        tags.extend([f.strip() for f in product_data['features'].split(',')])
    product_data['tags'] = tags
    
    return product_data

def comprehensive_upload(items_file, stock_file, images_file, limit=None):
    """Upload products from CSV files to Shopify with all fields"""
    
    print("="*60)
    print("COMPREHENSIVE SHOPIFY PRODUCT UPLOAD")
    print("="*60)
    print(f"Items file: {items_file}")
    print(f"Stock file: {stock_file}")
    print(f"Images file: {images_file}")
    print("="*60)
    
    # Check if files exist
    for file in [items_file, stock_file, images_file]:
        if not os.path.exists(file):
            print(f"ERROR: File '{file}' not found")
            return False
    
    # Load configuration
    try:
        config = ConfigManager()
        shopify_config = config.get_shopify_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        print(f"ERROR: Failed to load configuration: {str(e)}")
        return False
    
    # Initialize Shopify API client
    shopify_client = ShopifyAPIClient(
        shop_url=shopify_config['shop_url'],
        api_key=shopify_config['api_key'],
        api_password=shopify_config['api_password']
    )
    
    # Test connection
    print("Testing Shopify connection...")
    if not shopify_client.test_connection():
        print("ERROR: Failed to connect to Shopify")
        return False
    print("SUCCESS: Connected to Shopify\n")
    
    # Load product data
    print("Loading product data from CSV files...")
    try:
        products_df = load_product_data(items_file, stock_file, images_file)
        
        if products_df is None or len(products_df) == 0:
            print("ERROR: No data found in CSV files")
            return False
        
        print(f"SUCCESS: Found {len(products_df)} products")
        
    except Exception as e:
        print(f"ERROR reading CSV files: {str(e)}")
        logger.error(f"Error reading CSV files: {str(e)}")
        return False
    
    # Limit products if specified
    if limit:
        products_df = products_df.head(limit)
        print(f"Limited to {len(products_df)} products for upload\n")
    
    # Upload products
    print("="*60)
    print(f"Uploading {len(products_df)} products to Shopify...")
    print("="*60)
    
    upload_results = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'upload_details': []
    }
    
    for index, row in products_df.iterrows():
        sku = row.get('SKU', f'Product_{index}')
        
        print(f"\n[{index + 1}/{len(products_df)}] Processing: {sku}")
        print(f"  Title: {row.get('Title', 'Unknown')}")
        print(f"  Price: ${row.get('Price', 0)}")
        print(f"  Category: {row.get('Category', 'General')}")
        print(f"  Brand: {row.get('Brand', 'Unknown')}")
        print(f"  Quantity: {row.get('Quantity', 0)}")
        
        try:
            # Prepare comprehensive product data
            product_data = prepare_product_data(row)
            
            # Upload product using GraphQL API
            success, response = shopify_client.create_product(product_data)
            
            if success and response:
                product = response['data']['productCreate']['product']
                product_id = product['id']
                
                print(f"  ✓ SUCCESS: Product uploaded!")
                print(f"    Shopify ID: {product_id}")
                
                # Check for images
                if product_data['image_links']:
                    print(f"    Images: Uploading {len(product_data['image_links'].split(','))} images...")
                
                upload_results['successful'] += 1
                upload_results['upload_details'].append({
                    'sku': sku,
                    'status': 'success',
                    'shopify_id': product_id,
                    'title': product_data['title'],
                    'price': product_data['price'],
                    'quantity': product_data['quantity']
                })
            else:
                error_msg = "Unknown error"
                if response and 'errors' in response:
                    error_msg = str(response['errors'])
                elif response and 'data' in response and 'productCreate' in response['data']:
                    user_errors = response['data']['productCreate'].get('userErrors', [])
                    if user_errors:
                        error_msg = str(user_errors)
                
                print(f"  ✗ FAILED: {error_msg}")
                upload_results['failed'] += 1
                upload_results['upload_details'].append({
                    'sku': sku,
                    'status': 'failed',
                    'error': error_msg
                })
                logger.error(f"Failed to upload product {sku}: {error_msg}")
                
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            upload_results['failed'] += 1
            upload_results['upload_details'].append({
                'sku': sku,
                'status': 'failed',
                'error': str(e)
            })
            logger.error(f"Error processing product {sku}: {str(e)}", exc_info=True)
        
        upload_results['total_processed'] += 1
    
    # Print summary
    print("\n" + "="*60)
    print("UPLOAD SUMMARY")
    print("="*60)
    print(f"Total Products Processed: {upload_results['total_processed']}")
    print(f"✓ Successful: {upload_results['successful']}")
    print(f"✗ Failed: {upload_results['failed']}")
    print("="*60)
    
    if upload_results['successful'] > 0:
        print(f"\n✓ SUCCESS: {upload_results['successful']} products uploaded to Shopify!")
        print("Please check your Shopify admin panel to verify the products.")
        
        # Save upload report
        report_file = f"reports/upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        report_df = pd.DataFrame(upload_results['upload_details'])
        report_df.to_csv(report_file, index=False)
        print(f"\nUpload report saved to: {report_file}")
        
        return True
    else:
        print("\n✗ No products were uploaded successfully.")
        print("Please check the logs for error details.")
        return False

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # CSV file paths
    items_file = "data/Items.csv"
    stock_file = "data/Stock.csv"
    images_file = "data/Images.csv"
    
    # Upload products (set limit=None to upload all products)
    comprehensive_upload(items_file, stock_file, images_file, limit=10)
