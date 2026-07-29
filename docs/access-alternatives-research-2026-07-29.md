# Consent-based access paths for blocked sources — 2026-07-29

Documentation-only research (no probing) into legal, well-known,
ethos-compatible ways to reach the content of the registry's 19
`unavailable` sources. The governing test throughout: **does the
publisher, or a legitimate intermediary, consent to this access path?**
We never take what a server refuses; we find paths where consent exists.

Structural fact: the blocked set splits into **11 WAF-403 sources**
(HHS, HUD, DOT, SSA, CBO, FERC, DEA, ATF, FAA, NHTSA + Commerce-family)
— a security-appliance default, not a considered publisher statement —
and **8 robots-disallowed sources** (Treasury, USDA, EPA, and the six
DVIDS-platform military sites), where the publisher did speak and
alternate paths should lean on channels the publisher affirmatively
operates.

## The policy ground is stronger than expected

**OMB M-23-22** ("Delivering a Digital-First Public Experience", Sept
2023, implementing the 21st Century IDEA; verbatim from the memo):

> "The Federal Government's public web presence is an open book that may
> be crawled, archived, or 'scraped' by anyone in the general public, at
> any time."

> "Agencies must not limit which search engines or crawlers can access
> or archive their public content."

> "**Permit automated web scraping:** Generally, agencies shall permit
> web scraping and archival services to operate unimpeded without
> challenge-response restrictions (e.g., without presenting CAPTCHAs).
> Blocking or throttling of even potentially abusive crawlers is only
> appropriate in exceptional circumstances, such as an active
> denial-of-service attack, and, even then, is appropriate only on a
> temporary basis."

A blanket 403 to an honestly-identified, robots-obeying, 1-req/s crawler
is squarely what this binding guidance tells agencies not to do. The
OPEN Government Data Act (P.L. 115-435; 44 U.S.C. § 3506(b)(6)) adds
statutory spine on open formats and open licenses for public data
assets. GSA's own Site Scanning program crawls every federal site — an
in-government precedent for exactly this activity.

## Methods, ranked

### 1. Email ingestion over GovDelivery (pursue first)

Most cabinet agencies push press output through GovDelivery/Granicus —
the agency's own chosen channel, affirmatively *sending* content to
subscribers. Confirmed live accounts for our blocked set include DEA
(USDOJDEA), FAA (USAFAA), Treasury (USTREAS), SSA (USSSA), plus HHS
Email Updates, HUD's listserv, EPA and USDA-component subscriptions.
One email-ingestion adapter plausibly re-opens the **majority** of the
blocked list.

**Provenance bonus:** GovDelivery mail is DKIM-signed — a stored raw
message with a verifying signature is cryptographic evidence that the
agency's distributor sent exactly these bytes, arguably stronger than a
web capture (archive the DKIM public keys at ingest; they rotate).

Ethos verdict: **perfect consent** — nothing is taken; everything is
given. Steps: GUIDE amendment for the email-adapter class (mailbox
identity, DKIM verify-and-archive rule, teaser-vs-full-text posture);
project mailbox under the public identity; subscribe USTREAS, USSSA,
USDOJDEA, USAFAA, HHS first; run the FDIC `USFDIC_26/feed.rss` probe to
settle whether GovDelivery topic RSS lets some agencies skip email.
Risks: bulletins may be teasers linking to the blocked site (ingest
what's offered; never force the link); mailbox hygiene.

### 2. Formal engagement citing M-23-22 (pursue second)

One respectful template letter to each WAF-blocked agency's digital
team: identify the project, describe its conduct (1 req/s, robots-
obeying, fully logged), quote M-23-22's crawler language, and ask for
any of a feed, an API, or an allowlist entry — offering Friendly-Bots
or Web-Bot-Auth verification as zero-trust options for them. CC GSA/TTS
Digital.gov (authors of the crawler-friendly guidance). Record every
outcome, including silence, in registry notes. Honest gap: no precedent
found of an agency publicly allowlisting a small civic crawler — expect
slow or no replies; even refusals become accountability data.

### 3. Verified-crawler identity: Web Bot Auth + vendor programs

The IETF now has a chartered **webbotauth Working Group** (specs to
IESG April/August 2026): bots sign each request with HTTP Message
Signatures (RFC 9421, Ed25519), publishing the key at
`/.well-known/http-message-signatures-directory` on the bot's own
domain. Cloudflare verifies these today and fast-tracks signed bots in
its Verified Bots directory; Akamai, AWS WAF, and Vercel support the
scheme. Cloudflare's **Friendly Bots** program lets an individual
site owner (i.e., an agency) allowlist a named small crawler in a few
clicks without global verification.

Ethos verdict: **maximal alignment** — identifying *more* strongly,
with passage granted by the site's own security layer under the owner's
configuration; verified status never forces passage, and residual
refusals are still honored. Steps: keypair + signed JWKS on the FAPD
site, signing middleware (three headers) in the HTTP client, Cloudflare
dashboard submission, reference the setup in every Method-2 letter.
Risks: pre-RFC drift; global verification may fail the
"serves the broader Internet" bar (Friendly-Bots per-site allowlisting
is the realistic near-term win); verification ≠ unblocked.

### Interim and niche paths

- **Wayback Machine as a read path**: reading pre-existing CDX-
  discovered captures of blocked pages is consuming a legitimate
  intermediary's lawful public service (IA has archived .gov/.mil
  ignoring robots since 2016, with the government as an End-of-Term
  archiving partner). **Bright line adopted: never use Save Page Now as
  an on-demand proxy to fetch a page whose origin just refused us** —
  that is evasion-by-intermediary. Pre-existing captures only, labeled
  archive-sourced with capture timestamps; freshness per newsroom
  unverified.
- **Federal Register** (already active) carries every *regulatory*
  action of the blocked agencies — the legally significant slice
  already flows to us through GPO.
- **DVIDS API** (already Tier A): the answer for all six military-
  service blocks — the publisher's purpose-built machine channel.
- **Common Crawl / End-of-Term / LoC archives**: ethos-compatible,
  useless for daily freshness (monthly/quadrennial); backfill only.
- **Official YouTube channels**: consent-clean but content-mismatched;
  needs a GUIDE decision before any use. **X API**: practically
  excluded (paid, restrictive).
- **FOIA: wrong tool** — it compels records not already public; press
  releases are affirmatively published. Procedurally legal,
  substantively silly; niche backfill at most.

### Excluded on ethos grounds (regardless of legality)

Residential proxies, UA rotation/browser impersonation, stealth
headless browsers, CAPTCHA solvers, commercial "unblocker" APIs: each
works by defeating a refusal — making the request look like something
it isn't so a server that said no says yes by mistake. A bypassed WAF
is the opposite of consent; using these would forfeit the registry's
accountability meaning and our standing to cite M-23-22 at agencies.

## Source-by-source best paths

| Blocked source | Best path | Second |
|---|---|---|
| treasury-newsroom | GovDelivery (USTREAS) | M-23-22 letter |
| agriculture-newsroom | Re-probe documented RSS page | GovDelivery components |
| hhs-newsroom | HHS Email Updates | M-23-22 letter; Web Bot Auth |
| hud-newsroom | Press listserv | Federal Register; letter |
| transportation-newsroom | GovDelivery (DOT family) | Letter; Web Bot Auth |
| epa-newsroom | GovDelivery | Federal Register |
| ssa-newsroom | GovDelivery (USSSA) | OIG RSS + oversight.gov |
| cbo-publications | CBO email alerts + US-CBO GitHub | congress.gov cost estimates |
| ferc-news | eCollection filings RSS | FERC email |
| dea-press | GovDelivery (USDOJDEA, confirmed) | DOJ division feeds |
| atf-news | DOJ-family feeds/GovDelivery | Letter |
| faa-newsroom | GovDelivery (USAFAA, confirmed) | Federal Register |
| nhtsa-press | Recalls API + Federal Register | DOT GovDelivery |
| uscg + 5 military services | **DVIDS API** | Service GovDelivery |

## Honest uncertainties

Which WAF vendor fronts each agency (unprobed); Cloudflare global
verification odds for a single-project crawler; per-GovDelivery-account
topic coverage vs. full newsroom output; Wayback capture freshness per
source; Akamai known-bot inclusion has no self-serve route.
