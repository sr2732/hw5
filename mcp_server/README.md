# Campus Customs MCP Server

This FastMCP server provides the agent team with read-only, database-backed tools for the Campus Customs shop. It is designed to be the shared tool layer for every agent. The server is written in `server.py` but is not connected to or run for Problem 3.

It uses `data/campus_customs_new.db`, the working copy. The untouched `data/campus_customs.db` remains the reset source.

## Tools

1. `get_ticket_context(ticket_id)` reads `tickets` and any linked `leases` or `invoices`, so an agent can see the complete database context for a ticket before delegating or deciding.
2. `get_product_position(sku, size)` reads `inventory` and `pricing`, so an agent can compare the requested SKU/size quantity with its unit cost and list price.
3. `get_cash_and_obligations()` reads `desk`, `cash_accounts`, open `invoices`, and `leases`, so an agent can evaluate the shop date, available cash, and payment obligations before preparing a payment.
4. `list_open_tickets()` reads `tickets`, so the Boss can load the current work board before delegating.
5. `list_vendors()` reads `vendors`, so Inventory can use only recorded vendor names, specialties, and lead times when preparing a restock recommendation.
6. `get_payment_history(kind, ref_id)` reads `payments`, so Accounting can avoid claiming an obligation was paid without a ledger record.

All three tools use parameterized SQLite queries and do not write to the database.

The server prefers the assignment's `mcp.server.fastmcp.FastMCP`; it also has a small compatibility fallback for MCP 2.x, where that class is named `MCPServer`.

