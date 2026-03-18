#!/usr/bin/env python3
"""Clinical system demo using currently implemented APIs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows where the console may default to cp1252/cp850.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root so local execution works from repo root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from sml.config import load_config
from sml.clinical_data_integration import ClinicalDataIntegrator
from sml.enhanced_biological_model import EnhancedBiologicalModel
from sml.patient_pipeline import run_patient_dna_pipeline
from sml.safety_validator import EnhancedSafetyValidator

# ---------------------------------------------------------------------------
# Synthetic DNA sequences used when no real FASTA files are provided.
# Each base unit repeats to produce ~13 kb of DNA.
# ---------------------------------------------------------------------------
_UNIT = (
    "ATCGATCGTAGCTAGCTAGCATGCTAGCTGACTAGCTAGCTGACTAGCTAGC"
    "ATCGATCGTAGCTAGCTAGCATGCTAGCTGACTAGCTAGCTGACTAGCTAGC"
)
_SYNTHETIC_NORMAL_DNA = _UNIT * 150  # ~15 000 nt

# Introduce a handful of somatic point-mutations to create detectable neoantigens.
_t = list(_UNIT * 150)
for _pos in (500, 1001, 1503, 2100, 2700):
    _t[_pos] = {"A": "G", "G": "A", "C": "T", "T": "C"}.get(_t[_pos], "G")
_SYNTHETIC_TUMOR_DNA = "".join(_t)


def _write_fasta(path: Path, header: str, sequence: str) -> None:
    """Write a DNA sequence to a FASTA file with 80-char line wrapping."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f">{header}"]
    for i in range(0, len(sequence), 80):
        lines.append(sequence[i : i + 80])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_demo(
    sample_id: str = "patient_001",
    normal_fasta: Path | None = None,
    tumor_fasta: Path | None = None,
    output_dir: Path | None = None,
) -> int:
    cfg = load_config()
    output_dir = output_dir or Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Part 1: Clinical data integration + biological model demo
    # ------------------------------------------------------------------
    integrator = ClinicalDataIntegrator(cfg.__dict__)
    model = EnhancedBiologicalModel()
    validator = EnhancedSafetyValidator()

    record = integrator.integrate_patient_data(sample_id)

    genomic_data = {
        "sample_id": sample_id,
        "cancer_type": "lung_adenocarcinoma",
        "mutations": {"KRAS": "G12C", "TP53": "R175H", "EGFR": "L858R"},
        "sequenced_bases": 30000000,
        "hla_alleles": ["HLA-A*02:01", "HLA-A*03:01"],
        "pd_l1_expression": 0.45,
    }
    immune_data = {
        "patient_id": sample_id,
        "t_cell_infiltration": 0.65,
        "immune_cell_counts": {},
        "cytokine_levels": {"IL-2": 0.5, "IFN-gamma": 0.8},
        "tcr_diversity": 0.7,
        "immune_exhaustion": 0.3,
    }

    analysis = model.analyze_patient_sample(genomic_data, immune_data)

    mrna_construct = {
        "sequence": "AUGCGAUC" * 400,
        "length": 3200,
        "stability_score": 0.6,
        "immunogenicity_score": 0.4,
        "5_utr": True,
        "kozak": True,
        "coding_sequence": True,
        "3_utr": True,
        "poly_a": True,
        "dose_recommendation": 120,
    }
    validation = validator.validate_complete_pipeline(
        dna_sequence="ATCGATCGATCG" * 100,
        neoantigens=["SIINFEKL", "GILGFVFTL"],
        mrna_construct=mrna_construct,
    )
    report = validator.generate_safety_report(validation)

    clinical_summary = {
        "patient_data_found": record is not None,
        "response_score": analysis["response_prediction"]["response_score"],
        "treatment_strategy": analysis["treatment_plan"]["treatment_strategy"],
        "recommended_dose": analysis["treatment_plan"]["recommended_dose"],
        "safety_status": report["summary"]["overall_status"],
        "critical_issues": report["summary"]["critical_issues"],
        "warnings": report["summary"]["warnings"],
    }

    print("Clinical run completed")
    print(json.dumps(clinical_summary, indent=2))

    # ------------------------------------------------------------------
    # Part 2: Real FASTA -> neoantigen -> mRNA output pipeline
    # ------------------------------------------------------------------
    if normal_fasta is None:
        normal_fasta = output_dir / f"{sample_id}_normal.fasta"
        _write_fasta(normal_fasta, f"{sample_id}_normal", _SYNTHETIC_NORMAL_DNA)
        print(f"[pipeline] Synthetic normal FASTA written: {normal_fasta}")

    if tumor_fasta is None:
        tumor_fasta = output_dir / f"{sample_id}_tumor.fasta"
        _write_fasta(tumor_fasta, f"{sample_id}_tumor", _SYNTHETIC_TUMOR_DNA)
        print(f"[pipeline] Synthetic tumor FASTA written:  {tumor_fasta}")

    output_json = output_dir / f"pipeline_{sample_id}.json"
    output_mrna_fasta = output_dir / f"{sample_id}_mrna_construct.fasta"

    print(f"\n[pipeline] Running DNA -> neoantigen -> mRNA pipeline for {sample_id} ...")
    pipeline_report = run_patient_dna_pipeline(
        sample_id=sample_id,
        normal_fasta_path=normal_fasta,
        tumor_fasta_path=tumor_fasta,
        output_json_path=output_json,
        output_mrna_fasta_path=output_mrna_fasta,
        max_binding_affinity_nm=500.0,
        min_immunogenicity=0.30,
        min_peptide_stability=0.25,
        max_warning_count=12,
    )

    decision = pipeline_report["decision"]
    mrna = pipeline_report.get("mrna_construct") or {}
    safety_summary = (pipeline_report.get("safety_report") or {}).get("summary") or {}

    print("\nPIPELINE SUMMARY")
    print("=" * 42)
    print(f"  Sample ID:             {sample_id}")
    print(f"  Mutations detected:    {pipeline_report['mutation_report']['total_mutations']}")
    print(f"  Selected neoantigens:  {len(pipeline_report['selected_neoantigens'])}")
    if mrna:
        print(f"  mRNA length:           {mrna.get('length')} nt")
        print(f"  mRNA stability score:  {mrna.get('stability_score', 'N/A')}")
        print(f"  Delivery efficiency:   {mrna.get('delivery_efficiency', 'N/A')}")
    print(f"  Safety status:         {safety_summary.get('overall_status', 'N/A')}")
    print(f"  Critical issues:       {safety_summary.get('critical_issues', 'N/A')}")
    print(f"  Approved for research: {decision['approved_for_research']}")
    for reason in decision.get("reasons", []):
        print(f"    - {reason}")
    print(f"\n  JSON report:  {output_json}")
    if output_mrna_fasta.exists():
        print(f"  mRNA FASTA:   {output_mrna_fasta}")

    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Clinical system run")
    p.add_argument("--sample-id", default="patient_001", help="Patient / sample identifier")
    p.add_argument(
        "--normal-fasta",
        type=Path,
        default=None,
        help="Normal-tissue DNA FASTA (synthetic generated when omitted)",
    )
    p.add_argument(
        "--tumor-fasta",
        type=Path,
        default=None,
        help="Tumor-tissue DNA FASTA (synthetic generated when omitted)",
    )
    p.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output directory")
    return p.parse_args()


if __name__ == "__main__":
    _args = _parse_args()
    raise SystemExit(
        run_demo(
            sample_id=_args.sample_id,
            normal_fasta=_args.normal_fasta,
            tumor_fasta=_args.tumor_fasta,
            output_dir=_args.output_dir,
        )
    )
