"""
MCP server for database operations using SQLite.
"""

import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP


@dataclass
class AppContext:
    """Application context with database connection."""
    db: sqlite3.Connection


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with database connection."""
    db = sqlite3.connect("example.db")
    # Create sample table if it doesn't exist
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER
        )
    """)
    # Insert sample data if table is empty
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
        )
    db.commit()
    try:
        yield AppContext(db=db)
    finally:
        db.close()


# Create FastMCP server
mcp = FastMCP("DB Server", lifespan=app_lifespan)


@mcp.tool()
def query_db(query: str, ctx: Context) -> str:
    """Execute a SELECT query on the database and return results."""
    db = ctx.request_context.lifespan_context.db
    cursor = db.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return str(results)
    except Exception as e:
        return f"Error executing query: {e}"


@mcp.tool()
def execute_db(query: str, ctx: Context) -> str:
    """Execute an INSERT, UPDATE, or DELETE query on the database."""
    db = ctx.request_context.lifespan_context.db
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
        return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except Exception as e:
        return f"Error executing query: {e}"


@mcp.resource("db://schema")
def get_schema() -> str:
    """Get the database schema."""
    return """
Tables:
- users: id (INTEGER PRIMARY KEY), name (TEXT), age (INTEGER)
"""


if __name__ == "__main__":
    mcp.run()