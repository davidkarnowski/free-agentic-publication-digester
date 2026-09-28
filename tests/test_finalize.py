"""fapd.finalize — the model layers as recordable, non-fatal steps
(GUIDE §6 rule 15, 2026-08-24).

The incident these pin: one provider 429 in the plain layer was a
traceback out of run_pipeline.py, exit 1, three times, then a halted
day — while the render could have proceeded on stored rows throughout.
"""

import json

import pytest

from fapd import config, finalize, inference, llm


class _Client:
    """A stand-in LLM client with the two things finalize reads: a
    status() dict and (via the patched layer functions) a way to fail."""

    def __init__(self, backend="fake", unavailable=None, models=("m1",),
                 backends_used=None):
        self._status = {"backend": backend, "unavailable": unavailable,
                        "models_used": list(models),
                        "backends_used": list(
                            backends_used if backends_used is not None
                            else [backend])}

    def status(self):
        return dict(self._status)

    def trip(self, reason):
        self._status["unavailable"] = reason


def _patch_layers(monkeypatch, behaviors, outcomes=None):
    """behaviors: {layer: callable(conn, client, date)}; unlisted layers
    return an empty stats dict. The stand-in layers store nothing, so the
    outcome of a layer that returns is fixed too: "ran" unless
    `outcomes` says otherwise. The real input/output reading is pinned
    against a database in the tests at the end of this file."""
    def fn_for(name):
        return behaviors.get(name, lambda conn, client, date: {name: "ok"})

    monkeypatch.setattr(finalize, "_layer_fn", fn_for)
    monkeypatch.setattr(finalize, "_layer_outcome",
                        lambda conn, name, date: (outcomes or {}).get(name, "ran"))


def test_all_layers_run_and_are_recorded(conn, monkeypatch):
    _patch_layers(monkeypatch, {})
    result = finalize.run_model_layers(conn, _Client(), "2026-08-24")
    assert result["layers"] == dict.fromkeys(finalize.LAYER_ORDER, "ran")
    row = inference.load(conn, "2026-08-24")
    assert row["available"] is True
    assert row["backend"] == "fake"
    assert row["models"] == ["m1"]


def test_a_provider_outage_mid_run_skips_the_rest_and_records_it(conn, monkeypatch):
    client = _Client()

    def plain_fails(conn, c, date):
        c.trip("quota exhausted")
        raise llm.ProviderUnavailableError("quota exhausted")

    _patch_layers(monkeypatch, {"plain": plain_fails})
    result = finalize.run_model_layers(conn, client, "2026-08-24")
    assert result["layers"] == {"map": "ran", "plain": "failed",
                                "compose": "skipped", "sections": "skipped",
                                "tags": "skipped"}
    assert inference.load(conn, "2026-08-24")["layers"]["compose"] == "skipped"
    # "ran" survives: the map layer's stored rows are the day's prose
    assert inference.load(conn, "2026-08-24")["available"] is True


def test_no_provider_at_all_records_every_layer_skipped(conn, monkeypatch):
    calls = []
    _patch_layers(monkeypatch, {
        name: (lambda conn, c, date: calls.append(1)) for name in finalize.LAYER_ORDER})
    result = finalize.run_model_layers(
        conn, _Client(backend="none", unavailable="disabled", models=()), "2026-08-24")
    assert calls == [], "an unavailable provider is never called"
    assert set(result["layers"].values()) == {"skipped"}
    assert inference.load(conn, "2026-08-24")["available"] is False


def test_a_plain_llm_error_fails_only_its_layer(conn, monkeypatch):
    def compose_fails(conn, c, date):
        raise llm.LLMError("backend failed (compose:day-in-review): boom")

    _patch_layers(monkeypatch, {"compose": compose_fails})
    result = finalize.run_model_layers(conn, _Client(), "2026-08-24")
    assert result["layers"]["compose"] == "failed"
    assert result["layers"]["sections"] == "ran", "a plain LLMError does not trip the run"


def test_our_own_bugs_still_propagate(conn, monkeypatch):
    def broken(conn, c, date):
        raise KeyError("not a provider problem")

    _patch_layers(monkeypatch, {"map": broken})
    with pytest.raises(KeyError):
        finalize.run_model_layers(conn, _Client(), "2026-08-24")


def test_record_false_leaves_no_row(conn, monkeypatch):
    _patch_layers(monkeypatch, {})
    finalize.run_model_layers(conn, _Client(), "2026-08-24", record=False)
    assert inference.load(conn, "2026-08-24") is None


def test_summary_line_names_the_reason_for_the_operator(conn, monkeypatch):
    """The console/log line MAY carry the cause — the digest never does."""
    _patch_layers(monkeypatch, {})
    result = finalize.run_model_layers(
        conn, _Client(unavailable="not authenticated", models=()), "2026-08-24")
    line = finalize.summary_line(result)
    assert "map=skipped" in line and "not authenticated" in line


def test_a_failover_day_records_every_provider_that_produced_prose(conn, monkeypatch):
    """GUIDE §6 r7: attribution follows the work. A day the CLI started
    and Gemini finished names both — recording only the client's current
    backend would make the digest's attribution false in one direction,
    and only the original in the other."""
    _patch_layers(monkeypatch, {})
    client = _Client(backend="gemini", models=("haiku", "gemini-2.5-flash"),
                     backends_used=["cli", "gemini"])
    finalize.run_model_layers(conn, client, "2026-09-01")
    row = inference.load(conn, "2026-09-01")
    assert row["backend"] == "cli, gemini"
    assert row["models"] == ["gemini-2.5-flash", "haiku"]
    # And the reader-facing line still carries no cause (r15).
    text = inference.label(row)
    assert text == "model layers ran — cli, gemini/gemini-2.5-flash, haiku"
    for banned in ("429", "quota", "error", "fail", "exhaust", "auth"):
        assert banned not in text.lower()


def test_a_day_with_no_prose_still_records_the_provider_that_was_asked(conn, monkeypatch):
    """backends_used is empty when nothing was produced — the recorded
    backend falls back to the client's own, so a no-inference day still
    says which provider refused to answer."""
    client = _Client(backend="cli", models=(), backends_used=[])

    def map_fails(conn, c, date):
        c.trip("quota exhausted")
        raise llm.ProviderUnavailableError("quota exhausted")

    _patch_layers(monkeypatch, {"map": map_fails})
    finalize.run_model_layers(conn, client, "2026-09-01")
    row = inference.load(conn, "2026-09-01")
    assert row["backend"] == "cli"
    assert row["available"] is False
    assert inference.label(row) == inference.NO_INFERENCE


# ---------------------------------------------------------------------------
# A layer with nothing to do is not a layer that ran (GUIDE §6 r15,
# amended 2026-09-28). The incident: on 2026-09-27 nothing passed a
# summary rule, no model call was made for the day, and all five layers
# were still recorded "ran" — the digest said "model layers ran — cli".
# ---------------------------------------------------------------------------

DAY = "2026-09-27"


def _observe(conn, package_id, collection, doc_type, metadata=None):
    conn.execute(
        "INSERT INTO packages (package_id, collection, last_modified, first_seen_at,"
        " date_issued, fetch_status, digest_day) VALUES (?, ?, 'x', 'x', ?, 'fetched', ?)",
        (package_id, collection, DAY, DAY))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, '', ?, ?, 'A title', ?, 'body', 4, 'x', 1)",
        (package_id, collection, doc_type, json.dumps(metadata or {})))
    conn.commit()


def test_every_layer_idle_on_a_day_that_observed_nothing(conn):
    for name in finalize.LAYER_ORDER:
        assert finalize._layer_outcome(conn, name, DAY) == "idle"


def test_a_quiet_day_is_idle_except_the_short_review(conn):
    """District opinions only: nothing for map, plain, sections or tags;
    the Day in Review has a quiet day to review, and ran once it stored
    one."""
    _observe(conn, "USCOURTS-ctd-1", "USCOURTS", "DISTRICT",
             {"court_name": "United States District Court for the District of Connecticut"})
    for name in ("map", "plain", "sections", "tags"):
        assert finalize._layer_outcome(conn, name, DAY) == "idle"
    # Material, but nothing stored: the gate withheld the short review.
    assert finalize._layer_outcome(conn, "compose", DAY) == "failed"
    conn.execute(
        "INSERT INTO day_summaries (date, prompt_version, model, summary,"
        " created_at, kind) VALUES (?, ?, 'opus', 'Short.', 'x', 'short')",
        (DAY, config.COMPOSE_PROMPT_VERSION))
    conn.commit()
    assert finalize._layer_outcome(conn, "compose", DAY) == "ran"


def test_a_selected_item_left_unsummarized_is_a_failed_map_layer(conn):
    _observe(conn, "USCOURTS-ca2-1", "USCOURTS", "APPELLATE")
    assert finalize._layer_outcome(conn, "map", DAY) == "failed"
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " inclusion_rule, summary, created_at)"
        " VALUES ('USCOURTS-ca2-1', '', ?, 'llm', 'USCOURTS-SEL-01', 'Affirmed.', 'x')",
        (config.PROMPT_VERSION,))
    conn.commit()
    assert finalize._layer_outcome(conn, "map", DAY) == "ran"
    # The plain layer now has material, and nothing stored yet.
    assert finalize._layer_outcome(conn, "plain", DAY) == "failed"


def test_an_all_idle_day_records_available_and_says_so(conn, monkeypatch):
    _patch_layers(monkeypatch, {}, dict.fromkeys(finalize.LAYER_ORDER, "idle"))
    finalize.run_model_layers(conn, _Client(models=(), backends_used=[]), DAY)
    row = inference.load(conn, DAY)
    assert row["available"] is True
    assert inference.label(row) == inference.NO_MODEL_WORK


def test_idle_layers_are_not_listed_as_missing(conn, monkeypatch):
    """The quiet day with a short review: only compose ran, and the row
    attributes it without calling the idle layers unavailable."""
    _patch_layers(monkeypatch, {}, {"map": "idle", "plain": "idle", "compose": "ran",
                                    "sections": "idle", "tags": "idle"})
    finalize.run_model_layers(conn, _Client(backend="cli", models=("opus",)), DAY)
    assert inference.label(inference.load(conn, DAY)) == "model layers ran — cli/opus"
