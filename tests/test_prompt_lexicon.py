"""GUIDE §2/§3a two-layer lexicon enforcement (review D8): every prose
prompt restates the COMPLETE banned-term list from config.BANNED_TERMS,
and the render-time gate compiles its regex from the same constant. Two
lists in two modules with no drift test was the root cause of the compose
model producing prose the gate then rejected — for a constraint it was
never given."""

from fapd import analyze, assess, compose, config, tags
from fapd.report import _BANNED_RE

PROMPTS = {
    "map preamble": analyze._PREAMBLE,
    "plain preamble": analyze._PLAIN_PREAMBLE,
    "compose day-in-review": compose._PROMPT,
    "compose section synopses": compose._SECTION_PROMPT,
    "section tags": tags._TAG_PROMPT,
    "source assessments": assess._ASSESS_PROMPT,
    "source descriptions": assess._DESC_PROMPT,
}


def test_every_prose_prompt_carries_the_full_banned_list():
    for name, prompt in PROMPTS.items():
        low = prompt.lower()
        missing = [t for t in config.BANNED_TERMS if t not in low]
        assert not missing, f"{name} prompt is missing banned terms: {missing}"


def test_no_prompt_ships_an_unsubstituted_placeholder():
    for name, prompt in PROMPTS.items():
        assert "{banned}" not in prompt, f"{name} prompt kept the placeholder"


def test_gate_regex_matches_every_canonical_term():
    for term in config.BANNED_TERMS:
        assert _BANNED_RE.search(term), f"gate regex misses {term!r}"
