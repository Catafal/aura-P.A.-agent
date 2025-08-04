#!/usr/bin/env python3
"""
Basic Usage Example for Aura P.A. Agent

This example demonstrates how to use the Aura P.A. Agent for basic process analysis
without requiring a full Ollama setup. It shows the data structures and basic
functionality of the system.

Note: For full LLM-powered analysis, you'll need to set up Ollama with the phi4 model.
"""

import sys
import os
import pandas as pd
from typing import Dict, Any

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.model.math_analysis import AnalysisInput, ProcessActions, HumanResources, Frequency, ErrorMetrics, ImpactAssessment, Automation
from src.backend.kpi.types import KPICategory

def create_sample_survey_data() -> pd.DataFrame:
    """Create sample survey data for demonstration"""
    sample_data = {
        'process_name': [
            'Invoice Processing',
            'Customer Onboarding', 
            'Inventory Management'
        ],
        'process_description': [
            'Manual invoice data entry and approval workflow',
            'New customer account setup and verification process',
            'Daily inventory counting and reconciliation tasks'
        ],
        'total_time_minutes': [45, 120, 180],
        'people_involved': [3, 5, 2],
        'daily_frequency': [25, 8, 1],
        'error_rate_percentage': [8, 5, 12],
        'error_impact_rating': [7, 9, 6],
        'business_importance': [8, 9, 7],
        'automation_potential': [85, 70, 60],
        'main_challenges': [
            'Manual data entry errors, slow approval process',
            'Complex verification requirements, multiple systems',
            'Time-consuming counting, inventory discrepancies'
        ],
        'current_systems_used': [
            'Excel, Email, Accounting Software',
            'CRM, Document Management, Email',
            'Spreadsheets, Barcode Scanner, ERP'
        ]
    }
    
    return pd.DataFrame(sample_data)

def create_sample_company_context() -> Dict[str, Any]:
    """Create sample company context for demonstration"""
    return {
        'company_name': 'Sample Manufacturing Co.',
        'industry': 'Manufacturing',
        'company_size': 'Medium (100-500 employees)',
        'company_location': 'United States',
        'company_description': 'Mid-sized manufacturing company specializing in automotive parts',
        'regulatory_requirements': ['ISO 9001', 'OSHA Compliance', 'Environmental Standards'],
        'business_priorities': {
            'efficiency': 8,
            'quality': 9,
            'compliance': 10
        }
    }

def create_sample_analysis_input(process_name: str) -> AnalysisInput:
    """Create a sample AnalysisInput for demonstration"""
    
    # Sample metrics for Invoice Processing
    if process_name == 'Invoice Processing':
        metrics = {
            'process_actions': ProcessActions(
                steps=['Receive Invoice', 'Data Entry', 'Validation', 'Approval', 'Payment Processing'],
                duration_per_step=[5, 15, 10, 10, 5]
            ),
            'human_resources': HumanResources(
                max_people_involved=3,
                roles=['Data Entry Clerk', 'Supervisor', 'Finance Manager']
            ),
            'frequency': Frequency(
                daily_repetitions=25,
                peak_hours=[9, 10, 11, 14, 15]
            ),
            'error_metrics': ErrorMetrics(
                error_rate=0.08,
                error_impact=7,
                error_types=['Data Entry Errors', 'Missing Information', 'Duplicate Entries']
            ),
            'impact_assessment': ImpactAssessment(
                importance_rating=8,
                affected_departments=['Finance', 'Accounting', 'Procurement']
            ),
            'automation': Automation(
                feasibility_rating=85,
                potential_savings=0.67
            )
        }
    else:
        # Default sample metrics
        metrics = {
            'process_actions': ProcessActions(
                steps=['Step 1', 'Step 2', 'Step 3'],
                duration_per_step=[30, 60, 30]
            ),
            'human_resources': HumanResources(
                max_people_involved=2,
                roles=['Operator', 'Supervisor']
            ),
            'frequency': Frequency(
                daily_repetitions=10,
                peak_hours=[9, 10, 11]
            ),
            'error_metrics': ErrorMetrics(
                error_rate=0.05,
                error_impact=6,
                error_types=['Process Errors']
            ),
            'impact_assessment': ImpactAssessment(
                importance_rating=7,
                affected_departments=['Operations']
            ),
            'automation': Automation(
                feasibility_rating=70,
                potential_savings=0.50
            )
        }
    
    return AnalysisInput(
        metrics=metrics,
        target_variables=['efficiency', 'quality', 'automation_potential', 'resource_optimization'],
        company_context=create_sample_company_context()
    )

def demonstrate_kpi_categories():
    """Demonstrate available KPI categories"""
    print("📊 Available KPI Categories:")
    for category in KPICategory:
        print(f"   • {category.value.replace('_', ' ').title()}")
    print()

def demonstrate_data_structures():
    """Demonstrate the main data structures used in the system"""
    print("🏗️  Data Structure Examples:")
    print("\n1. Sample Survey Data:")
    survey_data = create_sample_survey_data()
    print(survey_data[['process_name', 'total_time_minutes', 'automation_potential']].to_string(index=False))
    
    print("\n2. Sample Company Context:")
    company_context = create_sample_company_context()
    for key, value in company_context.items():
        if key != 'business_priorities':
            print(f"   • {key}: {value}")
    
    print("\n3. Sample Analysis Input Structure:")
    analysis_input = create_sample_analysis_input('Invoice Processing')
    print(f"   • Target Variables: {analysis_input.target_variables}")
    print(f"   • Process Steps: {analysis_input.metrics['process_actions'].steps}")
    print(f"   • Automation Feasibility: {analysis_input.metrics['automation'].feasibility_rating}%")
    print(f"   • Potential Savings: {analysis_input.metrics['automation'].potential_savings:.1%}")
    print()

def calculate_basic_metrics(analysis_input: AnalysisInput):
    """Calculate some basic metrics without LLM"""
    print("🧮 Basic Process Metrics Calculation:")
    
    # Calculate total process time
    total_time = sum(analysis_input.metrics['process_actions'].duration_per_step)
    daily_time = total_time * analysis_input.metrics['frequency'].daily_repetitions
    people_hours = daily_time * analysis_input.metrics['human_resources'].max_people_involved / 60
    
    # Calculate potential savings
    automation_potential = analysis_input.metrics['automation'].potential_savings
    potential_time_saved = daily_time * automation_potential / 60  # hours
    
    print(f"   • Total Process Time: {total_time} minutes")
    print(f"   • Daily Process Time: {daily_time} minutes")
    print(f"   • Daily People-Hours: {people_hours:.1f} hours")
    print(f"   • Potential Time Savings: {potential_time_saved:.1f} hours/day")
    print(f"   • Error Rate: {analysis_input.metrics['error_metrics'].error_rate:.1%}")
    print(f"   • Business Impact: {analysis_input.metrics['impact_assessment'].importance_rating}/10")
    print()

def main():
    """Main demonstration function"""
    print("🚀 Aura P.A. Agent - Basic Usage Example")
    print("=" * 50)
    print()
    
    print("This example demonstrates the core data structures and basic")
    print("calculations without requiring Ollama LLM setup.")
    print()
    
    # Demonstrate KPI categories
    demonstrate_kpi_categories()
    
    # Demonstrate data structures
    demonstrate_data_structures()
    
    # Calculate basic metrics
    analysis_input = create_sample_analysis_input('Invoice Processing')
    calculate_basic_metrics(analysis_input)
    
    print("📝 Next Steps:")
    print("   1. Install Ollama: https://ollama.ai/")
    print("   2. Pull phi4 model: ollama pull phi4:latest")
    print("   3. Run main.py for full LLM-powered analysis")
    print("   4. Prepare your survey data in CSV format")
    print("   5. Configure database connections in .env file")
    print()
    
    print("✅ Basic functionality demonstration complete!")
    print("   For full analysis capabilities, set up Ollama and run main.py")

if __name__ == "__main__":
    main()