from pathlib import Path
from types import SimpleNamespace

import pytest

from sml import patient_pipeline as pp


class _FakeAnalyzer:
    def analyze_sample(self, sample_id: str, normal_dna: str, tumor_dna: str, hla_allele: str):
        neo = SimpleNamespace(
            peptide_sequence="SIINFEKL",
            hla_allele=hla_allele,
            binding_affinity=90.0,
            immunogenicity_score=0.82,
            stability_score=0.73,
            mutation=SimpleNamespace(position=11, consequence="missense_variant"),
        )
        return SimpleNamespace(
            predicted_neoantigens=[neo],
            total_mutations=3,
            driver_mutations=[1],
            passenger_mutations=[1, 2],
            tumor_mutational_burden=4.3,
            microsatellite_status="MSS",
        )


class _FakeDesigner:
    def design_vaccine(self, neoantigens):
        sequence = ("AUGC" * 220)[:850]
        return SimpleNamespace(
            sequence=sequence,
            gc_content=0.50,
            stability_score=0.70,
            immunogenicity_score=0.62,
            delivery_efficiency=0.64,
            optimizations_applied=["mock"],
        )


class _FakeSafety:
    def validate_complete_pipeline(self, **kwargs):
        return {"mock": [{"level": "PASS"}]}

    def generate_safety_report(self, _):
        return {"summary": {"overall_status": "PASS", "critical_issues": 0, "warnings": 0, "passed_checks": 1}, "recommendations": []}


def test_patient_pipeline_emits_gmp_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pp, "DNAMutationAnalyzer", _FakeAnalyzer)
    monkeypatch.setattr(pp, "MRNAVaccineDesigner", _FakeDesigner)
    monkeypatch.setattr(pp, "EnhancedSafetyValidator", _FakeSafety)

    normal = tmp_path / "normal.fasta"
    tumor = tmp_path / "tumor.fasta"
    out_json = tmp_path / "report.json"

    normal.write_text(">normal\n" + ("ACGT" * 50) + "\n", encoding="utf-8")
    tumor.write_text(">tumor\n" + ("ACGT" * 50) + "\n", encoding="utf-8")

    result = pp.run_patient_dna_pipeline(
        sample_id="PTEST",
        normal_fasta_path=normal,
        tumor_fasta_path=tumor,
        output_json_path=out_json,
    )

    assert out_json.exists()
    assert "gmp_release_record" in result
    assert result["gmp_release_record"]["gc_window_pass"] is True
    assert result["gmp_release_record"]["release_status"] == "CONDITIONAL_RELEASE"


def test_patient_pipeline_invalid_fasta_raises_runtime_error(tmp_path: Path) -> None:
    normal = tmp_path / "normal.fasta"
    tumor = tmp_path / "tumor.fasta"

    normal.write_text(">normal\nACGT\n", encoding="utf-8")
    tumor.write_text(">tumor\nACGX\n", encoding="utf-8")

    with pytest.raises(RuntimeError):
        pp.run_patient_dna_pipeline(
            sample_id="PINVALID",
            normal_fasta_path=normal,
            tumor_fasta_path=tumor,
        )
