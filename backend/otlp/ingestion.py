import sqlite3
from typing import Any

from backend.db.database import insert_trace_batches
from backend.otlp.parser import parse_resource_spans
from backend.otlp.trace_summary import build_trace_batches

