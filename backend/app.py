from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.db.database import get_connection, init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    connection = get_connection()
    try:
        init_db(connection)
    finally:
        connection.close()

    yield


app = FastAPI(
    title="Anveshan",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

