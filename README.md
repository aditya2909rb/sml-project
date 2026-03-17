# OncoSML: Cancer Vaccine Learning System

OncoSML is an end-to-end autonomous machine-learning system for cancer vaccine research. It continuously ingests biomedical data from the web, trains and self-heals an online classifier, runs biological safety validation pipelines, and exposes a live Streamlit dashboard and HTTP status API â€” all from a single entry point.

## What This Project Does

- **Continuous Learning Loop**: Ingests RSS/Atom feeds, Hacker News, Reddit, and arXiv papers on a configurable schedule, deduplicates them, and incrementally trains an online `SGDClassifier`.
- **Cancer Vaccine Classifier**: `model_store/cancer_vaccine_classifier.joblib` â€” a persisted scikit-learn model for cancer-vaccineâ€“related text classification.
- **DNA / mRNA / Neoantigen Analysis**: Validates biological sequences and vaccine constructs through a multi-level safety pipeline.
- **Enhanced Biological Modeling**: Genomic analysis, immune-response simulation, pharmacokinetics, and clinical-trial simulation.
- **Clinical Data Integration**: Structured patient demographics, diagnosis, and biomarker data with quality scoring and validation.
- **Self-Healing**: Detects model drift or data starvation and attempts automatic recovery.
- **Git-Persisted State**: Optionally commits SQLite state and model checkpoints to a dedicated `sml-state` branch.
- **Status API + Dashboard**: HTTP health/status API (default `127.0.0.1:8787`) and a Streamlit monitoring dashboard.

## Project Structure

```
sml-project/
â”œâ”€â”€ main.py                        # CLI entry point (run-once | run-loop | serve-status | run-service | run-clinical | run-demo)
â”œâ”€â”€ dashboard.py                   # Streamlit monitoring dashboard
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ sml_state.sqlite3              # Runtime state database (cycles, events, accuracy)
â”œâ”€â”€ model_store/
â”‚   â””â”€â”€ cancer_vaccine_classifier.joblib   # Persisted SGDClassifier
â”œâ”€â”€ sml/
â”‚   â”œâ”€â”€ config.py                  # Environment-variable-driven SMLConfig dataclass
â”‚   â”œâ”€â”€ runner.py                  # Orchestrates ingest â†’ train â†’ heal â†’ persist cycle
â”‚   â”œâ”€â”€ data_ingest.py             # Fetches RSS, HN, Reddit, arXiv samples
â”‚   â”œâ”€â”€ model.py                   # OnlineTextModel (SGDClassifier + TF-IDF, incremental)
â”‚   â”œâ”€â”€ healing.py                 # Self-healing: drift detection & recovery
â”‚   â”œâ”€â”€ state.py                   # SQLite helpers for cycles, events, accuracy logs
â”‚   â”œâ”€â”€ git_persist.py             # Commits state/model to sml-state branch
â”‚   â”œâ”€â”€ status_api.py              # Lightweight HTTP status/health API
â”‚   â”œâ”€â”€ cancer_vaccine_model.py    # Cancer-vaccineâ€“specific model & feature engineering
â”‚   â”œâ”€â”€ dna_analyzer.py            # DNA sequence analysis utilities
â”‚   â”œâ”€â”€ mrna_designer.py           # mRNA construct design
â”‚   â”œâ”€â”€ safety_validator.py        # Multi-level safety/validation pipeline
â”‚   â”œâ”€â”€ enhanced_biological_model.py  # Genomic, immune, pharmacokinetic & trial simulation
â”‚   â”œâ”€â”€ clinical_data_integration.py  # Patient data structures, quality scoring, validation
â”‚   â””â”€â”€ github_trainer.py         # GitHub-Actionsâ€“compatible trainer helpers
â”œâ”€â”€ examples/
â”‚   â””â”€â”€ clinical_demo.py           # End-to-end clinical workflow demo
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ build_monitor_dashboard.py # Builds the monitoring dashboard artefacts
â”‚   â””â”€â”€ download_cbioportal_data.py # Downloads cBioPortal cancer genomics data
â””â”€â”€ tests/
    â”œâ”€â”€ test_smoke.py              # Config load & README existence checks
    â””â”€â”€ test_clinical_integration.py  # 21 unit/integration tests for clinical modules
```

## Key Modules

| Module | Purpose |
|---|---|
| `sml/runner.py` | Main cycle: fetch â†’ deduplicate â†’ train â†’ self-heal â†’ optionally git-persist |
| `sml/model.py` | `OnlineTextModel` â€” incremental SGD with TF-IDF hashing, feature scaling |
| `sml/data_ingest.py` | Pulls text samples from RSS feeds, HN, Reddit JSON, arXiv API |
| `sml/cancer_vaccine_model.py` | Domain-specific classifier for cancer vaccine literature |
| `sml/dna_analyzer.py` | GC-content, motif search, restriction-site detection, BLAST-style alignment |
| `sml/mrna_designer.py` | Codon optimisation, UTR design, stability scoring |
| `sml/safety_validator.py` | DNA / neoantigen / mRNA / vaccine-construct multi-level safety checks |
| `sml/enhanced_biological_model.py` | Genomic profiling, immune-response ODE simulation, PK modeling, trial simulation |
| `sml/clinical_data_integration.py` | Patient demographics, diagnosis, biomarker data, quality scoring |
| `sml/healing.py` | Detects accuracy drop / data starvation and triggers recovery |
| `sml/git_persist.py` | Auto-commits SQLite DB + model file to `sml-state` branch |
| `sml/status_api.py` | `/health`, `/status` HTTP endpoints for monitoring |

## Quick Start

### Prerequisites

- Python 3.10+
- Git (for state persistence, optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/aditya2909rb/sml-project.git
cd sml-project

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Running

```bash
# Run one ingest/train/heal cycle
python main.py run-once

# Run continuously (every 5 minutes)
python main.py run-loop --sleep-seconds 300

# Serve the status API only
python main.py serve-status --host 127.0.0.1 --port 8787

# Run loop + status API together (recommended)
python main.py run-service --sleep-seconds 300

# Run clinical data integration and analysis
python main.py run-clinical

# Run clinical system demonstration
python main.py run-demo

# Open the Streamlit dashboard
streamlit run dashboard.py
```

### Example: Patient Analysis

```python
from sml.clinical_data_integration import ClinicalDataIntegrator
from sml.enhanced_biological_model import EnhancedBiologicalModel
from sml.safety_validator import EnhancedSafetyValidator
from sml.config import load_config

config = load_config()
bio_model = EnhancedBiologicalModel()
safety_validator = EnhancedSafetyValidator()

# Analyse a patient sample
result = bio_model.analyze_patient_sample(
    genomic_data={"mutations": [...], "tumor_type": "LUAD"},
    immune_data={"cd8_count": 1200, "pd1_expression": 0.4},
)

# Validate the derived vaccine construct
validation = safety_validator.validate_complete_pipeline(
    dna_sequence=result["dna_sequence"],
    neoantigens=result["neoantigens"],
    mrna_construct=result["mrna_construct"],
)
report = safety_validator.generate_safety_report(validation)
print(report)
```

## Configuration

All settings are driven by environment variables (or `.env` file):

```bash
# Core
SML_DB_PATH=sml_state.sqlite3
SML_MODEL_DIR=model_store
SML_STATUS_HOST=127.0.0.1
SML_STATUS_PORT=8787

# Data sources
SML_HN_ENABLED=true
SML_HN_MAX_ITEMS=100
SML_REDDIT_ENABLED=true
SML_REDDIT_SUBREDDITS=technology,MachineLearning,artificial
SML_ARXIV_ENABLED=true
SML_ARXIV_QUERY=cat:cs.LG OR cat:cs.AI

# Model scaling
SML_SCALING_ENABLED=true
SML_INITIAL_FEATURES=262144      # 2^18
SML_MAX_FEATURES=4194304         # 2^22
SML_SCALE_EVERY_CYCLES=3
SML_SCALE_MIN_ACCURACY=0.62

# Git persistence
SML_PERSIST_ENABLED=false
SML_STATE_BRANCH=sml-state
SML_PERSIST_EVERY_CYCLES=1
SML_PERSIST_MIN_BATCH_ACCURACY=0.55

# Clinical system
SML_CLINICAL_ENABLED=true
SML_CLINICAL_DATA_SOURCES=EHR,CLINICAL_TRIALS,CANCER_REGISTRIES,BIOMEDICAL_DATABASES

# Safety validation
SML_SAFETY_VALIDATION_ENABLED=true
SML_SAFETY_CRITICAL_THRESHOLD=0.8
SML_SAFETY_WARNING_THRESHOLD=0.6
SML_ETHICAL_COMPLIANCE_ENABLED=true
SML_REGULATORY_COMPLIANCE_ENABLED=true
SML_PATIENT_DATA_ENCRYPTION=true
SML_AUDIT_LOGGING_ENABLED=true
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | System status page |
| GET | `/health` | Health check (returns `{"status":"ok"}`) |
| GET | `/status` | Detailed system status (cycle count, accuracy, model info) |

## Testing

```bash
# Run the full test suite (23 tests)
pytest tests/ -v

# Specific suites
pytest tests/test_smoke.py
pytest tests/test_clinical_integration.py
```

All 23 tests pass on Python 3.13 with the versions pinned in `requirements.txt`.

## Tech Stack

| Layer | Library |
|---|---|
| ML / classifier | scikit-learn (SGDClassifier, HashingVectorizer) |
| Data ingestion | feedparser, aiohttp, requests |
| Biological analysis | biopython, scipy, numpy |
| Dashboard | Streamlit, matplotlib, seaborn |
| State storage | SQLite (via stdlib `sqlite3`) |
| Git automation | GitPython |
| Validation / serialisation | pydantic-settings, cryptography, PyJWT |
| Testing | pytest |
| Linting / formatting | ruff, black |

## Security & Privacy

- Patient data encryption flag (`SML_PATIENT_DATA_ENCRYPTION`)
- JWT-based API authentication support (`pyjwt`)
- Audit-logging for all data access (`SML_AUDIT_LOGGING_ENABLED`)
- Safety-critical thresholds enforced before any model persistence
- No raw patient data is committed to git â€” only anonymised state metadata

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes and add tests
4. Run `pytest tests/` and `ruff check sml/` before committing
5. Submit a pull request

## Links

- **Repository**: https://github.com/aditya2909rb/sml-project
- **Issues**: https://github.com/aditya2909rb/sml-project/issues
- **Discussions**: https://github.com/aditya2909rb/sml-project/discussions

## License

MIT License â€” see [LICENSE](LICENSE) for details.

## Disclaimer

This software is for research and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.


