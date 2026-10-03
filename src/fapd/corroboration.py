"""Cross-time cross-source document corroboration (GUIDE §3, amended
2026-10-02).

The same government document reaches us through more than one channel on
*different* days. The clearest case: the President signs an executive
order or proclamation, the White House publishes it on whitehouse.gov
(our ``PRESACT`` collection), and the Federal Register compiles the same
instrument a few days later (``FR`` documents of type ``PRESDOCU``).
``report.corroborate`` already de-duplicates *same-day, same-URL*
observations; this module records the *cross-day* relationship as a
stored fact so the digest can reference the earlier publication without
suppressing the later one (operator decisions, 2026-10-02):

1. a 30-day look-back window;
2. the later copy is never suppressed — it is listed as "what the
   government said today", carrying a reference to the prior
   publication's date and source;
3. frozen days stay frozen — the link is recorded and shown on the day
   the later copy appears, pointing back; the earlier day is untouched;
4. a normalized-title match is only a *candidate*; a programmatic
   body-similarity check must confirm it before a link is recorded;
5. the relationship is recorded in the database (write-once), not
   re-derived at render time.

Everything here is mechanical and deterministic — no inference, no
network. Detection runs once in the end-of-day pipeline
(:func:`record_cross_source`) and the render reads the stored link
(:func:`prior_links`).

Scope, for now: the one class where the same document deterministically
appears in two channels with a stable official title — an FR
presidential document (the *later* compilation) duplicating an earlier
White House presidential action. Direction is therefore inherent (the
Federal Register is always the compiler, never the origin), which is why
the 2026-08-06 White House-feed activation backfill — months of old
actions observed on one day — cannot create a spurious link: a
``PRESACT`` row is never the *later* side of this rule. The matcher
(:func:`_title_key`, :func:`_same_document`) is written generically so
the rule can widen later (agency release -> FR) behind an indexed title
key.

The secondary body check is two numbers over word *k*-shingles: the
Jaccard coefficient |A∩B| / |A∪B| (the operator's chosen metric, stored
as the audit score) and the overlap/containment coefficient
|A∩B| / min(|A|, |B|). Both thresholds were set from the production
corpus (2026-10-02, read-only): across the 36 genuine FR↔PRESACT pairs
then on record, Jaccard ran 0.20–0.83 and overlap 0.51–0.99, while a
title-key collision between unrelated documents scores like any two
unrelated texts (Jaccard ≈ 0.10). Jaccard alone separates poorly because
an FR compilation and the White House web copy differ in length and
boilerplate, which deflates a symmetric metric for a genuine duplicate;
the overlap coefficient is robust to that size gap. Requiring *both*
``jaccard >= 0.15`` and ``overlap >= 0.45`` admits every genuine pair
observed and rejects an unrelated collision. The check errs toward
*missing* a link, never toward a false one — a missed link just means
the later entry lists normally (decision 2), while a false link would
assert a duplication that is not real.
"""

import datetime as dt
import json
import re

#: Look-back window (operator decision 1, 2026-10-02). The measured
#: forward lag from the White House feed to the Federal Register was a
#: 5-day median with a thin tail to ~15 days; 30 days covers it with
#: margin without reaching into unrelated history.
WINDOW_DAYS = 30

#: Word-shingle width for the secondary body-similarity check.
SHINGLE_K = 3

#: Secondary-check gate (see the module docstring for the measured
#: basis). Both must hold; the gate is intentionally conservative.
JACCARD_MIN = 0.15
OVERLAP_MIN = 0.45

_EO_PREFIX = re.compile("^\\s*executive order\\s+\\d+\\s*[—:-]\\s*",
                        re.IGNORECASE)
_NONALNUM = re.compile(r"[^a-z0-9]+")
_WORD = re.compile(r"[a-z0-9]+")


def _title_key(title):
    """A document's identity across channels, from its official title:
    lowercased, a leading ``Executive Order NNNNN—`` prefix dropped (the
    Federal Register prepends the EO number the White House page omits),
    every non-alphanumeric run collapsed to a single space, trimmed.
    Pure string work — the strong primary gate, confirmed by
    :func:`_same_document`."""
    key = _EO_PREFIX.sub("", (title or "").lower())
    return _NONALNUM.sub(" ", key).strip()


def _shingles(text, k=SHINGLE_K):
    """The set of k-consecutive-word tuples in ``text`` (lowercased
    alphanumeric tokens). Shorter-than-k texts fall back to their bare
    word set so the metrics stay defined."""
    words = _WORD.findall((text or "").lower())
    if len(words) < k:
        return {(w,) for w in words}
    return {tuple(words[i:i + k]) for i in range(len(words) - k + 1)}


def _similarity(a_text, b_text):
    """``(jaccard, overlap)`` over word k-shingles. Returns ``(0.0, 0.0)``
    when either text has no shingles (nothing to compare is not a match)."""
    a, b = _shingles(a_text), _shingles(b_text)
    if not a or not b:
        return 0.0, 0.0
    inter = len(a & b)
    jaccard = inter / len(a | b)
    overlap = inter / min(len(a), len(b))
    return jaccard, overlap


def _same_document(a_text, b_text):
    """``(is_duplicate, jaccard)``: the secondary confirmation. True only
    when both the Jaccard and the overlap coefficient clear their gates
    (see the module docstring). The Jaccard is returned for storage as
    the audit score regardless of the verdict."""
    jaccard, overlap = _similarity(a_text, b_text)
    return (jaccard >= JACCARD_MIN and overlap >= OVERLAP_MIN), jaccard


def _url_of(metadata_json):
    """The official URL stored in an ``extracted_texts.metadata`` blob, or
    None. Tolerant of a malformed blob — provenance reads never raise."""
    try:
        meta = json.loads(metadata_json or "{}")
    except (TypeError, ValueError):
        return None
    url = meta.get("url")
    return url if isinstance(url, str) and url else None


def _now_iso():
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_cross_source(conn, date, *, window_days=WINDOW_DAYS, now=None):
    """Detect and record cross-day duplicate publications for digest day
    ``date`` and return the link rows created this call.

    For every Federal Register presidential document filed on ``date``
    (the later compilation), look back ``window_days`` for a White House
    presidential action (``PRESACT``) filed on a strictly earlier day
    whose title key matches, confirm it with :func:`_same_document`, and
    ``INSERT OR IGNORE`` a corroboration link pointing from the later
    copy to the earlier one. Write-once and idempotent: a re-finalize of
    the same day records nothing new. Zero inference, no network — reads
    ``extracted_texts`` and writes ``corroborations`` only.

    Every observation stays its own distinct row (GUIDE §3): this records
    a *relationship between* rows, it never merges or drops one. Filing
    is by ``digest_day`` — our observation clock and the single source of
    the day a document belongs to (CLAUDE.md §9) — so the earlier,
    already-frozen day is only read, never rewritten (decision 3)."""
    now = now or _now_iso()
    window_start = (
        dt.date.fromisoformat(date) - dt.timedelta(days=window_days)
    ).isoformat()

    later = conn.execute(
        """
        SELECT e.package_id, e.granule_id, e.title, e.text
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'FR' AND e.doc_type = 'PRESDOCU'
          AND p.digest_day = ?
        """,
        (date,),
    ).fetchall()
    if not later:
        return []

    priors = conn.execute(
        """
        SELECT e.package_id, e.granule_id, e.title, e.text, e.collection,
               e.metadata, p.digest_day
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'PRESACT'
          AND p.digest_day < ? AND p.digest_day >= ?
        """,
        (date, window_start),
    ).fetchall()
    if not priors:
        return []

    by_key = {}
    for r in priors:
        by_key.setdefault(_title_key(r["title"]), []).append(r)

    created = []
    for lr in later:
        candidates = by_key.get(_title_key(lr["title"]))
        if not candidates:
            continue
        # The best confirmed prior: highest containment, then highest
        # Jaccard, then the earliest observation — a deterministic pick
        # when a title recurs (e.g. the feed carried it twice).
        best = None
        for pr in candidates:
            ok, jaccard = _same_document(lr["text"], pr["text"])
            if not ok:
                continue
            _, overlap = _similarity(lr["text"], pr["text"])
            rank = (overlap, jaccard, _negate_date(pr["digest_day"]))
            if best is None or rank > best[0]:
                best = (rank, pr, jaccard)
        if best is None:
            continue
        _, pr, jaccard = best
        row = (
            lr["package_id"], lr["granule_id"] or "",
            pr["package_id"], pr["granule_id"] or "",
            pr["collection"], _source_label(pr["collection"]),
            pr["digest_day"], _url_of(pr["metadata"]),
            _title_key(lr["title"]), round(jaccard, 4), now,
        )
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO corroborations
                (package_id, granule_id, prior_package_id, prior_granule_id,
                 prior_collection, prior_source, prior_date, prior_url,
                 title_key, similarity, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )
        if cur.rowcount:
            created.append({
                "package_id": row[0], "granule_id": row[1],
                "prior_package_id": row[2], "prior_granule_id": row[3],
                "prior_collection": row[4], "prior_source": row[5],
                "prior_date": row[6], "prior_url": row[7],
                "title_key": row[8], "similarity": row[9],
                "detected_at": row[10],
            })
    conn.commit()
    return created


def _negate_date(date):
    """A sort key that makes the *earliest* date rank highest (we prefer
    the first time the government published the prior document)."""
    return tuple(-n for n in (int(p) for p in date.split("-")))


#: Display label for the prior publication's channel (decision 2). Kept
#: tiny and local; a wider rule adds its channels here.
_SOURCE_LABELS = {"PRESACT": "the White House"}


def _source_label(collection):
    return _SOURCE_LABELS.get(collection, collection)


def prior_links(conn, keys):
    """``{(package_id, granule_id): [prior-publication dict, ...]}`` for the
    later entries among ``keys`` that carry a recorded prior publication.
    The render reads this and references the prior publication on the
    later entry (:func:`report._prior_pub_lines`); it never reads the
    frozen earlier day. ``keys`` is an iterable of
    ``(package_id, granule_id)`` pairs."""
    out = {}
    for pkg, gran in {(k[0], k[1] or "") for k in keys}:
        rows = conn.execute(
            """
            SELECT prior_collection, prior_source, prior_date, prior_url,
                   title_key, similarity
            FROM corroborations
            WHERE package_id = ? AND granule_id = ?
            ORDER BY prior_date, prior_package_id
            """,
            (pkg, gran),
        ).fetchall()
        if rows:
            out[(pkg, gran)] = [dict(r) for r in rows]
    return out


def attach_prior_links(conn, items):
    """Set ``item['_prior_publication']`` on each item that has a recorded
    prior publication, keyed by ``(package_id, granule_id)``. A no-op for
    items without a link. Mutates and returns ``items``."""
    links = prior_links(conn, [(i["package_id"], i["granule_id"]) for i in items])
    for item in items:
        link = links.get((item["package_id"], item["granule_id"] or ""))
        if link:
            item["_prior_publication"] = link
    return items


def links_for_manifest(conn, utc_day):
    """The corroboration links detected on UTC calendar day ``utc_day``,
    as plain dicts for the daily provenance manifest (decision 6). The
    manifest is a UTC-capture-day record, and detection is itself an
    event on the UTC day it runs — the end-of-day finalize — so a link
    is folded into the manifest for the day it was *detected*. Ordered
    deterministically."""
    rows = conn.execute(
        """
        SELECT package_id, granule_id, prior_package_id, prior_granule_id,
               prior_collection, prior_source, prior_date, prior_url,
               title_key, similarity, detected_at
        FROM corroborations
        WHERE substr(detected_at, 1, 10) = ?
        ORDER BY package_id, granule_id, prior_package_id
        """,
        (utc_day,),
    ).fetchall()
    return [dict(r) for r in rows]
