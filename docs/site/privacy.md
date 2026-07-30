# Privacy & licensing

The **Free Agentic Publication Digester (FAPD)** publishes a static
website. This page states, for humans and for AI agents alike, exactly
what that means for visitors — and under what terms the content may be
reused.

## What this site does not do

- **No data collection.** No cookies, no analytics, no trackers, no
  fingerprinting, no advertising.
- **No JavaScript.** Pages are static HTML; nothing executes in your
  browser on our behalf.
- **No accounts, no forms.** Nothing here accepts input, so nothing
  stores it.
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
