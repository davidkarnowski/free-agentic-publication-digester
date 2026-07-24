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

## Layout

```
src/info_intel/   pipeline code (fetch → extract → analyze → report)
scripts/          one-off / operational scripts
data/             raw document archive + SQLite (git-ignored)
digests/          generated daily digests (committed)
tests/
```
