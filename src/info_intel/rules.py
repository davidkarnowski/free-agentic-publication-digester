"""Mechanical selection rules — the versioned registry that answers "why
did this item make the digest?" (GUIDE §2 method transparency; §6 rule 4:
selection before summarization, always).

Every predicate is party-blind and subject-blind and runs at zero token
cost: floor time consumed, presence of a recorded vote, stage of the
legislative process, Federal Register document class. Loosening or adding
a rule is a GUIDE change, not a tweak. Exclusions are named rules too, so
the digest's Coverage Statement can account for every document — silent
omission is the failure mode we most guard against (GUIDE §2).

Registry order is precedence: an item matching several rules is attributed
to the first match, so each item carries exactly one inclusion rule.
"""

import re

# CREC-SEL-01 threshold: extracted-text length is the floor-time proxy
# (GUIDE §2 "floor time consumed"). Calibrated on the 2026-07-23 issue:
# 167 House/Senate floor granules, most a few hundred chars of procedure;
# >= 15000 chars keeps the six granules of sustained debate.
CREC_FLOOR_CHAR_THRESHOLD = 15000

# CREC-SEL-02 markers, as actually printed in the Record (2026-07-23):
#   House:  "[Roll No. 282]"        then "YEAS--214 ... NAYS--208"
#   Senate: "[Rollcall Vote No. 207 Leg.]" then "YEAS--47 ... NAYS--45"
# Case-sensitive on purpose: narrative text such as "the yeas and nays
# were ordered ... further proceedings postponed" reports a demanded vote
# with no recorded result and must not match.
RECORDED_VOTE_RE = re.compile(
    r"\[Roll No\. \d+\]"
    r"|\[Rollcall Vote No\. \d+"
    r"|YEAS--\d+[\s\S]{1,20000}?NAYS--\d+"
)

_CREC_FLOOR_TYPES = ("HOUSE", "SENATE")
_CREC_COUNTED_TYPES = ("EXTENSIONS", "DAILYDIGEST")

# BILLS-SEL-01: reached-stage markers. The extractor stores bulk-data stage
# strings ("Enrolled-Bill", "Reported-in-House", "Placed-on-Calendar-Senate");
# bare GPO version codes are accepted too so the rule survives an extractor
# change.
_BILL_STAGE_SUBSTRINGS = ("Enrolled", "Reported", "Placed-on-Calendar")
_BILL_VERSION_CODES = frozenset({"enr", "rh", "rs", "pcs"})

RULES = {
    "CREC-SEL-01": {
        "description": (
            "House/Senate floor granule with extracted text of at least "
            f"{CREC_FLOOR_CHAR_THRESHOLD} characters (floor-time proxy)."
        ),
    },
    "CREC-SEL-02": {
        "description": (
            "House/Senate floor granule containing a recorded-vote marker "
            "(Roll No. / Rollcall Vote No. / YEAS–NAYS tally); always "
            "included regardless of length."
        ),
    },
    "BILLS-SEL-01": {
        "description": (
            "Bill text at a reached stage: Enrolled, Reported, or "
            "Placed-on-Calendar (version codes enr/rh/rs/pcs)."
        ),
    },
    "FR-SEL-01": {
        "description": "Federal Register final rule (doc_type RULE); all are listed.",
    },
    "FR-SEL-02": {
        "description": "Federal Register proposed rule (doc_type PRORULE); all are listed.",
    },
    "FR-SEL-03": {
        "description": (
            "Federal Register presidential document (doc_type PRESDOCU); all are listed."
        ),
    },
    "USCOURTS-SEL-01": {
        "description": "appellate court opinion (doc_type APPELLATE); all listed.",
    },
    "USCOURTS-SEL-02": {
        "description": (
            "national court opinion (doc_type NATIONAL — e.g. Court of "
            "International Trade, Court of Federal Claims); all listed."
        ),
    },
}

EXCLUSIONS = {
    "FR-EX-01": {
        "description": (
            "Federal Register notices (doc_type NOTICE): counted in totals, "
            "not individually summarized."
        ),
    },
    "CREC-EX-01": {
        "description": (
            "House/Senate floor granules below the "
            f"{CREC_FLOOR_CHAR_THRESHOLD}-character floor-time threshold "
            "with no recorded-vote marker: counted only."
        ),
    },
    "CREC-EX-02": {
        "description": (
            "EXTENSIONS and DAILYDIGEST granules: counted; Daily Digest "
            "text feeds the compose stage as input, not as a listed item."
        ),
    },
    "USCOURTS-EX-01": {
        "description": (
            "District court opinions (doc_type DISTRICT): counted in "
            "totals, not individually summarized."
        ),
    },
    "USCOURTS-EX-02": {
        "description": (
            "Bankruptcy court opinions (doc_type BANKRUPTCY): counted in "
            "totals, not individually summarized."
        ),
    },
}


def _is_crec_floor(row):
    return row["collection"] == "CREC" and row["doc_type"] in _CREC_FLOOR_TYPES


def _match_crec_sel_01(row):
    return _is_crec_floor(row) and row["char_count"] >= CREC_FLOOR_CHAR_THRESHOLD


def _match_crec_sel_02(row):
    return _is_crec_floor(row) and RECORDED_VOTE_RE.search(row["text"]) is not None


def _match_bills_sel_01(row):
    if row["collection"] != "BILLS":
        return False
    doc_type = row["doc_type"] or ""
    return (
        any(s in doc_type for s in _BILL_STAGE_SUBSTRINGS)
        or doc_type.lower() in _BILL_VERSION_CODES
    )


def _match_fr(doc_type):
    return lambda row: row["collection"] == "FR" and row["doc_type"] == doc_type


def _match_uscourts(doc_type):
    return lambda row: row["collection"] == "USCOURTS" and row["doc_type"] == doc_type


# Same keys, same order as RULES — precedence is registry order.
_MATCHERS = {
    "CREC-SEL-01": _match_crec_sel_01,
    "CREC-SEL-02": _match_crec_sel_02,
    "BILLS-SEL-01": _match_bills_sel_01,
    "FR-SEL-01": _match_fr("RULE"),
    "FR-SEL-02": _match_fr("PRORULE"),
    "FR-SEL-03": _match_fr("PRESDOCU"),
    "USCOURTS-SEL-01": _match_uscourts("APPELLATE"),
    "USCOURTS-SEL-02": _match_uscourts("NATIONAL"),
}

assert list(_MATCHERS) == list(RULES)

_ROWS_SQL = """
SELECT et.package_id, et.granule_id, et.collection, et.doc_type, et.title,
       et.char_count, et.text
FROM extracted_texts AS et
JOIN packages AS p ON p.package_id = et.package_id
WHERE p.date_issued = ?
ORDER BY et.collection, et.package_id, et.granule_id
"""


def _first_matching_rule(row):
    for rule_id, matcher in _MATCHERS.items():
        if matcher(row):
            return rule_id
    return None


def select_items(conn, date):
    """All extracted documents for the publication date that match a
    selection rule. Each item appears once, attributed to its first
    matching rule in registry order."""
    items = []
    for row in conn.execute(_ROWS_SQL, (date,)):
        rule_id = _first_matching_rule(row)
        if rule_id is not None:
            items.append(
                {
                    "package_id": row["package_id"],
                    "granule_id": row["granule_id"],
                    "collection": row["collection"],
                    "doc_type": row["doc_type"],
                    "title": row["title"],
                    "rule_id": rule_id,
                }
            )
    return items


def exclusion_counts(conn, date):
    """Counts per named exclusion rule for the Coverage Statement. Every
    unselected document of a covered class is attributed to exactly one
    exclusion rule; keys are always present, zero-count included."""
    counts = dict.fromkeys(EXCLUSIONS, 0)
    for row in conn.execute(_ROWS_SQL, (date,)):
        if _first_matching_rule(row) is not None:
            continue
        if row["collection"] == "FR" and row["doc_type"] == "NOTICE":
            counts["FR-EX-01"] += 1
        elif _is_crec_floor(row):
            counts["CREC-EX-01"] += 1
        elif row["collection"] == "CREC" and row["doc_type"] in _CREC_COUNTED_TYPES:
            counts["CREC-EX-02"] += 1
        elif row["collection"] == "USCOURTS" and row["doc_type"] == "DISTRICT":
            counts["USCOURTS-EX-01"] += 1
        elif row["collection"] == "USCOURTS" and row["doc_type"] == "BANKRUPTCY":
            counts["USCOURTS-EX-02"] += 1
    return counts
