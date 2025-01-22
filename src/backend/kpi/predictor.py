from typing import List, Optional, Tuple, Dict
from .types import KPIMetric, PredictionResult, KPICategory, ProcessAnalysis
from .data_generator import KPIDataGenerator
import re
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from langchain_ollama import OllamaLLM
import numpy as np
import pandas as pd
import platform
import os
import json
from langchain.schema import SystemMessage, HumanMessage
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='sklearn.utils.validation')

class MPSAccelerationMixin:
    """Mixin to handle Apple Silicon hardware acceleration"""
    
    @staticmethod
    def setup_mps_acceleration():
        """Setup MPS acceleration if available"""
        if platform.system() != 'Darwin':
            print("Not running on macOS. Hardware acceleration not available")
            return False
            
        try:
            # First check if we're on Apple Silicon
            cmd = os.popen('sysctl -n machdep.cpu.brand_string')
            cpu_info = cmd.read().strip()
            if 'Apple' not in cpu_info:
                print(f"Not running on Apple Silicon: {cpu_info}")
                return False
                
            # Try to import torch and check MPS availability
            import torch
            if not torch.backends.mps.is_available():
                print("PyTorch MPS backend not available. Installing required packages...")
                return False
                
            # If we get here, we can use MPS
            os.environ['NUMPY_ARRAY_API_BACKEND'] = 'mps'
            print(f"Apple Silicon detected ({cpu_info})")
            print("Hardware acceleration enabled via MPS backend")
            return True
            
        except ImportError:
            print("PyTorch not installed. To enable hardware acceleration, install:")
            print("pip install torch torchvision")
            return False
        except Exception as e:
            print(f"Error setting up MPS acceleration: {str(e)}")
            return False

class LLMKPITransformer(BaseEstimator, TransformerMixin, MPSAccelerationMixin):
    """Custom transformer that uses LLM for KPI feature extraction with hardware acceleration support"""
    
    def __init__(self, model_name: str = "deepseek-r1:8b", use_acceleration: bool = True):
        self.llm = OllamaLLM(model=model_name)
        if use_acceleration:
            self.setup_mps_acceleration()
        
    def fit(self, X, y=None):
        return self
        
    async def _process_features(self, metrics: List[KPIMetric]) -> float:
        """Process features using LLM"""
        # Calculate basic statistics using hardware-accelerated NumPy
        values = np.array([m.value for m in metrics], dtype=np.float32)  # Use float32 for better performance on Apple Silicon
        mean_value = np.mean(values)
        
        # Vectorized trend calculation
        x = np.arange(len(values), dtype=np.float32)
        trend = np.polyfit(x, values, 1)[0]
        
        # Format process steps
        steps_str = "\n".join([f"  - {step}" for step in metrics[-1].process_steps])
        
        # Format company context
        context_str = "\n".join([f"  - {k}: {v}" for k, v in metrics[-1].company_context.items()])
        
        prompt = f"""Analyze these KPI metrics and predict the next value:

Company Context:
{context_str}

Process Steps:
{steps_str}

Metrics:
- Current Value: {values[-1]:.2f}
- Mean Value: {mean_value:.2f}
- Trend: {trend:.2f}
- Process: {metrics[-1].process_name}
- Category: {metrics[-1].category.value}
- Automated: {metrics[-1].is_automated}

Consider:
1. Historical trend
2. Automation impact
3. Category specifics
4. Process complexity (steps)
5. Company context

Respond with ONLY a number between 0-100.
"""
        response = await self.llm.agenerate([prompt])
        try:
            return float(response.generations[0][0].text.strip())
        except:
            return values[-1]  # Fallback to last known value
    
    async def transform(self, X):
        """Transform metrics into features using hardware acceleration when available"""
        predictions = []
        for metrics in X:
            pred = await self._process_features(metrics)
            predictions.append([pred])
        return np.array(predictions, dtype=np.float32)  # Use float32 for better performance

# Add to the existing prompts
PREDICTION_SYSTEM_PROMPT = """You are a JSON-only response generator for process improvement predictions.
Rules:
1. ONLY output valid JSON
2. NO explanatory text outside the JSON
3. NO thinking out loud
4. NO markdown formatting
5. Follow the exact structure below:

{
    "current_value": float,
    "predicted_improvement": float,
    "confidence": float,
    "implementation_time": int,
    "roi_estimate": float,
    "explanation": {
        "improvement_rationale": string,
        "process_challenges": string,
        "risk_factors": [{"factor": string, "mitigation": string}],
        "resource_requirements": [string],
        "learning_curve": string,
        "maintenance_support": string
    }
}"""

class KPIPredictor:
    """Predicts potential improvements from AI/automation integration"""
    
    def __init__(self):
        self.llm = OllamaLLM(model="deepseek-r1:14b")
        self.data_path = "/Volumes/970Evo Plus/GitHub/aura-P.A.-agent/tests/data/synthetic_kpi_data.csv"
        self.model = None
        
    def _load_synthetic_data(self, category: KPICategory) -> pd.DataFrame:
        """Load synthetic data for the specified category"""
        df = pd.read_csv(self.data_path)
        return df[df["category"] == category.value]
    
    def _train_ml_model(self, data: pd.DataFrame):
        """Train ML model on synthetic data"""
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.preprocessing import StandardScaler
        
        # Prepare features
        X = data[["is_automated"]].astype(int)  # Add more features as needed
        y = data["value"]
        
        # Create and train model
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3
        )
        self.model.fit(X_scaled, y)
    
    async def predict_improvement(self, category: KPICategory, analysis: dict, process_steps: List[str], company_context: dict) -> dict:
        try:
            # Instead of using SystemMessage, we'll combine the prompts into a single string
            system_prompt = """You are a JSON-only response generator for process improvement predictions.
Rules:
1. ONLY output valid JSON
2. NO explanatory text outside the JSON
3. NO thinking out loud
4. NO markdown formatting
5. Follow the exact structure below:

{
    "current_value": float,
    "predicted_improvement": float,
    "confidence": float,
    "implementation_time": int,
    "roi_estimate": float,
    "explanation": {
        "improvement_rationale": string,
        "process_challenges": string,
        "risk_factors": [{"factor": string, "mitigation": string}],
        "resource_requirements": [string],
        "learning_curve": string,
        "maintenance_support": string
    }
}"""

            human_prompt = f"""Based on the following process information, generate a prediction for {category.value}:
Process Steps: {process_steps}
Analysis Results: {analysis}
Company Context: {company_context}

Remember: Output ONLY valid JSON following the specified structure."""

            full_prompt = f"{system_prompt}\n\n{human_prompt}"
            
            # Get prediction from LLM
            response = await self.llm.agenerate([full_prompt])
            prediction_text = response.generations[0][0].text.strip()
            
            # Parse JSON response
            import json
            try:
                # Clean up the response to find JSON
                import re
                json_match = re.search(r'\{[\s\S]*\}', prediction_text)
                if json_match:
                    prediction = json.loads(json_match.group())
                    prediction['category'] = category.value
                    return prediction
                else:
                    raise ValueError("No JSON found in response")
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse prediction. Raw response: {prediction_text}")
                raise
                
        except Exception as e:
            print(f"Prediction failed: {str(e)}")
            # Return a fallback prediction instead of raising
            return {
                "category": category.value,
                "current_value": 0.0,
                "predicted_improvement": 0.0,
                "confidence": 0.0,
                "implementation_time": 0,
                "roi_estimate": 0.0,
                "explanation": {
                    "improvement_rationale": f"Failed to generate prediction: {str(e)}",
                    "process_challenges": "Unknown",
                    "risk_factors": [{"factor": "Analysis failed", "mitigation": "Retry analysis"}],
                    "resource_requirements": ["Unknown"],
                    "learning_curve": "Unknown",
                    "maintenance_support": "Unknown"
                }
            }

    def _format_steps(self, steps: List[str]) -> str:
        """Format process steps for prompt"""
        return "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    
    def _format_context(self, context: Dict[str, str]) -> str:
        """Format company context for prompt"""
        return "\n".join(f"{k}: {v}" for k, v in context.items())
    
    async def analyze_process(self, process_steps: List[str], 
                            company_context: Dict[str, str]) -> ProcessAnalysis:
        """Analyze process for improvement potential"""
        
        prompt = f"""You are an AI expert system analyst. Analyze this business process and respond ONLY with a JSON object.

Process Steps:
{self._format_steps(process_steps)}

Company Context:
{self._format_context(company_context)}

Respond with ONLY this JSON structure:
{{
    "automation_potential": 0.75,  // Example value, use 0-1 score
    "complexity_score": 0.45,      // Example value, use 0-1 score
    "ai_applicability": 0.8,       // Example value, use 0-1 score
    "bottlenecks": ["Manual data entry", "Verification delays"],  // Example values
    "current_metrics": {{
        "avg_completion_time": 45.5,    // In minutes
        "error_rate": 0.05,            // 0-1 rate
        "cost_per_execution": 25.0,     // Currency units
        "resource_utilization": 0.7     // 0-1 rate
    }}
}}

DO NOT include any other text, ONLY the JSON object."""

        # Get LLM response
        response = await self.llm.ainvoke(prompt)
        
        try:
            analysis = self._extract_json_from_response(response)
            return ProcessAnalysis(
                current_metrics=analysis["current_metrics"],
                automation_potential=analysis["automation_potential"],
                complexity_score=analysis["complexity_score"],
                ai_applicability=analysis["ai_applicability"],
                bottlenecks=analysis["bottlenecks"]
            )
        except Exception as e:
            print(f"Failed to process analysis. Raw response: {response}")
            raise ValueError(f"Analysis failed: {str(e)}")

    def _extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from LLM response, handling various formats"""
        try:
            # Try to find JSON-like structure in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON structure found in response")
        except json.JSONDecodeError as e:
            print(f"Raw response: {response}")
            raise ValueError(f"Failed to parse response as JSON: {e}") 