# 🚀 Quick Setup Guide

## Step 1: Create Environment File

Copy the `env.example` file to `.env`:

```bash
# Windows
copy env.example .env

# Or manually create .env file with:
SHOPIFY_SHOP_URL=furniturehomestores.myshopify.com
SHOPIFY_API_PASSWORD=your_shopify_access_token_here
```

## Step 2: Get Shopify Credentials

1. **Go to Shopify Admin**: https://furniturehomestores.myshopify.com/admin
2. **Navigate to**: Settings → Apps and sales channels
3. **Click**: "Develop apps" → "Create an app"
4. **Name**: "Product Upload System"
5. **Configure Permissions**:
   - ✅ `write_products` (Create/update products)
   - ✅ `read_products` (Read product data)
   - ✅ `write_inventory` (Update inventory)
   - ✅ `read_inventory` (Read inventory data)
6. **Install App** and copy the "Admin API access token"
7. **Update .env file** with your access token

## Step 3: Test Connection

```bash
# Test your credentials
python test_shopify_rest.py

# If successful, upload products
python upload_products.py
```

## Step 4: Upload Products

```bash
# Simple upload (3 products for testing)
python upload_products.py

# Full system upload (all 10 products)
python main.py data/sample_products_with_descriptions.xlsx
```

## 📋 Files Created

- ✅ `env.example` - Template for environment variables
- ✅ `ENVIRONMENT_SETUP.md` - Detailed setup guide
- ✅ `QUICK_SETUP.md` - This quick guide
- ✅ `setup_env.py` - Automated setup script

## 🔧 Troubleshooting

### "Invalid API key or access token"
- Check your Shopify access token is correct
- Ensure the app has proper permissions
- Verify the shop URL is correct (no https://)

### "Environment variable not found"
- Make sure you have a .env file in the project root
- Check the variable names match exactly
- Restart your terminal/IDE after creating .env

## 📚 More Help

- `GET_CORRECT_CREDENTIALS.md` - Detailed Shopify setup
- `SHOPIFY_SETUP_GUIDE.md` - Step-by-step instructions
- `ENVIRONMENT_SETUP.md` - Complete environment guide
