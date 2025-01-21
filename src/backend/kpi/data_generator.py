import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
from .types import KPIMetric, KPICategory
from langchain_ollama import OllamaLLM
import pandas as pd
import os
import platform
import json
import re

class KPIDataGenerator:
    """Generates synthetic KPI data using both statistical and LLM approaches"""
    
    def __init__(self, seed: int = 42, data_path: str = "data/kpi_data.csv", use_acceleration: bool = True):
        """
        Initialize with seed for reproducibility
        
        Args:
            seed: Random seed for reproducibility
            data_path: Path to save/load KPI data
            use_acceleration: Whether to use hardware acceleration if available
        """
        self._setup_hardware_acceleration(use_acceleration)
        np.random.seed(seed)
        self.llm = OllamaLLM(model="deepseek-r1:8b")
        self.data_path = data_path
        
    def _setup_hardware_acceleration(self, use_acceleration: bool):
        """Setup hardware acceleration for Apple Silicon if available"""
        if not use_acceleration:
            return
            
        # Check if running on macOS
        if platform.system() == 'Darwin':
            try:
                # Try to import the MPS backend
                import numpy as np
                import torch
                if torch.backends.mps.is_available():
                    device = torch.device("mps")
                    # Enable MPS backend if available
                    os.environ['NUMPY_ARRAY_API_BACKEND'] = 'mps'
                    print("Apple Silicon hardware acceleration enabled via MPS backend")
            except ImportError:
                print("MPS backend not available. Running with standard NumPy")
        else:
            print("Not running on macOS. Hardware acceleration not available")
    
    def _save_to_csv(self, metrics: List[KPIMetric]):
        """Save metrics to CSV file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        # Convert metrics to DataFrame
        data = []
        for m in metrics:
            data.append({
                'category': m.category.value,
                'value': m.value,
                'timestamp': m.timestamp,
                'process_name': m.process_name,
                'is_automated': m.is_automated,
                'is_llm_generated': getattr(m, 'is_llm_generated', False)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.data_path, index=False)
    
    def load_from_csv(self) -> List[KPIMetric]:
        """Load metrics from CSV file"""
        if not os.path.exists(self.data_path):
            return []
            
        df = pd.read_csv(self.data_path)
        metrics = []
        
        for _, row in df.iterrows():
            metric = KPIMetric(
                category=KPICategory(row['category']),
                value=float(row['value']),
                timestamp=row['timestamp'],
                process_name=row['process_name'],
                is_automated=bool(row['is_automated']),
                process_steps=[],  # Empty as these are filled during prediction
                company_context={}  # Empty as these are filled during prediction
            )
            metrics.append(metric)
            
        return metrics
    
    def _generate_time_series(self, base_value: float, n_samples: int, 
                            trend: float = 0.1, noise: float = 0.05) -> np.ndarray:
        """
        Generate realistic time series with trend and seasonality using hardware acceleration when available
        
        Args:
            base_value: Starting KPI value
            n_samples: Number of samples to generate
            trend: Upward/downward trend coefficient
            noise: Noise level for randomness
        """
        # Generate time component - use array operations for better hardware utilization
        t = np.linspace(0, 1, n_samples, dtype=np.float32)  # Use float32 for better performance on Apple Silicon
        
        # Compute all components in parallel using vectorized operations
        trend_component = base_value + trend * t * base_value
        seasonality = np.sin(2 * np.pi * 4 * t) * base_value * 0.05
        noise_component = np.random.normal(0, noise * base_value, n_samples).astype(np.float32)
        
        # Combine all components in a single operation
        result = trend_component + seasonality + noise_component
        
        return result
    
    async def _generate_llm_data(self, category: KPICategory, process_name: str, 
                                is_automated: bool, base_value: float) -> float: # not used, we have to add it to the data generator
        """Generate single data point using LLM"""
        prompt = f"""As a KPI analysis expert, generate a realistic KPI value for:
- Process: {process_name}
- Category: {category.value}
- Current Automation: {'Automated' if is_automated else 'Not Automated'}
- Base Value: {base_value}

Consider these factors:
1. Automated processes typically show 15-30% improvement
2. Values should be between 0-100
3. Natural variation should be present

Respond with ONLY a single number (no text).
"""
        try:
            response = await self.llm.agenerate([prompt])
            value = float(response.generations[0][0].text.strip())
            return max(0, min(100, value))  # Clamp between 0-100
        except:
            # Fallback to statistical generation if LLM fails
            return base_value * (1.2 if is_automated else 1.0) + np.random.normal(0, 2)
    
    async def _generate_process_variations(self) -> Dict[str, List]:
        """Generate variations of processes and contexts using LLM"""
        
        # Default fallback variations
        DEFAULT_VARIATIONS = {
            'process_names': [
                "Client Intake", "Document Review", "Case Filing",
                "Contract Review", "Legal Research", "Client Billing",
                "Court Filing", "Discovery Process", "Client Communication",
                "Compliance Check", "Witness Interview", "Evidence Collection",
                "Settlement Negotiation", "Trial Preparation", "Appeal Filing",
                "Legal Consultation", "Document Drafting", "Case Management",
                "Client Reporting", "Legal Analysis"
            ],
            'process_steps': [
                ["Initial contact", "Data collection", "Processing", "File creation"],
                ["Document receipt", "Review", "Annotation", "Summary"],
                ["Case preparation", "Document check", "Filing submission"],
                ["Contract receiving", "Terms review", "Legal check", "Feedback"],
                ["Research request", "Source identification", "Analysis", "Report"],
                ["Time tracking", "Rate calculation", "Invoice generation"],
                ["Document preparation", "Court check", "Submission"],
                ["Request review", "Document collection", "Analysis", "Response"],
                ["Email drafting", "Call scheduling", "Meeting notes", "Follow-up"],
                ["Regulation review", "Gap analysis", "Report generation"],
                ["Schedule interview", "Conduct interview", "Document statement"],
                ["Evidence request", "Collection", "Cataloging", "Analysis"],
                ["Offer review", "Client consultation", "Counter proposal"],
                ["Evidence review", "Strategy development", "Document prep"],
                ["Decision review", "Ground identification", "Appeal draft"],
                ["Client meeting", "Issue analysis", "Advice preparation"],
                ["Template selection", "Content writing", "Legal review"],
                ["Case review", "Task assignment", "Progress tracking"],
                ["Data gathering", "Report writing", "Client presentation"],
                ["Issue identification", "Research", "Recommendation"]
            ],
            'company_contexts': [
                {
                    "industry": "Legal Services",
                    "company_size": "Small",
                    "current_tech_stack": "Basic Legal Software",
                    "automation_experience": "Limited",
                    "annual_case_volume": "200"
                },
                {
                    "industry": "Law Firm",
                    "company_size": "Medium",
                    "current_tech_stack": "Advanced Case Management",
                    "automation_experience": "Moderate",
                    "annual_case_volume": "500"
                },
                {
                    "industry": "Legal Consulting",
                    "company_size": "Large",
                    "current_tech_stack": "Integrated Legal Suite",
                    "automation_experience": "Advanced",
                    "annual_case_volume": "1000"
                }
            ] * 7  # Repeat contexts to match number of processes
        }
        
        prompt = """Generate 20 realistic business processes for a law firm or agency.
For each process provide:
1. Process name (short)
2. Process steps (3-7 steps)
3. Company context (industry, size, tech stack, experience level, volume)

Format each as JSON. Example:
{
    "process_name": "Client Intake Process",
    "process_steps": ["Initial consultation", "Document collection", "Conflict check", "Engagement letter", "Setup client file"],
    "company_context": {
        "industry": "Legal Services",
        "company_size": "Medium",
        "current_tech_stack": "MS Office, Legal Case Management",
        "automation_experience": "Moderate",
        "annual_case_volume": "500"
    }
}

Generate 20 different variations, focusing on common law firm and agency processes."""

        try:
            response = await self.llm.agenerate([prompt])
            response_text = response.generations[0][0].text.strip()
            
            # Extract JSON objects from response
            variations = []
            json_pattern = r'\{[^{}]*\}'
            matches = re.finditer(json_pattern, response_text)
            
            for match in matches:
                try:
                    process_data = json.loads(match.group())
                    variations.append(process_data)
                except json.JSONDecodeError:
                    continue
            
            if len(variations) >= 10:  # If we got enough valid variations
                return {
                    'process_names': [v['process_name'] for v in variations],
                    'process_steps': [v['process_steps'] for v in variations],
                    'company_contexts': [v['company_context'] for v in variations]
                }
            
            print(f"Not enough valid process variations from LLM ({len(variations)}), using defaults")
            return DEFAULT_VARIATIONS
            
        except Exception as e:
            print(f"Failed to generate process variations: {e}")
            print("Using default variations")
            return DEFAULT_VARIATIONS

    async def generate_statistical_data(self, category: KPICategory, 
                                     process_variations: Dict[str, List],
                                     n_samples: int = 500) -> List[KPIMetric]:
        """Generate statistically-based synthetic data with process variations"""
        metrics = []
        base_value = self._get_base_value(category)
        
        # Generate variations
        indices = np.arange(n_samples)
        time_factors = np.sin(indices / 50) * 0.1
        growth_factors = indices / n_samples * 0.2
        noise = np.random.normal(0, 0.05, n_samples)
        is_automated = np.random.binomial(1, 0.3, n_samples)
        
        # Generate timestamps
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(n_samples)]
        
        # Calculate values
        values = base_value * (1 + time_factors + growth_factors + noise)
        values = np.clip(values, 0, None)
        
        # Randomly select process variations for each sample
        n_variations = len(process_variations['process_names'])
        variation_indices = np.random.randint(0, n_variations, n_samples)
        
        metrics = [
            KPIMetric(
                category=category,
                value=float(value),
                timestamp=date.isoformat(),
                process_name=process_variations['process_names'][idx],
                is_automated=bool(auto),
                process_steps=process_variations['process_steps'][idx],
                company_context=process_variations['company_contexts'][idx]
            )
            for value, date, auto, idx in zip(values, dates, is_automated, variation_indices)
        ]
        
        return metrics
    
    async def generate_llm_data(self, category: KPICategory,
                              process_steps: List[str],
                              company_context: Dict[str, str],
                              n_samples: int = 50) -> List[KPIMetric]:
        """Generate LLM-based synthetic data in batch"""
        base_value = self._get_base_value(category)
        
        prompt = f"""Generate {n_samples} realistic KPI values for:
Category: {category.value}
Process: {process_steps[0]}
Industry: {company_context.get('industry', 'Unknown')}
Base Value Range: {base_value * 0.8:.1f} - {base_value * 1.2:.1f}

Requirements:
1. Generate exactly {n_samples} numbers between 0-100
2. Include natural variations and trends
3. Consider industry standards and process type
4. Values should be realistic for {category.value}

RESPOND WITH ONLY {n_samples} NUMBERS, ONE PER LINE.
Example format:
45.2
38.7
52.1
(continue until {n_samples} numbers)"""

        try:
            response = await self.llm.agenerate([prompt])
            response_text = response.generations[0][0].text.strip()
            
            # Extract all numbers from response
            numbers = re.findall(r'\d+\.?\d*', response_text)
            
            if len(numbers) < n_samples:
                raise ValueError(f"Not enough numbers in response: got {len(numbers)}, expected {n_samples}")
            
            # Generate timestamps and automation states
            end_date = datetime.now()
            dates = [end_date - timedelta(days=i) for i in range(n_samples)]
            is_automated = np.random.binomial(1, 0.3, n_samples)
            
            # Create metrics
            metrics = []
            for i, (number_str, date, auto) in enumerate(zip(numbers[:n_samples], dates, is_automated)):
                try:
                    value = float(number_str)
                    value = max(0, min(100, value))  # Ensure within bounds
                    
                    metrics.append(KPIMetric(
                        category=category,
                        value=value,
                        timestamp=date.isoformat(),
                        process_name=process_steps[0],
                        is_automated=bool(auto),
                        process_steps=process_steps,
                        company_context=company_context
                    ))
                except ValueError as e:
                    print(f"Skipping invalid number: {number_str}")
                    continue
                    
            return metrics
            
        except Exception as e:
            print(f"Failed to generate LLM data: {e}")
            print(f"Raw response: {response_text if 'response_text' in locals() else 'No response'}")
            return []  # Return empty list on failure
    
    def _get_base_value(self, category: KPICategory) -> float:
        """Get base value for different KPI categories"""
        base_values = {
            KPICategory.TIME_REDUCTION: 60,    # 60 minutes
            KPICategory.COST_SAVINGS: 100,     # $100
            KPICategory.ERROR_REDUCTION: 0.15, # 15% error rate
            KPICategory.EFFICIENCY_GAIN: 0.7   # 70% efficiency
        }
        return base_values.get(category, 50.0)
    
    async def generate_and_save_data(self, 
                                   output_path: str = "data/synthetic_kpi_data.csv"):
        """Generate both statistical and LLM-based data with process variations"""
        all_data = []
        
        # Generate process variations once
        print("Generating process variations...")
        process_variations = await self._generate_process_variations()
        print(f"Generated {len(process_variations['process_names'])} process variations")
        
        for category in KPICategory:
            print(f"Generating data for {category.value}...")
            
            # Generate data using variations
            statistical_data = await self.generate_statistical_data(
                category, process_variations)
            print(f"Generated {len(statistical_data)} statistical data points")
            
            all_data.extend(statistical_data)
        
        # Convert to DataFrame and save
        df = pd.DataFrame([
            {
                "category": m.category.value,
                "value": m.value,
                "timestamp": m.timestamp,
                "process_name": m.process_name,
                "is_automated": m.is_automated,
                "process_steps": "|".join(m.process_steps),
                "company_context": json.dumps(m.company_context)
            }
            for m in all_data
        ])
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} synthetic KPI records to {output_path}")

    async def generate_initial_data(self, force_regenerate: bool = False):
        """
        Generate and save initial dataset if it doesn't exist
        
        Args:
            force_regenerate: If True, regenerate data even if CSV exists
        """
        print("Checking KPI data...")
        if force_regenerate or not os.path.exists(self.data_path):
            print("Generating synthetic KPI data...")
            data = await self.generate_and_save_data(force_regenerate=True)
            print(f"Generated {len(data)} KPI metrics")
            print(f"Data saved to: {self.data_path}")
        else:
            print(f"Using existing KPI data from: {self.data_path}")