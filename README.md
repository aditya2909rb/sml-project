# Self-Maintaining Learning (SML) Starter

This project gives you a **continuous learning system** that can:

- Fetch fresh internet text data (RSS, Hacker News, Reddit, arXiv)
- Train a model incrementally in cycles
- Run guarded self-healing actions when checks fail
- Persist learning state to a dedicated Git branch automatically
- Grow model capacity automatically with staged parameter scaling
- Track all learning/healing events in SQLite
- Show live progress in a local Streamlit dashboard
- Expose live health and status JSON endpoints
- Expose a live browser status page and JSON endpoints

## Important reality check

A system with **"no limitations"** is unsafe and unstable. This implementation is built to be practical:

- Uses approved feed sources
- Uses guardrails before applying code fixes
- Keeps logs for every cycle
- Makes healing predictable and reviewable

## Project structure

- `sml/` core engine
- `dashboard.py` local visual tracker
- `main.py` command entrypoint
- `.github/workflows/continuous-learning.yml` GitHub automation

## Quick start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py run-loop --sleep-seconds 120
```

Open dashboard in another terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run dashboard.py
```

## GitHub tracking

After pushing to GitHub, the workflow starts automatically and then keeps running on schedule. It:

1. Pulls new internet data
2. Runs one training/healing cycle
3. Commits and pushes learning state to `sml-learning-state` branch
4. Uploads cycle database as an artifact

You can watch local progress from your own machine with Streamlit (`dashboard.py`).

## Auto-start after upload

The workflow in `.github/workflows/continuous-learning.yml` now triggers on:

1. Push to `main` (starts immediately)
2. Every 30 minutes (`cron`)
3. Manual run (`workflow_dispatch`)

For GitHub-hosted runs, each new VM now resumes from previous state automatically:

1. Restore `sml_state.sqlite3` and `model_store/` from `sml-learning-state`
2. Run one training cycle
3. Persist updated state back to `sml-learning-state`

This means each scheduled run continues from where the previous VM stopped.

## No-limit runtime on GitHub

GitHub-hosted runners are time-limited and ephemeral, so true unlimited runtime is not possible there.

For continuous no-time-limit behavior, use a **self-hosted runner**:

1. In GitHub repo settings, add a self-hosted runner on your own machine or server.
2. Keep that runner online.
3. Push to `main`.

The workflow includes an optional `train-self-hosted-continuous` job that starts:

```bash
python main.py run-loop --sleep-seconds 30
```

This keeps learning from live internet feeds continuously until you stop the runner.

Enable it by setting repository variable `SML_USE_SELF_HOSTED=true`.

## Automatic parameter growth

The system now has a scaling controller that increases model capacity over time.

How it works:

1. Every N cycles (`SML_SCALE_EVERY_CYCLES`), it checks scaling conditions.
2. It only scales when the cycle has enough training samples and minimum accuracy.
3. It moves to the next feature size in `SML_FEATURE_LADDER`.
4. If the ladder is exhausted, it doubles up to `SML_MAX_FEATURES`.

Tracked values are written to `model_progress` in the SQLite DB and shown in:

- Streamlit dashboard (`dashboard.py`)
- Status API (`/status`) as `latest_model_progress`

Long-term target configuration:

- `SML_PARAMETER_TARGET=1024000000000` (1024B target tracker)

Important:

- 1024B is a tracking target in this starter system.
- Actual reachable size on one machine is bounded by RAM/CPU/GPU and `SML_MAX_FEATURES`.
- To move beyond local limits, migrate to distributed training infrastructure.

## Auto state branch persistence

Each cycle can persist the learning state (`sml_state.sqlite3` and `model_store/`) to a separate branch.

Default branch name: `sml-learning-state`

Control with environment variables:

- `SML_PERSIST_ENABLED=true|false`
- `SML_STATE_BRANCH=sml-learning-state`
- `SML_PERSIST_EVERY_CYCLES=1`

The GitHub workflow enables this automatically.

## Live status endpoint

Run status API only:

```bash
python main.py serve-status --host 127.0.0.1 --port 8787
```

Run loop + status API together:

```bash
python main.py run-service --sleep-seconds 30 --host 127.0.0.1 --port 8787
```

Endpoints:

- `GET /` (live browser page)
- `GET /health`
- `GET /status`

Example:

```bash
curl http://127.0.0.1:8787/status
```

Open in browser:

```bash
http://127.0.0.1:8787/
```

## Multi-source ingestion and rate controls

Sources enabled by default:

- RSS feeds (`SML_FEEDS`)
- Hacker News (`SML_HN_ENABLED=true`)
- Reddit (`SML_REDDIT_ENABLED=true`)
- arXiv (`SML_ARXIV_ENABLED=true`)

Rate and per-source volume controls:

- `SML_REQUEST_DELAY_SECONDS=1.0`
- `SML_MAX_ITEMS_PER_FEED=50`
- `SML_HN_MAX_ITEMS=50`
- `SML_REDDIT_SUBREDDITS=technology,MachineLearning,programming`
- `SML_REDDIT_MAX_ITEMS=30`
- `SML_ARXIV_QUERY=cat:cs.LG OR cat:cs.AI`
- `SML_ARXIV_MAX_ITEMS=40`

Source filters:

- `SML_SOURCE_ALLOWLIST=` (empty means all allowed)
- `SML_SOURCE_BLOCKLIST=`

Supported filter tokens:

- `rss`
- `rss:<domain>` (example: `rss:feeds.bbci.co.uk`)
- `hackernews`
- `reddit`
- `reddit:r/<subreddit>` (example: `reddit:r/machinelearning`)
- `arxiv`

Examples:

- Allow only arXiv + Hacker News: `SML_SOURCE_ALLOWLIST=arxiv,hackernews`
- Block one subreddit: `SML_SOURCE_BLOCKLIST=reddit:r/programming`

## Persistence quality gate

State commit/push is blocked unless quality thresholds are met.

Controls:

- `SML_PERSIST_MIN_BATCH_ACCURACY=0.55`
- `SML_PERSIST_RECENT_WINDOW=5`
- `SML_PERSIST_RECENT_MIN_AVG_ACCURACY=0.52`
- `SML_PERSIST_MIN_TRAINED_SAMPLES=20`

If a cycle fails the gate, persistence is skipped and an event is logged as `persist_guard_blocked`.

## Environment options

Copy `.env.example` to `.env` and adjust values.

## Safe self-healing model

When checks fail, the system tries only safe fixes:

1. `ruff check --fix .`
2. `black .`

Then checks are run again. If still failing, it records failure and stops auto-fixing.
