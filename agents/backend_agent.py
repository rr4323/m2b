"""
Backend Agent for creating the backend API and database schema.
"""
import logging
import json
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from utils.openai_utils import generate_json_completion, generate_completion

class BackendAgent(BaseAgent):
    """Agent for creating the backend API and database schema based on product specs."""
    
    def __init__(self):
        """Initialize the Backend Agent."""
        super().__init__(
            name="Backend Agent",
            description="Creates the backend API and database schema based on product specs"
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the backend development process.
        
        Args:
            input_data (Dict[str, Any]): Input data containing product blueprint
                
        Returns:
            Dict[str, Any]: Backend implementation details
        """
        self.log_info("Starting backend development process")
        
        blueprint = input_data.get("blueprint", {})
        
        if not blueprint:
            self.log_error("No product blueprint provided for backend development")
            return {"error": "No product blueprint provided for backend development"}
        
        product_name = blueprint.get("product_name", "")
        
        self.log_info(f"Building backend for: {product_name}")
        
        # Step 1: Define backend architecture
        architecture = await self._define_architecture(blueprint)
        
        # Step 2: Create database schema
        db_schema = await self._create_database_schema(blueprint)
        
        # Step 3: Define API endpoints
        api_endpoints = await self._define_api_endpoints(blueprint, db_schema)
        
        # Step 4: Define authentication and authorization strategy
        auth_strategy = await self._define_auth_strategy(blueprint)
        
        # Step 5: Generate project structure
        project_structure = await self._generate_project_structure(
            architecture, 
            db_schema, 
            api_endpoints, 
            auth_strategy
        )
        
        return {
            "product_name": product_name,
            "architecture": architecture,
            "db_schema": db_schema,
            "api_endpoints": api_endpoints,
            "auth_strategy": auth_strategy,
            "project_structure": project_structure
        }
    
    async def _define_architecture(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define the backend architecture.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            
        Returns:
            Dict[str, Any]: Backend architecture specification
        """
        self.log_info("Defining backend architecture")
        
        tech_stack = blueprint.get("stack", {})
        backend_tech = tech_stack.get("backend", {})
        db_tech = tech_stack.get("database_storage", {})
        
        system_message = (
            "You are a backend architect specializing in SaaS applications. "
            "Define a comprehensive backend architecture for the product based "
            "on the specified technology stack and product requirements. The "
            "architecture should be scalable, secure, and maintainable."
        )
        
        prompt = (
            f"Define a backend architecture for the product with these specifications:\n\n"
            f"Backend Tech Stack: {json.dumps(backend_tech)}\n\n"
            f"Database Tech Stack: {json.dumps(db_tech)}\n\n"
            f"The architecture should include:\n"
            f"1. Framework and library choices\n"
            f"2. Project structure\n"
            f"3. Service organization\n"
            f"4. Database design approach\n"
            f"5. Authentication and authorization strategy\n"
            f"6. API design principles\n"
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
            "database": {
                "type": "Database type",
                "version": "Version",
                "justification": "Justification for this choice"
            },
            "project_organization": {
                "structure": "Structure description",
                "patterns": ["Pattern 1", "Pattern 2"]
            },
            "service_architecture": {
                "approach": "Approach description",
                "organization": "Organization description"
            },
            "auth_strategy": {
                "solution": "Solution name",
                "approach": "Approach description"
            },
            "api_design": {
                "style": "API style",
                "principles": ["Principle 1", "Principle 2"]
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
            self.log_error("Failed to define backend architecture, using default structure")
            return architecture_structure
        
        return result
    
    async def _create_database_schema(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the database schema based on the product blueprint.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            
        Returns:
            Dict[str, Any]: Database schema
        """
        self.log_info("Creating database schema")
        
        features = blueprint.get("features", {})
        
        # Extract all features to inform schema design
        core_features = features.get("core_features", [])
        new_features = features.get("new_features", [])
        advanced_features = features.get("advanced_features", [])
        ai_powered_features = features.get("ai_powered_features", [])
        
        all_features = core_features + new_features + advanced_features + ai_powered_features
        
        system_message = (
            "You are a database architect specializing in SaaS applications. "
            "Create a comprehensive database schema for the product based on "
            "its features. Define the entities, relationships, and attributes "
            "necessary to support the product's functionality."
        )
        
        prompt = (
            f"Create a database schema based on these features:\n\n"
            f"Features:\n{str(all_features)[:2000]}...\n\n"
            f"Define the following for the database schema:\n"
            f"1. Entities/tables\n"
            f"2. Relationships between entities\n"
            f"3. Attributes/columns for each entity\n"
            f"4. Primary and foreign keys\n"
            f"5. Indexes for performance\n"
            f"6. Data types and constraints\n\n"
            f"The schema should be normalized and follow best practices for "
            f"database design in a SaaS application. Consider aspects like "
            f"multi-tenancy, user management, and audit logging."
        )
        
        schema_structure = {
            "entities": [
                {
                    "name": "users",
                    "description": "Stores user information",
                    "attributes": [
                        {
                            "name": "id",
                            "type": "UUID",
                            "constraints": ["PRIMARY KEY"]
                        },
                        {
                            "name": "email",
                            "type": "VARCHAR(255)",
                            "constraints": ["UNIQUE", "NOT NULL"]
                        }
                    ],
                    "indexes": ["email"],
                    "relationships": [
                        {
                            "entity": "profiles",
                            "type": "one-to-one",
                            "description": "Each user has one profile"
                        }
                    ]
                }
            ],
            "multi_tenancy_approach": "Approach description",
            "migration_strategy": "Strategy description"
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to create database schema, using default structure")
            return schema_structure
        
        return result
    
    async def _define_api_endpoints(
        self, 
        blueprint: Dict[str, Any],
        db_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Define API endpoints based on the product blueprint and database schema.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            db_schema (Dict[str, Any]): The database schema
            
        Returns:
            Dict[str, Any]: API endpoints specification
        """
        self.log_info("Defining API endpoints")
        
        features = blueprint.get("features", {})
        entities = db_schema.get("entities", [])
        
        # Extract all features to inform API design
        core_features = features.get("core_features", [])
        new_features = features.get("new_features", [])
        advanced_features = features.get("advanced_features", [])
        ai_powered_features = features.get("ai_powered_features", [])
        
        all_features = core_features + new_features + advanced_features + ai_powered_features
        
        system_message = (
            "You are an API designer specializing in RESTful and GraphQL APIs for "
            "SaaS applications. Define comprehensive API endpoints for the product "
            "based on its features and database schema. The API should be intuitive, "
            "consistent, and follow best practices for API design."
        )
        
        prompt = (
            f"Define API endpoints based on these features and database schema:\n\n"
            f"Features:\n{str(all_features)[:1000]}...\n\n"
            f"Database Entities:\n{str(entities)[:1000]}...\n\n"
            f"Define the following for the API:\n"
            f"1. Resource endpoints (e.g., /users, /products)\n"
            f"2. HTTP methods for each endpoint (GET, POST, PUT, DELETE)\n"
            f"3. Request parameters and body schemas\n"
            f"4. Response schemas\n"
            f"5. Authentication requirements\n"
            f"6. Rate limiting and caching directives\n\n"
            f"The API should follow RESTful principles and/or GraphQL best practices, "
            f"depending on the chosen approach."
        )
        
        api_structure = {
            "base_path": "/api/v1",
            "authentication": "JWT Bearer token",
            "resources": [
                {
                    "name": "users",
                    "path": "/users",
                    "description": "User management endpoints",
                    "endpoints": [
                        {
                            "method": "GET",
                            "path": "/",
                            "description": "List users",
                            "query_params": [
                                {
                                    "name": "page",
                                    "type": "integer",
                                    "description": "Page number for pagination"
                                }
                            ],
                            "response": {
                                "type": "array",
                                "items": "User object"
                            },
                            "auth_required": true
                        }
                    ]
                }
            ],
            "error_handling": {
                "approach": "Standard error response format",
                "error_codes": ["ERROR_CODE_1", "ERROR_CODE_2"]
            },
            "rate_limiting": {
                "approach": "Rate limiting approach",
                "limits": "Rate limits description"
            },
            "documentation": {
                "type": "Documentation type",
                "url": "Documentation URL"
            }
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define API endpoints, using default structure")
            return api_structure
        
        return result
    
    async def _define_auth_strategy(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define the authentication and authorization strategy.
        
        Args:
            blueprint (Dict[str, Any]): The product blueprint
            
        Returns:
            Dict[str, Any]: Authentication and authorization strategy
        """
        self.log_info("Defining authentication and authorization strategy")
        
        tech_stack = blueprint.get("stack", {})
        auth_tech = tech_stack.get("auth", {})
        
        system_message = (
            "You are a security architect specializing in authentication and authorization "
            "for SaaS applications. Define a comprehensive auth strategy for the product "
            "based on the specified technology stack and security requirements. The "
            "strategy should be secure, scalable, and user-friendly."
        )
        
        prompt = (
            f"Define an authentication and authorization strategy with these specifications:\n\n"
            f"Auth Tech Stack: {json.dumps(auth_tech)}\n\n"
            f"The auth strategy should include:\n"
            f"1. Authentication mechanism\n"
            f"2. User registration and login flows\n"
            f"3. Password policies and recovery processes\n"
            f"4. Session management\n"
            f"5. Role-based or attribute-based access control\n"
            f"6. API authentication\n"
            f"7. Social login integration\n"
            f"8. Multi-factor authentication\n"
            f"9. Security considerations\n\n"
            f"Justify your auth decisions and explain how they support "
            f"the product's security requirements."
        )
        
        auth_structure = {
            "authentication": {
                "mechanism": "Mechanism description",
                "implementation": "Implementation details",
                "libraries": ["Library 1", "Library 2"]
            },
            "registration": {
                "flow": "Registration flow description",
                "validation": "Validation approach"
            },
            "login": {
                "flow": "Login flow description",
                "security_measures": ["Measure 1", "Measure 2"]
            },
            "password_policy": {
                "requirements": ["Requirement 1", "Requirement 2"],
                "recovery": "Recovery process description"
            },
            "session_management": {
                "approach": "Approach description",
                "expiry": "Expiry policy"
            },
            "authorization": {
                "model": "Authorization model",
                "roles": ["Role 1", "Role 2"],
                "permissions": ["Permission 1", "Permission 2"]
            },
            "api_auth": {
                "method": "API auth method",
                "implementation": "Implementation details"
            },
            "social_login": {
                "providers": ["Provider 1", "Provider 2"],
                "implementation": "Implementation details"
            },
            "mfa": {
                "methods": ["Method 1", "Method 2"],
                "implementation": "Implementation details"
            },
            "security_considerations": ["Consideration 1", "Consideration 2"]
        }
        
        result = generate_json_completion(prompt, system_message)
        
        if not result or not isinstance(result, dict):
            self.log_error("Failed to define auth strategy, using default structure")
            return auth_structure
        
        return result
    
    async def _generate_project_structure(
        self, 
        architecture: Dict[str, Any],
        db_schema: Dict[str, Any],
        api_endpoints: Dict[str, Any],
        auth_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate the backend project structure.
        
        Args:
            architecture (Dict[str, Any]): The backend architecture
            db_schema (Dict[str, Any]): The database schema
            api_endpoints (Dict[str, Any]): The API endpoints specification
            auth_strategy (Dict[str, Any]): The authentication and authorization strategy
            
        Returns:
            Dict[str, Any]: Project structure
        """
        self.log_info("Generating project structure")
        
        framework = architecture.get("framework", {}).get("name", "").lower()
        
        # Determine appropriate structure based on framework
        base_structure = "FastAPI" if "fastapi" in framework else "Django" if "django" in framework else "Flask" if "flask" in framework else "Generic"
        
        system_message = (
            f"You are a backend architect specializing in {base_structure} applications. "
            f"Generate a comprehensive project structure for the product based on "
            f"the specified architecture, database schema, API endpoints, and "
            f"auth strategy. The structure should be organized, maintainable, "
            f"and follow best practices for {base_structure} applications."
        )
        
        prompt = (
            f"Generate a {base_structure} project structure for the product with these specifications:\n\n"
            f"Framework: {framework}\n\n"
            f"Entities: {json.dumps([entity.get('name') for entity in db_schema.get('entities', [])])}\n\n"
            f"API Resources: {json.dumps([resource.get('name') for resource in api_endpoints.get('resources', [])])}\n\n"
            f"Auth Mechanism: {auth_strategy.get('authentication', {}).get('mechanism', '')}\n\n"
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
                    "structure": self._create_default_file_structure(base_structure, db_schema, api_endpoints)
                }
        except Exception as e:
            self.log_error(f"Failed to process file tree: {e}")
            file_tree = {
                "description": result,
                "structure": self._create_default_file_structure(base_structure, db_schema, api_endpoints)
            }
        
        return file_tree
    
    def _create_default_file_structure(
        self, 
        base_structure: str, 
        db_schema: Dict[str, Any],
        api_endpoints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a default file structure based on the framework.
        
        Args:
            base_structure (str): The base framework structure
            db_schema (Dict[str, Any]): The database schema
            api_endpoints (Dict[str, Any]): The API endpoints specification
            
        Returns:
            Dict[str, Any]: Default file structure
        """
        entities = [entity.get('name') for entity in db_schema.get('entities', [])]
        resources = [resource.get('name') for resource in api_endpoints.get('resources', [])]
        
        if base_structure == "FastAPI":
            structure = {
                "app": {
                    "api": {
                        "routes": {},
                        "dependencies.py": {"description": "Dependency injection"},
                        "errors.py": {"description": "Error handling"}
                    },
                    "core": {
                        "config.py": {"description": "Application configuration"},
                        "security.py": {"description": "Security and auth"},
                        "db.py": {"description": "Database configuration"}
                    },
                    "models": {},
                    "schemas": {},
                    "services": {},
                    "main.py": {"description": "Application entry point"}
                },
                "alembic": {
                    "versions": {"description": "Database migrations"},
                    "env.py": {"description": "Alembic configuration"}
                },
                "tests": {
                    "api": {"description": "API tests"},
                    "services": {"description": "Service tests"},
                    "conftest.py": {"description": "Test configuration"}
                },
                ".env": {"description": "Environment variables"},
                "alembic.ini": {"description": "Alembic configuration"},
                "Dockerfile": {"description": "Docker configuration"},
                "docker-compose.yml": {"description": "Docker Compose configuration"},
                "requirements.txt": {"description": "Python dependencies"}
            }
            
            # Add models and schemas for each entity
            for entity in entities:
                structure["app"]["models"][f"{entity}.py"] = {"description": f"{entity} model"}
                structure["app"]["schemas"][f"{entity}.py"] = {"description": f"{entity} schema"}
            
            # Add routes for each resource
            for resource in resources:
                structure["app"]["api"]["routes"][f"{resource}.py"] = {"description": f"{resource} routes"}
                structure["app"]["services"][f"{resource}.py"] = {"description": f"{resource} service"}
                
            return structure
        elif base_structure == "Django":
            structure = {
                "project_name": {
                    "settings.py": {"description": "Project settings"},
                    "urls.py": {"description": "URL configuration"},
                    "wsgi.py": {"description": "WSGI configuration"},
                    "asgi.py": {"description": "ASGI configuration"}
                },
                "apps": {},
                "core": {
                    "utils.py": {"description": "Utility functions"},
                    "permissions.py": {"description": "Custom permissions"},
                    "exceptions.py": {"description": "Custom exceptions"}
                },
                "templates": {"description": "HTML templates"},
                "static": {"description": "Static files"},
                "media": {"description": "Media files"},
                "tests": {"description": "Test directory"},
                "manage.py": {"description": "Django management script"},
                "requirements.txt": {"description": "Python dependencies"},
                "Dockerfile": {"description": "Docker configuration"},
                "docker-compose.yml": {"description": "Docker Compose configuration"}
            }
            
            # Add app for each resource group
            resource_groups = {}
            for resource in resources:
                group = resource.split('_')[0] if '_' in resource else resource
                resource_groups[group] = True
            
            for group in resource_groups:
                structure["apps"][group] = {
                    "migrations": {"description": "Database migrations"},
                    "models.py": {"description": "Data models"},
                    "views.py": {"description": "API views"},
                    "serializers.py": {"description": "API serializers"},
                    "urls.py": {"description": "URL patterns"},
                    "admin.py": {"description": "Admin configuration"},
                    "tests.py": {"description": "Tests"}
                }
                
            return structure
        elif base_structure == "Flask":
            structure = {
                "app": {
                    "__init__.py": {"description": "Application factory"},
                    "config.py": {"description": "Application configuration"},
                    "extensions.py": {"description": "Flask extensions"},
                    "api": {
                        "__init__.py": {"description": "API package"},
                        "routes": {}
                    },
                    "models": {},
                    "schemas": {},
                    "services": {},
                    "utils": {
                        "__init__.py": {"description": "Utilities package"},
                        "errors.py": {"description": "Error handling"}
                    }
                },
                "migrations": {"description": "Database migrations"},
                "tests": {
                    "conftest.py": {"description": "Test configuration"},
                    "api": {"description": "API tests"},
                    "services": {"description": "Service tests"}
                },
                ".env": {"description": "Environment variables"},
                "wsgi.py": {"description": "WSGI entry point"},
                "requirements.txt": {"description": "Python dependencies"},
                "Dockerfile": {"description": "Docker configuration"},
                "docker-compose.yml": {"description": "Docker Compose configuration"}
            }
            
            # Add models and schemas for each entity
            for entity in entities:
                structure["app"]["models"][f"{entity}.py"] = {"description": f"{entity} model"}
                structure["app"]["schemas"][f"{entity}.py"] = {"description": f"{entity} schema"}
            
            # Add routes for each resource
            for resource in resources:
                structure["app"]["api"]["routes"][f"{resource}.py"] = {"description": f"{resource} routes"}
                structure["app"]["services"][f"{resource}.py"] = {"description": f"{resource} service"}
                
            return structure
        else:
            # Generic structure
            structure = {
                "src": {
                    "api": {
                        "routes": {},
                        "middleware": {"description": "Middleware directory"}
                    },
                    "models": {},
                    "services": {},
                    "utils": {"description": "Utility functions directory"},
                    "config": {"description": "Configuration directory"},
                    "db": {"description": "Database configuration and migrations"},
                    "app.js": {"description": "Application entry point"}
                },
                "tests": {"description": "Tests directory"},
                ".env": {"description": "Environment variables"},
                "Dockerfile": {"description": "Docker configuration"},
                "docker-compose.yml": {"description": "Docker Compose configuration"}
            }
            
            # Add models for each entity
            for entity in entities:
                structure["src"]["models"][f"{entity}.js"] = {"description": f"{entity} model"}
            
            # Add routes for each resource
            for resource in resources:
                structure["src"]["api"]["routes"][f"{resource}.js"] = {"description": f"{resource} routes"}
                structure["src"]["services"][f"{resource}.js"] = {"description": f"{resource} service"}
                
            return structure
