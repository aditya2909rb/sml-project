from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description="OQ backup/restore smoke test")
    parser.add_argument("--source-dir", default="outputs", help="Source directory to back up")
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = output_dir / f"backup_smoke_{ts}.zip"
    restore_dir = output_dir / f"restore_smoke_{ts}"

    checks = {
        "source_exists": source_dir.exists(),
        "source_is_dir": source_dir.is_dir(),
    }

    if checks["source_exists"] and checks["source_is_dir"]:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in source_dir.rglob("*"):
                if p.is_file():
                    zf.write(p, p.relative_to(source_dir))

        checks["backup_zip_created"] = zip_path.exists() and zip_path.stat().st_size > 0

        restore_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(restore_dir)

        restored_files = [p for p in restore_dir.rglob("*") if p.is_file()]
        checks["restore_contains_files"] = len(restored_files) > 0
    else:
        checks["backup_zip_created"] = False
        checks["restore_contains_files"] = False

    passed = all(checks.values())
    evidence = {
        "script_id": "TS-003",
        "generated_at_utc": utc_now(),
        "source_dir": str(source_dir),
        "backup_zip": str(zip_path),
        "restore_dir": str(restore_dir),
        "checks": checks,
        "result": "PASS" if passed else "FAIL",
    }

    evidence_path = output_dir / f"OQ-DR-01_02_TS-003_{ts}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {evidence_path}")
    print(f"Result: {evidence['result']}")

    if restore_dir.exists():
        shutil.rmtree(restore_dir)

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
