from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from sml.dna_analyzer import DNAMutationAnalyzer
from sml.gmp_framework import build_gmp_batch_record
from sml.mrna_designer import MRNAVaccineDesigner
from sml.safety_validator import EnhancedSafetyValidator, SafetyLevel


logger = logging.getLogger(__name__)


def _read_fasta_sequence(path: Path) -> str:
    """Read a FASTA file and return its merged sequence in uppercase."""
    if not path.exists():
        raise FileNotFoundError(f"FASTA file not found: {path}")

    sequence_parts: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(">"):
            continue
        sequence_parts.append(line)

    sequence = "".join(sequence_parts).upper()
    if not sequence:
        raise ValueError(f"No sequence content found in FASTA file: {path}")
    invalid_bases = set(sequence) - {"A", "C", "G", "T", "N"}
    if invalid_bases:
        raise ValueError(f"Invalid FASTA bases in {path}: {''.join(sorted(invalid_bases))}")
    return sequence


def _safety_level_counts(validation_results: dict[str, list[Any]]) -> dict[str, int]:
    counts = {
        "CRITICAL": 0,
        "WARNING": 0,
        "INFO": 0,
        "PASS": 0,
    }
    for _, results in validation_results.items():
        for result in results:
            if hasattr(result, "level"):
                level = result.level.value
            else:
                level = str(result.get("level", "INFO"))
            counts[level] += 1
    return counts


def run_patient_dna_pipeline(
    sample_id: str,
    normal_fasta_path: Path,
    tumor_fasta_path: Path,
    hla_allele: str = "HLA-A*02:01",
    output_json_path: Path | None = None,
    output_mrna_fasta_path: Path | None = None,
    max_binding_affinity_nm: float = 200.0,
    min_immunogenicity: float = 0.6,
    min_peptide_stability: float = 0.5,
    max_warning_count: int = 3,
) -> dict[str, Any]:
    """Run the patient DNA -> neoantigen -> mRNA pipeline with strict safety gates."""
    logger.info("Starting patient DNA pipeline", extra={"sample_id": sample_id})
    try:
        normal_dna = _read_fasta_sequence(normal_fasta_path)
        tumor_dna = _read_fasta_sequence(tumor_fasta_path)

        analyzer = DNAMutationAnalyzer()
        mrna_designer = MRNAVaccineDesigner()
        safety_validator = EnhancedSafetyValidator()

        report = analyzer.analyze_sample(
            sample_id=sample_id,
            normal_dna=normal_dna,
            tumor_dna=tumor_dna,
            hla_allele=hla_allele,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline failed before neoantigen selection", extra={"sample_id": sample_id})
        raise RuntimeError(f"Patient pipeline failed for {sample_id}") from exc

    neoantigen_candidates: list[dict[str, Any]] = []
    selected_neoantigen_sequences: list[str] = []

    for neo in report.predicted_neoantigens:
        candidate = {
            "peptide": neo.peptide_sequence,
            "hla_allele": neo.hla_allele,
            "binding_affinity_nm": neo.binding_affinity,
            "immunogenicity_score": neo.immunogenicity_score,
            "stability_score": neo.stability_score,
            "mutation_position": neo.mutation.position,
            "mutation_consequence": neo.mutation.consequence,
        }
        neoantigen_candidates.append(candidate)

        if (
            neo.binding_affinity <= max_binding_affinity_nm
            and neo.immunogenicity_score >= min_immunogenicity
            and neo.stability_score >= min_peptide_stability
        ):
            selected_neoantigen_sequences.append(neo.peptide_sequence)

    # Keep a unique, deterministic shortlist.
    selected_neoantigen_sequences = sorted(set(selected_neoantigen_sequences))[:10]

    mrna_construct = None
    safety_report = None
    safety_counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0, "PASS": 0}

    if selected_neoantigen_sequences:
        selected_metadata = []
        for cand in neoantigen_candidates:
            if cand["peptide"] in selected_neoantigen_sequences:
                selected_metadata.append(
                    {
                        "binding_affinity_nm": cand["binding_affinity_nm"],
                        "immunogenicity_score": cand["immunogenicity_score"],
                    }
                )

        construct = mrna_designer.design_vaccine(selected_neoantigen_sequences)
        # Designer currently emits DNA alphabet; normalize to RNA alphabet for
        # downstream mRNA safety validation.
        rna_sequence = construct.sequence.replace("T", "U")
        mrna_construct = {
            "sequence": rna_sequence,
            "length": len(rna_sequence),
            "gc_content": construct.gc_content,
            "stability_score": construct.stability_score,
            "immunogenicity_score": construct.immunogenicity_score,
            "delivery_efficiency": construct.delivery_efficiency,
            "optimizations_applied": construct.optimizations_applied,
            "5_utr": True,
            "kozak": True,
            "coding_sequence": True,
            "3_utr": True,
            "poly_a": True,
            "dose_recommendation": 120,
        }

        validation_results = safety_validator.validate_complete_pipeline(
            dna_sequence=tumor_dna,
            neoantigens=selected_neoantigen_sequences,
            mrna_construct=mrna_construct,
            neoantigen_metadata=selected_metadata,
        )
        safety_report = safety_validator.generate_safety_report(validation_results)
        safety_counts = _safety_level_counts(validation_results)
        logger.info(
            "Construct generated and validated",
            extra={
                "sample_id": sample_id,
                "gc_content": mrna_construct["gc_content"],
                "stability_score": mrna_construct["stability_score"],
                "warnings": safety_counts[SafetyLevel.WARNING.value],
            },
        )

    decision_reasons: list[str] = []

    if report.total_mutations <= 0:
        decision_reasons.append("No mutations detected in tumor vs normal DNA")

    if report.tumor_mutational_burden < 1.0:
        decision_reasons.append("Tumor mutational burden below strict threshold (1.0 mut/Mb)")

    if not selected_neoantigen_sequences:
        decision_reasons.append(
            "No neoantigens passed strict gates: "
            f"affinity <= {max_binding_affinity_nm} nM, "
            f"immunogenicity >= {min_immunogenicity}, "
            f"stability >= {min_peptide_stability}"
        )

    if mrna_construct is not None:
        if mrna_construct["stability_score"] < 0.55:
            decision_reasons.append("mRNA stability score below strict threshold (0.55)")
        if mrna_construct["delivery_efficiency"] < 0.50:
            decision_reasons.append("mRNA delivery efficiency below strict threshold (0.50)")

    if safety_report is not None:
        if safety_counts[SafetyLevel.CRITICAL.value] > 0:
            decision_reasons.append("Safety validator reported critical issues")
        if safety_counts[SafetyLevel.WARNING.value] > max_warning_count:
            decision_reasons.append(
                f"Safety validator warnings exceed strict threshold ({max_warning_count})"
            )

    approved_for_research = len(decision_reasons) == 0

    output: dict[str, Any] = {
        "sample_id": sample_id,
        "inputs": {
            "normal_fasta": str(normal_fasta_path),
            "tumor_fasta": str(tumor_fasta_path),
            "hla_allele": hla_allele,
            "normal_length": len(normal_dna),
            "tumor_length": len(tumor_dna),
        },
        "mutation_report": {
            "total_mutations": report.total_mutations,
            "driver_mutations": len(report.driver_mutations),
            "passenger_mutations": len(report.passenger_mutations),
            "tumor_mutational_burden": report.tumor_mutational_burden,
            "microsatellite_status": report.microsatellite_status,
        },
        "neoantigen_candidates": neoantigen_candidates,
        "selected_neoantigens": selected_neoantigen_sequences,
        "mrna_construct": mrna_construct,
        "safety_report": safety_report,
        "decision": {
            "approved_for_research": approved_for_research,
            "reasons": decision_reasons,
            "strict_thresholds": {
                "max_binding_affinity_nm": max_binding_affinity_nm,
                "min_immunogenicity": min_immunogenicity,
                "min_peptide_stability": min_peptide_stability,
                "max_warning_count": max_warning_count,
            },
        },
    }

    if mrna_construct is not None:
        output["gmp_release_record"] = build_gmp_batch_record(sample_id, mrna_construct)

    if output_json_path is None:
        output_json_path = Path("outputs") / f"patient_pipeline_{sample_id}.json"
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    if output_mrna_fasta_path is not None and mrna_construct is not None:
        output_mrna_fasta_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f">{sample_id}_mrna_construct",
        ]
        seq = mrna_construct["sequence"]
        for i in range(0, len(seq), 80):
            lines.append(seq[i : i + 80])
        output_mrna_fasta_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    output["output_paths"] = {
        "json_report": str(output_json_path),
        "mrna_fasta": str(output_mrna_fasta_path) if output_mrna_fasta_path else None,
    }

    logger.info(
        "Patient DNA pipeline completed",
        extra={
            "sample_id": sample_id,
            "approved_for_research": approved_for_research,
            "selected_neoantigen_count": len(selected_neoantigen_sequences),
            "json_report": str(output_json_path),
        },
    )

    return output
