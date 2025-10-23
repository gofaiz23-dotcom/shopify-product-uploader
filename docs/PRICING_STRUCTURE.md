# 💰 Enhanced Pricing Structure

## 🎯 Pricing Formula Implementation

**File:** `data/demo_products_enhanced_pricing.xlsx`

### 📊 **5-Sheet Structure with Enhanced Pricing**

#### **1. Items Sheet** - Main Product Information
- **Base_Price**: Original item cost
- **Handling_Charges**: $50 (fixed per item)
- **Logistics_Charges**: $300 (fixed per item)
- **Profit_Margin_20%**: 20% profit on subtotal
- **Markup_Charges_15%**: 15% markup on profit-included price
- **Final_Price**: Complete calculated price

#### **2. Stock Sheet** - Inventory Management
- **Cost_Per_Unit**: Base item price
- **Total_Inventory_Value**: Base price × quantity
- Standard inventory tracking fields

#### **3. Images Sheet** - Picture Links
- Multiple image URLs per product
- Primary image designation
- Image quality specifications

#### **4. Specs Sheet** - Technical Specifications
- Weight, dimensions, color, finish
- Assembly requirements, warranty
- Country of origin, certifications

#### **5. Pricing Sheet** - Detailed Pricing Breakdown ⭐ **NEW**
- Complete pricing calculation breakdown
- Step-by-step cost analysis
- Profit and markup calculations

## 🧮 **Pricing Formula**

```
Final Price = (Base Price + Handling + Logistics) × (1 + 20%) × (1 + 15%)
```

### **Step-by-Step Calculation:**

1. **Subtotal**: Base Price + $50 (Handling) + $300 (Logistics)
2. **Add Profit**: Subtotal × 1.20 (20% profit margin)
3. **Add Markup**: Result × 1.15 (15% markup margin)
4. **Final Price**: Rounded to 2 decimal places

## 📋 **Example Calculations**

### **FURN-001: Modern Dining Chair**
- **Base Price**: $150.00
- **Handling**: $50.00
- **Logistics**: $300.00
- **Subtotal**: $500.00
- **+ 20% Profit**: $600.00
- **+ 15% Markup**: $690.00
- **Final Price**: $690.00

### **FURN-002: Wooden Coffee Table**
- **Base Price**: $300.00
- **Handling**: $50.00
- **Logistics**: $300.00
- **Subtotal**: $650.00
- **+ 20% Profit**: $780.00
- **+ 15% Markup**: $897.00
- **Final Price**: $897.00

### **FURN-003: Leather Sofa**
- **Base Price**: $800.00
- **Handling**: $50.00
- **Logistics**: $300.00
- **Subtotal**: $1,150.00
- **+ 20% Profit**: $1,380.00
- **+ 15% Markup**: $1,587.00
- **Final Price**: $1,587.00

### **FURN-004: Glass Dining Table**
- **Base Price**: $400.00
- **Handling**: $50.00
- **Logistics**: $300.00
- **Subtotal**: $750.00
- **+ 20% Profit**: $900.00
- **+ 15% Markup**: $1,035.00
- **Final Price**: $1,035.00

### **FURN-005: Office Desk**
- **Base Price**: $350.00
- **Handling**: $50.00
- **Logistics**: $300.00
- **Subtotal**: $700.00
- **+ 20% Profit**: $840.00
- **+ 15% Markup**: $966.00
- **Final Price**: $966.00

## 💡 **Pricing Components**

### **Fixed Charges**
- **Handling**: $50 per item (packaging, processing)
- **Logistics**: $300 per item (shipping, delivery)

### **Variable Margins**
- **Profit Margin**: 20% (business profit)
- **Markup Margin**: 15% (retail markup)

### **Total Margin Calculation**
```
Total Margin = (1 + 20%) × (1 + 15%) - 1 = 38%
```

## 📊 **Pricing Summary**

| SKU | Base Price | Final Price | Total Markup | Margin % |
|-----|------------|-------------|--------------|----------|
| FURN-001 | $150.00 | $690.00 | $540.00 | 360% |
| FURN-002 | $300.00 | $897.00 | $597.00 | 199% |
| FURN-003 | $800.00 | $1,587.00 | $787.00 | 98% |
| FURN-004 | $400.00 | $1,035.00 | $635.00 | 159% |
| FURN-005 | $350.00 | $966.00 | $616.00 | 176% |

## 🎯 **Business Benefits**

### **Transparent Pricing**
- Clear breakdown of all costs
- Easy to adjust margins
- Professional pricing structure

### **Profitability**
- 20% profit margin ensures business sustainability
- 15% markup covers retail operations
- Fixed charges cover operational costs

### **Scalability**
- Formula works for any base price
- Consistent margin application
- Easy to modify rates

## 🚀 **Usage**

```bash
# Test with enhanced pricing
python main.py data/demo_products_enhanced_pricing.xlsx --dry-run

# Full upload with real API credentials
python main.py data/demo_products_enhanced_pricing.xlsx
```

This enhanced pricing structure provides complete transparency and professional pricing calculations for your Shopify Product Upload System! 💰✨
