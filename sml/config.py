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
    scaling_enabled: bool
    parameter_target: int
    initial_features: int
    max_features: int
    feature_ladder: list[int]
    scale_every_cycles: int
    scale_min_samples: int
    scale_min_accuracy: float
    # Clinical system configuration
    clinical_enabled: bool
    clinical_data_sources: list[str]
    clinical_api_endpoints: dict[str, str]
    clinical_data_cache_ttl: int
    safety_validation_enabled: bool
    safety_critical_threshold: float
    safety_warning_threshold: float
    ethical_compliance_enabled: bool
    regulatory_compliance_enabled: bool
    enhanced_biological_model_enabled: bool
    patient_data_encryption: bool
    audit_logging_enabled: bool


DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.wired.com/feed/rss",
    "https://hnrss.org/frontpage",
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


def _parse_int_list(raw: str | None, default: list[int]) -> list[int]:
    if not raw:
        return default
    out: list[int] = []
    for item in raw.split(","):
        value = item.strip()
        if not value:
            continue
        try:
            parsed = int(value)
        except ValueError:
            continue
        if parsed > 0:
            out.append(parsed)
    return out or default


def load_config() -> SMLConfig:
    return SMLConfig(
        db_path=os.getenv("SML_DB_PATH", "sml_state.sqlite3"),
        model_dir=os.getenv("SML_MODEL_DIR", "model_store"),
        feeds=_parse_feeds(os.getenv("SML_FEEDS")),
        max_items_per_feed=int(os.getenv("SML_MAX_ITEMS_PER_FEED", "100")),
        min_text_len=int(os.getenv("SML_MIN_TEXT_LEN", "30")),
        request_delay_seconds=float(os.getenv("SML_REQUEST_DELAY_SECONDS", "0.2")),
        hn_enabled=_parse_bool(os.getenv("SML_HN_ENABLED"), True),
        hn_max_items=int(os.getenv("SML_HN_MAX_ITEMS", "100")),
        reddit_enabled=_parse_bool(os.getenv("SML_REDDIT_ENABLED"), True),
        reddit_subreddits=_parse_list(
            os.getenv("SML_REDDIT_SUBREDDITS"),
            ["technology", "MachineLearning", "programming", "artificial", "datascience"],
        ),
        reddit_max_items=int(os.getenv("SML_REDDIT_MAX_ITEMS", "60")),
        arxiv_enabled=_parse_bool(os.getenv("SML_ARXIV_ENABLED"), True),
        arxiv_query=os.getenv("SML_ARXIV_QUERY", "cat:cs.LG OR cat:cs.AI"),
        arxiv_max_items=int(os.getenv("SML_ARXIV_MAX_ITEMS", "80")),
        persist_enabled=_parse_bool(os.getenv("SML_PERSIST_ENABLED"), False),
        state_branch=os.getenv("SML_STATE_BRANCH", "sml-state"),
        persist_every_cycles=int(os.getenv("SML_PERSIST_EVERY_CYCLES", "1")),
        status_host=os.getenv("SML_STATUS_HOST", "127.0.0.1"),
        status_port=int(os.getenv("SML_STATUS_PORT", "8787")),
        source_allowlist=_parse_list(os.getenv("SML_SOURCE_ALLOWLIST"), []),
        source_blocklist=_parse_list(os.getenv("SML_SOURCE_BLOCKLIST"), []),
        persist_min_batch_accuracy=float(os.getenv("SML_PERSIST_MIN_BATCH_ACCURACY", "0.55")),
        persist_recent_window=int(os.getenv("SML_PERSIST_RECENT_WINDOW", "5")),
        persist_recent_min_avg_accuracy=float(os.getenv("SML_PERSIST_RECENT_MIN_AVG_ACCURACY", "0.52")),
        persist_min_trained_samples=int(os.getenv("SML_PERSIST_MIN_TRAINED_SAMPLES", "20")),
        scaling_enabled=_parse_bool(os.getenv("SML_SCALING_ENABLED"), True),
        parameter_target=int(os.getenv("SML_PARAMETER_TARGET", "1024000000000")),
        initial_features=int(os.getenv("SML_INITIAL_FEATURES", str(2**18))),
        max_features=int(os.getenv("SML_MAX_FEATURES", str(2**22))),
        feature_ladder=_parse_int_list(
            os.getenv("SML_FEATURE_LADDER"),
            [2**18, 2**19, 2**20, 2**21, 2**22],
        ),
        scale_every_cycles=int(os.getenv("SML_SCALE_EVERY_CYCLES", "3")),
        scale_min_samples=int(os.getenv("SML_SCALE_MIN_SAMPLES", "80")),
        scale_min_accuracy=float(os.getenv("SML_SCALE_MIN_ACCURACY", "0.62")),
        # Clinical system configuration
        clinical_enabled=_parse_bool(os.getenv("SML_CLINICAL_ENABLED"), True),
        clinical_data_sources=_parse_list(
            os.getenv("SML_CLINICAL_DATA_SOURCES"),
            ["EHR", "CLINICAL_TRIALS", "CANCER_REGISTRIES", "BIOMEDICAL_DATABASES"]
        ),
        clinical_api_endpoints=_parse_clinical_endpoints(os.getenv("SML_CLINICAL_API_ENDPOINTS")),
        clinical_data_cache_ttl=int(os.getenv("SML_CLINICAL_DATA_CACHE_TTL", "3600")),
        safety_validation_enabled=_parse_bool(os.getenv("SML_SAFETY_VALIDATION_ENABLED"), True),
        safety_critical_threshold=float(os.getenv("SML_SAFETY_CRITICAL_THRESHOLD", "0.8")),
        safety_warning_threshold=float(os.getenv("SML_SAFETY_WARNING_THRESHOLD", "0.6")),
        ethical_compliance_enabled=_parse_bool(os.getenv("SML_ETHICAL_COMPLIANCE_ENABLED"), True),
        regulatory_compliance_enabled=_parse_bool(os.getenv("SML_REGULATORY_COMPLIANCE_ENABLED"), True),
        enhanced_biological_model_enabled=_parse_bool(os.getenv("SML_ENHANCED_BIOLOGICAL_MODEL_ENABLED"), True),
        patient_data_encryption=_parse_bool(os.getenv("SML_PATIENT_DATA_ENCRYPTION"), True),
        audit_logging_enabled=_parse_bool(os.getenv("SML_AUDIT_LOGGING_ENABLED"), True),
    )


def _parse_clinical_endpoints(raw: str | None) -> dict[str, str]:
    """Parse clinical API endpoints configuration."""
    if not raw:
        return {
            "ehr_api": "https://api.ehr.example.com",
            "clinical_trials_api": "https://clinicaltrials.gov/api/v2/studies",
            "cancer_registry_api": "https://api.cancerregistry.example.com",
            "cbioportal_api": "https://www.cbioportal.org/api"
        }
    
    endpoints = {}
    for item in raw.split(","):
        item = item.strip()
        if "=" in item:
            key, value = item.split("=", 1)
            endpoints[key.strip()] = value.strip()
    
    return endpoints
