"""
Gap Analysis Agent for identifying improvement opportunities in SaaS applications.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.web_scraper import (
    scrape_g2_reviews,
    find_reddit_discussions,
    get_website_text_content
)
from utils.openai_utils import analyze_text_with_structure, generate_json_completion

class GapAnalysisAgent(BaseAgent):
    """Agent for analyzing gaps and improvement opportunities in SaaS applications."""
    
    def __init__(self):
        """Initialize the Gap Analysis Agent."""
        super().__init__(
            name="Gap Analysis Agent",
            description="Identifies improvement opportunities in SaaS applications"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the gap analysis process to identify improvement opportunities.
        
        Args:
            input_data (Dict[str, Any]): Input data containing the product to analyze
                
        Returns:
            Dict[str, Any]: Dictionary containing identified gaps and improvement opportunities
        """
        self.log_info("Starting gap analysis process")
        
        product = input_data.get("product", {})
        
        if not product:
            self.log_error("No product provided for gap analysis")
            return {"error": "No product provided for gap analysis"}
        
        product_name = product.get("name", "")
        product_domain = product.get("domain", "")
        
        self.log_info(f"Analyzing gaps for product: {product_name}")
        
        # Step 1: Collect reviews and feedback
        reviews = await self._collect_reviews(product_name, product_domain)
        
        # Step 2: Analyze feedback to identify gaps
        gaps = await self._identify_gaps(product_name, reviews)
        
        # Step 3: Generate improvement ideas
        improvements = await self._generate_improvements(product, gaps)
        
        return {
            "product_name": product_name,
            "reviews_analyzed": len(reviews),
            "identified_gaps": gaps,
            "improvement_opportunities": improvements
        }
    
    async def _collect_reviews(self, product_name: str, product_domain: str) -> List[Dict[str, Any]]:
        """
        Collect reviews and feedback for a product from various sources.
        
        Args:
            product_name (str): The name of the product
            product_domain (str): The domain of the product
            
        Returns:
            List[Dict[str, Any]]: A list of reviews and feedback
        """
        all_reviews = []
        
        # Try to generate a G2 slug from the product name or domain
        g2_slug = product_domain.replace('.', '-') if product_domain else product_name.lower().replace(' ', '-')
        
        # Collect G2 reviews
        self.log_info(f"Collecting G2 reviews for {product_name}")
        g2_reviews = scrape_g2_reviews(g2_slug, limit=10)
        
        if g2_reviews:
            all_reviews.extend(g2_reviews)
            self.log_info(f"Found {len(g2_reviews)} G2 reviews")
        else:
            self.log_warning(f"No G2 reviews found for {product_name}")
        
        # Find Reddit discussions
        self.log_info(f"Finding Reddit discussions about {product_name}")
        reddit_discussions = find_reddit_discussions(product_name, limit=5)
        
        for discussion in reddit_discussions:
            try:
                url = discussion.get("url", "")
                if url:
                    # Extract content from the Reddit URL
                    content = get_website_text_content(url)
                    if content:
                        discussion["content"] = content
                        all_reviews.append(discussion)
            except Exception as e:
                self.log_error(f"Error extracting content from Reddit discussion: {e}")
        
        self.log_info(f"Found {len(reddit_discussions)} Reddit discussions")
        
        if not all_reviews:
            self.log_warning(f"No reviews found for {product_name}, using AI to generate potential feedback")
            # If no real reviews were found, use AI to generate likely user feedback
            all_reviews = await self._generate_synthetic_feedback(product_name)
        
        return all_reviews
    
    async def _generate_synthetic_feedback(self, product_name: str) -> List[Dict[str, Any]]:
        """
        Generate synthetic feedback when real reviews cannot be found.
        
        Args:
            product_name (str): The name of the product
            
        Returns:
            List[Dict[str, Any]]: A list of synthetic reviews
        """
        system_message = (
            "You are a product review analyst who understands common pain points "
            "in SaaS products. For the given product, generate realistic user "
            "feedback that represents typical complaints and suggestions that users "
            "might have. Make sure to include a mix of positive and negative feedback, "
            "with specific feature requests, usability issues, and pricing concerns."
        )
        
        prompt = (
            f"Generate 10 realistic user reviews for the SaaS product '{product_name}'. "
            f"Each review should include:\n"
            f"1. A title\n"
            f"2. Content with specific feedback\n"
            f"3. A rating from 1 to 5\n"
            f"4. The type of user (role and company size)\n\n"
            f"Make the reviews diverse and realistic, covering different aspects of the "
            f"product and varying sentiments."
        )
        
        reviews_structure = {
            "reviews": [
                {
                    "title": "Example title",
                    "content": "Example content",
                    "rating": 4.5,
                    "user_type": "Marketing Manager at mid-size company",
                    "source": "Synthetic"
                }
            ]
        }
        
        result = analyze_text_with_structure(
            prompt,
            system_message,
            reviews_structure
        )
        
        return result.get("reviews", [])
    
    async def _identify_gaps(
        self, 
        product_name: str, 
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze reviews to identify gaps and pain points.
        
        Args:
            product_name (str): The name of the product
            reviews (List[Dict[str, Any]]): The collected reviews
            
        Returns:
            Dict[str, Any]: Identified gaps and pain points
        """
        self.log_info(f"Identifying gaps from {len(reviews)} reviews")
        
        # Combine all review content for analysis
        combined_content = ""
        
        for i, review in enumerate(reviews):
            content = review.get("content", "")
            title = review.get("title", "Untitled")
            rating = review.get("rating", "No rating")
            source = review.get("source", "Unknown")
            
            combined_content += f"--- Review {i+1} ({source}) ---\n"
            combined_content += f"Title: {title}\n"
            combined_content += f"Rating: {rating}\n"
            combined_content += f"Content: {content}\n\n"
        
        # Define the output structure
        gaps_structure = {
            "list_of_problems": ["Problem 1", "Problem 2"],
            "missing_features": ["Feature 1", "Feature 2"],
            "ui_ux_issues": ["Issue 1", "Issue 2"],
            "pricing_feedback": ["Feedback 1", "Feedback 2"],
            "technical_issues": ["Issue 1", "Issue 2"],
            "competitor_advantages": ["Advantage 1", "Advantage 2"]
        }
        
        # Analyze the combined content to identify gaps
        system_message = (
            f"You are a product analyst specializing in SaaS applications. You have been "
            f"given a collection of reviews for the product '{product_name}'. Analyze these "
            f"reviews to identify common problems, missing features, UI/UX issues, pricing "
            f"feedback, technical issues, and advantages that competitors might have over "
            f"this product."
        )
        
        # If the combined content is too long, summarize it first
        if len(combined_content) > 15000:
            self.log_info("Reviews content is too long, summarizing first")
            summary_prompt = (
                f"Summarize the following reviews for the product '{product_name}', "
                f"focusing on extracting key points of feedback, complaints, and suggestions:\n\n"
                f"{combined_content[:15000]}..."
            )
            combined_content = generate_json_completion(summary_prompt)
        
        gaps = analyze_text_with_structure(
            combined_content,
            system_message,
            gaps_structure
        )
        
        return gaps
    
    async def _generate_improvements(
        self, 
        product: Dict[str, Any], 
        gaps: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate improvement ideas based on identified gaps.
        
        Args:
            product (Dict[str, Any]): The product data
            gaps (Dict[str, Any]): The identified gaps
            
        Returns:
            Dict[str, Any]: Improvement opportunities
        """
        self.log_info("Generating improvement ideas")
        
        product_name = product.get("name", "")
        product_description = product.get("description", "")
        product_features = product.get("feature_list", [])
        
        # Combine product info and gaps for analysis
        system_message = (
            f"You are a product innovation expert specializing in SaaS applications. "
            f"Based on the product information and identified gaps, generate specific "
            f"improvement ideas that would make a significantly better version of this "
            f"product. Focus on realistic, implementable improvements that leverage "
            f"modern technology, AI capabilities, and superior UX design."
        )
        
        prompt = (
            f"Product: {product_name}\n"
            f"Description: {product_description}\n"
            f"Current Features: {', '.join(product_features)}\n\n"
            f"Identified Gaps:\n"
        )
        
        # Add each category of gaps
        for category, items in gaps.items():
            if items:
                category_name = category.replace('_', ' ').title()
                prompt += f"{category_name}:\n"
                for item in items:
                    prompt += f"- {item}\n"
                prompt += "\n"
        
        prompt += (
            f"Based on this information, generate comprehensive improvement ideas "
            f"that would make a significantly better version of {product_name}. Include:\n"
            f"1. Core functionality enhancements\n"
            f"2. User experience improvements\n"
            f"3. AI/ML integrations that would add value\n"
            f"4. Technical architecture improvements\n"
            f"5. Pricing and business model optimizations\n"
            f"6. Key differentiators from the original product\n"
        )
        
        improvements_structure = {
            "core_functionality_enhancements": ["Enhancement 1", "Enhancement 2"],
            "user_experience_improvements": ["Improvement 1", "Improvement 2"],
            "ai_ml_integrations": ["Integration 1", "Integration 2"],
            "technical_improvements": ["Improvement 1", "Improvement 2"],
            "pricing_optimizations": ["Optimization 1", "Optimization 2"],
            "key_differentiators": ["Differentiator 1", "Differentiator 2"],
            "implementation_priority": ["High Priority Item 1", "Medium Priority Item 2"],
            "potential_challenges": ["Challenge 1", "Challenge 2"]
        }
        
        improvements = analyze_text_with_structure(
            prompt,
            system_message,
            improvements_structure
        )
        
        return improvements
