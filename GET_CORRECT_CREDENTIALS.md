# 🔑 How to Get Correct Shopify API Credentials

## ❌ Current Issue
Your current credentials are returning "Invalid API key or access token" error.

## ✅ Solution: Get Correct Credentials

### Method 1: Private App (Recommended)

1. **Go to Shopify Admin**
   - Login to: https://furniturehomestores.myshopify.com/admin
   - Go to **Settings** → **Apps and sales channels**

2. **Create Private App**
   - Click **"Develop apps"**
   - Click **"Create an app"**
   - Name: "Product Upload System"
   - Click **"Create app"**

3. **Configure API Access**
   - Click **"Configure Admin API scopes"**
   - Enable these permissions:
     - ✅ `write_products`
     - ✅ `read_products`
     - ✅ `write_inventory`
     - ✅ `read_inventory`
   - Click **"Save"**

4. **Install App**
   - Click **"Install app"**
   - **Copy the "Admin API access token"** (this is your password)

5. **Get API Key**
   - In the app details, find **"Admin API key"**
   - Copy this key

### Method 2: Check Existing Apps

1. **Go to Apps and sales channels**
2. **Look for existing private apps**
3. **Check if you already have one with the right permissions**

## 📝 Update Your .env File

Replace the credentials in your `.env` file:

```env
# Shopify API Configuration
SHOPIFY_SHOP_URL=furniturehomestores.myshopify.com
SHOPIFY_API_KEY=your_admin_api_key_here
SHOPIFY_API_PASSWORD=your_admin_api_access_token_here
```

## 🧪 Test Your Credentials

After updating, test with:

```bash
python -c "
import requests
url = 'https://furniturehomestores.myshopify.com/admin/api/2025-10/products.json'
headers = {'X-Shopify-Access-Token': 'YOUR_ACCESS_TOKEN'}
response = requests.get(url, headers=headers)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print('✅ SUCCESS: Credentials are valid!')
else:
    print('❌ FAILED: Invalid credentials')
    print(response.text)
"
```

## 🔍 Common Issues

### Wrong Credential Type
- ❌ **API Key**: This is NOT the access token
- ✅ **Access Token**: This is what you need for authentication

### Wrong URL Format
- ❌ `https://furniturehomestores.myshopify.com/`
- ✅ `furniturehomestores.myshopify.com`

### Missing Permissions
Make sure you have:
- `write_products` - To create products
- `read_products` - To read existing products
- `write_inventory` - To set stock levels
- `read_inventory` - To read stock levels

## 🚀 Once Credentials Work

Run the real upload:

```bash
# Test with 2 products first
python test_real_shopify_upload.py

# Upload all products
python scripts/upload_with_descriptions.py data/sample_products_with_descriptions.xlsx
```
