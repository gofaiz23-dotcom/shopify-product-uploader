"""
Create comprehensive demo Excel data with 4 sheets for testing
"""

import pandas as pd
import os

def create_demo_excel():
    """Create comprehensive demo Excel file with 4 sheets"""
    
    # 5 products with consistent SKUs across all sheets
    base_skus = ['FURN-001', 'FURN-002', 'FURN-003', 'FURN-004', 'FURN-005']
    
    # 1. Items Sheet - Main product information
    items_data = {
        'SKU': base_skus,
        'Title': [
            'Modern Dining Chair',
            'Wooden Coffee Table', 
            'Leather Sofa',
            'Glass Dining Table',
            'Office Desk'
        ],
        'Price': [299.99, 599.99, 1299.99, 899.99, 799.99],
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
        'Status': ['In Stock', 'Low Stock', 'In Stock', 'In Stock', 'In Stock']
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
    
    # Create Excel file with multiple sheets
    output_file = 'data/demo_products_comprehensive.xlsx'
    
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Items sheet
            pd.DataFrame(items_data).to_excel(writer, sheet_name='Items', index=False)
            
            # Stock sheet  
            pd.DataFrame(stock_data).to_excel(writer, sheet_name='Stock', index=False)
            
            # Images sheet
            pd.DataFrame(images_data).to_excel(writer, sheet_name='Images', index=False)
            
            # Specs sheet
            pd.DataFrame(specs_data).to_excel(writer, sheet_name='Specs', index=False)
        
        print(f"✅ Created comprehensive demo Excel file: {output_file}")
        print(f"📊 Generated {len(items_data)} products across 4 sheets:")
        print(f"   - Items sheet: {len(items_data)} products")
        print(f"   - Stock sheet: {len(stock_data)} inventory records")
        print(f"   - Images sheet: {len(images_data)} image records")
        print(f"   - Specs sheet: {len(specs_data)} specification records")
        print("\n🎯 All SKUs are consistent across all 4 sheets!")
        print("\n📋 Sheet Details:")
        print("   - Items: Product information, pricing, features")
        print("   - Stock: Inventory levels, reorder points, locations")
        print("   - Images: Picture links, primary images, quality info")
        print("   - Specs: Dimensions, weight, color, warranty, certifications")
        
    except Exception as e:
        print(f"❌ Error creating demo Excel file: {str(e)}")

if __name__ == "__main__":
    create_demo_excel()
