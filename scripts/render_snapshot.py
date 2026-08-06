"""Render a digest from a database SNAPSHOT into a scratch directory —
the offline test bench for digest-pipeline changes.

Zero LLM calls, zero HTTP, zero writes to the repo, the canonical
digests, the site, or the snapshot's own rows: `report.render` is the
deterministic render stage, fed here by whatever summaries and compose
layers the snapshot already stores. Change pipeline code, re-run, and
diff two outputs to see exactly what the change does to a real day —
without waiting for tonight's EOD or touching production.

Typical loop (snapshot pulled per deploy/dev/scripts/dev-seed.sh's
VACUUM INTO method, e.g. into data/seeds/<date>/):

    uv run python scripts/render_snapshot.py \
        --db data/seeds/2026-08-06/fapd.db --date 2026-08-05 \
        --out /tmp/render-before
    # ...edit report.py / rules.py / compose display code...
    uv run python scripts/render_snapshot.py \
        --db data/seeds/2026-08-06/fapd.db --date 2026-08-05 \
        --out /tmp/render-after
    diff /tmp/render-{before,after}/2026-08-05.md

The snapshot is opened on a throwaway COPY so `db.connect`'s
self-migrating DDL and any future render-side bookkeeping can never
alter the seed — the same snapshot stays byte-identical across every
run, which is what makes before/after diffs trustworthy.
"""

import argparse
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", required=True, help="snapshot fapd.db path")
    ap.add_argument("--date", required=True, help="digest date YYYY-MM-DD")
    ap.add_argument("--out", required=True,
                    help="output directory (created; NOT digests/)")
    args = ap.parse_args()

    src = pathlib.Path(args.db)
    if not src.is_file():
        sys.exit(f"no such snapshot: {src}")
    out_dir = pathlib.Path(args.out)
    repo_digests = pathlib.Path(__file__).resolve().parents[1] / "digests"
    if out_dir.resolve() == repo_digests.resolve():
        sys.exit("refusing to write into the canonical digests/ directory")

    from fapd import db, report

    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "snapshot.db"
        shutil.copyfile(src, work)
        conn = db.connect(work)
        try:
            path = report.render(conn, args.date, out_dir=out_dir)
        finally:
            conn.close()
    print(f"rendered {args.date} from {src} -> {path}")
    print("compare against the canonical record with e.g.:")
    print(f"  diff digests/{args.date}.md {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
