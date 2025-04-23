"""
Knowledge Graph utilities for the SaaS Cloner system.

This module provides functionality for creating, manipulating, and visualizing
a knowledge graph of SaaS products, features, markets, and their relationships.
"""
import logging
import os
from typing import Dict, Any, List, Set, Tuple, Optional

import networkx as nx
from pyvis.network import Network

import config

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """
    Knowledge Graph for SaaS products and their relationships.
    
    This class provides functionality for building and analyzing a knowledge graph
    of SaaS products, features, markets, and their relationships.
    """
    
    def __init__(self):
        """Initialize the Knowledge Graph."""
        self.graph = nx.Graph()
        self.product_nodes = set()
        self.feature_nodes = set()
        self.category_nodes = set()
        self.company_nodes = set()
        self.user_need_nodes = set()
        
    def add_product(self, product_data: Dict[str, Any]) -> str:
        """
        Add a product to the knowledge graph.
        
        Args:
            product_data: A dictionary containing product information
                
        Returns:
            str: The ID of the added product node
        """
        # Extract product information
        product_id = f"product:{product_data.get('name', '').lower().replace(' ', '_')}"
        product_name = product_data.get('name', 'Unknown Product')
        product_description = product_data.get('description', '')
        product_url = product_data.get('url', '')
        product_category = product_data.get('category', '')
        product_features = product_data.get('feature_list', [])
        product_pricing = product_data.get('pricing_model', '')
        product_audience = product_data.get('target_audience', '')
        
        # Add product node
        self.graph.add_node(
            product_id, 
            type='product',
            name=product_name,
            description=product_description,
            url=product_url,
            pricing=product_pricing,
            audience=product_audience
        )
        self.product_nodes.add(product_id)
        
        # Add category and connect to product
        if product_category:
            category_id = f"category:{product_category.lower().replace(' ', '_')}"
            self.graph.add_node(
                category_id,
                type='category',
                name=product_category
            )
            self.category_nodes.add(category_id)
            self.graph.add_edge(product_id, category_id, relationship='belongs_to')
        
        # Add features and connect to product
        for feature in product_features:
            feature_id = f"feature:{feature.lower().replace(' ', '_')}"
            self.graph.add_node(
                feature_id,
                type='feature',
                name=feature
            )
            self.feature_nodes.add(feature_id)
            self.graph.add_edge(product_id, feature_id, relationship='has_feature')
        
        logger.info(f"Added product '{product_name}' to knowledge graph")
        return product_id
    
    def add_gap(self, gap_data: Dict[str, Any], related_products: Optional[List[str]] = None) -> str:
        """
        Add a gap to the knowledge graph.
        
        Args:
            gap_data: A dictionary containing gap information
            related_products: Optional list of product IDs that this gap relates to
                
        Returns:
            str: The ID of the added gap node
        """
        # Extract gap information
        gap_type = gap_data.get('type', 'feature')  # feature, market, or experience
        gap_description = gap_data.get('description', '')
        gap_name = gap_data.get('name', gap_description[:30])
        
        # Create a unique ID for the gap
        gap_id = f"gap:{gap_type}:{gap_name.lower().replace(' ', '_')}"
        
        # Add gap node
        self.graph.add_node(
            gap_id,
            type='gap',
            gap_type=gap_type,
            name=gap_name,
            description=gap_description
        )
        
        # Connect gap to related products
        if related_products:
            for product_id in related_products:
                if product_id in self.product_nodes:
                    self.graph.add_edge(gap_id, product_id, relationship='identified_in')
        
        # If this is a feature gap, add it as a potential feature
        if gap_type == 'feature':
            feature_id = f"feature:{gap_name.lower().replace(' ', '_')}"
            
            if feature_id not in self.feature_nodes:
                self.graph.add_node(
                    feature_id,
                    type='feature',
                    name=gap_name
                )
                self.feature_nodes.add(feature_id)
            
            self.graph.add_edge(gap_id, feature_id, relationship='suggests')
        
        logger.info(f"Added gap '{gap_name}' to knowledge graph")
        return gap_id
    
    def add_user_need(self, need_data: Dict[str, Any], related_features: Optional[List[str]] = None) -> str:
        """
        Add a user need to the knowledge graph.
        
        Args:
            need_data: A dictionary containing user need information
            related_features: Optional list of feature IDs that address this need
                
        Returns:
            str: The ID of the added user need node
        """
        # Extract need information
        need_name = need_data.get('name', 'Unknown Need')
        need_description = need_data.get('description', '')
        need_importance = need_data.get('importance', 'medium')
        
        # Create a unique ID for the need
        need_id = f"need:{need_name.lower().replace(' ', '_')}"
        
        # Add need node
        self.graph.add_node(
            need_id,
            type='user_need',
            name=need_name,
            description=need_description,
            importance=need_importance
        )
        self.user_need_nodes.add(need_id)
        
        # Connect need to related features
        if related_features:
            for feature_id in related_features:
                if feature_id in self.feature_nodes:
                    self.graph.add_edge(need_id, feature_id, relationship='addressed_by')
        
        logger.info(f"Added user need '{need_name}' to knowledge graph")
        return need_id
    
    def add_company(self, company_data: Dict[str, Any], company_products: Optional[List[str]] = None) -> str:
        """
        Add a company to the knowledge graph.
        
        Args:
            company_data: A dictionary containing company information
            company_products: Optional list of product IDs made by this company
                
        Returns:
            str: The ID of the added company node
        """
        # Extract company information
        company_name = company_data.get('name', 'Unknown Company')
        company_description = company_data.get('description', '')
        company_url = company_data.get('url', '')
        company_size = company_data.get('size', '')
        company_funding = company_data.get('funding', '')
        
        # Create a unique ID for the company
        company_id = f"company:{company_name.lower().replace(' ', '_')}"
        
        # Add company node
        self.graph.add_node(
            company_id,
            type='company',
            name=company_name,
            description=company_description,
            url=company_url,
            size=company_size,
            funding=company_funding
        )
        self.company_nodes.add(company_id)
        
        # Connect company to its products
        if company_products:
            for product_id in company_products:
                if product_id in self.product_nodes:
                    self.graph.add_edge(company_id, product_id, relationship='makes')
        
        logger.info(f"Added company '{company_name}' to knowledge graph")
        return company_id
    
    def add_relationship(self, source_id: str, target_id: str, relationship_type: str, 
                         properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a relationship between two nodes.
        
        Args:
            source_id: The ID of the source node
            target_id: The ID of the target node
            relationship_type: The type of relationship
            properties: Optional dictionary of relationship properties
                
        Returns:
            bool: True if the relationship was added, False otherwise
        """
        if source_id in self.graph and target_id in self.graph:
            # Add the edge with properties
            edge_properties = {'relationship': relationship_type}
            if properties:
                edge_properties.update(properties)
            
            self.graph.add_edge(source_id, target_id, **edge_properties)
            logger.info(f"Added relationship '{relationship_type}' between '{source_id}' and '{target_id}'")
            return True
        else:
            logger.warning(f"Cannot add relationship: one or both nodes '{source_id}' and '{target_id}' do not exist")
            return False
    
    def find_similar_products(self, product_id: str, similarity_threshold: float = 0.5) -> List[Tuple[str, float]]:
        """
        Find products similar to the given product.
        
        Args:
            product_id: The ID of the product to find similar products for
            similarity_threshold: Minimum similarity score (0-1) for products to be considered similar
                
        Returns:
            List[Tuple[str, float]]: List of tuples containing product IDs and similarity scores
        """
        if product_id not in self.product_nodes:
            logger.warning(f"Product '{product_id}' not found in knowledge graph")
            return []
        
        similarity_scores = []
        product_features = set(neighbor for neighbor in self.graph.neighbors(product_id)
                               if neighbor in self.feature_nodes)
        
        for other_product in self.product_nodes:
            if other_product == product_id:
                continue
            
            other_features = set(neighbor for neighbor in self.graph.neighbors(other_product)
                                if neighbor in self.feature_nodes)
            
            # Calculate Jaccard similarity
            if not product_features or not other_features:
                similarity = 0.0
            else:
                intersection = len(product_features.intersection(other_features))
                union = len(product_features.union(other_features))
                similarity = intersection / union
            
            if similarity >= similarity_threshold:
                similarity_scores.append((other_product, similarity))
        
        # Sort by similarity score in descending order
        return sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    def find_gaps_for_product(self, product_id: str) -> List[str]:
        """
        Find gaps identified for a specific product.
        
        Args:
            product_id: The ID of the product to find gaps for
                
        Returns:
            List[str]: List of gap IDs
        """
        if product_id not in self.product_nodes:
            logger.warning(f"Product '{product_id}' not found in knowledge graph")
            return []
        
        gaps = []
        for node in self.graph.nodes():
            if node.startswith('gap:') and product_id in [neighbor for neighbor in self.graph.neighbors(node)]:
                gaps.append(node)
        
        return gaps
    
    def find_feature_gap_opportunities(self, min_products: int = 2) -> List[Tuple[str, List[str]]]:
        """
        Find features that multiple products have but some don't, indicating potential gaps.
        
        Args:
            min_products: Minimum number of products that must have a feature for it to be considered common
                
        Returns:
            List[Tuple[str, List[str]]]: List of tuples containing feature IDs and list of products missing the feature
        """
        opportunities = []
        
        for feature in self.feature_nodes:
            # Find products that have this feature
            products_with_feature = [neighbor for neighbor in self.graph.neighbors(feature)
                                     if neighbor in self.product_nodes]
            
            if len(products_with_feature) >= min_products:
                # Find products that don't have this feature
                products_without_feature = self.product_nodes - set(products_with_feature)
                
                if products_without_feature:
                    opportunities.append((feature, list(products_without_feature)))
        
        return opportunities
    
    def visualize(self, output_path: Optional[str] = None) -> str:
        """
        Create a visualization of the knowledge graph.
        
        Args:
            output_path: Optional path to save the visualization to
                
        Returns:
            str: Path to the saved visualization
        """
        if not output_path:
            output_path = config.KNOWLEDGE_GRAPH_VISUALIZATION_PATH
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create network visualization
        net = Network(height="800px", width="100%", notebook=False)
        
        # Add nodes with proper colors and shapes
        for node_id in self.graph.nodes():
            node_type = self.graph.nodes[node_id].get('type', 'unknown')
            node_name = self.graph.nodes[node_id].get('name', node_id)
            
            # Set node properties based on type
            if node_type == 'product':
                color = '#4285F4'  # Blue
                shape = 'dot'
                size = 25
            elif node_type == 'feature':
                color = '#34A853'  # Green
                shape = 'diamond'
                size = 15
            elif node_type == 'category':
                color = '#FBBC05'  # Yellow
                shape = 'triangle'
                size = 20
            elif node_type == 'gap':
                color = '#EA4335'  # Red
                shape = 'star'
                size = 20
            elif node_type == 'user_need':
                color = '#9C27B0'  # Purple
                shape = 'square'
                size = 15
            elif node_type == 'company':
                color = '#FF6D01'  # Orange
                shape = 'hexagon'
                size = 20
            else:
                color = '#CCCCCC'  # Grey
                shape = 'dot'
                size = 10
            
            # Create node title (tooltip)
            node_title = f"<b>{node_name}</b><br>"
            for key, value in self.graph.nodes[node_id].items():
                if key not in ['type', 'name']:
                    node_title += f"{key}: {value}<br>"
            
            net.add_node(node_id, label=node_name, title=node_title, 
                         color=color, shape=shape, size=size)
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            relationship = data.get('relationship', 'related_to')
            
            # Set edge properties based on relationship
            if relationship == 'has_feature':
                color = '#34A853'  # Green
            elif relationship == 'belongs_to':
                color = '#FBBC05'  # Yellow
            elif relationship == 'identified_in':
                color = '#EA4335'  # Red
            elif relationship == 'makes':
                color = '#FF6D01'  # Orange
            elif relationship == 'addressed_by':
                color = '#9C27B0'  # Purple
            else:
                color = '#AAAAAA'  # Light grey
            
            net.add_edge(source, target, title=relationship, color=color)
        
        # Apply physics settings for better visualization
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {
              "enabled": true,
              "iterations": 1000
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 200
          }
        }
        """)
        
        # Save the visualization
        net.save_graph(output_path)
        logger.info(f"Knowledge graph visualization saved to {output_path}")
        
        return output_path
    
    def export_to_json(self) -> Dict[str, Any]:
        """
        Export the knowledge graph to a JSON serializable dictionary.
        
        Returns:
            Dict[str, Any]: The knowledge graph as a JSON serializable dictionary
        """
        json_graph = {
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for node_id, node_data in self.graph.nodes(data=True):
            node_info = {"id": node_id}
            node_info.update(node_data)
            json_graph["nodes"].append(node_info)
        
        # Add edges
        for source, target, edge_data in self.graph.edges(data=True):
            edge_info = {
                "source": source,
                "target": target
            }
            edge_info.update(edge_data)
            json_graph["edges"].append(edge_info)
        
        return json_graph
    
    def import_from_json(self, json_graph: Dict[str, Any]) -> None:
        """
        Import a knowledge graph from a JSON serializable dictionary.
        
        Args:
            json_graph: The knowledge graph as a JSON serializable dictionary
        """
        # Create a new graph
        self.graph = nx.Graph()
        self.product_nodes = set()
        self.feature_nodes = set()
        self.category_nodes = set()
        self.company_nodes = set()
        self.user_need_nodes = set()
        
        # Add nodes
        for node_info in json_graph["nodes"]:
            node_id = node_info.pop("id")
            self.graph.add_node(node_id, **node_info)
            
            # Add to appropriate set based on type
            node_type = node_info.get("type", "unknown")
            if node_type == "product":
                self.product_nodes.add(node_id)
            elif node_type == "feature":
                self.feature_nodes.add(node_id)
            elif node_type == "category":
                self.category_nodes.add(node_id)
            elif node_type == "company":
                self.company_nodes.add(node_id)
            elif node_type == "user_need":
                self.user_need_nodes.add(node_id)
        
        # Add edges
        for edge_info in json_graph["edges"]:
            source = edge_info.pop("source")
            target = edge_info.pop("target")
            self.graph.add_edge(source, target, **edge_info)
        
        logger.info(f"Imported knowledge graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")

# Create a singleton instance
knowledge_graph = KnowledgeGraph()