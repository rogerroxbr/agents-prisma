"""LangGraph checkpoint saver for PostgreSQL using official PostgresSaver."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from src.db.config import get_psycopg_url

try:
    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg_pool import ConnectionPool

    HAS_POSTGRES_SAVER = True
except ImportError:
    HAS_POSTGRES_SAVER = False


@contextmanager
def get_postgres_checkpointer() -> Generator[Any, None, None]:  # type: ignore
    """Context manager to yield a configured PostgresSaver for LangGraph.

    Yields:
        PostgresSaver instance ready to be passed to StateGraph.compile()
    """
    if not HAS_POSTGRES_SAVER:
        print(
            "[CHECKPOINT] psycopg_pool or langgraph-checkpoint-postgres not installed. Yielding None."
        )
        yield None
        return

    db_uri = get_psycopg_url()

    if db_uri.startswith("sqlite"):
        print("[CHECKPOINT] SQLite is not supported by PostgresSaver. Yielding None.")
        yield None
        return

    # In production, kwargs like max_size, min_size might be tuned
    pool_kwargs = {
        "max_size": 10,
    }

    with ConnectionPool(conninfo=db_uri, **pool_kwargs) as pool:
        checkpointer = PostgresSaver(pool)

        # Ensure the schema (langgraph checkpoints tables) exists
        # In a production environment with concurrent workers, this setup
        # might be done via migrations instead of on every run.
        checkpointer.setup()

        yield checkpointer


__all__ = ["get_postgres_checkpointer"]
