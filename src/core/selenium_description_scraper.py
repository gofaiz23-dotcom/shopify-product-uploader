"""
Selenium Description Scraper for Shopify Product Upload System
Generates HTML product descriptions using web scraping with Selenium
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
import re
from typing import Dict, Optional, List
import random

class SeleniumDescriptionScraper:
    """
    Selenium-based description scraper for generating product descriptions
    """
    
    def __init__(self, headless: bool = True, wait_timeout: int = 10):
        """
        Initialize Selenium Description Scraper
        
        Args:
            headless (bool): Run browser in headless mode
            wait_timeout (int): Timeout for web driver waits
        """
        self.headless = headless
        self.wait_timeout = wait_timeout
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        # Description template for consistent formatting
        self.description_template = """
<p>{intro_paragraph}</p>
<p>KD line: {kd_line}</p>
<ul>
{materials_list}
</ul>
<hr>
<h1><strong>Specs:</strong></h1>
<ul>
<li>SKU: {sku}</li>
<li>Name: {name}</li>
<li>Brand: {brand}</li>
{additional_specs}
</ul>
"""
        
        # AI Fiesta and other AI services for description generation
        self.ai_sources = [
            "https://aifiesta.com/",
            "https://chat.openai.com/",
            "https://claude.ai/",
            "https://gemini.google.com/",
            "https://www.perplexity.ai/"
        ]
        
        # Product information sources for context
        self.product_sources = [
            "https://www.google.com/search?q=",
            "https://www.amazon.com/s?k=",
            "https://www.wayfair.com/keyword.php?keyword="
        ]
        
        self.logger.info("Selenium Description Scraper initialized")
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with options"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(self.wait_timeout)
            self.logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise
    
    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def generate_description(self, product_data: Dict) -> str:
        """
        Generate HTML description for a product using web scraping
        
        Args:
            product_data (Dict): Product data dictionary containing all product information
            
        Returns:
            str: Generated HTML description
        """
        try:
            # Extract product information
            sku = product_data.get('sku', '')
            title = product_data.get('title', '')
            brand = product_data.get('brand', '')
            category = product_data.get('category', '')
            
            self.logger.info(f"Generating description for SKU: {sku}")
            
            # Setup driver
            self._setup_driver()
            
            # Search for product information
            product_info = self._search_product_info(product_data)
            
            # Generate description based on scraped data
            description = self._create_description_from_data(product_data, product_info)
            
            self.logger.info(f"Generated description for SKU: {sku}")
            return description
            
        except Exception as e:
            self.logger.error(f"Error generating description for SKU {product_data.get('sku', 'unknown')}: {str(e)}")
            return self._create_fallback_description(product_data)
        finally:
            self._close_driver()
    
    def _search_product_info(self, product_data: Dict) -> Dict:
        """
        Search for product information using AI Fiesta and other AI services
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            Dict: AI-generated product information
        """
        product_info = {
            'description': '',
            'features': [],
            'materials': [],
            'specifications': {}
        }
        
        try:
            # First, get product context from regular sources
            product_context = self._get_product_context(product_data)
            
            # Then use AI Fiesta to generate description
            ai_description = self._generate_with_ai_fiesta(product_data, product_context)
            
            if ai_description:
                product_info['description'] = ai_description
                # Extract features and materials from AI description
                product_info['features'] = self._extract_features_from_description(ai_description)
                product_info['materials'] = self._extract_materials_from_description(ai_description)
            
            return product_info
            
        except Exception as e:
            self.logger.error(f"Error generating AI description: {str(e)}")
            return product_info
    
    def _create_search_query(self, product_data: Dict) -> str:
        """Create search query from product data"""
        title = product_data.get('title', '')
        brand = product_data.get('brand', '')
        category = product_data.get('category', '')
        
        # Create search query
        query_parts = []
        if brand:
            query_parts.append(brand)
        if title:
            query_parts.append(title)
        if category:
            query_parts.append(category)
        
        query = " ".join(query_parts)
        return query.replace(" ", "+")
    
    def _get_product_context(self, product_data: Dict) -> str:
        """Get product context from regular sources for AI input"""
        context = ""
        
        try:
            search_query = self._create_search_query(product_data)
            
            # Try to get basic product info from Amazon or Google
            for source in self.product_sources[:1]:  # Just use one source for context
                try:
                    url = f"{source}{search_query}"
                    self.logger.info(f"Getting context from: {url}")
                    
                    self.driver.get(url)
                    time.sleep(random.uniform(2, 3))
                    
                    # Extract basic product info
                    context_elements = self.driver.find_elements(By.CSS_SELECTOR, "h3, .product-title, .product-name, .title")
                    for element in context_elements[:3]:  # Get first 3 titles
                        text = element.text.strip()
                        if text and len(text) > 10:
                            context += text + " "
                    
                    if context:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Failed to get context from {source}: {str(e)}")
                    continue
            
            return context.strip()
            
        except Exception as e:
            self.logger.warning(f"Error getting product context: {str(e)}")
            return ""
    
    def _generate_with_ai_fiesta(self, product_data: Dict, context: str) -> str:
        """Generate description using AI Fiesta"""
        try:
            # Navigate to AI Fiesta
            self.logger.info("Navigating to AI Fiesta...")
            self.driver.get("https://aifiesta.com/")
            time.sleep(random.uniform(3, 5))
            
            # Create the prompt for AI Fiesta
            prompt = self._create_ai_fiesta_prompt(product_data, context)
            
            # Find the input field and enter the prompt
            input_selectors = [
                "textarea[placeholder*='message']",
                "textarea[placeholder*='Message']",
                "textarea[placeholder*='Ask']",
                "input[type='text']",
                "textarea",
                ".chat-input",
                "#message-input"
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not input_element:
                self.logger.warning("Could not find input field on AI Fiesta")
                return ""
            
            # Enter the prompt
            input_element.clear()
            input_element.send_keys(prompt)
            time.sleep(random.uniform(1, 2))
            
            # Find and click send button
            send_selectors = [
                "button[type='submit']",
                "button[aria-label*='Send']",
                "button[aria-label*='send']",
                ".send-button",
                "#send-button",
                "button:contains('Send')",
                "button:contains('Submit')"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if send_button:
                send_button.click()
                self.logger.info("Prompt sent to AI Fiesta, waiting for response...")
            else:
                # Try pressing Enter
                input_element.send_keys("\n")
            
            # Wait for response
            time.sleep(random.uniform(10, 15))
            
            # Extract the AI response
            response = self._extract_ai_response()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating with AI Fiesta: {str(e)}")
            return ""
    
    def _create_ai_fiesta_prompt(self, product_data: Dict, context: str) -> str:
        """Create a prompt for AI Fiesta"""
        title = product_data.get('title', '')
        brand = product_data.get('brand', '')
        category = product_data.get('category', '')
        material = product_data.get('material', '')
        price = product_data.get('price', '')
        
        prompt = f"""Please create a professional e-commerce product description in HTML format for this product:

Product Details:
- Title: {title}
- Brand: {brand}
- Category: {category}
- Material: {material}
- Price: ${price}

Context from web search: {context}

Please generate a compelling product description in HTML format that includes:
1. An engaging introductory paragraph (2-3 sentences)
2. A "KD line" (key features) in a single line
3. A bulleted list of materials and features
4. A specifications section with SKU, Name, Brand, and relevant details

Format the response as clean HTML without explanations. Focus on highlighting the product's key selling points, quality, and practical benefits. Make it compelling for potential customers while being informative and professional.

The description should be suitable for an e-commerce website like Shopify."""
        
        return prompt
    
    def _extract_ai_response(self) -> str:
        """Extract AI response from the page"""
        try:
            # Wait for response to appear
            WebDriverWait(self.driver, 30).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".message, .response, .ai-response, .content")) > 0
            )
            
            # Look for response elements
            response_selectors = [
                ".message:last-child",
                ".response:last-child", 
                ".ai-response",
                ".content:last-child",
                ".chat-message:last-child",
                "[class*='message']:last-child",
                "[class*='response']:last-child"
            ]
            
            for selector in response_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        response_element = elements[-1]  # Get the last (most recent) response
                        response_text = response_element.text.strip()
                        if response_text and len(response_text) > 50:
                            return response_text
                except:
                    continue
            
            # Fallback: get all text content and extract the last substantial block
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            lines = page_text.split('\n')
            
            # Find the last substantial text block (likely the AI response)
            for line in reversed(lines):
                if len(line.strip()) > 100 and ('<p>' in line or '<ul>' in line or 'HTML' in line):
                    return line.strip()
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"Error extracting AI response: {str(e)}")
            return ""
    
    def _extract_features_from_description(self, description: str) -> List[str]:
        """Extract features from AI-generated description"""
        features = []
        
        # Look for list items
        list_items = re.findall(r'<li>(.*?)</li>', description, re.DOTALL)
        for item in list_items:
            if len(item.strip()) > 10 and len(item.strip()) < 100:
                features.append(item.strip())
        
        return features[:5]  # Limit to 5 features
    
    def _extract_materials_from_description(self, description: str) -> List[str]:
        """Extract materials from AI-generated description"""
        materials = []
        
        # Look for material-related content
        material_keywords = ['material', 'wood', 'metal', 'fabric', 'leather', 'plastic', 'glass', 'finish']
        
        list_items = re.findall(r'<li>(.*?)</li>', description, re.DOTALL)
        for item in list_items:
            if any(keyword in item.lower() for keyword in material_keywords):
                materials.append(item.strip())
        
        return materials[:3]  # Limit to 3 materials
    
    def _extract_search_results(self) -> Dict:
        """Extract information from search results"""
        info = {
            'description': '',
            'features': [],
            'materials': [],
            'specifications': {}
        }
        
        try:
            # Look for product descriptions
            description_selectors = [
                "div[class*='description']",
                "div[class*='product-description']",
                "p[class*='description']",
                ".product-info",
                ".description"
            ]
            
            for selector in description_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if len(text) > 50 and len(text) < 500:  # Reasonable description length
                            info['description'] = text
                            break
                    if info['description']:
                        break
                except:
                    continue
            
            # Look for features and specifications
            feature_selectors = [
                "ul li",
                "div[class*='feature'] li",
                "div[class*='spec'] li",
                ".features li"
            ]
            
            for selector in feature_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) < 100:  # Reasonable feature length
                            info['features'].append(text)
                    if len(info['features']) > 0:
                        break
                except:
                    continue
            
            # Limit features to avoid too much data
            info['features'] = info['features'][:5]
            
        except Exception as e:
            self.logger.warning(f"Error extracting search results: {str(e)}")
        
        return info
    
    def _create_description_from_data(self, product_data: Dict, scraped_info: Dict) -> str:
        """Create description from product data and scraped information"""
        try:
            # Extract basic info
            sku = product_data.get('sku', 'N/A')
            title = product_data.get('title', 'N/A')
            brand = product_data.get('brand', 'N/A')
            category = product_data.get('category', 'N/A')
            material = product_data.get('material', 'High-quality materials')
            
            # Create intro paragraph
            if scraped_info.get('description'):
                intro_paragraph = scraped_info['description'][:200] + "..."
            else:
                intro_paragraph = f"Introducing the {title}, a beautifully crafted {category.lower()} that combines style and functionality."
            
            # Create KD line
            if scraped_info.get('features'):
                kd_line = scraped_info['features'][0] if scraped_info['features'] else f"Premium {category.lower()} featuring {material.lower()}."
            else:
                kd_line = f"Premium {category.lower()} featuring {material.lower()} and exceptional design."
            
            # Create materials list
            materials_list = self._create_materials_list(product_data, scraped_info)
            
            # Create specs
            specs = self._create_specs(product_data, scraped_info)
            
            # Format the description
            description = self.description_template.format(
                intro_paragraph=intro_paragraph,
                kd_line=kd_line,
                materials_list=materials_list,
                sku=sku,
                name=title,
                brand=brand,
                additional_specs=specs
            )
            
            return description
            
        except Exception as e:
            self.logger.error(f"Error creating description from data: {str(e)}")
            return self._create_fallback_description(product_data)
    
    def _create_materials_list(self, product_data: Dict, scraped_info: Dict) -> str:
        """Create materials list from product data and scraped info"""
        materials = []
        
        # Add material from product data
        if product_data.get('material'):
            materials.append(f"<li>Material: {product_data['material']}</li>")
        
        # Add features as materials if available
        if scraped_info.get('features'):
            for feature in scraped_info['features'][:3]:  # Limit to 3 features
                materials.append(f"<li>{feature}</li>")
        
        # Add default materials if not enough
        if len(materials) < 3:
            default_materials = [
                "<li>Durable construction for lasting quality</li>",
                "<li>Professional finish and attention to detail</li>",
                "<li>High-quality materials and craftsmanship</li>"
            ]
            materials.extend(default_materials[:3-len(materials)])
        
        return '\n'.join(materials)
    
    def _create_specs(self, product_data: Dict, scraped_info: Dict) -> str:
        """Create specifications from product data and scraped info"""
        specs = []
        
        # Add basic specs
        if product_data.get('category'):
            specs.append(f"<li>Category: {product_data['category']}</li>")
        if product_data.get('material'):
            specs.append(f"<li>Material: {product_data['material']}</li>")
        if product_data.get('price'):
            specs.append(f"<li>Price: ${product_data['price']}</li>")
        
        # Add scraped specifications
        if scraped_info.get('specifications'):
            for key, value in scraped_info['specifications'].items():
                specs.append(f"<li>{key}: {value}</li>")
        
        return '\n'.join(specs)
    
    def _create_fallback_description(self, product_data: Dict) -> str:
        """Create a fallback description when scraping fails"""
        title = product_data.get('title', 'Product')
        brand = product_data.get('brand', 'Brand')
        category = product_data.get('category', 'Furniture')
        material = product_data.get('material', 'High-quality materials')
        
        intro = f"Introducing the {title}, a beautifully crafted {category.lower()} that combines style and functionality."
        kd_line = f"Premium {category.lower()} featuring {material.lower()} and exceptional design."
        
        materials = f"""
<li>Material: {material}</li>
<li>Durable construction for lasting quality</li>
<li>Professional finish and attention to detail</li>
"""
        
        specs = f"""
<li>Category: {category}</li>
<li>Material: {material}</li>
"""
        
        return self.description_template.format(
            intro_paragraph=intro,
            kd_line=kd_line,
            materials_list=materials,
            sku=product_data.get('sku', 'N/A'),
            name=title,
            brand=brand,
            additional_specs=specs
        )
    
    def batch_generate_descriptions(self, products_data: List[Dict]) -> Dict[str, str]:
        """
        Generate descriptions for multiple products
        
        Args:
            products_data (List[Dict]): List of product data dictionaries
            
        Returns:
            Dict[str, str]: Dictionary mapping SKU to generated description
        """
        descriptions = {}
        
        for product_data in products_data:
            sku = product_data.get('sku')
            if not sku:
                self.logger.warning("Skipping product without SKU")
                continue
            
            try:
                description = self.generate_description(product_data)
                descriptions[sku] = description
                
                # Add delay between products to avoid being blocked
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                self.logger.error(f"Failed to generate description for SKU {sku}: {str(e)}")
                # Use fallback description
                descriptions[sku] = self._create_fallback_description(product_data)
        
        return descriptions

def create_selenium_scraper(headless: bool = True) -> SeleniumDescriptionScraper:
    """
    Create a Selenium description scraper instance
    
    Args:
        headless (bool): Run browser in headless mode
        
    Returns:
        SeleniumDescriptionScraper: Selenium scraper instance
    """
    return SeleniumDescriptionScraper(headless=headless)
