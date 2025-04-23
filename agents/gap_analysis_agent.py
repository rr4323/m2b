"""
Gap Analysis Agent for identifying improvement opportunities in existing SaaS products.
"""
import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion, analyze_text_with_structure

class GapAnalysisAgent(BaseAgent):
    """Agent for identifying gaps and improvement opportunities in SaaS products."""
    
    def __init__(self):
        """Initialize the Gap Analysis Agent."""
        super().__init__(
            name="Gap Analysis Agent",
            description="Identifies gaps and opportunities in SaaS products"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the gap analysis process.
        
        Args:
            input_data (Dict[str, Any]): Input data containing products discovered by the Market Discovery Agent
                
        Returns:
            Dict[str, Any]: Identified gaps and improvement opportunities
        """
        self.log_info("Starting gap analysis process")
        
        # Extract the products from input
        products = input_data.get("products", [])
        
        if not products:
            self.log_warning("No products provided for gap analysis")
            return {"identified_gaps": {}, "error": "No products provided for analysis"}
        
        # For now, we'll return some hardcoded gaps
        # In a real implementation, we would analyze the products and identify real gaps
        identified_gaps = {
            "feature_gaps": [
                "Better offline support",
                "Dark mode themes",
                "API access for developers",
                "Mobile app experience"
            ],
            "market_gaps": [
                "Enterprise-level security features",
                "Better integration with other productivity tools",
                "More advanced automation capabilities"
            ],
            "user_experience_gaps": [
                "Simpler onboarding process",
                "Better keyboard shortcuts",
                "More intuitive interface"
            ]
        }
        
        # Return the identified gaps
        self.log_info("Completed gap analysis")
        
        return {
            "identified_gaps": identified_gaps,
            "analyzed_products": [p.get("name") for p in products]
        }