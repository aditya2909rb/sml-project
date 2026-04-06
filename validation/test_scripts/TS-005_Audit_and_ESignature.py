from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sml.compliance.audit_trail import AuditAction, AuditSeverity, AuditTrailManager
from sml.compliance.electronic_signatures import ElectronicSignatureManager, SignatureMeaning


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description="OQ audit and e-signature evidence script")
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    audit_db = output_dir / "oq_comp_audit_trail.db"
    sign_db = output_dir / "oq_comp_signatures.db"
    if audit_db.exists():
        audit_db.unlink()
    if sign_db.exists():
        sign_db.unlink()

    audit = AuditTrailManager(db_path=str(audit_db))
    sig = ElectronicSignatureManager(db_path=str(sign_db))

    entry = audit.log(
        user_id="u_qa",
        user_name="QA Reviewer",
        action=AuditAction.UPDATE,
        resource_type="validation_record",
        resource_id="OQ-001",
        description="Updated OQ evidence register",
        old_value={"status": "draft"},
        new_value={"status": "review"},
        ip_address="127.0.0.1",
        session_id="oq-session",
        severity=AuditSeverity.HIGH,
    )
    integrity = audit.verify_integrity()

    user_created = sig.create_user(
        user_id="u_qa",
        username="qa1",
        password="StrongPass!123",
        full_name="QA Reviewer",
        title="QA",
    )

    doc_text = "OQ approval record v1"
    signature, success = sig.sign_document(
        user_id="u_qa",
        user_name="QA Reviewer",
        document_id="OQ-REC-001",
        document_version="1.0",
        document_content=doc_text,
        signature_meaning=SignatureMeaning.REVIEWED,
        reason="OQ evidence review",
        ip_address="127.0.0.1",
    )

    verification = sig.verify_signature(signature.signature_id, current_document_content=doc_text)

    checks = {
        "audit_entry_created": bool(entry.entry_id),
        "audit_integrity_valid": bool(integrity.get("valid")),
        "signature_user_created": user_created,
        "signature_created": success,
        "signature_verifies": bool(verification.get("valid")),
    }

    passed = all(checks.values())
    evidence = {
        "script_id": "TS-005",
        "generated_at_utc": utc_now(),
        "checks": checks,
        "audit_integrity": integrity,
        "signature_verification": verification,
        "result": "PASS" if passed else "FAIL",
    }

    out_path = output_dir / f"OQ-COMP-01_02_TS-005_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {out_path}")
    print(f"Result: {evidence['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
