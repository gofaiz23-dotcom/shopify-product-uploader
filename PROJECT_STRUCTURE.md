# Shopify Product Upload System - Project Structure

## 📁 Directory Structure

```
shopify-product-upload-system/
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── excel_reader.py          # Excel data processing
│   │   ├── ai_description_generator.py  # AI description generation
│   │   └── batch_processor.py       # Batch processing logic
│   ├── 📁 api/                      # External API integrations
│   │   ├── __init__.py
│   │   └── shopify_api_client.py    # Shopify GraphQL API client
│   ├── 📁 utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── logger_config.py         # Logging configuration
│   ├── 📁 reports/                  # Report generation
│   │   ├── __init__.py
│   │   └── excel_report_generator.py  # Excel report generation
│   └── 📁 config/                   # Configuration management
│       ├── __init__.py
│       └── config_manager.py        # Configuration handling
├── 📁 data/                         # Data files
│   ├── Items.csv                    # Sample product data
│   ├── Stock.csv                    # Sample inventory data
│   ├── Images.csv                   # Sample image data
│   └── sample_products.xlsx        # Sample Excel file
├── 📁 tests/                        # Test files
├── 📁 docs/                         # Documentation
│   ├── env_template.txt            # Environment variables template
│   └── SYSTEM_OVERVIEW.md          # System overview
├── 📁 scripts/                      # Utility scripts
├── 📁 logs/                         # Log files (auto-created)
├── 📁 reports/                      # Generated reports (auto-created)
├── 📁 backups/                      # Backup files (auto-created)
├── main.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── config.env.example              # Environment configuration template
├── .env                            # Environment variables (user-created)
├── README.md                       # Project documentation
└── PROJECT_STRUCTURE.md            # This file
```

## 🏗️ Architecture Overview

### Core Modules (`src/core/`)
- **ExcelReader**: Handles reading and merging Excel sheets
- **AIDescriptionGenerator**: Generates AI-powered product descriptions
- **BatchProcessor**: Manages batch processing with rate limiting
- **ProductProcessor**: Processes individual products

### API Modules (`src/api/`)
- **ShopifyAPIClient**: GraphQL API integration with Shopify

### Utility Modules (`src/utils/`)
- **LoggerConfig**: Comprehensive logging system
- **ErrorHandler**: Centralized error handling

### Report Modules (`src/reports/`)
- **ExcelReportGenerator**: Generates comprehensive Excel reports

### Configuration Modules (`src/config/`)
- **ConfigManager**: Centralized configuration management

## 📋 File Organization Principles

### 1. **Separation of Concerns**
- Each module has a single responsibility
- Clear boundaries between different functionalities
- Easy to maintain and extend

### 2. **Professional Structure**
- Follows Python packaging best practices
- Proper `__init__.py` files for imports
- Logical grouping of related functionality

### 3. **Scalability**
- Easy to add new features
- Modular design allows independent testing
- Clear import paths

### 4. **Maintainability**
- Self-documenting structure
- Easy to locate specific functionality
- Consistent naming conventions

## 🚀 Usage

### Import Structure
```python
# Core functionality
from src.core import ExcelReader, AIDescriptionGenerator, BatchProcessor

# API integrations
from src.api import ShopifyAPIClient

# Utilities
from src.utils import setup_logging, get_upload_logger

# Reports
from src.reports import ExcelReportGenerator

# Configuration
from src.config import ConfigManager
```

### Running the System
```bash
# From project root
python main.py data/sample_products.xlsx

# With dry run
python main.py data/sample_products.xlsx --dry-run
```

## 📁 Data Flow

1. **Input**: Excel files in `data/` directory
2. **Processing**: Core modules in `src/core/`
3. **API Calls**: Shopify integration via `src/api/`
4. **Output**: Reports in `reports/` directory
5. **Logs**: Processing logs in `logs/` directory

## 🔧 Configuration

- **Environment Variables**: `.env` file in project root
- **Template**: `config.env.example` for reference
- **Management**: `src/config/config_manager.py`

## 📊 Reports

Generated reports include:
- **All Data Sheet**: Complete product information
- **Injected Items Sheet**: Successfully uploaded products
- **Rejected Items Sheet**: Failed products with reasons
- **Summary Sheet**: Processing statistics

## 🧪 Testing

- Test files go in `tests/` directory
- Separate test modules for each component
- Integration tests for end-to-end workflows

## 📚 Documentation

- **README.md**: Main project documentation
- **docs/**: Additional documentation files
- **Inline comments**: Code documentation
- **Type hints**: Function signatures with types

This structure provides a professional, maintainable, and scalable foundation for the Shopify Product Upload System.
