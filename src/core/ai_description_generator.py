"""
AI Description Generator for Shopify Product Upload System
Generates HTML product descriptions using OpenAI API
"""

from openai import OpenAI
import logging
import re
from typing import Dict, Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIDescriptionGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Description Generator
        
        Args:
            api_key (Optional[str]): OpenAI API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
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
    
    def generate_description(self, product_data: Dict) -> str:
        """
        Generate HTML description for a product using AI
        
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
            features = product_data.get('features', '')
            material = product_data.get('material', '')
            price = product_data.get('price', '')
            
            # Create prompt for AI
            prompt = self._create_prompt(product_data)
            
            # Generate description using OpenAI
            response = self._call_openai_api(prompt)
            
            # Parse and format the response
            formatted_description = self._format_description(response, product_data)
            
            self.logger.info(f"Generated description for SKU: {sku}")
            return formatted_description
            
        except Exception as e:
            self.logger.error(f"Error generating description for SKU {product_data.get('sku', 'unknown')}: {str(e)}")
            return self._create_fallback_description(product_data)
    
    def _create_prompt(self, product_data: Dict) -> str:
        """
        Create a detailed prompt for the AI to generate product description
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            str: Formatted prompt for AI
        """
        prompt = f"""
You are an expert e-commerce copywriter specializing in furniture and home goods. 
Create a professional product description in HTML format for the following product:

Product Details:
- SKU: {product_data.get('sku', 'N/A')}
- Title: {product_data.get('title', 'N/A')}
- Brand: {product_data.get('brand', 'N/A')}
- Category: {product_data.get('category', 'N/A')}
- Price: ${product_data.get('price', 'N/A')}
- Features: {product_data.get('features', 'N/A')}
- Material: {product_data.get('material', 'N/A')}

Please generate a description that follows this exact HTML structure:

1. An introductory paragraph (2-3 sentences) describing the product, its style, and usage
2. A "KD line" (key features) in a single line format
3. A bulleted list of materials and finishes
4. A specs section with SKU, Name, Brand, and any relevant specifications

Format the response as clean HTML without any explanations or markdown formatting.
Focus on highlighting the product's key selling points, quality, and practical benefits.
Make it compelling for potential customers while being informative and professional.
"""
        return prompt
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        Call OpenAI API to generate description
        
        Args:
            prompt (str): The prompt to send to OpenAI
            
        Returns:
            str: AI-generated response
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert e-commerce copywriter specializing in furniture and home goods. Generate professional, compelling product descriptions in HTML format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _format_description(self, ai_response: str, product_data: Dict) -> str:
        """
        Format the AI response into the required HTML structure
        
        Args:
            ai_response (str): Raw AI response
            product_data (Dict): Product data for fallback information
            
        Returns:
            str: Formatted HTML description
        """
        try:
            # Clean the AI response
            cleaned_response = self._clean_html_response(ai_response)
            
            # If the response already has good structure, use it
            if self._validate_html_structure(cleaned_response):
                return cleaned_response
            
            # Otherwise, try to extract components and rebuild
            return self._rebuild_description(cleaned_response, product_data)
            
        except Exception as e:
            self.logger.warning(f"Error formatting AI response: {str(e)}")
            return self._create_fallback_description(product_data)
    
    def _clean_html_response(self, response: str) -> str:
        """
        Clean and normalize the HTML response
        
        Args:
            response (str): Raw AI response
            
        Returns:
            str: Cleaned HTML
        """
        # Remove any markdown formatting
        response = re.sub(r'```html\n?', '', response)
        response = re.sub(r'```\n?', '', response)
        
        # Remove extra whitespace
        response = re.sub(r'\n\s*\n', '\n', response)
        
        # Ensure proper HTML structure
        if not response.strip().startswith('<'):
            # If response doesn't start with HTML, try to find HTML content
            html_match = re.search(r'<.*>', response, re.DOTALL)
            if html_match:
                response = html_match.group()
        
        return response.strip()
    
    def _validate_html_structure(self, html: str) -> bool:
        """
        Validate that the HTML has the required structure
        
        Args:
            html (str): HTML content to validate
            
        Returns:
            bool: True if structure is valid
        """
        required_elements = ['<p>', '<ul>', '<li>', 'SKU:', 'Brand:']
        return all(element in html for element in required_elements)
    
    def _rebuild_description(self, ai_response: str, product_data: Dict) -> str:
        """
        Rebuild description using AI response and product data
        
        Args:
            ai_response (str): AI response
            product_data (Dict): Product data
            
        Returns:
            str: Rebuilt HTML description
        """
        # Extract components from AI response
        intro_paragraph = self._extract_intro_paragraph(ai_response)
        kd_line = self._extract_kd_line(ai_response)
        materials_list = self._extract_materials_list(ai_response)
        
        # Use product data for specs
        specs = f"""
<li>SKU: {product_data.get('sku', 'N/A')}</li>
<li>Name: {product_data.get('title', 'N/A')}</li>
<li>Brand: {product_data.get('brand', 'N/A')}</li>
"""
        
        # Add additional specs if available
        if product_data.get('material'):
            specs += f"<li>Material: {product_data['material']}</li>"
        if product_data.get('category'):
            specs += f"<li>Category: {product_data['category']}</li>"
        
        return self.description_template.format(
            intro_paragraph=intro_paragraph,
            kd_line=kd_line,
            materials_list=materials_list,
            sku=product_data.get('sku', 'N/A'),
            name=product_data.get('title', 'N/A'),
            brand=product_data.get('brand', 'N/A'),
            additional_specs=specs
        )
    
    def _extract_intro_paragraph(self, response: str) -> str:
        """Extract introductory paragraph from AI response"""
        # Look for first paragraph
        p_match = re.search(r'<p>(.*?)</p>', response, re.DOTALL)
        if p_match:
            return p_match.group(1).strip()
        
        # Fallback: look for first substantial text
        lines = response.split('\n')
        for line in lines:
            if len(line.strip()) > 50 and not line.strip().startswith('<'):
                return line.strip()
        
        return "A high-quality product designed for modern living."
    
    def _extract_kd_line(self, response: str) -> str:
        """Extract KD line from AI response"""
        # Look for KD line pattern
        kd_match = re.search(r'KD line[:\s]*(.*?)(?:\n|<)', response, re.IGNORECASE)
        if kd_match:
            return kd_match.group(1).strip()
        
        # Look for key features
        features_match = re.search(r'Key features?[:\s]*(.*?)(?:\n|<)', response, re.IGNORECASE)
        if features_match:
            return features_match.group(1).strip()
        
        return "Premium quality with exceptional design and functionality."
    
    def _extract_materials_list(self, response: str) -> str:
        """Extract materials list from AI response"""
        # Look for existing list items
        list_items = re.findall(r'<li>(.*?)</li>', response, re.DOTALL)
        if list_items:
            # Filter out specs items (contain SKU, Name, Brand)
            materials = [item.strip() for item in list_items 
                        if not any(spec in item.lower() for spec in ['sku:', 'name:', 'brand:'])]
            if materials:
                return '\n'.join([f'<li>{item}</li>' for item in materials[:3]])  # Limit to 3 items
        
        # Fallback materials
        return """
<li>High-quality materials and construction</li>
<li>Durable finish for long-lasting beauty</li>
<li>Professional craftsmanship and attention to detail</li>
"""
    
    def _create_fallback_description(self, product_data: Dict) -> str:
        """
        Create a fallback description when AI generation fails
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            str: Fallback HTML description
        """
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
<li>SKU: {product_data.get('sku', 'N/A')}</li>
<li>Name: {title}</li>
<li>Brand: {brand}</li>
<li>Category: {category}</li>
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
            except Exception as e:
                self.logger.error(f"Failed to generate description for SKU {sku}: {str(e)}")
                # Use fallback description
                descriptions[sku] = self._create_fallback_description(product_data)
        
        return descriptions

