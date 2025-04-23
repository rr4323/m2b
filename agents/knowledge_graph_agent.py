"""
Knowledge Graph Agent for interacting with the SaaS knowledge graph.
"""
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.knowledge_graph import knowledge_graph
from utils.openai_utils import generate_json_completion, generate_completion

class KnowledgeGraphAgent(BaseAgent):
    """Agent for interacting with the SaaS knowledge graph."""
    
    def __init__(self):
        """Initialize the Knowledge Graph Agent."""
        super().__init__(
            name="Knowledge Graph Agent",
            description="Interacts with the SaaS knowledge graph"
        )
        self.kg = knowledge_graph
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the knowledge graph process.
        
        Args:
            input_data (Dict[str, Any]): Input data for the knowledge graph process
                
        Returns:
            Dict[str, Any]: The results of the knowledge graph process
        """
        self.log_info("Starting knowledge graph process")
        
        # Extract the operation to perform
        operation = input_data.get("operation", "")
        
        if operation == "build_graph":
            # Extract product data
            products = input_data.get("products", [])
            gaps = input_data.get("gaps", [])
            
            # Process products and gaps to build the graph
            result = await self._build_knowledge_graph(products, gaps)
            
        elif operation == "query_similar_products":
            # Find similar products
            product_id = input_data.get("product_id", "")
            result = await self._find_similar_products(product_id)
            
        elif operation == "identify_gaps":
            # Identify gaps in products
            result = await self._identify_potential_gaps(input_data.get("min_products", 2))
            
        elif operation == "analyze_product":
            # Analyze a product in detail
            product_id = input_data.get("product_id", "")
            result = await self._analyze_product(product_id)
            
        elif operation == "visualize":
            # Visualize the knowledge graph
            result = {"visualization_path": self.kg.visualize()}
            
        elif operation == "export":
            # Export the knowledge graph
            result = {"graph_data": self.kg.export_to_json()}
            
        else:
            self.log_warning(f"Unknown operation: {operation}")
            result = {"error": f"Unknown operation: {operation}"}
        
        self.log_info("Completed knowledge graph process")
        return result
    
    async def _build_knowledge_graph(self, products: List[Dict[str, Any]], 
                                    gaps: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Build a knowledge graph from products and gaps.
        
        Args:
            products: List of product data dictionaries
            gaps: Optional list of gap data dictionaries
                
        Returns:
            Dict[str, Any]: Information about the built knowledge graph
        """
        # Add all products to the graph
        product_ids = []
        for product in products:
            product_id = self.kg.add_product(product)
            product_ids.append(product_id)
        
        # Add all gaps to the graph
        gap_ids = []
        if gaps:
            for gap in gaps:
                # For each gap, determine which products it might be related to
                related_products = []
                if "product_name" in gap:
                    # If the gap specifies a product name, find the corresponding product
                    product_name = gap["product_name"].lower().replace(" ", "_")
                    for product_id in product_ids:
                        if product_name in product_id:
                            related_products.append(product_id)
                
                gap_id = self.kg.add_gap(gap, related_products)
                gap_ids.append(gap_id)
        
        # Add additional relationships based on similarities
        for i, product_id1 in enumerate(product_ids):
            for product_id2 in product_ids[i+1:]:
                # Find common features
                product1_features = set(neighbor for neighbor in self.kg.graph.neighbors(product_id1)
                                       if neighbor in self.kg.feature_nodes)
                product2_features = set(neighbor for neighbor in self.kg.graph.neighbors(product_id2)
                                      if neighbor in self.kg.feature_nodes)
                
                common_features = product1_features.intersection(product2_features)
                if common_features:
                    similarity = len(common_features) / len(product1_features.union(product2_features))
                    if similarity > 0.3:  # Only add relationship if similarity is significant
                        self.kg.add_relationship(
                            product_id1, 
                            product_id2, 
                            "similar_to", 
                            {"similarity": similarity, "common_features": len(common_features)}
                        )
        
        # Visualize the knowledge graph
        visualization_path = self.kg.visualize()
        
        return {
            "num_products": len(product_ids),
            "num_gaps": len(gap_ids),
            "num_features": len(self.kg.feature_nodes),
            "num_relationships": len(self.kg.graph.edges),
            "visualization_path": visualization_path
        }
    
    async def _find_similar_products(self, product_id: str) -> Dict[str, Any]:
        """
        Find products similar to the given product.
        
        Args:
            product_id: The ID of the product to find similar products for
                
        Returns:
            Dict[str, Any]: Information about similar products
        """
        if not product_id.startswith("product:"):
            product_id = f"product:{product_id.lower().replace(' ', '_')}"
        
        if product_id not in self.kg.product_nodes:
            return {"error": f"Product '{product_id}' not found in knowledge graph"}
        
        similar_products = self.kg.find_similar_products(product_id)
        
        # Extract product details
        product_details = []
        for prod_id, similarity in similar_products:
            product_data = self.kg.graph.nodes[prod_id]
            product_details.append({
                "id": prod_id,
                "name": product_data.get("name", prod_id),
                "similarity": similarity,
                "description": product_data.get("description", ""),
                "url": product_data.get("url", "")
            })
        
        return {
            "product_id": product_id,
            "product_name": self.kg.graph.nodes[product_id].get("name", product_id),
            "similar_products": product_details
        }
    
    async def _identify_potential_gaps(self, min_products: int = 2) -> Dict[str, Any]:
        """
        Identify potential gaps in products.
        
        Args:
            min_products: Minimum number of products that must have a feature for it to be considered common
                
        Returns:
            Dict[str, Any]: Information about potential gaps
        """
        opportunities = self.kg.find_feature_gap_opportunities(min_products)
        
        # Format the opportunities
        gap_opportunities = []
        for feature_id, missing_products in opportunities:
            feature_name = self.kg.graph.nodes[feature_id].get("name", feature_id)
            
            # Get products that have this feature
            products_with_feature = []
            for neighbor in self.kg.graph.neighbors(feature_id):
                if neighbor in self.kg.product_nodes:
                    product_name = self.kg.graph.nodes[neighbor].get("name", neighbor)
                    products_with_feature.append({"id": neighbor, "name": product_name})
            
            # Get products that don't have this feature
            products_without_feature = []
            for product_id in missing_products:
                product_name = self.kg.graph.nodes[product_id].get("name", product_id)
                products_without_feature.append({"id": product_id, "name": product_name})
            
            gap_opportunities.append({
                "feature_id": feature_id,
                "feature_name": feature_name,
                "products_with_feature": products_with_feature,
                "products_without_feature": products_without_feature,
                "opportunity_strength": len(products_with_feature) / (len(products_with_feature) + len(products_without_feature))
            })
        
        # Sort by opportunity strength
        gap_opportunities.sort(key=lambda x: x["opportunity_strength"], reverse=True)
        
        return {
            "gap_opportunities": gap_opportunities,
            "num_opportunities": len(gap_opportunities)
        }
    
    async def _analyze_product(self, product_id: str) -> Dict[str, Any]:
        """
        Analyze a product in detail using the knowledge graph.
        
        Args:
            product_id: The ID of the product to analyze
                
        Returns:
            Dict[str, Any]: Detailed analysis of the product
        """
        if not product_id.startswith("product:"):
            product_id = f"product:{product_id.lower().replace(' ', '_')}"
        
        if product_id not in self.kg.product_nodes:
            return {"error": f"Product '{product_id}' not found in knowledge graph"}
        
        # Get product details
        product_data = self.kg.graph.nodes[product_id]
        product_name = product_data.get("name", product_id)
        
        # Get product features
        features = []
        for neighbor in self.kg.graph.neighbors(product_id):
            if neighbor in self.kg.feature_nodes:
                feature_name = self.kg.graph.nodes[neighbor].get("name", neighbor)
                
                # Find how many other products have this feature
                products_with_feature = [p for p in self.kg.graph.neighbors(neighbor) 
                                        if p in self.kg.product_nodes and p != product_id]
                
                features.append({
                    "id": neighbor,
                    "name": feature_name,
                    "uniqueness": 1.0 - (len(products_with_feature) / len(self.kg.product_nodes) if self.kg.product_nodes else 0)
                })
        
        # Sort features by uniqueness
        features.sort(key=lambda x: x["uniqueness"], reverse=True)
        
        # Get product gaps
        gaps = []
        for gap_id in self.kg.find_gaps_for_product(product_id):
            gap_data = self.kg.graph.nodes[gap_id]
            gaps.append({
                "id": gap_id,
                "name": gap_data.get("name", gap_id),
                "type": gap_data.get("gap_type", "feature"),
                "description": gap_data.get("description", "")
            })
        
        # Get similar products
        similar_products = []
        for neighbor, edge_data in self.kg.graph.edges(product_id, data=True):
            if neighbor in self.kg.product_nodes and edge_data.get("relationship") == "similar_to":
                product_data = self.kg.graph.nodes[neighbor]
                similar_products.append({
                    "id": neighbor,
                    "name": product_data.get("name", neighbor),
                    "similarity": edge_data.get("similarity", 0.0),
                    "common_features": edge_data.get("common_features", 0)
                })
        
        # Sort similar products by similarity
        similar_products.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Get product category
        categories = []
        for neighbor in self.kg.graph.neighbors(product_id):
            if neighbor in self.kg.category_nodes:
                category_name = self.kg.graph.nodes[neighbor].get("name", neighbor)
                categories.append({
                    "id": neighbor,
                    "name": category_name
                })
        
        # Visualize the product's subgraph
        # This would typically involve creating a subgraph of the product and its immediate neighbors
        # and visualizing it
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "description": product_data.get("description", ""),
            "url": product_data.get("url", ""),
            "pricing": product_data.get("pricing", ""),
            "audience": product_data.get("audience", ""),
            "features": features,
            "gaps": gaps,
            "similar_products": similar_products,
            "categories": categories,
            "uniqueness_score": sum(f["uniqueness"] for f in features) / len(features) if features else 0.0
        }