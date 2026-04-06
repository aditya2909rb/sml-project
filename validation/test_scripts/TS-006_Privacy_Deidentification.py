from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sml.compliance.privacy import PrivacyManager


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description="OQ privacy de-identification evidence script")
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    privacy = PrivacyManager()

    raw = {
        "patient_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "medical_record_number": "MRN-123456",
        "notes": "Contact john.doe@example.com for follow-up",
        "non_identifying_field": "tumor_sample_batch_01",
    }

    deid = privacy.deidentify_safe_harbor(raw)

    checks = {
        "identifier_fields_removed": "patient_name" not in deid and "medical_record_number" not in deid,
        "email_redacted_in_notes": "[REDACTED]" in deid.get("notes", ""),
        "non_identifying_field_preserved": deid.get("non_identifying_field") == "tumor_sample_batch_01",
    }

    passed = all(checks.values())

    evidence = {
        "script_id": "TS-006",
        "generated_at_utc": utc_now(),
        "checks": checks,
        "deidentified_payload": deid,
        "result": "PASS" if passed else "FAIL",
    }

    out_path = output_dir / f"OQ-PRIV-01_TS-006_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {out_path}")
    print(f"Result: {evidence['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
