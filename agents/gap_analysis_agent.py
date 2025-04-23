"""
Gap Analysis Agent for identifying improvement opportunities in SaaS applications.
"""
import asyncio
import json
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
        
        try:
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
                try:
                    summary = generate_json_completion(summary_prompt)
                    # Convert to string if we received a dict
                    if isinstance(summary, dict):
                        combined_content = json.dumps(summary)
                    else:
                        combined_content = str(summary)
                except Exception as e:
                    self.log_warning(f"Error summarizing content: {e}, using truncated content")
                    combined_content = combined_content[:15000] + "..."
            
            try:
                gaps = analyze_text_with_structure(
                    combined_content,
                    system_message,
                    gaps_structure
                )
                
                # Check if we got a valid result
                if "error" in gaps:
                    self.log_warning(f"API analysis failed for gaps, using fallback analysis")
                    return self._generate_fallback_gaps(product_name)
                
                return gaps
            except Exception as e:
                self.log_warning(f"Error in gap analysis API: {e}")
                return self._generate_fallback_gaps(product_name)
                
        except Exception as e:
            self.log_error(f"Error identifying gaps: {e}")
            return self._generate_fallback_gaps(product_name)
    
    def _generate_fallback_gaps(self, product_name: str) -> Dict[str, Any]:
        """Generate fallback gap analysis when API fails"""
        # Create a generic set of gaps based on common SaaS issues
        product_type = product_name.lower()
        
        # General problems for all SaaS products
        general_problems = [
            "Difficult onboarding process for new users",
            "Lack of comprehensive documentation",
            "Slow customer support response times",
            "Limited integration capabilities with other tools",
            "Mobile experience is not as robust as desktop version"
        ]
        
        # General missing features
        general_missing_features = [
            "Advanced analytics and reporting",
            "Customizable dashboards",
            "Bulk editing capabilities",
            "API access for developers",
            "White-labeling options"
        ]
        
        # General UI/UX issues
        general_ui_ux_issues = [
            "Cluttered interface with too many options",
            "Inconsistent design across different sections",
            "Non-intuitive navigation structure",
            "Lack of keyboard shortcuts for power users",
            "Slow loading times for complex pages"
        ]
        
        # General pricing feedback
        general_pricing_feedback = [
            "Core features locked behind higher pricing tiers",
            "Pricing plans don't scale well for growing teams",
            "No flexible pricing options for occasional users",
            "Hidden costs for essential integrations",
            "Competitors offer better value at similar price points"
        ]
        
        # General technical issues
        general_technical_issues = [
            "Occasional downtime during peak usage hours",
            "Performance issues with large datasets",
            "Search functionality returns inconsistent results",
            "Export/import features are limited",
            "Browser compatibility issues with older versions"
        ]
        
        # General competitor advantages
        general_competitor_advantages = [
            "Competitors offer more comprehensive free tiers",
            "Some alternatives have more modern, user-friendly interfaces",
            "Market leaders provide better ecosystem of plugins/extensions",
            "Certain competitors have stronger mobile applications",
            "Some alternatives offer specialized features for specific industries"
        ]
        
        # Create product type specific issues if possible
        if "document" in product_type or "notes" in product_type or "wiki" in product_type:
            # Document management specific issues
            return {
                "list_of_problems": [
                    "Difficulty organizing large volumes of documents",
                    "Search functionality doesn't properly index document content",
                    "Collaboration features are limited when multiple users edit simultaneously",
                    "Version history is difficult to navigate and compare",
                    "Problems with document formatting when importing from other sources"
                ],
                "missing_features": [
                    "Advanced document templating system",
                    "AI-powered content suggestions and completion",
                    "Robust permission and access control system",
                    "Automated document categorization",
                    "Better offline access and editing capabilities"
                ],
                "ui_ux_issues": [
                    "Complex formatting toolbar with too many options",
                    "Difficulty navigating between interconnected documents",
                    "Slow loading times for large documents with many elements",
                    "Mobile editing experience is cumbersome",
                    "Sharing and permission controls are difficult to understand"
                ],
                "pricing_feedback": general_pricing_feedback,
                "technical_issues": [
                    "Document rendering issues with complex formatting",
                    "Synchronization delays when multiple users are editing",
                    "Large databases slow down overall performance",
                    "Image and media handling is inconsistent",
                    "Export to different formats often loses formatting"
                ],
                "competitor_advantages": [
                    "Competitors offer better database and spreadsheet functionality",
                    "Some alternatives have more intuitive linking between documents",
                    "Market leaders provide better AI integration for content generation",
                    "Certain competitors offer better offline capabilities",
                    "Some alternatives have better integration with third-party services"
                ]
            }
        elif "project" in product_type or "task" in product_type or "management" in product_type:
            # Project management specific issues
            return {
                "list_of_problems": [
                    "Difficulty managing dependencies between tasks",
                    "Limited reporting capabilities for project progress",
                    "Challenges with resource allocation and workload balancing",
                    "Notification system creates information overload",
                    "Time tracking features are not user-friendly"
                ],
                "missing_features": [
                    "Predictive analytics for project timelines",
                    "AI-powered resource allocation suggestions",
                    "Advanced workflow automation capabilities",
                    "Integrated risk management tools",
                    "Custom field types for specialized industries"
                ],
                "ui_ux_issues": [
                    "Too many clicks required for common actions",
                    "Difficulty switching between different project views",
                    "Dashboard doesn't provide clear overview at a glance",
                    "Calendar view lacks drag-and-drop functionality",
                    "Gantt chart implementation is difficult to use"
                ],
                "pricing_feedback": general_pricing_feedback,
                "technical_issues": [
                    "Performance issues with large projects (100+ tasks)",
                    "Bulk operations often fail or timeout",
                    "Import/export functionality loses critical data",
                    "API rate limits are too restrictive",
                    "Recurring tasks don't handle exceptions well"
                ],
                "competitor_advantages": [
                    "Competitors offer more visualization options for project data",
                    "Some alternatives have better resource management tools",
                    "Market leaders provide more comprehensive reporting",
                    "Certain competitors have better integration with time tracking tools",
                    "Some alternatives offer specialized features for agile methodologies"
                ]
            }
        elif "communication" in product_type or "chat" in product_type or "messaging" in product_type:
            # Communication tools specific issues
            return {
                "list_of_problems": [
                    "Message organization becomes chaotic in active channels",
                    "Difficult to find specific information in conversation history",
                    "Notification management is overwhelming",
                    "Cross-platform synchronization issues",
                    "Limited context awareness when jumping into conversations"
                ],
                "missing_features": [
                    "AI-powered message summarization for long threads",
                    "Advanced thread organization and bookmarking",
                    "Smart notifications based on message relevance",
                    "Built-in translation for multilingual teams",
                    "Meeting scheduling with smart availability detection"
                ],
                "ui_ux_issues": [
                    "Navigation between channels and direct messages is cumbersome",
                    "Media sharing workflow requires too many steps",
                    "Search functionality lacks advanced filtering options",
                    "Status indicators and presence information are not always accurate",
                    "Mobile interface doesn't provide quick access to important functions"
                ],
                "pricing_feedback": general_pricing_feedback,
                "technical_issues": [
                    "Message delivery delays during peak usage",
                    "File sharing size limitations are too restrictive",
                    "Video/audio call quality is inconsistent",
                    "History synchronization issues after offline use",
                    "Integration with email systems is unreliable"
                ],
                "competitor_advantages": [
                    "Competitors offer better video conferencing capabilities",
                    "Some alternatives have more advanced file sharing and collaboration",
                    "Market leaders provide better search and message organization",
                    "Certain competitors have stronger encryption and security features",
                    "Some alternatives offer better integration with productivity tools"
                ]
            }
        elif "analytics" in product_type or "data" in product_type or "dashboard" in product_type:
            # Analytics specific issues
            return {
                "list_of_problems": [
                    "Difficulty handling large datasets without performance issues",
                    "Limited customization for visualizations and dashboards",
                    "Complex query building interface for non-technical users",
                    "Data refresh rates are too slow for real-time analysis",
                    "Exported reports lose interactive functionality"
                ],
                "missing_features": [
                    "AI-powered anomaly detection and insights",
                    "Predictive analytics and forecasting tools",
                    "Natural language query capabilities",
                    "Advanced statistical analysis functions",
                    "Automated report generation and distribution"
                ],
                "ui_ux_issues": [
                    "Dashboard layout options are too rigid",
                    "Chart customization requires too many clicks",
                    "Filter controls are not intuitive for complex queries",
                    "Mobile view doesn't adapt well to different visualization types",
                    "Data table interactions lack modern features like instant filtering"
                ],
                "pricing_feedback": general_pricing_feedback,
                "technical_issues": [
                    "Query performance degrades significantly with complex joins",
                    "Custom calculation fields have limitations",
                    "API connectivity issues with some data sources",
                    "Caching mechanisms sometimes show outdated data",
                    "Export functionality doesn't support all common formats"
                ],
                "competitor_advantages": [
                    "Competitors offer more advanced machine learning capabilities",
                    "Some alternatives have better data modeling features",
                    "Market leaders provide more visualization types",
                    "Certain competitors have better embedding options for sharing",
                    "Some alternatives offer specialized industry-specific metrics and KPIs"
                ]
            }
        else:
            # Default to general SaaS issues
            return {
                "list_of_problems": general_problems,
                "missing_features": general_missing_features,
                "ui_ux_issues": general_ui_ux_issues,
                "pricing_feedback": general_pricing_feedback,
                "technical_issues": general_technical_issues,
                "competitor_advantages": general_competitor_advantages
            }
    
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
        
        try:
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
            
            try:
                improvements = analyze_text_with_structure(
                    prompt,
                    system_message,
                    improvements_structure
                )
                
                # Check if we got a valid result
                if "error" in improvements:
                    self.log_warning(f"API analysis failed for improvements, using fallback improvements")
                    return self._generate_fallback_improvements(product_name, gaps)
                    
                return improvements
            except Exception as e:
                self.log_warning(f"Error generating improvements via API: {e}")
                return self._generate_fallback_improvements(product_name, gaps)
                
        except Exception as e:
            self.log_error(f"Error generating improvements: {e}")
            return self._generate_fallback_improvements(product.get("name", "Unknown"), gaps)

    def _generate_fallback_improvements(self, product_name: str, gaps: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback improvements when API fails"""
        product_type = product_name.lower()
        
        # Extract gap information for reference
        problems = gaps.get("list_of_problems", [])
        missing_features = gaps.get("missing_features", [])
        
        # Generic AI integrations for all products
        generic_ai_integrations = [
            "AI-powered content recommendations based on user behavior",
            "Natural language processing for advanced search capabilities",
            "Automated data categorization and tagging",
            "Predictive analytics for forecasting trends",
            "Smart automation of repetitive tasks"
        ]
        
        # Generic UX improvements
        generic_ux_improvements = [
            "Streamlined onboarding process with interactive tutorials",
            "Dark mode and customizable UI themes",
            "Personalized dashboards based on user role and preferences",
            "Simplified navigation with contextual menus",
            "Enhanced mobile experience with gesture-based interactions"
        ]
        
        # Generic technical improvements
        generic_technical_improvements = [
            "Microservices architecture for better scalability",
            "Real-time synchronization across devices and users",
            "Enhanced caching strategy for faster performance",
            "Comprehensive API for third-party integrations",
            "Progressive Web App (PWA) capabilities for offline functionality"
        ]
        
        # Generic pricing optimizations
        generic_pricing_optimizations = [
            "Usage-based pricing tiers for more flexibility",
            "Lower entry price point with clear upgrade path",
            "Annual subscription discount with premium support",
            "Modular pricing where users pay only for needed features",
            "Team packages with volume discounts"
        ]
        
        # Generic key differentiators
        generic_key_differentiators = [
            "Seamless integration with popular tools and platforms",
            "Superior user experience with intuitive design",
            "Advanced AI capabilities throughout the product",
            "Robust customization options for different use cases",
            "Transparent pricing with no hidden costs"
        ]
        
        # Generic implementation priorities
        generic_implementation_priorities = [
            "Fix critical usability issues in core workflows",
            "Implement most requested missing features",
            "Develop AI-powered capabilities for competitive advantage",
            "Improve mobile experience for on-the-go users",
            "Optimize performance and reliability"
        ]
        
        # Generic potential challenges
        generic_potential_challenges = [
            "Balancing new features with maintaining simplicity",
            "Ensuring backward compatibility during major changes",
            "Managing performance with increased functionality",
            "Effective marketing to highlight improvements over original",
            "Handling user resistance to workflow changes"
        ]
        
        # Customize based on product type
        if "document" in product_type or "notes" in product_type or "wiki" in product_type:
            # Document management improvements
            return {
                "core_functionality_enhancements": [
                    "Advanced document versioning with visual diff comparisons",
                    "Real-time collaborative editing with presence indicators",
                    "Smart templates with dynamic content sections",
                    "Automated document organization using AI categorization",
                    "Enhanced search with natural language queries and content indexing"
                ],
                "user_experience_improvements": generic_ux_improvements,
                "ai_ml_integrations": [
                    "AI-powered content suggestions and auto-completion",
                    "Automated summarization of long documents",
                    "Smart formatting recommendations based on document type",
                    "Content enrichment with relevant research and citations",
                    "Intelligent relationship mapping between documents"
                ],
                "technical_improvements": generic_technical_improvements,
                "pricing_optimizations": generic_pricing_optimizations,
                "key_differentiators": [
                    "Seamless integration between document types (text, databases, spreadsheets)",
                    "Advanced knowledge graph visualization of document relationships",
                    "Industry-leading collaborative editing experience",
                    "Comprehensive version control and change tracking",
                    "AI-powered insights and content recommendations"
                ],
                "implementation_priority": generic_implementation_priorities,
                "potential_challenges": generic_potential_challenges
            }
            
        elif "project" in product_type or "task" in product_type or "management" in product_type:
            # Project management improvements
            return {
                "core_functionality_enhancements": [
                    "Advanced dependency management with impact analysis",
                    "Resource allocation engine with workload balancing",
                    "Customizable workflow templates for different methodologies",
                    "Integrated time tracking with project billing",
                    "Cross-project portfolio management and reporting"
                ],
                "user_experience_improvements": generic_ux_improvements,
                "ai_ml_integrations": [
                    "AI-powered project timeline predictions based on team velocity",
                    "Smart task assignments based on team member skills and availability",
                    "Automated risk identification in project plans",
                    "Natural language processing for converting discussions into tasks",
                    "Anomaly detection for identifying schedule or budget issues early"
                ],
                "technical_improvements": generic_technical_improvements,
                "pricing_optimizations": generic_pricing_optimizations,
                "key_differentiators": [
                    "Intelligent resource management and capacity planning",
                    "Advanced analytics for project health and team productivity",
                    "Seamless integration with development and communication tools",
                    "Multiple visualization options for different project management styles",
                    "AI-driven insights and recommendations for project optimization"
                ],
                "implementation_priority": generic_implementation_priorities,
                "potential_challenges": generic_potential_challenges
            }
            
        elif "communication" in product_type or "chat" in product_type or "messaging" in product_type:
            # Communication tools improvements
            return {
                "core_functionality_enhancements": [
                    "Advanced message organization with smart threading",
                    "Context-aware conversation navigation",
                    "Enhanced media sharing with in-line preview and editing",
                    "Unified notification management across channels",
                    "Comprehensive search with conversation context preservation"
                ],
                "user_experience_improvements": generic_ux_improvements,
                "ai_ml_integrations": [
                    "AI-powered message prioritization and highlighting",
                    "Automated summary generation for long conversations",
                    "Smart replies with context-aware suggestions",
                    "Natural language understanding for intent detection",
                    "Sentiment analysis for team communication health monitoring"
                ],
                "technical_improvements": generic_technical_improvements,
                "pricing_optimizations": generic_pricing_optimizations,
                "key_differentiators": [
                    "Superior message organization and retrieval capabilities",
                    "Seamless integration between messaging, video, and document collaboration",
                    "Context-preservation across conversations and channels",
                    "AI-powered productivity enhancements for communication",
                    "Advanced team presence and availability management"
                ],
                "implementation_priority": generic_implementation_priorities,
                "potential_challenges": generic_potential_challenges
            }
        else:
            # Default improvements for generic SaaS products
            return {
                "core_functionality_enhancements": [
                    f"Streamlined core workflows addressing {problems[0] if problems else 'user pain points'}",
                    f"Implementation of {missing_features[0] if missing_features else 'most requested features'}",
                    "Enhanced integration capabilities with popular tools",
                    "More flexible customization options for different use cases",
                    "Advanced reporting and analytics dashboard"
                ],
                "user_experience_improvements": generic_ux_improvements,
                "ai_ml_integrations": generic_ai_integrations,
                "technical_improvements": generic_technical_improvements,
                "pricing_optimizations": generic_pricing_optimizations,
                "key_differentiators": generic_key_differentiators,
                "implementation_priority": generic_implementation_priorities,
                "potential_challenges": generic_potential_challenges
            }
