from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sml.security.access_control import AccessControlManager, Permission, Role


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    parser = argparse.ArgumentParser(description="OQ RBAC and session control evidence script")
    parser.add_argument("--output-dir", default="validation/evidence", help="Evidence output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    db_path = output_dir / "oq_sec_access_control.db"
    if db_path.exists():
        db_path.unlink()

    ac = AccessControlManager(db_path=str(db_path), session_timeout_minutes=30)

    researcher = ac.create_user(
        user_id="u_researcher",
        username="researcher1",
        password="StrongPass!123",
        full_name="Research User",
        email="researcher@example.org",
        role=Role.CLINICAL_RESEARCHER,
    )
    viewer = ac.create_user(
        user_id="u_viewer",
        username="viewer1",
        password="StrongPass!123",
        full_name="Viewer User",
        email="viewer@example.org",
        role=Role.VIEWER,
    )

    researcher_session = ac.authenticate("researcher1", "StrongPass!123")
    viewer_session = ac.authenticate("viewer1", "StrongPass!123")

    checks = {
        "users_created": researcher is not None and viewer is not None,
        "sessions_created": researcher_session is not None and viewer_session is not None,
        "researcher_can_approve_analysis": ac.check_permission("u_researcher", Permission.ANALYSIS_APPROVE),
        "viewer_cannot_approve_analysis": not ac.check_permission("u_viewer", Permission.ANALYSIS_APPROVE),
    }

    # Session lifecycle control check
    if viewer_session:
        ac.invalidate_session(viewer_session.session_id)
        checks["invalidated_session_denied"] = ac.validate_session(viewer_session.session_id) is None
    else:
        checks["invalidated_session_denied"] = False

    passed = all(checks.values())

    evidence = {
        "script_id": "TS-004",
        "generated_at_utc": utc_now(),
        "checks": checks,
        "db_path": str(db_path),
        "result": "PASS" if passed else "FAIL",
    }

    out_path = output_dir / f"OQ-SEC-01_02_TS-004_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {out_path}")
    print(f"Result: {evidence['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
