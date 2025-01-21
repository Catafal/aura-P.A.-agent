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

async def extract_process_data_from_survey(survey_data: pd.DataFrame, process_name: str) -> Dict[str, Any]:
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

Here is the survey data to convert:

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
    "automation": {{"feasibility_rating": 65, "potential_savings": 0.6}}  # feasibility_rating must be integer 1-100
 }},
 "process_context": {{
    "description": "Process description",
    "systems": ["System 1"],
    "challenges": ["Challenge 1"]
 }},
 "company_context": {{
    "industry": "Industry name",
    "company_size": "Size",
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
        systems=process_row['current_systems_used']
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

async def run_math_analysis_test(survey_data: pd.DataFrame, process_name: str, verify_with_local: bool = False):
    """Run the mathematical analysis test using survey data"""
    
    # Extract structured data from survey
    process_data = await extract_process_data_from_survey(survey_data, process_name)
    
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

async def run_example_test(survey_data: pd.DataFrame, process_name: str):
    """Run the example test using survey data"""
    if not os.path.exists("tests/data/synthetic_kpi_data.csv"):
        data_generator = KPIDataGenerator()
        await data_generator.generate_and_save_data()
    
    data = pd.read_csv("tests/data/synthetic_kpi_data.csv")
    predictor = KPIPredictor()
    
    # Extract process data from survey
    process_data = await extract_process_data_from_survey(survey_data, process_name)
    
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
        prediction = await predictor.predict_improvement(
            category, analysis, process_data['process_steps'], process_data['company_context']
        )
        predictions.append(prediction)
    
    return {
        "process_data": process_data,
        "analysis": analysis,
        "predictions": predictions
    }

def save_combined_report(math_results: dict, example_results: dict, output_path: str = "reports/combined_analysis.md"):
    """Save combined analysis results to a markdown file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# Combined Process Analysis Report
Generated on: {timestamp}

## Process Information
### Process Overview
{math_results['process_data']['process_context'].get('description', '')}

### Process Steps:
{chr(10).join(f'1. {step}' for step in math_results['process_data']['process_steps'])}

### Current Systems:
{math_results['process_data']['process_context'].get('systems', 'No systems information available')}

### Main Challenges:
{math_results['process_data']['process_context'].get('challenges', 'No challenges information available')}

## Part 1: Mathematical Analysis Results
### Current Metrics:
{chr(10).join(f'- **{k}**: {v}' for k, v in math_results['process_data']['metrics'].items())}

### Primary Analysis:
{math_results['primary_analysis']}

{f'''### Verification Analysis:
{math_results.get('verification_analysis', 'No verification analysis performed')}''' if 'verification_analysis' in math_results else ''}

## Part 2: KPI Prediction Results
### Company Context:
{chr(10).join(f'- **{k}**: {v}' for k, v in example_results['process_data']['company_context'].items())}

### Analysis Results:
- **Automation Potential**: {example_results['analysis'].automation_potential:.2f}
- **AI Applicability**: {example_results['analysis'].ai_applicability:.2f}
- **Process Complexity**: {example_results['analysis'].complexity_score:.2f}

### KPI Predictions:
"""
    
    for pred in example_results['predictions']:
        content += f"""#### {pred.category.value.replace('_', ' ').title()}
- **Current Value**: {pred.current_value:.2f}
- **Predicted Improvement**: {pred.predicted_improvement:.1f}%
- **ROI Estimate**: {pred.roi_estimate:.1f}%
- **Implementation Time**: {pred.implementation_time} weeks
- **Confidence Score**: {pred.confidence:.2f}

**Detailed Analysis**:
{pred.explanation}

---

"""

    # Add appendix with raw data
    content += """
## Appendix: Raw Data Analysis
### Survey Data Metrics:
```python
"""
    content += str(math_results['process_data']['metrics'])
    content += """
```

### Process Context:
```python
"""
    content += str(math_results['process_data']['process_context'])
    content += """
```

### Company Context:
```python
"""
    content += str(math_results['process_data']['company_context'])
    content += """
```
"""
    
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write(content)
    
    print(f"\nCombined analysis report saved to: {output_path}")

async def main():
    try:
        # Load survey data
        survey_data = pd.read_csv("tests/data/law-firm-survey.csv")
        process_name = "Legal Document Review"  # We can analyze any process from the survey
        
        print(f"\nAnalyzing process: {process_name}")
        print("\nRunning Mathematical Analysis Test...")
        math_results = await run_math_analysis_test(survey_data, process_name, verify_with_local=True)
        
        print("\nRunning Example Test...")
        example_results = await run_example_test(survey_data, process_name)
        
        print("\nGenerating Combined Report...")
        save_combined_report(math_results, example_results)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 