from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class KPICategory(Enum):
    """Categories of KPI improvements we want to predict"""
    TIME_REDUCTION = "time_reduction"  # Percentage of time that could be saved
    COST_SAVINGS = "cost_savings"      # Percentage of costs that could be reduced
    ERROR_REDUCTION = "error_reduction" # Percentage of errors that could be eliminated
    EFFICIENCY_GAIN = "efficiency_gain" # Percentage of efficiency improvement

@dataclass
class KPIMetric:
    """Represents a single KPI measurement"""
    category: KPICategory
    value: float
    timestamp: str
    process_name: str
    is_automated: bool
    process_steps: List[str]  # List of steps in the process
    company_context: Dict[str, str]  # Quick context about the company and process
    
@dataclass
class ProcessAnalysis:
    """Detailed analysis of a process for improvement prediction"""
    current_metrics: Dict[str, float]  # Current performance metrics
    automation_potential: float        # 0-1 score of automation potential
    complexity_score: float           # 0-1 score of process complexity
    ai_applicability: float          # 0-1 score of AI applicability
    bottlenecks: List[str]          # Identified process bottlenecks
    
@dataclass 
class PredictionResult:
    """Represents the improvement prediction"""
    category: KPICategory
    current_value: float              # Current metric value
    predicted_improvement: float      # Predicted percentage improvement
    confidence: float                # Confidence score (0-1)
    implementation_time: int         # Estimated implementation time in weeks
    roi_estimate: float             # Estimated ROI
    explanation: str                # Detailed explanation of prediction