"""Five fully connected PydanticAI agents for Campus Customs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic_ai import Agent, RunContext, UsageLimits

try:
    from .models import AgentDecision, AgentRole, Delegation
    from .runtime import TeamRuntime, portkey_model
except ImportError:  # supports imports when uvicorn runs from backend/
    from models import AgentDecision, AgentRole, Delegation
    from runtime import TeamRuntime, portkey_model


ROOT = Path(__file__).resolve().parents[1]


class ShopAgent:
    role: AgentRole

    def __init__(self, role: AgentRole) -> None:
        self.role = role
        prompt = (ROOT / "backend" / "prompts" / f"{role.value}.md").read_text()
        self.agent = Agent(portkey_model(), output_type=AgentDecision, system_prompt=prompt)
        self._add_tools()

    def _add_tools(self) -> None:
        async def _mcp(ctx: RunContext[TeamRuntime], name: str, arguments: dict[str, Any]) -> Any:
            result = await ctx.deps.gateway.call(name, arguments)
            ctx.deps.audit.append(self.role, "mcp_tool_called", detail_tool=name,
                                  arguments=arguments)
            return result

        @self.agent.tool
        async def get_ticket_context(ctx: RunContext[TeamRuntime], ticket_id: int) -> Any:
            """Read one ticket and its linked lease or invoice through MCP."""
            return await _mcp(ctx, "get_ticket_context", {"ticket_id": ticket_id})

        @self.agent.tool
        async def get_product_position(ctx: RunContext[TeamRuntime], sku: str, size: str = "") -> Any:
            """Read inventory and pricing for an exact SKU and size through MCP."""
            return await _mcp(ctx, "get_product_position", {"sku": sku, "size": size})

        @self.agent.tool
        async def get_cash_and_obligations(ctx: RunContext[TeamRuntime]) -> Any:
            """Read shop date, cash, open invoices, and leases through MCP."""
            return await _mcp(ctx, "get_cash_and_obligations", {})

        @self.agent.tool
        async def list_open_tickets(ctx: RunContext[TeamRuntime]) -> Any:
            """Read the open ticket board through MCP."""
            return await _mcp(ctx, "list_open_tickets", {})

        @self.agent.tool
        async def list_vendors(ctx: RunContext[TeamRuntime]) -> Any:
            """Read recorded vendors and lead times through MCP."""
            return await _mcp(ctx, "list_vendors", {})

        @self.agent.tool
        async def get_payment_history(ctx: RunContext[TeamRuntime], kind: str | None = None,
                                      ref_id: int | None = None) -> Any:
            """Read recorded payments through MCP."""
            return await _mcp(ctx, "get_payment_history", {"kind": kind, "ref_id": ref_id})

        @self.agent.tool
        async def delegate_task(ctx: RunContext[TeamRuntime], target: AgentRole,
                                ticket_id: int, task: str) -> Any:
            """Delegate to any other team role, preserving full connectivity."""
            if target == self.role:
                raise ValueError("An agent may not delegate to itself")
            return await ctx.deps.delegate(self.role, Delegation(
                target=target, ticket_id=ticket_id, task=task))

    async def run_task(self, runtime: TeamRuntime, delegation: Delegation) -> AgentDecision:
        runtime.audit.append(self.role, "agent_started", delegation.ticket_id,
                             task=delegation.task)
        result = await self.agent.run(
            delegation.task,
            deps=runtime,
            usage_limits=UsageLimits(request_limit=8, tool_calls_limit=12),
        )
        runtime.audit.append(self.role, "agent_completed", delegation.ticket_id,
                             status=result.output.status,
                             needs_user_approval=result.output.needs_user_approval,
                             summary=result.output.summary,
                             proposed_actions=result.output.proposed_actions)
        return result.output


def build_team() -> dict[AgentRole, ShopAgent]:
    return {role: ShopAgent(role) for role in AgentRole}

