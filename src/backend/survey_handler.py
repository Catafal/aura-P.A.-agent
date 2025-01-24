from typing import Dict, List, Tuple
from src.backend.kpi.types import KPICategory, ProcessAnalysis
from src.backend.model.math_analysis import AnalysisInput, ProcessActions, HumanResources, Frequency, ErrorMetrics, ImpactAssessment, Automation
import pandas as pd
from .database.survey_db import SurveyDatabase
from .database.company_db import CompanyDatabase

class SurveyProcessor:
    """Processes survey data and prepares it for KPI and mathematical analysis"""
    
    def __init__(self, company_id: str):
        """
        Initialize with company ID
        
        Args:
            company_id: UUID of the company in database
        """
        self.survey_db = SurveyDatabase()
        self.company_db = CompanyDatabase()
        self.company_id = company_id
        
    async def load_data(self):
        """Load survey and company data"""
        self.survey_data = await self.survey_db.get_survey_data(self.company_id)
        if self.survey_data is None or self.survey_data.empty:
            print(f"Warning: No survey data found for company {self.company_id}")
            # Create a sample survey data for testing
            self.survey_data = pd.DataFrame([{
                'respondent_role': 'Test User',
                'experience_with_process': '1 year',
                'department': 'Test Department',
                'process_name': 'Sample Process',
                'process_description': 'Step 1, Step 2, Step 3',
                'total_time_minutes': 60,
                'people_involved': 1,
                'daily_frequency': 5,
                'error_rate_percentage': 5,
                'error_impact_rating': 5,
                'business_importance': 7,
                'automation_potential': 70,
                'main_challenges': ['Challenge 1', 'Challenge 2'],
                'current_systems_used': ['System 1', 'System 2']
            }])
            
        await self._load_company_context()
        
    async def _load_company_context(self):
        """Load company context from database"""
        company_data = await self.company_db.get_company_data(self.company_id)
        if company_data:
            self.company_context = {
                "industry": company_data.get("company_industry", "Unknown"),
                "company_size": company_data.get("company_size", "Unknown"),
                "company_name": company_data.get("company_name", "Unknown"),
                "company_location": company_data.get("company_location", "Unknown"),
                "company_description": company_data.get("company_description", "Unknown"),
                "current_tech_stack": company_data.get("tech_stack", "Basic"),
                "automation_experience": company_data.get("automation_experience", "Limited"),
                "regulatory_requirements": company_data.get("regulatory_requirements", "Medium"),
                "annual_case_volume": company_data.get("annual_case_volume", "Unknown"),
                "primary_practice_areas": company_data.get("practice_areas", []),
                "client_base": company_data.get("client_base", "Mixed")
            }
            return
                
        # Fallback to default context if no company_id or data not found
        self.company_context = {
            "industry": "Legal Services",
            "company_size": "Medium",
            "current_tech_stack": "Document Management, CRM, E-filing",
            "automation_experience": "Limited",
            "regulatory_requirements": "High",
            "annual_case_volume": "500-1000",
            "primary_practice_areas": ["Corporate Law", "Litigation", "Compliance"],
            "client_base": "Corporate and Individual"
        }

    def process_survey_row(self, row: pd.Series) -> Tuple[Dict, List[str]]:
        """Process a single survey row into required formats"""
        
        # Extract process steps from description
        process_steps = [step.strip() for step in row['process_description'].split(',')]
        
        # Convert survey data to analysis metrics
        metrics = {
            "process_actions": ProcessActions(
                steps=process_steps,
                duration_per_step=[row['total_time_minutes'] // len(process_steps)] * len(process_steps)
            ),
            "human_resources": HumanResources(
                max_people_involved=row['people_involved'],
                roles=[row['respondent_role']]
            ),
            "frequency": Frequency(
                daily_repetitions=row['daily_frequency'],
                peak_hours=[9, 10, 11, 14, 15, 16]  # Assumed standard business hours
            ),
            "error_metrics": ErrorMetrics(
                error_rate=row['error_rate_percentage'] / 100,
                error_impact=row['error_impact_rating'],
                error_types=["Data Entry", "Communication", "Documentation"]  # Example types
            ),
            "impact_assessment": ImpactAssessment(
                importance_rating=row['business_importance'],
                affected_departments=[row['department']]
            ),
            "automation": Automation(
                feasibility_rating=row['automation_potential'] // 10,  # Convert to 1-10 scale
                potential_savings=row['automation_potential'] / 100 * row['total_time_minutes']
            )
        }
        
        return metrics, process_steps

    def get_kpi_category(self, row: pd.Series) -> KPICategory:
        """Determine KPI category based on process characteristics"""
        if 'time' in row['process_name'].lower():
            return KPICategory.TIME_REDUCTION
        elif 'cost' in row['process_name'].lower() or 'billing' in row['process_name'].lower():
            return KPICategory.COST_SAVINGS
        elif 'error' in row['process_name'].lower() or 'quality' in row['process_name'].lower():
            return KPICategory.ERROR_REDUCTION
        else:
            return KPICategory.EFFICIENCY_GAIN

    def prepare_process_analysis(self, metrics: Dict) -> ProcessAnalysis:
        """Convert metrics to ProcessAnalysis format"""
        return ProcessAnalysis(
            current_metrics={
                "avg_completion_time": metrics["process_actions"].duration_per_step[0],
                "error_rate": metrics["error_metrics"].error_rate,
                "cost_per_execution": metrics["process_actions"].duration_per_step[0] * 2,  # Assumed cost rate
                "resource_utilization": metrics["human_resources"].max_people_involved / 10  # Scale to 0-1
            },
            automation_potential=metrics["automation"].feasibility_rating / 10,  # Scale to 0-1
            complexity_score=len(metrics["process_actions"].steps) / 10,  # Scale to 0-1
            ai_applicability=metrics["automation"].feasibility_rating / 10,  # Scale to 0-1
            bottlenecks=["Manual data entry", "Document review", "Approval delays"]  # Example bottlenecks
        )

    def prepare_analysis_input(self, metrics: Dict) -> AnalysisInput:
        """Convert metrics to AnalysisInput format"""
        return AnalysisInput(
            metrics=metrics,
            target_variables=[
                "efficiency_score",
                "quality_score",
                "automation_potential"
            ]
        )