    CREATE TABLE IF NOT EXISTS traces (
        trace_id TEXT PRIMARY KEY,
        root_span_id TEXT,
        service_name TEXT,
        name TEXT,
        start_time INTEGER,        -- Unix epoch in nanoseconds or microseconds
        end_time INTEGER,
        duration_ms REAL,
        span_count INTEGER DEFAULT 0,
        error_count INTEGER DEFAULT 0,
        total_cost REAL DEFAULT 0.0,
        total_input_tokens INTEGER DEFAULT 0,
        total_output_tokens INTEGER DEFAULT 0,
        status TEXT DEFAULT 'UNSET',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS spans (
        span_id TEXT PRIMARY KEY,
        trace_id TEXT NOT NULL,
        parent_span_id TEXT,
        name TEXT NOT NULL,
        kind TEXT NOT NULL,                 -- SERVER, INTERNAL, CLIENT, or GenAI kind (LLM, TOOL, CHAIN)
        status TEXT DEFAULT 'UNSET',
        start_time INTEGER NOT NULL,        -- High precision integer for sorting
        end_time INTEGER NOT NULL,
        duration_ms REAL NOT NULL,

        -- GenAI & Observability Indexed Columns
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        cost REAL DEFAULT 0.0,

        -- Flexible JSON Blobs for details/lazy-loading
        attributes_json TEXT,               -- E.g. prompt, completion, tool params, custom attrs
        events_json TEXT,                   -- In-line events / logs
        resource_json TEXT,                 -- Service metadata

        FOREIGN KEY(trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
    );

    -- Performance Indexes for Graph Building and Querying
    CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id);
    CREATE INDEX IF NOT EXISTS idx_spans_parent_span_id ON spans(parent_span_id);
    CREATE INDEX IF NOT EXISTS idx_spans_trace_parent ON spans(trace_id, parent_span_id);
    CREATE INDEX IF NOT EXISTS idx_spans_start_time ON spans(start_time);
    CREATE INDEX IF NOT EXISTS idx_spans_status ON spans(status);
