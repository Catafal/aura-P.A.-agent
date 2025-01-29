import sys
import os
import asyncio
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, SystemMessage

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.model.math_analysis import MathematicalAnalyzer, AnalysisInput, ProcessActions, HumanResources, Frequency, ErrorMetrics, ImpactAssessment, Automation
from src.backend.kpi.predictor import KPIPredictor
from src.backend.kpi.types import KPICategory
from src.backend.kpi.data_generator import KPIDataGenerator
from src.backend.model.prompt_templates import MathAnalysisPrompts
from src.backend.report_converter import process_reports
from src.backend.survey_handler import SurveyProcessor
from src.backend.database.company_db import CompanyDatabase

async def extract_process_data_from_survey(survey_data: pd.DataFrame, process_name: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
    """Use LLM to extract and structure process data from survey responses"""
    process_row = survey_data[survey_data['process_name'] == process_name].iloc[0]
    
    # Create a structured prompt for the LLM
    prompt = """You are a Python dictionary generator. Your task is to convert survey data into a Python dictionary.
Rules:
1. Output ONLY the dictionary
2. NO explanations
3. NO markdown
4. NO thinking out loud
5. Proper Python syntax
6. Convert percentages to decimals
7. Use correct types:
   - feasibility_rating must be an integer (1-100)
   - potential_savings must be a float (0.0-1.0)

Company Context:
Name: {company_name}
Industry: {industry}
Size: {size}
Location: {location}
Description: {description}

Process Data:
Process: {name}
Description: {desc}
Time: {time} minutes
People: {people}
Frequency: {freq} times per day
Error Rate: {err_rate}%
Error Impact: {err_impact}/10
Business Importance: {bus_imp}/10
Automation Potential: {auto_pot}%
Challenges: {challenges}
Systems: {systems}

Return this EXACT dictionary structure with the survey data (no other text):

{{"process_steps": ["Step 1"],
 "metrics": {{
    "process_actions": {{"steps": ["Step 1"], "duration_per_step": [60]}},
    "human_resources": {{"max_people_involved": 3, "roles": ["Role 1"]}},
    "frequency": {{"daily_repetitions": 5, "peak_hours": [9, 10, 11]}},
    "error_metrics": {{"error_rate": 0.08, "error_impact": 8, "error_types": ["Type 1"]}},
    "impact_assessment": {{"importance_rating": 9, "affected_departments": ["Dept 1"]}},
    "automation": {{"feasibility_rating": 65, "potential_savings": 0.6}}
 }},
 "process_context": {{
    "description": "Process description",
    "systems": ["System 1"],
    "challenges": ["Challenge 1"]
 }},
 "company_context": {{
    "industry": "{industry}",
    "company_size": "{size}",
    "company_name": "{company_name}",
    "company_location": "{location}",
    "company_description": "{description}",
    "regulatory_requirements": ["Req 1"],
    "business_priorities": {{"efficiency": 8, "quality": 9, "compliance": 10}}
 }}}}""".format(
        name=process_row['process_name'],
        desc=process_row['process_description'],
        time=process_row['total_time_minutes'],
        people=process_row['people_involved'],
        freq=process_row['daily_frequency'],
        err_rate=process_row['error_rate_percentage'],
        err_impact=process_row['error_impact_rating'],
        bus_imp=process_row['business_importance'],
        auto_pot=process_row['automation_potential'],
        challenges=process_row['main_challenges'],
        systems=process_row['current_systems_used'],
        company_name=company_data.get('company_name', 'Unknown'),
        industry=company_data.get('company_industry', 'Unknown'),
        size=company_data.get('company_size', 'Unknown'),
        location=company_data.get('company_location', 'Unknown'),
        description=company_data.get('company_description', 'Unknown')
    )

    # Use Ollama with phi4 model
    llm = OllamaLLM(model="phi4:latest")
    
    # Get the structured data
    response = await llm.agenerate([prompt])
    try:
        # Clean up the response
        response_text = response.generations[0][0].text.strip()
        
        # Try to find the dictionary part
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        
        if start_idx < 0 or end_idx <= start_idx:
            # If we can't find valid JSON boundaries, try to extract from markdown
            if "```python" in response_text:
                response_text = response_text.split("```python")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
            
            # Try to find JSON boundaries again
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx]
        else:
            raise ValueError("Could not find valid dictionary in response")
        
        # Try to evaluate the dictionary
        structured_data = eval(response_text)
        
        # Validate the structure
        required_keys = ["process_steps", "metrics", "process_context", "company_context"]
        if not all(key in structured_data for key in required_keys):
            raise ValueError("Missing required keys in response")
            
        required_metrics = ["process_actions", "human_resources", "frequency", "error_metrics", "impact_assessment", "automation"]
        if not all(key in structured_data["metrics"] for key in required_metrics):
            raise ValueError("Missing required metrics in response")
            
    except Exception as e:
        print(f"Error parsing LLM response: {str(e)}")
        print("Raw response:", response.generations[0][0].text)
        raise
    
    # Convert the extracted data into proper class instances
    metrics = structured_data['metrics']
    metrics['process_actions'] = ProcessActions(**metrics['process_actions'])
    metrics['human_resources'] = HumanResources(**metrics['human_resources'])
    metrics['frequency'] = Frequency(**metrics['frequency'])
    metrics['error_metrics'] = ErrorMetrics(**metrics['error_metrics'])
    metrics['impact_assessment'] = ImpactAssessment(**metrics['impact_assessment'])
    metrics['automation'] = Automation(**metrics['automation'])
    
    structured_data['metrics'] = metrics
    return structured_data

async def run_math_analysis_test(survey_data: pd.DataFrame, process_name: str, company_context: Dict = None, verify_with_local: bool = False):
    """Run the mathematical analysis test using survey data"""
    
    # Extract structured data from survey
    process_data = await extract_process_data_from_survey(survey_data, process_name, company_context or {})
    
    test_data = AnalysisInput(
        metrics=process_data['metrics'],
        target_variables=["efficiency", "quality", "automation_potential", "resource_optimization"],
        company_context=process_data['company_context']
    )
    
    # Use deepseek for both primary and verification analysis
    analyzer = MathematicalAnalyzer(llm_provider="ollama")
    result = await analyzer.analyze_cost_benefit(test_data)
    primary_analysis = result.generations[0][0].text if hasattr(result, 'generations') else result
    
    if verify_with_local:
        # Use a different prompt template for verification to get a fresh perspective
        local_result = await analyzer.verify_analysis(
            original_analysis=primary_analysis,
            full_data=test_data,
            company_context=process_data['company_context']
        )
        return {
            "process_data": process_data,
            "primary_analysis": primary_analysis,
            "verification_analysis": local_result.generations[0][0].text
        }
    
    return {
        "process_data": process_data,
        "primary_analysis": primary_analysis
    }

async def run_example_test(survey_data: pd.DataFrame, process_name: str, company_context: Dict = None):
    """Run the example test using survey data"""
    if not os.path.exists("/Volumes/970Evo Plus/GitHub/aura-P.A.-agent/tests/data/synthetic_kpi_data.csv"):
        data_generator = KPIDataGenerator()
        await data_generator.generate_and_save_data()
    
    data = pd.read_csv("/Volumes/970Evo Plus/GitHub/aura-P.A.-agent/tests/data/synthetic_kpi_data.csv")
    predictor = KPIPredictor()
    
    # Extract process data from survey
    process_data = await extract_process_data_from_survey(survey_data, process_name, company_context or {})
    
    try:
        analysis = await predictor.analyze_process(
            process_steps=process_data['process_steps'],
            company_context=process_data['company_context']
        )
        
        categories = [
            KPICategory.TIME_REDUCTION,
            KPICategory.COST_SAVINGS,
            KPICategory.ERROR_REDUCTION
        ]
        
        predictions = []
        for category in categories:
            try:
                prediction = await predictor.predict_improvement(
                    category, analysis, process_data['process_steps'], process_data['company_context']
                )
                
                # Extract JSON from LLM response if needed
                if isinstance(prediction, str):
                    import json
                    import re
                    
                    # Find JSON pattern in the response
                    json_match = re.search(r'\{[\s\S]*\}', prediction)
                    if json_match:
                        try:
                            prediction = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            print(f"Warning: Could not parse JSON from response for {category}")
                            continue
                
                # Clean up the prediction response
                if hasattr(prediction, 'model_dump'):
                    prediction = prediction.model_dump()
                
                predictions.append(prediction)
                
            except Exception as e:
                print(f"Warning: Failed to generate prediction for {category}: {str(e)}")
                # Add a placeholder prediction
                predictions.append({
                    "category": category.value,
                    "current_value": 0.0,
                    "predicted_improvement": 0.0,
                    "confidence": 0.0,
                    "implementation_time": 0,
                    "roi_estimate": 0.0,
                    "explanation": f"Failed to generate prediction: {str(e)}"
                })
        
        return {
            "process_data": process_data,
            "analysis": analysis,
            "predictions": predictions
        }
    except Exception as e:
        print(f"Warning: Analysis failed for process '{process_name}': {str(e)}")
        return {
            "process_data": process_data,
            "analysis": {
                "automation_potential": 0.0,
                "ai_applicability": 0.0,
                "complexity_score": 0.0
            },
            "predictions": []
        }

def save_combined_report(math_results: dict, example_results: dict, output_path: str = "reports/combined_analysis.md"):
    """Save combined analysis results to a markdown file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# Combined Process Analysis Report
Generated on: {timestamp}

## Process Information
### Process Overview
{math_results.get('process_data', {}).get('process_context', {}).get('description', 'No description available')}

### Process Steps:
{chr(10).join(f'1. {step}' for step in math_results.get('process_data', {}).get('process_steps', ['No steps available']))}

### Current Systems:
{chr(10).join(str(system) for system in math_results.get('process_data', {}).get('process_context', {}).get('systems', ['No systems information available']))}

### Main Challenges:
{chr(10).join(str(challenge) for challenge in math_results.get('process_data', {}).get('process_context', {}).get('challenges', ['No challenges information available']))}

## Part 1: Mathematical Analysis Results
### Current Metrics:
"""
        # Safely handle metrics
        metrics = math_results.get('process_data', {}).get('metrics', {})
        for k, v in metrics.items():
            if isinstance(v, (dict, list)):
                content += f"- **{k}**: {str(v)}\n"
            else:
                content += f"- **{k}**: {v}\n"

        content += f"""
### Primary Analysis:
{math_results.get('primary_analysis', 'No primary analysis available')}

"""
        if 'verification_analysis' in math_results:
            content += f"""### Verification Analysis:
{math_results['verification_analysis']}

"""

        content += """## Part 2: KPI Prediction Results
### Company Context:
"""
        # Safely handle company context
        company_context = example_results.get('process_data', {}).get('company_context', {})
        for k, v in company_context.items():
            content += f"- **{k}**: {str(v)}\n"

        # Safely handle analysis results
        analysis = example_results.get('analysis', {})
        content += f"""
### Analysis Results:
- **Automation Potential**: {getattr(analysis, 'automation_potential', 0.0):.2f}
- **AI Applicability**: {getattr(analysis, 'ai_applicability', 0.0):.2f}
- **Process Complexity**: {getattr(analysis, 'complexity_score', 0.0):.2f}

### KPI Predictions:
"""
        
        # Safely handle predictions
        for pred in example_results.get('predictions', []):
            if isinstance(pred, dict):
                content += f"""#### {pred.get('category', 'Unknown').replace('_', ' ').title()}
- **Current Value**: {pred.get('current_value', 0.0):.2f}
- **Predicted Improvement**: {pred.get('predicted_improvement', 0.0):.1f}%
- **ROI Estimate**: {pred.get('roi_estimate', 0.0):.1f}%
- **Implementation Time**: {pred.get('implementation_time', 0)} weeks
- **Confidence Score**: {pred.get('confidence', 0.0):.2f}

**Detailed Analysis**:
{pred.get('explanation', 'No explanation available')}

---

"""

        # Create reports directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nCombined analysis report saved to: {output_path}")
        
    except Exception as e:
        print(f"Error saving report: {str(e)}")
        # Create a minimal valid report
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(f"""# Combined Process Analysis Report
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Error generating full report: {str(e)}

## Basic Process Information
Process name: {math_results.get('process_data', {}).get('process_steps', ['Unknown'])[0]}
""")

async def main():
    try:
        # Initialize company database
        company_db = CompanyDatabase()
        
        # Get all available companies
        print("\nFetching available companies...")
        companies = await company_db.get_all_companies()
        
        if not companies:
            print("No companies found in the database.")
            return
            
        # Display companies
        print("\nAvailable companies:")
        for i, company in enumerate(companies, 1):
            print(f"{i}. {company['company_name']} (ID: {company['id']})")
            
        # Get user selection
        while True:
            try:
                selection = input("\nEnter the number of the company to analyze (or 'q' to quit): ")
                if selection.lower() == 'q':
                    return
                    
                idx = int(selection) - 1
                if 0 <= idx < len(companies):
                    company_id = companies[idx]['id']
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Initialize survey processor with selected company
        processor = SurveyProcessor(company_id)
        
        # Load data
        print(f"\nLoading data for {companies[idx]['company_name']}...")
        await processor.load_data()
        survey_data = processor.survey_data
        company_context = processor.company_context
        
        if survey_data is None or company_context is None:
            print("Error: Could not load survey data or company context.")
            return
            
        print("\nAnalyzing all processes from survey...")
        
        # Get unique process names from survey
        process_names = survey_data['process_name'].unique()
        
        # Create directory in desktop with company name
        company_name = company_context['company_name'].replace(' ', '_').lower()
        desktop_path = os.path.expanduser("~/Desktop")
        reports_dir = os.path.join(desktop_path, f"{company_name}_analysis_reports")
        process_reports_dir = os.path.join(reports_dir, "process_analysis")
        os.makedirs(process_reports_dir, exist_ok=True)
        
        # Create a summary report
        summary_content = "# Process Analysis Summary Report\n\n"
        summary_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        summary_content += f"Company: {company_context['company_name']}\n"
        summary_content += f"Industry: {company_context['industry']}\n"
        summary_content += f"Size: {company_context['company_size']}\n\n"
        summary_content += f"Total Processes Analyzed: {len(process_names)}\n\n"
        
        # Analyze each process
        for process_name in process_names:
            print(f"\nAnalyzing process: {process_name}")
            
            try:
                print("Running Mathematical Analysis Test...")
                math_results = await run_math_analysis_test(survey_data, process_name, company_context, verify_with_local=True)
                
                print("Running Example Test...")
                example_results = await run_example_test(survey_data, process_name, company_context)
                
                print("Generating Process Report...")
                # Save individual process report
                report_path = os.path.join(process_reports_dir, f"{process_name.lower().replace(' ', '_')}_analysis.md")
                save_combined_report(math_results, example_results, output_path=report_path)
                
                # Add to summary - safely handle different object types
                summary_content += f"## {process_name}\n"
                
                # Safely access analysis attributes
                analysis = example_results.get('analysis', {})
                automation_potential = getattr(analysis, 'automation_potential', 0.0) if hasattr(analysis, 'automation_potential') else analysis.get('automation_potential', 0.0)
                ai_applicability = getattr(analysis, 'ai_applicability', 0.0) if hasattr(analysis, 'ai_applicability') else analysis.get('ai_applicability', 0.0)
                complexity_score = getattr(analysis, 'complexity_score', 0.0) if hasattr(analysis, 'complexity_score') else analysis.get('complexity_score', 0.0)
                
                summary_content += f"- Automation Potential: {automation_potential:.2f}\n"
                summary_content += f"- AI Applicability: {ai_applicability:.2f}\n"
                summary_content += f"- Process Complexity: {complexity_score:.2f}\n"
                
                # Add KPI predictions summary - handle both dict and object types
                summary_content += "### Key Predictions:\n"
                for pred in example_results.get('predictions', []):
                    if isinstance(pred, dict):
                        category = pred.get('category', 'Unknown')
                        improvement = pred.get('predicted_improvement', 0.0)
                    else:
                        # Handle PredictionResult object
                        category = getattr(pred, 'category', 'Unknown')
                        if hasattr(category, 'value'):  # If category is an enum
                            category = category.value
                        improvement = getattr(pred, 'predicted_improvement', 0.0)
                    
                    summary_content += f"- {category.replace('_', ' ').title()}: {improvement:.1f}% improvement\n"
                
                summary_content += "\n---\n\n"
                
            except Exception as e:
                print(f"Error analyzing process '{process_name}': {str(e)}")
                summary_content += f"## {process_name}\n"
                summary_content += f"Error during analysis: {str(e)}\n\n---\n\n"
        
        # Save summary report
        summary_path = os.path.join(reports_dir, "analysis_summary.md")
        with open(summary_path, "w", encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"\nAnalysis complete!")
        print(f"Individual process reports saved in: {process_reports_dir}")
        print(f"Summary report saved as: {summary_path}")
        
        # convert the md files to latex
        await process_reports()
        
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 