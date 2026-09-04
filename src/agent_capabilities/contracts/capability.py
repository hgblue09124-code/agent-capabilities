"""Capability interface and metadata definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from agent_capabilities.contracts.context import CapabilityContext
from agent_capabilities.contracts.lifecycle import CapabilityStatus
from agent_capabilities.contracts.request import CapabilityRequest
from agent_capabilities.contracts.result import CapabilityResult


@dataclass(frozen=True)
class CapabilityMetadata:
    """Metadata declaring capability capabilities, requirements, and information."""

    id: str
    name: str
    version: str
    description: str
    actions: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


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
        """Validate the request before execution.

        Must raise CapabilityValidationError or UnsupportedActionError if invalid.
        Must NOT have arbitrary side effects or external network calls.
        """
        pass

    @abstractmethod
    def execute(
        self, request: CapabilityRequest, context: CapabilityContext
    ) -> CapabilityResult:
        """Execute the capability request using the provided context."""
        pass
