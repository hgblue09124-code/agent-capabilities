"""Capability execution context."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional


def _make_immutable_dict(d: Optional[dict[str, Any]]) -> MappingProxyType[str, Any]:
    if d is None:
        return MappingProxyType({})
    if isinstance(d, MappingProxyType):
        return d
    return MappingProxyType(dict(d))


@dataclass(frozen=True)
class CapabilityContext:
    """Execution context provided to capability invocations."""

    request_id: str
    caller: Optional[str] = None
    permissions: frozenset[str] = field(default_factory=frozenset)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    deadline: Optional[float] = None
    cancellation_info: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.request_id or not isinstance(self.request_id, str):
            raise ValueError("CapabilityContext request_id must be a non-empty string.")

        # Convert permissions to frozenset
        perms = self.permissions
        if not isinstance(perms, frozenset):
            object.__setattr__(self, "permissions", frozenset(perms if perms else ()))

        # Convert metadata to MappingProxyType
        meta = self.metadata
        if not isinstance(meta, MappingProxyType):
            object.__setattr__(self, "metadata", _make_immutable_dict(meta))

        # Convert cancellation_info to MappingProxyType if present
        cancel = self.cancellation_info
        if cancel is not None and not isinstance(cancel, MappingProxyType):
            object.__setattr__(self, "cancellation_info", _make_immutable_dict(cancel))
