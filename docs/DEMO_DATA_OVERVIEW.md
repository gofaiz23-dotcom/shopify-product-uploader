# 📊 Demo Data Overview

## 🎯 Comprehensive Demo Excel File Created

**File:** `data/demo_products_comprehensive.xlsx`

### 📋 4 Sheets with 5 Products Each

#### 1. **Items Sheet** - Main Product Information
- **SKU**: FURN-001, FURN-002, FURN-003, FURN-004, FURN-005
- **Products**: Modern Dining Chair, Wooden Coffee Table, Leather Sofa, Glass Dining Table, Office Desk
- **Data Includes**: Title, Price, Category, Brand, Features, Material
- **Price Range**: $299.99 - $1,299.99

#### 2. **Stock Sheet** - Inventory Management
- **SKU**: Same 5 SKUs (FURN-001 to FURN-005)
- **Data Includes**: Quantity, Min_Stock, Max_Stock, Reorder_Point, Location, Status
- **Inventory Levels**: 10-50 units per product
- **Warehouse Locations**: Warehouse A, B, C
- **Stock Status**: In Stock, Low Stock

#### 3. **Images Sheet** - Picture Links
- **SKU**: Same 5 SKUs (FURN-001 to FURN-005)
- **Data Includes**: Image_Links, Primary_Image, Image_Count, Image_Quality
- **Images per Product**: 3 images each
- **Image Quality**: All HD quality
- **Sample URLs**: https://example.com/chair1.jpg, etc.

#### 4. **Specs Sheet** - Detailed Specifications
- **SKU**: Same 5 SKUs (FURN-001 to FURN-005)
- **Data Includes**: Weight, Dimensions, Color, Finish, Assembly_Required, Warranty, Country_Origin, Certification
- **Weight Range**: 15.5 lbs - 120.8 lbs
- **Dimensions**: Various sizes (24" to 84" width)
- **Colors**: Black, Natural Oak, Brown Leather, Clear Glass, White
- **Warranties**: 1-5 years
- **Certifications**: FSC Certified, GREENGUARD, OEKO-TEX, ISO 9001

## ✅ Key Features

### **Consistent SKUs Across All Sheets**
- All 4 sheets use the same 5 SKUs: FURN-001 through FURN-005
- Perfect for testing data merging and validation
- Ensures data integrity across the system

### **Rich Data for Testing**
- **Items**: Complete product information with pricing
- **Stock**: Comprehensive inventory management data
- **Images**: Multiple image URLs per product
- **Specs**: Detailed technical specifications

### **Realistic Product Data**
- Furniture products with realistic pricing
- Varied inventory levels and locations
- Professional image URLs and specifications
- Different brands, materials, and features

## 🚀 Usage

### **Test the System**
```bash
# Dry run (validation only)
python main.py data/demo_products_comprehensive.xlsx --dry-run

# Full upload (with real API credentials)
python main.py data/demo_products_comprehensive.xlsx
```

### **Expected Results**
- **Items Sheet**: 5 products with complete information
- **Stock Sheet**: 5 inventory records with warehouse locations
- **Images Sheet**: 5 products with 3 images each (15 total images)
- **Specs Sheet**: 5 products with detailed specifications

## 📊 Data Summary

| Sheet | Records | Key Data |
|-------|---------|----------|
| Items | 5 | Product info, pricing, features |
| Stock | 5 | Inventory levels, locations, status |
| Images | 5 | Image URLs, quality, counts |
| Specs | 5 | Dimensions, weight, warranty, certifications |

## 🎯 Testing Scenarios

1. **Data Merging**: Test how the system merges data from 4 different sheets
2. **SKU Validation**: Verify SKU consistency across all sheets
3. **Image Processing**: Test handling of multiple images per product
4. **Inventory Management**: Test stock level processing
5. **Specification Handling**: Test detailed product specifications

This comprehensive demo data provides everything needed to test the Shopify Product Upload System with realistic, varied data across all 4 required sheets! 🎉
