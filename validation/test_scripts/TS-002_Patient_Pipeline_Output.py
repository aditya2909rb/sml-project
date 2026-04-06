from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description="OQ patient pipeline verification script")
    parser.add_argument("--python-exe", default="python", help="Python executable path")
    parser.add_argument("--sample-id", default="oq_validation_sample", help="Validation sample ID")
    parser.add_argument(
        "--normal-fasta",
        default="outputs/check_demo/check_patient_01_normal.fasta",
        help="Path to normal FASTA",
    )
    parser.add_argument(
        "--tumor-fasta",
        default="outputs/check_demo/check_patient_01_tumor.fasta",
        help="Path to tumor FASTA",
    )
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline_json = output_dir / f"pipeline_{args.sample_id}.json"
    pipeline_fasta = output_dir / f"{args.sample_id}_mrna.fasta"

    cmd = [
        args.python_exe,
        "main.py",
        "run-patient-pipeline",
        "--sample-id",
        args.sample_id,
        "--normal-fasta",
        args.normal_fasta,
        "--tumor-fasta",
        args.tumor_fasta,
        "--output-json",
        str(pipeline_json),
        "--output-mrna-fasta",
        str(pipeline_fasta),
    ]

    run = subprocess.run(cmd, text=True, capture_output=True)  # noqa: S603

    checks = {
        "command_exit_zero": run.returncode == 0,
        "output_json_exists": pipeline_json.exists(),
    }

    payload = {}
    if pipeline_json.exists():
        payload = json.loads(pipeline_json.read_text(encoding="utf-8"))
        decision = payload.get("decision") or {}
        approved = bool(decision.get("approved_for_research", False))
        has_construct = bool(payload.get("mrna_construct"))

        checks.update(
            {
                "payload_has_sample_id": bool(payload.get("sample_id")),
                "payload_has_decision": "decision" in payload,
                "output_fasta_if_construct": (not has_construct) or pipeline_fasta.exists(),
                "payload_has_gmp_record_if_construct": (not has_construct) or ("gmp_release_record" in payload),
                "approved_or_reasoned_rejection": approved or bool(decision.get("reasons")),
            }
        )

    passed = all(checks.values())

    evidence = {
        "script_id": "TS-002",
        "generated_at_utc": utc_now(),
        "command": cmd,
        "checks": checks,
        "command_returncode": run.returncode,
        "stdout_tail": run.stdout[-2000:],
        "stderr_tail": run.stderr[-2000:],
        "result": "PASS" if passed else "FAIL",
    }

    evidence_path = output_dir / f"OQ-FUNC-01_TS-002_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {evidence_path}")
    print(f"Result: {evidence['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
