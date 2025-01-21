from typing import Dict

class MathAnalysisPrompts:
    """Collection of prompt templates for mathematical analysis"""
    
    @staticmethod
    def cost_benefit_prompt(metrics: Dict) -> str:
        """
        Creates a detailed cost-benefit analysis prompt incorporating all process metrics
        """
        return f"""
        Analyze the following metrics for comprehensive cost-benefit analysis:
        {metrics}
        
        Consider these key aspects:
        1. Process Efficiency
           - Step-by-step process breakdown
           - Time allocation per action
           - Total process duration
        
        2. Resource Utilization
           - Human resource requirements
           - Team composition and roles
           - Resource allocation efficiency
        
        3. Operational Metrics
           - Daily frequency and peak hours
           - Error rates and impact
           - Quality control measures
        
        4. Strategic Value
           - Business impact rating
           - Affected departments
           - Process importance
        
        5. Future Potential
           - Automation feasibility
           - Potential time/cost savings
           - Implementation considerations
        
        Format response as JSON with fields:
        {{
            "overall_score": float,
            "component_scores": {{
                "efficiency_score": float,
                "resource_score": float,
                "quality_score": float,
                "impact_score": float,
                "automation_score": float
            }},
            "analysis": string,
            "recommendations": list,
            "priority_level": string
        }}
        """
    
    @staticmethod
    def performance_indicators_prompt(metrics: Dict) -> str:
        """
        Creates a performance analysis prompt focusing on operational metrics
        """
        return f"""
        Analyze the following performance metrics:
        {metrics}
        
        Calculate and evaluate:
        1. Process Performance
           - Average completion time
           - Step efficiency ratings
           - Resource utilization rate
        
        2. Quality Metrics
           - Error frequency and patterns
           - Impact severity analysis
           - Quality control effectiveness
        
        3. Operational Efficiency
           - Daily throughput analysis
           - Peak load handling
           - Resource allocation optimization
        
        4. Strategic Alignment
           - Business value score
           - Cross-department impact
           - Process criticality rating
        
        5. Improvement Potential
           - Automation readiness score
           - Optimization opportunities
           - Risk assessment
        
        Format response as JSON with fields:
        {{
            "performance_metrics": {{
                "throughput_score": float,
                "quality_score": float,
                "efficiency_score": float,
                "strategic_value": float,
                "improvement_potential": float
            }},
            "key_findings": list,
            "optimization_recommendations": list,
            "risk_factors": list
        }}
        """ 