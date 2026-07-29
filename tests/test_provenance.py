"""Provenance layer tests: hashing, change semantics, manifest chaining."""

import json

import pytest

from fapd import config, db, provenance


class Resp:
    def __init__(self, body=b"<html><body>Hello world</body></html>",
                 status=200, headers=None, url="https://x.gov/a"):
        self.content = body
        self.status_code = status
        self.headers = headers or {"Content-Type": "text/html; charset=utf-8",
                                   "Date": "Sun, 26 Jul 2026 12:00:00 GMT"}
        self.url = url


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CAPTURE_DIR", tmp_path / "captures")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")
    conn = db.connect(tmp_path / "meta.db")
    yield conn
    conn.close()


def doc(conn, stable="guid-1"):
    return provenance.get_or_create_document(
        conn, "doj-press", stable, "https://x.gov/a", title="T",
        claimed_published_at="2026-07-25T10:00:00Z",
    )


def test_content_addressed_store_and_dedupe(env, tmp_path):
    d = doc(env)
    cid, kind = provenance.capture(env, d, "https://x.gov/a", Resp())
    assert kind == "new"
    row = env.execute("SELECT * FROM captures WHERE id = ?", (cid,)).fetchone()
    path = config.CAPTURE_DIR / row["content_sha256"][:2] / f"{row['content_sha256']}.bin"
    assert path.read_bytes() == Resp().content
    assert provenance.verify_stored(row["content_sha256"])
    # Same bytes again: dedupes on disk, records "unchanged"
    _, kind2 = provenance.capture(env, d, "https://x.gov/a", Resp())
    assert kind2 == "unchanged"
    assert len(list((tmp_path / "captures").rglob("*.bin"))) == 1


def test_change_kind_semantics(env):
    d = doc(env)
    provenance.capture(env, d, "https://x.gov/a", Resp())
    # Template noise changes, words identical -> bytes_changed
    noisy = Resp(body=b'<html><script>x=1</script><body>Hello   world</body></html>')
    _, kind = provenance.capture(env, d, "https://x.gov/a", noisy)
    assert kind == "bytes_changed"
    # Words change -> modified
    edited = Resp(body=b"<html><body>Hello world, revised</body></html>")
    _, kind = provenance.capture(env, d, "https://x.gov/a", edited)
    assert kind == "modified"


def test_attempt_records_absence(env):
    d = doc(env)
    provenance.record_attempt(env, d, "https://x.gov/a", "robots_refused",
                              note="robots disallowed")
    provenance.record_attempt(env, d, "https://x.gov/a", "unchanged_304",
                              http_status=304)
    kinds = [r["change_kind"] for r in
             env.execute("SELECT change_kind FROM captures ORDER BY id")]
    assert kinds == ["robots_refused", "unchanged_304"]


def test_document_identity_and_first_seen(env):
    d1 = doc(env, "guid-1")
    d2 = doc(env, "guid-1")  # same stable id -> same document
    assert d1 == d2
    row = env.execute("SELECT * FROM documents WHERE id = ?", (d1,)).fetchone()
    assert row["claimed_published_at"] == "2026-07-25T10:00:00Z"
    assert row["first_seen_at"] != row["claimed_published_at"]  # separate axes


def test_manifest_chain_and_content(env, monkeypatch):
    d = doc(env)
    clock = iter([
        "2026-07-25T10:00:00Z", "2026-07-26T10:00:00Z", "2026-07-26T10:01:00Z",
    ])
    monkeypatch.setattr(provenance, "utc_now_iso", lambda: next(clock))
    provenance.capture(env, d, "https://x.gov/a", Resp())          # day 1
    provenance.capture(env, d, "https://x.gov/a",                  # day 2
                       Resp(body=b"<html><body>Edited</body></html>"))
    provenance.record_attempt(env, d, "https://x.gov/a", "unchanged_304",
                              http_status=304)                     # day 2
    m1 = provenance.export_manifest(env, "2026-07-25")
    m2 = provenance.export_manifest(env, "2026-07-26")

    h1 = json.loads(m1.read_text().splitlines()[0])
    assert h1["prev_manifest_sha256"] is None
    assert h1["entries"] == 1
    lines2 = m2.read_text().splitlines()
    h2 = json.loads(lines2[0])
    assert h2["prev_manifest_sha256"] == provenance.sha256_hex(m1.read_bytes())
    assert h2["entries"] == 2  # the modified capture AND the 304 attempt
    entry_kinds = [json.loads(x)["change_kind"] for x in lines2[1:]]
    assert entry_kinds == ["modified", "unchanged_304"]


def test_charset_fallback_deterministic(env):
    latin = "Café statement".encode("latin-1")
    body = b"<html><body>" + latin + b"</body></html>"
    r = Resp(body=body, headers={"Content-Type": "text/html; charset=latin-1"})
    t1 = provenance.normalize_text(r.content, r.headers["Content-Type"])
    t2 = provenance.normalize_text(r.content, r.headers["Content-Type"])
    assert t1 == t2 == "Café statement"
