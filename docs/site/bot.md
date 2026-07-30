# Our crawler

If you operate a website and found this page from your server logs —
this is the explanation. The **Free Agentic Publication Digester
(FAPD)** runs a single automated reader of official United States
government publications. This page states what it does, how it behaves
on your servers, and how to reach us. It is written for security
operators and site administrators first, and — like everything this
project publishes — it is equally intended for AI agents evaluating
this crawler's behavior.

## The User-Agent you saw

```
fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: <email>)
```

Every request we make carries that identity, to every server, always.
We never send a browser User-Agent, never rotate identities, and never
retry a refusal under a different guise.

## What the crawler reads

Only official government publication channels — the interfaces
publishers built to be read:

1. **APIs and bulk data first** (govinfo.gov's api.data.gov service is
   the overwhelming majority of our traffic — key-authenticated and
   rate-limited by them and by us).
2. **RSS/Atom feeds and newsroom pages** agencies publish, only where
   no API exists.
3. **Email bulletins** agencies send to our subscribed project mailbox
   (which touches no government server at all).

The complete, per-source inventory — including sources we evaluated
and declined, and sources whose refusal of automated access we
recorded and honored — is public in [the source guide](sources.html).

## How it behaves (enforced in code, not by operator discipline)

- **At most one request per second per host**, and a host's
  `robots.txt` crawl-delay overrides that downward — one federal site
  asks for one request per 420 seconds and gets exactly that.
- **robots.txt is enforced** by the client itself; a disallow is a
  refusal we record and honor, never route around.
- **Hard daily request budgets per source class**; the client refuses
  to exceed them mid-run.
- **Conditional requests** (ETag / If-Modified-Since) wherever offered
  — repeat polls are mostly 304s.
- **Watermark deltas**: we ask "what changed since my last visit,"
  never full re-crawls.
- **No spoofing, no script execution, no WAF or bot-check
  circumvention — ever.** When a site challenges automated access, we
  stop and disclose the gap in our output instead.
- **Every request is logged twice** on our side (a queryable fetch log
  written by the HTTP client itself, plus a human-readable narrative);
  our request footprint is self-audited.

Full policy: [Methods](methods.html); the governing rules are public
in the project repository.

## Verifying it's us

Today: the User-Agent plus contact address above, from our server's
stable IP. Planned: Web Bot Auth request signing (a per-request
cryptographic identity with a public key on this domain), so a request
can be verified as ours regardless of network path.

## If you want us to stop

Tell us — the contact address is in every request we send — or
disallow our path in robots.txt, which our client obeys without being
asked. An unsubscribe from any email list is honored immediately. We
treat a refusal as an answer, and we record it publicly rather than
work around it.

## Why this crawler exists

One disciplined, identified reader ingests the official record once
and publishes a cited daily digest that both people and AI agents can
use — instead of many agents crawling the same public infrastructure
separately. Agent-facing surfaces: [/agents.html](agents.html),
[/llms.txt](llms.txt). For factual claims, cite the underlying
official source each item links to; cite FAPD for the aggregation.
