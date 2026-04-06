from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch_json(url: str, timeout: float) -> tuple[int, dict, float, str | None]:
    req = Request(url, headers={"User-Agent": "OncoSML-OQ-TS-001/1.0"})
    started = time.perf_counter()
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode("utf-8"))
            elapsed = time.perf_counter() - started
            return resp.status, payload, elapsed, None
    except URLError as exc:
        elapsed = time.perf_counter() - started
        return 0, {}, elapsed, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="OQ endpoint verification script")
    parser.add_argument("--base-url", default="http://127.0.0.1:8787", help="Base URL for status API")
    parser.add_argument("--timeout-seconds", type=float, default=5.0, help="Per-request timeout")
    parser.add_argument(
        "--output-dir",
        default="validation/evidence",
        help="Directory for generated evidence JSON",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    health_status, health_payload, health_elapsed, health_error = fetch_json(
        f"{args.base_url}/health", args.timeout_seconds
    )
    status_status, status_payload, status_elapsed, status_error = fetch_json(
        f"{args.base_url}/status", args.timeout_seconds
    )

    checks = {
        "health_http_200": health_status == 200,
        "health_status_ok": health_payload.get("status") == "ok",
        "health_response_leq_2s": health_elapsed <= 2.0,
        "status_http_200": status_status == 200,
        "status_has_cycle_count": "cycle_count" in status_payload,
        "status_response_leq_3s": status_elapsed <= 3.0,
    }

    passed = all(checks.values())

    evidence = {
        "script_id": "TS-001",
        "generated_at_utc": utc_now(),
        "base_url": args.base_url,
        "checks": checks,
        "health": {
            "http_status": health_status,
            "elapsed_seconds": round(health_elapsed, 4),
            "payload": health_payload,
            "error": health_error,
        },
        "status": {
            "http_status": status_status,
            "elapsed_seconds": round(status_elapsed, 4),
            "payload_keys": sorted(status_payload.keys()),
            "error": status_error,
        },
        "result": "PASS" if passed else "FAIL",
    }

    output_path = output_dir / f"OQ-FUNC-02_03_TS-001_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Evidence written: {output_path}")
    print(f"Result: {evidence['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
