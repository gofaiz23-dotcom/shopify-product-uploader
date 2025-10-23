#!/usr/bin/env python3
"""
Environment Setup Helper
Creates a .env file from the example template
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Setup environment file from example"""
    
    print("SHOPIFY AUTOMATION TOOL - ENVIRONMENT SETUP")
    print("="*50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("WARNING: .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    # Copy from example
    if os.path.exists('env.example'):
        shutil.copy('env.example', '.env')
        print("SUCCESS: Created .env file from env.example")
    else:
        print("ERROR: env.example file not found!")
        return
    
    print("\nNEXT STEPS:")
    print("1. Edit the .env file with your actual credentials")
    print("2. Get your Shopify access token from Shopify admin")
    print("3. Update SHOPIFY_API_PASSWORD in .env file")
    print("4. Test with: python test_shopify_rest.py")
    print("5. Upload with: python upload_products.py")
    
    print("\nREQUIRED CREDENTIALS:")
    print("- SHOPIFY_SHOP_URL: furniturehomestores.myshopify.com")
    print("- SHOPIFY_API_PASSWORD: Your Shopify access token")
    
    print("\nHELP:")
    print("- See ENVIRONMENT_SETUP.md for detailed instructions")
    print("- See GET_CORRECT_CREDENTIALS.md for Shopify setup")

if __name__ == "__main__":
    setup_environment()
