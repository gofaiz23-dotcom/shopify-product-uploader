# 🔑 Shopify API Setup Guide

## Step 1: Create Private App in Shopify

1. **Go to Shopify Admin**
   - Login to your Shopify store
   - Go to Settings → Apps and sales channels

2. **Create Private App**
   - Click "Develop apps" → "Create an app"
   - Name: "Product Upload System"
   - Click "Create app"

3. **Configure API Permissions**
   - Click "Configure Admin API scopes"
   - Enable these permissions:
     - ✅ `write_products` (Create/update products)
     - ✅ `read_products` (Read product data)
     - ✅ `write_inventory` (Update inventory)
     - ✅ `read_inventory` (Read inventory data)
   - Click "Save"

4. **Install App**
   - Click "Install app"
   - Copy the "Admin API access token"

## Step 2: Update .env File

Replace the credentials in your `.env` file:

```env
# Shopify API Configuration
SHOPIFY_SHOP_URL=furniturehomestores.myshopify.com
SHOPIFY_API_KEY=your_new_api_key_here
SHOPIFY_API_PASSWORD=your_new_access_token_here
```

## Step 3: Test Connection

```bash
python -c "
import sys; sys.path.append('.')
from src.api.shopify_api_client import ShopifyAPIClient
client = ShopifyAPIClient('furniturehomestores.myshopify.com', 'YOUR_API_KEY', 'YOUR_ACCESS_TOKEN')
print('Testing connection...')
result = client.test_connection()
print(f'Connection successful: {result}')
"
```

## Step 4: Upload Products

```bash
# Upload with real Shopify API
python scripts/upload_with_descriptions.py data/sample_products_with_descriptions.xlsx

# Or dry run first (recommended)
python scripts/upload_with_descriptions.py data/sample_products_with_descriptions.xlsx --dry-run
```

## 🔍 Troubleshooting

### If Connection Fails:
1. **Check API Key**: Make sure it's the correct API key (not access token)
2. **Check Access Token**: Make sure it's the Admin API access token
3. **Check Permissions**: Ensure all required permissions are enabled
4. **Check URL**: Use format: `your-shop.myshopify.com` (no https://)

### Common Issues:
- ❌ "Invalid API key" → Wrong API key
- ❌ "Invalid access token" → Wrong access token  
- ❌ "Insufficient permissions" → Missing API scopes
- ❌ "Shop not found" → Wrong shop URL

## 📋 Required API Scopes:
- `write_products` - Create/update products
- `read_products` - Read product data
- `write_inventory` - Update inventory levels
- `read_inventory` - Read inventory data
