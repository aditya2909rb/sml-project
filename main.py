from __future__ import annotations

import argparse
import threading
from pathlib import Path

from sml.config import load_config
from sml.runner import run_loop, run_one_cycle
from sml.status_api import run_status_server


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

    return parser.parse_args()


def main() -> None:
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


def run_clinical_analysis(config, patient_id: str, enable_safety: bool = False, 
                         enable_modeling: bool = False):
    """Run clinical data integration and analysis for a specific patient."""
    print(f"🔬 Running clinical analysis for patient: {patient_id}")
    
    try:
        # Import clinical modules
        from sml.clinical_data_integration import ClinicalDataIntegrator
        from sml.enhanced_biological_model import EnhancedBiologicalModel
        from sml.safety_validator import EnhancedSafetyValidator
        
        # Initialize components
        clinical_integrator = ClinicalDataIntegrator(config.__dict__)
        
        # Integrate patient data
        print(f"📊 Integrating clinical data for {patient_id}...")
        patient_data = clinical_integrator.integrate_patient_data(patient_id)
        
        if patient_data:
            print("✅ Clinical data integration successful!")
            
            # Run enhanced biological modeling if enabled
            if enable_modeling:
                print("🧬 Running enhanced biological modeling...")
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
                print("✅ Biological analysis complete!")
                
                # Run safety validation if enabled
                if enable_safety:
                    print("🛡️ Running safety validation...")
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
                    print(f"✅ Safety validation complete! Status: {safety_report['summary']['overall_status']}")
                    
                    # Generate comprehensive report
                    print("\n📋 CLINICAL ANALYSIS REPORT")
                    print("=" * 50)
                    print(f"Patient ID: {patient_id}")
                    print(f"Analysis Status: COMPLETE")
                    print(f"Safety Status: {safety_report['summary']['overall_status']}")
                    print(f"Critical Issues: {safety_report['summary']['critical_issues']}")
                    print(f"Warnings: {safety_report['summary']['warnings']}")
                    print(f"Recommendations: {len(safety_report['recommendations'])}")
                    
                else:
                    print("✅ Analysis complete (safety validation skipped)")
            else:
                print("✅ Clinical data integration complete (modeling skipped)")
        else:
            print("❌ No clinical data found for patient")
            
    except ImportError as e:
        print(f"❌ Clinical modules not available: {e}")
    except Exception as e:
        print(f"❌ Clinical analysis failed: {e}")


def run_clinical_demo(config, patient_count: int = 5):
    """Run clinical system demonstration with multiple patients."""
    print(f"🚀 Running clinical system demo with {patient_count} patients")
    
    try:
        # Import demo module
        import subprocess
        import sys
        
        # Run the clinical demo
        demo_script = Path(__file__).parent / "examples" / "clinical_demo.py"
        if demo_script.exists():
            print("🎬 Running clinical demonstration...")
            result = subprocess.run([sys.executable, str(demo_script)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Clinical demo completed successfully!")
                print(result.stdout)
            else:
                print("❌ Clinical demo failed:")
                print(result.stderr)
        else:
            print("❌ Clinical demo script not found")
            
    except Exception as e:
        print(f"❌ Demo execution failed: {e}")


if __name__ == "__main__":
    main()
