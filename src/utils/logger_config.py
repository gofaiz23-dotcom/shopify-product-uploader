"""
Logging Configuration for Shopify Product Upload System
Provides comprehensive logging setup with file and console output
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class LoggerConfig:
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Initialize logging configuration
        
        Args:
            log_dir (str): Directory for log files
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamp for log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configure root logger
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                # Console handler
                logging.StreamHandler(),
                # File handler for all logs
                logging.FileHandler(self.log_dir / f"shopify_upload_{timestamp}.log"),
                # File handler for errors only
                logging.FileHandler(self.log_dir / f"errors_{timestamp}.log")
            ]
        )
        
        # Set error handler to only log ERROR and CRITICAL
        error_handler = logging.FileHandler(self.log_dir / f"errors_{timestamp}.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Add error handler to root logger
        logging.getLogger().addHandler(error_handler)
        
        # Configure specific loggers
        self._configure_module_loggers()
    
    def _configure_module_loggers(self):
        """Configure specific module loggers"""
        # Excel reader logger
        excel_logger = logging.getLogger('excel_reader')
        excel_logger.setLevel(logging.INFO)
        
        # AI description generator logger
        ai_logger = logging.getLogger('ai_description_generator')
        ai_logger.setLevel(logging.INFO)
        
        # Shopify API client logger
        shopify_logger = logging.getLogger('shopify_api_client')
        shopify_logger.setLevel(logging.INFO)
        
        # Main application logger
        main_logger = logging.getLogger('main')
        main_logger.setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance
        
        Args:
            name (str): Logger name
            
        Returns:
            logging.Logger: Logger instance
        """
        return logging.getLogger(name)

class UploadLogger:
    """
    Specialized logger for upload operations with detailed tracking
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize upload logger
        
        Args:
            log_dir (str): Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.upload_log_file = self.log_dir / f"upload_results_{timestamp}.log"
        self.error_log_file = self.log_dir / f"upload_errors_{timestamp}.log"
        
        # Setup upload-specific loggers
        self.upload_logger = logging.getLogger('upload_results')
        self.upload_logger.setLevel(logging.INFO)
        
        # File handler for upload results
        upload_handler = logging.FileHandler(self.upload_log_file)
        upload_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.upload_logger.addHandler(upload_handler)
        
        # Error logger
        self.error_logger = logging.getLogger('upload_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(self.error_log_file)
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.error_logger.addHandler(error_handler)
    
    def log_upload_success(self, sku: str, product_id: int, title: str):
        """
        Log successful product upload
        
        Args:
            sku (str): Product SKU
            product_id (int): Shopify product ID
            title (str): Product title
        """
        message = f"SUCCESS - SKU: {sku}, Product ID: {product_id}, Title: {title}"
        self.upload_logger.info(message)
    
    def log_upload_failure(self, sku: str, error_message: str, product_data: Optional[Dict] = None):
        """
        Log failed product upload
        
        Args:
            sku (str): Product SKU
            error_message (str): Error message
            product_data (Optional[Dict]): Product data for debugging
        """
        message = f"FAILED - SKU: {sku}, Error: {error_message}"
        self.upload_logger.error(message)
        self.error_logger.error(message)
        
        if product_data:
            self.error_logger.error(f"Product data: {product_data}")
    
    def log_processing_stats(self, total_products: int, successful: int, failed: int, skipped: int):
        """
        Log processing statistics
        
        Args:
            total_products (int): Total products processed
            successful (int): Successfully uploaded products
            failed (int): Failed uploads
            skipped (int): Skipped products
        """
        stats = f"""
PROCESSING COMPLETE
==================
Total Products: {total_products}
Successful: {successful}
Failed: {failed}
Skipped: {skipped}
Success Rate: {(successful/total_products*100):.1f}%
        """
        self.upload_logger.info(stats)
    
    def log_batch_start(self, batch_number: int, batch_size: int):
        """
        Log batch processing start
        
        Args:
            batch_number (int): Batch number
            batch_size (int): Batch size
        """
        message = f"Starting batch {batch_number} with {batch_size} products"
        self.upload_logger.info(message)
    
    def log_batch_complete(self, batch_number: int, successful: int, failed: int):
        """
        Log batch processing completion
        
        Args:
            batch_number (int): Batch number
            successful (int): Successful uploads in batch
            failed (int): Failed uploads in batch
        """
        message = f"Completed batch {batch_number} - Success: {successful}, Failed: {failed}"
        self.upload_logger.info(message)

class ErrorHandler:
    """
    Centralized error handling for the upload system
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize error handler
        
        Args:
            logger (logging.Logger): Logger instance
        """
        self.logger = logger
    
    def handle_excel_error(self, error: Exception, file_path: str) -> bool:
        """
        Handle Excel reading errors
        
        Args:
            error (Exception): The error that occurred
            file_path (str): Path to Excel file
            
        Returns:
            bool: True if error was handled, False if critical
        """
        error_msg = f"Excel reading error for {file_path}: {str(error)}"
        self.logger.error(error_msg)
        
        # Check if it's a critical error
        if "Permission denied" in str(error):
            self.logger.critical("Excel file is locked or in use. Please close the file and try again.")
            return False
        elif "No such file" in str(error):
            self.logger.critical(f"Excel file not found: {file_path}")
            return False
        else:
            self.logger.warning("Non-critical Excel error, attempting to continue...")
            return True
    
    def handle_api_error(self, error: Exception, sku: str, operation: str) -> bool:
        """
        Handle API errors
        
        Args:
            error (Exception): The error that occurred
            sku (str): Product SKU
            operation (str): Operation being performed
            
        Returns:
            bool: True if error was handled, False if critical
        """
        error_msg = f"API error for SKU {sku} during {operation}: {str(error)}"
        self.logger.error(error_msg)
        
        # Check error type
        if "Rate limit" in str(error) or "429" in str(error):
            self.logger.warning("Rate limit reached, will retry after delay")
            return True
        elif "Authentication" in str(error) or "401" in str(error):
            self.logger.critical("Authentication failed. Check API credentials.")
            return False
        elif "Not found" in str(error) or "404" in str(error):
            self.logger.warning(f"Resource not found for SKU {sku}")
            return True
        else:
            self.logger.warning(f"API error for SKU {sku}, will skip and continue")
            return True
    
    def handle_ai_error(self, error: Exception, sku: str) -> bool:
        """
        Handle AI description generation errors
        
        Args:
            error (Exception): The error that occurred
            sku (str): Product SKU
            
        Returns:
            bool: True if error was handled, False if critical
        """
        error_msg = f"AI generation error for SKU {sku}: {str(error)}"
        self.logger.error(error_msg)
        
        if "API key" in str(error) or "Authentication" in str(error):
            self.logger.critical("OpenAI API authentication failed. Check API key.")
            return False
        elif "Rate limit" in str(error):
            self.logger.warning("OpenAI rate limit reached, will retry")
            return True
        else:
            self.logger.warning(f"AI error for SKU {sku}, will use fallback description")
            return True
    
    def handle_validation_error(self, error: Exception, sku: str, field: str) -> bool:
        """
        Handle data validation errors
        
        Args:
            error (Exception): The error that occurred
            sku (str): Product SKU
            field (str): Field that failed validation
            
        Returns:
            bool: True if error was handled, False if critical
        """
        error_msg = f"Validation error for SKU {sku}, field '{field}': {str(error)}"
        self.logger.error(error_msg)
        
        # Log the error but continue processing
        self.logger.warning(f"Skipping SKU {sku} due to validation error in field '{field}'")
        return True

def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging for the application
    
    Args:
        log_dir (str): Directory for log files
        log_level (str): Logging level
        
    Returns:
        logging.Logger: Main logger instance
    """
    logger_config = LoggerConfig(log_dir, log_level)
    return logger_config.get_logger('main')

def get_upload_logger(log_dir: str = "logs") -> UploadLogger:
    """
    Get upload logger instance
    
    Args:
        log_dir (str): Directory for log files
        
    Returns:
        UploadLogger: Upload logger instance
    """
    return UploadLogger(log_dir)

