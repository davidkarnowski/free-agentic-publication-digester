# How AI Built This

This project was developed with generative artificial intelligence —
and a project whose editorial code requires every machine-generated
sentence in its digests to be labeled would be in a strange position
hiding its own machine authorship. So here is the plain statement.

## The arrangement

FAPD — the Free Agentic Publication Digester — was designed and written
in collaboration between its human operator and Claude, Anthropic's AI
system, working as coding and research agents. The division of labor: the operator set intent,
constraints, and editorial judgment — what the project is for, what it
must never do, which trade-offs are acceptable — and reviewed, directed,
and sometimes stopped the work. The AI agents wrote code and tests,
probed source documentation, drafted governing documents, and carried
out research sprints across the federal source universe. Every commit in
the repository carries a co-author trailer naming the AI. The full
development narrative — including wrong turns, corrected diagnoses, and
decisions reversed on evidence — is preserved verbatim in the work log
(`WORKLOG.md`), committed to the repository as a timestamped record that
is never retroactively edited.

## Past syntax, toward intent

The working thesis of this collaboration: when generative AI handles the
mechanics of software — the syntax, the language idioms, the boilerplate
of parsers and test harnesses — human attention moves up a level, to the
content and intent of the project itself. The operator's time on this
project went overwhelmingly to questions no programming language
expresses: What makes a selection rule party-blind? What may a summary
claim, and what must it merely attribute? What does a hash actually
prove, and what would be dishonest to imply it proves? How slowly must
you fetch from a server whose robots.txt asks for seven minutes between
requests — and what do you owe a server that asks for nothing?

The result is a codebase where the governing document is longer than
most of the modules, where editorial and ethical rules were written
*before* the code that enforces them, and where the interesting
engineering — the banned-lexicon gate, the coverage arithmetic that must
reconcile before publication, the hash-chained manifests — exists to
serve editorial commitments rather than the other way around. That
inversion is what AI assistance bought.

## Built for agents, built with agents

FAPD publishes for two readerships, and one of them — AI agents
researching government actions — is the same kind of system that helped
build it. That symmetry was used deliberately during development:

- The agent-facing surfaces (`llms.txt`, the machine-readable digest
  index, the stable URLs, the onward-citation ask) were designed by
  asking what the development agents themselves would need to consume
  this data reliably — then building exactly that.
- Research sprints ran as multiple AI agents working documentation-first
  across the federal source universe in parallel, under the same rule
  the pipeline itself obeys: read what the publisher says about access
  before touching their servers.
- The pipeline's own summarization layers are governed by prompts that
  are versioned in this repository like any other code, because the
  development process demonstrated daily that model output is an
  artifact of its instructions — and artifacts of instructions belong
  under version control.

## What this does and doesn't mean

It does not mean the digests are "written by AI" in any loose sense:
selection is mechanical code, most summary text is verbatim official
language, and the four model-written layers are labeled in place,
validated against a banned lexicon, and blocked from publication on any
failure. It does not mean the development was unsupervised: the record
shows the operator redirecting, refusing, and deciding throughout.

It does mean that a small project could afford discipline usually
reserved for large ones — a 300+ case test suite, per-request
accountability logging, tamper-evident provenance, a governing document
that is actually kept current — because the marginal cost of doing
things properly fell far enough to stop cutting corners. We think that
is the honest promise of this way of working, and this page exists so
readers can weigh it with full information.
