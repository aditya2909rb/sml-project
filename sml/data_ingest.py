from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from urllib.parse import quote_plus, urlparse

import feedparser  # type: ignore[import-not-found]
import requests


POSITIVE_HINTS = {"growth", "breakthrough", "success", "improve", "win", "record"}
NEGATIVE_HINTS = {"crisis", "fail", "drop", "lawsuit", "attack", "loss"}
USER_AGENT = "sml-bot/1.0 (+https://github.com/)"


@dataclass
class TextSample:
    source: str
    text: str
    label: int
    text_hash: str


def _label_from_text(text: str) -> int:
    low = text.lower()
    pos = sum(1 for w in POSITIVE_HINTS if w in low)
    neg = sum(1 for w in NEGATIVE_HINTS if w in low)
    return 1 if pos >= neg else 0


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_tags(source: str) -> set[str]:
    src = source.strip().lower()
    if src.startswith("http://") or src.startswith("https://"):
        domain = urlparse(src).netloc
        return {"rss", f"rss:{domain}", src}
    if src.startswith("reddit:r/"):
        return {"reddit", src}
    if src == "hackernews":
        return {"hackernews"}
    if src == "arxiv":
        return {"arxiv"}
    return {src}


def _is_source_allowed(source: str, allowlist: list[str], blocklist: list[str]) -> bool:
    tags = _source_tags(source)
    blocked = {item.strip().lower() for item in blocklist if item.strip()}
    if blocked and any(tag in blocked for tag in tags):
        return False

    allowed = {item.strip().lower() for item in allowlist if item.strip()}
    if not allowed:
        return True
    return any(tag in allowed for tag in tags)


def _filter_samples_by_source(samples: list[TextSample], allowlist: list[str], blocklist: list[str]) -> list[TextSample]:
    return [sample for sample in samples if _is_source_allowed(sample.source, allowlist=allowlist, blocklist=blocklist)]


def fetch_feed_samples(feed_url: str, max_items: int, min_text_len: int) -> list[TextSample]:
    response = requests.get(feed_url, timeout=15, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()

    parsed = feedparser.parse(response.text)
    out: list[TextSample] = []
    for entry in parsed.entries[:max_items]:
        title = str(entry.get("title", "")).strip()
        summary = str(entry.get("summary", "")).strip()
        text = f"{title}. {summary}".strip()
        if len(text) < min_text_len:
            continue
        out.append(
            TextSample(
                source=feed_url,
                text=text,
                label=_label_from_text(text),
                text_hash=_stable_hash(text),
            )
        )
    return out


def fetch_hackernews_samples(max_items: int, min_text_len: int, delay_seconds: float) -> list[TextSample]:
    url = f"https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage={max_items}"
    response = requests.get(url, timeout=15, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    payload = response.json()

    out: list[TextSample] = []
    for hit in payload.get("hits", [])[:max_items]:
        title = str(hit.get("title") or "").strip()
        story = str(hit.get("story_text") or "").strip()
        text = f"{title}. {story}".strip()
        if len(text) < min_text_len:
            continue
        out.append(
            TextSample(
                source="hackernews",
                text=text,
                label=_label_from_text(text),
                text_hash=_stable_hash(text),
            )
        )

    if delay_seconds > 0:
        time.sleep(delay_seconds)
    return out


def fetch_reddit_samples(
    subreddits: list[str],
    max_items_per_subreddit: int,
    min_text_len: int,
    delay_seconds: float,
) -> list[TextSample]:
    out: list[TextSample] = []
    for subreddit in subreddits:
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={max_items_per_subreddit}"
        response = requests.get(url, timeout=15, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        payload = response.json()

        children = payload.get("data", {}).get("children", [])
        for child in children[:max_items_per_subreddit]:
            data = child.get("data", {})
            title = str(data.get("title") or "").strip()
            body = str(data.get("selftext") or "").strip()
            text = f"{title}. {body}".strip()
            if len(text) < min_text_len:
                continue
            out.append(
                TextSample(
                    source=f"reddit:r/{subreddit}",
                    text=text,
                    label=_label_from_text(text),
                    text_hash=_stable_hash(text),
                )
            )

        if delay_seconds > 0:
            time.sleep(delay_seconds)
    return out


def fetch_arxiv_samples(query: str, max_items: int, min_text_len: int, delay_seconds: float) -> list[TextSample]:
    encoded_query = quote_plus(query)
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={encoded_query}&start=0&max_results={max_items}&sortBy=submittedDate&sortOrder=descending"
    )
    response = requests.get(url, timeout=20, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    parsed = feedparser.parse(response.text)

    out: list[TextSample] = []
    for entry in parsed.entries[:max_items]:
        title = str(entry.get("title", "")).strip()
        summary = str(entry.get("summary", "")).strip()
        text = f"{title}. {summary}".strip()
        if len(text) < min_text_len:
            continue
        out.append(
            TextSample(
                source="arxiv",
                text=text,
                label=_label_from_text(text),
                text_hash=_stable_hash(text),
            )
        )

    if delay_seconds > 0:
        time.sleep(delay_seconds)
    return out


def fetch_all_samples(
    feeds: list[str],
    max_items: int,
    min_text_len: int,
    request_delay_seconds: float,
    hn_enabled: bool,
    hn_max_items: int,
    reddit_enabled: bool,
    reddit_subreddits: list[str],
    reddit_max_items: int,
    arxiv_enabled: bool,
    arxiv_query: str,
    arxiv_max_items: int,
    source_allowlist: list[str],
    source_blocklist: list[str],
) -> tuple[list[TextSample], list[str]]:
    samples: list[TextSample] = []
    errors: list[str] = []

    for url in feeds:
        try:
            samples.extend(fetch_feed_samples(url, max_items=max_items, min_text_len=min_text_len))
            if request_delay_seconds > 0:
                time.sleep(request_delay_seconds)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{url}: {exc}")

    if hn_enabled:
        try:
            samples.extend(
                fetch_hackernews_samples(
                    max_items=hn_max_items,
                    min_text_len=min_text_len,
                    delay_seconds=request_delay_seconds,
                )
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"hackernews: {exc}")

    if reddit_enabled:
        try:
            samples.extend(
                fetch_reddit_samples(
                    subreddits=reddit_subreddits,
                    max_items_per_subreddit=reddit_max_items,
                    min_text_len=min_text_len,
                    delay_seconds=request_delay_seconds,
                )
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"reddit: {exc}")

    if arxiv_enabled:
        try:
            samples.extend(
                fetch_arxiv_samples(
                    query=arxiv_query,
                    max_items=arxiv_max_items,
                    min_text_len=min_text_len,
                    delay_seconds=request_delay_seconds,
                )
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"arxiv: {exc}")

    filtered = _filter_samples_by_source(samples, allowlist=source_allowlist, blocklist=source_blocklist)
    return filtered, errors
