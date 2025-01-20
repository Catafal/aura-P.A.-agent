# prd.md

# Project overview
The Project Evaluation Agent is designed to analyze business processes and recommend optimal candidates for automation or AI enhancement. This system employs a mathematics-specific Large Language Model to process various operational metrics and generate actionable insights for process optimization.

# Core functionalities
1. Process Data Collection
 - reads .csv files from a directory or database (directory if no database is available)
2. Mathematical Analysis
 - uses a mathematics-specific Large Language Model to process the data
 - Analyzes cost-benefit ratios
 - Generates performance indicators
 - Calculates composite scores using weighted algorithms
3. Process Optimization Engine
 - Identifies bottlenecks
 - Recommends process improvements
 - Calculates potential time/resource savings
4. Recommendation System
 - Provides ROI projections
 - Generates detailed reports
 - Suggests AI-driven solutions
5. Predictive Analytics
 - Performs trend analysis
 - Forecasts future performance
 - Provides actionable insights
6. Reporting and Visualization
- Generates comprehensive reports
- Provides visualizations
- Supports data-driven decision-making
- Tracks optimization metrics
- Helps us to add then future data, and see the changes

# Doc
Models:
- https://huggingface.co/unsloth/phi-4
- https://huggingface.co/Qwen/Qwen2.5-Math-PRM-7B
- https://huggingface.co/microsoft/phi-4
- https://huggingface.co/softcatala/translate-cat-eng


# Current file structure
tree -L 4 -a -I 'node_modules|.git|__pycache__|.DS_Store|.pytest_cache|.vscode'


# Additional requirements
- language: python
- Langchain
- Start using HuggingFace for the LLM (also implement Groq)
- pydantic to validate the data
- Use the .env file to store the API keys
- We get our data from Airtable



