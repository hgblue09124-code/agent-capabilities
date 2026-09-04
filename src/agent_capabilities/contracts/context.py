"""Capability execution context."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class CapabilityContext:
    """Execution context provided to capability invocations."""

    request_id: str
    caller: Optional[str] = None
    permissions: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    deadline: Optional[float] = None
    cancellation_info: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        if isinstance(self.permissions, (list, tuple)):
            object.__setattr__(self, "permissions", set(self.permissions))
