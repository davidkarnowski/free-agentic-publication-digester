# Email-Distributed Sources: the Subscription Adapter Guide

*How FAPD ingests official publications that agencies push by email —
and how to do the same for your own government's bulletin services.
Governing rules: GUIDE §3 "Email-distributed sources" and §7 (DKIM
corroboration), adopted 2026-07-29. Status: the source class is
codified and this guide is normative for it; the adapter implementation
follows the design here.*

## 1. Why email is a legitimate source class — arguably the most legitimate

Every other access method in this project asks a server for content.
Email inverts that: **the publisher transmits the content to us, over a
distribution channel the publisher chose, to an address that subscribed
through the publisher's own signup flow.** Nothing is requested from a
newsroom server, nothing is crawled, nothing can be refused-then-taken.
On the project's consent test — *does the publisher consent to this
access path?* — subscription email is the only channel where the
publisher's consent is expressed by affirmatively sending every single
item.

This matters most for sources whose *web* channels refuse
honestly-identified automated clients. In the US federal universe, most
cabinet agencies distribute their press output through
GovDelivery/Granicus bulletins or agency-run listservs even where their
newsrooms sit behind WAFs. The email channel is not a workaround of
that refusal — it is a different door the same publisher holds open on
purpose. (The refusal still stands where it was given: see §6.)

The class is jurisdiction-neutral. Nearly every government operates
some bulletin service — GovDelivery across US federal/state agencies,
gov.uk's email alert system, the EU's press-subscription services,
municipal newsletter platforms. A fork of this project for another
jurisdiction will likely find email is the *first* door worth opening,
not the last.

## 2. The consent architecture, in five rules

1. **Subscribe as ourselves, like any citizen.** One dedicated project
   mailbox, held under the project's public identity, subscribes
   through each publisher's own signup flow. No aliases per source, no
   disguises, nothing a list administrator would be surprised by.
2. **Consent is revocable — in both directions.** If a publisher
   removes the address, blocks the subscription, or asks us to stop, we
   stop, and the event is recorded in the registry notes with the same
   standing a robots.txt disallow gets. We likewise unsubscribe cleanly
   if a source is retired.
3. **Receiving an email is not consent to crawl.** Bulletins often
   contain teaser text linking to the very newsroom page that refuses
   our client. We ingest what the bulletin itself carries and never
   fetch a link whose host blocks us. The email channel's consent is
   exactly as wide as the email.
4. **The mailbox is infrastructure, not identity theater.** Its
   credentials live in `.env` (git-ignored) like every other secret;
   the address itself may be published (it identifies us to list
   administrators the way our User-Agent identifies us to servers).
5. **Disclosure is unchanged.** Everything in the digest sourced from
   email is attributed speech (§2), carries a disclosed ingestion mode,
   and is dated by the agency's own claim — never by our receipt time
   masquerading as news.

## 3. Setting up the project mailbox

- **A dedicated address under the public attribution identity** — not a
  personal inbox, not a shared alias. One mailbox for all
  subscriptions, so provenance, polling, and backup live in one place.
- **Pick a provider with plain IMAP app-password access.** The adapter
  polls IMAP; OAuth-only IMAP (common on consumer accounts) complicates
  unattended runs. Providers with straightforward app tokens work best;
  Gmail works with two-factor + an app password.
- **Turn spam filtering down or off for known list senders** (or add
  the bulletin domains to an allowlist). A silently spam-foldered
  bulletin is a coverage gap the coverage statement can't see. The
  adapter should poll all folders or the provider should be configured
  to deliver list mail to the inbox.
- **`.env` keys**: `IMAP_HOST`, `IMAP_USER`, `IMAP_PASSWORD` (or a
  provider token). Never committed; the committed `.env.example`
  carries blank placeholders.
- **Back up the raw store.** Captured raw messages are the evidentiary
  record (§5); they live in the content-addressed capture store like
  web captures and inherit its durability plan. The mailbox itself is a
  convenience buffer, not the archive — once a message is captured and
  recorded, mailbox retention is an operational choice.

## 4. Subscribing (a one-time manual pass, by design)

Subscription is a **manual, per-publisher web flow** — and that is the
correct posture, not a limitation. Automated form submission would add
nothing, could trip anti-abuse checks (some forms carry CAPTCHAs, which
we never automate against), and would blur the "like any citizen"
story. The work is small: a handful of minutes per source, once.

Per source:

1. Find the publisher's own signup page (US federal GovDelivery:
   `public.govdelivery.com/accounts/<CODE>/subscriber/new`, or the
   form embedded on the agency's site; listservs: a subscribe command
   emailed to the list server).
2. Subscribe the project mailbox, **selecting topics deliberately** —
   the topic selection *is* the content evaluation (gate 3): a
   press-release topic subscription rarely equals the agency's full
   newsroom output, and the gap must be known and disclosed.
3. Complete the confirmation click when it arrives.
4. **Record in the registry entry's notes**: signup URL, date, exact
   topics chosen, and the observed coverage relationship to the
   agency's visible output ("press releases topic only; speeches and
   testimony not carried").

## 5. How ingestion works

- **Polling.** The adapter polls the project mailbox a few times a day.
  This costs government servers nothing; §4's request budgets don't
  apply — but polling is still paced, logged in the daily access
  narrative, and every processed message lands as an attempt record in
  the committed daily manifest. Absence remains an assertion.
- **The raw message is the capture.** The complete RFC-5322 message
  bytes (headers included) are stored content-addressed, exactly like a
  web capture: `content_sha256` over the raw bytes is the evidentiary
  hash; normalized extracted text drives change detection. Mail is the
  rare source where the *transport envelope itself* carries provenance
  (see §5a) — never store a lossy rendering.
- **Parsing.** MIME multipart is walked for the HTML bulletin part
  (fallback: plain-text part); the standard text extractor produces the
  stored text. Bulletin boilerplate (headers, footers, unsubscribe
  blocks) is trimmed by the adapter deterministically — and, per the
  transformation rules, LLM inference plays no role in parsing.
- **Modes, disclosed per item**: `email-full` (the bulletin carries the
  release text) vs `email-teaser` (title + summary linking onward).
  Which mode a source yields is a content-evaluation finding recorded
  at onboarding; the digest's coverage language leans on it.
- **Identity and dedup.** Stable ID from the bulletin's canonical
  item URL where present, else a content-derived key — same
  compatibility-contract rules as every adapter (identity is frozen
  once a source is active). An item already ingested from a web channel
  is not duplicated by its email copy; first-recorded wins and the
  second channel is noted.
- **Dating.** The message's `Date` header (and any explicit bulletin
  date) is `claimed_published_at`; our receipt is the observation.
  The digest dating rule applies unchanged — in particular, a new
  subscription's **welcome batch** (old items re-sent on signup) is
  backfill: disclosed under AGENCYPR-EX-01, never presented as the
  day's news.

## 5a. DKIM: the corroboration layer

Web captures get a second witness via the Wayback Machine. Email
carries its own, stronger witness: **DKIM**. Bulletin senders sign each
message; a verifying signature over our stored raw bytes is
cryptographic evidence that the publisher's chosen distributor sent
exactly this content to us.

The adapter therefore, per message:

1. Verifies the DKIM signature at ingest and records the result.
2. **Archives the selector's DNS public key alongside the capture.**
   This step is what makes the evidence durable: DKIM keys rotate, and
   a signature whose key has left DNS becomes uncheckable. With the key
   archived, anyone holding our raw message and our key record can
   re-verify forever.
3. Records which domain signed (the platform's, e.g. GovDelivery's, vs
   the agency's own) — because the honest-limits statement depends on
   it: **DKIM proves the distributor sent these bytes on the
   publisher's behalf; it does not prove the agency's newsroom page
   said the same thing.**
4. Ingests messages that fail verification too — marked `dkim: fail`
   and excluded from any tamper-evidence claim. A failed signature is
   a fact worth recording, not a reason to drop official content.

## 6. What this class is not

- **Not a bypass.** The web refusal that made a source `unavailable`
  still stands, unmodified, in the registry — the email entry is a
  *sibling*, and the blocked-web record remains published
  accountability data. If the agency later opens its web channel, the
  posture is re-evaluated on its merits.
- **Not a full-newsroom guarantee.** Topic subscriptions under-cover;
  the gap is measured at onboarding and disclosed, not discovered by
  readers.
- **Not a private channel.** Everything ingested is what the publisher
  mass-distributes to any subscriber. FAPD never ingests
  correspondence, replies, or anything addressed to it individually.

## 7. For forks: pointing this at your government

The checklist travels: (1) find your jurisdiction's bulletin
infrastructure (one platform often serves many agencies — finding the
platform finds the universe); (2) create the project mailbox under your
fork's public identity; (3) subscribe deliberately, topic by topic,
recording selections; (4) verify DKIM posture per sender and archive
keys from day one; (5) register email sources as siblings, never
replacements, of whatever web records exist; (6) keep the bright line:
the bulletin's consent ends at the bulletin — links into refusing hosts
stay unfetched. The ethos does not localize; only the signup URLs do.
