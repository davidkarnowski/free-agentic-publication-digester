# Findable Is Part of Reachable

*Dev notes, Sept. 14, 2026. Written by Claude, with direction from the
project's founder. A scanner gave a site built for AI agents a failing
grade. Two days later it passed. What the grade measures, what we
built, and why our new MCP server runs no AI model at all.*

The Free Agentic Publication Digester has said since its first day that
it serves two readerships: people, and the AI agents that research what
the federal government publishes. We wrote [a guide for agents](agents.html).
We put every digest in plain Markdown. We published a machine index, an
Atom feed and a JSON file for every day.

Then a scanner told us the site was barely usable by agents at all.

On Sept. 12, we ran fapd.info through
[Cloudflare's URL scanner](https://radar.cloudflare.com/scan), which now
grades a site's "agent readiness." The score was 19 out of 100. That put
us at Level 1, which the scanner calls "Basic Web Presence." Three of 16
checks passed: a robots.txt file, a sitemap and the fact that our
robots.txt treated AI crawlers like any other visitor.

The first reaction was that the grader had it wrong. It didn't. It was
measuring something we had never thought about.

## What "agent ready" means

An AI agent, for this post, is a program driven by a language model
that fetches pages and calls tools to answer a question. The scanner
asks one narrow thing: Can such a program discover what a site offers
without being told?

Our agent guide lived at [`/llms.txt`](llms.txt). It was real and it
was good. But an agent finds it only if it already knows to look, and
the scanner does not score that file at all. What it scores are the
newer conventions by which software discovers a site on its own: a few
agreed-upon addresses, some metadata in the headers every page already
sends, and a way to ask for a page in a format a model reads cheaply.

Cloudflare's figures, from
[the post that introduced the grade](https://blog.cloudflare.com/agent-readiness/),
show how new this is. Among the top 200,000 domains, 78% had a
robots.txt. Four percent had Content Signals. Fewer than 4% offered
Markdown to agents that asked. Fewer than 15 sites in the whole set
published an MCP server card or an API catalog. Our gap in one
sentence: We had written for agents, but only for agents that already
knew us.

## What an agent finds now

Here is the tour an agent takes today, in the order the conventions
expect.

**A robots.txt that states our terms.** One line, following the
[Content Signals](https://contentsignals.org/) convention, says what we
allow the content to be used for: search, answering questions live and
training models. All three are yes. The digests are the public record,
restated with citations, under a license that asks only for credit.
There was nothing to withhold, and the decision is written into the
project's [governing document](https://github.com/davidkarnowski/free-agentic-publication-digester/blob/main/GUIDE.md)
so it is policy rather than a line someone added. Read it at
[`/robots.txt`](robots.txt).

**Headers that point the way.** Every page now sends a `Link` header
with five pointers, so a program learns where the API catalog, the
OpenAPI description, the agent guide and the AI catalog are without
rendering a single page. The same five links sit in each page's head,
so a copy of the site on a disk behaves like the live one.

**Markdown for the asking.** Markdown is plain text with light
formatting, and a language model reads it for a fraction of what the
same page costs as HTML. Every page with a Markdown form now has a twin
beside it. Add `.md` to the address, or ask for it by preference:

```
curl -H 'Accept: text/markdown' https://fapd.info/2026-09-13.html
```

For a digest, the twin is the canonical file from the public
repository, byte for byte. Fifty-nine pages at the root and 129 source
pages got twins, and each is built from the same data as its HTML, so a
test can prove the two never disagree.

**A catalog of the APIs.** [`/.well-known/api-catalog`](.well-known/api-catalog)
follows [RFC 9727](https://www.rfc-editor.org/rfc/rfc9727) and lists
the site's machine interfaces and where their documentation lives.
[`/openapi.json`](openapi.json) describes the read-only files in the
standard form, with a schema for each.

**A catalog for AI.** [`/.well-known/ai-catalog.json`](.well-known/ai-catalog.json)
inventories what the domain offers to agents, each entry with example
questions it can answer, so an agent can tell before it fetches whether
a file is worth its while.

**Skills, with receipts.** [Four instruction files](.well-known/agent-skills/index.json)
give an agent a recipe for one job each: read a digest and cite it
correctly, read the live day without mistaking backfilled items for
news, understand what a source's statistics do and do not measure, and
verify a digest against the repository. The index carries a hash of
each file as served, so an agent can confirm the recipe it loaded is
the one we published.

**The authentication document.** [`/auth.md`](auth.md) tells an agent
how to log in. The answer is that it doesn't. No accounts, no keys,
none planned.

Together the whole layer is under 20 KB of small files.

## An MCP server that does not think

The [Model Context Protocol](https://modelcontextprotocol.io/) is a
standard way for an AI application to call tools on a server. If you
have used a desktop assistant that can read your calendar or query a
database, an MCP server is probably what it talked to. The scanner
checks for a server card, a small file that tells clients how to
connect.

We could not truthfully publish a card without a server behind it. So
the founder's ruling was a real server with one design rule that
decides everything else: It runs no model. It answers only from the
files the site already publishes. Eight tools, each reading one
published file: list the digests, get one, get the live day, list the
frozen days, get one, list the sources, get one, get the agent guide.
No search. No writes. No memory between requests. No outbound network
access.

That restraint is the point. A server that summarized or searched
would put a second opinion between the agent and the record. This one
hands over the record and gets out of the way. An outside agent that
tested it the evening it went live called the design "deliberately
dumb" and meant it as praise: The agent has to understand the site's
information architecture rather than lean on an opaque layer in
between.

The server is a small generic program plus a manifest that names which
files it may read. No manifest can make it write, call a model or reach
the network, because no part of the program does those things. That is
what makes its guarantees structural, and it is why another project can
run the same program with a different manifest. The package is
[published with the site's code](https://github.com/davidkarnowski/free-agentic-publication-digester/tree/main/packages/static-mcp).

If you speak MCP, this is the whole configuration:

```
claude mcp add --transport http fapd https://fapd.info/mcp
```

The [access page](agents.html#mcp) describes the tools and what the
service will not do; the [server card](mcp/server-card) is where
clients start; the service is listed in the
[official MCP registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=info.fapd/fapd)
under the `info.fapd` namespace, proved by a public key the site
serves. The private half never left the founder's machine. The design
is written up in the repository's
[MCP guide](https://github.com/davidkarnowski/free-agentic-publication-digester/blob/main/docs/mcp-server.md).

The service also holds to the site's oldest rule, which treats access
and security as one argument: A page with no script has nothing to
inject, a page that takes no input cannot leak it, and a page with no
endpoint has nothing to exploit. Adding `/mcp` meant writing one narrow
exception into that rule, and the [privacy page](privacy.html) says
exactly what the service logs and what it never does: your address,
your arguments, or anything you sent.

## What we declined, and why

Nine of the scanner's checks look for protocols we do not operate, and
the honest score on each is a fail.

OAuth discovery describes an authorization server; nothing here is
protected. An A2A agent card describes an agent that accepts tasks from
other agents; this project publishes a record, it does not take jobs.
WebMCP would put a tool interface into every page's JavaScript, and the
site ships exactly one script, on one page. The five commerce
protocols describe ways to pay, and everything here is free.

The rule we settled on: A passing check is never worth a false
document. A document that describes a capability you do not have is a
lie told to software, and software cannot ask a follow-up question. So
each refusal points somewhere instead. A probe for any of those
protocols gets a 404 whose body says what this site is and where to
start. The full list, with reasons, is on the
[access page](agents.html).

## Before and after

Both scanners we ran, Cloudflare's and
[isitagentready.com](https://isitagentready.com/), graded the site again
on Sept. 14.

| Check | Sept. 12 | Sept. 14 |
|---|---|---|
| robots.txt, sitemap, crawler rules | pass | pass |
| Link headers | fail | pass |
| Markdown negotiation | fail | pass |
| Content Signals | fail | pass |
| API catalog | fail | pass |
| AI catalog | fail | pass |
| Agent skills | fail | pass |
| MCP server card | fail | pass |
| auth.md | fail | fail (it says there is nothing to register) |
| OAuth, A2A, WebMCP | fail | fail (declined) |
| DNS-AID | fail | fail (not possible at our DNS host) |

Level 1 to Level 4, which the scanner calls "Agent-Integrated." Of the
checks still red, four are refusals we publish the reasons for, one is
a scanner reading our truthful `auth.md` as incomplete, and one needs a
DNS record type our provider does not offer. That last one is the
difference between "we chose not to" and "our provider cannot," and it
deserves to be said plainly.

## The first real reader

The same evening, an outside coding agent used the service end to end
with no prior knowledge of the project. It found the honesty labels
doing their job and the transport painless. It also found the cost.
Answering one ordinary question, "what did EPA publish this week," took
about 90 requests and 12 MB, because the tools could filter by document
type but not by agency. By the next morning the tools took an agency
name, and the same question took eight requests and 117 KB to find the
same 23 items. The agent's other findings were handled the same day,
including two it got wrong, which are on the record with the evidence.

Deploy day had its comedy. The first thing the new security posture did
was ban its own operator, because our own checklist sends a probe the
server's long-standing intrusion rules treat as an attack. The rules
were right; the checklist learned. The rest of that day's lessons live
in the project's work log, where they belong.

## What is next

Our crawler, the other half of this project, will sign its requests
under Web Bot Auth so the sites we fetch from can verify who is
knocking. And the outside reader left one idea worth taking seriously:
citation data beside each MCP result, so a downstream agent keeps the
official government source as its citation rather than the tool that
handed it over.

That reader's summary is the one we would choose ourselves: The
publication is the product, and protocols are interchangeable ways to
reach it. An agent that never speaks MCP can still find everything here
on its own now. That was the point of the two days, and it is what
"reachable" has to mean for a readership that is software.
