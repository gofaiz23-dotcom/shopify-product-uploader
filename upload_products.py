#!/usr/bin/env python3
"""
Simple Product Upload Script
Uploads products from CSV files to Shopify with all fields
"""

import os
import sys
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.shopify_api_client import ShopifyAPIClient

def load_product_data(items_file, stock_file, images_file):
    """Load product data from CSV files"""
    
    # Load Items.csv
    items_df = pd.read_csv(items_file)
    
    # Load Stock.csv
    stock_df = pd.read_csv(stock_file)
    
    # Load Images.csv
    images_df = pd.read_csv(images_file)
    
    # Merge all dataframes on SKU
    products_df = items_df.merge(stock_df, on='SKU', how='left')
    products_df = products_df.merge(images_df, on='SKU', how='left')
    
    # Fill missing values
    products_df['Quantity'] = products_df['Quantity'].fillna(0).astype(int)
    products_df['Image Links'] = products_df['Image Links'].fillna('')
    
    return products_df

def upload_products_from_csv(items_file, stock_file, images_file, limit=None):
    """Upload products from CSV files to Shopify"""
    
    print("SHOPIFY PRODUCT UPLOAD - COMPREHENSIVE")
    print("="*50)
    print(f"Items file: {items_file}")
    print(f"Stock file: {stock_file}")
    print(f"Images file: {images_file}")
    print("="*50)
    
    # Check if files exist
    for file in [items_file, stock_file, images_file]:
        if not os.path.exists(file):
            print(f"ERROR: File '{file}' not found")
            return False
    
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
        return False
    
    # Shopify API configuration from environment variables
    shop_url = os.getenv('SHOPIFY_SHOP_URL', 'furniturehomestores.myshopify.com')
    access_token = os.getenv('SHOPIFY_API_PASSWORD', '')
    
    # Clean shop URL - remove https:// if present
    shop_url = shop_url.replace('https://', '').replace('http://', '').rstrip('/')
    
    if not access_token:
        print("ERROR: SHOPIFY_API_PASSWORD not found in environment variables")
        print("Please set your Shopify API password in .env file or environment")
        return False
    
    # Test Shopify REST API connection
    print("Testing Shopify REST API connection...")
    try:
        
        test_url = f"https://{shop_url}/admin/api/2023-10/shop.json"
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"FAILED: Cannot connect to Shopify API")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            print("Please update your access token in the script")
            return False
        
        shop_data = response.json()
        shop_name = shop_data.get('shop', {}).get('name', 'Unknown')
        print(f"SUCCESS: Connected to shop '{shop_name}'")
        
    except Exception as e:
        print(f"ERROR: Failed to connect to Shopify: {str(e)}")
        return False
    
    # Upload products (limit if specified)
    if limit:
        products_df = products_df.head(limit)
    
    print(f"\nUploading {len(products_df)} products to Shopify...")
    upload_results = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'upload_details': []
    }
    
    for index, row in products_df.iterrows():
        sku = row.get('SKU', f'Product_{index}')
        title = row.get('Title', 'Unknown Product')
        price = row.get('Price', 0)
        category = row.get('Category', 'General')
        brand = row.get('Brand', 'Unknown Brand')
        features = row.get('Features', '')
        material = row.get('Material', '')
        weight = row.get('Weight', 0)
        quantity = int(row.get('Quantity', 0))
        image_links = row.get('Image Links', '')
        
        print(f"\nProcessing {index + 1}/{len(products_df)}: {sku}")
        print(f"  Title: {title}")
        print(f"  Price: ${price}")
        print(f"  Category: {category}")
        print(f"  Quantity: {quantity}")
        print(f"  Weight: {weight} kg")
        
        try:
            # Create comprehensive description
            description = f"<h2>{title}</h2>"
            
            if features:
                description += f"<h3>Features</h3><p>{features}</p>"
            
            if material:
                description += f"<h3>Materials</h3><p>{material}</p>"
            
            # Build variant with weight
            variant = {
                "price": str(price),
                "sku": sku,
                "inventory_quantity": quantity,
                "inventory_management": "shopify",
                "inventory_policy": "deny"
            }
            
            # Add weight if available
            if weight and weight > 0:
                variant["weight"] = float(weight)
                variant["weight_unit"] = "kg"
            
            # Create product data for Shopify REST API with ALL fields
            product_data = {
                "product": {
                    "title": title,
                    "body_html": description,
                    "vendor": brand,
                    "product_type": category,
                    "tags": [category, brand] + (features.split(', ') if features else []),
                    "variants": [variant]
                }
            }
            
            # Upload to Shopify using REST API
            print(f"  Uploading to Shopify...")
            upload_url = f"https://{shop_url}/admin/api/2023-10/products.json"
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(upload_url, headers=headers, json=product_data, timeout=30)
            
            if response.status_code in [200, 201]:
                product_info = response.json()
                product_id = product_info.get('product', {}).get('id')
                variant_id = product_info.get('product', {}).get('variants', [{}])[0].get('id')
                
                print(f"  SUCCESS: Product uploaded!")
                print(f"  Shopify ID: {product_id}")
                
                # Upload images if available
                if image_links and image_links.strip():
                    upload_images(shop_url, access_token, product_id, image_links)
                
                upload_results['successful'] += 1
                upload_results['upload_details'].append({
                    'sku': sku,
                    'status': 'success',
                    'shopify_id': product_id,
                    'variant_id': variant_id,
                    'title': title,
                    'price': price,
                    'quantity': quantity
                })
            else:
                print(f"  FAILED: {response.status_code} - {response.text}")
                upload_results['failed'] += 1
                upload_results['upload_details'].append({
                    'sku': sku,
                    'status': 'failed',
                    'error': f"{response.status_code} - {response.text}"
                })
                
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            upload_results['failed'] += 1
            upload_results['upload_details'].append({
                'sku': sku,
                'status': 'failed',
                'error': str(e)
            })
        
        upload_results['total_processed'] += 1
    
    # Print summary
    print("\n" + "="*50)
    print("UPLOAD SUMMARY")
    print("="*50)
    print(f"Total Products: {upload_results['total_processed']}")
    print(f"Successful: {upload_results['successful']}")
    print(f"Failed: {upload_results['failed']}")
    
    if upload_results['successful'] > 0:
        print(f"\nSUCCESS: {upload_results['successful']} products uploaded to Shopify!")
        print("Check your Shopify admin to see the products.")
        return True
    else:
        print("\nNo products were uploaded successfully.")
        print("Please check your API credentials and try again.")
        return False

def upload_images(shop_url, access_token, product_id, image_links):
    """Upload images for a product"""
    try:
        if not image_links or not image_links.strip():
            return
        
        # Split image links
        image_urls = [url.strip() for url in image_links.split(',') if url.strip()]
        
        for i, image_url in enumerate(image_urls):
            if not image_url:
                continue
            
            image_data = {
                "image": {
                    "product_id": product_id,
                    "src": image_url,
                    "alt": f"Product image {i+1}"
                }
            }
            
            upload_url = f"https://{shop_url}/admin/api/2023-10/products/{product_id}/images.json"
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(upload_url, headers=headers, json=image_data, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"  Image {i+1} uploaded")
            else:
                print(f"  Failed to upload image {i+1}: {response.status_code}")
        
    except Exception as e:
        print(f"  Error uploading images: {str(e)}")

if __name__ == "__main__":
    # Use CSV files
    items_file = "data/Items.csv"
    stock_file = "data/Stock.csv"
    images_file = "data/Images.csv"
    
    # Upload products (limit to 10 for testing, remove limit for all products)
    upload_products_from_csv(items_file, stock_file, images_file, limit=10)
