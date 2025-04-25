"""
Frontend Agent for developing the frontend of SaaS products.
"""
import logging
import os
from typing import Dict, Any

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion, generate_completion

class FrontendAgent(BaseAgent):
    """Agent for developing the frontend of SaaS products."""
    
    def __init__(self):
        """Initialize the Frontend Agent."""
        super().__init__(
            name="Frontend Agent",
            description="Develops the frontend of SaaS products"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the frontend development process.
        
        Args:
            input_data (Dict[str, Any]): Input data containing product blueprint and design
                
        Returns:
            Dict[str, Any]: The frontend implementation details and output path
        """
        self.log_info("Starting frontend development")
        
        # Extract the necessary data from input
        blueprint = input_data.get("product_blueprint", {})
        design = input_data.get("design", {})
        agent_context = input_data.get("_agent_context")
        
        if agent_context != "frontend":
            self.log_warning("Skipping frontend agent as context is not frontend")
            return {}
        
        if not blueprint or not design:
            self.log_warning("Insufficient data for frontend development")
            return {"frontend_result": {}, "error": "Insufficient data for frontend development"}
        
        # Example: Generate a simple React component from blueprint
        output_dir = "output/frontend/"
        os.makedirs(output_dir, exist_ok=True)
        component_name = blueprint.get("name", "App").replace(" ", "")
        component_file = os.path.join(output_dir, f"{component_name}.jsx")
        component_code = f"""
import React from 'react';

export default function {component_name}() {{
    return (
        <div style={{{{ padding: 32 }}}}>
            <h1>{blueprint.get('name', 'Product')}</h1>
            <p>{blueprint.get('description', '')}</p>
            {{{{/* Add more UI based on design and features */}}}}
        </div>
    );
}}
"""
        with open(component_file, "w") as f:
            f.write(component_code)

        frontend_implementation = {
            "tech_stack": {
                "framework": "React",
                "styling": "Tailwind CSS",
                "state_management": "Redux Toolkit",
                "routing": "React Router",
                "api_client": "Axios",
                "testing": "Jest + React Testing Library"
            },
            "components": {
                "layout": [
                    "Header",
                    "Sidebar",
                    "Footer",
                    "MainContent"
                ]
            },
            "main_component_file": component_file
        }
        
        self.log_info("Completed frontend development")
        
        return {
            "frontend_result": frontend_implementation,
            "output_path": output_dir
        }