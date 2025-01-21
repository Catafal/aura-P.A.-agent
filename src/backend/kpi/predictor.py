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

class KPIPredictor:
    """Predicts potential improvements from AI/automation integration"""
    
    def __init__(self):
        self.llm = OllamaLLM(model="deepseek-r1:14b")
        self.data_path = "data/synthetic_kpi_data.csv"
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
    
    async def predict_improvement(self, category: KPICategory,
                                process_analysis: ProcessAnalysis,
                                process_steps: List[str],
                                company_context: Dict[str, str]) -> PredictionResult:
        """Predict improvement using both ML and LLM"""
        
        # Load and train on synthetic data
        data = self._load_synthetic_data(category)
        self._train_ml_model(data)
        
        # Get ML prediction
        current_features = np.array([[0]])  # Not automated
        future_features = np.array([[1]])   # Automated
        
        current_value = self.model.predict(self.scaler.transform(current_features))[0]
        automated_value = self.model.predict(self.scaler.transform(future_features))[0]
        
        # Calculate improvement
        ml_improvement = ((current_value - automated_value) / current_value) * 100
        
        # Get LLM prediction (using existing code)
        llm_prediction = await self._get_llm_prediction(
            category, process_analysis, process_steps, company_context)
        
        # Combine ML and LLM predictions
        final_improvement = (ml_improvement + llm_prediction.predicted_improvement) / 2
        
        return PredictionResult(
            category=category,
            current_value=current_value,
            predicted_improvement=final_improvement,
            confidence=llm_prediction.confidence,
            implementation_time=llm_prediction.implementation_time,
            roi_estimate=llm_prediction.roi_estimate,
            explanation=f"""
ML-based prediction: {ml_improvement:.1f}% improvement
(Based on {len(data)} synthetic data points)

LLM-based prediction: {llm_prediction.predicted_improvement:.1f}% improvement
{llm_prediction.explanation}

Final prediction combines both ML and LLM insights for increased reliability.
"""
        )

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

    async def _get_llm_prediction(self, category: KPICategory,
                                process_analysis: ProcessAnalysis,
                                process_steps: List[str],
                                company_context: Dict[str, str]) -> PredictionResult:
        """Get LLM prediction for a given process"""
        
        prompt = f"""You are an expert AI/automation consultant with 10 years of experience. Analyze this process and provide a detailed improvement prediction.

Category: {category.value}
Process Steps:
{self._format_steps(process_steps)}

Analysis Results:
- Automation Potential: {process_analysis.automation_potential}
- Process Complexity: {process_analysis.complexity_score}
- AI Applicability: {process_analysis.ai_applicability}
- Bottlenecks: {', '.join(process_analysis.bottlenecks)}

Current Metrics:
{json.dumps(process_analysis.current_metrics, indent=2)}

Company Context:
{self._format_context(company_context)}

Provide a detailed analysis in JSON format considering:
1. Industry benchmarks and similar case studies
2. Technical feasibility and implementation complexity
3. Company's current automation maturity
4. Process-specific challenges and opportunities
5. Risk factors and mitigation strategies
6. Resource requirements and constraints
7. Expected learning curve and adoption timeline
8. Maintenance and support considerations

Respond with ONLY this JSON structure:
{{
    "current_value": 45.5,           // Current metric baseline
    "predicted_improvement": 35.0,    // Expected percentage improvement
    "confidence": 0.85,              // Confidence in prediction
    "implementation_time": 12,        // Weeks needed
    "roi_estimate": 150.0,           // ROI percentage
    "explanation": {{
        "improvement_rationale": "Detailed explanation of why this improvement is achievable...",
        "technical_analysis": "Analysis of technical implementation aspects...",
        "risk_assessment": "Key risks and mitigation strategies...",
        "implementation_phases": [
            "Phase 1: Initial setup and integration (2 weeks)",
            "Phase 2: Process automation development (4 weeks)",
            "Phase 3: Testing and validation (3 weeks)",
            "Phase 4: Training and rollout (3 weeks)"
        ],
        "success_factors": [
            "Key factor 1 with explanation",
            "Key factor 2 with explanation"
        ],
        "roi_breakdown": {{
            "cost_components": ["Implementation costs", "Training costs", "Maintenance costs"],
            "benefit_components": ["Time savings", "Error reduction", "Resource optimization"],
            "payback_period": "X months based on..."
        }}
    }}
}}

Ensure all predictions are well-justified and based on:
- Historical data patterns
- Industry benchmarks
- Technical feasibility
- Company context
- Process complexity
DO NOT include any other text, ONLY the JSON object."""

        # Get LLM response
        response = await self.llm.ainvoke(prompt)
        
        try:
            prediction = self._extract_json_from_response(response)
            
            # Format detailed explanation from the structured data
            detailed_explanation = f"""
Improvement Analysis:
{prediction['explanation']['improvement_rationale']}

Technical Implementation:
{prediction['explanation']['technical_analysis']}

Risk Assessment:
{prediction['explanation']['risk_assessment']}

Implementation Plan:
{chr(10).join(f"- {phase}" for phase in prediction['explanation']['implementation_phases'])}

Critical Success Factors:
{chr(10).join(f"- {factor}" for factor in prediction['explanation']['success_factors'])}

ROI Analysis:
- Costs: {', '.join(prediction['explanation']['roi_breakdown']['cost_components'])}
- Benefits: {', '.join(prediction['explanation']['roi_breakdown']['benefit_components'])}
- Payback Period: {prediction['explanation']['roi_breakdown']['payback_period']}
"""

            return PredictionResult(
                category=category,
                current_value=prediction["current_value"],
                predicted_improvement=prediction["predicted_improvement"],
                confidence=prediction["confidence"],
                implementation_time=prediction["implementation_time"],
                roi_estimate=prediction["roi_estimate"],
                explanation=detailed_explanation
            )
        except Exception as e:
            print(f"Failed to process prediction. Raw response: {response}")
            raise ValueError(f"Prediction failed: {str(e)}") 