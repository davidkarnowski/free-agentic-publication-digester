<!-- Markdown twin of https://fapd.info/sources/education-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/education-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: education-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Education Press Releases

planned · Executive · Tier 1 · HTML index · Department of Education

Official site: https://www.ed.gov/about/news · All sources: [sources.md](../sources.md)

## What this source is

The Department of Education administers federal student aid and elementary, secondary, and higher-education programs. Its press-release index carries departmental announcements on grants, regulations, and enforcement, typically several items per week.

**Model-written orientation**

The Department of Education publishes press releases on federal education programs, student financial aid policy, and education regulations.

The Department of Education is the federal executive agency responsible for administering federal education programs and policy, including federal student financial aid, K-12 education programs, higher education oversight, education research, and special education. The department works with state education agencies and local school districts, as well as colleges and universities, to implement federal education law and administer federal funding for education. It also enforces federal civil rights law in education and administers the student loan program.

Through its press office, the Department of Education publishes official announcements on departmental policies, enforcement actions, program changes, and major initiatives affecting K-12 education, higher education, and student financial aid. Readers will find press releases covering topics such as changes to federal student aid programs and application processes, announcements of federal education grants to schools and universities, enforcement actions related to education law or civil rights protections in education, final regulations affecting schools or institutions of higher education, leadership statements and appointments, major departmental initiatives addressing educational access or achievement, program results and evaluations, and policy responses to education-related issues.

Education Department releases typically include information on affected populations, implementation timelines, funding amounts where applicable, and statements from departmental leadership. The releases serve as official notification to state education agencies, local school districts, higher education institutions, educators, families, and the public of federal education policy decisions and program changes. Individual offices within the Department of Education—such as the Office of Federal Student Aid or the Office for Civil Rights—may maintain specialized communication channels for their specific program areas, but the departmental press office publishes releases reflecting policies affecting education broadly. This source is currently being evaluated for regular ingestion.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `education-newsroom` |
| Agency / parent organization | Department of Education |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.ed.gov/about/news |
| URL (index) | https://www.ed.gov/about/news/press-release |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 404 at registered URL — path likely wrong or moved; correct URL and re-probe before concluding availability. Candidate correction: the pre-redesign /news/press-releases path. URL recovered 2026-07-31 (operator machine, off the server budget): the path is singular — /about/news/press-release, not /press-releases. It answers HTTP 200, robots permitting, with a dated index (three items on 2026-07-29/30). No RSS or Atom feed anywhere on the page and none autodiscovered, so there is nothing machine-readable to poll; left planned, awaiting the html-index adapter. Worth noting for a separate email entry: the page offers a GovDelivery subscription (public.govdelivery.com/accounts/USDE/signup/49108), which is the consent-maximal channel we already ingest for other departments. Re-probe through scripts/check_sources.py, 2026-07-31: verdict html-only — HTTP 200, 98 KB, 7,623 characters of extracted index text. ed.gov serves no robots.txt (HTTP 404), so nothing is disallowed. Probed 2026-07-31: registered URL returned 404 (https://www.ed.gov/about/news/press-releases) — the publisher moved or retired it; not a refusal. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the press-release HTML index daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.ed.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.
