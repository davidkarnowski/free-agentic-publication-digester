# The day the backlog ate the day

*Dev notes, 2026-07-31. What the first fully autonomous overnight run
published, what it spent, and the four changes that came out of reading
its own report.*

## What happened

The pipeline ran itself overnight for the first time with nobody
watching. It produced the 2026-07-30 digest, wrote its operations
report, and made the first automated evidence commit to a public
repository. All three of those are firsts, and all three worked.

Then we read the report it wrote about itself, and the day looked worse
the longer we looked.

**17,441,543 input tokens** for the run day. **79.5% of that was
retries.** And the digest those tokens were meant to serve contained no
Congressional Record, no bills, and no public laws — not thin coverage
of them, none of them, an entire branch of government absent from a
Thursday.

## Following the money

Three hundred and one items were collected for 2026-07-30: 159 agency
releases, 126 Federal Register documents, 16 court opinions. Twenty-eight
of them were summarized, and every one of those twenty-eight was an
*official* summary — a Federal Register preamble, quoted verbatim,
costing nothing. **The model produced zero summaries for the digest
day.**

So where did seventeen million tokens go? Into 184 summaries spread
across eleven *other* dates: 2026-07-24, 2026-04-02, 2025-04-11,
2024-06-18. The analyze worker had a queue of every day that had ever
been ingested but not summarized, and it worked that queue faithfully,
newest-first, without any notion that only one of those days would ever
be published.

The missing Congress has the same shape. The govinfo request budget —
2,000 a day — was exhausted before CREC and BILLS were synced. Exhausted
by the same backlog. The finalizer then tried to top up the sync it
needed to publish the day, found the budget gone, and failed. It retried
twelve times, each retry dying at stage one, because a daily budget
cannot be un-exhausted by trying again.

An expensive night that published a thin day, and every piece of it
followed from one unstated assumption: that catching up is free.

## Four changes

**We stopped buying days we will not publish.** FAPD does not issue
post-dated digests. That was always true and nothing in the code knew
it. The analyze layer is now bounded to the current publication day and
the one before it — the day the finalizer freezes just after midnight.
Older items stay pending and get disclosed by the coverage accounting,
which is precisely the machinery for saying "this exists and we did not
summarize it."

**The retry ladder got a ceiling.** This is the number worth carrying
around: on the CLI backend, *every call costs about 29,000 input tokens
regardless of payload*. A one-item retry buys a single ~800-token
summary for the price of a full batch. Three hundred and sixty-six of
them cost 10,860,137 tokens — 62% of the day. Past twelve single retries
per run, an item is now left unsummarized and the log says so. Silence
would have read as completeness.

**The govinfo budget went up, on evidence.** The project's rule is that
budgets are never raised to fix a symptom, and never without the
operator. Both held: the operator authorised it and made it conditional
on the publisher's own limits. So we went and read them. api.data.gov,
the shared GSA service govinfo runs on, documents **1,000 requests per
hour per key** and answers **429** above it. Our logs contain no 429 of
any kind. At 2,000 a day we were averaging **83 requests an hour** —
about 8% of what the key permits. The daily cap is now 6,000, bounded by
a new ceiling of **500 requests an hour**, half the documented
allowance, enforced from the fetch log so it survives restarts. The
ceiling binds the finalizer too, because it is the publisher's limit and
not ours.

One number in that investigation deserves its own sentence: **882 of
4,868 govinfo requests over three days came back 503.** Those count
against our budget, deliberately — a 503 cost the server a request
whatever it returned to us. Roughly a fifth of a day's allowance is
spent on the server's own unavailability before any policy of ours
applies, and the answer to that is fewer requests, never faster retries.

**The finalizer got a reserve.** Collectors now stop at 85% of a daily
budget. The rest belongs to the end-of-day run, and a sync shortfall no
longer aborts it: refusing to publish a day that was collected hours ago
because a top-up could not run is the wrong failure. It cost us a day's
Congress to learn that.

## The part that worked

The report that exposed all of this is the one the pipeline wrote about
itself, unprompted, as its last act of the night. It was built the
previous evening on the theory that a system should hand you the numbers
you would otherwise have to go find. Its first real outing found a
seventeen-million-token misallocation, a missing branch of government,
and a stuck worker.

It was also, fittingly, wrong about itself in one place: its coverage
table read zero summaries on every day, because model events are
journaled without a digest date and it grouped them by one. A feedback
loop under-reporting its own subject is a good reminder that the
instrument needs checking too. Fixed, along with the first automated
evidence commit having been authored as the operator rather than the
bot — the rsynced repository's git config quietly outranking the
container's.

## What we would tell someone building the same thing

A queue with no notion of what will be published will faithfully spend
everything you have on things nobody will read. A backend with a large
fixed per-call cost turns "just retry it individually" from a fallback
into the dominant line item. And the component that publishes needs its
resources protected from the components that merely prepare — otherwise
the last step in the pipeline is the one that starves.

None of that is visible from the code. All of it was visible in one
day's numbers, from a report that took an evening to build.
