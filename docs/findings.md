1. AI agents fail silently. Logs show success but the output is wrong. Existing tools either show you what happened (tracing) or measure quality (evaluation), but not both in one local-first tool. Lets ingests OTLP traces from any AI framework, visualizes the full decision graph, and runs automated evaluation - hallucination detection, compliance checks, cost tracking - so developers catch failures that logs miss, without sending data to the cloud.

2. Span Emission Order Discrepancy:
   - Empirical observation: In nested tracing (`Root` -> `Thinking` -> `Tool`), console exporter prints child spans (`Tool`) first and root spans (`Root`) last.
   - Cause: OpenTelemetry exports spans on completion (`span.end()`). Innermost execution contexts resolve first.
   - Architectural Implication: Ingestion & graph building logic cannot assume chronological arrival. Graph reconstruction must decouple arrival sequence from temporal execution sequence using `trace_id`, `span_id`, `parent_id`, and `start_time`.

