import json
from collections import defaultdict
from typing import Any

def _service_name(resource_json: str) -> str:
    resource = json.loads(resource_json)

    for attribute in resource.get("attributes", []):
        if attribute.get("key") == "service.name":
            value = attribute.get("value", {})
            return value.get("stringValue", "unknown")

    return "unknown"

def build_trace_batches(
    spans: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], list[dict[str, Any]]]]:
    spans_by_trace: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for span in spans:
        spans_by_trace[span["trace_id"]].append(span)

    batches = []

    for trace_id, trace_spans in spans_by_trace.items():
        earliest_span = min(trace_spans, key=lambda span: span["start_time"])

        root_candidates = [
            span for span in trace_spans
            if span["parent_span_id"] is None
        ]
        root_span = (
            min(root_candidates, key=lambda span: span["start_time"])
            if root_candidates
            else None
        )

        start_time = min(span["start_time"] for span in trace_spans)
        end_time = max(span["end_time"] for span in trace_spans)
        error_count = sum(
            span["status"] == "ERROR"
            for span in trace_spans
        )

        trace_summary = {
            "trace_id": trace_id,
            "root_span_id": root_span["span_id"] if root_span else None,
            "service_name": _service_name(earliest_span["resource_json"]),
            "name": (
                root_span["name"]
                if root_span
                else earliest_span["name"]
            ),
            "start_time": start_time,
            "end_time": end_time,
            "duration_ms": (end_time - start_time) / 1_000_000,
            "span_count": len(trace_spans),
            "error_count": error_count,
            "total_cost": sum(
                span.get("cost", 0.0)
                for span in trace_spans
            ),
            "total_input_tokens": sum(
                span.get("input_tokens", 0)
                for span in trace_spans
            ),
            "total_output_tokens": sum(
                span.get("output_tokens", 0)
                for span in trace_spans
            ),
            "status": "ERROR" if error_count else "OK",
        }

        batches.append((trace_summary, trace_spans))

    return batches
