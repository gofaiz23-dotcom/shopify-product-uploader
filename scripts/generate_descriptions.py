#!/usr/bin/env python3
"""
Standalone Description Generator
Generates product descriptions using AI Fiesta and saves them to Excel sheet
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add src to path (scripts directory is one level up from src)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.selenium_description_scraper import SeleniumDescriptionScraper
from src.core.excel_reader import ExcelReader
from src.config import ConfigManager
from src.utils import setup_logging

class DescriptionGenerator:
    """
    Standalone description generator that reads from Excel and saves descriptions
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize description generator
        
        Args:
            config_file (Optional[str]): Path to configuration file
        """
        # Setup logging
        self.logger = setup_logging(
            log_dir="logs",
            log_level="INFO"
        )
        
        # Initialize configuration
        self.config_manager = ConfigManager(config_file)
        self.selenium_config = self.config_manager.get_selenium_config()
        self.ai_fiesta_config = self.config_manager.get_ai_fiesta_config()
        
        # Initialize Selenium scraper
        self.scraper = SeleniumDescriptionScraper(
            headless=self.selenium_config['headless'],
            wait_timeout=self.selenium_config['wait_timeout']
        )
        
        self.logger.info("Description Generator initialized")
    
    def generate_descriptions_for_sheet(self, excel_file_path: str, output_file_path: Optional[str] = None) -> str:
        """
        Generate descriptions for all products in Excel sheet and save to new sheet
        
        Args:
            excel_file_path (str): Path to input Excel file
            output_file_path (Optional[str]): Path to output Excel file (optional)
            
        Returns:
            str: Path to output file with descriptions
        """
        try:
            self.logger.info(f"Starting description generation for: {excel_file_path}")
            
            # Read Excel file
            excel_reader = ExcelReader(excel_file_path)
            products_data = excel_reader.get_merged_data()
            
            if products_data is None:
                self.logger.error("Failed to read Excel file")
                return None
            
            self.logger.info(f"Found {len(products_data)} products to process")
            
            # Generate descriptions
            descriptions = self._generate_descriptions_batch(products_data)
            
            # Add descriptions to DataFrame
            products_data['generated_description'] = descriptions
            products_data['description_generated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to output file
            if output_file_path is None:
                # Create output filename
                input_path = Path(excel_file_path)
                output_file_path = input_path.parent / f"{input_path.stem}_with_descriptions{input_path.suffix}"
            
            # Save to Excel
            with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                # Save main data with descriptions
                products_data.to_excel(writer, sheet_name='Products_with_Descriptions', index=False)
                
                # Create summary sheet
                summary_data = self._create_summary_data(products_data, descriptions)
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Description_Summary', index=False)
            
            self.logger.info(f"Descriptions saved to: {output_file_path}")
            return str(output_file_path)
            
        except Exception as e:
            self.logger.error(f"Error generating descriptions: {str(e)}")
            return None
    
    def _generate_descriptions_batch(self, products_data: pd.DataFrame) -> List[str]:
        """
        Generate descriptions for a batch of products
        
        Args:
            products_data (pd.DataFrame): Products data
            
        Returns:
            List[str]: Generated descriptions
        """
        descriptions = []
        total_products = len(products_data)
        
        self.logger.info(f"Generating descriptions for {total_products} products...")
        
        for index, row in products_data.iterrows():
            try:
                # Convert row to dictionary
                product_data = row.to_dict()
                sku = product_data.get('sku', f'Product_{index}')
                
                self.logger.info(f"Processing {index + 1}/{total_products}: {sku}")
                
                # Check if description already exists
                if 'generated_description' in product_data and product_data['generated_description']:
                    self.logger.info(f"Description already exists for {sku}, skipping...")
                    descriptions.append(product_data['generated_description'])
                    continue
                
                # Generate description using AI Fiesta
                description = self.scraper.generate_description(product_data)
                
                if description and len(description) > 50:
                    descriptions.append(description)
                    self.logger.info(f"✅ Generated description for {sku} ({len(description)} chars)")
                else:
                    # Use fallback description
                    fallback = self.scraper._create_fallback_description(product_data)
                    descriptions.append(fallback)
                    self.logger.warning(f"⚠️ Used fallback description for {sku}")
                
                # Add delay between products to avoid being blocked
                import time
                import random
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                self.logger.error(f"Error generating description for {sku}: {str(e)}")
                # Use fallback description
                fallback = self.scraper._create_fallback_description(product_data)
                descriptions.append(fallback)
        
        return descriptions
    
    def _create_summary_data(self, products_data: pd.DataFrame, descriptions: List[str]) -> List[Dict]:
        """Create summary data for the description generation process"""
        total_products = len(products_data)
        successful_descriptions = sum(1 for desc in descriptions if len(desc) > 100)
        fallback_descriptions = total_products - successful_descriptions
        
        return [
            {
                'Metric': 'Total Products',
                'Value': total_products
            },
            {
                'Metric': 'Successful Descriptions',
                'Value': successful_descriptions
            },
            {
                'Metric': 'Fallback Descriptions',
                'Value': fallback_descriptions
            },
            {
                'Metric': 'Success Rate',
                'Value': f"{(successful_descriptions / total_products * 100):.1f}%" if total_products > 0 else "0%"
            },
            {
                'Metric': 'Generation Date',
                'Value': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    
    def generate_descriptions_for_products(self, products_data: List[Dict]) -> List[str]:
        """
        Generate descriptions for a list of product dictionaries
        
        Args:
            products_data (List[Dict]): List of product data dictionaries
            
        Returns:
            List[str]: Generated descriptions
        """
        descriptions = []
        
        for i, product_data in enumerate(products_data):
            try:
                sku = product_data.get('sku', f'Product_{i}')
                self.logger.info(f"Generating description for {sku}")
                
                description = self.scraper.generate_description(product_data)
                descriptions.append(description)
                
            except Exception as e:
                self.logger.error(f"Error generating description for {sku}: {str(e)}")
                fallback = self.scraper._create_fallback_description(product_data)
                descriptions.append(fallback)
        
        return descriptions

def main():
    """Main function for standalone description generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate product descriptions using AI Fiesta')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('-o', '--output', help='Path to output Excel file (optional)')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    # Create description generator
    generator = DescriptionGenerator(config_file=args.config)
    
    # Override headless mode if specified
    if args.headless:
        generator.scraper.headless = True
    
    print("="*60)
    print("AI FIESTA DESCRIPTION GENERATOR")
    print("="*60)
    print(f"Input file: {args.input_file}")
    print(f"Output file: {args.output or 'Auto-generated'}")
    print("="*60)
    
    # Generate descriptions
    output_file = generator.generate_descriptions_for_sheet(
        excel_file_path=args.input_file,
        output_file_path=args.output
    )
    
    if output_file:
        print(f"\n✅ Descriptions generated successfully!")
        print(f"📁 Output file: {output_file}")
        print(f"\nYou can now use this file for Shopify upload with pre-generated descriptions.")
    else:
        print(f"\n❌ Failed to generate descriptions")
        sys.exit(1)

if __name__ == "__main__":
    main()
