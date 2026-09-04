"""Capability request definition."""

from dataclasses import dataclass, field
from typing import Any, Optional

from agent_capabilities.contracts.context import CapabilityContext


@dataclass(frozen=True)
class CapabilityRequest:
    """Invocation request for a capability action."""

    capability_id: str
    action: str
    input: dict[str, Any] = field(default_factory=dict)
    context: Optional[CapabilityContext] = None
