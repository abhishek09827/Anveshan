1. AI agents fail silently. Logs show success but the output is wrong. Existing tools either show you what happened (tracing) or measure quality (evaluation), but not both in one local-first tool. Lets ingests OTLP traces from any AI framework, visualizes the full decision graph, and runs automated evaluation - hallucination detection, compliance checks, cost tracking - so developers catch failures that logs miss, without sending data to the cloud.

2. Span Emission Order Discrepancy:
   - Empirical observation: In nested tracing (`Root` -> `Thinking` -> `Tool`), console exporter prints child spans (`Tool`) first and root spans (`Root`) last.
   - Cause: OpenTelemetry exports spans on completion (`span.end()`). Innermost execution contexts resolve first.
   - Architectural Implication: Ingestion & graph building logic cannot assume chronological arrival. Graph reconstruction must decouple arrival sequence from temporal execution sequence using `trace_id`, `span_id`, `parent_id`, and `start_time`.

3. ScopeSpans Boundary & Parent-Child Continuity:
   - Empirical observation: The OTel Collector outputs spans separated into `ScopeSpans` arrays (e.g. `ScopeSpans #0` for `anveshan.manual.tracer` and `ScopeSpans #1` for `opentelemetry.instrumentation.fastapi`).
   - Key Finding: Parent-child pointers cross scope boundaries seamlessly (`otlp_parent_span` in Scope #0 has `parent_id: 23c44cd5cbd5e0e4` which resolves to `GET /otlp-trace` in Scope #1).
   - Architectural Implication: Anveshan's ingestion parser must flatten or globally index all `ScopeSpans` by `span_id` within a `ResourceSpans` batch before resolving parent-child relationships.

4. Direct OTLP/HTTP Ingestion & Graph-Ready API Pivot:
   - Architectural Decision: Replaced file-watcher handoff with direct `otlphttp` exporter push from OTel Collector to FastAPI ingestion endpoint (`/api/v1/otlp/v1/traces`).
   - Rationale: Eliminates file tailing latency, partial line read errors, and disk I/O.
   - Graph Strategy: Server computes and returns `nodes` and `edges` (Graph-ready API) to keep UI rendering fast, with lazy-loading (`GET /spans/{span_id}`) for full prompts/attributes.

5. Phase 1 Ingestion Integrity Verification:
   - Verification Outcome: 2,113 spans across 100 ReAct agent traces successfully stored in SQLite with 0 orphaned child spans (`parent_span_id` validation query returned 0 missing parents).
   - Performance: Single-transaction batch insert (`executemany` with `PRAGMA journal_mode=WAL;`) achieved 100% data integrity with zero span loss.

6. Phase 2 Preflight — 2026-07-26:
   - The persistence layer is ready for a receiver: `backend/db/database.py` initializes the schema, enables WAL and foreign keys, and provides a batch writer.
   - The HTTP ingestion layer is not implemented yet: `backend/app.py` is empty, so no FastAPI route currently receives OTLP payloads.
   - The Collector is correctly configured to receive OTLP on HTTP `4318` and gRPC `4317`, but its only active trace exporter is `debug`; it cannot yet forward traces to Anveshan.
   - Decision: retain direct Collector-to-FastAPI OTLP/HTTP delivery. Do not reintroduce the obsolete JSON-file handoff shown in the previous planning diagram.

7. Phase 2 Receiver Foundation Verification — 2026-07-26:
   - `backend/app.py` now uses a FastAPI lifespan to initialize the SQLite schema before it accepts requests.
   - `GET /health` returned `200` with `{"status":"ok"}`, and the local database contains the expected `traces` and `spans` tables.
   - Follow-up decision: the current database path is relative to the process working directory. Make it an explicit application setting before running the Collector in a different execution environment, so traces cannot be written to an unintended SQLite file.

8. Phase 2 Incremental OTLP Write Risk — 2026-07-26:
   - `insert_trace_and_spans` currently uses `INSERT OR REPLACE` for the parent `traces` row.
   - In SQLite, `REPLACE` is implemented as a delete followed by an insert. With the `spans.trace_id` foreign key configured as `ON DELETE CASCADE`, replacing a trace can delete its already-persisted spans.
   - Decision: use a non-destructive UPSERT for trace summaries and insert/update spans independently. This is required before live OTLP ingestion because one logical trace may be exported across multiple batches.

9. Phase 2 Incremental-write Verification & Identity Review — 2026-07-26:
   - A disposable two-delivery test inserted `span-1` and then `span-2` for the same trace. Both span rows remained after the trace UPSERT, and trace bounds merged from 1s–2s and 3s–4s into 1s–4s (3,000 ms).
   - The verification must become a committed regression test before this gate is closed.
   - The schema currently makes `spans.span_id` the global primary key. OTLP requires span IDs to be unique within a trace, not across all traces. Use `(trace_id, span_id)` as the identity key before receiving arbitrary external telemetry.
   - MVP scope decision: defer this schema migration while Anveshan remains a local prototype. The non-destructive trace UPSERT remains mandatory; the composite key becomes required before broader external telemetry support.

10. Phase 2 OTLP Parser Verification — 2026-07-29:
   - `backend/otlp/parser.py` is a pure transformation layer with no FastAPI or SQLite dependency.
   - The parser test passes with a root and child span emitted from different `ScopeSpans`, confirming that flattening preserves `trace_id` and `parent_span_id` rather than relying on arrival order.
   - Instrumentation scope is retained in `attributes_json`; resource metadata and events remain available in their corresponding JSON fields.
   - Current scope: numeric OTLP enum values are mapped to span kinds and status values. Input validation and alternate enum representations belong at the HTTP boundary in a later step.
