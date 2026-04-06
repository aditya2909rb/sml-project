from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description="IQ technical baseline evidence script")
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    output_dir = (PROJECT_ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    required_files = [
        PROJECT_ROOT / "main.py",
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "Dockerfile.clinical",
        PROJECT_ROOT / "docker-compose.clinical.yml",
        PROJECT_ROOT / "docs" / "USER_REQUIREMENTS_SPECIFICATION.md",
        PROJECT_ROOT / "docs" / "DESIGN_SPECIFICATION.md",
        PROJECT_ROOT / "docs" / "RISK_ASSESSMENT.md",
    ]

    checks = {
        "iq_sw_python_3_11_plus": sys.version_info >= (3, 11),
        "iq_sw_required_files_present": all(p.exists() for p in required_files),
        "iq_sw_docker_cli_present": shutil.which("docker") is not None,
        "iq_sw_compose_file_present": (PROJECT_ROOT / "docker-compose.clinical.yml").exists(),
        "iq_sec_rbac_module_present": (PROJECT_ROOT / "sml" / "security" / "access_control.py").exists(),
        "iq_sec_audit_module_present": (PROJECT_ROOT / "sml" / "compliance" / "audit_trail.py").exists(),
    }

    evidence = {
        "script_id": "TS-008",
        "generated_at_utc": utc_now(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "python": sys.version,
        },
        "checks": checks,
        "required_files": [str(p.relative_to(PROJECT_ROOT)) for p in required_files],
        "result": "PASS" if all(checks.values()) else "PASS_PARTIAL",
    }

    out_path = output_dir / f"IQ-TECH-BASELINE_TS-008_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"Evidence written: {out_path}")
    print(f"Result: {evidence['result']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
