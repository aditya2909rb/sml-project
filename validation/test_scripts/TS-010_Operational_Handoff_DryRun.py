from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description="PQ operational handoff technical dry-run")
    parser.add_argument("--python-exe", default=sys.executable, help="Python executable path")
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    out_dir = (PROJECT_ROOT / args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    required_docs = [
        PROJECT_ROOT / "docs" / "OQ_EXECUTION_QUICKSTART.md",
        PROJECT_ROOT / "docs" / "SOP-001_Software_Development.md",
        PROJECT_ROOT / "docs" / "SOP-002_Change_Control.md",
        PROJECT_ROOT / "docs" / "SOP-003_Document_Control.md",
        PROJECT_ROOT / "docs" / "SOP-004_Training.md",
        PROJECT_ROOT / "docs" / "SOP-005_Incident_Management.md",
        PROJECT_ROOT / "docs" / "SOP-006_Backup_Restore.md",
        PROJECT_ROOT / "validation" / "OQ_EVIDENCE_LOG.md",
        PROJECT_ROOT / "validation" / "PQ_Performance_Qualification.md",
    ]

    sample_id = "pq_handoff_dryrun"
    out_json = out_dir / f"pipeline_{sample_id}.json"
    out_fasta = out_dir / f"{sample_id}.fasta"

    cmd = [
        args.python_exe,
        "main.py",
        "run-patient-pipeline",
        "--sample-id",
        sample_id,
        "--normal-fasta",
        "outputs/check_demo/check_patient_01_normal.fasta",
        "--tumor-fasta",
        "outputs/check_demo/check_patient_01_tumor.fasta",
        "--output-json",
        str(out_json),
        "--output-mrna-fasta",
        str(out_fasta),
    ]

    started = time.perf_counter()
    run = subprocess.run(cmd, cwd=str(PROJECT_ROOT), text=True, capture_output=True)  # noqa: S603
    elapsed = time.perf_counter() - started

    checks = {
        "required_docs_present": all(p.exists() for p in required_docs),
        "dryrun_command_exit_zero": run.returncode == 0,
        "dryrun_output_json_exists": out_json.exists(),
        "dryrun_runtime_under_10min": elapsed <= 600.0,
        "handoff_artifacts_packaged": (PROJECT_ROOT / "docs" / "SIGNOFF_PACKET.md").exists(),
    }

    result = "PASS" if all(checks.values()) else "FAIL"

    evidence = {
        "script_id": "TS-010",
        "generated_at_utc": utc_now(),
        "checks": checks,
        "runtime_seconds": round(elapsed, 3),
        "stdout_tail": run.stdout[-1500:],
        "stderr_tail": run.stderr[-1500:],
        "result": result,
        "note": "Technical operational handoff dry-run evidence. Human training competency signoff remains governance-controlled.",
    }

    out_file = out_dir / f"PQ-OPS-01_TS-010_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {out_file}")
    print(f"Result: {result}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
