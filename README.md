# OncoSML: Cancer Vaccine Learning System

OncoSML is a self-maintaining machine learning system for cancer-vaccine research workflows.
Its primary GitHub automation path downloads cBioPortal datasets, stores dataset snapshots, trains on those datasets, and exposes status tracking.

## What This Project Does

- Downloads and processes cancer genomics data from cBioPortal.
- Trains automatically on cBioPortal-derived datasets on GitHub.
- Optionally runs a separate manual text-learning loop for experimentation.
- Applies guarded self-healing (lint/format only) when checks fail.
- Tracks training cycles, events, and model growth in SQLite.
- Exposes status endpoints and a local Streamlit dashboard.
- Supports scheduled GitHub Actions automation.

## Main Components

- sml/: core learning and cancer-vaccine modules
- scripts/download_cbioportal_data.py: cBioPortal data download and processing
- main.py: CLI entrypoint
- dashboard.py: Streamlit tracker UI
- .github/workflows/cancer-vaccine-training.yml: automatic cBioPortal download, dataset persistence, and training pipeline

## Quick Start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py run-loop --sleep-seconds 120
```

In another terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run dashboard.py
```

## CLI Commands

Run one cycle:

```bash
python main.py run-once
```

Run continuous loop:

```bash
python main.py run-loop --sleep-seconds 300
```

Serve status API only:

```bash
python main.py serve-status --host 127.0.0.1 --port 8787
```

Run loop plus status API together:

```bash
python main.py run-service --sleep-seconds 30 --host 127.0.0.1 --port 8787
```

## Status and Dashboard

- Streamlit dashboard: streamlit run dashboard.py
- API endpoints:
- GET /
- GET /health
- GET /status

## GitHub Automation

GitHub workflow included:

1. OncoSML Cancer Training Pipeline
- Downloads cBioPortal data.
- Prepares combined dataset with diagnostics and fallbacks.
- Runs GitHub training.
- Trains model from prepared dataset.
- Commits dataset snapshots to the cbioportal-datasets branch.
- Uploads training artifacts.
- Runs automatically on push and every 5 minutes on schedule.

## Configuration

Copy .env.example to .env and adjust values.

Common settings:

- SML_DB_PATH
- SML_MODEL_DIR
- SML_STATUS_HOST
- SML_STATUS_PORT
- SML_PERSIST_ENABLED
- SML_STATE_BRANCH
- SML_SCALING_ENABLED

## Safety and Limits

- Self-healing is restricted to safe formatting and lint fixes.
- True unlimited runtime is not possible on GitHub-hosted runners.
- Use self-hosted runners for long-running continuous execution.

## Testing

```bash
pytest tests/
python tests/test_smoke.py
```

## Project URL

https://github.com/aditya2909rb/sml-project

## Note

This repository is for research and engineering experimentation, not medical advice.
