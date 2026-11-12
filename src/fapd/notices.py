"""Operator notices: one small JSON file per end-of-day event.

GUIDE §2's no-silent-omission rule, applied to operations: a day that does
not publish should not wait for someone to read a log. This module decides
what a notice says and where it is written, never how it reaches the
operator. ``config.NOTICE_DIR`` (``FAPD_NOTICE_DIR``) names a directory;
whatever reads that directory belongs to the operator and lives outside
this repository. Unset, nothing is written.

A notice holds only facts the logs already hold: the day, the event, an
attempt count, an exit code, the recovery command. Never a secret, an
address or a path outside the project. Writing one is best-effort: a notice
that cannot be written is logged and dropped, and never fails the work that
raised it.

Format (version 1): one UTF-8 JSON object per file, at most ``MAX_BYTES``,
written atomically (a dotfile, then a rename), in a common notice shape
any relay can read::

    {"v": 1, "kind": "fapd-eod-halted", "level": "alert",
     "subject": "2026-11-11: digest halted after 4 failed attempts",
     "title": "...", "fields": {"Day": "2026-11-11", "Attempts": "4 of 4",
     "Detail": "..."}, "link": "https://<site>/", "queued_at": "...",
     "source": "fapd", "event": "eod.halted", "day": "2026-11-11"}

The subject names the day and the event, not the project: whatever delivers
the notice labels where it came from. The title, for the body, names both.
The file takes the directory's owner and group, mode 0640: whoever owns the
directory, and nobody else, can read it.
"""

import contextlib
import json
import logging
import os
import secrets
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from . import config

logger = logging.getLogger("fapd.notices")

VERSION = 1
#: Every event a notice may carry, and its level (info, ok, warn, alert).
EVENTS = {
    "eod.failed": "warn",
    "eod.halted": "alert",
    "eod.push_failed": "warn",
    "eod.push_halted": "alert",
    "eod.published": "ok",
}
MAX_BYTES = 4096
MAX_FACTS = 8


def _text(value, limit):
    return " ".join(str(value).split())[:limit]


def emit(event, day, title, detail="", facts=None, *, subject=None, link=None, notice_dir=None,
         now=None):
    """Write one notice. Returns its path, or None when notices are off or
    the write failed (logged, never raised)."""
    directory = config.NOTICE_DIR if notice_dir is None else notice_dir
    if not directory:
        return None
    tmp = None
    try:
        if event not in EVENTS:
            raise ValueError(f"unknown notice event {event!r}")
        stamp = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
        fields = {"Day": _text(day, 10)}
        fields.update({_text(k, 40): _text(v, 120)
                       for k, v in list((facts or {}).items())[:MAX_FACTS]})
        if detail:
            fields["Detail"] = _text(detail, 400)
        notice = {
            "v": VERSION, "kind": "fapd-" + event.replace(".", "-").replace("_", "-"),
            "level": EVENTS[event], "subject": _text(subject or title, 110),
            "title": _text(title, 160), "fields": fields, "queued_at": stamp,
            "source": "fapd", "event": event, "day": _text(day, 10),
        }
        if link and str(link).startswith("https://"):
            notice["link"] = _text(link, 200)
        body = json.dumps(notice, ensure_ascii=False, sort_keys=True).encode("utf-8")
        if len(body) > MAX_BYTES:
            raise ValueError(f"notice is {len(body)} bytes, over {MAX_BYTES}")
        folder = Path(directory)
        name = (stamp.replace("-", "").replace(":", "")
                + f"-{event.replace('.', '-')}-{secrets.token_hex(4)}.json")
        fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".json", dir=folder)
        with os.fdopen(fd, "wb") as fh:
            fh.write(body)
        _own_like(folder, tmp)
        os.replace(tmp, folder / name)
        tmp = None
        logger.info("notice %s for %s written", event, day)
        return folder / name
    except Exception as exc:  # noqa: BLE001 — best-effort by design (docstring)
        logger.warning("notice %s for %s not written: %r", event, day, exc)
        return None
    finally:
        if tmp:
            with contextlib.suppress(OSError):
                os.unlink(tmp)


def _own_like(folder, path):
    """Give the file the directory's owner and group, mode 0640: the reader
    of the directory may run as another user than the writer. Changing the
    owner needs privilege; without it the file keeps the writer's."""
    st = os.stat(folder)
    with contextlib.suppress(PermissionError):
        if (st.st_uid, st.st_gid) != (os.getuid(), os.getgid()):
            os.chown(path, st.st_uid, st.st_gid)
    os.chmod(path, 0o640)


def _site_link(day=None):
    base = config.SITE_BASE_URL
    if not base:
        return None
    return f"{base}/{day}.html" if day else f"{base}/"


# ---------------------------------------------------------------------------
# The end-of-day events. Wording lives here so the worker's hooks stay one
# line each. A failing night sends at most: the first failed attempt, the
# halt, and the publication once it recovers.
# ---------------------------------------------------------------------------

def _event(event, day, subject, detail, facts, link=None):
    """One end-of-day notice: the subject names the day and the event; the
    title, for the body, also names the project."""
    return emit(event, day, f"FAPD {subject}", detail, facts, subject=subject, link=link)


def finalize_failed(day, attempts, max_attempts, exit_code):
    """The finalizer failed: a notice on the first attempt and on the halt,
    none for the retries between (they would repeat the first)."""
    if attempts >= max_attempts:
        return _event(
            "eod.halted", day, f"{day}: digest halted after {attempts} failed attempts",
            "The day is not published and will not be retried. Fix the cause,"
            f" then run scripts/collect.py --finalize {day} in the backend.",
            {"Attempts": f"{attempts} of {max_attempts}", "Last exit code": exit_code})
    if attempts == 1:
        return _event(
            "eod.failed", day, f"{day}: end-of-day run failed, digest not yet published",
            "The finalizer will try again on the next end-of-day cycle. The"
            " backend log names the stage and the reason.",
            {"Attempt": f"1 of {max_attempts}", "Exit code": exit_code})
    return None


def evidence_push_failed(day, attempts, max_attempts, exit_code):
    """The digest is live but its evidence commit did not reach the
    repository: a notice on the first failure and on the halt."""
    if attempts >= max_attempts:
        return _event(
            "eod.push_halted", day, f"{day}: repository push halted after {attempts} attempts",
            "The digest is live on the site but not in the repository, and"
            " the push will not be retried. Fix the cause, then run"
            " deploy/vps/scripts/evidence-commit.sh in the backend.",
            {"Attempts": f"{attempts} of {max_attempts}", "Last exit code": exit_code})
    if attempts == 1:
        return _event(
            "eod.push_failed", day, f"{day}: digest is live but not yet in the repository",
            "The evidence push failed and will be retried on idle cycles.",
            {"Attempt": f"1 of {max_attempts}", "Exit code": exit_code})
    return None


def published(day, *, pushed, failed_attempts=0, failed_pushes=0):
    """The day is finalized (and pushed, when pushes are on). Sent every
    night; names a recovery when earlier attempts had failed."""
    subject = f"{day}: digest published"
    if failed_attempts:
        subject += f" after {failed_attempts} failed attempt(s)"
    elif failed_pushes:
        subject += f", repository push recovered after {failed_pushes} failure(s)"
    facts = {"Repository": "pushed" if pushed else "push not configured"}
    detail = "Finalized and published." + (" Evidence is in the repository." if pushed else "")
    return _event("eod.published", day, subject, detail, facts, link=_site_link(day))
