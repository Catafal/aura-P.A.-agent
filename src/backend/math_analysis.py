from pydantic import BaseModel
from typing import List, Dict, Union, Optional
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.schema import HumanMessage, SystemMessage
from transformers import AutoModelForCausalLM, AutoTokenizer

class ProcessActions(BaseModel):
    """Structure for process actions data"""
    steps: List[str]
    duration_per_step: List[int]

class HumanResources(BaseModel):
    """Structure for human resources data"""
    max_people_involved: int
    roles: List[str]

class Frequency(BaseModel):
    """Structure for frequency analysis data"""
    daily_repetitions: int
    peak_hours: List[int]

class ErrorMetrics(BaseModel):
    """Structure for error metrics data"""
    error_rate: float
    error_impact: int  # Scale 1-10
    error_types: List[str]

class ImpactAssessment(BaseModel):
    """Structure for impact assessment data"""
    importance_rating: int  # Scale 1-10
    affected_departments: List[str]

class Automation(BaseModel):
    """Structure for automation potential data"""
    feasibility_rating: int  # Scale 1-10
    potential_savings: float

class AnalysisInput(BaseModel):
    """Enhanced data structure for input validation"""
    metrics: Dict[str, Union[float, Dict, ProcessActions, HumanResources, 
                           Frequency, ErrorMetrics, ImpactAssessment, Automation]]
    weights: Optional[Dict[str, float]] = None
    target_variables: List[str]

class MathematicalAnalyzer:
    """Handles mathematical analysis using LLMs"""
    
    def __init__(self, llm_provider: str = "ollama"):
        """
        Initialize the analyzer with specified LLM provider
        
        Args:
            llm_provider (str): Provider name - "ollama" ors "groq"
        """
        load_dotenv()
        self.llm = self._initialize_llm(llm_provider)
        
    def _initialize_llm(self, provider: str):
        """
        Initialize the appropriate LLM based on provider
        
        Args:
            provider (str): The LLM provider to use
            
        Returns:
            LLM instance
            
        Raises:
            ValueError: If provider is not supported or API keys are missing
        """
        if provider.lower() == "ollama":
            return OllamaLLM(model="phi4:latest")
        elif provider.lower() == "groq":
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            return ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

    async def analyze_cost_benefit(self, data: AnalysisInput) -> Dict:
        """Analyze cost-benefit ratios using LLM with enhanced metrics"""
        # Format the prompt for comprehensive analysis
        prompt = f"""
        Analyze the following process metrics with their detailed components:
        - Process Metrics: {data.metrics}
        
        Provide a comprehensive analysis considering:
        1. Process efficiency (time and steps analysis)
        2. Resource utilization (human resources and workload)
        3. Error impact and frequency
        4. Business importance and department impact
        5. Automation potential and savings
        
        Format the response as a JSON with the following structure:
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
        
        if isinstance(self.llm, ChatGroq):
            messages = [
                SystemMessage(content="You are a mathematical analysis assistant that provides responses in JSON format."),
                HumanMessage(content=prompt)
            ]
            response = await self.llm.agenerate([messages])
        else:
            response = await self.llm.agenerate([prompt])
            
        return response

    async def calculate_performance_indicators(self, data: AnalysisInput) -> Dict:
        """Calculate key performance indicators"""
        # Implementation similar to cost_benefit analysis
        pass

    async def generate_composite_score(self, data: AnalysisInput) -> float:
        """Generate a composite score using weighted algorithms"""
        # Implementation for composite score calculation
        pass 