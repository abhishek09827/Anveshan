import unittest
from backend.otlp.parser import parse_resource_spans

class ParseResourceSpansTests(unittest.TestCase):
    def test_flattens_spans_across_scopes_and_preserves_parent_link(self):
        root_span_id = "1111111111111111"

        payload = {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {
                                "key": "service.name",
                                "value": {"stringValue": "anveshan-dev-lab"},
                            }
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {"name": "agent.tracer", "version": "1.0.0"},
                            "spans": [
                                {
                                    "traceId": "a" * 32,
                                    "spanId": root_span_id,
                                    "name": "agent.run",
                                    "kind": 1,
                                    "startTimeUnixNano": "1000000000",
                                    "endTimeUnixNano": "1250000000",
                                    "status": {"code": 1},
                                    "attributes": [],
                                    "events": [],
                                }
                            ],
                        },
                        {
                            "scope": {"name": "tool.tracer", "version": "1.0.0"},
                            "spans": [
                                {
                                    "traceId": "a" * 32,
                                    "spanId": "2222222222222222",
                                    "parentSpanId": root_span_id,
                                    "name": "calculator",
                                    "kind": 3,
                                    "startTimeUnixNano": "1100000000",
                                    "endTimeUnixNano": "1200000000",
                                    "status": {"code": 2},
                                    "attributes": [],
                                    "events": [],
                                }
                            ],
                        },
                    ],
                }
            ]
        }

        spans = parse_resource_spans(payload)

        self.assertEqual(len(spans), 2)

        root, child = spans
        self.assertEqual(root["trace_id"], "a" * 32)
        self.assertEqual(child["trace_id"], root["trace_id"])
        self.assertIsNone(root["parent_span_id"])
        self.assertEqual(child["parent_span_id"], root_span_id)

        self.assertEqual(root["kind"], "INTERNAL")
        self.assertEqual(child["kind"], "CLIENT")
        self.assertEqual(root["status"], "OK")
        self.assertEqual(child["status"], "ERROR")
        self.assertEqual(root["duration_ms"], 250.0)

        self.assertIn("agent.tracer", root["attributes_json"])
        self.assertIn("tool.tracer", child["attributes_json"])
        self.assertIn("anveshan-dev-lab", root["resource_json"])


if __name__ == "__main__":
    unittest.main()