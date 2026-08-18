"""Unit tests for src/fapd/tts.py (Text-to-Speech audio synthesis layer)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error

import pytest

from fapd.tts import (
    BaseTTSService,
    NullTTSService,
    OpenAITTSService,
    get_tts_service,
)


def test_null_tts_service(tmp_path):
    svc = NullTTSService()
    out = tmp_path / "test.mp3"
    res = svc.generate_audio("Test text", out)
    assert res is False
    assert not out.exists()


def test_get_tts_service_factory():
    assert isinstance(get_tts_service("none"), NullTTSService)
    assert isinstance(get_tts_service("disabled"), NullTTSService)
    assert isinstance(get_tts_service("invalid_provider"), NullTTSService)


def test_get_tts_service_openai(monkeypatch):
    monkeypatch.setattr("fapd.config.OPENAI_API_KEY", "sk-proj-testkey")
    monkeypatch.setattr("fapd.config.TTS_PROVIDER", "openai")
    svc = get_tts_service("openai")
    assert isinstance(svc, OpenAITTSService)
    assert svc.api_key == "sk-proj-testkey"


def test_get_tts_service_openai_no_key(monkeypatch):
    monkeypatch.setattr("fapd.config.OPENAI_API_KEY", "")
    svc = get_tts_service("openai")
    assert isinstance(svc, NullTTSService)


def test_openai_tts_service_empty_text(tmp_path):
    svc = OpenAITTSService(api_key="sk-test")
    out = tmp_path / "test.mp3"
    assert svc.generate_audio("", out) is False
    assert svc.generate_audio("   ", out) is False


def test_openai_tts_service_success(tmp_path):
    svc = OpenAITTSService(api_key="sk-test-key", default_model="tts-1", default_voice="nova")
    out_file = tmp_path / "subdir" / "audio.mp3"

    mock_resp = MagicMock()
    mock_resp.read.return_value = b"ID3_fake_mp3_binary_data"
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        result = svc.generate_audio("Hello daily digest narration", out_file)
        assert result is True
        assert out_file.exists()
        assert out_file.read_bytes() == b"ID3_fake_mp3_binary_data"

        # Check call arguments
        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "https://api.openai.com/v1/audio/speech"
        assert req.headers["Authorization"] == "Bearer sk-test-key"
        payload = json.loads(req.data.decode("utf-8"))
        assert payload["model"] == "tts-1"
        assert payload["voice"] == "nova"
        assert payload["input"] == "Hello daily digest narration"


def test_openai_tts_service_http_error(tmp_path):
    svc = OpenAITTSService(api_key="sk-test-key")
    out_file = tmp_path / "error.mp3"

    mock_err = urllib.error.HTTPError("url", 401, "Unauthorized", {}, None)
    mock_err.read = MagicMock(return_value=b'{"error": "Invalid key"}')

    with patch("urllib.request.urlopen", side_effect=mock_err):
        result = svc.generate_audio("Testing error path", out_file)
        assert result is False
        assert not out_file.exists()
