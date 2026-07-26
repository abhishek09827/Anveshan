import sqlite3
from typing import List, Dict, Any

DB_PATH = "anveshan_dev.db"

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode and Foreign Keys
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db(conn: sqlite3.Connection):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                trace_id TEXT PRIMARY KEY,
                root_span_id TEXT,
                service_name TEXT,
                name TEXT,
                start_time INTEGER,
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
            """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS spans (
                span_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                parent_span_id TEXT,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                status TEXT DEFAULT 'UNSET',
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                attributes_json TEXT,
                events_json TEXT,
                resource_json TEXT,
                FOREIGN KEY(trace_id) REFERENCES traces(trace_id) ON DELETE CASCADE
            );
            """)

            # 3. Performance Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_parent_span_id ON spans(parent_span_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_trace_parent ON spans(trace_id, parent_span_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_start_time ON spans(start_time);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_status ON spans(status);")

def insert_trace_and_spans(conn: sqlite3.Connection, trace_summary: Dict[str, Any], spans: List[Dict[str, Any]]):
    with conn:
        conn.execute("""
                INSERT OR REPLACE INTO traces (
                    trace_id, root_span_id, service_name, name, start_time, end_time,
                    duration_ms, span_count, error_count, total_cost, total_input_tokens,
                    total_output_tokens, status
                ) VALUES (
                    :trace_id, :root_span_id, :service_name, :name, :start_time, :end_time,
                    :duration_ms, :span_count, :error_count, :total_cost, :total_input_tokens,
                    :total_output_tokens, :status
                )
            """, trace_summary)

        conn.executemany("""
                INSERT OR REPLACE INTO spans (
                    span_id, trace_id, parent_span_id, name, kind, status,
                    start_time, end_time, duration_ms, input_tokens, output_tokens,
                    cost, attributes_json, events_json, resource_json
                ) VALUES (
                    :span_id, :trace_id, :parent_span_id, :name, :kind, :status,
                    :start_time, :end_time, :duration_ms, :input_tokens, :output_tokens,
                    :cost, :attributes_json, :events_json, :resource_json
                )
            """, spans)