#!/usr/bin/env python3
"""
Simple Product Upload Script
Uploads products from Excel file to Shopify
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

def upload_products_from_excel(excel_file_path):
    """Upload products from Excel file to Shopify"""
    
    print("SHOPIFY PRODUCT UPLOAD")
    print("="*50)
    print(f"Excel file: {excel_file_path}")
    print("="*50)
    
    # Check if file exists
    if not os.path.exists(excel_file_path):
        print(f"ERROR: File '{excel_file_path}' not found")
        return False
    
    # Read the Excel file
    print("Reading Excel file...")
    try:
        # Try to read the file with descriptions first
        if 'descriptions' in excel_file_path:
            products_data = pd.read_excel(excel_file_path, sheet_name='Products_with_Descriptions')
        else:
            products_data = pd.read_excel(excel_file_path)
        
        if products_data is None or len(products_data) == 0:
            print("ERROR: No data found in Excel file")
            return False
        
        print(f"SUCCESS: Found {len(products_data)} products")
        
    except Exception as e:
        print(f"ERROR reading Excel file: {str(e)}")
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
    
    # Upload products (limit to 3 for testing)
    print(f"\nUploading products to Shopify...")
    upload_results = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'upload_details': []
    }
    
    # Test with first 3 products only
    test_products = products_data.head(3)
    
    for index, row in test_products.iterrows():
        sku = row.get('sku', f'Product_{index}')
        title = row.get('title', 'Unknown Product')
        price = row.get('price', 0)
        description = row.get('generated_description', row.get('description', ''))
        
        print(f"\nProcessing {index + 1}/3: {sku}")
        print(f"  Title: {title}")
        print(f"  Price: ${price}")
        
        try:
            # Create product data for Shopify REST API
            product_data = {
                "product": {
                    "title": title,
                    "body_html": description,
                    "vendor": row.get('brand', 'Unknown Brand'),
                    "product_type": row.get('category', 'General'),
                    "tags": [row.get('category', 'General'), row.get('brand', 'Unknown')],
                    "variants": [{
                        "price": str(price),
                        "sku": sku,
                        "inventory_quantity": int(row.get('quantity', 0))
                    }]
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
                print(f"  SUCCESS: Product uploaded!")
                print(f"  Shopify ID: {product_id}")
                upload_results['successful'] += 1
                upload_results['upload_details'].append({
                    'sku': sku,
                    'status': 'success',
                    'shopify_id': product_id,
                    'title': title,
                    'price': price
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

if __name__ == "__main__":
    # Default to the file with descriptions
    excel_file = "data/sample_products_with_descriptions.xlsx"
    
    # Check if file exists, otherwise use basic sample
    if not os.path.exists(excel_file):
        excel_file = "data/sample_products.xlsx"
    
    print(f"Using Excel file: {excel_file}")
    upload_products_from_excel(excel_file)
