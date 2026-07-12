# Anveshan — reference card

**Witness your agent's mind.**
Local-first AI agent debugger and evaluation tool.

---

## What it solves

| Failure mode | What current tools miss | What Anveshan does |
|---|---|---|
| Blindness | Raw JSON, no structure | Visual decision graph |
| Silent success | No error, wrong output | Evaluation layer catches it |
| The why gap | "Where" but not "why" | Pattern inference on spans |

---

## Core capabilities (v1)

1. **Ingest** — OTLP from any framework → SQLite. Zero code changes, one env var.
2. **Visualize** — Cytoscape.js DAG. Nodes colored by span kind. Click for full context.
3. **Evaluate** — Sync (cost, errors, regex) + async (LLM-judge, embeddings).
4. **Explain** — Rule-based why-inference: tool loops, amount hallucinations, bad state propagation.
5. **Domain plugins** — Cybersecurity + financial evaluators (Phase 5, after core is solid).

---

## Architecture in one line

```
Any OTel app → Collector (Go) → JSON file → FastAPI (Python) → SQLite → React UI
```

---

## Key decisions and why

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Ingestion | OTel Collector | Custom receiver | Protocol already solved |
| Storage | SQLite WAL | Postgres | Zero setup, local-first |
| Schema | Hybrid (cols + blob) | Pure relational | GenAI attrs evolve, can't do migrations |
| Eval timing | Sync + async split | All-sync / all-batch | Blocking ingestion on LLM judge = broken UX |
| Visualization | Cytoscape.js | D3 | Native graph primitives, layout built-in |

---

## Schema fields that matter

```
trace:  trace_id, start/end, total_tokens, total_cost, hallucination_score
span:   span_id, parent_span_id, span_kind, gen_ai_model, input/output_tokens
        session_id, conversation_id, turn_count   ← multi-turn tracking
        prompt_source (human|agent|system)        ← self-prompting agents
        cost, error, hallucination_hit
        attributes_json                           ← everything else
```

---

## Build order + gates

| Phase | What | Gate |
|---|---|---|
| 0 | Schema + evaluator interface decisions | Nothing breaks later |
| 1 | Synthetic span generator + SQLite | 1000 spans → 1000 rows, zero loss |
| 2 | Ingestion + Collector config | Real app, 10 min, zero span loss |
| 3 | Evaluation engine | ≥75% accuracy on 40 labeled examples |
| 4 | REST API (graph endpoint last) | Graph returns correct nodes+edges |
| 5 | Frontend (500-span synthetic first) | Renders under 2 seconds |
| 6 | Domain plugins | Known test cases pass |
| 7 | Ship | Stranger installs + debugs in under 5 min |

---

## Interview framing (trade-off sentences)

- "I chose SQLite over Postgres because local-first means zero setup — write throughput was never the bottleneck."
- "I split evaluation into sync and async tiers because blocking ingestion on a network call to a judge model would make the tool feel broken during a live debug session."
- "I chose the OTel Collector over a custom receiver because the OTLP wire protocol is already solved — I own everything after the file."
- "I built granular span kinds because production teams like Intuit's are decomposing monolithic agents into specialized skills — the debugger needs to reflect that boundary."

---

## What it is not

- Not a cloud service (everything local, no data egress)
- Not framework-specific (any OTLP app works)
- Not a production monitoring tool (dev + debug only)
- Not an agent framework (observes agents, doesn't build them)

---

## The measure of v1 success

A developer installs Anveshan, runs their agent, opens `localhost:8080`, and catches a hallucination they would have missed through log inspection alone — in under 5 minutes from cold start.