# Aura P.A. Agent
*AI-Powered Business Process Analysis & Optimization*

## Project Overview

The **Aura P.A. Agent** (Process Analysis Agent) is an intelligent business process analysis tool that leverages advanced AI and Large Language Models to analyze, optimize, and provide actionable insights for business processes. Using mathematical analysis and predictive modeling, it helps organizations identify automation opportunities, reduce costs, and improve operational efficiency.

### Key Capabilities
- **AI-Driven Process Analysis**: Uses Ollama LLM (phi4 model) for intelligent process evaluation
- **Mathematical Cost-Benefit Analysis**: Provides quantitative insights with ROI calculations
- **KPI Prediction & Forecasting**: Predicts process improvements and performance metrics
- **Survey Data Processing**: Transforms business process surveys into actionable insights
- **Comprehensive Reporting**: Generates detailed analysis reports with LaTeX formatting

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/Catafal/aura-P.A.-agent.git
cd aura-P.A.-agent
pip install -r requirements.txt

# 2. Try the basic example (no LLM required)
python examples/basic_usage_example.py

# 3. For full analysis, install Ollama and run
ollama pull phi4:latest
python main.py
```

## Features

### 🔍 **Process Research & Analysis**
- Automated analysis of business process workflows
- Identification of bottlenecks and inefficiencies
- Process complexity scoring and evaluation
- Multi-step process mapping and optimization

### 📊 **KPI Prediction & Forecasting**
- Time reduction predictions
- Cost savings projections  
- Error reduction estimations
- ROI and implementation timeline forecasts
- Confidence scoring for predictions

### 🤖 **AI-Powered Insights**
- Integration with Ollama LLM using phi4 model
- Intelligent process context understanding
- Automated data extraction from survey responses
- Natural language processing for process descriptions

### 📈 **Mathematical Analysis Engine**
- Quantitative cost-benefit calculations
- Statistical process performance analysis
- Weighted scoring algorithms
- Composite process evaluation metrics

### 📋 **Comprehensive Reporting**
- Markdown and LaTeX report generation
- Individual process analysis reports
- Company-wide process summary reports
- Visual data presentations and charts

### 🔄 **Data Integration**
- Google Sheets integration for survey data
- Firestore and Supabase database support
- CSV data processing capabilities
- Multi-company data management

## Technical Requirements

### System Requirements
- **Python**: 3.12+ (tested with Python 3.12.3)
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 8GB RAM (16GB recommended for LLM operations)
- **Storage**: At least 10GB free space for model files

### Core Dependencies
- **Ollama**: Local LLM inference engine
- **LangChain**: LLM framework for AI interactions
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Matplotlib**: Data visualization
- **Scikit-learn**: Machine learning algorithms
- **Google Cloud Firestore**: Database integration
- **Supabase**: Backend database services

## Installation Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Catafal/aura-P.A.-agent.git
cd aura-P.A.-agent
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv aura_env

# Activate virtual environment
# On Linux/macOS:
source aura_env/bin/activate
# On Windows:
aura_env\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and Configure Ollama

#### Install Ollama
```bash
# On macOS:
brew install ollama

# On Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows:
# Download from https://ollama.ai/download
```

#### Pull the phi4 Model
```bash
ollama pull phi4:latest
```

#### Start Ollama Service
```bash
# Start Ollama server
ollama serve
```

### 5. Environment Configuration
Create a `.env` file in the project root:
```bash
# Database Configuration
GOOGLE_CLOUD_PROJECT_ID=your_project_id
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=phi4:latest

# Optional: Alternative LLM providers
GROQ_API_KEY=your_groq_key
HUGGINGFACE_API_KEY=your_hf_key
```

## Usage Guide

### Basic Usage

1. **Prepare Your Data**: Ensure your survey data is available in CSV format or connected database
2. **Run the Analysis**:
   ```bash
   python main.py
   ```
3. **Select Company**: Choose from available companies in your database
4. **Review Results**: Analysis reports will be generated in the `reports/` directory

### Input Data Format

The system expects survey data with the following columns:
- `process_name`: Name of the business process
- `process_description`: Detailed description of the process
- `total_time_minutes`: Time required to complete the process
- `people_involved`: Number of people involved
- `daily_frequency`: How many times the process runs per day
- `error_rate_percentage`: Current error rate (0-100)
- `error_impact_rating`: Impact of errors (1-10 scale)
- `business_importance`: Business importance rating (1-10)
- `automation_potential`: Automation feasibility (0-100)
- `main_challenges`: Primary challenges faced
- `current_systems_used`: Systems currently in use

### Expected Output

The system generates several types of reports:
- **Individual Process Reports**: Detailed analysis for each process
- **Summary Reports**: Company-wide process overview
- **Mathematical Analysis**: Quantitative cost-benefit calculations
- **KPI Predictions**: Forecasted improvements and timelines

## Project Structure

```
aura-P.A.-agent/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env                        # Environment configuration
├── src/                        # Source code
│   └── backend/                # Backend modules
│       ├── model/              # AI and mathematical models
│       │   ├── math_analysis.py      # Mathematical analysis engine
│       │   ├── prompt_templates.py   # LLM prompt templates
│       │   └── data_anonymizer.py    # Data privacy utilities
│       ├── kpi/                # KPI prediction system
│       │   ├── predictor.py          # KPI prediction engine
│       │   ├── types.py              # KPI data types
│       │   └── data_generator.py     # Synthetic data generation
│       ├── database/           # Database integrations
│       │   ├── company_db.py         # Company data management
│       │   └── survey_db.py          # Survey data handling
│       ├── survey_handler.py   # Survey data processing
│       └── report_converter.py # Report generation utilities
├── examples/                   # Usage examples and demonstrations
│   └── basic_usage_example.py  # Basic functionality demo
├── tests/                      # Test files and sample data
├── reports/                    # Generated analysis reports
└── instructions/               # Project documentation
    ├── prd.md                  # Product requirements
    ├── roadmap.md              # Development roadmap
    └── database_setup.md       # Database setup guide
```

### Key Components

- **Mathematical Analyzer** (`math_analysis.py`): Core engine for quantitative process analysis
- **KPI Predictor** (`kpi/predictor.py`): Machine learning-based performance forecasting
- **Survey Handler** (`survey_handler.py`): Processes and structures survey data
- **Report Converter** (`report_converter.py`): Generates formatted reports
- **Database Modules** (`database/`): Handles data persistence and retrieval

## Configuration

### Model Selection
Configure the LLM model in your environment:
```bash
# Default model (recommended)
DEFAULT_MODEL=phi4:latest

# Alternative models
# DEFAULT_MODEL=qwen2.5-math:7b
# DEFAULT_MODEL=llama3.1:8b
```

### Analysis Parameters
Adjust analysis parameters in the configuration:
- **Verification Analysis**: Enable dual-model verification for critical analyses
- **Confidence Thresholds**: Set minimum confidence levels for predictions
- **Report Formats**: Choose between Markdown, LaTeX, or both
- **Data Privacy**: Configure anonymization settings

### Database Configuration
Support for multiple database backends:
- **Google Firestore**: For scalable cloud storage
- **Supabase**: For PostgreSQL-based storage
- **Local CSV**: For file-based data processing

## Examples

### Sample Survey Data
```csv
process_name,process_description,total_time_minutes,people_involved,daily_frequency
"Invoice Processing","Manual invoice data entry and approval",45,3,25
"Customer Onboarding","New customer account setup process",120,5,8  
"Inventory Management","Daily inventory count and reconciliation",180,2,1
```

### Sample Analysis Output
```markdown
# Process Analysis Report

## Invoice Processing Analysis
- **Automation Potential**: 85%
- **Predicted Time Savings**: 67%
- **ROI Estimate**: 340% over 12 months
- **Implementation Complexity**: Medium

### Recommendations
1. Implement OCR for automatic data extraction
2. Add approval workflow automation
3. Integrate with existing accounting systems
```

### Basic Example (No LLM Required)
```bash
# Run basic demonstration without Ollama setup
python examples/basic_usage_example.py
```

### Command Line Usage
```bash
# Run full analysis (requires Ollama setup)
python main.py

# Use specific model
OLLAMA_MODEL=qwen2.5-math:7b python main.py
```

## Contributing

We welcome contributions to improve the Aura P.A. Agent! Here's how you can help:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Set up the development environment following the installation instructions
4. Make your changes and add tests
5. Run the test suite: `pytest tests/`
6. Submit a pull request

### Areas for Contribution
- **New LLM Integrations**: Add support for additional language models
- **Enhanced Analytics**: Improve mathematical analysis algorithms
- **Data Connectors**: Build integrations with more data sources
- **UI Development**: Create web interface for easier interaction
- **Documentation**: Improve guides and examples

### Reporting Issues
- Use GitHub Issues to report bugs or request features
- Include detailed reproduction steps and environment information
- Provide sample data when relevant (ensure no sensitive information)

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Add docstrings for all public functions and classes
- Include unit tests for new functionality

## License and Contact

### License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Contact Information
- **Project Repository**: [https://github.com/Catafal/aura-P.A.-agent](https://github.com/Catafal/aura-P.A.-agent)
- **Issues & Support**: [GitHub Issues](https://github.com/Catafal/aura-P.A.-agent/issues)
- **Documentation**: Check the `instructions/` directory for detailed guides

### Maintainer
This project is maintained by the Catafal development team. For business inquiries or enterprise support, please open an issue on GitHub.

---

**Ready to optimize your business processes with AI?** Follow the installation guide above and start analyzing your processes today!