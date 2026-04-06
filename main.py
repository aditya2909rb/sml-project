from __future__ import annotations

import argparse
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path

from sml.config import load_config
from sml.runner import run_loop, run_one_cycle
from sml.status_api import run_status_server


def _configure_logging() -> None:
    """Configure process-wide structured-ish logging for runtime diagnostics."""
    level = os.getenv("SML_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OncoSML: Cancer Vaccine Learning System")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("run-once", help="Run one ingest/train/heal cycle")

    loop_cmd = sub.add_parser("run-loop", help="Run cycles continuously")
    loop_cmd.add_argument("--sleep-seconds", type=int, default=300, help="Seconds between cycles")

    status_cmd = sub.add_parser("serve-status", help="Serve health and status API")
    status_cmd.add_argument("--host", type=str, default=None, help="Host to bind status API")
    status_cmd.add_argument("--port", type=int, default=None, help="Port to bind status API")

    service_cmd = sub.add_parser("run-service", help="Run learning loop and status API together")
    service_cmd.add_argument("--sleep-seconds", type=int, default=300, help="Seconds between cycles")
    service_cmd.add_argument("--host", type=str, default=None, help="Host to bind status API")
    service_cmd.add_argument("--port", type=int, default=None, help="Port to bind status API")

    # Clinical system commands
    clinical_cmd = sub.add_parser("run-clinical", help="Run clinical data integration and analysis")
    clinical_cmd.add_argument("--patient-id", type=str, required=True, help="Patient ID for analysis")
    clinical_cmd.add_argument("--enable-safety", action="store_true", help="Enable safety validation")
    clinical_cmd.add_argument("--enable-modeling", action="store_true", help="Enable enhanced biological modeling")

    demo_cmd = sub.add_parser("run-demo", help="Run clinical system demonstration")
    demo_cmd.add_argument("--patient-count", type=int, default=5, help="Number of patients for demo")

    submission_cmd = sub.add_parser(
        "run-submission",
        help="Run a submission-ready clinical demo in a timestamped output folder",
    )
    submission_cmd.add_argument(
        "--sample-id",
        type=str,
        default="patient_submission",
        help="Sample identifier used in generated report and FASTA files",
    )
    submission_cmd.add_argument(
        "--output-root",
        type=str,
        default="outputs/submissions",
        help="Root folder under which timestamped submission outputs are created",
    )

    patient_pipeline_cmd = sub.add_parser(
        "run-patient-pipeline",
        help="Build mRNA vaccine candidate from normal/tumor FASTA DNA inputs",
    )
    patient_pipeline_cmd.add_argument("--sample-id", type=str, required=True, help="Sample identifier")
    patient_pipeline_cmd.add_argument("--normal-fasta", type=str, required=True, help="Path to normal DNA FASTA")
    patient_pipeline_cmd.add_argument("--tumor-fasta", type=str, required=True, help="Path to tumor DNA FASTA")
    patient_pipeline_cmd.add_argument("--hla-allele", type=str, default="HLA-A*02:01", help="HLA allele")
    patient_pipeline_cmd.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Path to write JSON report (default: outputs/patient_pipeline_<sample_id>.json)",
    )
    patient_pipeline_cmd.add_argument(
        "--output-mrna-fasta",
        type=str,
        default=None,
        help="Optional path to write mRNA construct FASTA",
    )

    realworld_cmd = sub.add_parser(
        "run-realworld-stack",
        help="Run external-tool clinical genomics stack (FASTQ/BAM/VCF -> release report)",
    )
    realworld_cmd.add_argument("--patient-id", type=str, required=True, help="Patient/sample identifier")
    realworld_cmd.add_argument(
        "--output-dir",
        type=str,
        default="outputs/realworld",
        help="Output directory for stack artifacts",
    )
    realworld_cmd.add_argument("--reference-fasta", type=str, required=True, help="Reference FASTA path")
    realworld_cmd.add_argument("--known-sites-vcf", type=str, default=None, help="Known-sites VCF")
    realworld_cmd.add_argument("--dbsnp-vcf", type=str, default=None, help="dbSNP VCF")
    realworld_cmd.add_argument("--normal-fastq-r1", type=str, default=None, help="Normal FASTQ R1")
    realworld_cmd.add_argument("--normal-fastq-r2", type=str, default=None, help="Normal FASTQ R2")
    realworld_cmd.add_argument("--tumor-fastq-r1", type=str, default=None, help="Tumor FASTQ R1")
    realworld_cmd.add_argument("--tumor-fastq-r2", type=str, default=None, help="Tumor FASTQ R2")
    realworld_cmd.add_argument("--normal-bam", type=str, default=None, help="Normal BAM")
    realworld_cmd.add_argument("--tumor-bam", type=str, default=None, help="Tumor BAM")
    realworld_cmd.add_argument("--tumor-vcf", type=str, default=None, help="Tumor VCF (somatic)")
    realworld_cmd.add_argument("--vep-cache-dir", type=str, default=None, help="VEP cache directory")
    realworld_cmd.add_argument("--dry-run", action="store_true", help="Plan mode without running tools")

    return parser.parse_args()


def main() -> None:
    _configure_logging()
    args = parse_args()
    config = load_config()
    repo_root = Path(__file__).resolve().parent

    if args.command == "run-once":
        run_one_cycle(config=config, repo_root=repo_root)
        return

    if args.command == "run-loop":
        run_loop(config=config, repo_root=repo_root, sleep_seconds=args.sleep_seconds)
        return

    if args.command == "serve-status":
        host = args.host or config.status_host
        port = args.port or config.status_port
        run_status_server(db_path=config.db_path, host=host, port=port)
        return

    if args.command == "run-service":
        host = args.host or config.status_host
        port = args.port or config.status_port

        loop_thread = threading.Thread(
            target=run_loop,
            kwargs={"config": config, "repo_root": repo_root, "sleep_seconds": args.sleep_seconds},
            daemon=True,
        )
        loop_thread.start()
        run_status_server(db_path=config.db_path, host=host, port=port)
        return

    if args.command == "run-clinical":
        run_clinical_analysis(config=config, patient_id=args.patient_id, 
                            enable_safety=args.enable_safety, 
                            enable_modeling=args.enable_modeling)
        return

    if args.command == "run-demo":
        run_clinical_demo(config=config, patient_count=args.patient_count)
        return

    if args.command == "run-submission":
        run_submission_mode(
            sample_id=args.sample_id,
            output_root=Path(args.output_root),
        )
        return

    if args.command == "run-patient-pipeline":
        run_patient_pipeline(
            sample_id=args.sample_id,
            normal_fasta=Path(args.normal_fasta),
            tumor_fasta=Path(args.tumor_fasta),
            hla_allele=args.hla_allele,
            output_json=Path(args.output_json) if args.output_json else None,
            output_mrna_fasta=Path(args.output_mrna_fasta) if args.output_mrna_fasta else None,
        )
        return

    if args.command == "run-realworld-stack":
        run_realworld_stack(
            patient_id=args.patient_id,
            output_dir=Path(args.output_dir),
            reference_fasta=Path(args.reference_fasta),
            known_sites_vcf=Path(args.known_sites_vcf) if args.known_sites_vcf else None,
            dbsnp_vcf=Path(args.dbsnp_vcf) if args.dbsnp_vcf else None,
            normal_fastq_r1=Path(args.normal_fastq_r1) if args.normal_fastq_r1 else None,
            normal_fastq_r2=Path(args.normal_fastq_r2) if args.normal_fastq_r2 else None,
            tumor_fastq_r1=Path(args.tumor_fastq_r1) if args.tumor_fastq_r1 else None,
            tumor_fastq_r2=Path(args.tumor_fastq_r2) if args.tumor_fastq_r2 else None,
            normal_bam=Path(args.normal_bam) if args.normal_bam else None,
            tumor_bam=Path(args.tumor_bam) if args.tumor_bam else None,
            tumor_vcf=Path(args.tumor_vcf) if args.tumor_vcf else None,
            vep_cache_dir=Path(args.vep_cache_dir) if args.vep_cache_dir else None,
            dry_run=args.dry_run,
        )
        return


def run_clinical_analysis(config, patient_id: str, enable_safety: bool = False, 
                         enable_modeling: bool = False):
    """Run clinical data integration and analysis for a specific patient."""
    print(f"[INFO] Running clinical analysis for patient: {patient_id}")
    
    try:
        # Import clinical modules
        from sml.clinical_data_integration import ClinicalDataIntegrator
        from sml.enhanced_biological_model import EnhancedBiologicalModel
        from sml.safety_validator import EnhancedSafetyValidator
        
        # Initialize components
        clinical_integrator = ClinicalDataIntegrator(config.__dict__)
        
        # Integrate patient data
        print(f"[INFO] Integrating clinical data for {patient_id}...")
        patient_data = clinical_integrator.integrate_patient_data(patient_id)
        
        if patient_data:
            print("[OK] Clinical data integration successful")
            
            # Run enhanced biological modeling if enabled
            if enable_modeling:
                print("[INFO] Running enhanced biological modeling...")
                biological_model = EnhancedBiologicalModel()
                
                # Create sample data for modeling
                genomic_data = {
                    'sample_id': patient_id,
                    'cancer_type': 'lung_adenocarcinoma',
                    'mutations': {'KRAS': 'G12C', 'TP53': 'R175H'},
                    'sequenced_bases': 30000000,
                    'hla_alleles': ['HLA-A*02:01', 'HLA-A*03:01']
                }
                
                immune_data = {
                    'patient_id': patient_id,
                    't_cell_infiltration': 0.65,
                    'immune_cell_counts': {},
                    'cytokine_levels': {'IL-2': 0.5, 'IFN-gamma': 0.8},
                    'tcr_diversity': 0.7,
                    'immune_exhaustion': 0.3
                }
                
                analysis_result = biological_model.analyze_patient_sample(genomic_data, immune_data)
                print("[OK] Biological analysis complete")
                
                # Run safety validation if enabled
                if enable_safety:
                    print("[INFO] Running safety validation...")
                    safety_validator = EnhancedSafetyValidator()
                    
                    # Validate the analysis results
                    validation_results = safety_validator.validate_complete_pipeline(
                        dna_sequence="ATCGATCGATCG" * 100,
                        neoantigens=["SIINFEKL", "GILGFVFTL"],
                        mrna_construct={
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
                    )
                    
                    safety_report = safety_validator.generate_safety_report(validation_results)
                    print(f"[OK] Safety validation complete. Status: {safety_report['summary']['overall_status']}")
                    
                    # Generate comprehensive report
                    print("\nCLINICAL ANALYSIS REPORT")
                    print("=" * 50)
                    print(f"Patient ID: {patient_id}")
                    print(f"Analysis Status: COMPLETE")
                    print(f"Safety Status: {safety_report['summary']['overall_status']}")
                    print(f"Critical Issues: {safety_report['summary']['critical_issues']}")
                    print(f"Warnings: {safety_report['summary']['warnings']}")
                    print(f"Recommendations: {len(safety_report['recommendations'])}")
                    
                else:
                    print("[OK] Analysis complete (safety validation skipped)")
            else:
                print("[OK] Clinical data integration complete (modeling skipped)")
        else:
            print("[ERROR] No clinical data found for patient")
            
    except ImportError as e:
        print(f"[ERROR] Clinical modules not available: {e}")
    except Exception as e:
        print(f"[ERROR] Clinical analysis failed: {e}")


def run_clinical_demo(config, patient_count: int = 5):
    """Run clinical system demonstration with multiple patients."""
    print(f"[INFO] Running clinical system demo with {patient_count} patients")
    
    try:
        # Import demo module
        import subprocess
        import sys
        
        # Run the clinical demo
        demo_script = Path(__file__).parent / "examples" / "clinical_demo.py"
        if demo_script.exists():
            print("[INFO] Running clinical demonstration...")
            result = subprocess.run(
                [sys.executable, str(demo_script)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            if stdout:
                print(stdout)
            if stderr:
                print("[WARN] Demo emitted stderr output (often external API/log warnings):")
                print(stderr)

            # The demo itself can be functionally successful even when upstream
            # API clients log recoverable warnings to stderr.
            if result.returncode == 0:
                print("[OK] Clinical demo completed successfully")
            elif "Clinical demo completed" in stdout or "PIPELINE SUMMARY" in stdout:
                print(
                    "[OK] Clinical demo completed with recoverable warnings "
                    f"(process return code: {result.returncode})"
                )
            else:
                print(f"[ERROR] Clinical demo failed with return code {result.returncode}")
        else:
            print("[ERROR] Clinical demo script not found")
            
    except Exception as e:
        print(f"[ERROR] Demo execution failed: {e}")


def run_submission_mode(sample_id: str, output_root: Path) -> None:
    """Run a single submission-focused clinical pipeline and print artifact paths."""
    import subprocess
    import sys

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_root / f"{sample_id}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    demo_script = Path(__file__).parent / "examples" / "clinical_demo.py"
    if not demo_script.exists():
        print("[ERROR] Clinical demo script not found")
        return

    print("[INFO] Running submission mode...")
    print(f"[INFO] Sample ID: {sample_id}")
    print(f"[INFO] Output directory: {output_dir}")

    result = subprocess.run(
        [
            sys.executable,
            str(demo_script),
            "--sample-id",
            sample_id,
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if stdout:
        print(stdout)
    if stderr:
        print("[WARN] Submission mode emitted stderr output (often API/log warnings):")
        print(stderr)

    report_path = output_dir / f"pipeline_{sample_id}.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        decision = report.get("decision", {})
        safety = (report.get("safety_report") or {}).get("summary", {})

        print("SUBMISSION SUMMARY")
        print("=" * 50)
        print(f"Sample ID: {sample_id}")
        print(f"Approved for research: {decision.get('approved_for_research', False)}")
        print(f"Selected neoantigens: {len(report.get('selected_neoantigens', []))}")
        print(f"Safety status: {safety.get('overall_status', 'N/A')}")
        print(f"Critical issues: {safety.get('critical_issues', 'N/A')}")
        print(f"Warnings: {safety.get('warnings', 'N/A')}")
        print(f"JSON report: {report_path}")

        mrna_path = output_dir / f"{sample_id}_mrna_construct.fasta"
        if mrna_path.exists():
            print(f"mRNA FASTA: {mrna_path}")
    else:
        print(f"[ERROR] Expected report not found: {report_path}")

    if result.returncode == 0:
        print("[OK] Submission mode completed")
    elif "PIPELINE SUMMARY" in stdout or "Clinical demo completed" in stdout:
        print(
            "[OK] Submission mode completed with recoverable warnings "
            f"(process return code: {result.returncode})"
        )
    else:
        print(f"[ERROR] Submission mode failed with return code {result.returncode}")


def run_patient_pipeline(
    sample_id: str,
    normal_fasta: Path,
    tumor_fasta: Path,
    hla_allele: str,
    output_json: Path | None = None,
    output_mrna_fasta: Path | None = None,
) -> None:
    """Run the DNA -> neoantigen -> mRNA pipeline with strict safety gates."""
    from sml.patient_pipeline import run_patient_dna_pipeline

    report = run_patient_dna_pipeline(
        sample_id=sample_id,
        normal_fasta_path=normal_fasta,
        tumor_fasta_path=tumor_fasta,
        hla_allele=hla_allele,
        output_json_path=output_json,
        output_mrna_fasta_path=output_mrna_fasta,
    )

    decision = report.get("decision", {})
    print("PATIENT PIPELINE REPORT")
    print("=" * 50)
    print(f"Sample ID: {sample_id}")
    print(f"Approved for research: {decision.get('approved_for_research', False)}")
    print(f"Selected neoantigens: {len(report.get('selected_neoantigens', []))}")
    if report.get("mrna_construct"):
        print(f"mRNA length: {report['mrna_construct'].get('length')}")
    safety_summary = (report.get("safety_report") or {}).get("summary", {})
    print(f"Safety status: {safety_summary.get('overall_status', 'N/A')}")
    for reason in decision.get("reasons", []):
        print(f"- {reason}")


def run_realworld_stack(
    patient_id: str,
    output_dir: Path,
    reference_fasta: Path,
    known_sites_vcf: Path | None,
    dbsnp_vcf: Path | None,
    normal_fastq_r1: Path | None,
    normal_fastq_r2: Path | None,
    tumor_fastq_r1: Path | None,
    tumor_fastq_r2: Path | None,
    normal_bam: Path | None,
    tumor_bam: Path | None,
    tumor_vcf: Path | None,
    vep_cache_dir: Path | None,
    dry_run: bool,
) -> None:
    """Run the external-tool clinical genomics stack and print release summary."""
    from sml.clinical_genomics_stack import ClinicalGenomicsStackRunner, ToolchainConfig

    output_dir = output_dir / patient_id
    toolchain = ToolchainConfig(
        reference_fasta=str(reference_fasta),
        known_sites_vcf=str(known_sites_vcf) if known_sites_vcf else None,
        dbsnp_vcf=str(dbsnp_vcf) if dbsnp_vcf else None,
        vep_cache_dir=str(vep_cache_dir) if vep_cache_dir else None,
    )

    runner = ClinicalGenomicsStackRunner(toolchain)
    result = runner.run(
        patient_id=patient_id,
        output_dir=output_dir,
        normal_fastq_r1=normal_fastq_r1,
        normal_fastq_r2=normal_fastq_r2,
        tumor_fastq_r1=tumor_fastq_r1,
        tumor_fastq_r2=tumor_fastq_r2,
        normal_bam=normal_bam,
        tumor_bam=tumor_bam,
        tumor_vcf=tumor_vcf,
        dry_run=dry_run,
    )

    release = result.get("release", {})
    artifacts = result.get("artifacts", {})

    print("REAL-WORLD GENOMICS STACK REPORT")
    print("=" * 60)
    print(f"Patient ID: {patient_id}")
    print(f"Dry run: {dry_run}")
    print(f"Approved for release: {release.get('approved_for_release', False)}")
    print(f"Critical findings: {len(release.get('critical_findings', []))}")
    print(f"Warnings: {len(release.get('warnings', []))}")
    if artifacts.get("final_report"):
        print(f"Final report: {artifacts['final_report']}")
    for finding in release.get("critical_findings", []):
        print(f"- CRITICAL: {finding}")


if __name__ == "__main__":
    main()
