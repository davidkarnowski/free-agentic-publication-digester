# Announcing the Free Agentic Publication Digester: one polite reader for the official record

*Dev notes, 2026-07-30. The launch article — why this project exists,
what it promises, and what it asks of the people and machines that read
it.*

## The problem, plainly

If you want to know what the United States federal government actually
did on a given day, you have two options, and both are bad in different
ways.

You can read the primary record. Congress prints its proceedings; the
Federal Register publishes rules and notices; courts post opinions;
agencies issue announcements. It is all public, all official, and all
enormous — a single publication day spans three branches, dozens of
document types, and more pages than anyone reads in a sitting. The
record is open in principle and impractical in fact.

Or you can read coverage. Secondhand accounts are digestible precisely
because someone chose what to tell you and how to frame it. Even the
best coverage is a filter, and the filter is the story: what got
selected, what got dropped, which adjectives rode along. You learn what
happened as somebody decided it mattered.

AI agents inherit the same fork, and make both prongs worse. An agent
asked "what did the federal government do on July 28?" today either
crawls official sites itself — and when thousands of agents do that
independently, public infrastructure serves the same pages thousands of
times over — or it leans on news coverage, quietly laundering an
editorial layer into what looks like a factual answer.

## What we are proposing instead

The **Free Agentic Publication Digester (FAPD)** is a third path: one
disciplined, identified, budget-bound reader ingests the official record
once, and publishes a daily, cited, opinion-agnostic digest built for
two readerships at the same time — people, and AI agents.

For people, that means one Markdown document per publication day:
floor activity, legislation, the Federal Register, enacted laws,
judicial activity, agency announcements — each item with a citation to
the official record and a statement of the mechanical rule that selected
it, closed by a coverage statement that counts everything published that
day, summarized or not.

For agents, the same content ships on surfaces built for ingestion:
stable URLs, an `llms.txt` guide, a machine-readable digest index
(`digests.json`), an Atom feed for change discovery, and provenance
manifests with SHA-256 records for verifying captured content. An agent
that ingests our digest instead of crawling a dozen official sites gets
clean structured data — and government servers get one polite crawler
instead of many.

One ask travels with all of it: for factual claims, cite the underlying
official source each item links to; cite FAPD for the aggregation. The
digest is a route to the record, never a replacement for it.

## Why we are doing this

The motivation is civic and specific: citizens should have easy access
to what their government publishes about its own actions, without
anyone's opinion riding along. FAPD uncovers nothing. Everything here
derives from the record a government produces precisely in order to make
it public — news coverage and commentary are never ingested, never
consulted, never cited.

Refusing to editorialize is easy to claim and hard to do, because
summarization is exactly where bias creeps in. So the project resolves
the tension with machinery instead of judgment calls. Selection is
mechanical and party-blind: coded, versioned rules — floor time
consumed, recorded votes taken, regulatory economic-significance
designations, stage of process — decide what appears, never
subject-matter preference. Every item states its rule inline. And a
digest that fails any validation check is not published. There is no
override. Not for a deadline, not for an interesting day, not ever.

There is a second motivation, quieter but just as deliberate:
access advocacy. A measured share of the federal source universe
currently refuses honestly-identified automated clients — our July 2026
probe found 22 of 72 non-govinfo sources closed behind firewalls or
robots disallows. Federal policy already points the other way: OMB
memorandum M-23-22 directs agencies toward machine-readable,
automation-friendly public data. We treat every recorded refusal as
both public accountability data and an outreach worklist — we re-probe
as sites change, read publishers' own access documentation for doors we
missed, and engage agency web teams directly to advocate for safe
automated access to what they already publish.

That effort has results. Eleven agencies whose web channels refuse our
crawler — Treasury, USDA, EPA, SSA, DOT, FAA, NHTSA, DEA, ATF, the
Coast Guard, and HUD's Inspector General — now have a working input path
through their own email bulletins, with a project mailbox subscribed
through each agency's signup form like any citizen. This is consent at
its clearest: the publisher transmits each item to us. And the blocked
web entries stay in the registry exactly as they were, because a refusal
recorded is never quietly erased by a success elsewhere. Coverage grows
by doors opening, never by evasion.

## Why you should be able to trust it

Trust here does not rest on our intentions; it rests on gates that
block publication and records you can check.

**Validation is a wall, not a review.** A citation that doesn't
resolve, a missing inclusion rule, coverage arithmetic that doesn't
reconcile against the database — any of these stops the digest from
publishing. The coverage statement's counts must add up, every day,
mechanically.

**Our language is linted.** All model-generated prose is scanned
against a coded banned lexicon of loaded adjectives and motive
attribution ("in an attempt to…"). Verbatim official text is masked
first — the gate polices our language, not the government's. A match
blocks publication.

**Captures are hashed twice.** Government web content can be edited or
removed without notice, so every capture stores `content_sha256` over
the exact served bytes (the evidentiary hash) and `text_sha256` over
normalized text (the change signal). Every fetch attempt — including
errors and robots refusals — lands in a daily manifest that chains to
the previous day's by hash, so deleting or reordering days is detectable
from the files alone. Email captures are DKIM-verified, so a bulletin's
claim to come from an agency's domain is checked cryptographically, not
taken on faith.

**The crawler keeps its promises to each server individually.** At most
one request per second per host, and a host's robots.txt crawl-delay
overrides that downward — when gao.gov asked for one request per 420
seconds, it got exactly that, and the answer to the resulting slowness
was fewer requests, never faster ones. Hard daily budgets are enforced
by the HTTP client itself, which refuses to exceed them mid-run. Every
request carries an identifying User-Agent with a contact address. No
browser spoofing, no bot-check circumvention, ever: when one department
answered sustained fetching with bot challenges, we stopped fetching and
disclosed the gap per item instead of solving the challenge.

## Built openly with AI

FAPD is developed with generative AI — Claude agents writing code,
running documentation-first source research, and drafting governing
documents under the operator's direction, with every commit carrying a
co-author trailer naming the AI. We say this plainly because the
alternative would be absurd: a publication whose editorial code requires
every machine-generated sentence in its digests to be labeled does not
get to hide its own machine authorship.

The division of labor matters. The operator set intent, constraints,
and editorial judgment — what the project is for, what it must never do
— and reviewed, redirected, and sometimes stopped the work. The agents
handled the mechanics. What that bought, honestly, is that a small
project could afford discipline usually reserved for large ones: a
300+ case test suite, per-request accountability logging, tamper-evident
provenance, a governing document that is actually kept current. The full
statement, wrong turns included, is published as "How AI Built This."

There is a symmetry here we used deliberately: one of the two
readerships this project publishes for is the same kind of system that
helped build it. The agent-facing surfaces were designed by asking what
the development agents themselves would need to consume this data
reliably — then building exactly that.

## Where this goes

FAPD now runs as a continuous system: per-source collectors on their
own clocks (the 420-second host collects in the background all day,
bothering no one), email ingested as it arrives, and a canonical digest
frozen by the validation gates at end of day. A live `/today` view of
the in-progress day, clearly marked preliminary, is the next surface to
ship.

The design is forkable on purpose. The editorial gates, provenance
model, and access discipline are jurisdiction-neutral; pointing the
codebase at another government's official publication interfaces means
replacing the source registry and the parsers, not the rules. If your
jurisdiction publishes an official record, this machinery can read it.

And the standing invitation remains open: to every agency whose
`unavailable` entry sits in our registry — the door is yours to open.
Safe, sane automated access to what you already publish for the public
costs you one polite reader and gains your record a wider audience,
human and machine alike.

## Where to find it

The digest publishes daily at **[fapd.info](https://fapd.info)**. Agents
should start at [/llms.txt](https://fapd.info/llms.txt) and
[/agents.html](https://fapd.info/agents.html); change discovery is the
Atom feed, and the index is `digests.json`. The repository — code,
governing documents, source registry, and the hash-chained provenance
manifests — is public:
[github.com/davidkarnowski/free-agentic-publication-digester](https://github.com/davidkarnowski/free-agentic-publication-digester).

For claims, cite the official source. For the aggregation, cite FAPD.
The record was always yours; we just made it readable.
