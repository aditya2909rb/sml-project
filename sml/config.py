from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SMLConfig:
    db_path: str
    model_dir: str
    feeds: list[str]
    max_items_per_feed: int
    min_text_len: int
    request_delay_seconds: float
    hn_enabled: bool
    hn_max_items: int
    reddit_enabled: bool
    reddit_subreddits: list[str]
    reddit_max_items: int
    arxiv_enabled: bool
    arxiv_query: str
    arxiv_max_items: int
    persist_enabled: bool
    state_branch: str
    persist_every_cycles: int
    status_host: str
    status_port: int
    source_allowlist: list[str]
    source_blocklist: list[str]
    persist_min_batch_accuracy: float
    persist_recent_window: int
    persist_recent_min_avg_accuracy: float
    persist_min_trained_samples: int


DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://www.theverge.com/rss/index.xml",
]


def _parse_feeds(raw: str | None) -> list[str]:
    if not raw:
        return DEFAULT_FEEDS
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_list(raw: str | None, default: list[str]) -> list[str]:
    if not raw:
        return default
    parsed = [item.strip() for item in raw.split(",") if item.strip()]
    return parsed or default


def _parse_bool(raw: str | None, default: bool) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> SMLConfig:
    return SMLConfig(
        db_path=os.getenv("SML_DB_PATH", "sml_state.sqlite3"),
        model_dir=os.getenv("SML_MODEL_DIR", "model_store"),
        feeds=_parse_feeds(os.getenv("SML_FEEDS")),
        max_items_per_feed=int(os.getenv("SML_MAX_ITEMS_PER_FEED", "50")),
        min_text_len=int(os.getenv("SML_MIN_TEXT_LEN", "30")),
        request_delay_seconds=float(os.getenv("SML_REQUEST_DELAY_SECONDS", "1.0")),
        hn_enabled=_parse_bool(os.getenv("SML_HN_ENABLED"), True),
        hn_max_items=int(os.getenv("SML_HN_MAX_ITEMS", "50")),
        reddit_enabled=_parse_bool(os.getenv("SML_REDDIT_ENABLED"), True),
        reddit_subreddits=_parse_list(
            os.getenv("SML_REDDIT_SUBREDDITS"),
            ["technology", "MachineLearning", "programming"],
        ),
        reddit_max_items=int(os.getenv("SML_REDDIT_MAX_ITEMS", "30")),
        arxiv_enabled=_parse_bool(os.getenv("SML_ARXIV_ENABLED"), True),
        arxiv_query=os.getenv("SML_ARXIV_QUERY", "cat:cs.LG OR cat:cs.AI"),
        arxiv_max_items=int(os.getenv("SML_ARXIV_MAX_ITEMS", "40")),
        persist_enabled=_parse_bool(os.getenv("SML_PERSIST_ENABLED"), False),
        state_branch=os.getenv("SML_STATE_BRANCH", "sml-learning-state"),
        persist_every_cycles=int(os.getenv("SML_PERSIST_EVERY_CYCLES", "1")),
        status_host=os.getenv("SML_STATUS_HOST", "127.0.0.1"),
        status_port=int(os.getenv("SML_STATUS_PORT", "8787")),
        source_allowlist=_parse_list(os.getenv("SML_SOURCE_ALLOWLIST"), []),
        source_blocklist=_parse_list(os.getenv("SML_SOURCE_BLOCKLIST"), []),
        persist_min_batch_accuracy=float(os.getenv("SML_PERSIST_MIN_BATCH_ACCURACY", "0.55")),
        persist_recent_window=int(os.getenv("SML_PERSIST_RECENT_WINDOW", "5")),
        persist_recent_min_avg_accuracy=float(os.getenv("SML_PERSIST_RECENT_MIN_AVG_ACCURACY", "0.52")),
        persist_min_trained_samples=int(os.getenv("SML_PERSIST_MIN_TRAINED_SAMPLES", "20")),
    )
