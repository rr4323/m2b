"""
Marketing Agent for creating marketing materials and launch strategies.
"""
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion, generate_completion

class MarketingAgent(BaseAgent):
    """Agent for creating marketing materials and launch strategies."""
    
    def __init__(self):
        """Initialize the Marketing Agent."""
        super().__init__(
            name="Marketing Agent",
            description="Creates marketing materials and launch strategies"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the marketing process.
        
        Args:
            input_data (Dict[str, Any]): Input data containing product blueprint and implementation details
                
        Returns:
            Dict[str, Any]: Marketing strategies and materials
        """
        self.log_info("Starting marketing process")
        
        blueprint = input_data.get("blueprint", {})
        
        if not blueprint:
            self.log_error("No product blueprint provided for marketing")
            return {"error": "No product blueprint provided for marketing"}
        
        product_name = blueprint.get("product_name", "")
        
        self.log_info(f"Creating marketing strategy for: {product_name}")
        
        # Step 1: Define target audience and positioning
        positioning = await self._define_positioning(blueprint)
        
        # Step 2: Create product messaging
        messaging = await self._create_messaging(blueprint, positioning)
        
        # Step 3: Create launch strategy
        launch_strategy = await self._create_launch_strategy(blueprint, positioning, messaging)
        
        # Step 4: Create marketing materials
        marketing_materials = await self._create_marketing_materials(blueprint, positioning, messaging)
        
        # Step 5: Define channel strategy
        channel_strategy = await self._define_channel_strategy(blueprint, positioning, launch_strategy)
        
        return {
            "product_name": product_name,
            "positioning": positioning,
            "messaging": messaging,
            "launch_strategy": launch_strategy,
            "marketing_materials": marketing_materials,
            "channel_strategy": channel_strategy
        }
    
    async def _define_positioning(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define the product positioning and target audience.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            
        Returns:
            Dict[str, Any]: Product positioning and target audience
        """
        self.log_info("Defining product positioning and target audience")
        
        product_name = blueprint.get("product_name", "")
        product_description = blueprint.get("description", "")
        target_user = blueprint.get("target_user", "")
        features = blueprint.get("features", {})
        enhancements = blueprint.get("enhancements", [])
        
        system_message = (
            "You are a marketing strategist specializing in SaaS products. "
            "Define clear product positioning and target audience segmentation "
            "for the specified product based on its features, enhancements, and "
            "target users. The positioning should differentiate the product in "
            "the market and resonate with the target audience."
        )
        
        prompt = (
            f"Define positioning and target audience for '{product_name}':\n\n"
            f"Product Description: {product_description}\n\n"
            f"Target User: {target_user}\n\n"
            f"Key Features: {features}\n\n"
            f"Enhancements/Differentiators: {enhancements}\n\n"
            f"The positioning should include:\n"
            f"1. Value proposition\n"
            f"2. Unique selling points\n"
            f"3. Competitive positioning\n"
            f"4. Brand personality\n\n"
            f"The target audience should include:\n"
            f"1. Primary audience segments\n"
            f"2. Audience demographics and psychographics\n"
            f"3. Key pain points addressed\n"
            f"4. Decision-making factors\n\n"
            f"Consider the competitive landscape for this type of SaaS product "
            f"and how to effectively differentiate it."
        )
        
        positioning_structure = {
            "value_proposition": "Value proposition statement",
            "unique_selling_points": ["USP 1", "USP 2", "USP 3"],
            "competitive_positioning": {
                "category": "Product category",
                "alternatives": ["Alternative 1", "Alternative 2"],
                "differentiation": ["Differentiator 1", "Differentiator 2"]
            },
            "brand_personality": {
                "tone": "Brand tone",
                "attributes": ["Attribute 1", "Attribute 2"],
                "voice": "Brand voice description"
            },
            "target_audience": {
                "primary_segments": [
                    {
                        "name": "Segment name",
                        "description": "Segment description",
                        "pain_points": ["Pain point 1", "Pain point 2"],
                        "decision_factors": ["Factor 1", "Factor 2"]
                    }
                ],
                "demographics": {
                    "industries": ["Industry 1", "Industry 2"],
                    "company_size": ["Size 1", "Size 2"],
                    "roles": ["Role 1", "Role 2"]
                },
                "psychographics": {
                    "values": ["Value 1", "Value 2"],
                    "behaviors": ["Behavior 1", "Behavior 2"],
                    "goals": ["Goal 1", "Goal 2"]
                }
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define positioning, using default structure")
            return positioning_structure
        
        return result
    
    async def _create_messaging(
        self, 
        blueprint: Dict[str, Any],
        positioning: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create product messaging framework.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            positioning (Dict[str, Any]): The product positioning
            
        Returns:
            Dict[str, Any]: Product messaging framework
        """
        self.log_info("Creating product messaging framework")
        
        product_name = blueprint.get("product_name", "")
        value_proposition = positioning.get("value_proposition", "")
        unique_selling_points = positioning.get("unique_selling_points", [])
        target_audience = positioning.get("target_audience", {})
        
        system_message = (
            "You are a marketing copywriter specializing in SaaS products. "
            "Create a comprehensive messaging framework for the specified product "
            "based on its positioning and target audience. The messaging should be "
            "compelling, clear, and tailored to the target audience segments."
        )
        
        prompt = (
            f"Create a messaging framework for '{product_name}':\n\n"
            f"Value Proposition: {value_proposition}\n\n"
            f"Unique Selling Points: {unique_selling_points}\n\n"
            f"Target Audience: {target_audience}\n\n"
            f"The messaging framework should include:\n"
            f"1. Tagline/slogan\n"
            f"2. Elevator pitch (5-10 seconds)\n"
            f"3. Key messages for each audience segment\n"
            f"4. Feature-to-benefit mapping\n"
            f"5. Objection handling\n"
            f"6. Social proof frameworks\n\n"
            f"The messaging should be compelling, concise, and focused on "
            f"benefits rather than features. It should clearly communicate "
            f"the value proposition and appeal to the target audience's needs."
        )
        
        messaging_structure = {
            "tagline": "Product tagline",
            "elevator_pitch": "Elevator pitch",
            "key_messages": {
                "general": ["Message 1", "Message 2"],
                "segment_specific": [
                    {
                        "segment": "Segment name",
                        "messages": ["Message 1", "Message 2"]
                    }
                ]
            },
            "feature_benefits": [
                {
                    "feature": "Feature name",
                    "benefit": "Benefit description",
                    "audience": "Target audience for this benefit"
                }
            ],
            "objection_handling": [
                {
                    "objection": "Potential objection",
                    "response": "Response to objection"
                }
            ],
            "social_proof_frameworks": {
                "testimonial_templates": ["Template 1", "Template 2"],
                "case_study_framework": "Case study framework description",
                "success_metrics": ["Metric 1", "Metric 2"]
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to create messaging, using default structure")
            return messaging_structure
        
        return result
    
    async def _create_launch_strategy(
        self, 
        blueprint: Dict[str, Any],
        positioning: Dict[str, Any],
        messaging: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create product launch strategy.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            positioning (Dict[str, Any]): The product positioning
            messaging (Dict[str, Any]): The product messaging
            
        Returns:
            Dict[str, Any]: Product launch strategy
        """
        self.log_info("Creating product launch strategy")
        
        product_name = blueprint.get("product_name", "")
        target_audience = positioning.get("target_audience", {})
        
        system_message = (
            "You are a product marketing manager specializing in SaaS product launches. "
            "Create a comprehensive launch strategy for the specified product based on "
            "its positioning, messaging, and target audience. The strategy should maximize "
            "visibility, acquisition, and initial traction."
        )
        
        prompt = (
            f"Create a launch strategy for '{product_name}':\n\n"
            f"Target Audience: {target_audience}\n\n"
            f"The launch strategy should include:\n"
            f"1. Launch phases and timeline\n"
            f"2. Launch goals and KPIs\n"
            f"3. Pre-launch activities\n"
            f"4. Launch day activities\n"
            f"5. Post-launch activities\n"
            f"6. Marketplace listings (AppSumo, Product Hunt, etc.)\n"
            f"7. Content and PR strategy\n"
            f"8. Community engagement\n\n"
            f"Focus on actionable steps and tactics for a successful launch, "
            f"with particular emphasis on B2B SaaS marketplaces and platforms "
            f"that can provide immediate visibility and traction."
        )
        
        launch_structure = {
            "phases": [
                {
                    "name": "Phase name",
                    "timeline": "Timeline",
                    "activities": ["Activity 1", "Activity 2"],
                    "goals": ["Goal 1", "Goal 2"]
                }
            ],
            "goals": {
                "awareness": ["Goal 1", "Goal 2"],
                "acquisition": ["Goal 1", "Goal 2"],
                "activation": ["Goal 1", "Goal 2"]
            },
            "kpis": ["KPI 1", "KPI 2"],
            "pre_launch": {
                "activities": ["Activity 1", "Activity 2"],
                "timeline": "Timeline description",
                "resources": ["Resource 1", "Resource 2"]
            },
            "launch_day": {
                "activities": ["Activity 1", "Activity 2"],
                "checklist": ["Item 1", "Item 2"],
                "communications": ["Communication 1", "Communication 2"]
            },
            "post_launch": {
                "activities": ["Activity 1", "Activity 2"],
                "timeline": "Timeline description",
                "optimization": ["Optimization 1", "Optimization 2"]
            },
            "marketplace_listings": {
                "product_hunt": {
                    "strategy": "Strategy description",
                    "materials": ["Material 1", "Material 2"],
                    "timing": "Timing description"
                },
                "appsumo": {
                    "strategy": "Strategy description",
                    "materials": ["Material 1", "Material 2"],
                    "pricing": "Pricing strategy"
                },
                "other_marketplaces": ["Marketplace 1", "Marketplace 2"]
            },
            "content_pr": {
                "press_release": "Press release template",
                "content_calendar": ["Item 1", "Item 2"],
                "media_outreach": ["Outlet 1", "Outlet 2"]
            },
            "community": {
                "platforms": ["Platform 1", "Platform 2"],
                "engagement_tactics": ["Tactic 1", "Tactic 2"],
                "ambassador_program": "Program description"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to create launch strategy, using default structure")
            return launch_structure
        
        return result
    
    async def _create_marketing_materials(
        self, 
        blueprint: Dict[str, Any],
        positioning: Dict[str, Any],
        messaging: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create marketing materials.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            positioning (Dict[str, Any]): The product positioning
            messaging (Dict[str, Any]): The product messaging
            
        Returns:
            Dict[str, Any]: Marketing materials
        """
        self.log_info("Creating marketing materials")
        
        product_name = blueprint.get("product_name", "")
        tagline = messaging.get("tagline", "")
        elevator_pitch = messaging.get("elevator_pitch", "")
        
        system_message = (
            "You are a marketing content creator specializing in SaaS products. "
            "Create comprehensive marketing materials for the specified product "
            "based on its positioning and messaging. The materials should be "
            "engaging, professional, and effectively communicate the product's value."
        )
        
        prompt = (
            f"Create marketing materials for '{product_name}':\n\n"
            f"Tagline: {tagline}\n\n"
            f"Elevator Pitch: {elevator_pitch}\n\n"
            f"The marketing materials should include:\n"
            f"1. Landing page content\n"
            f"2. Email marketing templates\n"
            f"3. Social media content\n"
            f"4. Product Hunt listing\n"
            f"5. AppSumo listing\n"
            f"6. Ad copy (Google, LinkedIn, Reddit)\n"
            f"7. Product demo script\n\n"
            f"The materials should be compelling, concise, and focused on "
            f"communicating the product's value proposition and benefits."
        )
        
        materials_structure = {
            "landing_page": {
                "hero_section": {
                    "headline": "Hero headline",
                    "subheadline": "Hero subheadline",
                    "cta": "Call to action text"
                },
                "features_section": [
                    {
                        "title": "Feature title",
                        "description": "Feature description",
                        "benefit": "Feature benefit"
                    }
                ],
                "social_proof": {
                    "testimonials": ["Testimonial 1", "Testimonial 2"],
                    "logos": ["Company 1", "Company 2"]
                },
                "pricing_section": {
                    "plans": ["Plan 1", "Plan 2"],
                    "cta": "Pricing CTA"
                },
                "faq_section": [
                    {
                        "question": "FAQ question",
                        "answer": "FAQ answer"
                    }
                ]
            },
            "email_templates": {
                "welcome": {
                    "subject": "Email subject",
                    "body": "Email body",
                    "cta": "Email CTA"
                },
                "onboarding": [
                    {
                        "subject": "Email subject",
                        "body": "Email body",
                        "cta": "Email CTA"
                    }
                ],
                "feature_announcement": {
                    "subject": "Email subject",
                    "body": "Email body",
                    "cta": "Email CTA"
                }
            },
            "social_media": {
                "announcement_posts": ["Post 1", "Post 2"],
                "value_prop_posts": ["Post 1", "Post 2"],
                "feature_highlight_posts": ["Post 1", "Post 2"]
            },
            "product_hunt": {
                "tagline": "Product Hunt tagline",
                "description": "Product Hunt description",
                "first_comment": "First comment text",
                "maker_comments": ["Comment 1", "Comment 2"]
            },
            "appsumo": {
                "headline": "AppSumo headline",
                "description": "AppSumo description",
                "key_features": ["Feature 1", "Feature 2"],
                "deal_terms": ["Term 1", "Term 2"]
            },
            "ad_copy": {
                "google": [
                    {
                        "headline": "Ad headline",
                        "description": "Ad description",
                        "cta": "Ad CTA"
                    }
                ],
                "linkedin": [
                    {
                        "headline": "Ad headline",
                        "body": "Ad body",
                        "cta": "Ad CTA"
                    }
                ],
                "reddit": [
                    {
                        "title": "Ad title",
                        "body": "Ad body",
                        "cta": "Ad CTA"
                    }
                ]
            },
            "demo_script": {
                "intro": "Demo introduction",
                "key_features": ["Feature demo 1", "Feature demo 2"],
                "use_cases": ["Use case demo 1", "Use case demo 2"],
                "closing": "Demo closing"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to create marketing materials, using default structure")
            return materials_structure
        
        return result
    
    async def _define_channel_strategy(
        self, 
        blueprint: Dict[str, Any],
        positioning: Dict[str, Any],
        launch_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define channel strategy for marketing and distribution.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            positioning (Dict[str, Any]): The product positioning
            launch_strategy (Dict[str, Any]): The launch strategy
            
        Returns:
            Dict[str, Any]: Channel strategy
        """
        self.log_info("Defining channel strategy")
        
        product_name = blueprint.get("product_name", "")
        target_audience = positioning.get("target_audience", {})
        
        system_message = (
            "You are a marketing strategist specializing in channel strategy for "
            "SaaS products. Define a comprehensive channel strategy for the specified "
            "product based on its positioning, target audience, and launch strategy. "
            "The strategy should effectively reach and convert the target audience."
        )
        
        prompt = (
            f"Define a channel strategy for '{product_name}':\n\n"
            f"Target Audience: {target_audience}\n\n"
            f"The channel strategy should include:\n"
            f"1. Primary and secondary marketing channels\n"
            f"2. Channel-specific tactics and content\n"
            f"3. Budget allocation across channels\n"
            f"4. Channel performance metrics and KPIs\n"
            f"5. Channel optimization approach\n"
            f"6. Distribution partnerships and integrations\n\n"
            f"Focus on both paid and organic channels that are most effective "
            f"for reaching and converting B2B SaaS customers. Consider marketplace "
            f"distribution as a key channel."
        )
        
        channel_structure = {
            "primary_channels": [
                {
                    "name": "Channel name",
                    "description": "Channel description",
                    "target_segments": ["Segment 1", "Segment 2"],
                    "tactics": ["Tactic 1", "Tactic 2"],
                    "content_types": ["Content type 1", "Content type 2"],
                    "budget_allocation": "Budget allocation percentage",
                    "kpis": ["KPI 1", "KPI 2"]
                }
            ],
            "secondary_channels": [
                {
                    "name": "Channel name",
                    "description": "Channel description",
                    "target_segments": ["Segment 1", "Segment 2"],
                    "tactics": ["Tactic 1", "Tactic 2"],
                    "content_types": ["Content type 1", "Content type 2"],
                    "budget_allocation": "Budget allocation percentage",
                    "kpis": ["KPI 1", "KPI 2"]
                }
            ],
            "marketplace_distribution": {
                "platforms": ["Platform 1", "Platform 2"],
                "strategy": "Marketplace strategy description",
                "optimization": "Optimization approach"
            },
            "partnerships": {
                "types": ["Partnership type 1", "Partnership type 2"],
                "targets": ["Target 1", "Target 2"],
                "approach": "Partnership approach description"
            },
            "integrations": {
                "platforms": ["Platform 1", "Platform 2"],
                "benefits": ["Benefit 1", "Benefit 2"],
                "approach": "Integration approach description"
            },
            "channel_optimization": {
                "testing_approach": "Testing approach description",
                "measurement_framework": "Measurement framework description",
                "iteration_process": "Iteration process description"
            },
            "budget": {
                "total": "Total budget description",
                "allocation": {
                    "channel1": "Allocation percentage",
                    "channel2": "Allocation percentage"
                },
                "optimization": "Budget optimization approach"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define channel strategy, using default structure")
            return channel_structure
        
        return result
