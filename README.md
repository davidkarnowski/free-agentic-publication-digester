# Information Intelligence

Automated monitoring of official US government publications (Congressional
Record, bills, Federal Register) producing a cited, opinion-agnostic daily
digest.

- **[GUIDE.md](GUIDE.md)** — governing document: mission, editorial
  principles, data sources, respectful-access policy, architecture, roadmap.
- **[WORKLOG.md](WORKLOG.md)** — timestamped log of all work sessions.

## Setup

```sh
uv sync                                # install dependencies into .venv
cp .env.example .env                   # then paste your api.data.gov key
uv run python scripts/verify_key.py    # one-request sanity check
```

Get a free API key at https://api.data.gov/signup/ (emailed instantly).

## Daily sync

```sh
uv run python scripts/sync.py                  # delta sync CREC, BILLS, FR
uv run python scripts/sync.py --list-only      # inventory only, no downloads
uv run python scripts/sync.py --max-downloads 50
```

Sync is watermark-based (only changes since the last run are listed) and
rate-limited per [GUIDE.md](GUIDE.md) §4. A first run with no watermark is
date-bounded to the last 3 days; deeper history comes from govinfo's bulkdata
service, never the API.

## Layout

```
src/info_intel/   pipeline code (fetch → extract → analyze → report)
scripts/          one-off / operational scripts
data/             raw document archive + SQLite (git-ignored)
digests/          generated daily digests (committed)
tests/
```
