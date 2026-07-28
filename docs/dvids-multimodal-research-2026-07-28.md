# DVIDS multi-modal deep dive + government media-source survey — 2026-07-28

Documentation-only research (WebSearch/WebFetch of doc pages; no endpoints
probed). Evidence labels: **fetched** = page read this session;
**search-corroborated** = asserted from snippets. Research-fetcher 403s are
not availability verdicts for our identified client (standing rule,
`docs/source-research-2026-07-28.md` §6).

## DVIDS (dvidshub.net / api.dvidshub.net)

DoD's 24/7 distribution platform for public military media — "over 1.8
million assets" (docs index, fetched). Operated from Fort Meade by the
Defense Media Activity — whose `/about` page (fetched) now reads "DWIA
(Department of War Information Activity)" under the 2025 renaming, with
DVIDS expanded as "Digital Visual Information Distribution System"; treat
DMA→DWIA as a rename in progress and expect defense.gov→war.gov hostname
churn (another reason to prefer the stable API host). Support:
dvidsservicedesk@dvidshub.net.

### Search API — `GET /search` (docs fetched)

- `api_key` required; "access is currently open," free key via site
  registration. (OAuth2 exists but only for member-account operations.)
- Asset `type`: news, video, image, audio, publication_issue, webcast,
  graphics. Filters: `branch` (all seven incl. Space Force), unit
  (+`unit_rollup`), three date axes each with from/to ranges — `date`
  (shot), `publishdate`, `timestamp` (last update) — location/cocom,
  category, credit, media filters (hd, duration, has_captions).
- Pagination: `page` × `max_results` (≤50), **hard cap at depth 1000** —
  forces date-window slicing, which our §4 date-bound rule already mandates.
- Result fields include id, type, title, short_description (≤300 chars),
  credit, branch, unit_name, dates, keywords, thumbnail, dimensions,
  duration, url. `format=rss` output mode exists. `total_results` in
  `page_info` makes volume censuses cheap (~49 requests cover 7 branches ×
  7 types for any window — make this part of the probe).
- Rate limits unpublished; TOS reserves discretionary quotas.

### Asset API — `GET /asset?id=type:number` (docs fetched)

- **image**: `image` = *direct full-resolution download URL*; dynamic
  `thumbnail` (≤2000 px); `dimensions`; `description` = the official
  caption; `credit` = structured array (name, rank, ID); **`virin`**;
  `date` (shot) vs `date_published` vs `timestamp` all distinguished;
  location; unit/branch; canonical page `url`.
- **video**: `files[]` MP4 renditions with src/size/bitrate (documented
  example up to 1280×720 @ 9,173 kbps); `hls_url`;
  **`closed_caption_urls {srt, webvtt}`** — official transcripts as tiny
  text files; full-res frame capture; same credit/VIRIN apparatus.
- **publication_issue**: direct PDF `file`. **news**: no documented
  response example — whether it carries full body text is *the* open probe
  question.
- 403 = bad key, origin mismatch, **or asset unpublished** — takedowns are
  visible, a removal signal our mutable-source machinery should surface.

### Licensing (exact language, fetched)

- Copyright policy: "All media on the site is produced by U.S. DoD or
  Federal Agency and is in the public domain unless other copyright status
  is indicated." No suggesting DoD **endorsement**; journalist credit is
  *requested*.
- FAQ: public information, distributable "unless otherwise specified";
  some assets contractor-licensed — "examine the copyright area at the
  bottom of each media asset page."
- API TOS: "All media assets and information accessible via the DVIDS API
  is free for commercial use." Discretionary quotas, no circumvention; no
  obscuring usage from monitoring (our identified-client posture is
  exactly compliant); cache-refresh duty — poll `timestamp`, not just
  `publishdate`, to honor it.

### VIRIN (search-corroborated from DoDI 5040.02 + DoD VI Style Guide 2025)

18 characters, 4 fields: `YYMMDD-S-VISIONID-SEQ` (shoot date, service
letter of the photographer, photographer ID, 4-digit daily sequence).
DoD-wide official identifier — **store it, but don't key on it**: the API
returns it only "where applicable" (news has none), and the API's own
retrieval key is `type:number`. Recommended
`stable_id = dvids:{type}:{id}`, with VIRIN kept as an official
cross-system identifier (it encodes shoot date + service + photographer —
provenance for free).

### Content shape, volatility

Imagery (stills + b-roll) is the bulk; `news` is the unit-journalism
layer; publication_issue = unit magazines as PDFs. Captions are governed
official prose (DoD Captioning Style Guide): complete who/what/when/where
plus credit — **verbatim-eligible official text** under our
official-summaries-first rule, like FR abstracts. Volatility: documented
mass removals (2021 Afghan-war photos; 2025 DEI purge) — capture-before-
extract applies with full force; captured assets outliving platform
removals is itself accountability data.

**DIMOC** (dimoc.mil): the archive-of-record sibling — preservation, not
news-flow; adds nothing for a daily digest; historical backfill only.
defense.gov curated photo pages: no machine channel; superseded by the API.

## Adapter design sketch — `DvidsAdapter`

One registry entry, `type: api`, rung 1. Sync: per-branch date-windowed
`/search` from a `publishdate` watermark (+ a `timestamp` pass for the TOS
cache duty), then `/asset` for selected items, then media downloads —
everything through the budgeted client, one host = one worker = one pacing
clock.

Mapping: every asset → `packages` (stable_id `dvids:{type}:{id}`;
attributed to the originating unit per the aggregator rule — DVIDS is
transport). News body (probe-dependent, else short_description; mode
disclosed) → `extracted_texts`. Image caption → `extracted_texts`, marked
official. Image bytes → `graphic_assets` with sha256, dimensions,
structured credit, VIRIN, location, shot date. Video → metadata +
thumbnail + SRT/WebVTT captions only; `files[]` renditions stored as
metadata so the no-download decision is reversible per asset.

**New adapter decision — `asset_posture(type)`**, the `wants_article`
analog for multi-modal sources: news=fetch_body, image=download_original
(budget-gated), video=metadata+thumbnail+captions, audio=metadata_only,
webcast=skip. Recorded per package like fetch mode — under-coverage
disclosed, never silent.

### Proposed GUIDE amendments (pending operator approval — not yet applied)

1. **§4 media byte budget**: request counts don't govern 10 MB originals;
   add a per-day media download byte budget (suggest 250–500 MB) + image
   count cap, client-enforced.
2. **§3 video posture rule**: captions/thumbnail/metadata only; no A/V
   downloads without a deliberate GUIDE change.
3. **§2/§6 official captions as official text**: verbatim-eligible,
   attributed, zero-token drafting input.
4. **Credit-line rule**: rendered images carry the credit line; standing
   no-endorsement disclosure; per-asset copyright-status check (some DVIDS
   assets are contractor-licensed).
5. **Adapter contract**: add `asset_posture` as the fifth adapter decision.
6. **Registry currency class**: `archive` vs `news-flow` annotation, so
   archives can be registered without entering daily-coverage accounting.

### Probe checklist (operator step — key signup required first)

Registration friction; news body text presence/format; observed rate-limit
headers; whether the API image URL serves full-res without login; CDN URL
stability (signed/expiring?); per-branch daily volume census; robots.txt
on api host + CDN; defense.gov imagery-use page via our client.

## Multi-modal siblings survey

| Source | Access | Currency | Verdict |
|---|---|---|---|
| NASA Image & Video Library | images-api.nasa.gov (spec PDF fetched, v1.22.0): /search, /asset, /metadata, /captions; keyless | News-flow + archive; no changed-since filter — date-windowed search + client dedupe | **Onboard second**, after DVIDS proves the multi-modal path |
| NPS API | developer.nps.gov, 1,000 req/hr, key (search-corroborated) | Mixed; news/alerts current | Register tier 3 planned; text value first |
| NARA Catalog v2 | catalog.archives.gov/api/v2, key by email, 10k queries/month | Archive | Evaluated-excluded for daily flow (archive, not news-flow) |
| Library of Congress | loc.gov/apis, keyless, 429s under load; rights vary per item | Archive | Evaluated-excluded for daily flow |
| NOAA photolib / NESDIS | No documented media API found | — | Not registered |
| USGS galleries | No documented media API (M2M is science data) | — | Not registered |
| USDA / State Flickr | Official accounts on commercial platform | Semi-current | Operator decision — new source-class question (same family as epa.mediaroom.com and email ingestion) |

**Core finding:** DVIDS is the only government source that is at once a
daily visual news-flow, behind a documented filterable API with full-res
URLs + official captions + credit + identifiers, and explicitly free for
reuse. NASA is second on every axis. Everything else is archive, API-less,
or commercially hosted.
