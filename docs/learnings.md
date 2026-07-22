1. Data serialization is the process of converting complex data structures, such as objects or arrays, into a format that can be easily transmitted over a network or stored in a file.

2. Protobuf -> data format developed by Google used for serializing data
            -> Smaller n faster
            -> binary format
            -> Project Scope:
                -> used only for OTLP communication between AI applications and the OpenTelemetry Collector
                -> Compared to JSON, Protobuf produces smaller payloads and faster serialization/deserialization, which is important for high-volume telemetry streams.
                -> in later steps convert the data into a query-friendly hybrid SQLite schema internally, since the project's primary goal is debugging and analysis rather than efficient network communication.

3. OTLP     -> defines what telemetry messages look like (Protobuf schemas) and how
               they are transported (gRPC or HTTP).
            -> compatible with frameworks like LangGraph, OpenAI Agents SDK, CrewAI, LlamaIndex, and AutoGen without writing custom integrations.
            -> The OpenTelemetry Collector is a middleware component that receives telemetry from instrumented applications, optionally processes it (such as batching, filtering, or enriching), and exports it to one or more backends. In Sakshi, I use the Collector so I don't have to implement the OTLP protocol, retries, batching, or buffering myself. This lets Sakshi focus on its core responsibility—debugging and evaluating AI agent execution.

4. OpenTelemetry Core Hierarchy:
            -> Trace: End-to-end request workflow identified by a global `trace_id`.
            -> Span: Single unit of work with duration, attributes, status, and unique `span_id`.
            -> Parent-Child Linking: Spans link via `parent_id` to form a DAG (`Root -> Parent -> Child`).
            -> Auto vs Manual Instrumentation: Auto-instrumentation (e.g. `FastAPIInstrumentor`) captures incoming HTTP request spans; manual instrumentation (`tracer.start_as_current_span`) captures internal domain logic (e.g., agent thinking steps, tool invocations).

5. Span Emission Order (LIFO Call Stack):
            -> OpenTelemetry emits/exports spans only when they end (`span.end()`).
            -> Nested execution follows LIFO stack behavior: innermost child spans finish and export before parent spans finish.
            -> Anveshan parser/graph engines must reconstruct trace trees using `parent_id` and `start_time` rather than raw arrival order.