
import json
import unittest

from backend.otlp.trace_summary import build_trace_batches


RESOURCE_JSON = json.dumps(
    {
        "attributes": [
            {
                "key": "service.name",
                "value": {"stringValue": "anveshan-dev-lab"},
            }
        ]
    }
)


def span(
    trace_id: str,
    span_id: str,
    parent_span_id: str | None,
    start_time: int,
    end_time: int,
    status: str = "OK",
) -> dict:
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "name": span_id,
        "kind": "INTERNAL",
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "duration_ms": (end_time - start_time) / 1_000_000,
        "attributes_json": "{}",
        "events_json": "[]",
        "resource_json": RESOURCE_JSON,
    }


class BuildTraceBatchesTests(unittest.TestCase):
    def test_groups_spans_and_calculates_trace_summary(self):
        spans = [
            span("trace-a", "root-a", None, 1_000_000_000, 2_000_000_000),
            span("trace-a", "child-a", "root-a", 1_100_000_000, 3_000_000_000, "ERROR"),
            span("trace-b", "root-b", None, 4_000_000_000, 4_500_000_000),
        ]

        batches = build_trace_batches(spans)
        summaries = {
            summary["trace_id"]: (summary, trace_spans)
            for summary, trace_spans in batches
        }

        trace_a, trace_a_spans = summaries["trace-a"]
        self.assertEqual(trace_a["root_span_id"], "root-a")
        self.assertEqual(trace_a["span_count"], 2)
        self.assertEqual(trace_a["error_count"], 1)
        self.assertEqual(trace_a["status"], "ERROR")
        self.assertEqual(trace_a["duration_ms"], 2000.0)
        self.assertEqual(trace_a["service_name"], "anveshan-dev-lab")
        self.assertEqual([item["span_id"] for item in trace_a_spans], ["root-a", "child-a"])

        trace_b, trace_b_spans = summaries["trace-b"]
        self.assertEqual(trace_b["span_count"], 1)
        self.assertEqual(trace_b["status"], "OK")
        self.assertEqual(trace_b_spans[0]["span_id"], "root-b")


if __name__ == "__main__":
    unittest.main()
