# Official-channel YouTube transcripts — access & ethos research, 2026-07-29

Documentation-only research (no probing; public docs/terms pages only).
The consent test throughout: does the publisher (the agency) or the
intermediary (YouTube/Google) consent to the access path?

**Bottom line up front:** the YouTube caption/transcript itself is
mostly not legitimately reachable by a non-owner — and it barely
matters, because for essentially every class of official federal video
the transcript's authoritative home is a .gov page we can ingest under
existing rules. YouTube is the mirror, not the record.

## What the Data API actually permits (quotes fetched from Google docs)

- **`captions.download` is owner-only**: "requires the user to have
  permission to edit the video" (OAuth `youtube.force-ssl` /
  `youtubepartner` scopes; 200 quota units). No federal agency will
  OAuth-authorize our client against their channel. There is no API-key
  path to caption text. Not a probe candidate.
- **`captions.list`** returns track *metadata* only, and its docs
  require authorization too — so a key-only client likely cannot even
  classify a video's captions as official-vs-ASR. The public
  `contentDetails.caption` field is a bare true/false.
- **Terms that bind an API client:** Developer Policies III.E.1 (no
  downloading/caching/storing audiovisual content without written
  approval); III.E.6 (no scraping — and no *obtaining* scraped YouTube
  data from third parties); III.D.7 (only documented means);
  **III.E.4.d — the archival killer**: non-authorized data may be
  stored at most **30 calendar days**, then delete-or-refresh. FAPD's
  permanent tamper-evident capture archive is incompatible with that
  lifecycle — API-derived data could only ever be a *signal*, never an
  archived source.

## The scraper path (timedtext/InnerTube; youtube-transcript-api, yt-dlp): fails, finally

Verified verbatim: YouTube's ToS forbids access "using any automated
means (such as robots, botnets or scrapers)" except public search
engines per robots.txt or "with YouTube's prior written permission" —
and youtube.com/robots.txt disallows `/api/` (timedtext), `/youtubei/`
(InnerTube), and `/timedtext_video` for all agents. Those are exactly
the endpoints the transcript libraries hit.

**Ethos verdict, no hedge:** the intermediary has said no three times
in writing. That the underlying speech is public-domain does not make
the *path* consented — the transcript file is served by YouTube's
infrastructure under YouTube's rules. Excluded, same category as WAF
bypasses and stealth browsers. A project that cites M-23-22 at agencies
cannot scrape a private platform against its stated terms.

**The written-permission route:** YouTube's Researcher Program is
academic-affiliation-only and grants metadata *quota*, not captions.
No civic/press program exists. Not plannable.

## The Section 508 finding

Section 508 (fetched from section508.gov) requires federal ICT —
explicitly including social-media content — to be accessible: WCAG
1.2.2/1.2.4 captioning for pre-recorded and live media, with agencies
told to upload caption files (SRT) per platform. So agencies are
legally obligated to caption their public videos — but how consistently
official channels carry owner-authored (vs ASR) tracks is unverifiable
without the authorized API. The deeper point: the same 508/transparency
obligations that would make YouTube captions official also guarantee an
off-platform official transcript on .gov — the text we can actually
reach.

**Editorial rule this supports (for any future caption source):**
ASR/auto-generated captions are machine transcription — model-derived
text, never official government prose. Only publisher-authored caption
files (DVIDS SRT/WebVTT — already our solved case — or agency-posted
transcripts) are verbatim-eligible.

## Where the transcripts actually live (thesis confirmed)

| Video class | Authoritative home | Registry status |
|---|---|---|
| White House briefings/remarks | whitehouse.gov briefings + DCPD via govinfo (actively published 2026) | both registered |
| State press briefings | state.gov /department-press-briefings/ (full transcripts) | registered; documented feed to re-probe |
| Congressional hearings | govinfo CHRG (official verbatim; months of lag) + committee sites/congress.gov meetings for near-term materials | CHRG registered; the lag is the one real gap — and YouTube ASR is not an acceptable official-text substitute for it |
| Pentagon | war.gov /News/Transcripts/ (probe with our client) + DVIDS captions (solved) | DVIDS designed |
| Courts | supremecourt.gov argument transcripts (same-day, documented) | registered |
| Agency webcasts | newsroom/transcript pages; YouTube copies mirror events whose text already flows to us | existing classes |

## Bonus find: programmatic official-account verification

The U.S. Digital Registry lives on as **Touchpoints**
(touchpoints.app.cloud.gov/registry; public search UI deprecated, API
alive): `GET /api/v1/digital_service_accounts` at api.gsa.gov —
authenticated with the **same api.data.gov key family FAPD already
holds**. Government-operated, purpose-built, open source: rung-1
verification that a social account is officially federal, prerequisite
for any future social-platform source class (also useful for the open
Flickr question).

## What to build (and not)

1. **GovTranscriptAdapter family — the real deliverable.** Probe and
   register the .gov transcript pages (state.gov briefings feed,
   whitehouse.gov, war.gov transcripts) under existing GUIDE rules;
   transcripts are official text, verbatim-eligible.
2. **Digital Registry verifier** — small shared sync of
   `digital_service_accounts`; rule: no social-platform source is
   registered without appearing there or on the agency's own .gov
   listing.
3. **Deferred: key-only Data API signal client** (uploads-playlist
   metadata as a freshness signal only; hard 30-day lifecycle wholly
   outside the provenance store). Probably not worth building until a
   concrete latency need appears.
4. **Never build:** anything on `captions.download` (owner-only),
   timedtext/InnerTube scraping (fails consent — final), Researcher
   Program (ineligible).

## GUIDE amendments required before any implementation in this class

- §3 **commercial-platform mirrors rule**: platform content only via
  the platform's documented API within its terms (storage lifecycle
  included) or via the content's .gov home; platform ToS fences are
  honored exactly like robots.txt.
- §3 **official-account verification rule** (Digital Registry).
- §7 **signal-class source** definition: term-capped data (YouTube API
  30-day) never enters the permanent provenance store.
- §2 **caption provenance rule**: ASR ≠ official text.
- Registry: record the decision on official YouTube channels —
  metadata-signal at most; transcripts via .gov homes; scraper
  libraries excluded on ethos grounds (resolves the open 2026-07-28
  item).

Degraded links noted: digital.gov registry page is a bare redirect to
Touchpoints; state.gov /press-briefings/ served image bytes to the
research fetcher (use /department-press-briefings/); war.gov
transcripts 403'd the research fetcher — not a verdict for our
identified client.
