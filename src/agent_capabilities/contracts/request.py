"""Capability request definition."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from agent_capabilities.contracts.context import CapabilityContext


def _make_immutable_dict(d: Optional[dict[str, Any]]) -> MappingProxyType[str, Any]:
    if d is None:
        return MappingProxyType({})
    if isinstance(d, MappingProxyType):
        return d
    return MappingProxyType(dict(d))


@dataclass(frozen=True)
class CapabilityRequest:
    """Invocation request for a capability action."""

    capability_id: str
    action: str
    input: Mapping[str, Any] = field(default_factory=dict)
    context: Optional[CapabilityContext] = None

    def __post_init__(self) -> None:
        if not self.capability_id or not isinstance(self.capability_id, str):
            raise ValueError("CapabilityRequest capability_id must be a non-empty string.")
        if not self.action or not isinstance(self.action, str):
            raise ValueError("CapabilityRequest action must be a non-empty string.")

        inp = self.input
        if not isinstance(inp, MappingProxyType):
            object.__setattr__(self, "input", _make_immutable_dict(inp))
