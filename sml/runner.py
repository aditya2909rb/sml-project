from __future__ import annotations

import time
from pathlib import Path

from sml.config import SMLConfig
from sml.data_ingest import fetch_all_samples
from sml.git_persist import persist_learning_state
from sml.healing import attempt_self_heal
from sml.model import OnlineTextModel
from sml.state import end_cycle, get_recent_batch_accuracies, init_db, log_event, mark_seen_and_filter_new, start_cycle


def run_one_cycle(config: SMLConfig, repo_root: Path) -> None:
    init_db(config.db_path)
    cycle_id = start_cycle(config.db_path)
    log_event(config.db_path, "INFO", "cycle_start", f"cycle {cycle_id} started")

    try:
        samples, fetch_errors = fetch_all_samples(
            feeds=config.feeds,
            max_items=config.max_items_per_feed,
            min_text_len=config.min_text_len,
            request_delay_seconds=config.request_delay_seconds,
            hn_enabled=config.hn_enabled,
            hn_max_items=config.hn_max_items,
            reddit_enabled=config.reddit_enabled,
            reddit_subreddits=config.reddit_subreddits,
            reddit_max_items=config.reddit_max_items,
            arxiv_enabled=config.arxiv_enabled,
            arxiv_query=config.arxiv_query,
            arxiv_max_items=config.arxiv_max_items,
            source_allowlist=config.source_allowlist,
            source_blocklist=config.source_blocklist,
        )

        for err in fetch_errors:
            log_event(config.db_path, "WARN", "ingest_error", err)

        hashes = [s.text_hash for s in samples]
        new_hashes = mark_seen_and_filter_new(config.db_path, hashes)
        fresh = [s for s in samples if s.text_hash in new_hashes]

        model = OnlineTextModel(config.model_dir)
        model.load()
        train_result = model.train(
            texts=[s.text for s in fresh],
            labels=[s.label for s in fresh],
        )

        heal_result = attempt_self_heal(repo_root)
        status = "ok" if heal_result.checks_ok else "needs_attention"

        log_event(
            config.db_path,
            "INFO" if heal_result.checks_ok else "ERROR",
            "healing",
            "self-heal run completed",
            {
                "healed": heal_result.healed,
                "details": heal_result.details[-2000:],
            },
        )

        end_cycle(
            db_path=config.db_path,
            cycle_id=cycle_id,
            status=status,
            new_samples=len(fresh),
            trained_samples=train_result.trained_samples,
            batch_accuracy=train_result.batch_accuracy,
            notes="cycle completed",
        )

        should_persist = config.persist_enabled and cycle_id % max(1, config.persist_every_cycles) == 0
        if should_persist:
            current_acc = train_result.batch_accuracy
            recent_accuracies = get_recent_batch_accuracies(config.db_path, config.persist_recent_window)
            avg_recent_acc = sum(recent_accuracies) / len(recent_accuracies) if recent_accuracies else None

            gate_fail_reasons: list[str] = []
            if train_result.trained_samples < config.persist_min_trained_samples:
                gate_fail_reasons.append(
                    f"trained_samples={train_result.trained_samples} is below min {config.persist_min_trained_samples}"
                )
            if current_acc is None:
                gate_fail_reasons.append("batch_accuracy is None")
            elif current_acc < config.persist_min_batch_accuracy:
                gate_fail_reasons.append(
                    f"batch_accuracy={current_acc:.4f} is below min {config.persist_min_batch_accuracy:.4f}"
                )
            if avg_recent_acc is None:
                gate_fail_reasons.append("no recent accuracies available")
            elif avg_recent_acc < config.persist_recent_min_avg_accuracy:
                gate_fail_reasons.append(
                    f"recent_avg_accuracy={avg_recent_acc:.4f} is below min {config.persist_recent_min_avg_accuracy:.4f}"
                )

            if gate_fail_reasons:
                log_event(
                    config.db_path,
                    "WARN",
                    "persist_guard_blocked",
                    "state persistence blocked by quality gate",
                    {
                        "reasons": gate_fail_reasons,
                        "current_accuracy": current_acc,
                        "recent_window": config.persist_recent_window,
                        "recent_avg_accuracy": avg_recent_acc,
                    },
                )
                return

            ok, message = persist_learning_state(
                repo_root=repo_root,
                db_path=config.db_path,
                model_dir=config.model_dir,
                branch=config.state_branch,
            )
            log_event(
                config.db_path,
                "INFO" if ok else "ERROR",
                "state_persist",
                message,
                {"branch": config.state_branch},
            )

    except Exception as exc:  # noqa: BLE001
        log_event(config.db_path, "ERROR", "cycle_failure", str(exc))
        end_cycle(
            db_path=config.db_path,
            cycle_id=cycle_id,
            status="failed",
            new_samples=0,
            trained_samples=0,
            batch_accuracy=None,
            notes=str(exc),
        )


def run_loop(config: SMLConfig, repo_root: Path, sleep_seconds: int) -> None:
    while True:
        run_one_cycle(config=config, repo_root=repo_root)
        time.sleep(sleep_seconds)
