"""The suite never holds a narration key unless a test sets one itself.

Pins conftest's autouse `no_tts_key`: the compose tests narrate every Day in
Review they store, so a key that reached them meant real, paid speech calls
and MP3s written into the tracked site/ folder."""

import os

from fapd import compose, config
from fapd.tts import NullTTSService, get_tts_service


def test_the_suite_holds_no_narration_key():
    assert config.OPENAI_API_KEY == ""
    assert os.environ.get("OPENAI_API_KEY") == ""


def test_narration_resolves_to_the_null_service():
    assert isinstance(get_tts_service("openai"), NullTTSService)


def test_narrating_a_day_writes_nothing(tmp_path):
    saved = config.SITE_DIR
    config.SITE_DIR = tmp_path
    try:
        compose._narrate("2026-07-23", "A short Day in Review.")
    finally:
        config.SITE_DIR = saved
    assert not any(tmp_path.rglob("*.mp3"))
