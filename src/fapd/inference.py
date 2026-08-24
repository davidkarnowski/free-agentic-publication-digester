"""Per-day inference status — which model layers ran (GUIDE §6 r15).

Zero-LLM. The finalizing run records, for the publication day it
freezes, whether each model layer ran, was skipped, or failed, plus the
backend and the concrete models that produced prose. The digest renders
ONE neutral line from this record (its "Inference" header row) and
nothing else: the operator ruled (2026-08-24) that the published digest
never states the cause of a missing layer — provider not configured,
authentication refused, quota exhausted — because that is operational
detail, recorded in the day's provenance manifest and operations report,
not editorial content. This module therefore stores the mechanical
facts and exposes exactly the wording the digest may use.

Write-once per finalize: the finalizing run is the writer, and a later
finalize of the same day overwrites — the last finalize is the frozen
state (docs/schema.md, `day_inference`).
"""

import datetime as dt
import json

#: The model layers, in pipeline order (run_pipeline.stage_analyze).
LAYERS = ("map", "plain", "compose", "sections", "tags")

#: Reader-facing names for the layers — the only per-layer words the
#: digest may carry (no reasons, no error text).
LAYER_NAMES = {
    "map": "item summaries",
    "plain": "plain-language lines",
    "compose": "Day in Review",
    "sections": "section quick-reads",
    "tags": "discovery tags",
}

#: The whole disclosure for a day without inference — verbatim, and the
#: only sentence the digest uses for it (operator ruling 2026-08-24).
NO_INFERENCE = (
    "No inference was available for this publication day. All content"
    " is source-derived or mechanically constructed."
)


def _utc_now():
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def record(conn, date, *, backend, models, layers):
    """Upsert the day's inference status and return it as `load` would.

    `layers` maps each name in LAYERS to "ran" | "skipped" | "failed";
    missing names default to "skipped" so a partial map never reads as
    a layer that ran. `models` is any iterable of resolved model names
    (deduplicated, sorted); `backend` may be None when no client was
    constructed at all."""
    status = {}
    for name in LAYERS:
        value = (layers or {}).get(name, "skipped")
        if value not in ("ran", "skipped", "failed"):
            raise ValueError(f"layer {name!r}: unknown status {value!r}")
        status[name] = value
    model_list = sorted({m for m in (models or ()) if m})
    available = any(v == "ran" for v in status.values())
    conn.execute(
        """
        INSERT INTO day_inference (date, available, backend, models, layers,
                                   recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (date) DO UPDATE SET
            available = excluded.available,
            backend = excluded.backend,
            models = excluded.models,
            layers = excluded.layers,
            recorded_at = excluded.recorded_at
        """,
        (date, 1 if available else 0, backend, ",".join(model_list),
         json.dumps(status, sort_keys=True), _utc_now()),
    )
    conn.commit()
    return {"available": available, "backend": backend,
            "models": model_list, "layers": status}


def load(conn, date):
    """The recorded status for `date`, or None when no finalize has
    recorded one (every digest before 2026-08-24, and any render of a
    day whose finalizing run predates the table)."""
    row = conn.execute(
        "SELECT available, backend, models, layers FROM day_inference"
        " WHERE date = ?",
        (date,),
    ).fetchone()
    if row is None:
        return None
    layers = json.loads(row["layers"] or "{}")
    return {
        "available": bool(row["available"]),
        "backend": row["backend"],
        "models": [m for m in (row["models"] or "").split(",") if m],
        "layers": {name: layers.get(name, "skipped") for name in LAYERS},
    }


def label(status):
    """The digest's Inference row text for a recorded status (or None).

    Three states, no others: no inference at all → NO_INFERENCE; every
    layer ran → the attribution GUIDE §6 r7 owes; some ran → the same
    attribution plus which layers are not available, by their reader-
    facing names. Never a reason."""
    if not status or not status.get("available"):
        return NO_INFERENCE
    layers = status.get("layers") or {}
    missing = [LAYER_NAMES[name] for name in LAYERS
               if layers.get(name, "skipped") != "ran"]
    attribution = status.get("backend") or "unrecorded"
    models = ", ".join(status.get("models") or ())
    if models:
        attribution += f"/{models}"
    if not missing:
        return f"model layers ran — {attribution}"
    return (f"model layers ran in part — {attribution}; not available:"
            f" {', '.join(missing)}")
