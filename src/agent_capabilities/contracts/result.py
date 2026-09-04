"""Capability result definition."""

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
class CapabilityResult:
    """Result returned by a capability execution."""

    success: bool
    output: Optional[Mapping[str, Any]] = None
    error: Optional[Mapping[str, Any]] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise ValueError("CapabilityResult success must be a boolean.")

        out = self.output
        if out is not None and not isinstance(out, MappingProxyType):
            object.__setattr__(self, "output", _make_immutable_dict(out))

        err = self.error
        if err is not None and not isinstance(err, MappingProxyType):
            object.__setattr__(self, "error", _make_immutable_dict(err))

        meta = self.metadata
        if not isinstance(meta, MappingProxyType):
            object.__setattr__(self, "metadata", _make_immutable_dict(meta))

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the result."""
        return {
            "success": self.success,
            "output": dict(self.output) if self.output is not None else None,
            "error": dict(self.error) if self.error is not None else None,
            "metadata": dict(self.metadata),
        }
