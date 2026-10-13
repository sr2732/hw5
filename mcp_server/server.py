"""Campus Customs read-only MCP tools.

The server intentionally does not start on import.  Run it only in a later
problem when the MCP integration is requested.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

try:
    # MCP 1.x, as requested by the assignment.
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    # MCP 2.x renamed FastMCP to MCPServer.  Keep the same decorator and
    # stdio surface so this project remains runnable in either SDK generation.
    from mcp.server.mcpserver import MCPServer

    class FastMCP(MCPServer):
        """Compatibility name for the MCP 2.x replacement."""

        pass


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_DIR / "data" / "campus_customs_new.db"

mcp = FastMCP("campus-customs")


def _query_one(sql: str, parameters: tuple[Any, ...]) -> dict[str, Any] | None:
    """Return one SQLite row as a dictionary, or None when it does not exist."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(sql, parameters).fetchone()
        return dict(row) if row is not None else None


@mcp.tool()
def get_ticket_context(ticket_id: int) -> dict[str, Any]:
    """Read a ticket and its linked lease or invoice context from the database."""
    ticket = _query_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if ticket is None:
        return {"found": False, "ticket_id": ticket_id}

    result: dict[str, Any] = {"found": True, "ticket": ticket}
    if ticket["lease_id"] is not None:
        result["lease"] = _query_one(
            "SELECT * FROM leases WHERE id = ?", (ticket["lease_id"],)
        )
    if ticket["invoice_id"] is not None:
        result["invoice"] = _query_one(
            "SELECT * FROM invoices WHERE id = ?", (ticket["invoice_id"],)
        )
    return result


@mcp.tool()
def get_product_position(sku: str, size: str) -> dict[str, Any]:
    """Read inventory and pricing for one SKU and size without changing the DB."""
    inventory = _query_one(
        "SELECT * FROM inventory WHERE sku = ? AND size = ?", (sku, size)
    )
    pricing = _query_one("SELECT * FROM pricing WHERE sku = ?", (sku,))
    return {
        "sku": sku,
        "size": size,
        "inventory": inventory,
        "pricing": pricing,
    }


@mcp.tool()
def get_cash_and_obligations() -> dict[str, Any]:
    """Read the shop date, cash balances, open invoices, and lease obligations."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        desk = connection.execute("SELECT * FROM desk").fetchone()
        cash_accounts = connection.execute("SELECT * FROM cash_accounts").fetchall()
        invoices = connection.execute(
            "SELECT * FROM invoices WHERE status = 'open' ORDER BY due_date, id"
        ).fetchall()
        leases = connection.execute("SELECT * FROM leases ORDER BY next_due, id").fetchall()
    return {
        "desk": dict(desk) if desk is not None else None,
        "cash_accounts": [dict(row) for row in cash_accounts],
        "open_invoices": [dict(row) for row in invoices],
        "leases": [dict(row) for row in leases],
    }


@mcp.tool()
def list_open_tickets() -> list[dict[str, Any]]:
    """Read every ticket currently marked open on the shop board."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM tickets WHERE status = 'open' ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


@mcp.tool()
def list_vendors() -> list[dict[str, Any]]:
    """Read the complete vendor directory, including each recorded lead time."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM vendors ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@mcp.tool()
def get_payment_history(kind: str | None = None, ref_id: int | None = None) -> list[dict[str, Any]]:
    """Read recorded payments, optionally narrowed to an obligation reference."""
    clauses: list[str] = []
    parameters: list[Any] = []
    if kind is not None:
        clauses.append("kind = ?")
        parameters.append(kind)
    if ref_id is not None:
        clauses.append("ref_id = ?")
        parameters.append(ref_id)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM payments" + where + " ORDER BY paid_at, id", parameters
        ).fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    # Deliberately not invoked during Problem 3; this is available for later
    # integration once the assignment asks us to run the MCP server.
    mcp.run()

