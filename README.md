# 🚀 Shopify Product Upload & Reporting System

A comprehensive Python system for automating the upload of thousands of products to Shopify, featuring AI-generated descriptions, multi-sheet Excel integration, batch processing, and detailed Excel reporting.

## 📁 Project Structure

```
shopify-product-upload-system/
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core business logic
│   ├── 📁 api/                      # External API integrations  
│   ├── 📁 utils/                   # Utility functions
│   ├── 📁 reports/                 # Report generation
│   └── 📁 config/                  # Configuration management
├── 📁 data/                        # Data files
├── 📁 tests/                       # Test files
├── 📁 docs/                        # Documentation
├── 📁 scripts/                     # Utility scripts
├── main.py                         # Main application
└── requirements.txt               # Dependencies
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure information.

## Features

- **Multi-Sheet Excel Integration**: Automatically merges product data from multiple Excel sheets (Items, Stock, Images)
- **AI-Generated Descriptions**: Uses OpenAI API to create professional HTML product descriptions
- **Shopify GraphQL API Integration**: Direct upload to Shopify using the latest GraphQL API
- **Batch Processing**: Handles large product catalogs with rate limiting and progress tracking
- **Comprehensive Excel Reporting**: Generates detailed reports with All Data, Injected Items, and Rejected Items sheets
- **Advanced Error Handling**: Robust error handling with retry mechanisms and detailed error categorization
- **Dry Run Mode**: Validate data without uploading to Shopify
- **Configuration Management**: Flexible configuration system with environment variables
- **Professional Logging**: Detailed logs for success, failures, and debugging

## System Requirements

- Python 3.9+
- Shopify Admin API access
- OpenAI API key
- Excel file with structured product data

## Installation

1. **Clone or download the system files**

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp config.env.example .env
   # Edit .env with your API credentials
   ```

4. **Create necessary directories:**
   ```bash
   mkdir logs reports backups
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Shopify API Configuration
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
```

### Excel File Structure

The system expects an Excel file with multiple sheets:

#### Items Sheet (Required)
| Column | Description | Example |
|--------|-------------|---------|
| SKU | Product SKU (unique identifier) | FURN-001 |
| Title | Product name | Modern Dining Chair |
| Price | Product price | 299.99 |
| Category | Product category | Furniture |
| Brand | Product brand | Acme Furniture |
| Features | Product features | Ergonomic design, Easy assembly |
| Material | Product material | Solid wood, Metal legs |

#### Stock Sheet (Required)
| Column | Description | Example |
|--------|-------------|---------|
| SKU | Product SKU | FURN-001 |
| Quantity | Available stock | 50 |

#### Images Sheet (Optional)
| Column | Description | Example |
|--------|-------------|---------|
| SKU | Product SKU | FURN-001 |
| Image Links | Comma-separated image URLs | https://example.com/image1.jpg, https://example.com/image2.jpg |

## Usage

### Basic Usage

```bash
python main.py products.xlsx
```

### Dry Run (Validation Only)

```bash
python main.py products.xlsx --dry-run
```

### With Custom Configuration

```bash
python main.py products.xlsx --config custom_config.env
```

## Generated HTML Description Format

The system generates professional HTML descriptions following this structure:

```html
<p>Introductory paragraph describing the product, its style, and usage.</p>
<p>KD line: Key features summarized in a single line.</p>
<ul>
<li>Material & Finish bullet 1</li>
<li>Material & Finish bullet 2</li>
</ul>
<hr>
<h1><strong>Specs:</strong></h1>
<ul>
<li>SKU: 12345</li>
<li>Name: Product Name</li>
<li>Brand: Brand Name</li>
<li>Weight: xx lbs</li>
<li>Width: xx in</li>
<li>Height: xx in</li>
<li>Length: xx in</li>
</ul>
```

## Excel Reporting

The system automatically generates comprehensive Excel reports after each upload session:

### Report Structure

1. **All Data Sheet**: Complete product information with status and processing details
2. **Injected Items Sheet**: Successfully uploaded products with Shopify Product IDs
3. **Rejected Items Sheet**: Failed products with detailed rejection reasons
4. **Summary Sheet**: Processing statistics and performance metrics

### Report Features

- **Status Tracking**: Clear indication of success/failure for each product
- **Error Categorization**: Automatic categorization of rejection reasons
- **Performance Metrics**: Processing times, success rates, and error counts
- **Audit Trail**: Complete timestamp and processing information
- **Retry Recommendations**: Suggestions for which products can be retried

### Sample Data

Use the included sample data files to test the system:
- `Items.csv`, `Stock.csv`, `Images.csv` - Sample data in CSV format
- Convert to Excel format using: `python create_sample_data.py`

## Logging

The system creates detailed logs in the `logs/` directory:

- `shopify_upload_YYYYMMDD_HHMMSS.log` - Complete processing log
- `errors_YYYYMMDD_HHMMSS.log` - Error-only log
- `upload_results_YYYYMMDD_HHMMSS.log` - Upload results summary
- `upload_errors_YYYYMMDD_HHMMSS.log` - Upload error details

## Error Handling

The system includes comprehensive error handling for:

- **Excel Reading Errors**: Missing files, locked files, invalid formats
- **API Errors**: Rate limiting, authentication, network issues
- **AI Generation Errors**: API failures, invalid responses
- **Validation Errors**: Missing required fields, invalid data types

## Batch Processing

- **Batch Size**: Configurable batch size (default: 100 products)
- **Rate Limiting**: Automatic rate limit handling for Shopify API
- **Progress Tracking**: Real-time progress with tqdm progress bars
- **Parallel Processing**: Optional multi-threading for faster processing

## API Rate Limits

The system automatically handles Shopify API rate limits:
- **Shopify API**: 40 calls per second
- **OpenAI API**: Automatic retry with exponential backoff
- **Batch Delays**: Configurable delays between batches

## Troubleshooting

### Common Issues

1. **Excel File Not Found**
   - Ensure the file path is correct
   - Check file permissions

2. **API Authentication Failed**
   - Verify Shopify API credentials
   - Check OpenAI API key

3. **Missing Required Columns**
   - Ensure Excel sheets have required columns (SKU, Title, Price)
   - Check column names match expected format

4. **Rate Limit Errors**
   - Increase `DELAY_BETWEEN_BATCHES` in configuration
   - Reduce `BATCH_SIZE` for smaller batches

### Debug Mode

Enable debug logging by setting the log level:

```python
# In main.py, change:
self.logger = setup_logging(log_level="DEBUG")
```

## Performance Optimization

### For Large Catalogs (10,000+ products)

1. **Increase batch size** (up to 200 products per batch)
2. **Use parallel processing** (set `MAX_WORKERS=2-4`)
3. **Optimize API calls** by batching image uploads
4. **Monitor rate limits** and adjust delays accordingly

### Memory Optimization

- Process products in smaller batches
- Use generator functions for large datasets
- Clear unused variables between batches

## Security Considerations

- Store API keys in environment variables, not in code
- Use `.env` files for local development only
- Implement proper access controls for production
- Monitor API usage and costs

## Support

For issues and questions:

1. Check the logs in the `logs/` directory
2. Verify your Excel file structure matches requirements
3. Test with a small batch first using `--dry-run`
4. Ensure all API credentials are correct

## License

This system is provided as-is for educational and commercial use. Please ensure compliance with Shopify and OpenAI API terms of service.

