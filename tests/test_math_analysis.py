import sys
import os
import asyncio
from langchain.schema import HumanMessage, SystemMessage

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.math_analysis import MathematicalAnalyzer, AnalysisInput
from src.backend.prompt_templates import MathAnalysisPrompts

async def test_analyzer(verify_with_local: bool = False, company_context: dict = None):
    """
    Test the analyzer with optional local verification
    
    Args:
        verify_with_local (bool): Whether to verify Groq results with local model
        company_context (dict): Additional company context for verification
    """
    providers = ["groq"]
    
    # Default company context if none provided
    default_company_context = {
        "industry": "Financial Services",
        "company_size": "Medium Enterprise (500-1000 employees)",
        "regulatory_requirements": ["SOX", "GDPR", "PCI-DSS"],
        "business_priorities": {
            "cost_reduction": 8,  # Scale 1-10
            "quality_improvement": 9,
            "customer_satisfaction": 9,
            "compliance": 10
        },
        "department_context": {
            "operations": {
                "current_workload": "High",
                "staff_expertise": "Advanced",
                "tech_adoption_rate": "Medium"
            },
            "finance": {
                "budget_constraints": "Moderate",
                "automation_budget": "Available",
                "risk_tolerance": "Low"
            },
            "customer_service": {
                "satisfaction_score": 8.5,
                "response_time_sla": "4 hours",
                "team_capacity": "Stretched"
            }
        }
    }
    
    company_context = company_context or default_company_context
    
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
        target_variables=["efficiency", "quality", "automation_potential", "resource_optimization"],
        company_context=company_context  # Add company context to input
    )
    
    for provider in providers:
        print(f"\nTesting with {provider}:")
        try:
            analyzer = MathematicalAnalyzer(llm_provider=provider)
            
            # Get initial analysis from Groq
            result = await analyzer.analyze_cost_benefit(test_data)
            groq_analysis = result.generations[0][0].text if hasattr(result, 'generations') else result
            print(f"\nGroq Analysis:")
            print(groq_analysis)
            print(50*"-")
            
            # Optional local verification with full context
            if verify_with_local:
                print("\nVerifying with local model (including full context)...")
                local_analyzer = MathematicalAnalyzer(llm_provider="ollama")
                local_result = await local_analyzer.verify_analysis(
                    original_analysis=groq_analysis,
                    full_data=test_data,
                    company_context=company_context
                )
                print("\nLocal Verification Results:")
                print(local_result.generations[0][0].text)
            
        except Exception as e:
            print(f"Error with {provider}: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage:
    # Without local verification:
    # asyncio.run(test_analyzer())
    
    # With local verification:
    asyncio.run(test_analyzer(verify_with_local=True))
    
    # With custom company context:
    # custom_context = {...}  # Define custom company context
    # asyncio.run(test_analyzer(verify_with_local=True, company_context=custom_context)) 