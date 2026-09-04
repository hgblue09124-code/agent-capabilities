"""Capability interface and metadata definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from agent_capabilities.contracts.context import CapabilityContext
from agent_capabilities.contracts.lifecycle import CapabilityStatus
from agent_capabilities.contracts.request import CapabilityRequest
from agent_capabilities.contracts.result import CapabilityResult


def _make_immutable_dict(d: Optional[dict[str, Any]]) -> MappingProxyType[str, Any]:
    if d is None:
        return MappingProxyType({})
    if isinstance(d, MappingProxyType):
        return d
    return MappingProxyType(dict(d))


@dataclass(frozen=True)
class CapabilityMetadata:
    """Metadata declaring capability capabilities, requirements, and information."""

    id: str
    name: str
    version: str
    description: str
    actions: tuple[str, ...] = field(default_factory=tuple)
    permissions: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not isinstance(self.id, str):
            raise ValueError("CapabilityMetadata id must be a non-empty string.")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("CapabilityMetadata name must be a non-empty string.")

        acts = self.actions
        if not isinstance(acts, tuple):
            object.__setattr__(self, "actions", tuple(acts if acts else ()))

        perms = self.permissions
        if not isinstance(perms, tuple):
            object.__setattr__(self, "permissions", tuple(perms if perms else ()))

        meta = self.metadata
        if not isinstance(meta, MappingProxyType):
            object.__setattr__(self, "metadata", _make_immutable_dict(meta))


class Capability(ABC):
    """Abstract Base Class representing an external capability contract."""

    @property
    @abstractmethod
    def metadata(self) -> CapabilityMetadata:
        """Return the metadata for this capability."""
        pass

    @property
    def status(self) -> CapabilityStatus:
        """Return the current lifecycle status of the capability. Default is REGISTERED."""
        return getattr(self, "_status", CapabilityStatus.REGISTERED)

    @status.setter
    def status(self, new_status: CapabilityStatus) -> None:
        """Set the lifecycle status of the capability."""
        self._status = new_status

    @abstractmethod
    def validate(self, request: CapabilityRequest) -> None:
        """Validate the request before execution."""
        pass

    @abstractmethod
    def execute(
        self, request: CapabilityRequest, context: CapabilityContext
    ) -> CapabilityResult:
        """Execute the capability request using the provided context."""
        pass
