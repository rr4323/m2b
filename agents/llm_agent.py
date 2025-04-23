"""
LLM Agent for integrating AI capabilities into the application.
"""
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion, generate_completion

class LLMAgent(BaseAgent):
    """Agent for integrating AI capabilities into the application."""
    
    def __init__(self):
        """Initialize the LLM Agent."""
        super().__init__(
            name="LLM Agent",
            description="Integrates AI capabilities into the application"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the LLM integration process.
        
        Args:
            input_data (Dict[str, Any]): Input data containing product blueprint and implementation details
                
        Returns:
            Dict[str, Any]: LLM integration details
        """
        self.log_info("Starting LLM integration process")
        
        blueprint = input_data.get("blueprint", {})
        frontend_details = input_data.get("frontend_details", {})
        backend_details = input_data.get("backend_details", {})
        
        if not blueprint:
            self.log_error("No product blueprint provided for LLM integration")
            return {"error": "No product blueprint provided for LLM integration"}
        
        product_name = blueprint.get("product_name", "")
        
        self.log_info(f"Integrating AI capabilities for: {product_name}")
        
        # Step 1: Identify AI use cases
        ai_use_cases = await self._identify_ai_use_cases(blueprint)
        
        # Step 2: Define LLM service architecture
        llm_architecture = await self._define_llm_architecture(blueprint, ai_use_cases)
        
        # Step 3: Create prompt templates
        prompt_templates = await self._create_prompt_templates(ai_use_cases)
        
        # Step 4: Define API endpoints for LLM services
        llm_api_endpoints = await self._define_llm_api_endpoints(llm_architecture)
        
        # Step 5: Create integration code
        integration_code = await self._create_integration_code(
            llm_architecture, 
            prompt_templates, 
            llm_api_endpoints,
            frontend_details,
            backend_details
        )
        
        return {
            "product_name": product_name,
            "ai_use_cases": ai_use_cases,
            "llm_architecture": llm_architecture,
            "prompt_templates": prompt_templates,
            "llm_api_endpoints": llm_api_endpoints,
            "integration_code": integration_code
        }
    
    async def _identify_ai_use_cases(self, blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify AI use cases based on the product blueprint.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            
        Returns:
            List[Dict[str, Any]]: List of AI use cases
        """
        self.log_info("Identifying AI use cases")
        
        features = blueprint.get("features", {})
        ai_integration = blueprint.get("ai_integration", [])
        ai_powered_features = features.get("ai_powered_features", [])
        
        system_message = (
            "You are an AI product expert specializing in integrating large language "
            "models (LLMs) into SaaS applications. Identify concrete AI use cases "
            "for the product based on the specified AI integrations and features. "
            "Each use case should be specific, valuable to users, and technically "
            "feasible with current LLM capabilities."
        )
        
        prompt = (
            f"Identify AI use cases for the product with these specifications:\n\n"
            f"AI Integration: {ai_integration}\n\n"
            f"AI-Powered Features: {ai_powered_features}\n\n"
            f"For each AI use case, provide:\n"
            f"1. Name and description\n"
            f"2. User value proposition\n"
            f"3. Required data inputs\n"
            f"4. Expected outputs\n"
            f"5. LLM capabilities required\n"
            f"6. Implementation complexity (Low, Medium, High)\n"
            f"7. Potential limitations or challenges\n\n"
            f"Focus on use cases that provide real value to users and are "
            f"technically feasible with current LLM capabilities."
        )
        
        use_cases_structure = [
            {
                "name": "Use case name",
                "description": "Use case description",
                "value_proposition": "Value proposition",
                "inputs": ["Input 1", "Input 2"],
                "outputs": ["Output 1", "Output 2"],
                "llm_capabilities": ["Capability 1", "Capability 2"],
                "complexity": "Medium",
                "limitations": ["Limitation 1", "Limitation 2"]
            }
        ]
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, list):
            self.log_error("Failed to identify AI use cases, using default structure")
            return use_cases_structure
        
        return result
    
    async def _define_llm_architecture(
        self, 
        blueprint: Dict[str, Any],
        ai_use_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Define the LLM service architecture.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            ai_use_cases (List[Dict[str, Any]]): The identified AI use cases
            
        Returns:
            Dict[str, Any]: LLM service architecture
        """
        self.log_info("Defining LLM service architecture")
        
        tech_stack = blueprint.get("stack", {})
        
        system_message = (
            "You are an AI architect specializing in integrating large language "
            "models (LLMs) into SaaS applications. Define a comprehensive LLM "
            "service architecture for the product based on the identified AI "
            "use cases. The architecture should be scalable, efficient, and "
            "secure, with considerations for cost optimization."
        )
        
        prompt = (
            f"Define an LLM service architecture for the product with these specifications:\n\n"
            f"Tech Stack: {tech_stack}\n\n"
            f"AI Use Cases: {ai_use_cases}\n\n"
            f"The LLM service architecture should include:\n"
            f"1. LLM provider and model selection\n"
            f"2. API integration approach\n"
            f"3. Prompt management strategy\n"
            f"4. Caching and optimization strategies\n"
            f"5. Error handling and fallback mechanisms\n"
            f"6. Security and privacy considerations\n"
            f"7. Cost optimization approaches\n"
            f"8. Scaling strategies\n\n"
            f"Consider best practices for LLM integration in SaaS applications "
            f"and optimization for the specified use cases."
        )
        
        architecture_structure = {
            "llm_provider": {
                "name": "Provider name",
                "models": ["Model 1", "Model 2"],
                "justification": "Justification for this choice"
            },
            "api_integration": {
                "approach": "Integration approach",
                "implementation": "Implementation details"
            },
            "prompt_management": {
                "strategy": "Prompt management strategy",
                "implementation": "Implementation details"
            },
            "optimization": {
                "caching": "Caching strategy",
                "batching": "Batching strategy",
                "techniques": ["Technique 1", "Technique 2"]
            },
            "error_handling": {
                "strategies": ["Strategy 1", "Strategy 2"],
                "fallbacks": ["Fallback 1", "Fallback 2"]
            },
            "security": {
                "considerations": ["Consideration 1", "Consideration 2"],
                "implementation": "Implementation details"
            },
            "cost_optimization": {
                "strategies": ["Strategy 1", "Strategy 2"],
                "implementation": "Implementation details"
            },
            "scaling": {
                "approach": "Scaling approach",
                "implementation": "Implementation details"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define LLM architecture, using default structure")
            return architecture_structure
        
        return result
    
    async def _create_prompt_templates(self, ai_use_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create prompt templates for each AI use case.
        
        Args:
            ai_use_cases (List[Dict[str, Any]]): The identified AI use cases
            
        Returns:
            Dict[str, Any]: Prompt templates for each use case
        """
        self.log_info("Creating prompt templates")
        
        prompt_templates = {}
        
        for use_case in ai_use_cases:
            use_case_name = use_case.get("name", "")
            use_case_description = use_case.get("description", "")
            use_case_inputs = use_case.get("inputs", [])
            use_case_outputs = use_case.get("outputs", [])
            
            self.log_info(f"Creating prompt template for: {use_case_name}")
            
            system_message = (
                "You are a prompt engineering expert specializing in designing effective "
                "prompts for large language models (LLMs). Create a comprehensive prompt "
                "template for the specified AI use case, including system message, "
                "user message template, and output formatting instructions. The prompt "
                "should be optimized for the intended LLM capabilities and use case."
            )
            
            prompt = (
                f"Create a prompt template for the following AI use case:\n\n"
                f"Use Case: {use_case_name}\n"
                f"Description: {use_case_description}\n"
                f"Inputs: {use_case_inputs}\n"
                f"Expected Outputs: {use_case_outputs}\n\n"
                f"The prompt template should include:\n"
                f"1. System message that sets the context and role for the LLM\n"
                f"2. User message template with placeholders for inputs\n"
                f"3. Output formatting instructions\n"
                f"4. Few-shot examples (if applicable)\n"
                f"5. Constraints and guidelines for the LLM\n\n"
                f"The prompt should be designed to maximize the quality and "
                f"consistency of the LLM's outputs for this specific use case."
            )
            
            template_structure = {
                "system_message": "System message content",
                "user_message_template": "User message template with {placeholders}",
                "output_format": "Output format specification",
                "examples": [
                    {
                        "input": "Example input",
                        "output": "Example output"
                    }
                ],
                "constraints": ["Constraint 1", "Constraint 2"],
                "notes": "Additional notes and considerations"
            }
            
            result = generate_json_completion(prompt, system_message)
            
            if result and isinstance(result, dict):
                prompt_templates[use_case_name] = result
            else:
                self.log_error(f"Failed to create prompt template for {use_case_name}")
                prompt_templates[use_case_name] = template_structure
        
        return prompt_templates
    
    async def _define_llm_api_endpoints(self, llm_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define API endpoints for LLM services.
        
        Args:
            llm_architecture (Dict[str, Any]): The LLM service architecture
            
        Returns:
            Dict[str, Any]: LLM API endpoint specifications
        """
        self.log_info("Defining LLM API endpoints")
        
        api_integration = llm_architecture.get("api_integration", {})
        
        system_message = (
            "You are an API designer specializing in AI-powered services. Define "
            "comprehensive API endpoints for LLM services based on the specified "
            "LLM architecture. The API endpoints should be RESTful, intuitive, "
            "and follow best practices for API design."
        )
        
        prompt = (
            f"Define API endpoints for LLM services with these specifications:\n\n"
            f"API Integration Approach: {api_integration}\n\n"
            f"The API endpoints should include:\n"
            f"1. Endpoint paths and HTTP methods\n"
            f"2. Request parameters and body schemas\n"
            f"3. Response schemas\n"
            f"4. Authentication requirements\n"
            f"5. Rate limiting and caching directives\n"
            f"6. Error responses and status codes\n\n"
            f"Consider best practices for API design and optimization for "
            f"LLM service integration."
        )
        
        api_structure = {
            "base_path": "/api/v1/ai",
            "authentication": "JWT Bearer token",
            "endpoints": [
                {
                    "name": "Endpoint name",
                    "path": "/endpoint-path",
                    "method": "POST",
                    "description": "Endpoint description",
                    "request": {
                        "body": {
                            "property1": {
                                "type": "string",
                                "description": "Property description"
                            }
                        }
                    },
                    "response": {
                        "success": {
                            "status_code": 200,
                            "body": {
                                "property1": {
                                    "type": "string",
                                    "description": "Property description"
                                }
                            }
                        },
                        "error": {
                            "status_codes": [400, 401, 500],
                            "body": {
                                "error": {
                                    "type": "string",
                                    "description": "Error message"
                                }
                            }
                        }
                    },
                    "rate_limit": "Rate limit specification",
                    "caching": "Caching directive"
                }
            ],
            "error_handling": {
                "approach": "Error handling approach",
                "error_codes": ["ERROR_CODE_1", "ERROR_CODE_2"]
            },
            "rate_limiting": {
                "approach": "Rate limiting approach",
                "limits": "Rate limits description"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define LLM API endpoints, using default structure")
            return api_structure
        
        return result
    
    async def _create_integration_code(
        self, 
        llm_architecture: Dict[str, Any],
        prompt_templates: Dict[str, Any],
        llm_api_endpoints: Dict[str, Any],
        frontend_details: Dict[str, Any],
        backend_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create integration code for LLM services.
        
        Args:
            llm_architecture (Dict[str, Any]): The LLM service architecture
            prompt_templates (Dict[str, Any]): The prompt templates
            llm_api_endpoints (Dict[str, Any]): The LLM API endpoint specifications
            frontend_details (Dict[str, Any]): The frontend implementation details
            backend_details (Dict[str, Any]): The backend implementation details
            
        Returns:
            Dict[str, Any]: Integration code
        """
        self.log_info("Creating integration code")
        
        llm_provider = llm_architecture.get("llm_provider", {})
        backend_tech = backend_details.get("architecture", {}).get("framework", {}).get("name", "FastAPI")
        frontend_tech = frontend_details.get("architecture", {}).get("framework", {}).get("name", "React")
        
        integration_code = {
            "backend": {},
            "frontend": {}
        }
        
        # Generate backend integration code
        system_message = (
            f"You are a backend developer specializing in AI integration for {backend_tech} "
            f"applications. Create code for integrating LLM services into the backend "
            f"based on the specified architecture, prompt templates, and API endpoints. "
            f"The code should be efficient, secure, and follow best practices for "
            f"{backend_tech} development."
        )
        
        prompt = (
            f"Create backend integration code for LLM services with these specifications:\n\n"
            f"Backend Framework: {backend_tech}\n"
            f"LLM Provider: {llm_provider}\n"
            f"API Endpoints: {llm_api_endpoints.get('endpoints', [])[:1]}\n\n"
            f"Create code for:\n"
            f"1. LLM service client\n"
            f"2. API route implementations\n"
            f"3. Prompt management utilities\n"
            f"4. Error handling and retries\n\n"
            f"The code should be optimized for the specified backend framework "
            f"and follow best practices for LLM integration."
        )
        
        backend_code_structure = {
            "llm_client": "LLM client code",
            "api_routes": "API route implementation code",
            "prompt_management": "Prompt management utility code",
            "error_handling": "Error handling code"
        }
        
        backend_result = generate_json_completion(prompt, system_message)
        
        if backend_result and isinstance(backend_result, dict):
            integration_code["backend"] = backend_result
        else:
            self.log_error("Failed to create backend integration code")
            integration_code["backend"] = backend_code_structure
        
        # Generate frontend integration code
        system_message = (
            f"You are a frontend developer specializing in AI integration for {frontend_tech} "
            f"applications. Create code for integrating LLM services into the frontend "
            f"based on the specified architecture and API endpoints. The code should be "
            f"efficient, user-friendly, and follow best practices for {frontend_tech} development."
        )
        
        prompt = (
            f"Create frontend integration code for LLM services with these specifications:\n\n"
            f"Frontend Framework: {frontend_tech}\n"
            f"API Endpoints: {llm_api_endpoints.get('endpoints', [])[:1]}\n\n"
            f"Create code for:\n"
            f"1. API client for LLM services\n"
            f"2. UI components for AI features\n"
            f"3. State management for AI interactions\n"
            f"4. Error handling and loading states\n\n"
            f"The code should be optimized for the specified frontend framework "
            f"and provide a good user experience for AI features."
        )
        
        frontend_code_structure = {
            "api_client": "API client code",
            "ui_components": "UI component code",
            "state_management": "State management code",
            "error_handling": "Error handling code"
        }
        
        frontend_result = generate_json_completion(prompt, system_message)
        
        if frontend_result and isinstance(frontend_result, dict):
            integration_code["frontend"] = frontend_result
        else:
            self.log_error("Failed to create frontend integration code")
            integration_code["frontend"] = frontend_code_structure
        
        return integration_code
