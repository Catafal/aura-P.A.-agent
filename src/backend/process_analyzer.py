from typing import Dict, List
from src.backend.kpi.predictor import KPIPredictor
from src.backend.model.math_analysis import MathematicalAnalyzer
from src.backend.survey_handler import SurveyProcessor

class ProcessAnalyzer:
    """Combines KPI and mathematical analysis approaches"""
    
    def __init__(self, survey_path: str):
        self.survey_processor = SurveyProcessor(survey_path)
        self.kpi_predictor = KPIPredictor()
        self.math_analyzer = MathematicalAnalyzer()

    async def analyze_process(self, process_name: str) -> Dict:
        # Get survey row for the process
        process_row = self.survey_processor.survey_data[
            self.survey_processor.survey_data['process_name'] == process_name
        ].iloc[0]
        
        # Process survey data
        metrics, process_steps = self.survey_processor.process_survey_row(process_row)
        
        # Prepare analysis components
        kpi_category = self.survey_processor.get_kpi_category(process_row)
        process_analysis = self.survey_processor.prepare_process_analysis(metrics)
        analysis_input = self.survey_processor.prepare_analysis_input(metrics)
        
        # Get predictions and analysis
        kpi_prediction = await self.kpi_predictor.predict_improvement(
            category=kpi_category,
            process_analysis=process_analysis,
            process_steps=process_steps,
            company_context=self.survey_processor.company_context
        )
        
        # Get mathematical analysis and extract content
        math_analysis_result = await self.math_analyzer.analyze_cost_benefit(analysis_input)
        
        # Extract the generated content from LLMResult
        generated_content = math_analysis_result.generations[0][0].text if math_analysis_result.generations else ""
        
        # Convert LLMResult to dictionary format
        math_analysis = {
            "overall_score": self._extract_score(generated_content),
            "recommendations": self._extract_recommendations(generated_content),
            "raw_analysis": generated_content
        }
        
        return {
            "process_name": process_name,
            "kpi_prediction": {
                "category": kpi_category.value,
                "improvement": kpi_prediction.predicted_improvement,
                "confidence": kpi_prediction.confidence,
                "roi_estimate": kpi_prediction.roi_estimate,
                "implementation_time": kpi_prediction.implementation_time
            },
            "mathematical_analysis": math_analysis,
            "process_metrics": metrics,
            "company_context": self.survey_processor.company_context
        }

    def _extract_score(self, content: str) -> float:
        """Extract overall score from LLM response"""
        try:
            # Implement simple parsing logic - this is an example
            # You might need to adjust based on actual LLM response format
            if "overall score" in content.lower():
                score_text = content.lower().split("overall score")[1].split()[0]
                return float(score_text.strip(':%'))
            return 0.0
        except Exception:
            return 0.0

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from LLM response"""
        try:
            # Implement simple parsing logic - this is an example
            recommendations = []
            if "recommendations:" in content.lower():
                rec_section = content.lower().split("recommendations:")[1].split("\n")
                recommendations = [r.strip('- ').strip() for r in rec_section if r.strip()]
            return recommendations[:5]  # Return top 5 recommendations
        except Exception:
            return ["No specific recommendations available"]