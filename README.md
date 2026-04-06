# OncoSML: Cancer Vaccine Learning System

OncoSML is an end-to-end research platform for personalized cancer vaccine workflow exploration.
It combines mutation analysis, neoantigen filtering, mRNA construct design, safety validation, and evidence-oriented clinical-readiness tooling.

## What This Repository Delivers

- FASTA-based normal-vs-tumor workflow for mutation and candidate generation
- Multi-step decision gates for affinity, immunogenicity, peptide stability, and safety findings
- JSON-first outputs designed for traceability and downstream reporting
- Real-world genomics stack orchestration interface (FASTQ/BAM/VCF inputs)
- Status API and dashboard for runtime visibility
- Clinical-readiness framework with IQ/OQ/PQ protocols, evidence logs, and execution scripts

## High-Level Architecture

```
main.py
  -> command-line orchestration
  -> run-patient-pipeline / run-realworld-stack / run-service

sml/
  -> domain modules (dna_analyzer, mrna_designer, safety_validator)
  -> advanced modules (immunogenicity, HLA binding, PK, trial validator)
  -> compliance/security modules (audit trail, e-signature, privacy, RBAC)
  -> status API server

validation/
  -> IQ/OQ/PQ protocols and evidence logs
  -> executable TS-001..TS-010 evidence scripts
  -> deployment record templates

docs/
  -> readiness plans, SOPs, release controls, signoff forms
```

## Quick Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional, for container workflows)

### Install (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Install (bash)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI Command Reference

### Platform Runtime

```bash
python main.py run-once
python main.py run-loop --sleep-seconds 300
python main.py run-service --sleep-seconds 300 --host 127.0.0.1 --port 8787
python main.py serve-status --host 127.0.0.1 --port 8787
```

### Clinical Demo Commands

```bash
python main.py run-demo --patient-count 5
python main.py run-clinical --patient-id P001 --enable-safety --enable-modeling
```

### FASTA Pipeline Command (Primary Submission Flow)

```bash
python main.py run-patient-pipeline \
  --sample-id patient_submission \
  --normal-fasta path/to/normal.fasta \
  --tumor-fasta path/to/tumor.fasta \
  --hla-allele HLA-A*02:01 \
  --output-json outputs/submissions/pipeline_patient_submission.json \
  --output-mrna-fasta outputs/submissions/patient_submission_mrna_construct.fasta
```

Primary outputs:

- `pipeline_<sample_id>.json`
- `<sample_id>_mrna_construct.fasta` (if construct produced)

### Packaged Submission Mode

```bash
python main.py run-submission \
  --sample-id patient_submission \
  --output-root outputs/submissions
```

### Real-World Stack Orchestration

Dry run using pre-called variants:

```bash
python main.py run-realworld-stack \
  --patient-id P001 \
  --reference-fasta path/to/reference.fa \
  --tumor-vcf path/to/tumor.somatic.vcf.gz \
  --dry-run
```

FASTQ mode:

```bash
python main.py run-realworld-stack \
  --patient-id P001 \
  --reference-fasta path/to/reference.fa \
  --normal-fastq-r1 path/to/normal_R1.fastq.gz \
  --normal-fastq-r2 path/to/normal_R2.fastq.gz \
  --tumor-fastq-r1 path/to/tumor_R1.fastq.gz \
  --tumor-fastq-r2 path/to/tumor_R2.fastq.gz
```

Output root:

- `outputs/realworld/<patient_id>/clinical_stack_<patient_id>.json`

## Status API and Dashboard

Dashboard:

```bash
streamlit run dashboard.py
```

Status API:

```bash
python main.py serve-status --host 127.0.0.1 --port 8787
```

Endpoints:

- `/`
- `/health`
- `/status`

## Deployment Options

### Standard Local Container

```bash
docker build -t oncosml:latest .
docker run --rm -p 8787:8787 oncosml:latest
```

### Multi-Service Compose

```bash
docker compose up --build
```

Services:

- Status API: `http://localhost:8787`
- Dashboard: `http://localhost:8501`

### Clinical Compose Baseline

```bash
docker compose -f docker-compose.clinical.yml up --build
```

## Testing

Run automated tests:

```bash
pytest tests -v
```

## Clinical Validation Toolkit

The repository includes a technical validation framework for software-layer readiness.

Core documents:

- `validation/IQ_Installation_Qualification.md`
- `validation/OQ_Operational_Qualification.md`
- `validation/PQ_Performance_Qualification.md`
- `validation/IQ_EVIDENCE_LOG.md`
- `validation/OQ_EVIDENCE_LOG.md`
- `docs/CLINICAL_READINESS_ACTION_PLAN.md`
- `docs/ENVIRONMENT_RELEASE_CONTROLS.md`
- `docs/PHASE1_READINESS_CHECKLIST.md`

Execution scripts:

- `validation/test_scripts/TS-001_Service_Endpoints.py`
- `validation/test_scripts/TS-002_Patient_Pipeline_Output.py`
- `validation/test_scripts/TS-003_Backup_Restore_Smoke.py`
- `validation/test_scripts/TS-004_Access_Control_RBAC.py`
- `validation/test_scripts/TS-005_Audit_and_ESignature.py`
- `validation/test_scripts/TS-006_Privacy_Deidentification.py`
- `validation/test_scripts/TS-007_PQ_Core_Scenarios.py`
- `validation/test_scripts/TS-008_IQ_Technical_Baseline.py`
- `validation/test_scripts/TS-009_Incident_Drill_Simulation.py`
- `validation/test_scripts/TS-010_Operational_Handoff_DryRun.py`

Quickstart:

- `docs/OQ_EXECUTION_QUICKSTART.md`

## GMP and Readiness Assets

- GMP framework: `docs/GMP_MANUFACTURING_FRAMEWORK.md`
- GMP template: `templates/gmp_batch_record_template.json`
- Readiness scorecard: `templates/phase1_go_no_go_scorecard.json`
- Signoff packet: `docs/SIGNOFF_PACKET.md`
- QA approval sheet: `docs/QA_APPROVAL_SHEET.md`
- Incident drill worksheet: `docs/INCIDENT_DRILL_WORKSHEET.md`

## Current Readiness Boundary

Software technical groundwork and technical evidence tooling are implemented in-repo.
Final clinical deployment readiness still depends on external regulated execution steps such as regulatory submissions, GMP manufacturing readiness, nonclinical evidence, governance approvals, and signed QA/clinical documentation.

## Notes

- The real-world stack command is an orchestration layer and expects external tools for non-dry-run execution.
- Dry-run mode is recommended first to validate toolchain wiring and artifact generation.
- This repository is intended for research workflows, not clinical diagnosis or treatment decisions.

## License

MIT (see LICENSE if present).

## Disclaimer

This software is for research and educational use only. It is not medical advice and must not be used as a substitute for clinical judgment or regulatory-approved clinical workflows.
