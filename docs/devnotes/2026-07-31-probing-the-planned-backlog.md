# Probing the planned backlog: mostly not their fault

*Dev notes, 2026-07-31. Forty-two registered-but-unprobed sources, ninety-two
requests, and a finding that reframes what "planned" has been telling us.*

## The question

Seventy-six of our 127 registered sources sat at `planned` — registered as
in scope, not ingesting. The word carries no information about *why*, and
after a while a large planned list starts to feel like a list of doors
being held shut. So we probed all forty-two of the web-channel entries end
to end: robots, index or feed fetch, parse, and a sample article.

Deliberately from the operator's laptop rather than the server, so the
sweep spent none of the production request budget — the server had already
hit its ceiling once that day and the point was to learn something, not to
compete with the day's collection.

## What came back

| Verdict | Count |
|---|---|
| reachable, no machine-readable feed | 33 |
| HTTP error | 6 |
| working feed with items | 2 |
| working feed, currently empty | 1 |

**Thirty-three of forty-two are reachable and are not refusing us.** They
answer 200, their robots.txt permits us, and they simply do not advertise a
feed. That is the finding worth carrying: for most of the backlog, the
blocker is not an agency withholding anything. It is that we have not built
an HTML-index adapter. The registry has been recording our own unbuilt
capability in the same word it uses for genuine gaps, and a reader — or a
maintainer six months from now — could not tell the two apart from the
status alone. Every one of those thirty-three now carries a dated note
saying so in as many words: *ingestion waits on an adapter, not on the
publisher.*

**Four of the six errors are our own stale URLs**, not refusals. The
Department of the Interior's press page, the Department of Education's, the
Bureau of Labor Statistics' news feed, and ODNI's feed all answer 404 at
the address we registered. Publishers reorganise; our registry did not
notice. Recorded as URL drift with the exact address that failed, which is
the difference between "they blocked us" and "we are knocking on a door
that moved."

**One is a real refusal.** commerce.gov answered 403 to our identified
client, consistent with its 100% no-content rate in the fetch log. Moved to
`unavailable` on that evidence, which is where refusals belong — recorded,
not fought, and never erased by a success elsewhere.

**One is a server-side error.** The FCC's eDocs API returned 504. That is
the server having a bad moment, not a decision about us; it stays planned
with a note to re-probe.

## The two that worked, and why only one was added

`usps-newsroom` is now active. Its feed carries 669 items, 668 of them
dated, newest from four days ago — so the dating rule governs and the
archive tail is backfill, excluded and disclosed rather than passed off as
news. Descriptions average 268 characters, which is teaser length,
comparable to other active sources, and the article links resolve to a
feed-request wrapper that yields no text to our client. So it ingests
feed-only, with the mode disclosed per item, and identity comes from the
link because the feed carries no guids. All of that is in its activation
note, because a source that gives us headlines should be visibly different
from one that gives us documents.

`sba-newsroom` was not added, and the reason is more interesting than the
result. Its feed parses cleanly: ten items, every one dated, every one with
a guid. By every structural measure it passes. But its newest item is dated
2026-04-21 — three months stale — and the article it links to returns 404.
A feed can be well-formed, well-dated, and still be an artifact nobody
maintains. Structure is not freshness, and a viability check that only
measured structure would have activated a source that publishes nothing and
cites broken pages.

`ussc-news` has a clean, reachable, entirely empty feed. Nothing to ingest
yet; noted and left.

## A key that already worked

Separately: api.data.gov's developer manual states that one key "gives you
access to all APIs from agencies participating in api.data.gov's service."
Congress.gov's own documentation points at api.data.gov for key usage. One
request against `api.congress.gov/v3` with the key we already hold returned
200 and real bill data. That unlocks Congress.gov — and the CRS reports
reachable through it — with no new credential.

We did not try the same key against regulations.gov. Its documentation does
not mention api.data.gov, uses a different header, and describes its own
registration. The general statement about participating APIs is not the
same as that publisher telling us our key applies, and the difference is
exactly the sort of thing worth being strict about when the cost of being
wrong is an unauthorised request to a federal system.

## What changed

Active sources 34 → 35. Planned 76 → 70. Unavailable 19 → 20. Ninety-two
requests spent, none of them from the production budget. And thirty-nine
entries that previously said only "planned" now say what is actually in the
way — which, for the large majority, turns out to be us.
