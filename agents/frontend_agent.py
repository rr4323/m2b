"""
Frontend Agent for building the frontend application.
"""
import logging
import json
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion, generate_completion

class FrontendAgent(BaseAgent):
    """Agent for building the frontend application based on design specs."""
    
    def __init__(self):
        """Initialize the Frontend Agent."""
        super().__init__(
            name="Frontend Agent",
            description="Builds the frontend application based on design specs"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the frontend development process.
        
        Args:
            input_data (Dict[str, Any]): Input data containing design specs and blueprint
                
        Returns:
            Dict[str, Any]: Frontend implementation details
        """
        self.log_info("Starting frontend development process")
        
        blueprint = input_data.get("blueprint", {})
        design_specs = input_data.get("design_specs", {})
        
        if not blueprint:
            self.log_error("No product blueprint provided for frontend development")
            return {"error": "No product blueprint provided for frontend development"}
        
        if not design_specs:
            self.log_error("No design specs provided for frontend development")
            return {"error": "No design specs provided for frontend development"}
        
        product_name = blueprint.get("product_name", "")
        
        self.log_info(f"Building frontend for: {product_name}")
        
        # Step 1: Define frontend architecture
        architecture = await self._define_architecture(blueprint, design_specs)
        
        # Step 2: Create component specifications
        components = await self._create_component_specs(design_specs)
        
        # Step 3: Generate page implementations
        pages = await self._generate_page_implementations(design_specs, components)
        
        # Step 4: Define state management strategy
        state_management = await self._define_state_management(blueprint, pages)
        
        # Step 5: Define API integration approach
        api_integration = await self._define_api_integration(blueprint)
        
        # Step 6: Generate project structure
        project_structure = await self._generate_project_structure(
            architecture, 
            components, 
            pages, 
            state_management, 
            api_integration
        )
        
        return {
            "product_name": product_name,
            "architecture": architecture,
            "components": components,
            "pages": pages,
            "state_management": state_management,
            "api_integration": api_integration,
            "project_structure": project_structure
        }
    
    async def _define_architecture(
        self, 
        blueprint: Dict[str, Any],
        design_specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define the frontend architecture.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            design_specs (Dict[str, Any]): The design specifications
            
        Returns:
            Dict[str, Any]: Frontend architecture specification
        """
        self.log_info("Defining frontend architecture")
        
        tech_stack = blueprint.get("stack", {})
        frontend_tech = tech_stack.get("frontend", {})
        
        system_message = (
            "You are a frontend architect specializing in SaaS applications. "
            "Define a comprehensive frontend architecture for the product based "
            "on the specified technology stack and design requirements. The "
            "architecture should be modern, maintainable, and scalable."
        )
        
        prompt = (
            f"Define a frontend architecture for the product with these specifications:\n\n"
            f"Frontend Tech Stack: {json.dumps(frontend_tech)}\n\n"
            f"The architecture should include:\n"
            f"1. Framework and library choices\n"
            f"2. Project structure\n"
            f"3. Component organization\n"
            f"4. State management approach\n"
            f"5. Routing strategy\n"
            f"6. API integration approach\n"
            f"7. Performance optimization strategies\n"
            f"8. Testing approach\n\n"
            f"Justify your architectural decisions and explain how they support "
            f"the product's requirements."
        )
        
        architecture_structure = {
            "framework": {
                "name": "Framework name",
                "version": "Version",
                "justification": "Justification for this choice"
            },
            "ui_library": {
                "name": "UI library name",
                "version": "Version",
                "justification": "Justification for this choice"
            },
            "project_organization": {
                "structure": "Structure description",
                "patterns": ["Pattern 1", "Pattern 2"]
            },
            "component_strategy": {
                "approach": "Approach description",
                "organization": "Organization description"
            },
            "state_management": {
                "solution": "Solution name",
                "approach": "Approach description"
            },
            "routing": {
                "library": "Library name",
                "strategy": "Strategy description"
            },
            "api_integration": {
                "library": "Library name",
                "approach": "Approach description"
            },
            "performance": {
                "strategies": ["Strategy 1", "Strategy 2"]
            },
            "testing": {
                "framework": "Framework name",
                "approach": "Approach description"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define frontend architecture, using default structure")
            return architecture_structure
        
        return result
    
    async def _create_component_specs(self, design_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create specifications for frontend components.
        
        Args:
            design_specs (Dict[str, Any]): The design specifications
            
        Returns:
            Dict[str, Any]: Component specifications
        """
        self.log_info("Creating component specifications")
        
        design_system = design_specs.get("design_system", {})
        component_library = design_specs.get("component_library", {})
        
        system_message = (
            "You are a frontend component designer specializing in SaaS applications. "
            "Create specifications for implementing the components defined in the "
            "design system and component library. The specifications should be "
            "detailed enough for a developer to implement the components."
        )
        
        prompt = (
            f"Create component specifications based on this design system and component library:\n\n"
            f"Design System: {json.dumps(design_system)[:1000]}...\n\n"
            f"Component Library: {json.dumps(component_library)[:1000]}...\n\n"
            f"For each component category, create detailed specifications that include:\n"
            f"1. Component name and description\n"
            f"2. Props and prop types\n"
            f"3. Component variants\n"
            f"4. States and behaviors\n"
            f"5. Interaction patterns\n"
            f"6. Accessibility requirements\n"
            f"7. Implementation considerations\n\n"
            f"Focus on the most important components for a SaaS application."
        )
        
        component_specs_structure = {
            "button": {
                "description": "Component description",
                "props": {
                    "variant": {
                        "type": "string",
                        "options": ["primary", "secondary", "tertiary"],
                        "default": "primary"
                    },
                    "size": {
                        "type": "string",
                        "options": ["small", "medium", "large"],
                        "default": "medium"
                    },
                    "isLoading": {
                        "type": "boolean",
                        "default": false
                    },
                    "isDisabled": {
                        "type": "boolean",
                        "default": false
                    },
                    "onClick": {
                        "type": "function",
                        "description": "Function called when button is clicked"
                    }
                },
                "variants": ["primary", "secondary", "tertiary"],
                "states": ["default", "hover", "active", "focus", "disabled", "loading"],
                "accessibility": "Accessibility requirements",
                "implementation": "Implementation considerations"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to create component specs, using default structure")
            return component_specs_structure
        
        return result
    
    async def _generate_page_implementations(
        self, 
        design_specs: Dict[str, Any],
        components: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate implementation details for pages.
        
        Args:
            design_specs (Dict[str, Any]): The design specifications
            components (Dict[str, Any]): The component specifications
            
        Returns:
            Dict[str, Any]: Page implementation details
        """
        self.log_info("Generating page implementations")
        
        page_specs = design_specs.get("page_specs", [])
        wireframes = design_specs.get("wireframes", {})
        
        # Select key pages for implementation (limit to 5 for efficiency)
        key_pages = page_specs[:5] if len(page_specs) > 5 else page_specs
        
        page_implementations = {}
        
        for page in key_pages:
            page_name = page.get("name", "")
            page_path = page.get("path", "")
            wireframe = wireframes.get(page_name, {})
            
            self.log_info(f"Generating implementation for page: {page_name}")
            
            system_message = (
                "You are a frontend developer specializing in SaaS applications. "
                "Generate implementation details for the specified page based on "
                "the wireframe and page specifications. The implementation details "
                "should be detailed enough for a developer to create the page."
            )
            
            prompt = (
                f"Generate implementation details for the {page_name} page at path '{page_path}'.\n\n"
                f"Page specification:\n{json.dumps(page)[:1000]}...\n\n"
                f"Wireframe:\n{json.dumps(wireframe)[:1000]}...\n\n"
                f"The implementation details should include:\n"
                f"1. Component structure and hierarchy\n"
                f"2. Data requirements and sources\n"
                f"3. State management\n"
                f"4. Event handlers and user interactions\n"
                f"5. Responsive behavior\n"
                f"6. Accessibility considerations\n\n"
                f"Use components from the component library where appropriate."
            )
            
            page_implementation_structure = {
                "name": page_name,
                "path": page_path,
                "component_structure": "Component structure description",
                "data_requirements": ["Requirement 1", "Requirement 2"],
                "state": {
                    "local_state": ["State item 1", "State item 2"],
                    "global_state": ["State item 1", "State item 2"]
                },
                "event_handlers": ["Handler 1", "Handler 2"],
                "responsive_behavior": "Responsive behavior description",
                "accessibility": "Accessibility considerations",
                "implementation_notes": "Implementation notes"
            }
            
            result = generate_json_completion(prompt, system_message)
            
            if result and isinstance(result, dict):
                page_implementations[page_name] = result
            else:
                self.log_error(f"Failed to generate implementation for {page_name}")
                page_implementations[page_name] = page_implementation_structure
        
        return page_implementations
    
    async def _define_state_management(
        self, 
        blueprint: Dict[str, Any],
        pages: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define the state management strategy.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            pages (Dict[str, Any]): The page implementation details
            
        Returns:
            Dict[str, Any]: State management strategy
        """
        self.log_info("Defining state management strategy")
        
        tech_stack = blueprint.get("stack", {})
        frontend_tech = tech_stack.get("frontend", {})
        
        system_message = (
            "You are a frontend architect specializing in state management for "
            "SaaS applications. Define a comprehensive state management strategy "
            "for the product based on the specified technology stack and page "
            "requirements. The strategy should be efficient, maintainable, and "
            "appropriate for the scale of the application."
        )
        
        prompt = (
            f"Define a state management strategy with these specifications:\n\n"
            f"Frontend Tech Stack: {json.dumps(frontend_tech)}\n\n"
            f"Pages: {json.dumps(list(pages.keys()))}\n\n"
            f"The state management strategy should include:\n"
            f"1. State management library/approach\n"
            f"2. Global state structure\n"
            f"3. Local state guidelines\n"
            f"4. State update patterns\n"
            f"5. Async state management\n"
            f"6. Persistence strategy\n"
            f"7. Performance considerations\n\n"
            f"Justify your state management decisions and explain how they support "
            f"the product's requirements."
        )
        
        state_management_structure = {
            "library": {
                "name": "Library name",
                "justification": "Justification for this choice"
            },
            "global_state": {
                "structure": "Structure description",
                "slices": ["Slice 1", "Slice 2"]
            },
            "local_state": {
                "guidelines": "Guidelines description",
                "patterns": ["Pattern 1", "Pattern 2"]
            },
            "update_patterns": {
                "synchronous": "Synchronous update pattern",
                "asynchronous": "Asynchronous update pattern"
            },
            "async_management": {
                "approach": "Approach description",
                "patterns": ["Pattern 1", "Pattern 2"]
            },
            "persistence": {
                "strategy": "Persistence strategy",
                "implementation": "Implementation description"
            },
            "performance": {
                "considerations": ["Consideration 1", "Consideration 2"],
                "optimization_techniques": ["Technique 1", "Technique 2"]
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define state management strategy, using default structure")
            return state_management_structure
        
        return result
    
    async def _define_api_integration(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define the API integration approach.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            
        Returns:
            Dict[str, Any]: API integration approach
        """
        self.log_info("Defining API integration approach")
        
        tech_stack = blueprint.get("stack", {})
        frontend_tech = tech_stack.get("frontend", {})
        backend_tech = tech_stack.get("backend", {})
        
        system_message = (
            "You are a frontend architect specializing in API integration for "
            "SaaS applications. Define a comprehensive API integration approach "
            "for the product based on the specified technology stack. The approach "
            "should be efficient, maintainable, and secure."
        )
        
        prompt = (
            f"Define an API integration approach with these specifications:\n\n"
            f"Frontend Tech Stack: {json.dumps(frontend_tech)}\n\n"
            f"Backend Tech Stack: {json.dumps(backend_tech)}\n\n"
            f"The API integration approach should include:\n"
            f"1. API client library/approach\n"
            f"2. Authentication handling\n"
            f"3. Request/response handling\n"
            f"4. Error handling\n"
            f"5. Caching strategy\n"
            f"6. Rate limiting and retry logic\n"
            f"7. Type safety\n\n"
            f"Justify your API integration decisions and explain how they support "
            f"the product's requirements."
        )
        
        api_integration_structure = {
            "client": {
                "library": "Library name",
                "configuration": "Configuration description",
                "justification": "Justification for this choice"
            },
            "authentication": {
                "approach": "Approach description",
                "implementation": "Implementation description"
            },
            "request_handling": {
                "pattern": "Pattern description",
                "implementation": "Implementation description"
            },
            "response_handling": {
                "pattern": "Pattern description",
                "implementation": "Implementation description"
            },
            "error_handling": {
                "strategy": "Strategy description",
                "implementation": "Implementation description"
            },
            "caching": {
                "strategy": "Strategy description",
                "implementation": "Implementation description"
            },
            "rate_limiting": {
                "strategy": "Strategy description",
                "implementation": "Implementation description"
            },
            "type_safety": {
                "approach": "Approach description",
                "implementation": "Implementation description"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define API integration approach, using default structure")
            return api_integration_structure
        
        return result
    
    async def _generate_project_structure(
        self, 
        architecture: Dict[str, Any],
        components: Dict[str, Any],
        pages: Dict[str, Any],
        state_management: Dict[str, Any],
        api_integration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate the frontend project structure.
        
        Args:
            architecture (Dict[str, Any]): The frontend architecture
            components (Dict[str, Any]): The component specifications
            pages (Dict[str, Any]): The page implementation details
            state_management (Dict[str, Any]): The state management strategy
            api_integration (Dict[str, Any]): The API integration approach
            
        Returns:
            Dict[str, Any]: Project structure
        """
        self.log_info("Generating project structure")
        
        framework = architecture.get("framework", {}).get("name", "").lower()
        
        # Determine appropriate structure based on framework
        base_structure = "Next.js" if "next" in framework else "React" if "react" in framework else "Generic"
        
        system_message = (
            f"You are a frontend architect specializing in {base_structure} applications. "
            f"Generate a comprehensive project structure for the product based on "
            f"the specified architecture, components, pages, state management, and "
            f"API integration approach. The structure should be organized, maintainable, "
            f"and follow best practices for {base_structure} applications."
        )
        
        prompt = (
            f"Generate a {base_structure} project structure for the product with these specifications:\n\n"
            f"Framework: {framework}\n\n"
            f"Components: {json.dumps(list(components.keys()))}\n\n"
            f"Pages: {json.dumps(list(pages.keys()))}\n\n"
            f"State Management Library: {state_management.get('library', {}).get('name', '')}\n\n"
            f"API Client Library: {api_integration.get('client', {}).get('library', '')}\n\n"
            f"The project structure should include:\n"
            f"1. Directory organization\n"
            f"2. File naming conventions\n"
            f"3. Code organization principles\n"
            f"4. Configuration files\n"
            f"5. Key implementation files\n\n"
            f"Provide a comprehensive file tree and explain the purpose of each directory and key file."
        )
        
        # Use standard completion for a more readable file tree
        result = generate_completion(prompt, system_message)
        
        # Process the result to extract the file tree
        file_tree = {}
        
        try:
            # Try to find a file tree section in the result
            tree_section = None
            
            if "```" in result:
                # Extract code blocks
                code_blocks = result.split("```")
                for i in range(1, len(code_blocks), 2):
                    if "tree" in code_blocks[i-1].lower() or "structure" in code_blocks[i-1].lower():
                        tree_section = code_blocks[i]
                        break
            
            if tree_section:
                # Process the tree section
                lines = tree_section.strip().split('\n')
                current_path = []
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    # Count leading spaces to determine nesting level
                    spaces = len(line) - len(line.lstrip())
                    level = spaces // 2
                    
                    # Adjust the current path
                    if level < len(current_path):
                        current_path = current_path[:level]
                    
                    # Extract the file/directory name
                    name = line.strip()
                    if name.endswith('/'):
                        name = name[:-1]
                    
                    # Add to the file tree
                    current_path = current_path[:level]
                    current_path.append(name)
                    
                    # Build the full path
                    full_path = '/'.join(current_path)
                    file_tree[full_path] = {"type": "directory" if name.endswith('/') else "file"}
            
            # If we couldn't extract a file tree, create a structured representation
            if not file_tree:
                file_tree = {
                    "description": result,
                    "structure": self._create_default_file_structure(base_structure, pages)
                }
        except Exception as e:
            self.log_error(f"Failed to process file tree: {e}")
            file_tree = {
                "description": result,
                "structure": self._create_default_file_structure(base_structure, pages)
            }
        
        return file_tree
    
    def _create_default_file_structure(self, base_structure: str, pages: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a default file structure based on the framework.
        
        Args:
            base_structure (str): The base framework structure
            pages (Dict[str, Any]): The page implementation details
            
        Returns:
            Dict[str, Any]: Default file structure
        """
        if base_structure == "Next.js":
            structure = {
                "src": {
                    "app": {
                        "layout.js": {"description": "Root layout component"},
                        "page.js": {"description": "Homepage component"}
                    },
                    "components": {
                        "ui": {"description": "UI components directory"},
                        "layout": {"description": "Layout components directory"},
                        "features": {"description": "Feature-specific components directory"}
                    },
                    "lib": {
                        "api.js": {"description": "API client"},
                        "utils.js": {"description": "Utility functions"}
                    },
                    "hooks": {"description": "Custom hooks directory"},
                    "styles": {"description": "CSS/styling directory"}
                },
                "public": {"description": "Static assets directory"},
                "next.config.js": {"description": "Next.js configuration"},
                ".env.local": {"description": "Environment variables"}
            }
            
            # Add page routes
            for name, page in pages.items():
                path = page.get("path", "").strip("/")
                structure["src"]["app"][path] = {
                    "page.js": {"description": f"{name} page component"}
                }
                
            return structure
        elif base_structure == "React":
            structure = {
                "src": {
                    "components": {
                        "ui": {"description": "UI components directory"},
                        "layout": {"description": "Layout components directory"},
                        "features": {"description": "Feature-specific components directory"}
                    },
                    "pages": {},
                    "services": {
                        "api.js": {"description": "API client"},
                        "auth.js": {"description": "Authentication service"}
                    },
                    "store": {"description": "State management directory"},
                    "hooks": {"description": "Custom hooks directory"},
                    "utils": {"description": "Utility functions directory"},
                    "styles": {"description": "CSS/styling directory"},
                    "App.js": {"description": "Root App component"},
                    "index.js": {"description": "Application entry point"}
                },
                "public": {"description": "Static assets directory"},
                ".env": {"description": "Environment variables"}
            }
            
            # Add pages
            for name, page in pages.items():
                file_name = name.replace(" ", "") + ".js"
                structure["src"]["pages"][file_name] = {"description": f"{name} page component"}
                
            return structure
        else:
            # Generic structure
            structure = {
                "src": {
                    "components": {"description": "Components directory"},
                    "pages": {"description": "Pages directory"},
                    "services": {"description": "Services directory"},
                    "utils": {"description": "Utility functions directory"},
                    "styles": {"description": "CSS/styling directory"},
                    "main.js": {"description": "Application entry point"}
                },
                "public": {"description": "Static assets directory"},
                ".env": {"description": "Environment variables"}
            }
            
            # Add pages
            for name, page in pages.items():
                file_name = name.replace(" ", "") + ".js"
                structure["src"]["pages"][file_name] = {"description": f"{name} page component"}
                
            return structure
