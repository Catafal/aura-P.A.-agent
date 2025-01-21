import asyncio
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.backend.process_analyzer import ProcessAnalyzer

async def main():
    # Initialize analyzer with survey data
    analyzer = ProcessAnalyzer("/Volumes/970Evo Plus/GitHub/aura-P.A.-agent/tests/data/law-firm-survey.csv")
    
    # Analyze a specific process
    result = await analyzer.analyze_process("Legal Document Review")
    
    # Print results
    print("\nAnalysis Results:")
    print("-" * 50)
    print(f"Process: {result['process_name']}")
    print("\nKPI Prediction:")
    print(f"- Category: {result['kpi_prediction']['category']}")
    print(f"- Improvement: {result['kpi_prediction']['improvement']:.1f}%")
    print(f"- ROI Estimate: {result['kpi_prediction']['roi_estimate']:.1f}%")
    print(f"- Implementation Time: {result['kpi_prediction']['implementation_time']} weeks")
    
    print("\nMathematical Analysis:")
    print(f"- Overall Score: {result['mathematical_analysis']['overall_score']:.1f}")
    print("\nRecommendations:")
    for rec in result['mathematical_analysis']['recommendations']:
        print(f"- {rec}")
    
    print("\nRaw Analysis:")
    print(result['mathematical_analysis']['raw_analysis'])

if __name__ == "__main__":
    asyncio.run(main())