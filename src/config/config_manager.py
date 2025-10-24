"""
Configuration Manager for Shopify Product Upload System
Handles configuration loading, validation, and management
"""

import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file (Optional[str]): Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config = {}
        
        # Load configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables and config file"""
        # Load environment variables
        load_dotenv()
        
        # Default configuration
        self.config = {
            # Shopify API Configuration
            'shopify_shop_url': os.getenv('SHOPIFY_SHOP_URL', ''),
            'shopify_api_key': os.getenv('SHOPIFY_API_KEY', ''),
            'shopify_api_password': os.getenv('SHOPIFY_API_PASSWORD', ''),
            
            # Selenium Configuration
            'selenium_headless': os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true',
            'selenium_wait_timeout': int(os.getenv('SELENIUM_WAIT_TIMEOUT', '10')),
            
            # AI Fiesta Configuration
            'ai_fiesta_url': os.getenv('AI_FIESTA_URL', 'https://aifiesta.com/'),
            'ai_fiesta_wait_time': int(os.getenv('AI_FIESTA_WAIT_TIME', '15')),
            'ai_fiesta_retry_attempts': int(os.getenv('AI_FIESTA_RETRY_ATTEMPTS', '3')),
            
            # Processing Configuration
            'batch_size': int(os.getenv('BATCH_SIZE', '100')),
            'max_workers': int(os.getenv('MAX_WORKERS', '1')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'delay_between_batches': float(os.getenv('DELAY_BETWEEN_BATCHES', '1.0')),
            
            # Logging Configuration
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', 'logs/shopify_upload.log'),
            
            # Report Configuration
            'report_dir': os.getenv('REPORT_DIR', 'reports'),
            'backup_dir': os.getenv('BACKUP_DIR', 'backups'),
            
            
            # Shopify Configuration
            'shopify_api_version': os.getenv('SHOPIFY_API_VERSION', '2025-10'),
            'shopify_rate_limit': int(os.getenv('SHOPIFY_RATE_LIMIT', '1000')),
            
            # Validation Configuration
            'validate_images': os.getenv('VALIDATE_IMAGES', 'true').lower() == 'true',
            'validate_prices': os.getenv('VALIDATE_PRICES', 'true').lower() == 'true',
            'skip_duplicates': os.getenv('SKIP_DUPLICATES', 'false').lower() == 'true',
            
            # Retry Configuration
            'retry_delay': float(os.getenv('RETRY_DELAY', '2.0')),
            'max_retry_delay': float(os.getenv('MAX_RETRY_DELAY', '60.0')),
            'retry_backoff_factor': float(os.getenv('RETRY_BACKOFF_FACTOR', '2.0')),
            
            # Pricing Configuration
            'handling_charges': float(os.getenv('HANDLING_CHARGES', '50.0')),
            'logistics_charges': float(os.getenv('LOGISTICS_CHARGES', '300.0')),
            'marketplace_commission_percent': float(os.getenv('MARKETPLACE_COMMISSION_PERCENT', '15.0')),
            'profit_margin_percent': float(os.getenv('PROFIT_MARGIN_PERCENT', '20.0')),
            
            # Additional pricing configuration
            'use_dynamic_logistics': os.getenv('USE_DYNAMIC_LOGISTICS', 'false').lower() == 'true',
            'base_logistics_rate': float(os.getenv('BASE_LOGISTICS_RATE', '10.0')),
            'min_logistics_charge': float(os.getenv('MIN_LOGISTICS_CHARGE', '50.0')),
            'max_logistics_charge': float(os.getenv('MAX_LOGISTICS_CHARGE', '500.0')),
            'default_distance_km': float(os.getenv('DEFAULT_DISTANCE_KM', '100.0')),
            'default_weight_kg': float(os.getenv('DEFAULT_WEIGHT_KG', '1.0'))
        }
        
        # Load from config file if provided
        if self.config_file and os.path.exists(self.config_file):
            self._load_config_file()
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_config_file(self):
        """Load configuration from file"""
        try:
            if self.config_file.endswith('.env'):
                # Load .env file
                load_dotenv(self.config_file)
                # Reload environment variables
                self.config.update({
                    'shopify_shop_url': os.getenv('SHOPIFY_SHOP_URL', self.config['shopify_shop_url']),
                    'shopify_api_key': os.getenv('SHOPIFY_API_KEY', self.config['shopify_api_key']),
                    'shopify_api_password': os.getenv('SHOPIFY_API_PASSWORD', self.config['shopify_api_password']),
                    'openai_api_key': os.getenv('OPENAI_API_KEY', self.config['openai_api_key']),
                })
            else:
                # Load JSON or YAML config file
                import json
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            
            self.logger.info(f"Loaded configuration from {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Error loading config file {self.config_file}: {str(e)}")
            raise
    
    def _validate_configuration(self):
        """Validate required configuration"""
        required_config = [
            'shopify_shop_url',
            'shopify_api_key', 
            'shopify_api_password'
        ]
        
        missing_config = [key for key in required_config if not self.config[key]]
        
        if missing_config:
            self.logger.error(f"Missing required configuration: {missing_config}")
            self.logger.error("Please set the required environment variables or create a .env file")
            raise ValueError(f"Missing required configuration: {missing_config}")
        
        # Validate numeric values
        numeric_configs = [
            'batch_size', 'max_workers', 'max_retries', 'delay_between_batches',
            'shopify_rate_limit', 'retry_delay', 'max_retry_delay', 'retry_backoff_factor'
        ]
        
        for config_key in numeric_configs:
            if not isinstance(self.config[config_key], (int, float)):
                self.logger.warning(f"Invalid numeric value for {config_key}: {self.config[config_key]}")
                # Set default value
                defaults = {
                    'batch_size': 100,
                    'max_workers': 1,
                    'max_retries': 3,
                    'delay_between_batches': 1.0,
                    'shopify_rate_limit': 1000,
                    'retry_delay': 2.0,
                    'max_retry_delay': 60.0,
                    'retry_backoff_factor': 2.0
                }
                self.config[config_key] = defaults.get(config_key, 0)
        
        # Validate boolean values
        boolean_configs = ['validate_images', 'validate_prices', 'skip_duplicates']
        for config_key in boolean_configs:
            if not isinstance(self.config[config_key], bool):
                self.logger.warning(f"Invalid boolean value for {config_key}: {self.config[config_key]}")
                self.config[config_key] = False
        
        # Create directories if they don't exist
        self._create_directories()
        
        self.logger.info("Configuration validated successfully")
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.config['report_dir'],
            self.config['backup_dir'],
            'logs'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key (str): Configuration key
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            key (str): Configuration key
            value (Any): Configuration value
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration
        
        Returns:
            Dict[str, Any]: Complete configuration
        """
        return self.config.copy()
    
    def get_shopify_config(self) -> Dict[str, str]:
        """
        Get Shopify-specific configuration
        
        Returns:
            Dict[str, str]: Shopify configuration
        """
        return {
            'shop_url': self.config['shopify_shop_url'],
            'api_key': self.config['shopify_api_key'],
            'api_password': self.config['shopify_api_password'],
            'api_version': self.config['shopify_api_version'],
            'rate_limit': self.config['shopify_rate_limit']
        }
    
    def get_selenium_config(self) -> Dict[str, Any]:
        """
        Get Selenium-specific configuration
        
        Returns:
            Dict[str, Any]: Selenium configuration
        """
        return {
            'headless': self.config['selenium_headless'],
            'wait_timeout': self.config['selenium_wait_timeout']
        }
    
    def get_ai_fiesta_config(self) -> Dict[str, Any]:
        """
        Get AI Fiesta-specific configuration
        
        Returns:
            Dict[str, Any]: AI Fiesta configuration
        """
        return {
            'url': self.config['ai_fiesta_url'],
            'wait_time': self.config['ai_fiesta_wait_time'],
            'retry_attempts': self.config['ai_fiesta_retry_attempts']
        }
    
    def get_processing_config(self) -> Dict[str, Any]:
        """
        Get processing-specific configuration
        
        Returns:
            Dict[str, Any]: Processing configuration
        """
        return {
            'batch_size': self.config['batch_size'],
            'max_workers': self.config['max_workers'],
            'max_retries': self.config['max_retries'],
            'delay_between_batches': self.config['delay_between_batches'],
            'retry_delay': self.config['retry_delay'],
            'max_retry_delay': self.config['max_retry_delay'],
            'retry_backoff_factor': self.config['retry_backoff_factor']
        }
    
    def get_validation_config(self) -> Dict[str, bool]:
        """
        Get validation-specific configuration
        
        Returns:
            Dict[str, bool]: Validation configuration
        """
        return {
            'validate_images': self.config['validate_images'],
            'validate_prices': self.config['validate_prices'],
            'skip_duplicates': self.config['skip_duplicates']
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging-specific configuration
        
        Returns:
            Dict[str, Any]: Logging configuration
        """
        return {
            'log_level': self.config['log_level'],
            'log_file': self.config['log_file']
        }
    
    def get_report_config(self) -> Dict[str, str]:
        """
        Get report-specific configuration
        
        Returns:
            Dict[str, str]: Report configuration
        """
        return {
            'report_dir': self.config['report_dir'],
            'backup_dir': self.config['backup_dir']
        }
    
    def get_pricing_config(self) -> Dict[str, float]:
        """
        Get pricing-specific configuration
        
        Returns:
            Dict[str, float]: Pricing configuration
        """
        return {
            'handling_charges': self.config['handling_charges'],
            'logistics_charges': self.config['logistics_charges'],
            'marketplace_commission_percent': self.config['marketplace_commission_percent'],
            'profit_margin_percent': self.config['profit_margin_percent'],
            'use_dynamic_logistics': self.config['use_dynamic_logistics'],
            'base_logistics_rate': self.config['base_logistics_rate'],
            'min_logistics_charge': self.config['min_logistics_charge'],
            'max_logistics_charge': self.config['max_logistics_charge'],
            'default_distance_km': self.config['default_distance_km'],
            'default_weight_kg': self.config['default_weight_kg']
        }
    
    def save_config(self, output_file: str):
        """
        Save configuration to file
        
        Args:
            output_file (str): Output file path
        """
        try:
            import json
            
            # Remove sensitive information
            safe_config = self.config.copy()
            sensitive_keys = ['shopify_api_key', 'shopify_api_password', 'openai_api_key']
            for key in sensitive_keys:
                if key in safe_config:
                    safe_config[key] = '***HIDDEN***'
            
            with open(output_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            raise
    
    def create_sample_env(self, output_file: str = '.env.example'):
        """
        Create sample environment file
        
        Args:
            output_file (str): Output file path
        """
        try:
            env_content = """# Shopify API Configuration
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_PASSWORD=your_api_password  

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key

# Processing Configuration
BATCH_SIZE=100
MAX_WORKERS=1
MAX_RETRIES=3
DELAY_BETWEEN_BATCHES=1.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/shopify_upload.log

# Report Configuration
REPORT_DIR=reports
BACKUP_DIR=backups

# AI Configuration
AI_MODEL=gpt-3.5-turbo
AI_MAX_TOKENS=800
AI_TEMPERATURE=0.7

# Shopify Configuration
SHOPIFY_API_VERSION=2025-10
SHOPIFY_RATE_LIMIT=1000

# Validation Configuration
VALIDATE_IMAGES=true
VALIDATE_PRICES=true
SKIP_DUPLICATES=false

# Retry Configuration
RETRY_DELAY=2.0
MAX_RETRY_DELAY=60.0
RETRY_BACKOFF_FACTOR=2.0

# Pricing Configuration
HANDLING_CHARGES=50.0
LOGISTICS_CHARGES=300.0
MARKETPLACE_COMMISSION_PERCENT=15.0
PROFIT_MARGIN_PERCENT=20.0
"""
            
            with open(output_file, 'w') as f:
                f.write(env_content)
            
            self.logger.info(f"Sample environment file created: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating sample environment file: {str(e)}")
            raise
