"""Shared, validated types for the Campus Customs agent team."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    BOSS = "boss"
    INVENTORY = "inventory"
    ACCOUNTING = "accounting"
    FACILITIES = "facilities"
    CUSTOMER_SERVICE = "customer_service"


class Delegation(BaseModel):
    target: AgentRole
    ticket_id: int = Field(gt=0)
    task: str = Field(min_length=1, max_length=2000)


class AgentDecision(BaseModel):
    role: AgentRole
    ticket_id: int = Field(gt=0)
    status: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    proposed_actions: list[str] = Field(default_factory=list)
    needs_user_approval: bool = False
    delegations: list[Delegation] = Field(default_factory=list)
    approval_flags: list[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    timestamp: str
    run_id: str
    step: int
    role: AgentRole
    event: str
    ticket_id: int | None = None
    detail: dict[str, Any] = Field(default_factory=dict)

