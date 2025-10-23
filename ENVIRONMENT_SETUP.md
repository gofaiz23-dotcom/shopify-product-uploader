# 🔧 Environment Setup Guide

## 📋 Required Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# ===========================================
# SHOPIFY AUTOMATION TOOL - ENVIRONMENT CONFIG
# ===========================================

# ===========================================
# SHOPIFY API CONFIGURATION (REQUIRED)
# ===========================================
# Your Shopify shop URL (without https://)
SHOPIFY_SHOP_URL=furniturehomestores.myshopify.com

# Your Shopify Admin API access token (get from Shopify admin)
SHOPIFY_API_PASSWORD=your_shopify_access_token_here

# ===========================================
# AI CONFIGURATION (OPTIONAL)
# ===========================================
# OpenAI API key for AI description generation
OPENAI_API_KEY=your_openai_api_key_here

# ===========================================
# PROCESSING CONFIGURATION
# ===========================================
# Number of products to process in each batch
BATCH_SIZE=100

# Maximum number of worker threads
MAX_WORKERS=1

# Number of retry attempts for failed requests
MAX_RETRIES=3

# Delay between batches (seconds)
DELAY_BETWEEN_BATCHES=1.0

# ===========================================
# LOGGING CONFIGURATION
# ===========================================
# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Log file path
LOG_FILE=logs/shopify_upload.log

# ===========================================
# REPORT CONFIGURATION
# ===========================================
# Directory for generated reports
REPORT_DIR=reports

# Directory for backups
BACKUP_DIR=backups

# ===========================================
# SHOPIFY API SETTINGS
# ===========================================
# Shopify API version
SHOPIFY_API_VERSION=2023-10

# Rate limit (requests per second)
SHOPIFY_RATE_LIMIT=2.0

# ===========================================
# VALIDATION SETTINGS
# ===========================================
# Validate image URLs before upload
VALIDATE_IMAGES=true

# Validate price data
VALIDATE_PRICES=true

# Skip duplicate products
SKIP_DUPLICATES=false

# ===========================================
# RETRY CONFIGURATION
# ===========================================
# Initial delay between retries (seconds)
RETRY_DELAY=2.0

# Maximum delay between retries (seconds)
MAX_RETRY_DELAY=60.0

# Retry backoff factor
RETRY_BACKOFF_FACTOR=2.0

# ===========================================
# PRICING CONFIGURATION
# ===========================================
# Handling charges (fixed amount)
HANDLING_CHARGES=50.0

# Logistics charges (fixed amount)
LOGISTICS_CHARGES=300.0

# Marketplace commission percentage
MARKETPLACE_COMMISSION_PERCENT=15.0

# Profit margin percentage
PROFIT_MARGIN_PERCENT=20.0

# ===========================================
# SELENIUM CONFIGURATION
# ===========================================
# Run browser in headless mode
SELENIUM_HEADLESS=true

# Wait timeout for web elements (seconds)
SELENIUM_WAIT_TIMEOUT=10

# ===========================================
# AI FIESTA CONFIGURATION
# ===========================================
# AI Fiesta website URL
AI_FIESTA_URL=https://aifiesta.com/

# Wait time for AI processing (seconds)
AI_FIESTA_WAIT_TIME=15

# Number of retry attempts for AI requests
AI_FIESTA_RETRY_ATTEMPTS=3

# ===========================================
# DYNAMIC LOGISTICS (ADVANCED)
# ===========================================
# Enable dynamic logistics calculation
USE_DYNAMIC_LOGISTICS=false

# Base logistics rate per km
BASE_LOGISTICS_RATE=10.0

# Minimum logistics charge
MIN_LOGISTICS_CHARGE=50.0

# Maximum logistics charge
MAX_LOGISTICS_CHARGE=500.0

# Default distance (km)
DEFAULT_DISTANCE_KM=100.0

# Default weight (kg)
DEFAULT_WEIGHT_KG=1.0
```

## 🚀 Quick Setup

### Step 1: Create .env File
```bash
# Copy the environment variables above into a new file called .env
# Replace the placeholder values with your actual credentials
```

### Step 2: Get Shopify Credentials
1. Go to your Shopify admin: https://furniturehomestores.myshopify.com/admin
2. Navigate to Settings → Apps and sales channels
3. Click "Develop apps" → "Create an app"
4. Configure API permissions (write_products, read_products, etc.)
5. Install the app and copy the Admin API access token
6. Update `SHOPIFY_API_PASSWORD` in your .env file

### Step 3: Test Connection
```bash
# Test your credentials
python test_shopify_rest.py

# Upload products
python upload_products.py
```

## 🔑 Required Variables (Minimum)

For basic functionality, you only need:

```env
SHOPIFY_SHOP_URL=furniturehomestores.myshopify.com
SHOPIFY_API_PASSWORD=your_actual_access_token_here
```

## 📝 Optional Variables

All other variables have sensible defaults and are optional for basic usage.

## 🛠️ Troubleshooting

### If you get "Invalid API key or access token":
1. Check your Shopify access token is correct
2. Ensure the app has proper permissions
3. Verify the shop URL is correct (no https://)

### If you get "Environment variable not found":
1. Make sure you have a .env file in the project root
2. Check the variable names match exactly
3. Restart your terminal/IDE after creating .env

## 📚 More Help

- See `GET_CORRECT_CREDENTIALS.md` for detailed Shopify setup
- See `SHOPIFY_SETUP_GUIDE.md` for step-by-step instructions
- Check logs in the `logs/` directory for detailed error information
