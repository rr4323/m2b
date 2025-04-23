"""
Product Blueprint Agent for creating enhanced product specifications.
"""
import logging
import json
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.openai_utils import analyze_text_with_structure, generate_json_completion

class ProductBlueprintAgent(BaseAgent):
    """Agent for creating enhanced product specifications based on gap analysis."""
    
    def __init__(self):
        """Initialize the Product Blueprint Agent."""
        super().__init__(
            name="Product Blueprint Agent",
            description="Creates enhanced product specifications"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the product blueprint process to create an enhanced specification.
        
        Args:
            input_data (Dict[str, Any]): Input data containing product and gap analysis
                
        Returns:
            Dict[str, Any]: Enhanced product specification
        """
        self.log_info("Starting product blueprint creation")
        
        product = input_data.get("product", {})
        gaps = input_data.get("identified_gaps", {})
        improvements = input_data.get("improvement_opportunities", {})
        
        if not product:
            self.log_error("No product provided for blueprint creation")
            return {"error": "No product provided for blueprint creation"}
        
        product_name = product.get("name", "")
        
        self.log_info(f"Creating blueprint for enhanced version of: {product_name}")
        
        # Step 1: Generate a new product name
        new_product_name = await self._generate_product_name(product_name)
        
        # Step 2: Define the core feature set
        feature_set = await self._define_feature_set(product, gaps, improvements)
        
        # Step 3: Specify the technical stack
        tech_stack = await self._specify_tech_stack(product, improvements)
        
        # Step 4: Create the complete product blueprint
        blueprint = await self._create_blueprint(
            new_product_name,
            product,
            gaps,
            improvements,
            feature_set,
            tech_stack
        )
        
        return blueprint
    
    async def _generate_product_name(self, original_name: str) -> str:
        """
        Generate a new name for the enhanced product.
        
        Args:
            original_name (str): The original product name
            
        Returns:
            str: The new product name
        """
        self.log_info(f"Generating new name based on: {original_name}")
        
        system_message = (
            "You are a product naming expert. Create a new, distinctive name for "
            "an enhanced version of the provided product. The name should be:"
            "1. Memorable and brandable\n"
            "2. Suggestive of the product's purpose\n"
            "3. Different enough from the original to avoid legal issues\n"
            "4. Available as a .com domain (consider checking)\n"
            "5. Modern and professional sounding"
        )
        
        prompt = (
            f"Create a new product name for an enhanced version of '{original_name}'. "
            f"The new product will be similar but significantly improved. "
            f"Provide 5 potential names and then select the best one with a brief explanation."
        )
        
        name_structure = {
            "potential_names": ["Name 1", "Name 2", "Name 3", "Name 4", "Name 5"],
            "selected_name": "Best Name",
            "explanation": "Reason this name was selected"
        }
        
        result = analyze_text_with_structure(
            prompt,
            system_message,
            name_structure
        )
        
        return result.get("selected_name", f"Better{original_name}")
    
    async def _define_feature_set(
        self, 
        product: Dict[str, Any],
        gaps: Dict[str, Any],
        improvements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define the feature set for the enhanced product.
        
        Args:
            product (Dict[str, Any]): The original product data
            gaps (Dict[str, Any]): The identified gaps
            improvements (Dict[str, Any]): The improvement opportunities
            
        Returns:
            Dict[str, Any]: The defined feature set
        """
        self.log_info("Defining feature set for enhanced product")
        
        product_name = product.get("name", "")
        product_features = product.get("feature_list", [])
        missing_features = gaps.get("missing_features", [])
        core_enhancements = improvements.get("core_functionality_enhancements", [])
        ai_integrations = improvements.get("ai_ml_integrations", [])
        
        system_message = (
            "You are a product manager specializing in SaaS applications. "
            "Define a comprehensive feature set for an enhanced version of "
            "the provided product. The feature set should include retained "
            "features from the original product, improvements to address "
            "identified gaps, and innovative new features that leverage "
            "modern technology and AI capabilities."
        )
        
        prompt = (
            f"Define a feature set for an enhanced version of '{product_name}'.\n\n"
            f"Original Features: {json.dumps(product_features)}\n\n"
            f"Missing Features: {json.dumps(missing_features)}\n\n"
            f"Proposed Enhancements: {json.dumps(core_enhancements)}\n\n"
            f"AI Integrations: {json.dumps(ai_integrations)}\n\n"
            f"Create a comprehensive feature set that includes:\n"
            f"1. Core features (retained from original with improvements)\n"
            f"2. New features (addressing missing features and gaps)\n"
            f"3. Advanced features (innovative additions that differentiate)\n"
            f"4. AI-powered features (specific implementations of AI technology)\n\n"
            f"For each feature, provide a name, description, and priority (Core, High, Medium, Low)."
        )
        
        feature_set_structure = {
            "core_features": [
                {
                    "name": "Feature name",
                    "description": "Feature description",
                    "priority": "Core",
                    "status": "Retained" # or "Improved"
                }
            ],
            "new_features": [
                {
                    "name": "Feature name",
                    "description": "Feature description",
                    "priority": "High", # or "Medium" or "Low"
                    "addresses_gap": "Description of the gap this addresses"
                }
            ],
            "advanced_features": [
                {
                    "name": "Feature name",
                    "description": "Feature description",
                    "priority": "Medium", # or "High" or "Low"
                    "differentiator": "How this differentiates from competitors"
                }
            ],
            "ai_powered_features": [
                {
                    "name": "Feature name",
                    "description": "Feature description",
                    "priority": "High", # or "Medium" or "Low"
                    "ai_technology": "Specific AI/ML technology used"
                }
            ]
        }
        
        feature_set = analyze_text_with_structure(
            prompt,
            system_message,
            feature_set_structure
        )
        
        return feature_set
    
    async def _specify_tech_stack(
        self, 
        product: Dict[str, Any],
        improvements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Specify the technical stack for the enhanced product.
        
        Args:
            product (Dict[str, Any]): The original product data
            improvements (Dict[str, Any]): The improvement opportunities
            
        Returns:
            Dict[str, Any]: The specified technical stack
        """
        self.log_info("Specifying technical stack")
        
        original_tech_stack = product.get("tech_stack", [])
        technical_improvements = improvements.get("technical_improvements", [])
        
        system_message = (
            "You are a technical architect specializing in SaaS applications. "
            "Specify a modern, scalable, and maintainable technical stack for "
            "the enhanced product. Consider performance, security, scalability, "
            "developer experience, and integration capabilities."
        )
        
        prompt = (
            f"Specify a technical stack for the enhanced product.\n\n"
            f"Original Tech Stack (if known): {json.dumps(original_tech_stack)}\n\n"
            f"Technical Improvements: {json.dumps(technical_improvements)}\n\n"
            f"Define a comprehensive technical stack that includes:\n"
            f"1. Frontend technology\n"
            f"2. Backend technology\n"
            f"3. Database and storage\n"
            f"4. Authentication and authorization\n"
            f"5. Infrastructure and deployment\n"
            f"6. AI/ML components\n"
            f"7. Third-party services and APIs\n\n"
            f"For each component, provide specific technologies and explain why they are appropriate."
        )
        
        tech_stack_structure = {
            "frontend": {
                "framework": "Framework name",
                "ui_library": "UI library name",
                "state_management": "State management solution",
                "justification": "Justification for these choices"
            },
            "backend": {
                "framework": "Framework name",
                "language": "Programming language",
                "api_design": "API design approach",
                "justification": "Justification for these choices"
            },
            "database_storage": {
                "primary_database": "Database name",
                "caching": "Caching solution",
                "file_storage": "File storage solution",
                "justification": "Justification for these choices"
            },
            "auth": {
                "service": "Auth service name",
                "implementation": "Implementation details",
                "justification": "Justification for these choices"
            },
            "infrastructure": {
                "hosting": "Hosting solution",
                "containers": "Container solution",
                "ci_cd": "CI/CD pipeline",
                "monitoring": "Monitoring solution",
                "justification": "Justification for these choices"
            },
            "ai_ml": {
                "frameworks": "AI/ML frameworks",
                "services": "AI/ML services",
                "justification": "Justification for these choices"
            },
            "third_party_services": [
                {
                    "name": "Service name",
                    "purpose": "Service purpose",
                    "justification": "Justification for this choice"
                }
            ]
        }
        
        tech_stack = analyze_text_with_structure(
            prompt,
            system_message,
            tech_stack_structure
        )
        
        return tech_stack
    
    async def _create_blueprint(
        self,
        new_product_name: str,
        product: Dict[str, Any],
        gaps: Dict[str, Any],
        improvements: Dict[str, Any],
        feature_set: Dict[str, Any],
        tech_stack: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create the complete product blueprint.
        
        Args:
            new_product_name (str): The name of the enhanced product
            product (Dict[str, Any]): The original product data
            gaps (Dict[str, Any]): The identified gaps
            improvements (Dict[str, Any]): The improvement opportunities
            feature_set (Dict[str, Any]): The defined feature set
            tech_stack (Dict[str, Any]): The specified technical stack
            
        Returns:
            Dict[str, Any]: The complete product blueprint
        """
        self.log_info("Creating complete product blueprint")
        
        # Get target user and pricing from improvements
        pricing_optimizations = improvements.get("pricing_optimizations", [])
        
        # Define the output structure
        blueprint_structure = {
            "product_name": new_product_name,
            "original_product": product.get("name", ""),
            "description": "Product description",
            "features": feature_set,
            "enhancements": improvements.get("key_differentiators", []),
            "ai_integration": improvements.get("ai_ml_integrations", []),
            "target_user": "Description of target users",
            "pricing_strategy": "Pricing strategy",
            "stack": tech_stack,
            "implementation_roadmap": {
                "phase_1": ["Item 1", "Item 2"],
                "phase_2": ["Item 1", "Item 2"],
                "phase_3": ["Item 1", "Item 2"]
            },
            "marketing_highlights": ["Highlight 1", "Highlight 2"],
            "potential_challenges": improvements.get("potential_challenges", [])
        }
        
        system_message = (
            "You are a product strategist specializing in SaaS applications. "
            "Create a comprehensive blueprint for the enhanced product that "
            "combines all the information about features, technology, target users, "
            "and implementation strategy. This blueprint will serve as the "
            "foundational document for building the enhanced product."
        )
        
        prompt = (
            f"Create a comprehensive blueprint for '{new_product_name}', an enhanced "
            f"version of '{product.get('name', '')}'.\n\n"
            f"Use the following information to create the blueprint:\n"
            f"- Original product description: {product.get('description', '')}\n"
            f"- Key differentiators: {json.dumps(improvements.get('key_differentiators', []))}\n"
            f"- Pricing optimizations: {json.dumps(pricing_optimizations)}\n\n"
            f"Create a comprehensive blueprint that includes a compelling product description, "
            f"target user definition, pricing strategy, and implementation roadmap that logically "
            f"phases the development of the enhanced product."
        )
        
        blueprint = analyze_text_with_structure(
            prompt,
            system_message,
            blueprint_structure
        )
        
        # Add the pre-defined components
        blueprint["product_name"] = new_product_name
        blueprint["original_product"] = product.get("name", "")
        blueprint["features"] = feature_set
        blueprint["enhancements"] = improvements.get("key_differentiators", [])
        blueprint["ai_integration"] = improvements.get("ai_ml_integrations", [])
        blueprint["stack"] = tech_stack
        blueprint["potential_challenges"] = improvements.get("potential_challenges", [])
        
        return blueprint
