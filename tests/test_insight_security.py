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


def test_served_probes_are_attributed_and_app_fallbacks_shown():
    """2026-09-27: the sweep attributes a served probe to its site and counts
    a single-page app's index-page answers apart (a single-page-app false
    positive). Both render; neither hides the other."""
    sweep = {"window_hours": 24, "generated_utc": "t", "verdicts": [],
             "probing": {}, "auth": {},
             "refusals": {"by_status": {}, "probes_served_2xx": 1,
                          "probes_served_2xx_by_host": {"other.example": 1},
                          "probes_app_fallback": 76}}
    text = "\n".join(insight.render_security(sweep))
    assert "**1** (other.example: 1)" in text
    assert "| probe paths answered by an app's own index page | 76 |" in text


# ------------------------------------------- triage: new, standing, cleared
#
# Added 2026-10-07: night after night the report listed the same "high"
# verdicts as if they were news, so a real one read like the noise.

def _v(key, severity, detail="d"):
    return {"key": key, "severity": severity, "detail": detail,
            "escalate": severity == "critical"}


def _rec(*keys, sev="high", tags=()):
    return {"verdicts": {k: sev for k in keys}, "accepted_tags": list(tags), "by_status": {}}


def test_a_new_high_is_action_and_an_old_one_is_standing():
    s = _sweep(verdicts=[_v("patch.host", "high"), _v("jail.chainless", "high")])
    history = [("2026-10-05", _rec("jail.chainless")), ("2026-10-04", _rec("jail.chainless")),
               ("2026-10-03", _rec("jail.chainless"))]
    t = insight.triage("2026-10-06", s, history)
    assert [i["key"] for i in t["act"]] == ["patch.host"]
    assert [(i["key"], i["nights"]) for i in t["standing"]] == [("jail.chainless", 4)]


def test_a_gap_in_the_records_restarts_the_count():
    s = _sweep(verdicts=[_v("jail.chainless", "high")])
    history = [("2026-10-05", _rec("jail.chainless")), ("2026-10-03", _rec("jail.chainless"))]
    t = insight.triage("2026-10-06", s, history)
    assert t["standing"][0]["nights"] == 2


def test_critical_is_always_action_even_when_standing():
    s = _sweep(verdicts=[_v("intrusion.ports", "critical")])
    t = insight.triage("2026-10-06", s, [("2026-10-05", _rec("intrusion.ports", sev="critical"))])
    assert [i["key"] for i in t["act"]] == ["intrusion.ports"]


def test_low_is_recorded_and_disappearances_are_cleared():
    s = _sweep(verdicts=[_v("campaign.refused", "low")])
    t = insight.triage("2026-10-06", s, [("2026-10-05", _rec("campaign.active", "patch.host"))])
    assert [i["key"] for i in t["recorded"]] == ["campaign.refused"]
    assert t["cleared"] == ["campaign.active", "patch.host"]
    assert t["act"] == [] and t["standing"] == []


def test_a_login_from_an_unseen_address_is_counted_not_printed():
    s = _sweep()  # accepted_from 198.51.100.7
    old = insight._addr_tag("203.0.113.9")
    week = [(f"2026-09-{d:02d}", _rec(tags=[old])) for d in range(30, 23, -1)]
    t = insight.triage("2026-10-01", s, week)
    assert t["new_login_addresses"] == 1
    out = "\n".join(insight.render_action_today(t))
    assert "not seen in the previous 7 night" in out and "198.51.100.7" not in out
    seen = insight._addr_tag("198.51.100.7")
    assert insight.triage("2026-10-01", s, week[:-1] + [("2026-09-24", _rec(tags=[seen]))])[
        "new_login_addresses"] == 0
    # fewer than a week of records: too little to call anything new
    assert insight.triage("2026-10-01", s, week[:3])["new_login_addresses"] == 0


def test_action_today_says_plainly_when_nothing_is_new():
    s = _sweep(verdicts=[_v("patch.base_age", "medium", "python:3.12-slim is 18d old")])
    t = insight.triage("2026-10-06", s, [("2026-10-05", _rec("patch.base_age", sev="medium"))])
    out = "\n".join(insight.render_action_today(t))
    assert "**Nothing new needs action.**" in out
    assert "| `patch.base_age` | medium | 2 |" in out


def test_action_today_leads_with_an_unavailable_sweep():
    out = "\n".join(insight.render_action_today({}, problem="no sweep file"))
    assert "**Act: the security sweep did not run" in out


def test_who_acts_uses_the_longest_prefix():
    assert insight._who_acts("integrity.auth_changed").startswith("operator: confirm")
    assert insight._who_acts("jail.chainless") == "edge configuration"
    assert insight._who_acts("something.new") == "operator"


def test_history_reads_earlier_nights_newest_first_and_skips_bad_files(tmp_path):
    for day, keys in (("2026-10-03", ["a"]), ("2026-10-05", ["b"]), ("2026-10-06", ["c"])):
        insight.save_sweep_record(tmp_path, day, _sweep(verdicts=[_v(k, "high") for k in keys]))
    (tmp_path / "security-2026-10-04.record.json").write_text("{not json")
    hist = insight.load_history(tmp_path, "2026-10-06")
    assert [d for d, _ in hist] == ["2026-10-05", "2026-10-03"]
    assert hist[0][1]["verdicts"] == {"b": "high"}


def test_the_record_keeps_no_address():
    rec = json.dumps(insight.sweep_record(_sweep()))
    assert "198.51.100.7" not in rec


# --------------------------------------------- the table and the counts

def test_campaign_findings_are_counted_by_kind():
    s = _sweep(probing={"events": 9, "distinct_ips": 2, "by_family": {},
                        "findings": [{"kind": "by-target"}, {"kind": "by-agent"}]})
    out = "\n".join(insight.render_security(s))
    assert "| correlated campaign findings | 2 (by-agent 1, by-target 1) |" in out


def test_jail_table_names_chains_and_tells_missing_from_not_yet():
    s = _sweep(jails=[
        {"jail": "manual-bans", "currently_banned": 0, "total_banned": 1, "has_chain": 1,
         "chains": "manual-host,manual-web", "missing_chains": ""},
        {"jail": "nginx-botsearch", "currently_banned": 0, "total_banned": 0, "has_chain": 0},
        {"jail": "broken", "currently_banned": 2, "total_banned": 5, "has_chain": 0,
         "missing_chains": "broken"}])
    out = "\n".join(insight.render_security(s))
    assert "| manual-bans | 0 | 1 | manual-host,manual-web |" in out
    assert "| nginx-botsearch | 0 | 0 | none yet (no bans) |" in out
    assert "| broken | 2 | 5 | **missing: broken** |" in out


def test_new_sweep_fields_render_and_old_sweeps_do_not_break():
    s = _sweep(host={"disk_pct": 70, "reboot_required": False},
               edge_errors={"files": 2, "by_level": {"warn": 90, "crit": 1},
                            "buffered_to_temp_file": {"upstream_response": 81, "client_body": 9}},
               refusals={"by_status": {"404": 12, "413": 3}, "probes_served_2xx": 0})
    s["auth"].update(accepted_users="operator", password_logins=0)
    s["integrity"].update(fingerprints={"/etc/passwd": "ab"}, fingerprint_baseline=True)
    out = "\n".join(insight.render_security(s))
    for row in ("| root filesystem used | 70% |", "| reboot required | no |",
                "| SSH password logins | 0 |", "1, baseline recorded",
                "| edge error log, severe lines (crit/alert/emerg) | 1 |",
                "| 81 / 9 |", "| edge refusals by status | 404: 12, 413: 3 |"):
        assert row in out, row
    assert "root filesystem" not in "\n".join(insight.render_security(_sweep()))


# --------------------------------------------- grounding the model summary

#: The shape of a v1 summary (2026-10-06): a provider named after a colon.
_V1_SUMMARY_2026_10_06 = (
    "Nothing requires action today. The probing seen is refused: Examplenet-hosted "
    "probes are getting 404, not 2xx.")


def test_the_v1_summary_would_be_withheld_for_naming_a_provider():
    s = _sweep(probing={"events": 9, "distinct_ips": 4, "by_family": {"wordpress": 9},
                        "findings": [{"kind": "by-target", "statuses": {"404": 9}}]})
    assert "Examplenet-hosted" in insight.ungrounded(_V1_SUMMARY_2026_10_06, s)


def test_a_grounded_summary_passes_and_numbers_are_checked():
    s = _sweep(verdicts=[_v("patch.base_age", "medium", "python:3.12-slim is 18d old")])
    t = insight.triage("2026-10-06", s, [])
    ok = "Nothing new needs action. The base image python:3.12-slim is 18d old, past its threshold."
    assert insight.ungrounded(ok, s, t) == ""
    assert insight.ungrounded("Nothing new. 19 probes landed.", s, t) == "19"
