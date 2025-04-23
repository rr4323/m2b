"""
Product models for the SaaS Cloner system.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ProductFeature(BaseModel):
    """A feature of a SaaS product."""
    name: str = Field(..., description="Name of the feature")
    description: str = Field(..., description="Description of the feature")
    priority: str = Field(..., description="Priority of the feature (Core, High, Medium, Low)")
    status: Optional[str] = Field(None, description="Status of the feature (Retained, Improved, New)")
    addresses_gap: Optional[str] = Field(None, description="Gap that this feature addresses")
    differentiator: Optional[str] = Field(None, description="How this feature differentiates from competitors")
    ai_technology: Optional[str] = Field(None, description="AI/ML technology used in this feature")

class ProductFeatureSet(BaseModel):
    """Feature set of a SaaS product."""
    core_features: List[ProductFeature] = Field(default_factory=list, description="Core features of the product")
    new_features: List[ProductFeature] = Field(default_factory=list, description="New features of the product")
    advanced_features: List[ProductFeature] = Field(default_factory=list, description="Advanced features of the product")
    ai_powered_features: List[ProductFeature] = Field(default_factory=list, description="AI-powered features of the product")

class TechStackItem(BaseModel):
    """An item in the tech stack of a SaaS product."""
    name: str = Field(..., description="Name of the technology")
    version: Optional[str] = Field(None, description="Version of the technology")
    justification: Optional[str] = Field(None, description="Justification for using this technology")

class TechStack(BaseModel):
    """Tech stack of a SaaS product."""
    frontend: Dict[str, Any] = Field(default_factory=dict, description="Frontend technology stack")
    backend: Dict[str, Any] = Field(default_factory=dict, description="Backend technology stack")
    database_storage: Dict[str, Any] = Field(default_factory=dict, description="Database and storage technology stack")
    auth: Dict[str, Any] = Field(default_factory=dict, description="Authentication and authorization technology stack")
    infrastructure: Dict[str, Any] = Field(default_factory=dict, description="Infrastructure technology stack")
    ai_ml: Optional[Dict[str, Any]] = Field(default_factory=dict, description="AI/ML technology stack")
    third_party_services: List[Dict[str, Any]] = Field(default_factory=list, description="Third-party services")

class ImplementationRoadmap(BaseModel):
    """Implementation roadmap for a SaaS product."""
    phase_1: List[str] = Field(default_factory=list, description="Phase 1 implementation items")
    phase_2: List[str] = Field(default_factory=list, description="Phase 2 implementation items")
    phase_3: List[str] = Field(default_factory=list, description="Phase 3 implementation items")

class ProductCreate(BaseModel):
    """Data required to create a new product."""
    name: str = Field(..., description="Name of the product")
    description: str = Field(..., description="Description of the product")
    category: Optional[str] = Field(None, description="Category of the product")
    original_product: Optional[str] = Field(None, description="Name of the original product")
    url: Optional[str] = Field(None, description="URL of the product")
    features: Optional[ProductFeatureSet] = Field(None, description="Features of the product")
    tech_stack: Optional[TechStack] = Field(None, description="Tech stack of the product")

class Product(ProductCreate):
    """A SaaS product in the system."""
    id: str = Field(..., description="Unique identifier for the product")
    project_id: str = Field(..., description="ID of the project this product belongs to")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    enhancements: List[str] = Field(default_factory=list, description="Enhancements over the original product")
    ai_integration: List[str] = Field(default_factory=list, description="AI integrations in the product")
    target_user: Optional[str] = Field(None, description="Target user of the product")
    pricing_strategy: Optional[str] = Field(None, description="Pricing strategy of the product")
    implementation_roadmap: Optional[ImplementationRoadmap] = Field(None, description="Implementation roadmap")
    marketing_highlights: List[str] = Field(default_factory=list, description="Marketing highlights")
    potential_challenges: List[str] = Field(default_factory=list, description="Potential challenges")
    status: str = Field("draft", description="Status of the product")

class ProductList(BaseModel):
    """List of products with pagination."""
    items: List[Product] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(1, description="Current page number")
    size: int = Field(10, description="Number of items per page")

class GapAnalysis(BaseModel):
    """Gap analysis for a product."""
    list_of_problems: List[str] = Field(default_factory=list, description="List of problems")
    missing_features: List[str] = Field(default_factory=list, description="Missing features")
    ui_ux_issues: List[str] = Field(default_factory=list, description="UI/UX issues")
    pricing_feedback: List[str] = Field(default_factory=list, description="Pricing feedback")
    technical_issues: List[str] = Field(default_factory=list, description="Technical issues")
    competitor_advantages: List[str] = Field(default_factory=list, description="Competitor advantages")

class ImprovementOpportunity(BaseModel):
    """Improvement opportunity for a product."""
    core_functionality_enhancements: List[str] = Field(default_factory=list, description="Core functionality enhancements")
    user_experience_improvements: List[str] = Field(default_factory=list, description="User experience improvements")
    ai_ml_integrations: List[str] = Field(default_factory=list, description="AI/ML integrations")
    technical_improvements: List[str] = Field(default_factory=list, description="Technical improvements")
    pricing_optimizations: List[str] = Field(default_factory=list, description="Pricing optimizations")
    key_differentiators: List[str] = Field(default_factory=list, description="Key differentiators")
    implementation_priority: List[str] = Field(default_factory=list, description="Implementation priorities")
    potential_challenges: List[str] = Field(default_factory=list, description="Potential challenges")

class ProductAnalysis(BaseModel):
    """Analysis of a product."""
    product_id: str = Field(..., description="ID of the analyzed product")
    product_name: str = Field(..., description="Name of the analyzed product")
    reviews_analyzed: int = Field(..., description="Number of reviews analyzed")
    identified_gaps: GapAnalysis = Field(..., description="Identified gaps")
    improvement_opportunities: ImprovementOpportunity = Field(..., description="Improvement opportunities")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
