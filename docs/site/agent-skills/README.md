# Agent Skills sources

One directory per skill, each holding a `SKILL.md` with YAML front matter
(`name`, `description`) followed by the instructions an AI agent reads
(Agent Skills Discovery RFC v0.2.0). The site build
(`publish._build_discovery_documents`) copies every `<name>/SKILL.md`
here byte-for-byte to `site/.well-known/agent-skills/<name>/SKILL.md`
and writes `site/.well-known/agent-skills/index.json` with a `sha256:`
digest of each copied file, so the index always matches what is served.

`publish._doc_sources` globs `docs/site/*.md` non-recursively, so nothing
in this directory renders as a site page; this README is not published.

The four skills (`docs/ops/plan-2026-09-13-phase1-discovery-documents.md`,
AD-6): `fapd-daily-digest`, `fapd-live-day`, `fapd-source-coverage`,
`fapd-verify-the-record`. Every sentence in them is the project's own
prose and is scanned for the banned lexicon by
`tests/test_agent_discovery.py`; a skill that names a URL on fapd.info
must name one the build produces or `openapi.json` documents.
