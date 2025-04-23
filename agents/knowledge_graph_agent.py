"""
Knowledge Graph Agent for enhancing SaaS product analysis and recommendations.
"""
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.knowledge_graph import create_knowledge_graph, SaaSKnowledgeGraph
from utils.openai_utils import generate_json_completion


class KnowledgeGraphAgent(BaseAgent):
    """
    Agent for maintaining and querying a knowledge graph of SaaS products.
    This agent enhances the system's ability to analyze relationships between
    products, features, and market trends.
    """
    
    def __init__(self):
        """Initialize the Knowledge Graph Agent."""
        super().__init__(
            name="Knowledge Graph Agent",
            description="Manages and analyzes SaaS product knowledge graph"
        )
        # Initialize the knowledge graph
        self.knowledge_graph = create_knowledge_graph()
        
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the knowledge graph process to analyze and enhance product recommendations.
        
        Args:
            input_data (Dict[str, Any]): Input data containing products and analysis requirements
                
        Returns:
            Dict[str, Any]: Enhanced analysis and recommendations based on knowledge graph
        """
        self.log_info("Starting knowledge graph analysis process")
        
        operation = input_data.get("operation", "analyze")
        
        if operation == "add_product":
            product_data = input_data.get("product_data", {})
            return await self._add_product_to_graph(product_data)
        
        elif operation == "add_multiple_products":
            products_data = input_data.get("products_data", [])
            return await self._add_multiple_products(products_data)
        
        elif operation == "analyze_product":
            product_name = input_data.get("product_name", "")
            return await self._analyze_product(product_name)
        
        elif operation == "find_enhancement_opportunities":
            product_name = input_data.get("product_name", "")
            return await self._find_enhancement_opportunities(product_name)
        
        elif operation == "visualize":
            return await self._visualize_graph()
        
        elif operation == "market_analysis":
            category = input_data.get("category", None)
            return await self._analyze_market(category)
        
        else:
            self.log_error(f"Unknown operation: {operation}")
            return {"error": f"Unknown operation: {operation}"}
    
    async def _add_product_to_graph(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a product to the knowledge graph.
        
        Args:
            product_data (Dict[str, Any]): Data about the product to add
            
        Returns:
            Dict[str, Any]: Status of the operation
        """
        try:
            product_name = self.knowledge_graph.add_product(product_data)
            self.log_info(f"Added product to knowledge graph: {product_name}")
            return {
                "status": "success",
                "product_name": product_name,
                "message": f"Successfully added {product_name} to the knowledge graph"
            }
        except Exception as e:
            self.log_error(f"Error adding product to knowledge graph: {e}")
            return {
                "status": "error",
                "message": f"Failed to add product to knowledge graph: {str(e)}"
            }
    
    async def _add_multiple_products(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add multiple products to the knowledge graph.
        
        Args:
            products_data (List[Dict[str, Any]]): List of product data dictionaries
            
        Returns:
            Dict[str, Any]: Status of the operation
        """
        try:
            added_ids = self.knowledge_graph.bulk_add_products(products_data)
            self.log_info(f"Added {len(added_ids)} products to knowledge graph")
            return {
                "status": "success",
                "added_count": len(added_ids),
                "added_products": added_ids,
                "message": f"Successfully added {len(added_ids)} products to the knowledge graph"
            }
        except Exception as e:
            self.log_error(f"Error adding multiple products to knowledge graph: {e}")
            return {
                "status": "error",
                "message": f"Failed to add products to knowledge graph: {str(e)}"
            }
    
    async def _analyze_product(self, product_name: str) -> Dict[str, Any]:
        """
        Analyze a product using the knowledge graph.
        
        Args:
            product_name (str): Name of the product to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        if not product_name:
            return {"error": "Product name is required"}
        
        try:
            # Get product features
            features = self.knowledge_graph.get_product_features(product_name)
            
            # Get competitors
            competitors = self.knowledge_graph.get_competitive_products(product_name)
            
            # Find missing features compared to competitors
            missing_features = self.knowledge_graph.find_missing_features(product_name)
            
            # Find similar products
            similar_products = self.knowledge_graph.find_similar_products(product_name)
            
            self.log_info(f"Completed knowledge graph analysis for {product_name}")
            
            return {
                "product_name": product_name,
                "features": features,
                "competitors": competitors,
                "missing_features": missing_features,
                "similar_products": similar_products
            }
        except Exception as e:
            self.log_error(f"Error analyzing product {product_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze product {product_name}: {str(e)}"
            }
    
    async def _find_enhancement_opportunities(self, product_name: str) -> Dict[str, Any]:
        """
        Find enhancement opportunities for a product using the knowledge graph.
        
        Args:
            product_name (str): Name of the product
            
        Returns:
            Dict[str, Any]: Enhancement opportunities
        """
        if not product_name:
            return {"error": "Product name is required"}
        
        try:
            # Get basic product analysis
            analysis = await self._analyze_product(product_name)
            
            if "status" in analysis and analysis["status"] == "error":
                return analysis
            
            # Prepare data for AI enhancement
            features = analysis.get("features", [])
            missing_features = analysis.get("missing_features", {})
            competitors = analysis.get("competitors", [])
            
            # Flatten missing features for easier processing
            all_missing_features = []
            for competitor, features_list in missing_features.items():
                all_missing_features.extend(features_list)
            
            # Remove duplicates
            all_missing_features = list(set(all_missing_features))
            
            # Find popular features across similar products
            popular_features = self.knowledge_graph.find_popular_features()
            popular_feature_names = [f for f, _ in popular_features]
            
            # Combine all data for AI analysis
            enhancement_data = {
                "product_name": product_name,
                "current_features": features,
                "missing_features": all_missing_features,
                "popular_features": popular_feature_names,
                "competitor_count": len(competitors)
            }
            
            # Use AI to generate enhancement recommendations
            opportunities = await self._generate_enhancement_recommendations(enhancement_data)
            
            self.log_info(f"Generated enhancement opportunities for {product_name}")
            
            return {
                "product_name": product_name,
                "enhancement_opportunities": opportunities,
                "knowledge_graph_analysis": analysis
            }
        except Exception as e:
            self.log_error(f"Error finding enhancement opportunities for {product_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to find enhancement opportunities for {product_name}: {str(e)}"
            }
    
    async def _generate_enhancement_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate enhancement recommendations using AI.
        
        Args:
            data (Dict[str, Any]): Data about the product and its features
            
        Returns:
            Dict[str, Any]: Enhancement recommendations
        """
        try:
            product_name = data.get("product_name", "")
            current_features = data.get("current_features", [])
            missing_features = data.get("missing_features", [])
            popular_features = data.get("popular_features", [])
            
            # Prepare the prompt for the AI
            system_message = (
                "You are a SaaS product expert who specializes in identifying enhancement opportunities "
                "based on market analysis and competitor research. Given information about a product, "
                "its current features, and features it's missing compared to competitors, recommend "
                "specific enhancements that would make the product more competitive and innovative."
            )
            
            prompt = (
                f"Product: {product_name}\n\n"
                f"Current Features:\n"
                + "\n".join([f"- {feature}" for feature in current_features])
                + "\n\n"
                f"Features Missing Compared to Competitors:\n"
                + "\n".join([f"- {feature}" for feature in missing_features])
                + "\n\n"
                f"Popular Features in Similar Products:\n"
                + "\n".join([f"- {feature}" for feature in popular_features])
                + "\n\n"
                "Based on this analysis from our knowledge graph, provide enhancement recommendations in the following categories:\n"
                "1. Must-Have Features - Essential features the product should implement to remain competitive\n"
                "2. Innovative Differentiators - Unique features that could set this product apart from competitors\n"
                "3. User Experience Improvements - Enhancements to make the product more user-friendly\n"
                "4. Technical Enhancements - Backend or architectural improvements\n"
                "5. Integration Opportunities - Potential integrations with other services\n\n"
                "Provide your recommendations in a structured JSON format with these categories as keys, "
                "and a list of specific, actionable recommendations for each category."
            )
            
            # Generate recommendations using the AI
            recommendations_structure = {
                "must_have_features": ["Feature 1", "Feature 2"],
                "innovative_differentiators": ["Differentiator 1", "Differentiator 2"],
                "user_experience_improvements": ["Improvement 1", "Improvement 2"],
                "technical_enhancements": ["Enhancement 1", "Enhancement 2"],
                "integration_opportunities": ["Integration 1", "Integration 2"]
            }
            
            try:
                recommendations = generate_json_completion(prompt, system_message)
                
                # Default recommendations if API fails
                if not recommendations or "error" in recommendations:
                    self.log_warning("AI API failed, using basic recommendations")
                    return self._get_default_recommendations(data)
                
                return recommendations
            except Exception as e:
                self.log_error(f"Error generating AI recommendations: {e}")
                return self._get_default_recommendations(data)
            
        except Exception as e:
            self.log_error(f"Error in enhancement recommendation generation: {e}")
            return {
                "must_have_features": ["Error generating recommendations"],
                "innovative_differentiators": [],
                "user_experience_improvements": [],
                "technical_enhancements": [],
                "integration_opportunities": []
            }
    
    def _get_default_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate default recommendations when AI is unavailable.
        
        Args:
            data (Dict[str, Any]): Data about the product and its features
            
        Returns:
            Dict[str, Any]: Default enhancement recommendations
        """
        product_name = data.get("product_name", "").lower()
        missing_features = data.get("missing_features", [])
        
        # Select the top 3 missing features
        top_missing = missing_features[:3] if len(missing_features) >= 3 else missing_features
        
        # Basic recommendations based on product name keywords
        if "task" in product_name or "project" in product_name or "management" in product_name:
            return {
                "must_have_features": top_missing + ["Advanced filtering and sorting", "Customizable dashboards"],
                "innovative_differentiators": ["AI task prioritization", "Predictive deadline estimation"],
                "user_experience_improvements": ["Simplified task creation flow", "Keyboard shortcuts for common actions"],
                "technical_enhancements": ["Offline mode support", "Faster synchronization between devices"],
                "integration_opportunities": ["Calendar integration", "Email integration for task creation"]
            }
        elif "document" in product_name or "note" in product_name or "wiki" in product_name:
            return {
                "must_have_features": top_missing + ["Real-time collaboration", "Version history"],
                "innovative_differentiators": ["AI-powered content suggestions", "Semantic knowledge graph"],
                "user_experience_improvements": ["Distraction-free writing mode", "Customizable formatting options"],
                "technical_enhancements": ["Faster document loading", "Better conflict resolution"],
                "integration_opportunities": ["Integration with reference management tools", "Export to multiple formats"]
            }
        elif "chat" in product_name or "communication" in product_name or "messaging" in product_name:
            return {
                "must_have_features": top_missing + ["Message threading", "Read receipts"],
                "innovative_differentiators": ["AI message summarization", "Sentiment analysis for team health"],
                "user_experience_improvements": ["Simplified file sharing", "Better notification management"],
                "technical_enhancements": ["End-to-end encryption", "Improved search functionality"],
                "integration_opportunities": ["Integration with project management tools", "Calendar integration for scheduling"]
            }
        elif "analytics" in product_name or "data" in product_name or "metrics" in product_name:
            return {
                "must_have_features": top_missing + ["Custom report builder", "Scheduled reports"],
                "innovative_differentiators": ["AI-powered insight generation", "Anomaly detection"],
                "user_experience_improvements": ["Simplified dashboard creation", "Mobile-optimized views"],
                "technical_enhancements": ["Faster query processing", "Better data compression"],
                "integration_opportunities": ["CRM data integration", "Marketing platform integrations"]
            }
        else:
            # Generic recommendations
            return {
                "must_have_features": top_missing + ["User management", "Customizable dashboard"],
                "innovative_differentiators": ["AI-powered assistance", "Personalized user experience"],
                "user_experience_improvements": ["Simplified onboarding", "Dark mode support"],
                "technical_enhancements": ["Improved performance", "Better mobile responsiveness"],
                "integration_opportunities": ["API for third-party integrations", "Single Sign-On (SSO) support"]
            }
    
    async def _visualize_graph(self) -> Dict[str, Any]:
        """
        Generate a visualization of the knowledge graph.
        
        Returns:
            Dict[str, Any]: Status and path to the visualization
        """
        try:
            output_file = self.knowledge_graph.visualize()
            self.log_info(f"Generated knowledge graph visualization: {output_file}")
            return {
                "status": "success",
                "visualization_path": output_file,
                "message": "Successfully generated knowledge graph visualization"
            }
        except Exception as e:
            self.log_error(f"Error visualizing knowledge graph: {e}")
            return {
                "status": "error",
                "message": f"Failed to visualize knowledge graph: {str(e)}"
            }
    
    async def _analyze_market(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze the market using the knowledge graph.
        
        Args:
            category (Optional[str]): Optional category to focus the analysis on
            
        Returns:
            Dict[str, Any]: Market analysis results
        """
        try:
            # Get products by category
            if category is not None:
                products = self.knowledge_graph.get_products_by_category(category)
                category_name = category
            else:
                # Get all products
                products = []
                for node, attrs in self.knowledge_graph.graph.nodes(data=True):
                    if attrs.get('node_type') == 'Product':
                        products.append({
                            'name': node,
                            **{k: v for k, v in attrs.items() if k != 'name'}
                        })
                category_name = "All Categories"
            
            # Find popular features
            popular_features = self.knowledge_graph.find_popular_features(category=category, limit=15)
            
            # Count products per category if analyzing all categories
            category_distribution = {}
            if not category:
                for cat_node, attrs in self.knowledge_graph.graph.nodes(data=True):
                    if attrs.get('node_type') == 'Category':
                        cat_products = self.knowledge_graph.get_products_by_category(cat_node)
                        if cat_products:
                            category_distribution[cat_node] = len(cat_products)
            
            self.log_info(f"Completed market analysis for {category_name}")
            
            analysis = {
                "category": category_name,
                "product_count": len(products),
                "products": [p.get('name') for p in products],
                "popular_features": popular_features
            }
            
            if category_distribution:
                analysis["category_distribution"] = category_distribution
            
            return analysis
        except Exception as e:
            self.log_error(f"Error in market analysis: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze market: {str(e)}"
            }