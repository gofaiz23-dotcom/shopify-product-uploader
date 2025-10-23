#!/usr/bin/env python3
"""
Shopify Upload with Pre-generated Descriptions
Uploads products to Shopify using pre-generated descriptions from Excel sheet
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

# Add src to path (scripts directory is one level up from src)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core import ExcelReader, BatchProcessor, ProductProcessor, PricingCalculator
from src.api import ShopifyAPIClient
from src.reports import ExcelReportGenerator
from src.config import ConfigManager
from src.utils import setup_logging, get_upload_logger

class ShopifyUploadWithDescriptions:
    """
    Shopify upload system that uses pre-generated descriptions
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize upload system
        
        Args:
            config_file (Optional[str]): Path to configuration file
        """
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_all()
        
        # Setup logging
        logging_config = self.config_manager.get_logging_config()
        self.logger = setup_logging(
            log_dir="logs",
            log_level=logging_config['log_level']
        )
        self.upload_logger = get_upload_logger()
        
        # Initialize components
        self.shopify_client = None
        self.batch_processor = None
        self.product_processor = None
        self.report_generator = None
        self.pricing_calculator = None
        
        self.logger.info("Shopify Upload with Descriptions System initialized")
    
    def initialize_components(self):
        """Initialize all system components"""
        try:
            # Get configuration
            shopify_config = self.config_manager.get_shopify_config()
            processing_config = self.config_manager.get_processing_config()
            report_config = self.config_manager.get_report_config()
            pricing_config = self.config_manager.get_pricing_config()
            
            # Initialize pricing calculator
            self.logger.info("Initializing pricing calculator...")
            self.pricing_calculator = PricingCalculator(pricing_config)
            
            # Initialize Shopify API client
            self.logger.info("Initializing Shopify API client...")
            self.shopify_client = ShopifyAPIClient(
                shop_url=shopify_config['shop_url'],
                api_key=shopify_config['api_key'],
                api_password=shopify_config['api_password']
            )
            
            # Test Shopify connection
            if not self.shopify_client.test_connection():
                self.logger.error("Failed to connect to Shopify API. Please check your credentials.")
                sys.exit(1)
            
            # Initialize batch processor
            self.logger.info("Initializing batch processor...")
            self.batch_processor = BatchProcessor(
                batch_size=processing_config['batch_size'],
                max_workers=processing_config['max_workers'],
                delay_between_batches=processing_config['delay_between_batches']
            )
            
            # Initialize product processor (without description scraper)
            self.logger.info("Initializing product processor...")
            self.product_processor = ProductProcessor(
                shopify_client=self.shopify_client,
                description_scraper=None,  # No description generation needed
                upload_logger=self.upload_logger,
                pricing_calculator=self.pricing_calculator
            )
            
            # Initialize report generator
            self.logger.info("Initializing report generator...")
            self.report_generator = ExcelReportGenerator(output_dir=report_config['report_dir'])
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {str(e)}")
            sys.exit(1)
    
    def process_excel_file(self, excel_file_path: str) -> Optional[pd.DataFrame]:
        """
        Process Excel file and return product data with descriptions
        
        Args:
            excel_file_path (str): Path to Excel file
            
        Returns:
            Optional[pd.DataFrame]: Product data with descriptions
        """
        try:
            self.logger.info(f"Processing Excel file: {excel_file_path}")
            
            # Read Excel file
            excel_reader = ExcelReader(excel_file_path)
            products_data = excel_reader.get_merged_data()
            
            if products_data is None:
                self.logger.error("Failed to read Excel file")
                return None
            
            # Check if descriptions exist
            if 'generated_description' not in products_data.columns:
                self.logger.error("No 'generated_description' column found in Excel file")
                self.logger.error("Please run generate_descriptions.py first to generate descriptions")
                return None
            
            # Filter products with descriptions
            products_with_descriptions = products_data[products_data['generated_description'].notna()]
            products_without_descriptions = products_data[products_data['generated_description'].isna()]
            
            self.logger.info(f"Found {len(products_with_descriptions)} products with descriptions")
            if len(products_without_descriptions) > 0:
                self.logger.warning(f"Found {len(products_without_descriptions)} products without descriptions")
            
            return products_with_descriptions
            
        except Exception as e:
            self.logger.error(f"Error processing Excel file: {str(e)}")
            return None
    
    def upload_products(self, products_data: pd.DataFrame, dry_run: bool = False) -> Dict[str, any]:
        """
        Upload products to Shopify using pre-generated descriptions
        
        Args:
            products_data (pd.DataFrame): Product data with descriptions
            dry_run (bool): If True, only validate data without uploading
            
        Returns:
            Dict[str, any]: Upload results
        """
        try:
            # Convert DataFrame to list of dictionaries
            products_list = products_data.to_dict('records')
            
            if dry_run:
                self.logger.info("DRY RUN MODE - No products will be uploaded")
                return self._validate_products(products_list)
            
            # Process products in batches
            self.logger.info(f"Starting upload of {len(products_list)} products with pre-generated descriptions")
            
            results = self.batch_processor.process_products(
                products_data=products_list,
                process_function=self.product_processor.process_product
            )
            
            # Log final statistics
            self.upload_logger.log_processing_stats(
                total_products=results['total_processed'],
                successful=results['successful'],
                failed=results['failed'],
                skipped=results['skipped']
            )
            
            # Generate Excel report
            if not dry_run:
                self.logger.info("Generating Excel report...")
                report_path = self.report_generator.generate_upload_report(
                    upload_results=results,
                    products_data=products_list,
                    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                )
                self.logger.info(f"Excel report generated: {report_path}")
                results['report_path'] = report_path
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error uploading products: {str(e)}")
            return {
                'total_processed': 0,
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 1,
                'success_rate': 0,
                'error_message': str(e)
            }
    
    def _validate_products(self, products_list: List[Dict]) -> Dict[str, any]:
        """
        Validate products without uploading (dry run)
        
        Args:
            products_list (List[Dict]): List of product data
            
        Returns:
            Dict[str, any]: Validation results
        """
        validation_results = {
            'total_processed': len(products_list),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'success_rate': 0,
            'validation_errors': []
        }
        
        for product_data in products_list:
            sku = product_data.get('sku', 'unknown')
            
            # Check required fields
            required_fields = ['sku', 'title', 'price', 'generated_description']
            missing_fields = [field for field in required_fields if not product_data.get(field)]
            
            if missing_fields:
                validation_results['failed'] += 1
                validation_results['validation_errors'].append({
                    'sku': sku,
                    'error': f"Missing required fields: {missing_fields}"
                })
            else:
                validation_results['successful'] += 1
        
        validation_results['success_rate'] = (
            validation_results['successful'] / validation_results['total_processed'] * 100
            if validation_results['total_processed'] > 0 else 0
        )
        
        return validation_results
    
    def run(self, excel_file_path: str, dry_run: bool = False):
        """
        Run the complete upload process
        
        Args:
            excel_file_path (str): Path to Excel file with descriptions
            dry_run (bool): If True, only validate without uploading
        """
        try:
            self.logger.info("Starting Shopify Upload with Pre-generated Descriptions")
            self.logger.info(f"Excel file: {excel_file_path}")
            self.logger.info(f"Dry run: {dry_run}")
            
            # Initialize components
            self.initialize_components()
            
            # Process Excel file
            products_data = self.process_excel_file(excel_file_path)
            if products_data is None:
                self.logger.error("Failed to process Excel file. Exiting.")
                return
            
            # Upload products
            results = self.upload_products(products_data, dry_run=dry_run)
            
            # Print summary
            self._print_summary(results)
            
            self.logger.info("Upload process completed")
            
        except Exception as e:
            self.logger.error(f"Error in main process: {str(e)}")
            sys.exit(1)
    
    def _print_summary(self, results: Dict[str, any]):
        """
        Print processing summary
        
        Args:
            results (Dict[str, any]): Processing results
        """
        print("\n" + "="*50)
        print("UPLOAD SUMMARY")
        print("="*50)
        print(f"Total Products: {results['total_processed']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped: {results['skipped']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        
        if results.get('validation_errors'):
            print(f"\nValidation Errors: {len(results['validation_errors'])}")
            for error in results['validation_errors'][:5]:  # Show first 5 errors
                print(f"  - SKU {error['sku']}: {error['error']}")
            if len(results['validation_errors']) > 5:
                print(f"  ... and {len(results['validation_errors']) - 5} more errors")
        
        print("="*50)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Shopify Upload with Pre-generated Descriptions')
    parser.add_argument('excel_file', help='Path to Excel file with generated descriptions')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Validate data without uploading to Shopify')
    parser.add_argument('--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Check if Excel file exists
    if not os.path.exists(args.excel_file):
        print(f"Error: Excel file '{args.excel_file}' not found")
        sys.exit(1)
    
    # Create and run the system
    system = ShopifyUploadWithDescriptions(config_file=args.config)
    system.run(args.excel_file, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
