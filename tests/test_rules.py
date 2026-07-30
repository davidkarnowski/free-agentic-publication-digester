"""Selection-rule registry tests (rules.py) — the project's most
safety-critical module: what these rules select is what the digest
publishes, and registry order is precedence. Corpus fixtures live in
conftest.py, shared with the analyze suite."""

from conftest import DATE, EXPECTED_RULES, LONG_TEXT, SENATE_VOTE_TEXT, seed_corpus, seed_item

from fapd import rules


def test_selection_rule_assignment_and_no_duplicates(conn):
    seed_corpus(conn)
    items = rules.select_items(conn, DATE)
    got = {(i["package_id"], i["granule_id"]): i["rule_id"] for i in items}
    assert got == EXPECTED_RULES
    assert len(items) == len(got)  # one row per item — no duplicates
    for item in items:
        assert set(item) == {"package_id", "granule_id", "collection",
                             "doc_type", "title", "rule_id"}


def test_exclusion_counts(conn):
    seed_corpus(conn)
    assert rules.exclusion_counts(conn, DATE) == {
        "FR-EX-01": 1,        # the NOTICE, official summary notwithstanding
        "CREC-EX-01": 2,      # PgH2 (14999 chars) and PgH4 (postponed vote)
        "CREC-EX-02": 2,      # EXTENSIONS + DAILYDIGEST
        "USCOURTS-EX-01": 1,  # the DISTRICT opinion
        "USCOURTS-EX-02": 1,  # the BANKRUPTCY opinion
    }


def test_exclusion_counts_empty_day_has_all_keys(conn):
    assert rules.exclusion_counts(conn, DATE) == {
        "FR-EX-01": 0, "CREC-EX-01": 0, "CREC-EX-02": 0,
        "USCOURTS-EX-01": 0, "USCOURTS-EX-02": 0,
    }


def test_every_rule_has_a_description():
    for registry in (rules.RULES, rules.EXCLUSIONS):
        for spec in registry.values():
            assert spec["description"]


def test_plaw_selection(conn):
    # PLAW-SEL-01 shipped with the collection but had never been exercised
    # by a test (and govinfo has listed no real package yet).
    seed_item(conn, "PLAW-119publ23", "", "PLAW", "PUBLIC-LAW",
              "An Act to test the enacted-laws rule.")
    items = rules.select_items(conn, DATE)
    assert [(i["package_id"], i["rule_id"]) for i in items] == [
        ("PLAW-119publ23", "PLAW-SEL-01")]


def test_registry_order_is_precedence(conn):
    # The contract _first_matching_rule relies on: matcher order IS registry
    # order, and the first match wins. An item that satisfies both
    # CREC-SEL-01 (floor time) and CREC-SEL-02 (recorded vote) must carry
    # SEL-01 because it appears first in the registry.
    assert list(rules._MATCHERS) == list(rules.RULES)
    order = list(rules.RULES)
    assert order.index("CREC-SEL-01") < order.index("CREC-SEL-02")
    seed_item(conn, "CREC-2026-07-23", "PgBoth", "CREC", "SENATE",
              LONG_TEXT + SENATE_VOTE_TEXT)
    (item,) = rules.select_items(conn, DATE)
    assert item["rule_id"] == "CREC-SEL-01"


def test_unmatched_rows_are_neither_selected_nor_exclusion_counted(conn):
    # Current honest behavior, pinned: a row matching no selection rule and
    # no named exclusion (e.g. an introduced bill) is simply unselected —
    # it appears in the coverage statement's totals, not in these counts.
    seed_item(conn, "BILLS-119hr3ih", "", "BILLS", "Introduced-in-House")
    assert rules.select_items(conn, DATE) == []
    assert all(n == 0 for n in rules.exclusion_counts(conn, DATE).values())
