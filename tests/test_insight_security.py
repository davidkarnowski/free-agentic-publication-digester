"""The security section of the insight report.

The interesting cases here are all failure cases. A security section
that renders beautifully when the sweep is healthy and silently renders
*nothing* when the sweep stopped running is worse than no section at
all: it reads as "no findings" when it means "no data". Every test
below exists because that distinction has to survive a refactor.
"""

import datetime as dt
import json

import pytest

from fapd import config, insight

UTC = dt.UTC


def _sweep(**over):
    base = {
        "generated_utc": dt.datetime.now(UTC).isoformat(timespec="seconds"),
        "window_hours": 24,
        "thresholds": {"tls_warn_days": 21, "retention_min_days": 60},
        "probing": {"events": 51, "distinct_ips": 20, "by_family": {"wordpress": 33},
                    "findings": []},
        "refusals": {"by_status": {"404": 12}, "probes_served_2xx": 0},
        "jails": [{"jail": "nginx-ai-probe", "currently_banned": 0,
                   "total_banned": 0, "has_chain": 1}],
        "auth": {"failed_ssh": 3, "failed_ssh_distinct_ips": 1,
                 "failed_ssh_alltime": 54, "failed_ssh_alltime_distinct_ips": 29,
                 "usernames_tried": "postgres", "accepted_from": "198.51.100.7"},
        "patch": {"host_security_pending": 0, "base_images": []},
        "integrity": {"containers": "fapd-web", "unhealthy": 0,
                      "published_ports_non_edge": "", "mcp_hardening": "true|[ALL]|10001:10001",
                      "unexpected_listeners": ""},
        "tls": [{"cert": "fapd.info", "days": 36}],
        "retention": [{"config": "fapd-mcp", "rotate_days": 60}],
        "stage_errors": [],
        "verdicts": [],
        "escalate": False,
    }
    base.update(over)
    return base


def _write(tmp_path, sweep):
    p = tmp_path / "security-sweep.json"
    p.write_text(json.dumps(sweep))
    return p


# --------------------------------------------------------------- reading

def test_missing_file_is_a_visible_problem_not_a_clean_result(tmp_path):
    sweep, problem = insight.read_sweep(tmp_path / "nope.json")
    assert sweep is None
    assert "did not run" in problem


def test_malformed_file_is_reported_not_swallowed(tmp_path):
    p = tmp_path / "security-sweep.json"
    p.write_text("{not json")
    sweep, problem = insight.read_sweep(p)
    assert sweep is None
    assert "unreadable" in problem


def test_a_stale_sweep_is_treated_as_did_not_run(tmp_path):
    """The F-021 shape: a file that stopped being written would otherwise
    report a clean bill of health forever."""
    old = dt.datetime.now(UTC) - dt.timedelta(hours=config.SECURITY_SWEEP_STALE_HOURS + 2)
    p = _write(tmp_path, _sweep(generated_utc=old.isoformat(timespec="seconds")))
    sweep, problem = insight.read_sweep(p)
    assert sweep is None
    assert "DID NOT RUN" in problem


def test_a_fresh_sweep_reads_clean(tmp_path):
    p = _write(tmp_path, _sweep())
    sweep, problem = insight.read_sweep(p)
    assert problem is None
    assert sweep["probing"]["events"] == 51


def test_missing_timestamp_is_refused(tmp_path):
    s = _sweep()
    del s["generated_utc"]
    sweep, problem = insight.read_sweep(_write(tmp_path, s))
    assert sweep is None
    assert "generated_utc" in problem


# ------------------------------------------------------------- rendering

def test_unavailable_sweep_renders_loudly(tmp_path):
    out = "\n".join(insight.render_security(None, problem="the host timer did not run"))
    assert "unavailable" in out
    assert "gap in the record" in out


def test_section_is_complete_without_inference():
    """GUIDE §6 r15 posture: the mechanical findings stand alone."""
    out = "\n".join(insight.render_security(_sweep(), summary=None))
    assert "no inference available" in out
    assert "probe requests | 51" in out
    assert "No verdict tripped a threshold." in out


def test_escalation_leads_the_section():
    s = _sweep(
        escalate=True,
        verdicts=[{"key": "intrusion.response", "severity": "critical",
                   "detail": "2 probe-shaped request(s) received a 2xx response",
                   "escalate": True}],
        refusals={"by_status": {}, "probes_served_2xx": 2})
    out = "\n".join(insight.render_security(s))
    assert out.index("ESCALATE") < out.index("| measure | value |")
    assert "**2**" in out  # the served-2xx count is bolded because it matters


def test_window_and_alltime_ssh_counts_are_labeled_separately():
    """The first real render reported a day with zero failed logins as
    having 54, by counting all of btmp under a 24h heading."""
    out = "\n".join(insight.render_security(_sweep()))
    assert "failed SSH attempts (window) | 3 from 1 address(es)" in out
    assert "failed SSH attempts (retained) | 54 from 29 address(es)" in out


def test_thresholds_are_stated_with_the_verdicts():
    """A verdict without its threshold is unauditable six months later."""
    out = "\n".join(insight.render_security(_sweep()))
    assert "tls_warn_days=21" in out


def test_stage_errors_are_disclosed_as_missing_not_zero():
    out = "\n".join(insight.render_security(_sweep(stage_errors=["campaign-detect failed"])))
    assert "missing, not zero" in out
    assert "campaign-detect failed" in out


def test_summary_is_labeled_as_model_output_and_decides_nothing():
    out = "\n".join(insight.render_security(_sweep(), summary="Nothing to act on today."))
    assert "Model summary" in out
    assert "decides nothing" in out
    assert "Nothing to act on today." in out


# ------------------------------------------------------------ the call

class _StubLLM:
    def __init__(self, text="all quiet", exc=None):
        self.text, self.exc, self.calls = text, exc, []

    def complete(self, prompt, **kw):
        self.calls.append((prompt, kw))
        if self.exc:
            raise self.exc
        return {"text": self.text}


def test_summary_call_is_ledgered_under_its_own_purpose():
    llm = _StubLLM()
    insight.summarize_security(llm, _sweep())
    assert llm.calls[0][1]["purpose"] == "security:summary"


def test_summary_payload_is_trimmed_of_unbounded_fields():
    """Address lists and path samples are evidence for a human reading
    the JSON, not context a summariser needs — and they are the only
    fields in the file with no natural bound."""
    s = _sweep(probing={
        "events": 9, "distinct_ips": 2, "by_family": {},
        "findings": [{"kind": "by-sweep", "signature": "x",
                      "sample_paths": ["/a"] * 40, "ips": [f"10.0.0.{i}" for i in range(30)]}],
    })
    llm = _StubLLM()
    insight.summarize_security(llm, s)
    sent = llm.calls[0][0]
    assert "sample_paths" not in sent
    assert "10.0.0.20" not in sent          # truncated to five
    # and the original is untouched — trimming must not mutate the record
    assert len(s["probing"]["findings"][0]["sample_paths"]) == 40


def test_accepted_from_is_not_sent_to_the_model():
    llm = _StubLLM()
    insight.summarize_security(llm, _sweep())
    assert "198.51.100.7" not in llm.calls[0][0]


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_model_reply_becomes_none(text):
    assert insight.summarize_security(_StubLLM(text), _sweep()) is None
