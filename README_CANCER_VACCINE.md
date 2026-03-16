# Cancer Vaccine AI System

A comprehensive Self-Maintaining Learning (SML) system for cancer vaccine development using machine learning, genomics data, and continuous learning from GitHub repositories.

## Overview

This AI system combines:
- **cBioPortal Integration**: Downloads and processes real cancer genomics datasets
- **GitHub Continuous Learning**: Learns from bioinformatics repositories and tools
- **DNA Mutation Analysis**: Detects and classifies cancer mutations
- **Neoantigen Prediction**: Identifies potential immune targets
- **mRNA Vaccine Design**: Creates personalized vaccine constructs
- **Automated Training Pipeline**: GitHub Actions workflow for continuous improvement

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- GitHub account (for GitHub Actions)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aditya2909rb/sml-project.git
   cd sml-project
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your preferences
   ```

### Basic Usage

1. **Download cBioPortal Data:**
   ```bash
   python scripts/download_cbioportal_data.py
   ```

2. **Run GitHub Training:**
   ```bash
   python -m sml.github_trainer
   ```

3. **Train Cancer Vaccine Model:**
   ```bash
   python main.py run-once
   ```

4. **Start Continuous Learning:**
   ```bash
   python main.py run-loop --sleep-seconds 300
   ```

5. **Monitor Progress:**
   ```bash
   streamlit run dashboard.py
   ```

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   cBioPortal    │    │   GitHub Repos   │    │  Local Training │
│   Data Sources  │───▶│   (Bioinformatics│───▶│  & Validation   │
│                 │    │   & ML Tools)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Cancer Vaccine AI Model                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ DNA Mutation    │ Neoantigen      │ mRNA Vaccine                │
│ Analysis        │ Prediction      │ Design                      │
└─────────────────┴─────────────────┴─────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              Continuous Learning Loop                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Self-Healing│  │ Model Scaling│  │ State Persistence       │  │
│  │ & Validation│  │ & Improvement│  │ & GitHub Integration    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. cBioPortal Data Integration
- **Automatic Download**: Fetches cancer genomics datasets from cBioPortal
- **Data Processing**: Converts MAF files to training samples
- **Mutation Analysis**: Classifies mutations by impact and driver probability
- **Combined Dataset**: Creates unified training dataset

### 2. GitHub Continuous Learning
- **Repository Discovery**: Finds relevant bioinformatics repositories
- **Code Analysis**: Extracts ML algorithms and bioinformatics tools
- **Knowledge Integration**: Updates model with latest research
- **Scheduled Training**: Runs every 6 hours automatically

### 3. Cancer Vaccine Model
- **Multi-Modal Learning**: Combines text classification with DNA analysis
- **Mutation Detection**: Identifies driver vs passenger mutations
- **Neoantigen Prediction**: Predicts immune system targets
- **Vaccine Design**: Creates optimized mRNA constructs

### 4. Automated Pipeline
- **GitHub Actions**: Complete CI/CD pipeline for training
- **Artifact Management**: Stores models, datasets, and reports
- **Monitoring Dashboard**: Real-time training progress visualization
- **State Persistence**: Maintains learning state across runs

## Key Features

### DNA Mutation Analysis
```python
from sml.dna_analyzer import DNAMutationAnalyzer

analyzer = DNAMutationAnalyzer()
report = analyzer.analyze_sample(
    sample_id="patient_001",
    normal_dna="ATCG...",
    tumor_dna="ATCA...",
    hla_allele="HLA-A*02:01"
)
```

### Neoantigen Prediction
```python
from sml.cancer_vaccine_model import CancerVaccineModel

model = CancerVaccineModel("model_store", n_features=262144)
analysis = model.analyze_dna_sample(
    sample_id="patient_001",
    normal_dna="ATCG...",
    tumor_dna="ATCA...",
    hla_allele="HLA-A*02:01"
)
```

### mRNA Vaccine Design
```python
from sml.mrna_designer import MRNAVaccineDesigner

designer = MRNAVaccineDesigner()
construct = designer.design_vaccine(neoantigens)
```

## GitHub Actions Pipeline

The automated pipeline includes:

1. **Setup & Download**: Environment setup and cBioPortal data download
2. **GitHub Training**: Continuous learning from repositories
3. **Model Training**: Cancer vaccine model training with combined datasets
4. **Continuous Learning**: Scheduled learning loops with state persistence
5. **Dashboard Deployment**: Monitoring dashboard updates
6. **Notifications**: Training completion notifications

### Pipeline Triggers
- **Push to main**: Automatic training on code changes
- **Pull requests**: Validation training
- **Scheduled**: Every 6 hours
- **Manual**: Via GitHub Actions UI with different modes

## Monitoring & Dashboard

### Streamlit Dashboard
```bash
streamlit run dashboard.py
```

Features:
- Training progress visualization
- Model performance metrics
- Dataset statistics
- Learning history tracking

### Status API
```bash
python main.py serve-status --host 127.0.0.1 --port 8787
```

Endpoints:
- `GET /` - Live browser dashboard
- `GET /health` - System health check
- `GET /status` - Detailed system status

## Configuration

### Environment Variables
```bash
# Database and model storage
SML_DB_PATH=sml_state.sqlite3
SML_MODEL_DIR=model_store

# cBioPortal data sources
SML_FEEDS=https://feeds.bbci.co.uk/news/rss.xml,https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml
SML_MAX_ITEMS_PER_FEED=50
SML_MIN_TEXT_LEN=30

# GitHub training
SML_GITHUB_ENABLED=true
SML_GITHUB_TOKEN=your_github_token_here

# Model scaling
SML_SCALING_ENABLED=true
SML_INITIAL_FEATURES=262144
SML_MAX_FEATURES=4194304
SML_FEATURE_LADDER=262144,524288,1048576,2097152,4194304

# Training parameters
SML_SCALE_EVERY_CYCLES=3
SML_SCALE_MIN_SAMPLES=80
SML_SCALE_MIN_ACCURACY=0.62

# Status API
SML_STATUS_HOST=127.0.0.1
SML_STATUS_PORT=8787
```

## Testing

### Unit Tests
```bash
pytest tests/
```

### Smoke Tests
```bash
python tests/test_smoke.py
```

### Integration Tests
```bash
# Test cBioPortal download
python scripts/download_cbioportal_data.py

# Test GitHub training
python -m sml.github_trainer

# Test model training
python main.py run-once
```

## Performance Metrics

The system tracks:
- **Training Accuracy**: Model performance on validation data
- **Mutation Detection Accuracy**: Precision of mutation identification
- **Neoantigen Prediction Accuracy**: Quality of immune target prediction
- **Vaccine Design Score**: Optimization of mRNA constructs
- **Learning Progress**: Parameter growth and model improvements

## Security & Safety

### Safety Validator
- Code quality checks with ruff and black
- Security vulnerability scanning
- Model validation and testing
- Automated self-healing capabilities

### Data Privacy
- No patient data storage
- Anonymized mutation analysis
- Secure GitHub token handling
- Encrypted artifact storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest ruff black

# Run linting
ruff check sml/ scripts/
black sml/ scripts/

# Run tests
pytest tests/
```

## Documentation

- [API Documentation](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Training Guide](docs/training.md)
- [Deployment Guide](docs/deployment.md)

## Troubleshooting

### Common Issues

1. **cBioPortal Download Failures**
   - Check internet connection
   - Verify cBioPortal API availability
   - Check rate limits

2. **GitHub Training Failures**
   - Verify GitHub token permissions
   - Check repository access
   - Monitor API rate limits

3. **Model Training Issues**
   - Check available memory
   - Verify dataset format
   - Monitor training logs

### Getting Help
- Create an issue on GitHub
- Check the troubleshooting guide
- Review system logs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- cBioPortal for providing cancer genomics data
- GitHub for hosting bioinformatics repositories
- Open source bioinformatics community
- Machine learning and immunology researchers

## Contact

For questions and support:
- Create a GitHub issue
- Email: [your-email@example.com]
- Project homepage: [https://github.com/aditya2909rb/sml-project](https://github.com/aditya2909rb/sml-project)

---

**Note**: This is a research project for educational purposes. Always consult with medical professionals for actual medical advice and treatment.