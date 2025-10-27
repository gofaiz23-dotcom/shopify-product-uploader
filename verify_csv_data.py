#!/usr/bin/env python3
"""
CSV Data Verification Script
Verifies and displays product data from CSV files before uploading to Shopify
"""

import os
import pandas as pd
from pathlib import Path

def verify_csv_files(items_file, stock_file, images_file):
    """Verify CSV files and display product data"""
    
    print("="*70)
    print("CSV DATA VERIFICATION")
    print("="*70)
    
    # Check if files exist
    print("\n1. Checking files...")
    for file in [items_file, stock_file, images_file]:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✓ {file} ({size} bytes)")
        else:
            print(f"   ✗ {file} - NOT FOUND")
            return False
    
    # Load data
    print("\n2. Loading data...")
    try:
        items_df = pd.read_csv(items_file)
        stock_df = pd.read_csv(stock_file)
        images_df = pd.read_csv(images_file)
        print(f"   ✓ Items: {len(items_df)} products")
        print(f"   ✓ Stock: {len(stock_df)} records")
        print(f"   ✓ Images: {len(images_df)} records")
    except Exception as e:
        print(f"   ✗ Error loading CSV files: {str(e)}")
        return False
    
    # Merge data
    print("\n3. Merging data...")
    try:
        products_df = items_df.merge(stock_df, on='SKU', how='left')
        products_df = products_df.merge(images_df, on='SKU', how='left')
        print(f"   ✓ Merged: {len(products_df)} products")
    except Exception as e:
        print(f"   ✗ Error merging data: {str(e)}")
        return False
    
    # Check for missing values
    print("\n4. Checking data quality...")
    missing_sku = products_df[products_df['SKU'].isna()].shape[0]
    missing_title = products_df[products_df['Title'].isna()].shape[0]
    missing_price = products_df[products_df['Price'].isna()].shape[0]
    missing_quantity = products_df[products_df['Quantity'].isna()].shape[0]
    
    if missing_sku > 0:
        print(f"   ⚠ Warning: {missing_sku} products with missing SKU")
    else:
        print(f"   ✓ All products have SKU")
    
    if missing_title > 0:
        print(f"   ⚠ Warning: {missing_title} products with missing Title")
    else:
        print(f"   ✓ All products have Title")
    
    if missing_price > 0:
        print(f"   ⚠ Warning: {missing_price} products with missing Price")
    else:
        print(f"   ✓ All products have Price")
    
    if missing_quantity > 0:
        print(f"   ⚠ Warning: {missing_quantity} products with missing Quantity")
    else:
        print(f"   ✓ All products have Quantity")
    
    # Display sample data
    print("\n5. Sample product data:")
    print("="*70)
    
    for index, row in products_df.head(5).iterrows():
        print(f"\nProduct #{index + 1}:")
        print(f"  SKU: {row.get('SKU', 'N/A')}")
        print(f"  Title: {row.get('Title', 'N/A')}")
        print(f"  Price: ${row.get('Price', 0):.2f}")
        print(f"  Category: {row.get('Category', 'N/A')}")
        print(f"  Brand: {row.get('Brand', 'N/A')}")
        print(f"  Quantity: {row.get('Quantity', 0)}")
        print(f"  Features: {row.get('Features', 'N/A')}")
        print(f"  Material: {row.get('Material', 'N/A')}")
        
        images = row.get('Image Links', '')
        if images and images.strip():
            image_count = len([i for i in images.split(',') if i.strip()])
            print(f"  Images: {image_count} image(s)")
        else:
            print(f"  Images: None")
        
        if index < products_df.head(5).shape[0] - 1:
            print("-"*70)
    
    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    total_products = len(products_df)
    avg_price = products_df['Price'].mean()
    total_inventory = products_df['Quantity'].sum()
    total_value = (products_df['Price'] * products_df['Quantity']).sum()
    
    categories = products_df['Category'].value_counts()
    brands = products_df['Brand'].value_counts()
    
    print(f"\nTotal Products: {total_products}")
    print(f"Average Price: ${avg_price:.2f}")
    print(f"Total Inventory Units: {total_inventory}")
    print(f"Total Inventory Value: ${total_value:,.2f}")
    
    print(f"\nCategories ({len(categories)}):")
    for category, count in categories.items():
        print(f"  {category}: {count} products")
    
    print(f"\nBrands ({len(brands)}):")
    for brand, count in brands.head(10).items():
        print(f"  {brand}: {count} products")
    
    if len(brands) > 10:
        print(f"  ... and {len(brands) - 10} more brands")
    
    # Product fields summary
    print("\n" + "="*70)
    print("PRODUCT FIELDS SUMMARY")
    print("="*70)
    
    fields = {
        'SKU': 'Stock Keeping Unit',
        'Title': 'Product name',
        'Price': 'Product price',
        'Category': 'Product category',
        'Brand': 'Product brand/vendor',
        'Features': 'Product features',
        'Material': 'Product materials',
        'Quantity': 'Inventory quantity',
        'Image Links': 'Product image URLs'
    }
    
    for field, description in fields.items():
        if field in products_df.columns:
            filled = products_df[field].notna().sum()
            percentage = (filled / total_products) * 100
            print(f"  {field:15} ({description:20}) : {filled}/{total_products} ({percentage:.1f}%)")
    
    print("\n" + "="*70)
    print("✓ Verification complete!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    # CSV file paths
    items_file = "data/Items.csv"
    stock_file = "data/Stock.csv"
    images_file = "data/Images.csv"
    
    verify_csv_files(items_file, stock_file, images_file)
