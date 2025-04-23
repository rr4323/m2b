"""
Knowledge Graph utilities for the SaaS Cloner system.
This module provides functionality for creating, updating, and querying a knowledge graph
of SaaS products, features, and market trends.
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

import networkx as nx
from pyvis.network import Network

class SaaSKnowledgeGraph:
    """
    Knowledge Graph for SaaS products, features, and relationships.
    
    This class provides methods to build and query a knowledge graph of SaaS products,
    enabling sophisticated analysis of market trends, feature gaps, and enhancement opportunities.
    """
    
    def __init__(self, graph_file: str = "data/knowledge_graph.json"):
        """
        Initialize the knowledge graph.
        
        Args:
            graph_file: Path to store the graph data
        """
        self.graph = nx.DiGraph()
        self.graph_file = graph_file
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(graph_file), exist_ok=True)
        
        # Load existing graph if available
        if os.path.exists(graph_file):
            self._load_graph()
        else:
            self._initialize_empty_graph()
            
        logging.info(f"Knowledge graph initialized with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
    
    def _initialize_empty_graph(self):
        """Initialize an empty graph with basic categories"""
        # Add top-level category nodes
        categories = [
            "Productivity", "Project Management", "Communication", "CRM", 
            "Marketing", "Analytics", "Design", "Development", "HR", "Finance"
        ]
        
        for category in categories:
            self.graph.add_node(
                category,
                node_type="Category",
                description=f"{category} SaaS applications",
                created_at=datetime.now().isoformat()
            )
            
        # Add basic relationships between categories where relevant
        related_categories = [
            ("Productivity", "Project Management"),
            ("Project Management", "Development"),
            ("Communication", "Project Management"),
            ("Marketing", "CRM"),
            ("Analytics", "Marketing"),
            ("Development", "Design")
        ]
        
        for source, target in related_categories:
            self.graph.add_edge(
                source, target,
                relationship="related_to",
                weight=0.5,
                created_at=datetime.now().isoformat()
            )
        
        # Save the initialized graph
        self._save_graph()
            
    def _load_graph(self):
        """Load the graph from file"""
        try:
            data = json.load(open(self.graph_file, 'r'))
            
            # Clear existing graph
            self.graph.clear()
            
            # Add nodes
            for node, attrs in data['nodes'].items():
                self.graph.add_node(node, **attrs)
                
            # Add edges
            for source, targets in data['edges'].items():
                for target, attrs in targets.items():
                    self.graph.add_edge(source, target, **attrs)
                    
            logging.info(f"Loaded knowledge graph from {self.graph_file}")
        except Exception as e:
            logging.error(f"Error loading knowledge graph: {e}")
            self._initialize_empty_graph()
    
    def _save_graph(self):
        """Save the graph to file"""
        try:
            # Convert graph to serializable format
            data = {
                'nodes': {node: attrs for node, attrs in self.graph.nodes(data=True)},
                'edges': {}
            }
            
            # Process edges
            for source, target, attrs in self.graph.edges(data=True):
                if source not in data['edges']:
                    data['edges'][source] = {}
                data['edges'][source][target] = attrs
            
            # Save to file
            with open(self.graph_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logging.info(f"Saved knowledge graph to {self.graph_file}")
        except Exception as e:
            logging.error(f"Error saving knowledge graph: {e}")
    
    def add_product(self, product_data: Dict[str, Any]) -> str:
        """
        Add a SaaS product to the knowledge graph.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            str: ID of the added product node
        """
        product_name = product_data.get('name')
        if not product_name:
            raise ValueError("Product data must include a name")
        
        # Add the product node if it doesn't exist
        if product_name not in self.graph.nodes:
            self.graph.add_node(
                product_name,
                node_type="Product",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                **{k: v for k, v in product_data.items() if k != 'name'}
            )
        else:
            # Update existing product
            for key, value in product_data.items():
                if key != 'name':
                    self.graph.nodes[product_name][key] = value
            self.graph.nodes[product_name]['updated_at'] = datetime.now().isoformat()
        
        # Add connections to categories if provided
        categories = product_data.get('categories', [])
        for category in categories:
            if category in self.graph.nodes:
                self.graph.add_edge(
                    category, product_name,
                    relationship="contains",
                    weight=1.0,
                    created_at=datetime.now().isoformat()
                )
        
        # Add features if provided
        features = product_data.get('feature_list', [])
        for feature in features:
            feature_id = f"feature:{feature}"
            
            # Add feature node if it doesn't exist
            if feature_id not in self.graph.nodes:
                self.graph.add_node(
                    feature_id,
                    node_type="Feature",
                    name=feature,
                    description=feature,
                    created_at=datetime.now().isoformat()
                )
            
            # Connect product to feature
            self.graph.add_edge(
                product_name, feature_id,
                relationship="has_feature",
                weight=1.0,
                created_at=datetime.now().isoformat()
            )
        
        # Add competitors if provided
        competitors = product_data.get('competitors', [])
        for competitor in competitors:
            if competitor in self.graph.nodes:
                self.graph.add_edge(
                    product_name, competitor,
                    relationship="competes_with",
                    weight=1.0,
                    created_at=datetime.now().isoformat()
                )
                
                # Add the reverse relationship
                self.graph.add_edge(
                    competitor, product_name,
                    relationship="competes_with",
                    weight=1.0,
                    created_at=datetime.now().isoformat()
                )
        
        # Save changes
        self._save_graph()
        
        return product_name
    
    def get_product_features(self, product_name: str) -> List[str]:
        """
        Get features of a specific product.
        
        Args:
            product_name: Name of the product
            
        Returns:
            List of feature names
        """
        if product_name not in self.graph.nodes:
            return []
        
        features = []
        for _, target in self.graph.out_edges(product_name):
            if target.startswith("feature:") and self.graph[product_name][target].get('relationship') == 'has_feature':
                features.append(self.graph.nodes[target].get('name'))
        
        return features
    
    def get_competitive_products(self, product_name: str) -> List[Dict[str, Any]]:
        """
        Get products that compete with the specified product.
        
        Args:
            product_name: Name of the product
            
        Returns:
            List of competitor products with their details
        """
        if product_name not in self.graph.nodes:
            return []
        
        competitors = []
        for _, target in self.graph.out_edges(product_name):
            if self.graph[product_name][target].get('relationship') == 'competes_with':
                competitors.append({
                    'name': target,
                    **{k: v for k, v in self.graph.nodes[target].items() if k != 'name'}
                })
        
        return competitors
    
    def find_missing_features(self, product_name: str, competitor_names: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Identify features missing from the product compared to competitors.
        
        Args:
            product_name: Name of the product to analyze
            competitor_names: Optional list of specific competitors to compare against,
                              otherwise all competitors will be used
                              
        Returns:
            Dictionary mapping competitor names to lists of features missing from the product
        """
        if product_name not in self.graph.nodes:
            return {}
        
        # Get this product's features
        product_features = set(self.get_product_features(product_name))
        
        # Get competitors
        competitors = self.get_competitive_products(product_name)
        if competitor_names:
            competitors = [c for c in competitors if c['name'] in competitor_names]
        
        missing_features = {}
        for competitor in competitors:
            competitor_name = competitor['name']
            competitor_features = set(self.get_product_features(competitor_name))
            
            # Find features in competitor that are not in our product
            missing = competitor_features - product_features
            if missing:
                missing_features[competitor_name] = list(missing)
        
        return missing_features
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all products in a specific category.
        
        Args:
            category: Name of the category
            
        Returns:
            List of products with their details
        """
        if category not in self.graph.nodes:
            return []
        
        products = []
        for _, target in self.graph.out_edges(category):
            if self.graph[category][target].get('relationship') == 'contains':
                products.append({
                    'name': target,
                    **{k: v for k, v in self.graph.nodes[target].items() if k != 'name'}
                })
        
        return products
    
    def find_similar_products(self, product_name: str, min_similarity: float = 0.3) -> List[Tuple[str, float]]:
        """
        Find products similar to the given product based on shared features.
        
        Args:
            product_name: Name of the product
            min_similarity: Minimum similarity score (0-1) for inclusion in results
            
        Returns:
            List of tuples (product_name, similarity_score) sorted by descending similarity
        """
        if product_name not in self.graph.nodes:
            return []
        
        # Get all products
        product_nodes = [n for n, attrs in self.graph.nodes(data=True) 
                        if attrs.get('node_type') == 'Product' and n != product_name]
        
        # Get features of the reference product
        ref_features = set(self.get_product_features(product_name))
        if not ref_features:
            return []
        
        # Calculate similarity scores
        similarity_scores = []
        for other_product in product_nodes:
            other_features = set(self.get_product_features(other_product))
            if not other_features:
                continue
            
            # Jaccard similarity: intersection / union
            intersection = len(ref_features.intersection(other_features))
            union = len(ref_features.union(other_features))
            
            if union > 0:
                similarity = intersection / union
                if similarity >= min_similarity:
                    similarity_scores.append((other_product, similarity))
        
        # Sort by descending similarity
        return sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    def find_popular_features(self, category: Optional[str] = None, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Find the most popular features across products.
        
        Args:
            category: Optional category to filter products
            limit: Maximum number of features to return
            
        Returns:
            List of tuples (feature_name, count) sorted by descending count
        """
        # Get relevant products
        if category is not None:
            products = [p['name'] for p in self.get_products_by_category(category)]
        else:
            products = [n for n, attrs in self.graph.nodes(data=True) 
                      if attrs.get('node_type') == 'Product']
        
        # Count feature occurrences
        feature_counts = {}
        for product in products:
            features = self.get_product_features(product)
            for feature in features:
                if feature in feature_counts:
                    feature_counts[feature] += 1
                else:
                    feature_counts[feature] = 1
        
        # Sort by count and return top features
        sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_features[:limit]
    
    def visualize(self, output_file: str = "output/knowledge_graph.html", 
                 height: str = "800px", width: str = "100%"):
        """
        Generate an interactive visualization of the knowledge graph.
        
        Args:
            output_file: Path to save the HTML output
            height: Height of the visualization
            width: Width of the visualization
        """
        # Create network
        net = Network(height=height, width=width, directed=True, notebook=False)
        
        # Configure physics
        net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250)
        
        # Color configuration
        node_colors = {
            "Category": "#4287f5",  # Blue
            "Product": "#42f554",   # Green
            "Feature": "#f5a742"    # Orange
        }
        
        # Add nodes
        for node, attrs in self.graph.nodes(data=True):
            node_type = attrs.get('node_type', 'Unknown')
            label = attrs.get('name', node)
            
            if node.startswith("feature:"):
                label = attrs.get('name', node.replace("feature:", ""))
            
            title = f"<b>{label}</b><br>"
            if 'description' in attrs:
                title += f"{attrs['description']}<br>"
            
            for k, v in attrs.items():
                if k not in ['node_type', 'name', 'description', 'created_at', 'updated_at']:
                    title += f"{k}: {v}<br>"
            
            net.add_node(
                node, 
                label=label,
                title=title,
                color=node_colors.get(node_type, "#b2b2b2"),
                shape="dot" if node_type == "Feature" else "ellipse",
                size=15 if node_type == "Category" else 10
            )
        
        # Add edges
        for source, target, attrs in self.graph.edges(data=True):
            relationship = attrs.get('relationship', '')
            
            # Set edge color based on relationship
            if relationship == 'has_feature':
                color = '#9c27b0'  # Purple
            elif relationship == 'contains':
                color = '#2196f3'  # Blue
            elif relationship == 'competes_with':
                color = '#f44336'  # Red
            else:
                color = '#999999'  # Gray
            
            net.add_edge(
                source, target,
                title=relationship,
                color=color,
                arrows="to"
            )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save visualization
        net.save_graph(output_file)
        
        return output_file
    
    def query_graph(self, query_type: str, **kwargs) -> Any:
        """
        Query the knowledge graph with various query types.
        
        Args:
            query_type: Type of query to perform
            **kwargs: Parameters specific to the query type
            
        Returns:
            Query results (format depends on query type)
        """
        # Map query type to function
        query_functions = {
            'product_features': self.get_product_features,
            'competitive_products': self.get_competitive_products,
            'missing_features': self.find_missing_features,
            'products_by_category': self.get_products_by_category,
            'similar_products': self.find_similar_products,
            'popular_features': self.find_popular_features
        }
        
        if query_type not in query_functions:
            raise ValueError(f"Unknown query type: {query_type}")
        
        # Execute the query
        return query_functions[query_type](**kwargs)
    
    def bulk_add_products(self, products: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple products to the knowledge graph.
        
        Args:
            products: List of product data dictionaries
            
        Returns:
            List of added product IDs
        """
        added_ids = []
        for product in products:
            try:
                product_id = self.add_product(product)
                added_ids.append(product_id)
            except Exception as e:
                logging.error(f"Error adding product {product.get('name')}: {e}")
        
        return added_ids

def create_knowledge_graph() -> SaaSKnowledgeGraph:
    """
    Factory function to create a knowledge graph instance.
    
    Returns:
        SaaSKnowledgeGraph: Initialized knowledge graph
    """
    return SaaSKnowledgeGraph()