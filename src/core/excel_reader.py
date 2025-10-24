"""
Excel Reader Module for Shopify Product Upload System
Handles reading and merging multiple Excel sheets
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class ExcelReader:
    def __init__(self, excel_file_path: str):
        """
        Initialize Excel reader with file path
        
        Args:
            excel_file_path (str): Path to the Excel file
        """
        self.excel_file_path = Path(excel_file_path)
        self.sheets_data = {}
        self.logger = logging.getLogger(__name__)
        
    def read_excel_sheets(self) -> Dict[str, pd.DataFrame]:
        """
        Read all sheets from Excel file
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary with sheet names as keys and DataFrames as values
        """
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(self.excel_file_path)
            self.logger.info(f"Found {len(excel_file.sheet_names)} sheets: {excel_file.sheet_names}")
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
                    # Clean column names (remove extra spaces, convert to lowercase)
                    df.columns = df.columns.str.strip().str.lower()
                    self.sheets_data[sheet_name.lower()] = df
                    self.logger.info(f"Successfully read sheet '{sheet_name}' with {len(df)} rows")
                except Exception as e:
                    self.logger.error(f"Error reading sheet '{sheet_name}': {str(e)}")
                    
            return self.sheets_data
            
        except Exception as e:
            self.logger.error(f"Error reading Excel file: {str(e)}")
            raise
    
    def validate_required_columns(self, sheet_name: str, required_columns: List[str]) -> bool:
        """
        Validate that required columns exist in a sheet
        
        Args:
            sheet_name (str): Name of the sheet
            required_columns (List[str]): List of required column names
            
        Returns:
            bool: True if all required columns exist
        """
        if sheet_name not in self.sheets_data:
            self.logger.error(f"Sheet '{sheet_name}' not found")
            return False
            
        df = self.sheets_data[sheet_name]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.logger.error(f"Missing required columns in '{sheet_name}': {missing_columns}")
            return False
            
        return True
    
    def get_items_sheet(self) -> Optional[pd.DataFrame]:
        """
        Get the Items sheet with product information
        
        Returns:
            Optional[pd.DataFrame]: Items DataFrame or None if not found/invalid
        """
        required_columns = ['sku', 'title', 'price', 'category', 'brand']
        optional_columns = ['weight', 'weight_kg']
        
        # Try different possible sheet names for items
        possible_names = ['items', 'item', 'products', 'product', 'catalog', 'products_with_descriptions']
        
        for name in possible_names:
            if name in self.sheets_data:
                if self.validate_required_columns(name, required_columns):
                    return self.sheets_data[name]
        
        self.logger.error("Items sheet not found or missing required columns")
        return None
    
    def get_stock_sheet(self) -> Optional[pd.DataFrame]:
        """
        Get the Stock sheet with inventory information
        
        Returns:
            Optional[pd.DataFrame]: Stock DataFrame or None if not found/invalid
        """
        required_columns = ['sku', 'quantity']
        
        # Try different possible sheet names for stock
        possible_names = ['stock', 'inventory', 'quantities', 'qty']
        
        for name in possible_names:
            if name in self.sheets_data:
                if self.validate_required_columns(name, required_columns):
                    return self.sheets_data[name]
        
        self.logger.error("Stock sheet not found or missing required columns")
        return None
    
    def get_images_sheet(self) -> Optional[pd.DataFrame]:
        """
        Get the Images sheet with image URLs
        
        Returns:
            Optional[pd.DataFrame]: Images DataFrame or None if not found/invalid
        """
        required_columns = ['sku', 'image links']
        
        # Try different possible sheet names for images
        possible_names = ['images', 'image', 'photos', 'pictures']
        
        for name in possible_names:
            if name in self.sheets_data:
                if self.validate_required_columns(name, required_columns):
                    return self.sheets_data[name]
        
        self.logger.error("Images sheet not found or missing required columns")
        return None
    
    def merge_sheets(self) -> Optional[pd.DataFrame]:
        """
        Merge all sheets by SKU to create a unified product dataset
        
        Returns:
            Optional[pd.DataFrame]: Merged DataFrame or None if merge fails
        """
        try:
            # Get individual sheets
            items_df = self.get_items_sheet()
            stock_df = self.get_stock_sheet()
            images_df = self.get_images_sheet()
            
            if items_df is None:
                self.logger.error("Cannot merge sheets: Items sheet is required")
                return None
            
            # Start with items as base
            merged_df = items_df.copy()
            self.logger.info(f"Starting merge with {len(merged_df)} items")
            
            # Merge stock data
            if stock_df is not None:
                merged_df = merged_df.merge(
                    stock_df[['sku', 'quantity']], 
                    on='sku', 
                    how='left'
                )
                self.logger.info(f"Added stock data: {merged_df['quantity'].notna().sum()} products have stock info")
            else:
                merged_df['quantity'] = 0
                self.logger.warning("No stock data found, setting quantity to 0 for all products")
            
            # Merge image data
            if images_df is not None:
                merged_df = merged_df.merge(
                    images_df[['sku', 'image links']], 
                    on='sku', 
                    how='left'
                )
                self.logger.info(f"Added image data: {merged_df['image links'].notna().sum()} products have image info")
            else:
                merged_df['image links'] = ''
                self.logger.warning("No image data found, setting empty image links")
            
            # Clean up the merged data
            merged_df = self._clean_merged_data(merged_df)
            
            self.logger.info(f"Successfully merged data: {len(merged_df)} products ready for processing")
            return merged_df
            
        except Exception as e:
            self.logger.error(f"Error merging sheets: {str(e)}")
            return None
    
    def _clean_merged_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the merged DataFrame
        
        Args:
            df (pd.DataFrame): Merged DataFrame
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        # Remove rows with missing SKU
        initial_count = len(df)
        df = df.dropna(subset=['sku'])
        if len(df) < initial_count:
            self.logger.warning(f"Removed {initial_count - len(df)} rows with missing SKU")
        
        # Remove duplicates based on SKU
        initial_count = len(df)
        df = df.drop_duplicates(subset=['sku'])
        if len(df) < initial_count:
            self.logger.warning(f"Removed {initial_count - len(df)} duplicate SKUs")
        
        # Fill missing values
        df['quantity'] = df['quantity'].fillna(0)
        df['image links'] = df['image links'].fillna('')
        
        # Convert quantity to integer
        df['quantity'] = df['quantity'].astype(int)
        
        return df
    
    def get_merged_data(self) -> Optional[pd.DataFrame]:
        """
        Main method to read and merge all Excel sheets
        
        Returns:
            Optional[pd.DataFrame]: Merged product data or None if failed
        """
        # Read all sheets first
        self.read_excel_sheets()
        
        # Merge the sheets
        return self.merge_sheets()

