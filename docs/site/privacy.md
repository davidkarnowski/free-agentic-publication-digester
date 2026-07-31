# Privacy & licensing

The **Free Agentic Publication Digester (FAPD)** publishes a static
website. This page states, for humans and for AI agents alike, exactly
what that means for visitors — and under what terms the content may be
reused.

## What this site does not do

- **No data collection.** No cookies, no analytics, no trackers, no
  fingerprinting, no advertising.
- **No tracking scripts.** The digest pages are pure static HTML. The
  live page (`/today.html`) carries exactly one small inline script,
  and all it does is display each timestamp in your local time beside
  the published UTC time. It makes no network request, sets no cookie,
  stores nothing, and reports nothing to us — the computation happens
  in your browser and stays there. With JavaScript disabled the page is
  identical minus the local-time hint.
- **No accounts, no data entry.** The live page's keyword filter is a
  plain HTML form whose state never leaves your browser: it is not
  submitted, not stored, and not readable by us. Nothing on this site
  collects, transmits, or retains anything you type or click.
- **No third-party requests.** Pages load no external fonts, scripts,
  images, or embeds — your visit talks to this server and no one else.

## The one thing that is recorded

Like effectively every hosted service, the web server infrastructure
serving this site keeps **standard access logs** — the requesting IP
address, requested URL, timestamp, response code, and User-Agent — used
solely for security monitoring and abuse prevention (for example,
rate-limiting and intrusion detection), retained briefly under routine
log rotation, and shared with no one. TLS certificates are issued by
Let's Encrypt; certificate issuance is public by design (Certificate
Transparency logs), like every HTTPS site's.

That is the entire data story. There is nothing else to disclose.

## Licensing

- **Digests, site pages, and explanatory documents:**
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse
  freely with credit to "FAPD — Free Agentic Publication Digester."
- **The pipeline code:** Apache-2.0, in the project repository.
- **Quoted official government text** is public domain
  (17 U.S.C. § 105) — it was never ours to license.

The attribution ask mirrors our own citation ethic: for factual
claims, cite the underlying official source each digest item links to;
cite FAPD for the aggregation. Machine-readable reuse notes ride in
[/llms.txt](llms.txt).

## Our own outbound activity

The crawler that gathers this site's source material has its own
transparency page: [Our crawler](bot.html).

## Contact

The project contact address appears in every request our crawler makes
and in the repository metadata.
