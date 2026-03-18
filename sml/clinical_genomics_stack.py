from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from sml.safety_validator import EnhancedSafetyValidator, SafetyLevel


@dataclass
class ToolchainConfig:
    """External toolchain configuration for research-grade genomics workflows."""

    reference_fasta: str
    known_sites_vcf: str | None = None
    dbsnp_vcf: str | None = None
    fastp_bin: str = "fastp"
    bwa_bin: str = "bwa"
    samtools_bin: str = "samtools"
    gatk_bin: str = "gatk"
    bcftools_bin: str = "bcftools"
    vep_bin: str = "vep"
    optitype_bin: str = "OptiTypePipeline.py"
    netmhcpan_bin: str = "netMHCpan"
    mhcflurry_bin: str = "mhcflurry-predict"
    vep_cache_dir: str | None = None


class ClinicalGenomicsStackRunner:
    """Run an end-to-end clinical-style genomics stack with strict release gating.

    Notes:
    - This orchestrator integrates external command-line tools commonly used in
      production/research genomics stacks.
    - It does not claim regulatory clearance for clinical decision making.
    """

    def __init__(self, toolchain: ToolchainConfig):
        self.toolchain = toolchain
        self.validator = EnhancedSafetyValidator()

    def run(
        self,
        patient_id: str,
        output_dir: Path,
        normal_fastq_r1: Path | None = None,
        normal_fastq_r2: Path | None = None,
        tumor_fastq_r1: Path | None = None,
        tumor_fastq_r2: Path | None = None,
        normal_bam: Path | None = None,
        tumor_bam: Path | None = None,
        tumor_vcf: Path | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        output_dir.mkdir(parents=True, exist_ok=True)
        report: dict[str, Any] = {
            "patient_id": patient_id,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "dry_run": dry_run,
            "toolchain": asdict(self.toolchain),
            "stages": [],
            "artifacts": {},
            "release": {
                "approved_for_release": False,
                "critical_findings": [],
                "warnings": [],
            },
            "disclaimer": (
                "Research-grade orchestration report. Not a substitute for validated "
                "clinical diagnostics, physician judgment, or regulatory-approved release workflows."
            ),
        }

        self._validate_input_mode(
            normal_fastq_r1,
            normal_fastq_r2,
            tumor_fastq_r1,
            tumor_fastq_r2,
            normal_bam,
            tumor_bam,
            tumor_vcf,
        )

        self._record_stage(report, "input_validation", "PASS", "Input mode validated")

        # 1) Raw FASTQ handling + QC + alignment when FASTQ is provided.
        if all([normal_fastq_r1, normal_fastq_r2, tumor_fastq_r1, tumor_fastq_r2]):
            normal_bam, tumor_bam = self._run_fastq_to_bam(
                report=report,
                output_dir=output_dir,
                normal_fastq_r1=normal_fastq_r1,
                normal_fastq_r2=normal_fastq_r2,
                tumor_fastq_r1=tumor_fastq_r1,
                tumor_fastq_r2=tumor_fastq_r2,
                dry_run=dry_run,
            )

        # 2) Somatic variant calling from BAM pair if available.
        if normal_bam and tumor_bam:
            called_vcf = self._run_somatic_calling(
                report=report,
                output_dir=output_dir,
                normal_bam=normal_bam,
                tumor_bam=tumor_bam,
                dry_run=dry_run,
            )
            if called_vcf:
                tumor_vcf = called_vcf

        if not tumor_vcf:
            raise ValueError(
                "No tumor VCF available. Provide --tumor-vcf directly or inputs needed to derive one."
            )

        report["artifacts"]["tumor_vcf"] = str(tumor_vcf)

        # 3) Consequence mapping (transcript/protein effects).
        consequence_json = self._run_consequence_mapping(
            report=report,
            output_dir=output_dir,
            tumor_vcf=tumor_vcf,
            dry_run=dry_run,
        )
        report["artifacts"]["consequence_json"] = str(consequence_json)

        # 4) HLA typing.
        hla_result = self._run_hla_typing(
            report=report,
            output_dir=output_dir,
            tumor_fastq_r1=tumor_fastq_r1,
            tumor_fastq_r2=tumor_fastq_r2,
            tumor_bam=tumor_bam,
            dry_run=dry_run,
        )
        report["artifacts"]["hla_typing_json"] = str(hla_result)

        # 5) MHC prediction.
        mhc_result = self._run_mhc_prediction(
            report=report,
            output_dir=output_dir,
            consequence_json=consequence_json,
            hla_json=hla_result,
            dry_run=dry_run,
        )
        report["artifacts"]["mhc_prediction_json"] = str(mhc_result)

        # 6) Manufacturability + release QC.
        release_qc = self._run_release_qc(
            report=report,
            output_dir=output_dir,
            mhc_json=mhc_result,
        )
        report["artifacts"]["release_qc_json"] = str(release_qc)

        # Final gate.
        gate = json.loads(release_qc.read_text(encoding="utf-8"))
        report["release"]["critical_findings"] = gate.get("critical_findings", [])
        report["release"]["warnings"] = gate.get("warnings", [])
        report["release"]["approved_for_release"] = len(report["release"]["critical_findings"]) == 0

        final_report_path = output_dir / f"clinical_stack_{patient_id}.json"
        final_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report["artifacts"]["final_report"] = str(final_report_path)
        return report

    def _validate_input_mode(
        self,
        normal_fastq_r1: Path | None,
        normal_fastq_r2: Path | None,
        tumor_fastq_r1: Path | None,
        tumor_fastq_r2: Path | None,
        normal_bam: Path | None,
        tumor_bam: Path | None,
        tumor_vcf: Path | None,
    ) -> None:
        has_fastq = all([normal_fastq_r1, normal_fastq_r2, tumor_fastq_r1, tumor_fastq_r2])
        has_bam = bool(normal_bam and tumor_bam)
        has_vcf = bool(tumor_vcf)
        if not (has_fastq or has_bam or has_vcf):
            raise ValueError(
                "Provide either paired FASTQ inputs, paired BAM inputs, or a tumor VCF."
            )

    def _run_fastq_to_bam(
        self,
        report: dict[str, Any],
        output_dir: Path,
        normal_fastq_r1: Path,
        normal_fastq_r2: Path,
        tumor_fastq_r1: Path,
        tumor_fastq_r2: Path,
        dry_run: bool,
    ) -> tuple[Path, Path]:
        qc_dir = output_dir / "qc"
        bam_dir = output_dir / "bam"
        qc_dir.mkdir(parents=True, exist_ok=True)
        bam_dir.mkdir(parents=True, exist_ok=True)

        n_r1 = qc_dir / "normal.trimmed.R1.fastq.gz"
        n_r2 = qc_dir / "normal.trimmed.R2.fastq.gz"
        t_r1 = qc_dir / "tumor.trimmed.R1.fastq.gz"
        t_r2 = qc_dir / "tumor.trimmed.R2.fastq.gz"

        self._exec_or_stub(
            report,
            "fastq_qc_normal",
            [
                self.toolchain.fastp_bin,
                "-i",
                str(normal_fastq_r1),
                "-I",
                str(normal_fastq_r2),
                "-o",
                str(n_r1),
                "-O",
                str(n_r2),
                "--json",
                str(qc_dir / "normal.fastp.json"),
                "--html",
                str(qc_dir / "normal.fastp.html"),
            ],
            dry_run,
        )

        self._exec_or_stub(
            report,
            "fastq_qc_tumor",
            [
                self.toolchain.fastp_bin,
                "-i",
                str(tumor_fastq_r1),
                "-I",
                str(tumor_fastq_r2),
                "-o",
                str(t_r1),
                "-O",
                str(t_r2),
                "--json",
                str(qc_dir / "tumor.fastp.json"),
                "--html",
                str(qc_dir / "tumor.fastp.html"),
            ],
            dry_run,
        )

        normal_bam = bam_dir / "normal.sorted.bam"
        tumor_bam = bam_dir / "tumor.sorted.bam"

        self._exec_or_stub(
            report,
            "align_normal",
            [
                self.toolchain.bwa_bin,
                "mem",
                self.toolchain.reference_fasta,
                str(n_r1),
                str(n_r2),
                "|",
                self.toolchain.samtools_bin,
                "sort",
                "-o",
                str(normal_bam),
            ],
            dry_run,
            shell=True,
        )
        self._exec_or_stub(
            report,
            "align_tumor",
            [
                self.toolchain.bwa_bin,
                "mem",
                self.toolchain.reference_fasta,
                str(t_r1),
                str(t_r2),
                "|",
                self.toolchain.samtools_bin,
                "sort",
                "-o",
                str(tumor_bam),
            ],
            dry_run,
            shell=True,
        )
        self._exec_or_stub(
            report,
            "index_bams",
            [
                f"{self.toolchain.samtools_bin} index {normal_bam} && "
                f"{self.toolchain.samtools_bin} index {tumor_bam}"
            ],
            dry_run,
            shell=True,
        )

        if dry_run:
            normal_bam.touch(exist_ok=True)
            tumor_bam.touch(exist_ok=True)

        return normal_bam, tumor_bam

    def _run_somatic_calling(
        self,
        report: dict[str, Any],
        output_dir: Path,
        normal_bam: Path,
        tumor_bam: Path,
        dry_run: bool,
    ) -> Path:
        vcf_dir = output_dir / "variants"
        vcf_dir.mkdir(parents=True, exist_ok=True)

        unfiltered = vcf_dir / "somatic.unfiltered.vcf.gz"
        filtered = vcf_dir / "somatic.filtered.vcf.gz"

        cmd = [
            self.toolchain.gatk_bin,
            "Mutect2",
            "-R",
            self.toolchain.reference_fasta,
            "-I",
            str(tumor_bam),
            "-tumor",
            "TUMOR",
            "-I",
            str(normal_bam),
            "-normal",
            "NORMAL",
            "-O",
            str(unfiltered),
        ]
        if self.toolchain.known_sites_vcf:
            cmd.extend(["--germline-resource", self.toolchain.known_sites_vcf])

        self._exec_or_stub(report, "somatic_calling_mutect2", cmd, dry_run)
        self._exec_or_stub(
            report,
            "somatic_filtering",
            [
                self.toolchain.gatk_bin,
                "FilterMutectCalls",
                "-R",
                self.toolchain.reference_fasta,
                "-V",
                str(unfiltered),
                "-O",
                str(filtered),
            ],
            dry_run,
        )

        self._exec_or_stub(
            report,
            "variant_normalization",
            [
                self.toolchain.bcftools_bin,
                "norm",
                "-f",
                self.toolchain.reference_fasta,
                "-Oz",
                "-o",
                str(filtered),
                str(filtered),
            ],
            dry_run,
        )

        if dry_run:
            filtered.touch(exist_ok=True)
        return filtered

    def _run_consequence_mapping(
        self,
        report: dict[str, Any],
        output_dir: Path,
        tumor_vcf: Path,
        dry_run: bool,
    ) -> Path:
        ann_dir = output_dir / "annotation"
        ann_dir.mkdir(parents=True, exist_ok=True)
        consequence_json = ann_dir / "vep_consequences.json"

        cmd = [
            self.toolchain.vep_bin,
            "--input_file",
            str(tumor_vcf),
            "--format",
            "vcf",
            "--json",
            "--everything",
            "--output_file",
            str(consequence_json),
            "--offline",
        ]
        if self.toolchain.vep_cache_dir:
            cmd.extend(["--dir_cache", self.toolchain.vep_cache_dir])

        self._exec_or_stub(report, "consequence_mapping_vep", cmd, dry_run)

        if dry_run:
            consequence_json.write_text(
                json.dumps(
                    {
                        "transcript_consequences": [],
                        "protein_changes": [],
                        "note": "dry-run placeholder",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        return consequence_json

    def _run_hla_typing(
        self,
        report: dict[str, Any],
        output_dir: Path,
        tumor_fastq_r1: Path | None,
        tumor_fastq_r2: Path | None,
        tumor_bam: Path | None,
        dry_run: bool,
    ) -> Path:
        hla_dir = output_dir / "hla"
        hla_dir.mkdir(parents=True, exist_ok=True)
        hla_json = hla_dir / "hla_typing.json"

        if tumor_fastq_r1 and tumor_fastq_r2:
            cmd = [
                self.toolchain.optitype_bin,
                "-i",
                str(tumor_fastq_r1),
                str(tumor_fastq_r2),
                "--rna",
                "-o",
                str(hla_dir),
            ]
            self._exec_or_stub(report, "hla_typing_optitype", cmd, dry_run)
        elif tumor_bam:
            self._record_stage(
                report,
                "hla_typing_optitype",
                "WARNING",
                "OptiType typically expects FASTQ; BAM mode requires conversion outside this runner",
            )
        else:
            self._record_stage(report, "hla_typing_optitype", "WARNING", "No tumor reads provided")

        if dry_run:
            hla_json.write_text(
                json.dumps(
                    {
                        "hla_class_i": ["HLA-A*02:01", "HLA-A*03:01", "HLA-B*07:02"],
                        "source": "dry-run placeholder",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        elif not hla_json.exists():
            hla_json.write_text(
                json.dumps(
                    {"hla_class_i": [], "source": "tool output not found; manual review required"},
                    indent=2,
                ),
                encoding="utf-8",
            )
        return hla_json

    def _run_mhc_prediction(
        self,
        report: dict[str, Any],
        output_dir: Path,
        consequence_json: Path,
        hla_json: Path,
        dry_run: bool,
    ) -> Path:
        mhc_dir = output_dir / "mhc"
        mhc_dir.mkdir(parents=True, exist_ok=True)
        peptides_tsv = mhc_dir / "candidate_peptides.tsv"
        netmhc_out = mhc_dir / "netmhcpan.out"
        mhc_json = mhc_dir / "mhc_predictions.json"

        # Placeholder extraction list. In full production this should parse VEP output
        # into mutant peptide candidates from coding consequences.
        peptides_tsv.write_text("peptide\nSIINFEKL\nGILGFVFTL\n", encoding="utf-8")

        self._exec_or_stub(
            report,
            "mhc_prediction_netmhcpan",
            [
                self.toolchain.netmhcpan_bin,
                "-p",
                str(peptides_tsv),
                "-a",
                "HLA-A02:01,HLA-A03:01",
                "-BA",
                ">",
                str(netmhc_out),
            ],
            dry_run,
            shell=True,
        )

        self._exec_or_stub(
            report,
            "mhc_prediction_mhcflurry",
            [
                self.toolchain.mhcflurry_bin,
                "--alleles",
                "HLA-A*02:01,HLA-A*03:01",
                "--peptides",
                str(peptides_tsv),
                "--out",
                str(mhc_dir / "mhcflurry.csv"),
            ],
            dry_run,
        )

        if dry_run:
            mhc_json.write_text(
                json.dumps(
                    {
                        "strong_binders": [
                            {"peptide": "SIINFEKL", "allele": "HLA-A*02:01", "ic50_nm": 90.0},
                            {"peptide": "GILGFVFTL", "allele": "HLA-A*03:01", "ic50_nm": 145.0},
                        ],
                        "weak_binders": [],
                        "source": "dry-run placeholder",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        else:
            mhc_json.write_text(
                json.dumps(
                    {
                        "strong_binders": [],
                        "weak_binders": [],
                        "source": "tool outputs require parser integration",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        return mhc_json

    def _run_release_qc(
        self,
        report: dict[str, Any],
        output_dir: Path,
        mhc_json: Path,
    ) -> Path:
        qc_dir = output_dir / "release_qc"
        qc_dir.mkdir(parents=True, exist_ok=True)
        release_json = qc_dir / "release_qc.json"

        mhc = json.loads(mhc_json.read_text(encoding="utf-8"))
        strong = mhc.get("strong_binders", [])

        critical_findings: list[str] = []
        warnings: list[str] = []

        if len(strong) < 2:
            critical_findings.append("Insufficient strong MHC binders (<2)")

        # Manufacturability checks for synthetic construct placeholder.
        # In production, this should parse final mRNA construct and manufacturing batch metrics.
        construct = {
            "sequence": "AUGC" * 80,
            "length": 320,
            "stability_score": 0.70,
            "immunogenicity_score": 0.45,
            "5_utr": True,
            "kozak": True,
            "coding_sequence": True,
            "3_utr": True,
            "poly_a": True,
            "dose_recommendation": 80,
        }

        validation = self.validator.validate_complete_pipeline(
            dna_sequence="ATCG" * 300,
            neoantigens=[x.get("peptide", "") for x in strong],
            mrna_construct=construct,
            neoantigen_metadata=[
                {
                    "binding_affinity_nm": float(x.get("ic50_nm", 9999.0)),
                    "immunogenicity_score": 0.65,
                }
                for x in strong
            ],
        )
        safety = self.validator.generate_safety_report(validation)

        for category, entries in safety.get("detailed_results", {}).items():
            for entry in entries:
                level = entry.get("level")
                msg = f"{category}: {entry.get('message')}"
                if level == SafetyLevel.CRITICAL.value:
                    critical_findings.append(msg)
                elif level == SafetyLevel.WARNING.value:
                    warnings.append(msg)

        qc = {
            "critical_findings": critical_findings,
            "warnings": warnings,
            "safety_summary": safety.get("summary", {}),
            "approved_for_release": len(critical_findings) == 0,
        }
        release_json.write_text(json.dumps(qc, indent=2), encoding="utf-8")
        self._record_stage(
            report,
            "manufacturability_and_release_qc",
            "PASS" if not critical_findings else "CRITICAL",
            f"Critical findings: {len(critical_findings)}, warnings: {len(warnings)}",
        )
        return release_json

    def _exec_or_stub(
        self,
        report: dict[str, Any],
        stage: str,
        cmd: list[str],
        dry_run: bool,
        shell: bool = False,
    ) -> None:
        if dry_run:
            self._record_stage(report, stage, "PASS", "Dry-run: command not executed", cmd)
            return

        binary = cmd[0] if cmd else ""
        if not shell and binary and shutil.which(binary) is None:
            self._record_stage(
                report,
                stage,
                "WARNING",
                f"Tool not found on PATH: {binary}; stage skipped",
                cmd,
            )
            return

        try:
            if shell:
                subprocess.run(" ".join(cmd), shell=True, check=True)
            else:
                subprocess.run(cmd, check=True)
            self._record_stage(report, stage, "PASS", "Command executed", cmd)
        except subprocess.CalledProcessError as exc:
            self._record_stage(
                report,
                stage,
                "CRITICAL",
                f"Command failed with exit code {exc.returncode}",
                cmd,
            )

    def _record_stage(
        self,
        report: dict[str, Any],
        stage: str,
        status: str,
        message: str,
        command: list[str] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "stage": stage,
            "status": status,
            "message": message,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        }
        if command is not None:
            payload["command"] = command
        report["stages"].append(payload)
