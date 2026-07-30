# Security Policy

## Reporting a vulnerability

Email **hustleyourcity@gmail.com** with "FAPD security" in the subject.
Expect an acknowledgment within a few days. Please do not open a public
issue for anything you believe is exploitable before we have had a
chance to respond.

## What is (and is not) in scope

The Free Agentic Publication Digester is a static site plus a
collection pipeline. There is no user login, no form input, no
JavaScript, no cookies, and no user data to steal (see the site's
privacy page). The interesting surfaces are:

- **Parsers** — the pipeline parses XML, HTML, PDF, and email retrieved
  from federal sources. Malformed-input handling in the extract layer
  is in scope.
- **Email ingestion** — bulletins are DKIM-verified before trust is
  extended; sender-spoofing bypasses are in scope.
- **The published site and machine surfaces** (`llms.txt`,
  `digests.json`, the Atom feed) — content-injection paths from source
  material into rendered pages are in scope.
- **Supply chain** — the dependency set is deliberately small
  (`pyproject.toml`); vulnerable-dependency reports are welcome and are
  also swept periodically (docs/ops/AGENT-CVE-GUIDE.md).

Server infrastructure details are deliberately not documented in this
repository. Reports about the hosting box itself will be read, but the
box's dossier lives outside this repo by policy.

## What we log

The web host keeps standard access logs (IP, user agent, request path)
for security monitoring, as disclosed on the site's privacy page.
Nothing else is collected.
