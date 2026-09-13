# Phase 6 — DNS: DNSSEC and DNS-AID (agent discovery)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md).
Task AD-13. Performed by the **operator** in the Hostinger DNS panel
(checkpoint C-5), with the **orchestrator** researching the record format
and verifying from outside. Depends on Phase 5 done. Ruling D5: turn on
DNSSEC if supported; publish DNS-AID only after reading the current draft
and confirming SVCB support; don't move DNS providers. Last reviewed:
2026-09-13.*

## 0. Outcome

`fapd.info` is DNSSEC-signed (if Hostinger supports it for `.info`), and
a DNS-AID index record points agents at the site's AI Catalog. **Or**
the plan records, with evidence, which of those the panel can't do and
stops there.

## 1. What the scanner checks (2026-09-12 evidence)

DNS-over-HTTPS queries (Cloudflare resolver, Google fallback) for:
`SVCB` and `HTTPS` at `_index._agents.fapd.info`, `_a2a._agents.fapd.info`
and `_mcp._agents.fapd.info`, and `TXT` at `_index._agents.fapd.info`.
It also checks `TXT _catalog._agents` and `SRV _search._agents` for the AI
Catalog. It reports whether DNSSEC validated. All returned NXDOMAIN, and
the zone's authority is Hostinger (`dns-parking.com` nameservers).

The scanner's advice: SVCB records "with alpn and endpoint parameters",
`mandatory` for critical parameters, experimental parameters as
`keyNNNNN`, and a DNSSEC-signed zone.

## 2. Orchestrator research (before the operator touches the panel)

1. Find and read the **current** DNS-AID Internet-Draft (search the IETF
   datatracker for "DNS for AI Discovery" / "DNS-AID"; note the draft name
   and revision). Record in the orchestrator log: exact owner names, the
   SVCB `alpn` values it defines (for an HTTPS-reachable index, for MCP),
   any registered or experimental SvcParamKeys (e.g. a path or
   well-known-document key), and the TXT index-entry syntax.
2. Read the AI Catalog spec's DNS section
   (`Agent-Card/ai-catalog`, `specification/ai-catalog.md`) for
   `_catalog._agents` TXT syntax (e.g. `url=…`).
3. Draft the exact records for FAPD, **truthful only**:
   - `_index._agents.fapd.info` → the site's agent index, i.e.
     `https://fapd.info/.well-known/ai-catalog.json`, in whatever form
     the draft specifies (SVCB target `fapd.info.`, `port=443`, an
     `alpn` for HTTPS, plus the draft's path or document parameter if it
     has one; or a TXT index entry).
   - `_mcp._agents.fapd.info` → **only if the draft defines an MCP
     service binding**: target `fapd.info.`, port 443, the draft's MCP
     `alpn`, and the endpoint path `/mcp` in the draft's parameter. The
     service now genuinely exists (Phase 5), so this record is truthful.
   - `_catalog._agents.fapd.info TXT "url=https://fapd.info/.well-known/ai-catalog.json"`
     if the AI Catalog spec defines it that way.
   - **No `_a2a` record** (FAPD offers no A2A agent).
4. Hand the operator a table: owner name, type, TTL (3600), value, and the
   draft section that justifies each field.

## 3. Operator actions (C-5, Hostinger hPanel → Domains → fapd.info → DNS)

1. **DNSSEC:** in the domain's DNSSEC settings, turn it on if offered.
   Hostinger manages the keys when its nameservers are in use. Tell the
   orchestrator when it's done. (If the panel says it isn't available for
   this TLD or plan, report that; don't move providers.)
2. **Record support:** check whether "Add record" offers **SVCB** and
   **HTTPS** types.
   - If yes: add the records from §2.4.
   - If only TXT: add the TXT forms the draft allows, and report that
     SVCB wasn't available.
   - If neither form is allowed by the draft with the types available:
     add nothing, and report.
3. Don't change `A`, `AAAA`, `CAA`, `MX` or existing `TXT` records. **Never
   remove an apex TXT record without asking.** A future MCP Registry DNS
   proof would live there, and other verifications may already.

## 4. Verification (orchestrator, from outside, after propagation)

```sh
# DNSSEC: the AD flag from a validating resolver
curl -s 'https://cloudflare-dns.com/dns-query?name=fapd.info&type=A&do=1' -H 'accept: application/dns-json' | python3 -m json.tool | grep -E '"AD"|"Status"'
dig +dnssec fapd.info A @1.1.1.1 | grep -E 'flags:|RRSIG'
dig DS fapd.info @1.1.1.1 +short        # DS present at the parent once signed

# DNS-AID, the queries the scanner makes
for t in SVCB HTTPS TXT; do
  curl -s "https://cloudflare-dns.com/dns-query?name=_index._agents.fapd.info&type=$t&do=1" -H 'accept: application/dns-json'; echo
done
dig _index._agents.fapd.info SVCB @1.1.1.1 +short
dig _catalog._agents.fapd.info TXT @1.1.1.1 +short
```

Every record's target must resolve, and every URL it names must return
200 (checked with `curl -sI`).

## 5. Rollback

- Delete the added `_agents` records in the panel.
- **DNSSEC off, in this order:** remove the DS record at the registrar or
  parent (Hostinger may do both in one toggle; confirm first). Wait for
  the DS TTL to expire. Only then stop signing. Turning signing off while
  a DS remains makes the domain fail to resolve for validating resolvers.

## 6. Record

WORKLOG entry: panel capabilities found, records added (exact values),
verification output, and whether the scanner's check 4 now passes (from a
re-scan or the isitagentready API). Master plan status table: Phase 6.
Blog notes: what DNS-AID is, in two plain sentences, and whether a typical
small site can even publish it.
