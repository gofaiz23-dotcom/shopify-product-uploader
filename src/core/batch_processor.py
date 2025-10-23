"""
Batch Processor for Shopify Product Upload System
Handles batch processing with rate limiting and progress tracking
"""

import time
import logging
from typing import List, Dict, Optional, Callable, Any
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class BatchProcessor:
    def __init__(self, batch_size: int = 100, max_workers: int = 1, delay_between_batches: float = 1.0):
        """
        Initialize batch processor
        
        Args:
            batch_size (int): Number of products per batch
            max_workers (int): Maximum number of worker threads
            delay_between_batches (float): Delay between batches in seconds
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.delay_between_batches = delay_between_batches
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_processed = 0
        self.successful = 0
        self.failed = 0
        self.skipped = 0
        
        # Thread safety
        self.lock = threading.Lock()
    
    def process_products(self, products_data: List[Dict], 
                        process_function: Callable[[Dict], Dict],
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Process products in batches
        
        Args:
            products_data (List[Dict]): List of product data dictionaries
            process_function (Callable): Function to process each product
            progress_callback (Optional[Callable]): Callback for progress updates
            
        Returns:
            Dict[str, Any]: Processing results and statistics
        """
        self.logger.info(f"Starting batch processing of {len(products_data)} products")
        self.logger.info(f"Batch size: {self.batch_size}, Max workers: {self.max_workers}")
        
        # Reset statistics
        self._reset_statistics()
        
        # Split products into batches
        batches = self._create_batches(products_data)
        
        # Process batches
        all_results = []
        
        with tqdm(total=len(products_data), desc="Processing products") as pbar:
            for batch_num, batch in enumerate(batches, 1):
                self.logger.info(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} products)")
                
                batch_results = self._process_batch(batch, process_function, batch_num)
                all_results.extend(batch_results)
                
                # Update progress
                pbar.update(len(batch))
                
                # Progress callback
                if progress_callback:
                    progress_callback(batch_num, len(batches), batch_results)
                
                # Delay between batches (except for last batch)
                if batch_num < len(batches):
                    time.sleep(self.delay_between_batches)
        
        # Compile final results
        results = self._compile_results(all_results)
        
        self.logger.info(f"Batch processing complete: {self.successful} successful, {self.failed} failed, {self.skipped} skipped")
        
        return results
    
    def _create_batches(self, products_data: List[Dict]) -> List[List[Dict]]:
        """
        Split products into batches
        
        Args:
            products_data (List[Dict]): List of product data
            
        Returns:
            List[List[Dict]]: List of batches
        """
        batches = []
        for i in range(0, len(products_data), self.batch_size):
            batch = products_data[i:i + self.batch_size]
            batches.append(batch)
        
        self.logger.info(f"Created {len(batches)} batches")
        return batches
    
    def _process_batch(self, batch: List[Dict], 
                      process_function: Callable[[Dict], Dict], 
                      batch_num: int) -> List[Dict]:
        """
        Process a single batch
        
        Args:
            batch (List[Dict]): Batch of products
            process_function (Callable): Function to process each product
            batch_num (int): Batch number
            
        Returns:
            List[Dict]: Batch results
        """
        batch_results = []
        
        if self.max_workers == 1:
            # Sequential processing
            for product_data in batch:
                result = self._process_single_product(product_data, process_function)
                batch_results.append(result)
        else:
            # Parallel processing
            batch_results = self._process_batch_parallel(batch, process_function)
        
        # Update statistics
        self._update_batch_statistics(batch_results)
        
        return batch_results
    
    def _process_batch_parallel(self, batch: List[Dict], 
                              process_function: Callable[[Dict], Dict]) -> List[Dict]:
        """
        Process batch in parallel
        
        Args:
            batch (List[Dict]): Batch of products
            process_function (Callable): Function to process each product
            
        Returns:
            List[Dict]: Batch results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_product = {
                executor.submit(self._process_single_product, product_data, process_function): product_data
                for product_data in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_product):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    product_data = future_to_product[future]
                    sku = product_data.get('sku', 'unknown')
                    self.logger.error(f"Error processing product {sku}: {str(e)}")
                    
                    # Create error result
                    error_result = {
                        'sku': sku,
                        'status': 'error',
                        'message': str(e),
                        'product_id': None
                    }
                    results.append(error_result)
        
        return results
    
    def _process_single_product(self, product_data: Dict, 
                              process_function: Callable[[Dict], Dict]) -> Dict:
        """
        Process a single product
        
        Args:
            product_data (Dict): Product data
            process_function (Callable): Function to process the product
            
        Returns:
            Dict: Processing result
        """
        sku = product_data.get('sku', 'unknown')
        
        try:
            result = process_function(product_data)
            return result
        except Exception as e:
            self.logger.error(f"Error processing product {sku}: {str(e)}")
            return {
                'sku': sku,
                'status': 'error',
                'message': str(e),
                'product_id': None
            }
    
    def _update_batch_statistics(self, batch_results: List[Dict]):
        """
        Update processing statistics
        
        Args:
            batch_results (List[Dict]): Results from batch processing
        """
        with self.lock:
            for result in batch_results:
                self.total_processed += 1
                
                status = result.get('status', 'unknown')
                if status == 'success':
                    self.successful += 1
                elif status == 'failed':
                    self.failed += 1
                elif status == 'skipped':
                    self.skipped += 1
                else:
                    self.failed += 1
    
    def _reset_statistics(self):
        """Reset processing statistics"""
        with self.lock:
            self.total_processed = 0
            self.successful = 0
            self.failed = 0
            self.skipped = 0
    
    def _compile_results(self, all_results: List[Dict]) -> Dict[str, Any]:
        """
        Compile final processing results
        
        Args:
            all_results (List[Dict]): All processing results
            
        Returns:
            Dict[str, Any]: Compiled results
        """
        # Separate results by status
        successful_results = [r for r in all_results if r.get('status') == 'success']
        failed_results = [r for r in all_results if r.get('status') == 'failed']
        error_results = [r for r in all_results if r.get('status') == 'error']
        skipped_results = [r for r in all_results if r.get('status') == 'skipped']
        
        # Calculate success rate
        success_rate = (self.successful / self.total_processed * 100) if self.total_processed > 0 else 0
        
        # Create product results dictionary for easy lookup
        product_results = {}
        for result in all_results:
            sku = result.get('sku', 'unknown')
            product_results[sku] = {
                'status': result.get('status', 'unknown'),
                'product_id': result.get('product_id'),
                'timestamp': result.get('timestamp', ''),
                'error_message': result.get('message', ''),
                'notes': result.get('notes', ''),
                'processing_time': result.get('processing_time', 0),
                'images_uploaded': result.get('images_uploaded', 0)
            }
        
        # Calculate additional statistics
        processing_time_minutes = sum(r.get('processing_time', 0) for r in all_results) / 60
        avg_processing_time = sum(r.get('processing_time', 0) for r in all_results) / len(all_results) if all_results else 0
        
        # Count products with/without images
        products_with_images = sum(1 for r in all_results if r.get('images_uploaded', 0) > 0)
        products_without_images = len(all_results) - products_with_images
        
        # Count different types of errors
        api_errors = sum(1 for r in error_results if 'api' in r.get('message', '').lower())
        validation_errors = sum(1 for r in error_results if 'validation' in r.get('message', '').lower())
        network_errors = sum(1 for r in error_results if 'network' in r.get('message', '').lower())
        
        return {
            'total_processed': self.total_processed,
            'successful': self.successful,
            'failed': self.failed,
            'skipped': self.skipped,
            'errors': len(error_results),
            'success_rate': success_rate,
            'processing_time_minutes': processing_time_minutes,
            'avg_processing_time': avg_processing_time,
            'products_with_images': products_with_images,
            'products_without_images': products_without_images,
            'api_errors': api_errors,
            'validation_errors': validation_errors,
            'network_errors': network_errors,
            'successful_results': successful_results,
            'failed_results': failed_results,
            'error_results': error_results,
            'skipped_results': skipped_results,
            'product_results': product_results,
            'all_results': all_results
        }

class ProductProcessor:
    """
    Specialized processor for Shopify product uploads
    """
    
    def __init__(self, shopify_client, ai_generator, upload_logger, pricing_calculator=None):
        """
        Initialize product processor
        
        Args:
            shopify_client: Shopify API client
            ai_generator: AI description generator
            upload_logger: Upload logger
            pricing_calculator: Pricing calculator for final price calculation
        """
        self.shopify_client = shopify_client
        self.ai_generator = ai_generator
        self.upload_logger = upload_logger
        self.pricing_calculator = pricing_calculator
        self.logger = logging.getLogger(__name__)
    
    def process_product(self, product_data: Dict) -> Dict:
        """
        Process a single product (create description and upload to Shopify)
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            Dict: Processing result
        """
        import time
        from datetime import datetime
        
        sku = product_data.get('sku', 'unknown')
        start_time = time.time()
        
        try:
            # Validate required fields
            if not self._validate_product_data(product_data):
                return {
                    'sku': sku,
                    'status': 'skipped',
                    'message': 'Missing required fields',
                    'product_id': None,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time': time.time() - start_time,
                    'images_uploaded': 0
                }
            
            # Calculate final price if pricing calculator is available
            if self.pricing_calculator and 'price' in product_data:
                try:
                    original_price = float(product_data['price'])
                    pricing_result = self.pricing_calculator.calculate_final_price(original_price)
                    product_data['price'] = pricing_result['final_price']
                    
                    # Log pricing calculation
                    self.logger.info(f"Price calculation for SKU {sku}:")
                    self.logger.info(f"  Original: ${original_price:.2f} -> Final: ${pricing_result['final_price']:.2f}")
                    self.logger.info(f"  Logistics: ${pricing_result['logistics_charges']:.2f} (fixed)")
                    
                    # Store pricing breakdown for reporting
                    product_data['pricing_breakdown'] = pricing_result
                    
                except Exception as e:
                    self.logger.warning(f"Error calculating final price for SKU {sku}: {str(e)}")
                    # Continue with original price if calculation fails
            
            # Generate AI description
            self.logger.info(f"Generating description for SKU: {sku}")
            description = self.ai_generator.generate_description(product_data)
            product_data['body_html'] = description
            
            # Upload to Shopify
            self.logger.info(f"Uploading product SKU: {sku}")
            success, response = self.shopify_client.create_product(product_data)
            
            if success and response:
                # Extract product ID from GraphQL response
                product_id = response['data']['productCreate']['product']['id']
                self.upload_logger.log_upload_success(sku, product_id, product_data.get('title', ''))
                
                # Count images uploaded
                images_uploaded = 0
                if product_data.get('image_links'):
                    image_urls = [url.strip() for url in product_data['image_links'].split(',') if url.strip()]
                    images_uploaded = len(image_urls)
                
                return {
                    'sku': sku,
                    'status': 'success',
                    'message': 'Product uploaded successfully',
                    'product_id': product_id,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time': time.time() - start_time,
                    'images_uploaded': images_uploaded
                }
            else:
                error_msg = 'Failed to create product in Shopify'
                if response and 'errors' in response:
                    error_msg = f"GraphQL errors: {response['errors']}"
                self.upload_logger.log_upload_failure(sku, error_msg, product_data)
                
                return {
                    'sku': sku,
                    'status': 'failed',
                    'message': error_msg,
                    'product_id': None,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time': time.time() - start_time,
                    'images_uploaded': 0
                }
                
        except Exception as e:
            error_msg = f"Error processing product: {str(e)}"
            self.upload_logger.log_upload_failure(sku, error_msg, product_data)
            
            return {
                'sku': sku,
                'status': 'error',
                'message': error_msg,
                'product_id': None,
                'timestamp': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'images_uploaded': 0
            }
    
    def _validate_product_data(self, product_data: Dict) -> bool:
        """
        Validate product data has required fields
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['sku', 'title', 'price']
        
        for field in required_fields:
            if not product_data.get(field):
                self.logger.warning(f"Missing required field '{field}' for SKU {product_data.get('sku', 'unknown')}")
                return False
        
        # Validate price is numeric
        try:
            float(product_data.get('price', 0))
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid price for SKU {product_data.get('sku', 'unknown')}")
            return False
        
        return True

def create_batch_processor(batch_size: int = 100, max_workers: int = 1) -> BatchProcessor:
    """
    Create a batch processor instance
    
    Args:
        batch_size (int): Batch size
        max_workers (int): Maximum workers
        
    Returns:
        BatchProcessor: Batch processor instance
    """
    return BatchProcessor(batch_size=batch_size, max_workers=max_workers)

def create_product_processor(shopify_client, ai_generator, upload_logger, pricing_calculator=None) -> ProductProcessor:
    """
    Create a product processor instance
    
    Args:
        shopify_client: Shopify API client
        ai_generator: AI description generator
        upload_logger: Upload logger
        pricing_calculator: Pricing calculator for final price calculation
        
    Returns:
        ProductProcessor: Product processor instance
    """
    return ProductProcessor(shopify_client, ai_generator, upload_logger, pricing_calculator)

