"""Build the static HTML site from the canonical Markdown digests.

Usage: uv run python scripts/build_site.py

Derived output (GUIDE §5): zero LLM calls, zero network; safe to re-run
any time. Output: site/ (index + one page per digest + copied assets).
"""

import sys

from fapd.publish import build_site


def main() -> int:
    stats = build_site()
    print(
        f"site built: {stats['pages']} digest page(s) + index,"
        f" {stats['assets']} asset(s) -> {stats['out_dir']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
