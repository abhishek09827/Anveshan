import sqlite3
from typing import Any

from backend.db.database import insert_trace_batches
from backend.otlp.parser import parse_resource_spans
from backend.otlp.trace_summary import build_trace_batches

def ingest_payload(
    conn: sqlite3.Connection,
    payload: dict[str, Any],
) -> dict[str, int]:
    spans = parse_resource_spans(payload)
    batches = build_trace_batches(spans)

    insert_trace_batches(conn, batches)

    return {
        "traces_ingested": len(batches),
        "spans_ingested": len(spans),
    }

