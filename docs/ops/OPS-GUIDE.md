# FAPD ops guide — read-only health runbook

*Never writes anything. Anything that would — restarts, deploys, config
flips — lives behind the authorization gate in
[AGENT-VPS-SERVICING-GUIDE.md](AGENT-VPS-SERVICING-GUIDE.md) §4.
Last reviewed: 2026-08-02.*

## Local checks (work today, on the operator machine)

```sh
# Digest freshness — newest rendered day and newest complete day
ls digests/*.md | tail -3
uv run python - <<'EOF'
from fapd import db
conn = db.connect()
print("newest extracted day:", conn.execute(
    "SELECT MAX(p.date_issued) FROM packages p"
    " JOIN extracted_texts e USING (package_id)").fetchone()[0])
EOF

# Request-budget posture (per client class, vs GUIDE §4 caps)
uv run python scripts/audit.py

# Token spend today, by purpose and backend
sqlite3 -readonly data/llm_ledger.db "SELECT backend, substr(purpose,1,instr(purpose||':',':')-1),
  COUNT(*), SUM(input_tokens), SUM(output_tokens) FROM llm_calls
  WHERE ts_utc >= date('now') GROUP BY 1,2"

# Validation status of the last render: re-run the render for the newest
# digest date — deterministic and zero-LLM; a PASS costs nothing.
uv run python scripts/digest.py --date <newest> 2>&1 | tail -3

# Collector liveness
sqlite3 -readonly data/fapd.db "SELECT worker, last_ok_at, consecutive_errors
  FROM collector_state ORDER BY worker"
```

## VPS checks (read-only; access facts in the private dossier)

```sh
curl -sI https://fapd.info | head -1                 # HTTP/2 200
ssh <box> 'sudo docker ps --format "{{.Names}}\t{{.Status}}" | grep fapd'
ssh <box> 'sudo docker inspect fapd-web --format "{{json .NetworkSettings.Networks}}"'
#   ^ exactly fapd_edge, nothing else
ssh <box> 'sudo certbot certificates 2>/dev/null | grep -A3 fapd.info'
```

## Cadence

| When | What | Why |
|---|---|---|
| Daily / casual | local checks block | freshness, budget, spend anomalies |
| **After every deploy** | VPS block, immediately **and again ~5 min later** | containers came back clean, no error surge |
| Weekly | CVE sweep ([AGENT-CVE-GUIDE.md](AGENT-CVE-GUIDE.md)) | dependency/base-image drift |
| TLS <30 days to expiry | `certbot renew --dry-run` (on box) | catch hook breakage before the real renewal |
| After a collector change | `collect.py --once --no-llm --no-wayback` + collector_state read | cycle integrity without token spend or archive writes |
| Before any deploy | `deploy/dev/scripts/dev-up.sh` render against a recent VPS seed | the change seen on production-shaped data first (advisory) |
