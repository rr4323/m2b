"""
Market Discovery Agent for finding trending SaaS applications.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.web_scraper import (
    scrape_product_hunt, 
    get_website_text_content,
    extract_domain
)
from utils.openai_utils import generate_json_completion, analyze_text_with_structure

class MarketDiscoveryAgent(BaseAgent):
    """Agent for discovering trending SaaS applications in various marketplaces."""
    
    def __init__(self):
        """Initialize the Market Discovery Agent."""
        super().__init__(
            name="Market Discovery Agent",
            description="Discovers trending SaaS applications in B2B marketplaces"
        )
        
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the market discovery process to find trending SaaS apps.
        
        Args:
            input_data (Dict[str, Any]): Input data containing the category or domain to search
                
        Returns:
            Dict[str, Any]: Dictionary containing discovered products
        """
        self.log_info("Starting market discovery process")
        
        category = input_data.get("category", "productivity")
        limit = input_data.get("limit", 5)
        
        # Step 1: Scrape Product Hunt for trending products
        self.log_info(f"Searching Product Hunt for {category} products")
        product_hunt_results = scrape_product_hunt(category, limit)
        
        # Step 2: Enhance product data with AI analysis
        enhanced_products = []
        
        for product in product_hunt_results:
            self.log_info(f"Analyzing product: {product['name']}")
            
            # Get more information from the product's website
            if product.get('url'):
                product_domain = extract_domain(product['url'])
                product['domain'] = product_domain
                
                # Extract text content from the website
                website_content = get_website_text_content(product['url'])
                
                # Analyze the website content to extract product information
                if website_content:
                    product_analysis = await self._analyze_product_website(
                        website_content, 
                        product['name'],
                        product_domain
                    )
                    product.update(product_analysis)
            
            enhanced_products.append(product)
        
        # Step 3: Select the most promising products
        top_products = await self._select_top_products(enhanced_products)
        
        return {
            "products": top_products,
            "count": len(top_products),
            "category": category
        }
    
    async def _analyze_product_website(
        self, 
        website_content: str, 
        product_name: str,
        domain: str
    ) -> Dict[str, Any]:
        """
        Analyze website content to extract product information.
        
        Args:
            website_content (str): The text content of the product website
            product_name (str): The name of the product
            domain (str): The domain of the product website
            
        Returns:
            Dict[str, Any]: Extracted product information
        """
        output_structure = {
            "feature_list": ["Feature 1", "Feature 2"],
            "tech_stack": ["Technology 1", "Technology 2"],
            "pricing_model": "Description of pricing model",
            "target_audience": "Description of target users",
            "unique_selling_points": ["USP 1", "USP 2"],
            "competitors": ["Competitor 1", "Competitor 2"]
        }
        
        prompt = (
            f"Analyze this website content for the SaaS product '{product_name}' (domain: {domain}). "
            f"Extract the key features, likely tech stack, pricing model, target audience, "
            f"unique selling points, and potential competitors. If any information is not "
            f"available in the text, make a reasonable estimate based on similar SaaS products "
            f"and indicate that it's an estimate."
        )
        
        # Trim the website content if it's too long
        max_content_length = 10000
        if len(website_content) > max_content_length:
            website_content = website_content[:max_content_length] + "..."
        
        analysis = analyze_text_with_structure(
            website_content,
            prompt,
            output_structure
        )
        
        return analysis
    
    async def _select_top_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Select the most promising products for cloning based on various factors.
        
        Args:
            products (List[Dict[str, Any]]): List of discovered products
            
        Returns:
            List[Dict[str, Any]]: List of top products for potential cloning
        """
        if not products:
            return []
        
        # Use AI to rank the products
        system_message = (
            "You are a SaaS expert who can identify promising products for enhancement. "
            "Evaluate each product based on:\n"
            "1. Clarity of value proposition\n"
            "2. Market potential\n"
            "3. Technical feasibility for cloning\n"
            "4. Potential for AI-based enhancements\n"
            "5. Revenue generation potential\n\n"
            "For each product, assign a score from 1-10 for each category and provide "
            "a brief justification. Then, rank the products in order of overall potential."
        )
        
        prompt = (
            "Analyze the following SaaS products and identify which ones have the most "
            "potential for successful enhancement and cloning:\n\n"
        )
        
        for i, product in enumerate(products, 1):
            prompt += f"Product {i}: {product['name']}\n"
            prompt += f"Description: {product.get('description', 'No description available')}\n"
            
            # Add features if available
            if product.get('feature_list'):
                prompt += "Features: " + ", ".join(product['feature_list'][:5]) + "\n"
                
            # Add pricing model if available
            if product.get('pricing_model'):
                prompt += f"Pricing: {product['pricing_model']}\n"
                
            prompt += "\n"
        
        prompt += (
            "Format your response as a JSON object with the following structure:\n"
            "{\n"
            "  \"product_rankings\": [\n"
            "    {\n"
            "      \"product_name\": \"Name of product\",\n"
            "      \"overall_score\": 8.5,\n"
            "      \"justification\": \"Reason this product is ranked here\",\n"
            "      \"scores\": {\n"
            "        \"value_proposition\": 9,\n"
            "        \"market_potential\": 8,\n"
            "        \"technical_feasibility\": 7,\n"
            "        \"ai_enhancement_potential\": 9,\n"
            "        \"revenue_potential\": 8\n"
            "      }\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n"
        )
        
        # Generate rankings
        rankings = generate_json_completion(prompt, system_message)
        
        # If the AI fails to produce valid rankings, return all products
        if not rankings or "product_rankings" not in rankings:
            return products
        
        # Match ranked products back to original product data
        ranked_products = []
        for ranking in rankings.get("product_rankings", []):
            product_name = ranking.get("product_name")
            
            # Find the matching product
            for product in products:
                if product["name"].lower() == product_name.lower():
                    # Add ranking information to the product
                    product["ranking"] = {
                        "overall_score": ranking.get("overall_score"),
                        "justification": ranking.get("justification"),
                        "scores": ranking.get("scores", {})
                    }
                    ranked_products.append(product)
                    break
        
        # If no matches found, return original products
        if not ranked_products:
            return products
            
        return ranked_products
