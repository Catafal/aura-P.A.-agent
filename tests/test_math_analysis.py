import sys
import os
import asyncio
from langchain.schema import HumanMessage, SystemMessage

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.math_analysis import MathematicalAnalyzer, AnalysisInput
from src.backend.prompt_templates import MathAnalysisPrompts

async def test_analyzer():
    # Test with different providers
    providers = ["ollama", "groq"] 
    
    test_data = AnalysisInput(
        metrics={
            "process_time": 120,
            "error_rate": 0.05,
            "cost_per_unit": 50,
            "process_actions": {
                "steps": [
                    "Data input validation",
                    "Processing calculation",
                    "Quality check",
                    "Report generation"
                ],
                "duration_per_step": [15, 45, 30, 30]  # in minutes
            },
            "human_resources": {
                "max_people_involved": 3,
                "roles": ["operator", "supervisor", "quality checker"]
            },
            "frequency": {
                "daily_repetitions": 24,
                "peak_hours": [10, 14, 16]
            },
            "error_metrics": {
                "error_rate": 0.05,
                "error_impact": 7,  # Scale 1-10
                "error_types": ["data entry", "calculation", "reporting"]
            },
            "impact_assessment": {
                "importance_rating": 8,  # Scale 1-10
                "affected_departments": ["operations", "finance", "customer service"]
            },
            "automation": {
                "feasibility_rating": 7,  # Scale 1-10
                "potential_savings": 0.6  # 60% potential reduction in process time
            }
        },
        target_variables=["efficiency", "quality", "automation_potential", "resource_optimization"]
    )
    
    for provider in providers:
        print(f"\nTesting with {provider}:")
        try:
            analyzer = MathematicalAnalyzer(llm_provider=provider)
            
           
            cost_benefit_prompt = MathAnalysisPrompts.cost_benefit_prompt(test_data.metrics)
            
            messages = [
                SystemMessage(content="You are a mathematical analysis assistant that provides responses in JSON format."),
                HumanMessage(content=cost_benefit_prompt)
            ]
            
            # Call the LLM with proper async handling
            result = await analyzer.analyze_cost_benefit(test_data)
            print(f"Result: {result.generations[0][0].text if hasattr(result, 'generations') else result}")
            
        except Exception as e:
            print(f"Error with {provider}: {str(e)}")
            raise  # Re-raise to see full traceback

if __name__ == "__main__":
    asyncio.run(test_analyzer()) 