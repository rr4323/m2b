# AGENTS OVERVIEW

## Agent-Based Architecture

This project uses a modular, agent-based architecture. Each agent is responsible for a specific phase in the SaaS Cloner workflow. All agents inherit from a unified `BaseAgent` interface and are designed to be composed into flexible, automated pipelines.

### List of Agents

| Agent Name              | Description                                               | Example Output Path        |
|-------------------------|----------------------------------------------------------|---------------------------|
| AnalyticsAgent          | Sets up analytics, dashboards, feedback collection       | `output/analytics/`       |
| BackendAgent            | Develops backend code and API                            | `output/backend/`         |
| DeployAgent             | Handles deployment to cloud                              | `output/deploy/`          |
| DesignAgent             | Generates UI/UX designs and style guides                 | `output/design/`          |
| DevOpsAgent             | Sets up infrastructure and CI/CD                         | `output/devops/`          |
| FeedbackAgent         | Monitors reviews and triggers workflow iterations         | `output/feedback/`         |
| FrontendAgent           | Generates frontend code                                  | `output/frontend/`        |
| GapAnalysisAgent        | Identifies gaps in features, market, UX                  | `output/gap_analysis/`    |
| IterateAgent          | Launches improved SaaS clone versions                    | `output/iterate/`          |
| KnowledgeGraphAgent     | Builds and queries SaaS knowledge graph                  | `output/knowledge_graph/` |
| LLMAgent                | Integrates LLM/AI features                              | `output/llm/`             |
| MarketDiscoveryAgent    | Discovers trending SaaS products                        | `output/market_discovery/`|
| MarketingAgent          | Generates marketing materials and strategies             | `output/marketing/`       |
| ProductBlueprintAgent   | Creates improved product blueprints                      | `output/blueprint/`       |
| TestAgent               | Generates and runs tests                                 | `output/test/`            |

### Adding a New Agent

1. Inherit from `BaseAgent` in a new file in `agents/`.
2. Implement the `async run(self, input_data: Dict[str, Any]) -> Dict[str, Any]` method.
3. Write outputs to a designated directory and return paths in the result.
4. Document the agent in this overview.

### Example Agent Input/Output

```python
# Example for FrontendAgent
input_data = {
    "product_blueprint": {...},
    "design": {...},
    "_agent_context": "frontend"
}
result = await frontend_agent.run(input_data)
print(result)
# {'frontend_result': {...}, 'output_path': 'output/frontend/'}
