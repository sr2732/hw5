"""MCP gateway, agent delegation, and append-only audit support."""

from __future__ import annotations

import asyncio
import json
import os
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

try:
    from .models import AgentRole, AuditEvent, Delegation
except ImportError:  # supports imports when uvicorn runs from backend/
    from models import AgentRole, AuditEvent, Delegation


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "output" / "audit_trail.json"
AUDIT_LOCK = threading.Lock()


class MCPGateway:
    """The only shop-data gateway exposed to agents; it never talks to SQLite."""

    def __init__(self) -> None:
        self.params = StdioServerParameters(
            command="python3", args=[str(ROOT / "mcp_server" / "server.py")]
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[ClientSession]:
        async with stdio_client(self.params) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                yield client

    async def call(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        async with self.session() as client:
            result = await client.call_tool(tool_name, arguments)
            if getattr(result, "is_error", False):
                raise RuntimeError(f"MCP tool failed: {tool_name}")
            return getattr(result, "structured_content", None) or result.content[0].text


class AuditTrail:
    """Preserve prior runs while appending structured agent-loop events."""

    def __init__(self, path: Path = AUDIT_PATH, run_id: str | None = None) -> None:
        self.path = path
        self.run_id = run_id or str(uuid.uuid4())
        self.step = 0
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, role: AgentRole, event: str, ticket_id: int | None = None, **detail: Any) -> None:
        self.step += 1
        item = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            run_id=self.run_id,
            step=self.step,
            role=role,
            event=event,
            ticket_id=ticket_id,
            detail=detail,
        ).model_dump(mode="json")
        with AUDIT_LOCK:
            try:
                history = json.loads(self.path.read_text()) if self.path.exists() else []
                if not isinstance(history, list):
                    raise ValueError("audit trail must be a JSON array")
            except (json.JSONDecodeError, ValueError) as exc:
                raise RuntimeError("Refusing to overwrite an invalid audit trail") from exc
            history.append(item)
            temp = self.path.with_name(f".audit_trail.{uuid.uuid4().hex}.tmp")
            temp.write_text(json.dumps(history, indent=2) + "\n")
            temp.replace(self.path)


class TeamRuntime:
    """Routes delegations between all five roles without adding shop-data tools."""

    def __init__(self, agents: dict[AgentRole, Any], gateway: MCPGateway | None = None) -> None:
        self.agents = agents
        self.gateway = gateway or MCPGateway()
        self.audit = AuditTrail()
        self.delegation_counts: dict[int, int] = {}

    async def delegate(self, source: AgentRole, delegation: Delegation) -> Any:
        if delegation.target not in self.agents:
            raise ValueError(f"Unknown target agent: {delegation.target}")
        count = self.delegation_counts.get(delegation.ticket_id, 0) + 1
        self.delegation_counts[delegation.ticket_id] = count
        if count > 8:
            self.audit.append(source, "delegation_stopped_safety_cap", delegation.ticket_id,
                              target=delegation.target.value, count=count)
            return {"error": "Delegation safety cap reached; return findings to Boss."}
        self.audit.append(source, "delegation_requested", delegation.ticket_id,
                          target=delegation.target.value, task=delegation.task)
        return await self.agents[delegation.target].run_task(self, delegation)


def portkey_model() -> Any:
    """Build the one permitted model through Portkey; fail closed if unconfigured."""
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is required; no model call was attempted")
    from openai import AsyncOpenAI
    from pydantic_ai.models.openai import OpenAIResponsesModel
    from pydantic_ai.providers.openai import OpenAIProvider

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.portkey.ai/v1",
        default_headers={"x-portkey-api-key": api_key},
    )
    return OpenAIResponsesModel(
        "gpt-6-luna",
        provider=OpenAIProvider(openai_client=client),
    )

