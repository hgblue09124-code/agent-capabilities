"""Trivial local Echo Capability for framework proof-of-concept."""

from typing import Any

from agent_capabilities.contracts.capability import Capability, CapabilityMetadata
from agent_capabilities.contracts.context import CapabilityContext
from agent_capabilities.contracts.request import CapabilityRequest
from agent_capabilities.contracts.result import CapabilityResult
from agent_capabilities.errors import (
    CapabilityValidationError,
    UnsupportedActionError,
)


class EchoCapability(Capability):
    """Example capability providing a deterministic local 'echo' action."""

    def __init__(self) -> None:
        self._metadata = CapabilityMetadata(
            id="echo",
            name="Echo Capability",
            version="1.0.0",
            description="Trivial local capability that echoes input messages deterministically.",
            actions=["echo"],
            permissions=[],  # No permissions required
        )

    @property
    def metadata(self) -> CapabilityMetadata:
        return self._metadata

    def validate(self, request: CapabilityRequest) -> None:
        if request.action != "echo":
            raise UnsupportedActionError(self.metadata.id, request.action)
        if "message" not in request.input:
            raise CapabilityValidationError(
                capability_id=self.metadata.id,
                action=request.action,
                message="Missing required field 'message' in request input.",
            )
        if not isinstance(request.input["message"], str):
            raise CapabilityValidationError(
                capability_id=self.metadata.id,
                action=request.action,
                message="Field 'message' must be a string.",
            )

    def execute(
        self, request: CapabilityRequest, context: CapabilityContext
    ) -> CapabilityResult:
        message = request.input["message"]
        return CapabilityResult(
            success=True,
            output={"echo": message},
            metadata={"request_id": context.request_id},
        )
