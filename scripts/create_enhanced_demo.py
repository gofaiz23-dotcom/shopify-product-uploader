"""
Create enhanced demo Excel data with proper pricing calculations
"""

import pandas as pd
import os

def calculate_final_price(base_price, handling=50, logistics=300, profit_margin=0.20, markup_margin=0.15):
    """
    Calculate final price with all charges
    
    Formula: (Base Price + Handling + Logistics) * (1 + Profit) * (1 + Markup)
    """
    subtotal = base_price + handling + logistics
    with_profit = subtotal * (1 + profit_margin)
    final_price = with_profit * (1 + markup_margin)
    return round(final_price, 2)

def create_enhanced_demo_excel():
    """Create enhanced demo Excel file with proper pricing calculations"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # 5 products with base prices
    base_skus = ['FURN-001', 'FURN-002', 'FURN-003', 'FURN-004', 'FURN-005']
    base_prices = [150.00, 300.00, 800.00, 400.00, 350.00]  # Base item prices
    
    # Calculate final prices with all charges
    final_prices = []
    pricing_breakdown = []
    
    for base_price in base_prices:
        final_price = calculate_final_price(base_price)
        final_prices.append(final_price)
        
        # Create pricing breakdown
        handling = 50
        logistics = 300
        subtotal = base_price + handling + logistics
        profit_amount = subtotal * 0.20
        with_profit = subtotal + profit_amount
        markup_amount = with_profit * 0.15
        final_calc = with_profit + markup_amount
        
        breakdown = {
            'base_price': base_price,
            'handling': handling,
            'logistics': logistics,
            'subtotal': subtotal,
            'profit_20%': profit_amount,
            'with_profit': with_profit,
            'markup_15%': markup_amount,
            'final_price': final_price
        }
        pricing_breakdown.append(breakdown)
    
    # 1. Items Sheet - Main product information with enhanced pricing
    items_data = {
        'SKU': base_skus,
        'Title': [
            'Modern Dining Chair',
            'Wooden Coffee Table', 
            'Leather Sofa',
            'Glass Dining Table',
            'Office Desk'
        ],
        'Base_Price': base_prices,
        'Handling_Charges': [50] * 5,
        'Logistics_Charges': [300] * 5,
        'Profit_Margin_20%': [round((base_prices[i] + 50 + 300) * 0.20, 2) for i in range(5)],
        'Markup_Charges_15%': [round(((base_prices[i] + 50 + 300) * 1.20) * 0.15, 2) for i in range(5)],
        'Final_Price': final_prices,
        'Category': ['Furniture', 'Furniture', 'Furniture', 'Furniture', 'Furniture'],
        'Brand': [
            'Acme Furniture',
            'WoodCraft',
            'Luxury Living', 
            'Modern Glass',
            'Office Pro'
        ],
        'Features': [
            'Ergonomic design, Easy assembly, Adjustable height',
            'Solid wood construction, Handcrafted, Natural finish',
            'Premium leather, Comfortable seating, Reclining function',
            'Tempered glass top, Modern design, Easy to clean',
            'Spacious workspace, Cable management, Drawer storage'
        ],
        'Material': [
            'Solid wood, Metal legs, Fabric upholstery',
            'Oak wood, Natural finish, Metal hardware',
            'Genuine leather, Steel frame, Foam cushioning',
            'Tempered glass, Chrome legs, Rubber feet',
            'MDF top, Metal legs, Plastic handles'
        ]
    }
    
    # 2. Stock Sheet - Inventory management
    stock_data = {
        'SKU': base_skus,
        'Quantity': [50, 25, 10, 15, 30],
        'Min_Stock': [10, 5, 2, 3, 6],
        'Max_Stock': [100, 50, 20, 30, 60],
        'Reorder_Point': [15, 8, 3, 5, 10],
        'Location': ['Warehouse A', 'Warehouse B', 'Warehouse A', 'Warehouse C', 'Warehouse B'],
        'Status': ['In Stock', 'Low Stock', 'In Stock', 'In Stock', 'In Stock'],
        'Cost_Per_Unit': base_prices,
        'Total_Inventory_Value': [round(base_prices[i] * [50, 25, 10, 15, 30][i], 2) for i in range(5)]
    }
    
    # 3. Images Sheet - Picture links
    images_data = {
        'SKU': base_skus,
        'Image_Links': [
            'https://example.com/chair1.jpg, https://example.com/chair2.jpg, https://example.com/chair3.jpg',
            'https://example.com/table1.jpg, https://example.com/table2.jpg, https://example.com/table3.jpg',
            'https://example.com/sofa1.jpg, https://example.com/sofa2.jpg, https://example.com/sofa3.jpg',
            'https://example.com/dining1.jpg, https://example.com/dining2.jpg, https://example.com/dining3.jpg',
            'https://example.com/desk1.jpg, https://example.com/desk2.jpg, https://example.com/desk3.jpg'
        ],
        'Primary_Image': [
            'https://example.com/chair1.jpg',
            'https://example.com/table1.jpg', 
            'https://example.com/sofa1.jpg',
            'https://example.com/dining1.jpg',
            'https://example.com/desk1.jpg'
        ],
        'Image_Count': [3, 3, 3, 3, 3],
        'Image_Quality': ['HD', 'HD', 'HD', 'HD', 'HD']
    }
    
    # 4. Specs Sheet - Detailed specifications
    specs_data = {
        'SKU': base_skus,
        'Weight': ['15.5 lbs', '45.2 lbs', '120.8 lbs', '65.3 lbs', '85.7 lbs'],
        'Dimensions': [
            '24" W x 18" D x 32" H',
            '48" W x 24" D x 18" H', 
            '84" W x 36" D x 32" H',
            '60" W x 36" D x 30" H',
            '48" W x 24" D x 30" H'
        ],
        'Color': ['Black', 'Natural Oak', 'Brown Leather', 'Clear Glass', 'White'],
        'Finish': ['Matte', 'Natural', 'Smooth', 'Polished', 'Smooth'],
        'Assembly_Required': ['Yes', 'Yes', 'No', 'Yes', 'Yes'],
        'Warranty': ['2 Years', '5 Years', '3 Years', '1 Year', '2 Years'],
        'Country_Origin': ['USA', 'Canada', 'Italy', 'Germany', 'USA'],
        'Certification': ['FSC Certified', 'GREENGUARD', 'OEKO-TEX', 'ISO 9001', 'FSC Certified']
    }
    
    # 5. Pricing Sheet - Detailed pricing breakdown
    pricing_data = {
        'SKU': base_skus,
        'Base_Item_Price': base_prices,
        'Handling_Charges': [50] * 5,
        'Logistics_Charges': [300] * 5,
        'Subtotal_Before_Margins': [base_prices[i] + 50 + 300 for i in range(5)],
        'Profit_20_Percent': [round((base_prices[i] + 50 + 300) * 0.20, 2) for i in range(5)],
        'Price_After_Profit': [round((base_prices[i] + 50 + 300) * 1.20, 2) for i in range(5)],
        'Markup_15_Percent': [round(((base_prices[i] + 50 + 300) * 1.20) * 0.15, 2) for i in range(5)],
        'Final_Selling_Price': final_prices,
        'Profit_Margin_Amount': [round((base_prices[i] + 50 + 300) * 0.20, 2) for i in range(5)],
        'Markup_Margin_Amount': [round(((base_prices[i] + 50 + 300) * 1.20) * 0.15, 2) for i in range(5)]
    }
    
    # Create Excel file with multiple sheets
    output_file = 'data/demo_products_enhanced_pricing.xlsx'
    
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Items sheet with enhanced pricing
            pd.DataFrame(items_data).to_excel(writer, sheet_name='Items', index=False)
            
            # Stock sheet  
            pd.DataFrame(stock_data).to_excel(writer, sheet_name='Stock', index=False)
            
            # Images sheet
            pd.DataFrame(images_data).to_excel(writer, sheet_name='Images', index=False)
            
            # Specs sheet
            pd.DataFrame(specs_data).to_excel(writer, sheet_name='Specs', index=False)
            
            # Pricing sheet - NEW
            pd.DataFrame(pricing_data).to_excel(writer, sheet_name='Pricing', index=False)
        
        print(f"Created enhanced demo Excel file: {output_file}")
        print(f"Generated {len(items_data)} products across 5 sheets:")
        print(f"   - Items sheet: {len(items_data)} products with enhanced pricing")
        print(f"   - Stock sheet: {len(stock_data)} inventory records")
        print(f"   - Images sheet: {len(images_data)} image records")
        print(f"   - Specs sheet: {len(specs_data)} specification records")
        print(f"   - Pricing sheet: {len(pricing_data)} pricing breakdowns")
        print("\nAll SKUs are consistent across all 5 sheets!")
        print("\nPricing Formula Applied:")
        print("   Final Price = (Base Price + Handling + Logistics) * (1 + 20%) * (1 + 15%)")
        print("\nPricing Breakdown:")
        for i, sku in enumerate(base_skus):
            print(f"   {sku}: Base ${base_prices[i]} + Handling $50 + Logistics $300 = ${base_prices[i] + 350}")
            print(f"         + 20% Profit = ${round((base_prices[i] + 350) * 1.20, 2)}")
            print(f"         + 15% Markup = ${final_prices[i]} (Final Price)")
        
    except Exception as e:
        print(f"Error creating enhanced demo Excel file: {str(e)}")

if __name__ == "__main__":
    create_enhanced_demo_excel()
