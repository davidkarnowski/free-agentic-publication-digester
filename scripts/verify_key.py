"""One-request sanity check that the govinfo API key works.

Hits the `collections` service (a single cheap GET that lists all collection
codes) and prints the rate-limit headers so we can see our remaining budget.

Usage: uv run python scripts/verify_key.py
"""

import sys

import requests

from info_intel import config


def main() -> int:
    resp = requests.get(
        f"{config.API_BASE}/collections",
        params={"api_key": config.api_key()},
        headers={"User-Agent": config.USER_AGENT},
        timeout=30,
    )
    print(f"HTTP {resp.status_code}")
    print(f"X-RateLimit-Limit:     {resp.headers.get('X-RateLimit-Limit')}")
    print(f"X-RateLimit-Remaining: {resp.headers.get('X-RateLimit-Remaining')}")
    if resp.status_code != 200:
        print(resp.text[:500])
        return 1

    collections = resp.json().get("collections", [])
    print(f"\nAPI key OK — {len(collections)} collections available. Of interest to us:")
    ours = {"CREC", "BILLS", "FR", "PLAW", "CHRG", "CRPT", "DCPD"}
    for c in collections:
        if c.get("collectionCode") in ours:
            print(f"  {c['collectionCode']:6} {c.get('collectionName', '')}"
                  f"  (packages: {c.get('packageCount', '?')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
