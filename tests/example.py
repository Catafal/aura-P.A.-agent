import sys
import os
import asyncio
import pandas as pd
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.kpi.predictor import KPIPredictor
from src.backend.kpi.types import KPICategory
from src.backend.kpi.data_generator import KPIDataGenerator

def save_analysis_to_markdown(process_steps: list, company_context: dict, 
                            analysis: dict, predictions: list, 
                            output_path: str = "analysis_results.md"):
    """Save analysis results to a markdown file"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# Process Automation Analysis Report
Generated on: {timestamp}

## Process Overview
### Steps:
{chr(10).join(f"1. {step}" for step in process_steps)}

### Company Context:
{chr(10).join(f"- **{k}**: {v}" for k, v in company_context.items())}

## Process Analysis
- **Automation Potential**: {analysis.automation_potential:.2f}
- **AI Applicability**: {analysis.ai_applicability:.2f}
- **Process Complexity**: {analysis.complexity_score:.2f}

### Current Metrics:
{chr(10).join(f"- **{k}**: {v:.2f}" for k, v in analysis.current_metrics.items())}

### Identified Bottlenecks:
{chr(10).join(f"- {bottleneck}" for bottleneck in analysis.bottlenecks)}

## Improvement Predictions

"""
    
    # Add each category's prediction
    for pred in predictions:
        content += f"""### {pred.category.value.replace('_', ' ').title()}
- **Current Value**: {pred.current_value:.2f}
- **Predicted Improvement**: {pred.predicted_improvement:.1f}%
- **ROI Estimate**: {pred.roi_estimate:.1f}%
- **Implementation Time**: {pred.implementation_time} weeks
- **Confidence Score**: {pred.confidence:.2f}

#### Detailed Analysis:
{pred.explanation}

---

"""
    
    # Save to file
    with open(output_path, "w") as f:
        f.write(content)
    
    print(f"\nAnalysis saved to: {output_path}")

async def generate_initial_data():
    """Generate initial dataset if it doesn't exist"""
    data_generator = KPIDataGenerator()
    await data_generator.generate_and_save_data()

async def main():
    try:
        if not os.path.exists("/Volumes/970Evo Plus/GitHub/aura-P.A.-agent/tests/data/synthetic_kpi_data.csv"):
            # First, ensure we have our synthetic data
            print("\nGenerating synthetic data...")
            await generate_initial_data()
            print("Synthetic data generation complete!")
        
        # Load the synthetic data
        data = pd.read_csv("/Volumes/970Evo Plus/GitHub/aura-P.A.-agent/tests/data/synthetic_kpi_data.csv")
        
        print(f"Loaded {len(data)} synthetic data points")

        # Initialize predictor
        predictor = KPIPredictor()
        
        # Example law firm contract review process
        process_steps = [
            "Receive contract from client",
            "Initial document review and categorization",
            "Legal analysis of key terms and conditions",
            "Risk assessment and flagging issues",
            "Draft suggested modifications",
            "Internal review by senior attorney",
            "Client consultation on findings",
            "Prepare summary report and recommendations"
        ]
        
        # Law firm context
        company_context = {
            "industry": "Legal Services",
            "company_size": "Medium",
            "current_tech_stack": "MS Office, iManage DMS, Basic Contract Analysis Tools",
            "automation_experience": "Limited",
            "annual_case_volume": "500"
        }
        
        # Analyze process
        analysis = await predictor.analyze_process(process_steps, company_context)
        
        # Predict improvements for different KPIs
        categories = [
            KPICategory.TIME_REDUCTION,
            KPICategory.COST_SAVINGS,
            KPICategory.ERROR_REDUCTION
        ]
        
        predictions = []
        for category in categories:
            prediction = await predictor.predict_improvement(
                category, analysis, process_steps, company_context
            )
            predictions.append(prediction)
        
        # Save results to markdown
        save_analysis_to_markdown(
            process_steps=process_steps,
            company_context=company_context,
            analysis=analysis,
            predictions=predictions,
            output_path="analysis_results.md"
        )
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())