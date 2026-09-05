"""Tier 1 of the verification protocol (docs/accessibility-doctrine.md §6).

These are the structural invariants a future change is most likely to
break silently, swept across every built page class rather than asserted
on one page. GUIDE §2a rule 12 makes them part of a surface being done;
without them the doctrine is decoration.

What these tests do NOT do is claim conformance. They are inspection
made executable — tier 1. Announcement, focus tracking under
magnification, voice-control naming and switch navigation are tier 3 and
are performed against real assistive technology when it is available; no
result here is ever reported as that.
"""

import re
from itertools import pairwise

import pytest

from fapd import publish

DIGEST = """# Daily Digest — {date}

| Field | Value |
|---|---|
| Digest date | {date} |

## Day in Review

A quiet day on the federal record.

## 1. Congressional Record

Nothing to report.
"""


@pytest.fixture
def site(tmp_path):
    """A built site spanning two years, so the per-year archive pages
    and the cross-year links are exercised rather than assumed."""
    digests = tmp_path / "digests"
    digests.mkdir()
    for date in ("2025-12-30", "2026-07-01", "2026-07-02", "2026-07-04"):
        (digests / f"{date}.md").write_text(DIGEST.format(date=date),
                                            encoding="utf-8")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    return out


def _pages(out):
    """Every built HTML page, as (relative name, text)."""
    return [(str(p.relative_to(out)), p.read_text(encoding="utf-8"))
            for p in sorted(out.rglob("*.html"))]


# ---------------------------------------------------------------------------
# The no-script posture (GUIDE §2a rules 3-5; code-standards r10)
# ---------------------------------------------------------------------------

_HANDLER_RE = re.compile(r"\son[a-z]+=", re.IGNORECASE)


def test_only_the_live_page_carries_a_script(site):
    """GUIDE §2a rule 3. This is an access rule and a security rule at
    once: a control that needs script fails for some assistive
    technology, and a page with no script has nothing to inject."""
    for name, text in _pages(site):
        if name == "today.html":
            continue
        assert "<script" not in text.lower(), f"script on {name}"


def test_no_page_carries_an_inline_event_handler(site):
    """"One script" also means no `onclick=` — the 2026-08-18 audio
    players shipped handlers and every `<script`-counting audit stayed
    green (doc-audit item 2)."""
    for name, text in _pages(site):
        assert not _HANDLER_RE.search(text), f"inline handler on {name}"


_SUBRESOURCE_RE = re.compile(
    r"""<(?:script[^>]*\ssrc|link[^>]*\shref|img[^>]*\ssrc|iframe[^>]*\ssrc)"""
    r"""\s*=\s*["'](?P<url>[^"']+)["']""", re.IGNORECASE)


def test_no_page_loads_a_third_party_resource(site):
    """GUIDE §2a rule 4. Outbound *links* to official sources are the
    product; a loaded subresource is a dependency, and we have none —
    no fonts, no CDN, no analytics, no embedded player."""
    for name, text in _pages(site):
        for match in _SUBRESOURCE_RE.finditer(text):
            url = match.group("url")
            assert not url.lower().startswith(("http://", "https://", "//")), (
                f"{name} loads an external subresource: {url}")


# ---------------------------------------------------------------------------
# Structure (SC 1.3.1, 2.4.1, 2.4.6)
# ---------------------------------------------------------------------------

_H_RE = re.compile(r"<h([1-6])[\s>]", re.IGNORECASE)


def test_every_page_has_exactly_one_h1(site):
    for name, text in _pages(site):
        levels = [int(m) for m in _H_RE.findall(text)]
        assert levels.count(1) == 1, f"{name} has {levels.count(1)} h1"


def test_heading_levels_never_skip(site):
    """A jump from h2 to h4 breaks heading navigation, which is how a
    screen reader user moves through a long page."""
    for name, text in _pages(site):
        levels = [int(m) for m in _H_RE.findall(text)]
        for previous, current in pairwise(levels):
            assert current <= previous + 1, (
                f"{name}: h{previous} followed by h{current}")


def test_a_skip_link_precedes_the_main_content(site):
    """A11Y-02 / SC 2.4.1."""
    for name, text in _pages(site):
        assert 'class="skip-link"' in text, f"{name} has no skip link"
        assert text.index('class="skip-link"') < text.index('id="main"'), (
            f"{name}: skip link does not precede main")


def test_no_page_uses_a_positive_tabindex(site):
    """A positive tabindex reorders the tab sequence away from document
    order. `-1` (a programmatic focus target) and `0` are fine."""
    for name, text in _pages(site):
        for value in re.findall(r'tabindex\s*=\s*["\'](-?\d+)["\']', text):
            assert int(value) <= 0, f"{name}: tabindex={value}"


def test_tables_keep_their_semantics(site):
    """A11Y-03: a table is announced as a table — scoped headers, and a
    caption or a labelled region naming it."""
    for name, text in _pages(site):
        for table in re.findall(r"<table[^>]*>.*?</table>", text, re.DOTALL):
            if "<th" in table:
                assert "scope=" in table, f"{name}: <th> without scope"


def test_the_stylesheet_declares_forced_colors_behaviour(site):
    """When custom colours are discarded, control boundaries and state
    markers must still exist."""
    css = (site / "style.css").read_text(encoding="utf-8")
    assert "@media (forced-colors: active)" in css
    assert ".cal a { border: 1px solid LinkText; }" in css


# ---------------------------------------------------------------------------
# Computed values (doctrine §4) — the arithmetic, executable
# ---------------------------------------------------------------------------

def _luminance(hex_color):
    channels = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255
                for i in (0, 2, 4)]
    channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                for c in channels]
    return (0.2126 * channels[0] + 0.7152 * channels[1]
            + 0.0722 * channels[2])


def _contrast(foreground, background):
    high, low = sorted((_luminance(foreground), _luminance(background)),
                       reverse=True)
    return (high + 0.05) / (low + 0.05)


def _token_values(name):
    """Every declared value of a custom property, in source order —
    which is light palette first, then the dark override."""
    return re.findall(rf"--{name}:\s*(#[0-9a-fA-F]{{6}})", publish._STYLE)


def test_the_control_boundary_token_meets_non_text_contrast():
    """SC 1.4.11, in both palettes. This is the check that caught the
    archive's first draft: `--border` is 1.34:1 against the page — right
    for a dividing rule, and not a control boundary."""
    backgrounds = _token_values("bg")
    borders = _token_values("control-border")
    assert len(backgrounds) == len(borders) == 2, "palette count changed"
    for background, border in zip(backgrounds, borders):
        ratio = _contrast(border, background)
        assert ratio >= 3.0, f"{border} on {background} is {ratio:.2f}:1"


def test_the_decorative_border_token_is_not_used_for_calendar_cells():
    """The trap, pinned: a day cell is a control boundary, so it may not
    fall back to the decorative rule colour."""
    cell_rule = re.search(r"\.cal a \{[^}]*\}", publish._STYLE).group()
    assert "var(--control-border)" in cell_rule
    assert "var(--border)" not in cell_rule


def test_calendar_day_targets_are_fluid_and_never_overflow():
    """Doctrine §4.2. The height is a hard 44px (SC 2.5.5 Enhanced); the
    width is a seventh of the viewport, so the grid fits any screen by
    construction rather than at a guessed breakpoint. A11Y-23 was the
    fixed-pixel version scrolling a phone sideways."""
    rule = re.search(r"\.cal a, \.cal \.cal-none \{[^}]*\}",
                     publish._STYLE).group()
    assert "min-height: 44px" in rule
    assert "width: 100%" in rule
    # A fixed min-width is what made the grid unable to fit a phone.
    assert "min-width: 0" in rule and "min-width: 44px" not in rule
    table = re.search(r"table\.cal \{[^}]*\}", publish._STYLE).group()
    assert "width: 100%" in table and "table-layout: fixed" in table


def test_calendar_cells_do_not_inherit_the_data_table_styling():
    """A11Y-23's cause: the global `th, td` rule put 0.7rem of side
    padding and a border on every day cell, so seven columns wanted
    ~500px. The reset must also outrank the zebra-stripe selector."""
    reset = re.search(
        r"\.cal th, \.cal td, \.cal tr:nth-child\(even\) td \{[^}]*\}",
        publish._STYLE)
    assert reset, "the calendar does not reset the data-table cell styling"
    assert "padding: 0" in reset.group() and "border: 0" in reset.group()


def test_the_calendar_reflows_to_a_320px_viewport():
    """SC 1.4.10, computed from the declared values rather than assumed:
    seven columns plus their spacing, inside the page's own padding,
    must leave a cell wider than the 24px AA target floor."""
    side_padding = float(re.search(r"main \{[^}]*padding:\s*[\d.]+rem\s+([\d.]+)rem",
                                   publish._STYLE).group(1)) * 16
    spacing = float(re.search(r"table\.cal \{[^}]*border-spacing:\s*(\d+)px",
                              publish._STYLE, re.DOTALL).group(1))
    content = 320 - 2 * side_padding
    cell = (content - 8 * spacing) / 7
    assert cell >= 24, f"{cell:.1f}px per cell at a 320px viewport"


# ---------------------------------------------------------------------------
# The archive (GUIDE §2a; doctrine §1 rung 1)
# ---------------------------------------------------------------------------

_CAL_LINK_RE = re.compile(
    r'<a class="cal-day[^"]*" href="(?P<href>[^"]+)">'
    r'(?P<visible>\d+)<span class="vh">(?P<spoken> — digest for [^<]+)</span>')


def test_every_published_day_is_reachable_from_the_archive_exactly_once(site):
    """The index no longer enumerates the record, so the archive must —
    completely, and without offering two URLs for the same calendar."""
    dates = {"2025-12-30", "2026-07-01", "2026-07-02", "2026-07-04"}
    found = []
    for name, text in _pages(site):
        if name != "archive.html" and not name.startswith("archive/"):
            continue
        for match in _CAL_LINK_RE.finditer(text):
            found.append(match.group("href").rsplit("/", 1)[-1][:-5])
    assert sorted(found) == sorted(dates), found


def test_a_day_with_no_digest_is_not_a_link(site):
    """Nothing focusable that does nothing (doctrine §2)."""
    text = (site / "archive.html").read_text(encoding="utf-8")
    assert '<span class="cal-none' in text
    # 2026-07-03 sits between two published days and has no digest.
    assert 'href="2026-07-03.html"' not in text


def test_a_calendar_day_name_begins_with_its_visible_label(site):
    """SC 2.5.3 Label in Name — a voice-control user says "click 4",
    so the accessible name must start with the 4 they can see."""
    text = (site / "archive.html").read_text(encoding="utf-8")
    matches = list(_CAL_LINK_RE.finditer(text))
    assert matches, "no calendar day links found"
    for match in matches:
        assert match.group("spoken").startswith(" — digest for "), match
        day = match.group("href").rsplit("/", 1)[-1][8:10].lstrip("0")
        assert match.group("visible") == day


def test_reduced_publishing_days_state_their_reason_in_the_name(site):
    """Never by colour alone (SC 1.4.1): the dashed cell also says why.
    2026-07-04 is Independence Day and a Saturday."""
    text = (site / "archive.html").read_text(encoding="utf-8")
    assert "not a federal business day" in text
    assert "cal-closed" in text


def test_the_archive_carries_a_skip_link_past_the_calendars(site):
    """Twelve calendars is a long run of links to walk by keyboard."""
    text = (site / "archive.html").read_text(encoding="utf-8")
    assert 'href="#archive-end"' in text
    assert 'id="archive-end"' in text


def test_month_links_point_at_anchors_that_exist(site):
    """The index's plain-text month list is the fast path to a month;
    a fragment that resolves to nothing is a dead control."""
    index = (site / "index.html").read_text(encoding="utf-8")
    archive = (site / "archive.html").read_text(encoding="utf-8")
    year_pages = {p.name[:4]: p.read_text(encoding="utf-8")
                  for p in (site / "archive").glob("*.html")}
    links = re.findall(r'<li><a href="(archive[^"]*)#(m-\d{4}-\d{2})"', index)
    assert links, "no month links on the index"
    for href, anchor in links:
        target = archive if href == "archive.html" else year_pages[href[8:12]]
        assert f'id="{anchor}"' in target, f"{href}#{anchor} resolves to nothing"


def test_the_index_is_bounded_and_links_the_archive(site):
    """The failure this replaced: one card per digest, forever."""
    index = (site / "index.html").read_text(encoding="utf-8")
    cards = re.findall(r'<li><a class="date" href="(\d{4}-\d{2}-\d{2})\.html"',
                       index)
    assert len(cards) <= publish.RECENT_DIGEST_DAYS
    assert cards == sorted(cards, reverse=True), "recent list is not newest-first"
    assert 'href="archive.html"' in index


def test_the_archive_reaches_the_machine_surfaces(site):
    """Trimming the index removed a crawl path; the enumerating surfaces
    stay complete, and the sitemap lists the archive pages."""
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    assert "/archive.html" in sitemap
    assert "/archive/2025.html" in sitemap
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    assert "/archive.html" in llms
    assert "NOT a complete enumeration" in llms


def test_the_archive_renders_only_months_that_have_digests(site):
    """Operator's call, 2026-09-05: an empty month grid is not
    disclosure. The fixture publishes in December 2025 and July 2026, so
    neither year may render a month it has no digests for."""
    archive = (site / "archive.html").read_text(encoding="utf-8")
    assert 'id="m-2026-07"' in archive
    for month in ("01", "02", "03", "04", "05", "06", "08", "12"):
        assert f'id="m-2026-{month}"' not in archive, month
    year_2025 = (site / "archive" / "2025.html").read_text(encoding="utf-8")
    assert 'id="m-2025-12"' in year_2025
    assert 'id="m-2025-11"' not in year_2025
    # A gap of DAYS inside a month we do cover still renders: 2026-07-03
    # sits between two published days and is shown as "no digest".
    assert 'class="cal-none' in archive
