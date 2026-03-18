# OncoSML: Cancer Vaccine Learning System

OncoSML is a research-grade, end-to-end machine learning pipeline for personalized cancer vaccine exploration.
It combines sequence-based mutation analysis, neoantigen selection, mRNA construct design, and multi-stage safety validation.

## Core Capabilities

- DNA normal-vs-tumor analysis and mutation extraction
- Neoantigen candidate scoring (binding affinity, immunogenicity, stability)
- mRNA vaccine construct generation and optimization
- Strict biological safety validation gates with JSON reports
- Clinical workflow demo and command-line submission pipeline
- Real-world genomics stack orchestration (FASTQ/BAM/VCF-driven, toolchain hooks)
- Streamlit dashboard and lightweight status API

## Project Structure

```
main.py                          # CLI entry point
examples/clinical_demo.py        # End-to-end clinical run demo
sml/
  dna_analyzer.py                # Mutation and neoantigen analysis
  mrna_designer.py               # mRNA construct design
  safety_validator.py            # Safety and biological gate checks
  patient_pipeline.py            # FASTA -> neoantigen -> mRNA -> JSON decision
  clinical_genomics_stack.py     # Real-world stack orchestration layer
  clinical_data_integration.py   # Clinical data integration utilities
  enhanced_biological_model.py   # Extended biological modeling
  status_api.py                  # HTTP status endpoints
  ...
dashboard.py                     # Streamlit monitoring dashboard
requirements.txt
tests/
```

## Setup

### Prerequisites

- Python 3.10+
- Git

### Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Main Commands

### 1) Run a single learning cycle

```bash
python main.py run-once
```

### 2) Run continuous service loop

```bash
python main.py run-service --sleep-seconds 300
```

### 3) Run clinical workflow demo

```bash
python main.py run-clinical
python main.py run-demo
```

### 4) Run patient submission pipeline (FASTA in, mRNA + JSON out)

```bash
python main.py run-submission \
  --sample-id patient_submission \
  --normal-fasta path/to/normal.fasta \
  --tumor-fasta path/to/tumor.fasta \
  --output-dir outputs/submissions
```

Outputs include:

- `pipeline_<sample_id>.json`
- `<sample_id>_mrna_construct.fasta`

### 5) Run real-world genomics stack orchestration

```bash
python main.py run-realworld-stack \
  --patient-id P001 \
  --reference-fasta path/to/reference.fa \
  --tumor-vcf path/to/tumor.somatic.vcf.gz \
  --dry-run
```

For full FASTQ mode:

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

## Real-World Stack Stages

The orchestration layer supports staged execution/reporting for:

- Input validation
- FASTQ quality control and alignment hooks
- Somatic variant calling/filtering hooks
- Consequence mapping hooks (VEP)
- HLA typing hooks (OptiType)
- MHC prediction hooks (netMHCpan and MHCflurry)
- Manufacturability and release-QC gate

Each stage is written into a machine-readable report with status and artifact paths.

## Safety and Decision Gates

Pipeline approval can depend on thresholds such as:

- Maximum binding affinity (nM)
- Minimum immunogenicity score
- Minimum peptide stability score
- Maximum warning count
- Zero critical safety findings

Safety reports are JSON serializable and include:

- Summary counts (`critical_issues`, `warnings`, `passed_checks`)
- Detailed categorized findings
- Recommendation list

## Dashboard and API

### Dashboard

```bash
streamlit run dashboard.py
```

### Status API

```bash
python main.py serve-status --host 127.0.0.1 --port 8787
```

## Testing

```bash
pytest tests -v
```

## Notes

- The real-world stack command is an orchestration layer and expects external tools to be installed for non-dry-run execution.
- Dry-run mode is recommended first to validate command wiring and output structure.
- This repository is intended for research workflows, not clinical diagnosis or treatment decisions.

## License

MIT (see LICENSE if present).

## Disclaimer

This software is for research and educational use only. It is not medical advice and must not be used as a substitute for clinical judgment or regulatory-approved clinical workflows.
