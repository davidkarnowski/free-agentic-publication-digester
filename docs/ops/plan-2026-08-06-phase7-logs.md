# P7 — edge-log rotation + healthz silence (operator-approved "both")

**Files:** `scripts/staged/2026-08-06-edge-log-rotation.sh` (new);
the healthz change is authored in the **Spiralyst tree** (their edge
config), deployed per their runbook — record in both WORKLOGs.

1. Staged script (servicing-guide §2 shape: preconditions → backup →
   change → self-verify → verdict): writes
   `/etc/logrotate.d/spiralyst-nginx`:
   ```
   /opt/spiralyst/logs/nginx/*.log {
     daily
     rotate 14
     compress
     delaycompress
     missingok
     notifempty
     sharedscripts
     postrotate
       docker exec spiralyst-proxy nginx -s reopen
     endscript
   }
   ```
   Preconditions: file absent; logs exist; container running.
   Self-verify: `logrotate -d` dry-run clean, then `logrotate --force`
   once; access.log size drops to ~0 with a compressed sibling; a new
   request line lands in the fresh file (reopen worked).
2. Healthz: `location = /healthz { access_log off; return 200 ...; }`
   (match their existing healthz block's response) in the edge config
   in the Spiralyst repo; rehearse `nginx -t` in a throwaway container
   attached to the real networks; deploy with
   `up -d --force-recreate` (single-file bind-mount rule).
3. `docs/ops/ops-backlog.md` OB-15 Done-note — including the
   correction that `/etc/logrotate.d/docker-containers` already covers
   container json logs (the original entry overstated the docker gap).

**Verify:** next healthcheck cycle writes nothing to access.log;
`curl fapd.info` still 200; error.log rotating too.
**Rollback:** remove the logrotate file; revert the config, recreate.
