"""fapd.inference — the per-day model-layer status (GUIDE §6 r15) and
the ONLY wording the digest may carry for it."""

from fapd import db, inference


def _conn(tmp_path):
    return db.connect(tmp_path / "fapd.db")


def test_record_and_load_round_trip(tmp_path):
    conn = _conn(tmp_path)
    try:
        written = inference.record(
            conn, "2026-08-24", backend="cli", models=["haiku", "opus", "haiku"],
            layers={"map": "ran", "plain": "ran", "compose": "ran",
                    "sections": "ran", "tags": "ran"})
        loaded = inference.load(conn, "2026-08-24")
        assert loaded == written
        assert loaded["available"] is True
        assert loaded["models"] == ["haiku", "opus"]  # deduplicated, sorted
        assert loaded["layers"] == dict.fromkeys(inference.LAYERS, "ran")
    finally:
        conn.close()


def test_missing_layers_default_to_skipped_and_available_follows(tmp_path):
    conn = _conn(tmp_path)
    try:
        inference.record(conn, "2026-08-24", backend="gemini", models=[],
                         layers={"map": "failed"})
        loaded = inference.load(conn, "2026-08-24")
        assert loaded["available"] is False
        assert loaded["layers"]["map"] == "failed"
        assert loaded["layers"]["compose"] == "skipped"
    finally:
        conn.close()


def test_last_finalize_wins(tmp_path):
    conn = _conn(tmp_path)
    try:
        inference.record(conn, "2026-08-24", backend="none", models=[], layers={})
        inference.record(conn, "2026-08-24", backend="cli", models=["haiku"],
                         layers=dict.fromkeys(inference.LAYERS, "ran"))
        loaded = inference.load(conn, "2026-08-24")
        assert loaded["backend"] == "cli" and loaded["available"] is True
        assert conn.execute("SELECT COUNT(*) FROM day_inference").fetchone()[0] == 1
    finally:
        conn.close()


def test_load_returns_none_for_an_unrecorded_day(tmp_path):
    conn = _conn(tmp_path)
    try:
        assert inference.load(conn, "2026-01-01") is None
    finally:
        conn.close()


def test_unknown_layer_status_is_rejected(tmp_path):
    conn = _conn(tmp_path)
    try:
        try:
            inference.record(conn, "2026-08-24", backend="cli", models=[],
                             layers={"map": "maybe"})
        except ValueError as exc:
            assert "maybe" in str(exc)
        else:
            raise AssertionError("an unknown status must not be stored")
    finally:
        conn.close()


def test_label_three_states_and_nothing_else():
    ran = {"available": True, "backend": "cli", "models": ["haiku", "opus"],
           "layers": dict.fromkeys(inference.LAYERS, "ran")}
    assert inference.label(ran) == "model layers ran — cli/haiku, opus"

    partial = {"available": True, "backend": "gemini", "models": ["gemini-2.5-flash"],
               "layers": {"map": "ran", "plain": "failed", "compose": "skipped",
                          "sections": "ran", "tags": "ran"}}
    assert inference.label(partial) == (
        "model layers ran in part — gemini/gemini-2.5-flash;"
        " not available: plain-language lines, Day in Review")

    none = {"available": False, "backend": "gemini", "models": [],
            "layers": dict.fromkeys(inference.LAYERS, "failed")}
    assert inference.label(none) == inference.NO_INFERENCE
    assert inference.label(None) == inference.NO_INFERENCE
    # The ruling: no cause, no error text, no provider named as a cause.
    for text in (inference.label(none), inference.label(partial)):
        for banned in ("429", "quota", "error", "HTTP", "exhaust", "auth"):
            assert banned not in text.lower()
