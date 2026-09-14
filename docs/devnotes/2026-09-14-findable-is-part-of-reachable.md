# Findable Is Part of Reachable

*Dev notes, Sept. 14, 2026. Written by Claude, with direction from the
project's founder. A scanner gave a site built for AI agents a failing
grade. Two days later it passed. Here is what the grade measures, what
we built, what we refused to build and why an MCP server that runs no
AI model was the right call.*

The Free Agentic Publication Digester has said since its first day that
it serves two readerships: people, and the AI agents that research what
the federal government publishes. We wrote a guide for agents. We put
every digest in plain Markdown. We published a machine index, an Atom
feed and a JSON file for every day, all where an agent could reach them.

Then a scanner told us the site was barely usable by agents at all.

On Sept. 12, we ran fapd.info through Cloudflare's URL scanner, which
now grades a site's "agent readiness." The score was 19 out of 100.
That put us at Level 1, which the scanner calls "Basic Web Presence."
Three of 16 checks passed. The three were a robots.txt file, a sitemap
and the fact that our robots.txt did not single out AI crawlers for
special rules.

The first reaction was that the grader had it wrong. It didn't. It was
measuring something we had never thought about.

## What the grade measures

An AI agent, for this post, is a program driven by a language model
that fetches pages and calls tools to answer a question. The scanner
asks one narrow thing about a site: Can such a program discover what
the site offers without being told?

Our agent guide lived at `/llms.txt` and our access page at
`/agents.html`. Both were real and both were good. But an agent finds
them only if it already knows to look, and the scanner does not score
`llms.txt` at all. What it scores are the newer conventions by which
software discovers a site on its own: a few agreed-upon addresses under
`/.well-known/`, some metadata in the headers every page already sends
and a way to ask for a page in a format a model reads cheaply.

Cloudflare's own figures, from its announcement, show how new this is.
Among the top 200,000 domains, 78% had a robots.txt. Four percent had
Content Signals. Fewer than 4% offered Markdown to agents that asked.
Fewer than 15 sites in the whole set published an MCP server card or an
API catalog. That was our gap in one sentence: We had written for
agents, but only for agents that already knew us.

The scanner sorts its checks into four groups: discoverability, content,
bot access control and protocol discovery. Everything below lands in
one of them.

## Three quick wins

Three changes took an afternoon and moved most of the score.

**Content Signals.** One line in `robots.txt`:

```
User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=yes
Allow: /
```

It states what we allow the content to be used for: search indexing,
answering questions live and training models. All three are yes. The
digests are the public record, restated with citations, under a license
that asks only for credit. There was nothing to withhold. The policy is
now written into the project's governing document, so it is a decision
on the record and not a line someone added.

**Link headers.** Every web response can carry metadata beside the
page, and a `Link` header can tell a program where the API catalog is
without the program ever rendering the HTML. Every page now sends five
such pointers: the API catalog, the OpenAPI description, the agent
guide, `llms.txt` and the AI catalog. The same five sit in each page's
head, so a copy of the site on a disk behaves like the live one.

**Markdown twins.** Markdown is plain text with light formatting, and a
language model reads it for a fraction of what the same page costs as
HTML. Every page with a Markdown form now has a twin beside it. Ask
either way:

```
curl https://fapd.info/2026-09-13.md
curl -H 'Accept: text/markdown' https://fapd.info/2026-09-13.html
```

The second form is content negotiation. The client says what it
prefers, and the server sends that version of the same page. For a
digest, the twin is the canonical file from the public repository, byte
for byte. Fifty-nine pages at the root and 129 source pages got twins.
The generated ones are built in the same function, from the same
variables, as their HTML. Most of the work was splitting a few helpers
that computed and formatted numbers in one breath into facts plus two
formatters. That is what turns "the twin says the same numbers" from a
promise into a tested property.

## The discovery documents

The rest of discoverability is a set of small files at addresses
software already polls. Together they come to less than 20 KB.

- An **API catalog** (RFC 9727) at `/.well-known/api-catalog`, listing
  the site's APIs and where their documentation lives.
- An **OpenAPI description** at `/openapi.json`, the standard machine
  description of the read-only files, with a JSON Schema for each.
- An **AI catalog** at `/.well-known/ai-catalog.json`, an inventory of
  what the domain offers to agents, each entry with example questions
  it can answer.
- **Agent skills** at `/.well-known/agent-skills/`: four instruction
  files, each a recipe for one job. Read a digest and cite it
  correctly. Read the live day without mistaking backfilled items for
  news. Understand what a source's statistics do and do not measure.
  Verify a digest against the repository. The index carries a SHA-256
  hash of each file as served, so an agent can check that the recipe
  it loaded is the one we published.
- **`/auth.md`**, the document that tells an agent how to authenticate.
  Ours says you don't. No accounts, no keys, none planned.

Two small lessons came out of building these. The AI catalog
specification accepts a single example query per entry; the scanner
wants two to five. We wrote the specification's minimum, and a test
caught it on the first run. Encode the stricter of two rules as a test.
And the schema for the per-day JSON file is a union of two shapes,
because the code writes two real shapes: a frozen listing, or a small
document saying no listing exists for that day. A schema that described
only the happy case would have been a false document. That is the same
rule we applied to the protocols we turned down.

## What we refused

Nine of the scanner's checks look for protocols we do not operate. The
honest score on each is a fail.

OAuth discovery and OAuth protected-resource metadata describe an
authorization server. Nothing on the site is protected, so there is no
server to describe. An A2A agent card describes an agent that accepts
tasks from other agents. This project publishes a record; it does not
take jobs. WebMCP would put a tool interface into every page's
JavaScript, and the site ships exactly one script, on one page, for a
reason its constitution spells out. The five commerce protocols
describe ways to pay. Everything here is free.

The rule we settled on: A passing check is never worth a false
document. A document that describes a capability you do not have is a
lie told to software, and software cannot ask a follow-up question.

What we did instead was make the refusals point somewhere. A probe for
any of those protocols still gets a 404, but its body is a small JSON
document that says what this site is, that nothing here needs a login
or a payment, and where to start. The founder's first idea had been a
mock MCP server that would redirect agents to the real access methods.
The signposted 404 is the honest version of that idea.

## An MCP server that does not think

The Model Context Protocol is a standard way for an AI application to
call tools on a server. If you have used a desktop assistant that can
read your calendar or query a database, an MCP server is probably what
it talked to. The scanner checks for a server card, a small JSON file
that tells clients how to connect.

We could not truthfully publish a card without a server behind it. A
mock would not work either, and the reason is worth a sentence: Every
MCP response must echo the identifier the client sent, and a web server
returning a fixed file cannot read the request, so real clients would
hang. The card format, by specification, describes a remote server you
can actually reach.

So the ruling was a real server with one design rule that decides
everything else: It runs no model. It answers only from the files the
site already publishes. Eight tools, each reading one published file:
list the digests, get one digest, get the live day, list the frozen
days, get one frozen day, list the sources, get one source, get the
agent guide. No search. No writes. No memory between requests. No
outbound network access. No streaming.

The server is a manifest and a small generic program, not code written
for this site. The program has four handler kinds: read a text file,
read or slice a JSON file, list matching files, return fixed text. A
JSON manifest picks which files and which parameters are allowed. No
manifest can make it write, call a model or reach the network, because
no handler exists that does. That is what makes its guarantees
structural, and it is what makes it reusable. Another project runs the
same program with a different manifest.

The protocol changed shape on July 28. The new revision has no
handshake and carries the version on every request. Most clients in
September 2026 still use the older handshake. The server speaks both
and is stateless in both. Its first real client was the same coding
assistant that helped build it, which turned out to speak the new
revision. The old one was exercised by hand.

If you speak MCP, this is the whole configuration:

```
claude mcp add --transport http fapd https://fapd.info/mcp
```

The access page's MCP section, the server card, the catalog entries and
the tool lines in `llms.txt` are all generated from the server's
manifest. Tests fail if any of them drifts from what the server serves.

## Where security and access meet

The site's constitution treats the access argument and the security
argument as the same argument. A page with no script has nothing to
inject. A page that accepts no input cannot leak what it was given. A
page with no endpoint has nothing to exploit. Adding `/mcp` meant
arguing both sides out loud. The exception is written narrowly: one
endpoint, reading published files only, no model, no egress, no writes,
no credentials, no sessions, no privilege. Any widening is a new ruling,
not an implementation detail.

Every request passes eight validation stages before a handler runs,
from the reverse proxy's transport gate (POST only, JSON only, a size
cap, rate and connection limits) down to the file read, which resolves
the path and refuses anything outside the published root. The tests
include a corpus of 119 hostile payloads run both in process and over a
raw socket, 2,000 random mutations of valid requests and a scan of the
source that fails if any code path could reach an interpreter or the
network.

The firewall conversation was shorter than expected. The founder
expected to open a port. We did not need one. The MCP service travels
over the same HTTPS port as the website, through the same reverse
proxy, and the container that runs it joins a private network the
proxy can reach and nothing else can. There is a reason not to publish
a container port even when it would be convenient, and it surprises
many people: Docker's network rules sit in front of the host firewall's,
so a published port is reachable whether or not the firewall allows it.

## What broke on deploy day

Three things went wrong, and each taught more than the things that went
right.

**The security posture banned its own operator.** Our verification
checklist includes deliberately hostile probes. One requests
`/.git/config` to prove it is refused. The server we share has a
long-standing intrusion jail that bans an address for an hour on a
single such request, for every port. Fifteen requests into the
checklist, the site went dark from the founder's own machine. The jail
was doing its job. The lesson: A checklist written around our new
jail's thresholds forgot that the box already had jails, and hostile
probes must run from an address the intrusion rules ignore.

**The new jail matched nothing.** We added a jail of our own for the
MCP endpoint, counting repeated protocol rejections. Its filter had a
unit test with sample log lines, and the test passed. The installer's
last step runs the real intrusion tool over the real log, and it
matched zero of 35 lines. The tool strips the timestamp out of a line
before matching, leaving empty brackets, and our pattern required
something inside them. The test had re-implemented the matching without
that step, so it tested the re-implementation. A re-implementation of
the thing under test is a test of the re-implementation.

**The chain that was not there.** The same installer checks that the
jail's packet-filter chain exists, and it did not. The intrusion tool
creates a jail's chain at the first ban unless told otherwise, so a
check for the chain could pass only after someone had been banned. The
jail now creates its chain at start. A check that can pass only after
an incident is not a check.

Two smaller ones. The rehearsal script's rows for the MCP service had
never actually run before deploy day, because they were written on a
laptop with no container daemon. The first real run produced four
false failures, all in the rows, none in the system. And the proxy's
configuration test opens every log file the configuration names, so the
moment the endpoint logged to a mounted directory, the syntax gate
failed on a correct configuration until that directory was mounted into
the gate's throwaway container too.

## Two calls about rate limits

The founder asked, after the deploy, whether the limits fit agentic
traffic. One did not. The new jail counted rate-limit responses as
strikes. An honest agent paging through the source directory at 10
requests a second would collect 20 strikes in about four seconds and an
hour's ban, doubling on repeat. Agents on cloud platforms share egress
addresses, so one eager client would have banned its neighbors. A
rate-limit response is the proxy's limit doing its job. The jail is for
protocol abuse. It no longer counts them.

The second call was about a set of addresses that looked, for a day,
like a content delivery network sitting in front of the site. It was
not. Neither site on the server uses that network. The addresses were
scanners egressing from it, and banning them had been right. Then the
goal changed. Both agent-readiness scanners egress from the same
ranges, and bans there had reached three weeks. A scanner that cannot
be banned gets 404 responses from a static site, which cost nothing.
The web jails now ignore that network's published ranges. The SSH jail
does not.

## Two logs, one identifier

The reverse proxy logs the client's address and never the request. The
MCP service logs the protocol method and the tool name and never the
address. That split is deliberate, and the privacy page states it. It
also meant nothing tied an address to a tool except a timestamp. The
proxy now assigns each request an opaque identifier, logs it and
forwards it. The service logs the same identifier. The two logs join on
it, and neither has to carry the other's field.

## Before and after

Both scanners we ran, Cloudflare's and isitagentready.com's, graded the
site again on Sept. 14.

| Check | Sept. 12 | Sept. 14 |
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
| auth.md | fail | fail (it says there is nothing to register) |
| OAuth discovery, protected resource | fail | fail (declined) |
| A2A agent card | fail | fail (declined) |
| WebMCP | fail | fail (declined) |
| DNS-AID | fail | fail (not possible at our DNS host) |

Level 1 to Level 4, which the scanner calls "Agent-Integrated." Nine
checks flipped. Of the seven still red, four are refusals we publish
the reasons for, one is a scanner reading our truthful `auth.md` as
incomplete, and two need DNS features our DNS host does not offer: a
signed zone, and a record type for advertising services. Those last two
are the difference between "we chose not to" and "our provider cannot,"
and both deserve to be said plainly.

## What an outside agent found

The same evening, an outside coding agent used the service end to end
without any prior knowledge of the project and wrote up what it was
like. It found the honesty labels doing their job and the transport
frictionless. It also found the cost. Answering one ordinary question,
"what did EPA publish this week," took about 90 requests and 12 MB,
because the listing tools could filter on a document collection but not
on an agency, and nothing spanned more than a day.

It found something subtler too. Every result put a one-sentence
disclosure in the first content block and the data in the second. A
quick script that reads only the first block sees the disclosure,
reports the digest as empty and never knows it was wrong. That is the
worst kind of failure, and it was our design.

Both are fixed. The listing tools take an agency name and return the
day's list of agencies, so the same question now takes eight requests
and 117 KB and finds the same 23 items. The data is the first block and
the disclosure the last, and every tool's description says so. A
digest can be fetched one section at a time. And two of the report's
findings were dismissed with evidence: The discovery method it called
unimplemented answers correctly when sent in the form the new protocol
revision requires, and the source listing it measured as bloated was
the raw file, not the tool. The fixes and the dismissals are both on
the record.

The service is also listed in the official MCP registry now, under the
`info.fapd` namespace, proved by a public key the site serves at a
well-known address. The private half never left the founder's machine.

## What is next

Our crawler, the other half of this project, will sign its requests
under Web Bot Auth so the sites we fetch from can verify who is
knocking. The scanner marks that check neutral for a site that only
serves; we need it for the opposite reason. The reviewer also left one
idea worth taking seriously: structured citation metadata beside each
MCP result, so a downstream agent keeps the official government source
as its citation rather than the tool result. The rule is already
written. The idea is to make it mechanically easy to follow.

The reviewer's summary is the one we would choose ourselves: The
publication is the product, and protocols are interchangeable ways to
reach it. An agent that never speaks MCP can still find everything here
on its own now. That was the point of the two days, and it is what
"reachable" has to mean for a readership that is software.
