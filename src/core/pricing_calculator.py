"""
Pricing Calculator Module for Shopify Product Upload System
Handles calculation of final price with handling charges, logistics, commission, and profit margin
"""

import logging
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

class PricingCalculator:
    """
    Calculator for final product pricing with various charges and margins
    """
    
    def __init__(self, pricing_config: Dict[str, float]):
        """
        Initialize pricing calculator with configuration
        
        Args:
            pricing_config (Dict[str, float]): Pricing configuration containing:
                - handling_charges: Fixed handling charges
                - logistics_charges: Fixed logistics charges  
                - marketplace_commission_percent: Marketplace commission percentage
                - profit_margin_percent: Profit margin percentage
        """
        self.handling_charges = Decimal(str(pricing_config['handling_charges']))
        self.logistics_charges = Decimal(str(pricing_config['logistics_charges']))
        self.marketplace_commission_percent = Decimal(str(pricing_config['marketplace_commission_percent']))
        self.profit_margin_percent = Decimal(str(pricing_config['profit_margin_percent']))
        
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Pricing calculator initialized:")
        self.logger.info(f"  - Handling charges: {self.handling_charges}")
        self.logger.info(f"  - Logistics charges: {self.logistics_charges}")
        self.logger.info(f"  - Marketplace commission: {self.marketplace_commission_percent}%")
        self.logger.info(f"  - Profit margin: {self.profit_margin_percent}%")
    
    def calculate_final_price(self, sheet_price: float) -> Dict[str, float]:
        """
        Calculate final price from sheet price with all charges and margins
        
        Args:
            sheet_price (float): Original price from the sheet
            
        Returns:
            Dict[str, float]: Detailed pricing breakdown and final price
        """
        try:
            # Convert to Decimal for precise calculations
            base_price = Decimal(str(sheet_price))
            
            # Step 1: Add fixed charges
            price_with_charges = base_price + self.handling_charges + self.logistics_charges
            
            # Step 2: Calculate marketplace commission
            commission_amount = (price_with_charges * self.marketplace_commission_percent) / Decimal('100')
            price_after_commission = price_with_charges + commission_amount
            
            # Step 3: Add profit margin
            profit_amount = (price_after_commission * self.profit_margin_percent) / Decimal('100')
            final_price = price_after_commission + profit_amount
            
            # Round to 2 decimal places
            final_price = final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            commission_amount = commission_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            profit_amount = profit_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Convert back to float for return
            result = {
                'original_price': float(base_price),
                'handling_charges': float(self.handling_charges),
                'logistics_charges': float(self.logistics_charges),
                'price_with_charges': float(price_with_charges),
                'marketplace_commission_percent': float(self.marketplace_commission_percent),
                'commission_amount': float(commission_amount),
                'price_after_commission': float(price_after_commission),
                'profit_margin_percent': float(self.profit_margin_percent),
                'profit_amount': float(profit_amount),
                'final_price': float(final_price)
            }
            
            self.logger.debug(f"Price calculation for {sheet_price}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating final price for {sheet_price}: {str(e)}")
            # Return original price if calculation fails
            return {
                'original_price': sheet_price,
                'handling_charges': 0.0,
                'logistics_charges': 0.0,
                'price_with_charges': sheet_price,
                'marketplace_commission_percent': 0.0,
                'commission_amount': 0.0,
                'price_after_commission': sheet_price,
                'profit_margin_percent': 0.0,
                'profit_amount': 0.0,
                'final_price': sheet_price,
                'error': str(e)
            }
    
    def calculate_bulk_prices(self, prices: list) -> list:
        """
        Calculate final prices for a list of sheet prices
        
        Args:
            prices (list): List of sheet prices
            
        Returns:
            list: List of pricing breakdowns
        """
        results = []
        for price in prices:
            try:
                result = self.calculate_final_price(price)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error calculating price for {price}: {str(e)}")
                # Add error result
                results.append({
                    'original_price': price,
                    'final_price': price,
                    'error': str(e)
                })
        
        return results
    
    def get_pricing_summary(self, pricing_result: Dict[str, float]) -> str:
        """
        Get a human-readable summary of the pricing calculation
        
        Args:
            pricing_result (Dict[str, float]): Result from calculate_final_price
            
        Returns:
            str: Human-readable pricing summary
        """
        if 'error' in pricing_result:
            return f"Error in pricing calculation: {pricing_result['error']}"
        
        summary = f"""
Pricing Breakdown:
  Original Price: ${pricing_result['original_price']:.2f}
  + Handling Charges: ${pricing_result['handling_charges']:.2f}
  + Logistics Charges: ${pricing_result['logistics_charges']:.2f}
  = Subtotal: ${pricing_result['price_with_charges']:.2f}
  
  + Marketplace Commission ({pricing_result['marketplace_commission_percent']:.1f}%): ${pricing_result['commission_amount']:.2f}
  = After Commission: ${pricing_result['price_after_commission']:.2f}
  
  + Profit Margin ({pricing_result['profit_margin_percent']:.1f}%): ${pricing_result['profit_amount']:.2f}
  = FINAL PRICE: ${pricing_result['final_price']:.2f}
        """.strip()
        
        return summary

def create_pricing_calculator(pricing_config: Dict[str, float]) -> PricingCalculator:
    """
    Create a pricing calculator instance
    
    Args:
        pricing_config (Dict[str, float]): Pricing configuration
        
    Returns:
        PricingCalculator: Pricing calculator instance
    """
    return PricingCalculator(pricing_config)
