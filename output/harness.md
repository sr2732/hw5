# Campus Customs Database Harness

## Database under study

This document describes the original `data/campus_customs.db` database. The later working copy is `data/campus_customs_new.db`; the original should remain unchanged so the working copy can be reset.

Shop date: `desk.date_today = 2026-08-31`.

## Tables and fields

### `desk`

- `date_today` — the shop's authoritative current date; agents use it to evaluate overdue invoices, rent, and tickets.
- `notes` — general desk context for the agent team.

### `cash_accounts`

- `name` — account identifier, such as `checking`.
- `balance` — available cash; payment operations must never reduce it below zero.
- `date` — date associated with the balance snapshot.

Accounting uses this table to determine whether an approved payment is affordable and to record the resulting cash position.

### `vendors`

- `id` — vendor identifier.
- `name` — vendor name.
- `specialty` — products or services the vendor supplies.
- `lead_days` — expected shipping/restock lead time.

Inventory uses vendor specialties and lead times to select a restock source and estimate arrival. Accounting and the team must also consider open unpaid invoices before placing new vendor work.

### `inventory`

- `sku` — product identifier.
- `name` — product name.
- `size` — size or `OS` for one-size products.
- `qty` — quantity currently available.
- `location` — shop storage location.

Inventory checks this table against customer orders and bulk requests, identifies shortfalls, and validates fulfillment.

### `pricing`

- `sku` — product identifier.
- `unit_cost` — cost per unit for margin and purchasing analysis.
- `list_price` — standard selling price before discounts.

Inventory and Accounting use pricing to evaluate order economics, margins, discount requests, and purchase decisions.

### `invoices`

- `id` — invoice identifier.
- `vendor_id` — linked vendor in `vendors.id`.
- `amount` — amount owed.
- `due_date` — payment due date.
- `status` — payment state, such as `open`.
- `description` — what the invoice covers.

Accounting monitors unpaid and overdue vendor obligations, while Inventory uses open unpaid invoices as a shipping/restock constraint.

### `leases`

- `id` — lease identifier.
- `space_name` — shop space covered by the lease.
- `landlord` — landlord or property manager.
- `monthly_rent` — rent amount.
- `next_due` — next rent due date.
- `notes` — lease-specific context.

Facilities uses this table to manage shop space and rent obligations; Accounting uses it to prepare an approved payment.

### `payments`

- `id` — payment identifier.
- `kind` — payment category, such as rent or invoice.
- `ref_id` — related lease or invoice identifier.
- `amount` — amount paid.
- `account` — cash account used.
- `paid_at` — payment date/time.
- `approved_by` — approval record, required for every payment.

This is the payment ledger. A successful approved payment must be recorded here and reflected in the relevant obligation/account tables.

### `tickets`

- `id` — ticket identifier.
- `type` — workflow category.
- `requester` — person or organization making the request.
- `subject` — short ticket subject.
- `sku` — related product, when applicable.
- `size` — requested product size, when applicable.
- `qty` — requested quantity, when applicable.
- `lease_id` — linked lease, when applicable; foreign key to `leases.id`.
- `invoice_id` — linked invoice, when applicable; foreign key to `invoices.id`.
- `status` — workflow state, initially `open` for the three tickets studied.
- `notes` — detailed request and communication context.
- `created_at` — ticket creation timestamp.

This is the operations board. Boss reads and delegates tickets; other agents resolve the linked inventory, pricing, invoice, lease, payment, and customer-communication work.

## Open-ticket linkage

At the original database snapshot there are three open tickets:

### Ticket 101 — customer order

- Requester: Tauhid Zaman.
- Request: one `CC-TEE-WHITE`, size `S`.
- Links: `sku/size` → `inventory(sku, size)` and `pricing(sku)`; `invoice_id = 501` → `invoices.id` → vendor `1` (`Bulldog Print Co`).
- Current facts: size S inventory is `0`; invoice 501 is open for `$840`, due `2026-08-28`, for a rush reprint of the same SKU/size.
- Agent relevance: Boss delegates; Inventory identifies the shortfall; Accounting evaluates the unpaid invoice and any payment; Customer Service drafts the customer response.

### Ticket 102 — rent notice

- Requester/landlord: Elm City Properties.
- Request: rent due in two days.
- Link: `lease_id = 1` → `leases.id` for the Chapel Street shop.
- Current facts: monthly rent is `$2,400`, next due `2026-09-02`; with shop date `2026-08-31`, it is not yet overdue.
- Agent relevance: Facilities verifies the lease and timing; Accounting checks cash and prepares a payment for user approval; Customer Service can draft a response if needed.

### Ticket 103 — price override

- Requester: Yale AI Club.
- Request: 20 `CC-HOOD-NAVY`, size `M`, with a bulk discount.
- Links: `sku/size` → `inventory(sku, size)` and `pricing(sku)`.
- Current facts: inventory is `8`; list price is `$58`; unit cost is `$22`; requested quantity is `20`, so there is a shortfall of `12` before fulfillment.
- Agent relevance: Boss delegates; Inventory determines replenishment and vendor; Accounting reviews margin and any purchase order; Customer Service drafts the customer response.

## Initial snapshot summary

- Cash: checking balance `$3,400` as of `2026-08-31`.
- Vendor lead times: Bulldog Print Co `5` days, Elm City Gifts `3` days, QuickShip CT `1` day.
- No payments are recorded yet.
- The original database remains the reset source; later ticket resolutions belong in `campus_customs_new.db`.

## Problem 3 — MCP tools

The MCP server is in `mcp_server/server.py` and reads the working copy `data/campus_customs_new.db`; it is intentionally not run in this problem.

### `get_ticket_context(ticket_id)`

- Tables read: `tickets`, plus the linked `leases` row when `lease_id` is present and the linked `invoices` row when `invoice_id` is present.
- Ticket unlocked: 101.
- Why this is right: Ticket 101 carries `invoice_id = 501`, so this tool exposes the customer request and the open Bulldog Print Co invoice that can block the requested tee reprint.

### `get_product_position(sku, size)`

- Tables read: `inventory` and `pricing`.
- Ticket unlocked: 103.
- Why this is right: Ticket 103 requests 20 `CC-HOOD-NAVY` size M units, so this tool returns the current 8-unit stock, unit cost, and list price needed to evaluate its shortfall and discount margin.

### `get_cash_and_obligations()`

- Tables read: `desk`, `cash_accounts`, `invoices`, and `leases` (open invoices only).
- Ticket unlocked: 102.
- Why this is right: Ticket 102 concerns rent due on 2026-09-02, so this tool returns the shop date, the Chapel Street lease obligation, and checking cash needed before preparing an approved rent payment.

## Problem 5 — Agent team and expanded MCP tools

### Agents

- **Boss** (`backend/prompts/boss.md`, `AgentRole.BOSS`) reads the open board, delegates work to any other role, reconciles specialist results, and makes the final recommendation.
- **Inventory** (`backend/prompts/inventory.md`, `AgentRole.INVENTORY`) verifies SKU/size stock, identifies shortfalls, uses recorded vendor lead times, and recommends—but does not place—a restock.
- **Accounting** (`backend/prompts/accounting.md`, `AgentRole.ACCOUNTING`) evaluates cash, invoices, rent, margins, and payment/PO proposals while enforcing approval and no-negative-balance rules.
- **Facilities** (`backend/prompts/facilities.md`, `AgentRole.FACILITIES`) handles leases, shop space, landlord facts, and rent timing using the authoritative shop date.
- **Customer Service** (`backend/prompts/customer_service.md`, `AgentRole.CUSTOMER_SERVICE`) writes factual drafts for the board and never sends messages externally.

All five are PydanticAI agents using only `gpt-6-luna` through Portkey. `TeamRuntime.delegate()` allows any role to delegate to any other role, except itself; agent shop facts are retrieved through the MCP gateway rather than a second database/tool layer.

### MCP tools available to agents

| Tool | Tables read | Agent use |
|---|---|---|
| `get_ticket_context(ticket_id)` | `tickets`, linked `leases`, linked `invoices` | Retrieves the exact ticket relationships needed before delegation or a decision. |
| `get_product_position(sku, size)` | `inventory`, `pricing` | Verifies available quantity and economics for ticket 101 or 103. |
| `get_cash_and_obligations()` | `desk`, `cash_accounts`, open `invoices`, `leases` | Supplies authoritative date, cash, invoice, and rent facts for Accounting and Facilities. |
| `list_open_tickets()` | `tickets` | Gives Boss the current open work board. |
| `list_vendors()` | `vendors` | Gives Inventory the recorded vendor specialties and lead times without inventing a SKU mapping. |
| `get_payment_history(kind, ref_id)` | `payments` | Lets Accounting verify whether a payment is actually recorded. |

These MCP tools are read-only in Problem 5; no agent can transfer money, contact a vendor, or directly mutate shop data.

### Safety and token limits

- No payment is transferred unless the user explicitly approves that exact payment; recommendations are not authorization.
- A payment must be rejected if available cash would become negative, and every transaction over $1,000 is flagged.
- No revenue is assumed, and no cash inflow is modeled.
- No card numbers, account numbers, credentials, or other secure financial data may be shared.
- Vendor and customer communications remain drafts on the board; no email or phone call is sent.
- Agents must cite MCP-returned facts, surface missing data, and avoid invented vendor mappings, prices, dates, approvals, or commitments.
- The model is fixed to `gpt-6-luna` through Portkey; missing `PORTKEY_API_KEY` fails closed before a model call.
- One agent task produces one structured decision; delegation must name a target and ticket; audit events record MCP calls, starts, completions, and delegations.
- Each agent task is capped at 8 model requests and 12 tool calls, and each ticket is capped at 8 delegation hops, so full connectivity cannot become an unbounded loop.
- Prompts should request only the ticket context needed, and each run should stop after the assigned task and its necessary delegations rather than polling indefinitely.

## Problem 7 — FastAPI backend routes

- `GET /tickets` — returns tickets 101, 102, and 103 with their current open/resolved status.
- `POST /tickets/{ticket_id}/run` — runs the Boss agent for one ticket and returns its structured decision and run ID; marks the ticket resolved only when the decision is resolved without pending approval.
- `GET /events?limit=50` — returns the most recent append-only agent audit events for dashboard refresh.
- `POST /approvals` — applies an explicitly human-approved invoice, rent, or purchase outflow, updates `payments` and `cash_accounts`, and marks an invoice paid when applicable; it refuses missing obligations, mismatched amounts, non-open invoices, and negative balances.
- `POST /tickets/{ticket_id}/decision` — records an explicit human `resolve` or `keep_open` choice, updates the ticket status/notes, and appends the rationale to the audit trail.
- `GET /cash/checking` — returns the current checking balance from `cash_accounts`.
- `POST /reset` — copies untouched `data/campus_customs.db` over `data/campus_customs_new.db` and preserves `output/audit_trail.json`.

Start the backend from `backend/` with `uvicorn main:app --reload --port 8000`.

## Problem 9 — Resolution run and reconciliation

- The working database was reset from the untouched original before the full run; starting checking balance was `$3,400.00`.
- Ticket 101 resolved after human approval of invoice 501 for `$840.00`; invoice 501 is now paid and checking became `$2,560.00`.
- Ticket 102 resolved after human approval of lease 1 rent for `$2,400.00`; checking became `$160.00`.
- Ticket 103 resolved as unable to fulfill safely. Eight of 20 hoodies were in stock; the 12-unit estimated restock was `$264.00`, which the pay guard blocked because it exceeded the `$160.00` balance by `$104.00`. No purchase or payment was recorded.
- Final checking balance is `$160.00`, matching `cash_accounts.balance`; total cash outflow was `$3,240.00`, with no modeled inflow.
- Actual agent behavior and MCP usage are recorded in the Actual sections of `output/desk_tickets.html`; the full structured summary is `output/resolved_tickets.json`; the double-clickable board snapshot is `output/resolved_board.html`.
- The audit trail remains append-only in `output/audit_trail.json`; diagnostic failed/loop attempts are preserved and the final human decisions are also recorded.


