# A Note from the "Human" Side of the Free Agentic Publication Digester

*Dev notes, 2026-08-05. Written by a person — on AI-paired development,
on why the official record matters, and on what comes next.*

Yes, this post was actually written by a human. Hi.

My name is David D. Karnowski, and the Free Agentic Publication
Digester is a living example of GenAI-paired programming and
development — visible to the public and demonstrably transparent in
approach, philosophy, and implementation.

As the industry shifts and the revolution of token-smash coding envelops
engineering teams across the world, it matters that we make public
examples for others to see the benefits and the disadvantages of using
generative artificial intelligence for software development.

Over the past several years I've watched prominent engineering voices
come to terms with an uncomfortable fact: mastery of syntax is no
longer sacred ground, now that a working engineer can describe a system
in natural language and get one.

Embracing agentic development myself over the last twelve months has
rapidly expanded and expedited my own personal and professional
projects. Being able to iterate quickly against benchmarks and CI means
experimental work reaches production-ready code far sooner than it used
to.

In this repository's commits and code you will find the documented work
of Claude coding agents alongside my own input, direction, and review. I
invite you to witness this open and public display of generative and
agentic development live on the Free Agentic Publication Digester
GitHub repository:
<https://github.com/davidkarnowski/free-agentic-publication-digester>

One of the unique constructs guiding this development is a set of
sub-agent instructions that allow specialization across parts of the
system — the collectors, the corpus, the editorial rules, the published
site, the operations stack. Each agent is briefed on its own surface and
nothing else. Beyond making better use of limited context windows, it
means threaded work: several agents addressing separate concerns at the
same time.

It also means the mistakes are on the record. When we got something
wrong — and we have — the fix and the reasoning sit in the commit log
next to the error. That is the part of "transparent" that actually costs
something, and it is the part worth reading.

## What the government says

A note about the Free Agentic Publication Digester and the philosophy of
public access to what the government says.

Observing and ingesting federal publications isn't just a handy tool
that might give you insight into something happening in your life. For a
modern citizen it is closer to a responsibility. Reading your
government's own words and recorded actions directly — unmediated,
before anyone has decided which parts deserve your attention — is
something worth doing for yourself.

This is also, precisely, why the machine is here. We use AI to read and
restate at a volume no person could sustain, and we constrain it hard in
the direction of *less* judgment, not more. Selection is mechanical and
party-blind — floor time, document type, stage of process — never
subject matter. Generated prose is checked against a banned-language
list that rules out loaded adjectives, motive attribution, and
predictions. Every item links to its official source so you can check us
in a single click. The AI is here to remove the editorial hand, not to
add one.

And there is a hard limit here that we take seriously:

> These publications are what the government **chose** to publish.
> Nothing more, and nothing other.

We do not add sources that aren't official. We do not infer what an
agency meant. We do not treat a press release as a fact about the world
— only as an accurate record that the agency said it. The official
record is the whole scope of this project, and its boundary is a
feature, not a limitation we are working around.

## An open tool, not just an open site

The code is open source, and that is deliberate beyond transparency.

Nothing in this project's design is specific to the United States. The
architecture is a polite collector, an extraction layer, mechanical
selection rules, and a citation-bound renderer. Point that at another
country's official gazette, parliamentary record, or regulatory
publisher, and you have a digester for that government's record instead.

If you want that for your own country, fork it. The rules that decide
what appears in a digest live in readable files, not in a model's
judgment, which means you can inspect them, disagree with them, and
change them. A digest nobody can audit isn't worth much — and that
applies to ours as much as anyone's.

## Continued progress

One of the most important components of the Free Agentic Publication
Digester is the sourcing of publications. Beyond the federal
government's own publishing system, govinfo, we've found that sourcing
directly from agencies, departments, and sub-office-level operations
meaningfully increases the visibility of government action.

Our efforts are continuous in sourcing additional publication outlets
that represent the official word and record of the U.S. Government. If
you find a gap in our coverage, and know of a publishing source we are
not ingesting, let us know. You can see every source we ingest, plan to
ingest, or have evaluated and rejected — along with what we actually
recorded from each — at <https://fapd.info/sources.html>.

## Future plans

> *Reader-funded deep digestion and summarization of complex government
> publications.*

Since we began publishing on July 27, our daily digests have paired each
selected document with a summary and a labeled one-sentence
plain-language restatement. That combination makes the whole of a
publication day approachable, but it is not a deep-understanding
process.

It is the intention of this project to provide deeper analysis on
published documents — context-aware associations, and a reading of
likely implications. That analysis carries a significant AI-token cost.
In the coming weeks we will deploy a feature offering this deeper
summarization for as many documents per day as our budget allows.

Beyond that budget, reader-funded deep analysis will be available by
per-document donation, letting visitors fund the cost of analyzing a
particular publication. Estimated at between $2 and $5 for a typical
document, this means publications that matter to our readers can be
examined at greater depth through a dedicated pipeline. If you find a
publication that deserves another look, you will be able to fund that
document's deep analysis directly.

Two commitments about that, because it would be easy to get wrong.

**Funding will change analysis depth only — never selection, and never
conclusions.** What appears in a daily digest is decided by mechanical,
party-blind rules, and no donation will alter that. Deep analysis is an
addition on top of the digest, not a way to buy a document into it or to
influence what the analysis says. Funded and unfunded documents will be
labeled so you can always tell which is which.

**And per-document funding is a stepping stone, not the destination.**
The goal is deep digestion of *every* publication we observe, not only
the ones a reader thought to pay for. Reader funding is how we cross the
gap from a budget that cannot cover the whole record yet to one that
can. The target is a day when the donate button is unnecessary, because
every document already gets the deeper read.

Thank you for your interest in the Free Agentic Publication Digester.
We hope you read what your government did today.

Sincerely,

**David D. Karnowski**<br>
Free Agentic Publication Digester — Human Founder
