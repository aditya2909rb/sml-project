from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_pipeline(python_exe: str, sample_id: str, output_dir: Path) -> tuple[int, dict, float, str, str]:
    out_json = output_dir / f"pq_pipeline_{sample_id}.json"
    out_fasta = output_dir / f"pq_pipeline_{sample_id}.fasta"
    cmd = [
        python_exe,
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

    payload = {}
    if out_json.exists():
        payload = json.loads(out_json.read_text(encoding="utf-8"))

    return run.returncode, payload, elapsed, run.stdout[-1500:], run.stderr[-1500:]


def backup_restore_smoke(output_dir: Path) -> tuple[bool, str]:
    source_dir = PROJECT_ROOT / "outputs"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = output_dir / f"pq_backup_{ts}.zip"
    restore_dir = output_dir / f"pq_restore_{ts}"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in source_dir.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(source_dir))

    restore_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(restore_dir)

    restored_files = [p for p in restore_dir.rglob("*") if p.is_file()]
    return len(restored_files) > 0, str(zip_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="PQ core scenario evidence script")
    parser.add_argument("--python-exe", default=sys.executable, help="Python executable path")
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    output_dir = (PROJECT_ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rc1, p1, t1, out1, err1 = run_pipeline(args.python_exe, "pq_sample_a", output_dir)
    rc2, p2, t2, out2, err2 = run_pipeline(args.python_exe, "pq_sample_b", output_dir)

    same_top_level_keys = sorted(p1.keys()) == sorted(p2.keys()) if p1 and p2 else False
    perf_ok = t1 <= 600.0 and t2 <= 600.0
    recovery_ok, backup_zip = backup_restore_smoke(output_dir)

    checks = {
        "pq_e2e_01_end_to_end": rc1 == 0 and bool(p1),
        "pq_e2e_02_multi_run_consistency": rc2 == 0 and bool(p2) and same_top_level_keys,
        "pq_perf_01_runtime_leq_10min": perf_ok,
        "pq_perf_02_recovery_simulation": recovery_ok,
        "pq_ops_01_operational_handoff": False,
        "pq_ops_02_incident_drill": False,
    }

    result = "PASS_PARTIAL" if all(v for k, v in checks.items() if not k.startswith("pq_ops_")) else "FAIL"

    evidence = {
        "script_id": "TS-007",
        "generated_at_utc": utc_now(),
        "checks": checks,
        "runtime_seconds": {"run_a": round(t1, 3), "run_b": round(t2, 3)},
        "backup_zip": backup_zip,
        "notes": {
            "pq_ops_01_operational_handoff": "Manual training/competency evidence required",
            "pq_ops_02_incident_drill": "Manual incident drill evidence required",
        },
        "stdout_tail": {"run_a": out1, "run_b": out2},
        "stderr_tail": {"run_a": err1, "run_b": err2},
        "result": result,
    }

    out_path = output_dir / f"PQ-CORE_TS-007_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {out_path}")
    print(f"Result: {result}")
    return 0 if result != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
