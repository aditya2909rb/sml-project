#!/usr/bin/env python3
"""Clinical system demo using currently implemented APIs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root so local execution works from repo root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from sml.config import load_config
from sml.clinical_data_integration import ClinicalDataIntegrator
from sml.enhanced_biological_model import EnhancedBiologicalModel
from sml.safety_validator import EnhancedSafetyValidator


def run_demo() -> int:
    cfg = load_config()

    integrator = ClinicalDataIntegrator(cfg.__dict__)
    model = EnhancedBiologicalModel()
    validator = EnhancedSafetyValidator()

    # No real clinical backend is configured in this repo, so this may be None.
    patient_id = "demo_patient_001"
    record = integrator.integrate_patient_data(patient_id)

    genomic_data = {
        "sample_id": patient_id,
        "cancer_type": "lung_adenocarcinoma",
        "mutations": {"KRAS": "G12C", "TP53": "R175H", "EGFR": "L858R"},
        "sequenced_bases": 30000000,
        "hla_alleles": ["HLA-A*02:01", "HLA-A*03:01"],
        "pd_l1_expression": 0.45,
    }
    immune_data = {
        "patient_id": patient_id,
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

    summary = {
        "patient_data_found": record is not None,
        "response_score": analysis["response_prediction"]["response_score"],
        "treatment_strategy": analysis["treatment_plan"]["treatment_strategy"],
        "recommended_dose": analysis["treatment_plan"]["recommended_dose"],
        "safety_status": report["summary"]["overall_status"],
        "critical_issues": report["summary"]["critical_issues"],
        "warnings": report["summary"]["warnings"],
    }

    print("Clinical demo completed")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_demo())
