"""Conformance smoke (A.6 #10): scripted transcripts per era replayed in process and over HTTP,
with exact expected responses."""

from __future__ import annotations

import json

import pytest
from support_static_mcp import FIXTURES, in_process

TRANSCRIPTS = {
    p.stem: json.loads(p.read_text(encoding="utf-8"))
    for p in sorted((FIXTURES / "transcripts").glob("*.json"))
}
STEPS = [(name, step) for name, t in TRANSCRIPTS.items() for step in t["steps"]]


def test_both_eras_have_transcripts():
    assert set(TRANSCRIPTS) == {"legacy", "modern"}
    assert all(len(t["steps"]) >= 6 for t in TRANSCRIPTS.values())


@pytest.mark.parametrize("name, step", STEPS, ids=[f"{n}:{s['name']}" for n, s in STEPS])
def test_transcript_in_process(manifest, store, name, step):
    status, body, _ = in_process(manifest, store, step["body"], step["headers"])
    assert status == step["expect"]["status"]
    assert body == step["expect"]["body"]


@pytest.mark.parametrize("name", sorted(TRANSCRIPTS))
def test_transcript_over_http(running, name):
    for step in TRANSCRIPTS[name]["steps"]:
        status, _, raw = running.post(step["body"], step["headers"])
        assert status == step["expect"]["status"], step["name"]
        body = json.loads(raw) if raw else None
        assert body == step["expect"]["body"], step["name"]
