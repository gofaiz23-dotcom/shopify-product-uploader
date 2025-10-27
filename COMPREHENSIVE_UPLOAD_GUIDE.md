# Comprehensive Product Upload Guide

This guide explains how to upload products to Shopify with **ALL fields** including title, description, images, category, inventory, and more.

## Overview

The system now includes comprehensive product upload functionality that handles:
- ✅ Product title and description
- ✅ Product images
- ✅ Category and product type
- ✅ Inventory quantity
- ✅ Pricing
- ✅ Brand/vendor
- ✅ Features and materials
- ✅ Tags
- ✅ SKU

## CSV Files Required

The system uses three CSV files to load product data:

### 1. `data/Items.csv`
Contains basic product information:
- SKU
- Title
- Price
- Category
- Brand
- Features
- Material

### 2. `data/Stock.csv`
Contains inventory information:
- SKU
- Quantity

### 3. `data/Images.csv`
Contains product images:
- SKU
- Image Links (comma-separated URLs)

## Available Upload Scripts

### 1. `upload_products.py` (REST API)
Simple script using Shopify REST API:
- Reads from CSV files
- Uploads products with all fields
- Includes image upload
- Basic error handling

**Usage:**
```bash
python upload_products.py
```

**Features:**
- Uploads 10 products (configurable)
- Images uploaded after product creation
- REST API based

### 2. `comprehensive_upload.py` (GraphQL API - Recommended)
Advanced script using Shopify GraphQL API:
- Uses the full ShopifyAPIClient
- Better error handling
- Comprehensive logging
- Upload reports
- Rate limiting

**Usage:**
```bash
python comprehensive_upload.py
```

**Features:**
- Uploads 10 products (remove limit for all)
- Uses GraphQL for better performance
- Detailed logging
- CSV upload reports
- Professional output

## CSV File Format

### Items.csv Format
```csv
SKU,Title,Price,Category,Brand,Features,Material
FURN-001,Modern Dining Chair,299.99,Furniture,Acme Furniture,"Ergonomic design, Easy assembly","Solid wood, Metal legs"
```

### Stock.csv Format
```csv
SKU,Quantity
FURN-001,50
```

### Images.csv Format
```csv
SKU,Image Links
FURN-001,"https://example.com/chair1.jpg, https://example.com/chair2.jpg"
```

## Product Fields Uploaded

### Basic Information
- **Title**: Product name
- **Description**: HTML formatted description with features and materials
- **Vendor/Brand**: Product brand
- **Product Type**: Category

### Pricing & Inventory
- **Price**: Product price
- **SKU**: Stock keeping unit
- **Quantity**: Inventory quantity
- **Inventory Management**: Set to Shopify managed
- **Inventory Policy**: Set to deny when out of stock

### Metadata
- **Tags**: Generated from category, brand, and features
- **Features**: Added as description sections
- **Material**: Added as description sections

### Images
- Multiple images supported (comma-separated URLs)
- Images uploaded after product creation
- Alt text automatically added

## Configuration

Ensure your `.env` file has the correct credentials:

```env
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_PASSWORD=your_api_password
```

## Running the Upload

### Option 1: Quick Upload (REST API)
```bash
python upload_products.py
```

### Option 2: Comprehensive Upload (GraphQL API - Recommended)
```bash
python comprehensive_upload.py
```

### Upload All Products
To upload all products (remove the limit), edit either script and change:
```python
comprehensive_upload(items_file, stock_file, images_file, limit=None)  # Upload all
```

or in upload_products.py:
```python
upload_products_from_csv(items_file, stock_file, images_file, limit=None)  # Upload all
```

## Output

Both scripts provide detailed output showing:
- Connection status
- Products being uploaded
- Success/failure status
- Shopify product IDs
- Image upload status

### Example Output
```
============================================================
COMPREHENSIVE SHOPIFY PRODUCT UPLOAD
============================================================
Items file: data/Items.csv
Stock file: data/Stock.csv
Images file: data/Images.csv
============================================================
Testing Shopify connection...
SUCCESS: Connected to Shopify

Loading product data from CSV files...
SUCCESS: Found 10 products

[1/10] Processing: FURN-001
  Title: Modern Dining Chair
  Price: $299.99
  Category: Furniture
  Brand: Acme Furniture
  Quantity: 50
  ✓ SUCCESS: Product uploaded!
    Shopify ID: gid://shopify/Product/123456789
    Images: Uploading 2 images...
```

## Upload Reports

The `comprehensive_upload.py` script generates detailed CSV reports in the `reports/` directory:

- **Filename**: `upload_report_YYYYMMDD_HHMMSS.csv`
- **Contains**: SKU, status, Shopify ID, title, price, quantity
- **Location**: `reports/upload_report_[timestamp].csv`

## Logging

Comprehensive logging is available in `logs/comprehensive_upload.log`:
- Connection attempts
- Product uploads
- Errors and warnings
- Detailed error messages

## Troubleshooting

### Connection Issues
- Verify Shopify credentials in `.env` file
- Check API permissions
- Ensure shop URL is correct

### Image Upload Issues
- Verify image URLs are accessible
- Check image format (jpg, png)
- Ensure images are not too large

### Product Creation Issues
- Check for duplicate SKUs
- Verify all required fields are present
- Review error messages in logs

## Best Practices

1. **Test with a small batch first** - Upload 2-3 products to verify everything works
2. **Check your data** - Ensure CSV files are properly formatted
3. **Verify images** - Make sure image URLs are accessible
4. **Monitor logs** - Check the log files for any issues
5. **Review upload reports** - Verify successful uploads in reports

## Advanced Features

### Custom Product Data
You can extend the product data by modifying the `prepare_product_data()` function in `comprehensive_upload.py` to add:
- Weight
- Dimensions
- Barcode
- Metafields
- SEO fields

### Batch Processing
For large catalogs, consider:
- Processing in batches
- Adding delays between requests
- Using rate limiting
- Monitoring API usage

## Need Help?

If you encounter issues:
1. Check the logs in `logs/` directory
2. Review upload reports in `reports/` directory
3. Verify CSV file formats
4. Test API credentials
5. Review error messages for specific issues
