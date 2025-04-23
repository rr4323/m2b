"""
DevOps Agent for setting up infrastructure and CI/CD pipelines.
"""
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion, generate_completion

class DevOpsAgent(BaseAgent):
    """Agent for setting up infrastructure and CI/CD pipelines."""
    
    def __init__(self):
        """Initialize the DevOps Agent."""
        super().__init__(
            name="DevOps Agent",
            description="Sets up infrastructure and CI/CD pipelines"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the DevOps process to set up infrastructure and CI/CD pipelines.
        
        Args:
            input_data (Dict[str, Any]): Input data containing product specs and implementation details
                
        Returns:
            Dict[str, Any]: DevOps implementation details
        """
        self.log_info("Starting DevOps process")
        
        blueprint = input_data.get("blueprint", {})
        frontend_details = input_data.get("frontend_details", {})
        backend_details = input_data.get("backend_details", {})
        
        if not blueprint:
            self.log_error("No product blueprint provided for DevOps")
            return {"error": "No product blueprint provided for DevOps"}
        
        product_name = blueprint.get("product_name", "")
        
        self.log_info(f"Setting up DevOps for: {product_name}")
        
        # Step 1: Define infrastructure architecture
        infrastructure = await self._define_infrastructure(blueprint, frontend_details, backend_details)
        
        # Step 2: Create Docker configuration
        docker_config = await self._create_docker_config(blueprint, frontend_details, backend_details)
        
        # Step 3: Define Kubernetes manifests
        kubernetes_manifests = await self._define_kubernetes_manifests(blueprint, infrastructure)
        
        # Step 4: Create CI/CD pipeline
        ci_cd_pipeline = await self._create_ci_cd_pipeline(blueprint, infrastructure)
        
        # Step 5: Define monitoring and logging setup
        monitoring = await self._define_monitoring(blueprint, infrastructure)
        
        return {
            "product_name": product_name,
            "infrastructure": infrastructure,
            "docker_config": docker_config,
            "kubernetes_manifests": kubernetes_manifests,
            "ci_cd_pipeline": ci_cd_pipeline,
            "monitoring": monitoring
        }
    
    async def _define_infrastructure(
        self, 
        blueprint: Dict[str, Any],
        frontend_details: Dict[str, Any],
        backend_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define the infrastructure architecture.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            frontend_details (Dict[str, Any]): The frontend implementation details
            backend_details (Dict[str, Any]): The backend implementation details
            
        Returns:
            Dict[str, Any]: Infrastructure architecture
        """
        self.log_info("Defining infrastructure architecture")
        
        tech_stack = blueprint.get("stack", {})
        infrastructure_tech = tech_stack.get("infrastructure", {})
        
        system_message = (
            "You are a DevOps architect specializing in cloud infrastructure for "
            "SaaS applications. Define a comprehensive infrastructure architecture "
            "for the product based on the specified technology stack and implementation "
            "details. The architecture should be scalable, secure, and cost-effective."
        )
        
        prompt = (
            f"Define an infrastructure architecture for the product with these specifications:\n\n"
            f"Infrastructure Tech Stack: {tech_stack}\n\n"
            f"The architecture should include:\n"
            f"1. Cloud provider and services\n"
            f"2. Compute resources\n"
            f"3. Networking setup\n"
            f"4. Storage solutions\n"
            f"5. Database hosting\n"
            f"6. Security measures\n"
            f"7. Scalability approach\n"
            f"8. Disaster recovery strategy\n\n"
            f"Justify your infrastructure decisions and explain how they support "
            f"the product's requirements for performance, scalability, and reliability."
        )
        
        infrastructure_structure = {
            "cloud_provider": {
                "name": "Provider name",
                "region": "Region",
                "justification": "Justification for this choice"
            },
            "compute": {
                "type": "Compute type",
                "sizing": "Sizing details",
                "justification": "Justification for this choice"
            },
            "networking": {
                "architecture": "Network architecture",
                "components": ["Component 1", "Component 2"]
            },
            "storage": {
                "solutions": ["Solution 1", "Solution 2"],
                "justification": "Justification for these choices"
            },
            "database": {
                "hosting": "Hosting solution",
                "configuration": "Configuration details",
                "justification": "Justification for this choice"
            },
            "security": {
                "measures": ["Measure 1", "Measure 2"],
                "compliance": ["Compliance 1", "Compliance 2"]
            },
            "scalability": {
                "approach": "Scalability approach",
                "implementation": "Implementation details"
            },
            "disaster_recovery": {
                "strategy": "DR strategy",
                "implementation": "Implementation details"
            },
            "estimated_costs": {
                "monthly": "Estimated monthly cost",
                "breakdown": ["Cost item 1", "Cost item 2"]
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define infrastructure architecture, using default structure")
            return infrastructure_structure
        
        return result
    
    async def _create_docker_config(
        self, 
        blueprint: Dict[str, Any],
        frontend_details: Dict[str, Any],
        backend_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create Docker configuration for the application.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            frontend_details (Dict[str, Any]): The frontend implementation details
            backend_details (Dict[str, Any]): The backend implementation details
            
        Returns:
            Dict[str, Any]: Docker configuration
        """
        self.log_info("Creating Docker configuration")
        
        tech_stack = blueprint.get("stack", {})
        frontend_tech = tech_stack.get("frontend", {})
        backend_tech = tech_stack.get("backend", {})
        
        system_message = (
            "You are a DevOps engineer specializing in containerization for "
            "SaaS applications. Create comprehensive Docker configuration for "
            "the product based on the specified technology stack and implementation "
            "details. The configuration should be optimized for performance, "
            "security, and ease of deployment."
        )
        
        prompt = (
            f"Create Docker configuration for the product with these specifications:\n\n"
            f"Frontend Tech Stack: {frontend_tech}\n\n"
            f"Backend Tech Stack: {backend_tech}\n\n"
            f"The Docker configuration should include:\n"
            f"1. Dockerfile for each service (frontend, backend, etc.)\n"
            f"2. Docker Compose configuration for local development\n"
            f"3. Multi-stage builds for optimization\n"
            f"4. Base image selection and justification\n"
            f"5. Security considerations\n"
            f"6. Volume management\n"
            f"7. Network configuration\n\n"
            f"Consider best practices for containerization of the specified "
            f"technologies and optimization for production deployment."
        )
        
        docker_config_structure = {
            "frontend": {
                "base_image": "Base image",
                "build_stages": ["Stage 1", "Stage 2"],
                "dockerfile_content": "Dockerfile content",
                "optimizations": ["Optimization 1", "Optimization 2"]
            },
            "backend": {
                "base_image": "Base image",
                "build_stages": ["Stage 1", "Stage 2"],
                "dockerfile_content": "Dockerfile content",
                "optimizations": ["Optimization 1", "Optimization 2"]
            },
            "docker_compose": {
                "services": ["Service 1", "Service 2"],
                "networks": ["Network 1", "Network 2"],
                "volumes": ["Volume 1", "Volume 2"],
                "configuration": "Docker Compose content"
            },
            "security": {
                "considerations": ["Consideration 1", "Consideration 2"],
                "best_practices": ["Practice 1", "Practice 2"]
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to create Docker configuration, using default structure")
            return docker_config_structure
        
        return result
    
    async def _define_kubernetes_manifests(
        self, 
        blueprint: Dict[str, Any],
        infrastructure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define Kubernetes manifests for the application.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            infrastructure (Dict[str, Any]): The infrastructure architecture
            
        Returns:
            Dict[str, Any]: Kubernetes manifests
        """
        self.log_info("Defining Kubernetes manifests")
        
        system_message = (
            "You are a DevOps engineer specializing in Kubernetes for "
            "SaaS applications. Create comprehensive Kubernetes manifests "
            "for the product based on the specified infrastructure architecture. "
            "The manifests should follow best practices for Kubernetes deployment "
            "and be optimized for the specified cloud provider."
        )
        
        prompt = (
            f"Create Kubernetes manifests for the product with these specifications:\n\n"
            f"Infrastructure: {infrastructure}\n\n"
            f"The Kubernetes manifests should include:\n"
            f"1. Deployment configurations for each service\n"
            f"2. Service definitions\n"
            f"3. Ingress configuration\n"
            f"4. ConfigMaps and Secrets management\n"
            f"5. Volume claims\n"
            f"6. Resource limits and requests\n"
            f"7. Autoscaling configuration\n"
            f"8. Health checks and probes\n\n"
            f"Consider best practices for Kubernetes deployment and optimization "
            f"for the specified cloud provider."
        )
        
        kubernetes_structure = {
            "deployments": {
                "frontend": {
                    "replicas": "Number of replicas",
                    "container_spec": "Container specification",
                    "strategy": "Deployment strategy",
                    "manifest_content": "Deployment manifest content"
                },
                "backend": {
                    "replicas": "Number of replicas",
                    "container_spec": "Container specification",
                    "strategy": "Deployment strategy",
                    "manifest_content": "Deployment manifest content"
                }
            },
            "services": {
                "frontend": {
                    "type": "Service type",
                    "ports": ["Port mapping 1", "Port mapping 2"],
                    "manifest_content": "Service manifest content"
                },
                "backend": {
                    "type": "Service type",
                    "ports": ["Port mapping 1", "Port mapping 2"],
                    "manifest_content": "Service manifest content"
                }
            },
            "ingress": {
                "rules": ["Rule 1", "Rule 2"],
                "tls": "TLS configuration",
                "manifest_content": "Ingress manifest content"
            },
            "config": {
                "config_maps": ["ConfigMap 1", "ConfigMap 2"],
                "secrets": ["Secret 1", "Secret 2"]
            },
            "storage": {
                "volume_claims": ["Claim 1", "Claim 2"],
                "storage_classes": ["Class 1", "Class 2"]
            },
            "autoscaling": {
                "metrics": ["Metric 1", "Metric 2"],
                "min_replicas": "Minimum replicas",
                "max_replicas": "Maximum replicas",
                "manifest_content": "HPA manifest content"
            },
            "health": {
                "readiness_probes": ["Probe 1", "Probe 2"],
                "liveness_probes": ["Probe 1", "Probe 2"]
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define Kubernetes manifests, using default structure")
            return kubernetes_structure
        
        return result
    
    async def _create_ci_cd_pipeline(
        self, 
        blueprint: Dict[str, Any],
        infrastructure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create CI/CD pipeline configuration.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            infrastructure (Dict[str, Any]): The infrastructure architecture
            
        Returns:
            Dict[str, Any]: CI/CD pipeline configuration
        """
        self.log_info("Creating CI/CD pipeline")
        
        tech_stack = blueprint.get("stack", {})
        infrastructure_tech = tech_stack.get("infrastructure", {})
        ci_cd = infrastructure_tech.get("ci_cd", "GitHub Actions")
        
        system_message = (
            f"You are a DevOps engineer specializing in CI/CD pipelines for "
            f"SaaS applications. Create a comprehensive CI/CD pipeline using "
            f"{ci_cd} for the product based on the specified infrastructure "
            f"architecture. The pipeline should automate testing, building, "
            f"and deployment processes, following best practices for continuous "
            f"integration and deployment."
        )
        
        prompt = (
            f"Create a CI/CD pipeline using {ci_cd} with these specifications:\n\n"
            f"Infrastructure: {infrastructure}\n\n"
            f"The CI/CD pipeline should include:\n"
            f"1. Workflow definitions for each stage (build, test, deploy)\n"
            f"2. Environment configurations (dev, staging, production)\n"
            f"3. Testing strategies (unit, integration, e2e)\n"
            f"4. Artifact management\n"
            f"5. Deployment strategies\n"
            f"6. Rollback mechanisms\n"
            f"7. Security scanning\n"
            f"8. Notification and monitoring integrations\n\n"
            f"Consider best practices for CI/CD pipelines and optimization "
            f"for the specified infrastructure."
        )
        
        ci_cd_structure = {
            "platform": ci_cd,
            "workflows": {
                "build": {
                    "triggers": ["Trigger 1", "Trigger 2"],
                    "steps": ["Step 1", "Step 2"],
                    "configuration": "Workflow configuration"
                },
                "test": {
                    "triggers": ["Trigger 1", "Trigger 2"],
                    "steps": ["Step 1", "Step 2"],
                    "configuration": "Workflow configuration"
                },
                "deploy": {
                    "triggers": ["Trigger 1", "Trigger 2"],
                    "steps": ["Step 1", "Step 2"],
                    "configuration": "Workflow configuration"
                }
            },
            "environments": {
                "development": {
                    "configuration": "Environment configuration",
                    "deployment_process": "Deployment process description"
                },
                "staging": {
                    "configuration": "Environment configuration",
                    "deployment_process": "Deployment process description"
                },
                "production": {
                    "configuration": "Environment configuration",
                    "deployment_process": "Deployment process description"
                }
            },
            "testing": {
                "unit": "Unit testing strategy",
                "integration": "Integration testing strategy",
                "e2e": "End-to-end testing strategy"
            },
            "artifacts": {
                "storage": "Artifact storage solution",
                "management": "Artifact management process"
            },
            "deployment": {
                "strategy": "Deployment strategy",
                "rollback": "Rollback mechanism"
            },
            "security": {
                "scanning": ["Scanning tool 1", "Scanning tool 2"],
                "integration": "Security integration description"
            },
            "notifications": {
                "channels": ["Channel 1", "Channel 2"],
                "events": ["Event 1", "Event 2"]
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to create CI/CD pipeline, using default structure")
            return ci_cd_structure
        
        return result
    
    async def _define_monitoring(
        self, 
        blueprint: Dict[str, Any],
        infrastructure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define monitoring and logging setup.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            infrastructure (Dict[str, Any]): The infrastructure architecture
            
        Returns:
            Dict[str, Any]: Monitoring and logging configuration
        """
        self.log_info("Defining monitoring and logging setup")
        
        system_message = (
            "You are a DevOps engineer specializing in monitoring and observability "
            "for SaaS applications. Define a comprehensive monitoring and logging "
            "setup for the product based on the specified infrastructure architecture. "
            "The setup should provide full visibility into the application's performance, "
            "errors, and user experience."
        )
        
        prompt = (
            f"Define a monitoring and logging setup with these specifications:\n\n"
            f"Infrastructure: {infrastructure}\n\n"
            f"The monitoring and logging setup should include:\n"
            f"1. Metrics collection and visualization\n"
            f"2. Log aggregation and analysis\n"
            f"3. Application performance monitoring\n"
            f"4. Error tracking and alerting\n"
            f"5. Uptime and availability monitoring\n"
            f"6. User experience monitoring\n"
            f"7. Resource utilization tracking\n"
            f"8. Security monitoring\n\n"
            f"Consider best practices for monitoring and observability of "
            f"SaaS applications and integration with the specified infrastructure."
        )
        
        monitoring_structure = {
            "metrics": {
                "collection": {
                    "tool": "Collection tool",
                    "approach": "Collection approach",
                    "configuration": "Configuration details"
                },
                "visualization": {
                    "tool": "Visualization tool",
                    "dashboards": ["Dashboard 1", "Dashboard 2"],
                    "configuration": "Configuration details"
                }
            },
            "logging": {
                "aggregation": {
                    "tool": "Aggregation tool",
                    "approach": "Aggregation approach",
                    "configuration": "Configuration details"
                },
                "analysis": {
                    "tool": "Analysis tool",
                    "capabilities": ["Capability 1", "Capability 2"],
                    "configuration": "Configuration details"
                }
            },
            "apm": {
                "tool": "APM tool",
                "features": ["Feature 1", "Feature 2"],
                "configuration": "Configuration details"
            },
            "error_tracking": {
                "tool": "Error tracking tool",
                "integration": "Integration approach",
                "configuration": "Configuration details"
            },
            "uptime": {
                "tool": "Uptime monitoring tool",
                "checks": ["Check 1", "Check 2"],
                "configuration": "Configuration details"
            },
            "user_experience": {
                "tool": "User experience monitoring tool",
                "metrics": ["Metric 1", "Metric 2"],
                "configuration": "Configuration details"
            },
            "resource_monitoring": {
                "tool": "Resource monitoring tool",
                "resources": ["Resource 1", "Resource 2"],
                "configuration": "Configuration details"
            },
            "security_monitoring": {
                "tool": "Security monitoring tool",
                "capabilities": ["Capability 1", "Capability 2"],
                "configuration": "Configuration details"
            },
            "alerting": {
                "tool": "Alerting tool",
                "policies": ["Policy 1", "Policy 2"],
                "channels": ["Channel 1", "Channel 2"],
                "configuration": "Configuration details"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define monitoring setup, using default structure")
            return monitoring_structure
        
        return result
