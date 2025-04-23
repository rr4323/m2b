"""
Design Agent for creating UI wireframes and mockups.
"""
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion

class DesignAgent(BaseAgent):
    """Agent for creating UI wireframes and mockups based on product specs."""
    
    def __init__(self):
        """Initialize the Design Agent."""
        super().__init__(
            name="Design Agent",
            description="Creates UI wireframes and mockups based on product specs"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the design process to create UI wireframes and mockups.
        
        Args:
            input_data (Dict[str, Any]): Input data containing product blueprint
                
        Returns:
            Dict[str, Any]: Design specifications and wireframes
        """
        self.log_info("Starting design process")
        
        blueprint = input_data.get("blueprint", {})
        
        if not blueprint:
            self.log_error("No product blueprint provided for design")
            return {"error": "No product blueprint provided for design"}
        
        product_name = blueprint.get("product_name", "")
        
        self.log_info(f"Creating design for: {product_name}")
        
        # Step 1: Define design system
        design_system = await self._define_design_system(blueprint)
        
        # Step 2: Create page specifications
        page_specs = await self._create_page_specs(blueprint, design_system)
        
        # Step 3: Generate wireframe descriptions
        wireframes = await self._generate_wireframe_descriptions(blueprint, page_specs)
        
        # Step 4: Create UI component library
        component_library = await self._create_component_library(design_system)
        
        return {
            "product_name": product_name,
            "design_system": design_system,
            "page_specs": page_specs,
            "wireframes": wireframes,
            "component_library": component_library
        }
    
    async def _define_design_system(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define the design system for the product.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            
        Returns:
            Dict[str, Any]: The design system specification
        """
        self.log_info("Defining design system")
        
        product_name = blueprint.get("product_name", "")
        product_description = blueprint.get("description", "")
        target_user = blueprint.get("target_user", "")
        
        system_message = (
            "You are a UI/UX design expert specializing in SaaS applications. "
            "Define a comprehensive design system for the product that includes "
            "color scheme, typography, spacing, component styles, and design principles. "
            "The design system should be modern, accessible, and consistent with "
            "current design trends for SaaS applications."
        )
        
        prompt = (
            f"Create a design system for '{product_name}', a SaaS product described as: "
            f"'{product_description}'\n\n"
            f"Target users: {target_user}\n\n"
            f"The design system should include:\n"
            f"1. Color palette (primary, secondary, accent, neutral colors)\n"
            f"2. Typography (font families, sizes, weights)\n"
            f"3. Spacing system\n"
            f"4. Component styles (buttons, forms, cards, navigation)\n"
            f"5. Design principles\n"
            f"6. Responsive design guidelines\n"
            f"7. Accessibility considerations\n\n"
            f"The design should be modern, clean, and appropriate for a SaaS application."
        )
        
        design_system_structure = {
            "brand": {
                "name": product_name,
                "tagline": "Tagline",
                "design_principles": ["Principle 1", "Principle 2"]
            },
            "colors": {
                "primary": "#HEXCODE",
                "secondary": "#HEXCODE",
                "accent": "#HEXCODE",
                "success": "#HEXCODE",
                "warning": "#HEXCODE",
                "error": "#HEXCODE",
                "background": "#HEXCODE",
                "surface": "#HEXCODE",
                "text": {
                    "primary": "#HEXCODE",
                    "secondary": "#HEXCODE",
                    "disabled": "#HEXCODE"
                }
            },
            "typography": {
                "font_family": {
                    "primary": "Font name",
                    "secondary": "Font name",
                    "monospace": "Font name"
                },
                "font_sizes": {
                    "xs": "12px",
                    "sm": "14px",
                    "md": "16px",
                    "lg": "18px",
                    "xl": "20px",
                    "2xl": "24px",
                    "3xl": "30px",
                    "4xl": "36px"
                },
                "font_weights": {
                    "regular": "400",
                    "medium": "500",
                    "semibold": "600",
                    "bold": "700"
                },
                "line_heights": {
                    "tight": "1.2",
                    "normal": "1.5",
                    "relaxed": "1.75"
                }
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
                "2xl": "48px",
                "3xl": "64px"
            },
            "borders": {
                "radius": {
                    "sm": "4px",
                    "md": "8px",
                    "lg": "12px",
                    "full": "9999px"
                },
                "width": {
                    "thin": "1px",
                    "medium": "2px",
                    "thick": "4px"
                }
            },
            "shadows": {
                "sm": "0 1px 3px rgba(0,0,0,0.1)",
                "md": "0 4px 6px rgba(0,0,0,0.1)",
                "lg": "0 10px 15px rgba(0,0,0,0.1)"
            },
            "responsive": {
                "breakpoints": {
                    "sm": "640px",
                    "md": "768px",
                    "lg": "1024px",
                    "xl": "1280px"
                }
            },
            "accessibility": {
                "guidelines": ["Guideline 1", "Guideline 2"],
                "contrast_ratios": {
                    "text": "4.5:1 minimum",
                    "large_text": "3:1 minimum"
                }
            }
        }
        
        design_system = generate_json_completion(prompt, system_message)
        
        if not design_system or not isinstance(design_system, dict):
            self.log_error("Failed to generate design system, using default structure")
            return design_system_structure
        
        return design_system
    
    async def _create_page_specs(
        self, 
        blueprint: Dict[str, Any],
        design_system: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create specifications for each page in the application.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            design_system (Dict[str, Any]): The design system
            
        Returns:
            List[Dict[str, Any]]: Page specifications
        """
        self.log_info("Creating page specifications")
        
        product_name = blueprint.get("product_name", "")
        features = blueprint.get("features", {})
        
        # Extract core features to inform page structure
        core_features = features.get("core_features", [])
        new_features = features.get("new_features", [])
        advanced_features = features.get("advanced_features", [])
        
        all_features = core_features + new_features + advanced_features
        
        system_message = (
            "You are a UX architect specializing in SaaS applications. "
            "Create comprehensive page specifications for the product based on "
            "its features. Define the core pages, their purpose, and the key "
            "components and interactions on each page."
        )
        
        prompt = (
            f"Create page specifications for '{product_name}' based on these features:\n\n"
            f"Features:\n{str(all_features)[:2000]}...\n\n"
            f"Define the following for the SaaS application:\n"
            f"1. Common layout elements (header, footer, navigation)\n"
            f"2. Core pages (dashboard, settings, etc.)\n"
            f"3. Feature-specific pages\n"
            f"4. User flows between pages\n\n"
            f"For each page, specify:\n"
            f"- Page name and URL path\n"
            f"- Purpose and description\n"
            f"- Key components and sections\n"
            f"- Main user actions and interactions\n"
            f"- Related pages and navigation"
        )
        
        page_specs_structure = [
            {
                "name": "Dashboard",
                "path": "/dashboard",
                "description": "Main dashboard with overview of key metrics",
                "purpose": "Provide users with a quick overview of their account and activity",
                "sections": [
                    {
                        "name": "Header",
                        "components": ["Logo", "Navigation", "User menu"]
                    },
                    {
                        "name": "Main content",
                        "components": ["Metric cards", "Recent activity", "Quick actions"]
                    }
                ],
                "user_actions": ["View metrics", "Navigate to other pages", "Perform quick actions"],
                "related_pages": ["Settings", "Profile"]
            }
        ]
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, list):
            self.log_error("Failed to generate page specs, using default structure")
            return page_specs_structure
        
        return result
    
    async def _generate_wireframe_descriptions(
        self, 
        blueprint: Dict[str, Any],
        page_specs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate detailed wireframe descriptions for key pages.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            page_specs (List[Dict[str, Any]]): The page specifications
            
        Returns:
            Dict[str, Any]: Wireframe descriptions
        """
        self.log_info("Generating wireframe descriptions")
        
        product_name = blueprint.get("product_name", "")
        
        # Select key pages for wireframes (limit to 5 for efficiency)
        key_pages = page_specs[:5] if len(page_specs) > 5 else page_specs
        
        wireframes = {}
        
        for page in key_pages:
            page_name = page.get("name", "")
            page_description = page.get("description", "")
            page_sections = page.get("sections", [])
            
            self.log_info(f"Generating wireframe for: {page_name}")
            
            system_message = (
                "You are a UI designer specializing in SaaS applications. "
                "Create a detailed wireframe description for the specified page. "
                "The description should be detailed enough that a frontend developer "
                "could implement the page from it, including layout, components, "
                "and responsive behavior."
            )
            
            prompt = (
                f"Create a detailed wireframe description for the {page_name} page of '{product_name}'.\n\n"
                f"Page description: {page_description}\n\n"
                f"Page sections: {str(page_sections)}\n\n"
                f"The wireframe description should include:\n"
                f"1. Layout structure (grid, flexbox, etc.)\n"
                f"2. Component placements and sizes\n"
                f"3. Content organization\n"
                f"4. Responsive behavior\n"
                f"5. Interactive elements\n"
                f"6. States (loading, empty, error)\n\n"
                f"Describe the wireframe in text format with enough detail that a developer "
                f"could implement it accurately."
            )
            
            wireframe_structure = {
                "layout": "Layout description",
                "header": "Header description",
                "content": "Content description",
                "footer": "Footer description",
                "components": [
                    {
                        "name": "Component name",
                        "description": "Component description",
                        "placement": "Component placement",
                        "behavior": "Component behavior"
                    }
                ],
                "responsive": {
                    "desktop": "Desktop behavior",
                    "tablet": "Tablet behavior",
                    "mobile": "Mobile behavior"
                },
                "states": {
                    "loading": "Loading state description",
                    "empty": "Empty state description",
                    "error": "Error state description"
                }
            }
            
            result = generate_json_completion(prompt, system_message)
            
            if result and isinstance(result, dict):
                wireframes[page_name] = result
            else:
                self.log_error(f"Failed to generate wireframe for {page_name}")
                wireframes[page_name] = wireframe_structure
        
        return wireframes
    
    async def _create_component_library(self, design_system: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a UI component library based on the design system.
        
        Args:
            design_system (Dict[str, Any]): The design system
            
        Returns:
            Dict[str, Any]: Component library specifications
        """
        self.log_info("Creating component library")
        
        colors = design_system.get("colors", {})
        typography = design_system.get("typography", {})
        spacing = design_system.get("spacing", {})
        borders = design_system.get("borders", {})
        
        system_message = (
            "You are a UI component designer specializing in SaaS applications. "
            "Create a comprehensive component library based on the provided design "
            "system. The component library should include specifications for all "
            "common UI components used in SaaS applications."
        )
        
        prompt = (
            f"Create a component library based on this design system:\n\n"
            f"Colors: {str(colors)[:500]}...\n\n"
            f"Typography: {str(typography)[:500]}...\n\n"
            f"Spacing: {str(spacing)[:500]}...\n\n"
            f"Borders: {str(borders)[:500]}...\n\n"
            f"The component library should include specifications for:\n"
            f"1. Buttons (primary, secondary, tertiary, icon buttons)\n"
            f"2. Form elements (inputs, selects, checkboxes, radio buttons, toggles)\n"
            f"3. Cards and containers\n"
            f"4. Navigation elements (menus, tabs, breadcrumbs)\n"
            f"5. Feedback elements (alerts, toasts, modals)\n"
            f"6. Data display elements (tables, lists, badges)\n\n"
            f"For each component, specify:\n"
            f"- Appearance (using the design system tokens)\n"
            f"- Variants and states\n"
            f"- Behavior and interactions\n"
            f"- Accessibility considerations"
        )
        
        component_library_structure = {
            "buttons": {
                "primary": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Small", "Large"],
                    "states": ["Default", "Hover", "Active", "Disabled"],
                    "accessibility": "Accessibility considerations"
                },
                "secondary": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Small", "Large"],
                    "states": ["Default", "Hover", "Active", "Disabled"],
                    "accessibility": "Accessibility considerations"
                }
            },
            "form": {
                "input": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "With icon", "With validation"],
                    "states": ["Default", "Focus", "Error", "Disabled"],
                    "accessibility": "Accessibility considerations"
                },
                "select": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Multiple"],
                    "states": ["Default", "Open", "Disabled"],
                    "accessibility": "Accessibility considerations"
                }
            },
            "cards": {
                "default": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Elevated", "Interactive"],
                    "states": ["Default", "Hover", "Active"],
                    "accessibility": "Accessibility considerations"
                }
            },
            "navigation": {
                "menu": {
                    "appearance": "Appearance description",
                    "variants": ["Horizontal", "Vertical", "Dropdown"],
                    "states": ["Default", "Active", "Expanded"],
                    "accessibility": "Accessibility considerations"
                },
                "tabs": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Pills", "Underlined"],
                    "states": ["Default", "Active", "Disabled"],
                    "accessibility": "Accessibility considerations"
                }
            },
            "feedback": {
                "alert": {
                    "appearance": "Appearance description",
                    "variants": ["Info", "Success", "Warning", "Error"],
                    "states": ["Default", "Dismissible"],
                    "accessibility": "Accessibility considerations"
                },
                "modal": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Small", "Large"],
                    "states": ["Open", "Closing"],
                    "accessibility": "Accessibility considerations"
                }
            },
            "data_display": {
                "table": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Compact", "Striped"],
                    "states": ["Default", "Loading", "Empty"],
                    "accessibility": "Accessibility considerations"
                },
                "badge": {
                    "appearance": "Appearance description",
                    "variants": ["Default", "Status", "Counter"],
                    "states": ["Default"],
                    "accessibility": "Accessibility considerations"
                }
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to generate component library, using default structure")
            return component_library_structure
        
        return result
