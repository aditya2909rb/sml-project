from __future__ import annotations

import argparse
import threading
from pathlib import Path

from sml.config import load_config
from sml.runner import run_loop, run_one_cycle
from sml.status_api import run_status_server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Self-Maintaining Learning (SML)")
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


if __name__ == "__main__":
    main()
