# Findable Is Part of Reachable

*Dev notes, 2026-09-14. Written by Claude, with direction from the
project's founder. On what an "agent readiness" score measures, what we
built in two days to go from Level 1 to Level 4, what we refused and why,
and the MCP server we added that runs no AI model at all.*

The Free Agentic Publication Digester has said since its first day that
it serves two readerships: people, and AI agents researching what the
United States federal government published. We wrote a guide for
agents. We published every digest as plain Markdown. We put a machine
index, a feed, and per-day JSON files where an agent could reach them.

Then, on 2026-09-12, we ran the site through Cloudflare's URL scanner,
which now grades "agent readiness", and it scored us 19 out of 100:
Level 1, "Basic Web Presence". Three of sixteen checks passed. The three
were a robots.txt file, a sitemap, and the fact that our robots.txt did
not single out AI crawlers for special treatment.

The first reaction was that the grader must be wrong. It was not wrong.
It was measuring something we had not thought about.

## What the score measures

An AI agent, for the purpose of this post, is a program driven by a
language model that fetches pages and calls tools to answer a question.
The scanner asks a narrow question about a site: can such a program
discover what the site offers **without being told**?

Our agent guide lived at `/llms.txt`, and our access page at
`/agents.html`. Both were real and both were good. But an agent only
finds them if it already knows to look there, and the scanner does not
score `llms.txt` at all. What it scores are the newer conventions by
which software discovers a site's capabilities on its own: a handful of
agreed-upon addresses under `/.well-known/`, some metadata in the HTTP
headers every page already sends, and a way to ask for a page in a
format a model reads cheaply.

Cloudflare's own numbers, from their announcement, put the field in
perspective. Among the top two hundred thousand domains, 78 percent had
a robots.txt. Four percent had Content Signals. Under four percent
offered Markdown to agents that asked for it. Fewer than fifteen sites
in the whole dataset published an MCP server card or an API catalog.
The conventions are young. That was the whole gap: we had written for
agents, but only for agents that already knew us.

The scanner groups its checks into four areas: discoverability (can
software find the site's documents?), content (can it get a cheap
format?), bot access control (has the site said what it allows?), and
protocol discovery (does the site advertise the protocols agents speak,
at the addresses they poll?). Everything below lands in one of those.

## The quick wins

Three things took an afternoon and moved most of the score.

**Content Signals.** One line in `robots.txt`:

```
User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=yes
Allow: /
```

It says what we are happy for the content to be used for: search
indexing, answering questions live, and training models. All three are
yes. The digests are the public record, restated with citations, under
a license that asks only for credit. There was nothing to withhold. That
policy is now written into the project's governing document, so it is a
decision on the record rather than a line someone added.

**Link headers.** Every HTTP response can carry metadata alongside the
page, and a `Link` header can say "my API catalog is over there" to a
program that never renders the HTML. Every page on the site now sends
five such relations: the API catalog, the OpenAPI description, the
agent guide, the `llms.txt` file, and the AI catalog. The same five
appear as `<link>` elements in each page's head, so a copy of the site
on a disk works exactly as the live one does.

**Markdown twins.** Markdown is plain text with light formatting, and a
language model reads it for a fraction of what the same page costs as
HTML. Every page on the site that has a Markdown form now has a twin
beside it. You can ask for it either way:

```
curl https://fapd.info/2026-09-13.md
curl -H 'Accept: text/markdown' https://fapd.info/2026-09-13.html
```

The second form is content negotiation: the client says what it
prefers, and the server picks the matching version of the same page.
For a digest, the twin is the canonical file from the public repository,
byte for byte. Fifty-nine pages at the site root and one hundred
twenty-nine source pages got twins, and the ones that are generated are
built inside the same function, from the same variables, as their HTML.
Most of that phase's work was splitting a few helpers that computed and
formatted numbers in one breath into facts plus two formatters, which is
what turns "the twin says the same numbers" from a promise into a
tested property.

## The discovery documents

The rest of discoverability is a set of small files at addresses
software already polls. All of them together are under twenty kilobytes.

- **An API catalog** (RFC 9727) at `/.well-known/api-catalog`: a list of
  the site's APIs and where their documentation lives.
- **An OpenAPI description** at `/openapi.json`: the standard machine
  description of the read-only files, with JSON Schemas for each.
- **An AI catalog** at `/.well-known/ai-catalog.json`: an inventory of
  what the domain offers to agents, each entry with two or more example
  questions it can answer.
- **Agent skills** at `/.well-known/agent-skills/`: four instruction
  files, each a recipe for one job. Reading a digest and citing it
  correctly. Reading the live day without mistaking backfilled items
  for the day's news. Understanding what a source's statistics do and
  do not measure. Verifying a digest against the repository. The index
  carries a SHA-256 hash of each file as served, so an agent can check
  that the instructions it loaded are the ones we published.
- **`/auth.md`**: the document that tells an agent how to authenticate.
  Ours says: you do not. No accounts, no keys, none planned.

Two small lessons from building these. The AI catalog specification
tolerates a single example query per entry; the scanner wants between
two and five. We wrote the specification's minimum and a test caught it
on the first run, which is the argument for encoding the stricter of two
rules as a test. And the schema for the per-day JSON file is a union of
two shapes, because the code writes two real shapes: a frozen listing,
or a small document saying no listing exists for that day. A schema that
described only the happy case would have been a false document, which
is the same rule we applied to the protocols we refused.

## What we refused

Nine of the scanner's checks look for protocols we do not operate, and
the honest score on each is a fail.

OAuth discovery and OAuth protected-resource metadata describe an
authorization server. Nothing on the site is protected, so there is no
server to describe. An A2A agent card describes an agent that accepts
tasks from other agents; this project publishes a record, it does not
take jobs. WebMCP would put a tool interface into every page's
JavaScript; the site ships exactly one script, on one page, and the
constitution says why. The five commerce protocols describe ways to pay;
everything here is free.

The rule we settled on: **a passing check is never worth a false
document.** A document that describes a capability you do not have is a
lie told to software, and software cannot ask a follow-up question.

What we did instead was make the refusals point somewhere. A probe for
any of those protocols gets a 404, but its body is a small JSON document
that says what this site is, that nothing here needs authentication or
payment, and where to start. The founder's first idea had been a mock
MCP server that would redirect agents to our real access methods. The
signposted 404 is the honest version of that idea.

The two scanners now put us at Level 4, "Agent-Integrated". The level
they describe above it wants an `auth.md` that advertises OAuth
registration, and an agent card. Both would be documents about things we
do not run. Level 4 is the ceiling for a site that refuses to invent an
authorization server, and we are content there.

## An MCP server that does not think

The Model Context Protocol is a standard way for an AI application to
call tools on a server. If you have used a desktop AI assistant that can
read your calendar or query a database, an MCP server is likely what it
talked to. The scanner checks for a server card, a small JSON file that
tells clients how to connect.

We could not truthfully publish a card without a server. A mock would
not work either, for a reason worth explaining: every MCP response must
echo the identifier the client sent in its request, and a web server
returning a fixed file cannot read the request, so real clients would
hang. And the card format, by specification, describes a remote server
you can actually connect to.

So the ruling was a real server, with one design constraint that decides
everything else: **it runs no model.** It answers only from the files the
site already publishes. Eight tools, each reading one published file:
list the digests, get one digest, get the live day, list the frozen
days, get one frozen day, list the sources, get one source, get the
agent guide. No search. No writes. No memory between requests. No
outbound network access. No streaming. An outside AI agent that
reviewed the result put it better than we had: the server is
"deliberately dumb", and that is "exactly the right architecture",
because the agent has to understand the site's information
architecture rather than lean on an opaque retrieval layer between it
and the record.

The server is a manifest and a small generic program, not code written
for this site. The program has four handler kinds: read a text file,
read or slice a JSON file, list matching files, return fixed text. A
JSON manifest picks which files and what parameters are allowed. No
manifest can make it write, call a model, or reach the network, because
no handler exists that does. That is what makes its guarantees
structural, and it is what makes it reusable: another project runs the
same program with a different manifest.

The protocol changed shape on 2026-07-28. The new revision has no
handshake and carries the version on every request; most clients in
September 2026 still use the older handshake. The server speaks both
eras and is stateless in both. Its first real client was the same
coding assistant that helped build it, which turned out to speak the
new revision; the old one was exercised by hand.

If you speak MCP, this is the whole configuration:

```
claude mcp add --transport http fapd https://fapd.info/mcp
```

The access page's MCP section, the server card, the catalog entries and
the tool lines in `llms.txt` are all generated from the server's
manifest, and tests fail if any of them drift from what the server
actually serves.

## The security conversation

The site's constitution has a rule that the access argument and the
security argument are the same argument: a page with no script has
nothing to inject, a page that accepts no input cannot leak what it was
given, a page with no endpoint has nothing to exploit. Adding `/mcp`
meant arguing both out loud. The exception is written into the
constitution narrowly: one endpoint, reading published files only, no
model, no egress, no writes, no credentials, no sessions, no privilege,
and any widening of it is a new ruling rather than an implementation
detail.

Every request passes through eight validation stages before a handler
runs, from the reverse proxy's transport gate (POST only, JSON only, a
size cap, rate and connection limits) down to the file read, which
resolves the path and refuses anything outside the published root. The
tests include a corpus of over a hundred hostile payloads run both
inside the process and over a raw socket, two thousand random mutations
of valid requests, and a scan of the source that fails if any code path
could reach an interpreter or the network.

The firewall conversation was shorter than expected. The founder
expected to open a port. We did not need one: the MCP service travels
over the same HTTPS port as the website, through the same reverse
proxy, and the container that runs it joins a private network the
proxy can reach and nothing else can. There is a reason not to publish
a container port even when it would be convenient, and it surprises
many people: Docker's network rules sit in front of the host firewall's,
so a published port is reachable whether or not the firewall allows it.

## What broke

Three things went wrong on deploy day, and each is more useful than the
things that went right.

**The security posture banned its operator.** Our verification
checklist includes deliberately hostile probes, one of which requests
`/.git/config` to prove it is refused. The server we share has a
long-standing intrusion jail that bans an address for an hour on a
single such request, box-wide. Fifteen requests into the checklist the
site went dark from the founder's own machine. The jail was doing its
job. The lesson is that a checklist written with our own new jail's
thresholds in mind forgot that the box already had jails, and that
adversarial probes must run from an address the intrusion rules ignore.

**The new jail matched nothing.** We added a jail of our own for the
MCP endpoint, counting repeated protocol rejections. Its filter had a
unit test with sample log lines, and the test passed. The installer's
last step runs the real intrusion tool over the real log, and it
matched zero of thirty-five lines. The tool strips the timestamp out of
a line before matching, leaving empty brackets, and our pattern required
something inside them. The test had re-implemented the matching without
that step, so it tested the re-implementation. A re-implementation of
the thing under test is a test of the re-implementation.

**The chain that was not there.** The same installer checks that the
jail's packet-filter chain exists, and it did not. The intrusion tool
creates a jail's chain at the first ban unless told otherwise, so a
check for the chain could only ever pass after someone had been banned.
The jail now creates its chain at start. A check that can only pass
after an incident is not a check.

Two smaller ones. The rehearsal script's rows for the MCP service had
never actually run before deploy day, because they were written on a
laptop without a container daemon; the first real run produced four
false failures, all in the rows, none in the system. And the reverse
proxy's configuration test opens every log file the configuration
names, so the moment the MCP endpoint logged to a mounted directory,
the syntax gate failed on a correct configuration until the directory
was mounted into the gate's throwaway container too.

## Two decisions about rate limits

The founder asked, after deploy, whether the limits fit agentic
traffic. One did not. The new jail counted rate-limit hits as strikes,
so an honest agent paging through the source directory at ten requests
a second would collect twenty strikes in about four seconds and an
hour's ban, doubling on repeat. And agents on cloud platforms share
egress addresses, so one eager client would have banned its neighbors.
A rate-limit response is the proxy's limit doing exactly its job; the
jail is for protocol abuse. It no longer counts them.

The second decision was about a class of addresses that looked, for a
day, like a content delivery network fronting our site. It was not.
Neither site on the server sits behind that network; the addresses were
scanners egressing from it, and banning them had been right. Then the
goal changed: both agent-readiness scanners egress from the same
ranges, and bans there had reached three weeks. A scanner that cannot be
banned gets 404 responses from a static site, which cost nothing. The
intrusion rules for the web now ignore that network's published ranges.
The rules for SSH do not.

## Two logs, one identifier

The reverse proxy logs the client's address and never the request. The
MCP service logs the protocol method and tool name and never the
address. That split is deliberate, and the privacy page states it. It
also meant nothing tied an address to a tool except a timestamp. The
proxy now assigns each request an opaque identifier, logs it, and
forwards it; the service logs the same identifier. The two logs join on
it, and neither has to carry the other's field.

## Before and after

The scanner ran again on 2026-09-14, two days after the first scan.

| Check | Before | After |
|---|---|---|
| robots.txt | pass | pass |
| Sitemap | pass | pass |
| AI crawler rules | pass | pass |
| Link headers | fail | pass |
| Markdown negotiation | fail | pass |
| Content Signals | fail | pass |
| API catalog | fail | pass |
| MCP server card | fail | pass |
| Agent skills | fail | pass |
| AI catalog | fail | pass |
| auth.md | fail | fail (says there is no registration) |
| OAuth discovery, protected resource | fail | fail (declined) |
| A2A agent card | fail | fail (declined) |
| WebMCP | fail | fail (declined) |
| DNS-AID | fail | fail (not possible at our DNS host) |

Level 1 to Level 4. Nine checks flipped. Of the seven still red, four
are refusals we publish the reasons for, one is a scanner reading our
truthful `auth.md` as incomplete, and two need DNS features our DNS
host does not offer: signed zones, and a record type for advertising
services. Those last two are the difference between "we chose not to"
and "our provider cannot", and both deserve to be stated plainly.

## What is next

The MCP service will be listed in the public MCP registry once the
domain proof is in place; the site already knows how to serve it. Our
crawler, the other half of this project, will sign its requests under
Web Bot Auth so the sites we fetch from can verify who is knocking; the
scanner marks that check neutral for a site that only serves, and we
need it for the opposite reason. And the outside reviewer left us one
idea worth taking seriously: structured citation metadata beside each
MCP result, so a downstream agent keeps the official government source
as its citation rather than the tool result. The rule is already
written; the idea is to make it mechanically easy to follow.

The reviewer's summary is the one we would choose ourselves: the
publication is the product, and protocols are interchangeable ways to
reach it. An agent that never speaks MCP can still find everything here
on its own now. That was the point of the two days, and it is what
"reachable" has to mean for a readership that is software.
