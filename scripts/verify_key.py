"""One-request sanity check that the govinfo API key and client work.

Hits the `collections` service through the rate-limited client, so it also
exercises pacing, budget accounting, and the fetch log.

Usage: uv run python scripts/verify_key.py
"""

import sys

from fapd import logging_setup
from fapd.client import GovinfoClient


def main() -> int:
    logging_setup.setup(verbose=True)
    with GovinfoClient() as client:
        resp = client.get("collections")
        print(f"HTTP {resp.status_code}")
        print(f"X-RateLimit-Limit:     {resp.headers.get('X-RateLimit-Limit')}")
        print(f"X-RateLimit-Remaining: {resp.headers.get('X-RateLimit-Remaining')}")

        collections = resp.json().get("collections", [])
        print(f"\nAPI key OK — {len(collections)} collections available. Of interest to us:")
        ours = {"CREC", "BILLS", "FR", "PLAW", "CHRG", "CRPT", "DCPD"}
        for c in collections:
            if c.get("collectionCode") in ours:
                print(f"  {c['collectionCode']:6} {c.get('collectionName', '')}"
                      f"  (packages: {c.get('packageCount', '?')})")

        print(f"\nRequests logged today (UTC): {client.requests_today()}"
              f" / daily budget per GUIDE.md §4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
