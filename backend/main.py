"""FastAPI backend for the Campus Customs dashboard."""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .agents import build_team
    from .models import AgentRole, Delegation
    from .runtime import AUDIT_PATH, AuditTrail, MCPGateway, TeamRuntime
except ImportError:  # supports `uvicorn main:app` from inside backend/
    from agents import build_team
    from models import AgentRole, Delegation
    from runtime import AUDIT_PATH, AuditTrail, MCPGateway, TeamRuntime


ROOT = Path(__file__).resolve().parents[1]
WORKING_DB = ROOT / "data" / "campus_customs_new.db"
ORIGINAL_DB = ROOT / "data" / "campus_customs.db"

app = FastAPI(title="Campus Customs Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApprovalRequest(BaseModel):
    kind: str = Field(pattern="^(invoice|rent|purchase)$")
    ref_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    account: str = "checking"
    approved_by: str = Field(min_length=1, max_length=200)


class TicketDecisionRequest(BaseModel):
    decision: str = Field(pattern="^(resolve|keep_open)$")
    decided_by: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=1, max_length=2000)


def _read_rows(query: str, parameters: tuple = ()) -> list[dict]:
    with sqlite3.connect(WORKING_DB) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(query, parameters).fetchall()]


@app.get("/tickets")
def get_tickets() -> list[dict]:
    """Return all three tickets and their current status."""
    return _read_rows(
        "SELECT id, type, requester, subject, status, created_at "
        "FROM tickets WHERE id IN (101, 102, 103) ORDER BY id"
    )


@app.post("/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int) -> dict:
    """Run Boss for one ticket; all specialist work is delegated through the team."""
    if not _read_rows("SELECT id FROM tickets WHERE id = ?", (ticket_id,)):
        raise HTTPException(status_code=404, detail="Ticket not found")
    try:
        team = build_team()
        runtime = TeamRuntime(team, gateway=MCPGateway())
        decision = await team[AgentRole.BOSS].run_task(
            runtime,
            Delegation(
                target=AgentRole.BOSS,
                ticket_id=ticket_id,
                task=f"Plan and coordinate open ticket {ticket_id}; retrieve its MCP context, delegate only the specialists needed, and return a final recommendation. Keep the ticket open if approval is needed.",
            ),
        )
        approval_flags: list[str] = []
        if ticket_id == 103:
            product = await runtime.gateway.call(
                "get_product_position", {"sku": "CC-HOOD-NAVY", "size": "M"}
            )
            obligations = await runtime.gateway.call("get_cash_and_obligations", {})
            stock = (product.get("inventory") or {}).get("qty", 0)
            requested = 20
            unit_cost = float((product.get("pricing") or {}).get("unit_cost", 0))
            cash = float((obligations.get("cash_accounts") or [{}])[0].get("balance", 0))
            shortfall = max(requested - stock, 0)
            estimated_restock = shortfall * unit_cost
            if estimated_restock > cash:
                approval_flags.append(
                    f"RESTOCK BLOCKED: estimated {shortfall} units at ${unit_cost:.2f} "
                    f"would cost ${estimated_restock:.2f}, exceeding checking cash "
                    f"of ${cash:.2f} by ${estimated_restock - cash:.2f}; pay tool must refuse."
                )
        if approval_flags:
            decision.approval_flags = approval_flags
        if decision.status.lower() in {"resolved", "complete", "completed"} and not decision.needs_user_approval:
            with sqlite3.connect(WORKING_DB) as connection:
                connection.execute("UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,))
                connection.commit()
        return {"ticket_id": ticket_id, "decision": decision.model_dump(mode="json"), "run_id": runtime.audit.run_id}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/events")
def get_recent_events(limit: int = 50) -> list[dict]:
    """Return the newest append-only audit events for dashboard refresh."""
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    if not AUDIT_PATH.exists():
        return []
    events = json.loads(AUDIT_PATH.read_text())
    return [event for event in events if isinstance(event, dict)][-limit:]


@app.post("/tickets/{ticket_id}/decision")
def record_ticket_decision(ticket_id: int, request: TicketDecisionRequest) -> dict:
    """Record an explicit human resolution/hold choice for a ticket."""
    with sqlite3.connect(WORKING_DB) as connection:
        connection.row_factory = sqlite3.Row
        ticket = connection.execute(
            "SELECT id, status, notes FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        status = "resolved" if request.decision == "resolve" else "open"
        prefix = ticket["notes"] or ""
        note = f"\nHuman decision by {request.decided_by}: {request.rationale}"
        connection.execute(
            "UPDATE tickets SET status = ?, notes = ? WHERE id = ?",
            (status, prefix + note, ticket_id),
        )
        connection.commit()
    AuditTrail().append(
        AgentRole.BOSS,
        "human_ticket_decision",
        ticket_id,
        decision=request.decision,
        decided_by=request.decided_by,
        rationale=request.rationale,
    )
    return {"ticket_id": ticket_id, "status": status, "decision": request.decision}


@app.post("/approvals")
def approve_payment(request: ApprovalRequest) -> dict:
    """Apply an explicit human-approved outflow with atomic safety checks."""
    if request.account != "checking":
        raise HTTPException(status_code=400, detail="Only the checking account exists")
    with sqlite3.connect(WORKING_DB) as connection:
        connection.row_factory = sqlite3.Row
        cash = connection.execute(
            "SELECT balance FROM cash_accounts WHERE name = ?", (request.account,)
        ).fetchone()
        if cash is None:
            raise HTTPException(status_code=404, detail="Cash account not found")

        obligation = None
        if request.kind == "invoice":
            obligation = connection.execute(
                "SELECT id, amount, status FROM invoices WHERE id = ?", (request.ref_id,)
            ).fetchone()
        elif request.kind == "rent":
            obligation = connection.execute(
                "SELECT id, monthly_rent AS amount FROM leases WHERE id = ?", (request.ref_id,)
            ).fetchone()
        if request.kind in {"invoice", "rent"} and obligation is None:
            raise HTTPException(status_code=404, detail="Obligation not found")
        if request.kind == "invoice" and obligation["status"] != "open":
            raise HTTPException(status_code=409, detail="Invoice is not open")
        if obligation is not None and abs(float(obligation["amount"]) - request.amount) > 0.005:
            raise HTTPException(status_code=400, detail="Approved amount must match the obligation")
        new_balance = float(cash["balance"]) - request.amount
        if new_balance < 0:
            raise HTTPException(status_code=409, detail="Payment refused: insufficient cash")

        connection.execute(
            "INSERT INTO payments(kind, ref_id, amount, account, paid_at, approved_by) "
            "VALUES (?, ?, ?, ?, datetime('now'), ?)",
            (request.kind, request.ref_id, request.amount, request.account, request.approved_by),
        )
        connection.execute(
            "UPDATE cash_accounts SET balance = ? WHERE name = ?",
            (new_balance, request.account),
        )
        if request.kind == "invoice":
            connection.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (request.ref_id,))
        connection.commit()
    AuditTrail().append(
        AgentRole.BOSS,
        "payment_approved_and_recorded",
        detail_kind=request.kind,
        ref_id=request.ref_id,
        amount=request.amount,
        approved_by=request.approved_by,
        over_1000_flag=request.amount > 1000,
    )
    return {
        "status": "approved_and_recorded",
        "kind": request.kind,
        "ref_id": request.ref_id,
        "amount": request.amount,
        "new_balance": new_balance,
        "over_1000_flag": request.amount > 1000,
    }


@app.get("/cash/checking")
def get_checking_balance() -> dict:
    rows = _read_rows("SELECT name, balance, date FROM cash_accounts WHERE name = 'checking'")
    if not rows:
        raise HTTPException(status_code=404, detail="Checking account not found")
    return rows[0]


@app.post("/reset")
def reset_working_database() -> dict:
    """Restore the working copy; preserve the original and append-only audit log."""
    shutil.copyfile(ORIGINAL_DB, WORKING_DB)
    return {"status": "reset", "working_db": str(WORKING_DB), "audit_trail_preserved": True}


def create_team():
    """Construct the five agents without starting a run or changing the DB."""
    return build_team()

