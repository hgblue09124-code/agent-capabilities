"""Tests for CapabilityDispatcher invocation boundary."""

import pytest

from agent_capabilities.contracts import CapabilityContext, CapabilityRequest, CapabilityStatus
from agent_capabilities.contracts.capability import Capability, CapabilityMetadata
from agent_capabilities.errors import (
    CapabilityDisabledError,
    CapabilityExecutionError,
    CapabilityNotFoundError,
    CapabilityValidationError,
    PermissionDeniedError,
    UnsupportedActionError,
)
from agent_capabilities.execution.dispatcher import CapabilityDispatcher
from agent_capabilities.examples.echo import EchoCapability
from agent_capabilities.registry.registry import CapabilityRegistry


class RestrictedCapability(Capability):
    """Dummy capability requiring permissions."""

    @property
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            id="restricted",
            name="Restricted Cap",
            version="1.0.0",
            description="Requires special permission",
            actions=["do_secret"],
            permissions=["secret.access"],
        )

    def validate(self, request: CapabilityRequest) -> None:
        pass

    def execute(self, request: CapabilityRequest, context: CapabilityContext):
        from agent_capabilities.contracts import CapabilityResult
        return CapabilityResult(success=True, output={"secret": "data"})


class BuggyCapability(Capability):
    """Dummy capability throwing unexpected exception during execution."""

    @property
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            id="buggy",
            name="Buggy Cap",
            version="1.0.0",
            description="Buggy capability",
            actions=["crash"],
            permissions=[],
        )

    def validate(self, request: CapabilityRequest) -> None:
        pass

    def execute(self, request: CapabilityRequest, context: CapabilityContext):
        raise RuntimeError("Unexpected internal crash")


def test_dispatcher_successful_execution_and_observability():
    registry = CapabilityRegistry()
    echo = EchoCapability()
    registry.register(echo, status=CapabilityStatus.ENABLED)

    dispatcher = CapabilityDispatcher(registry)
    events = []
    dispatcher.add_event_listener(lambda e: events.append(e))

    req = CapabilityRequest(
        capability_id="echo",
        action="echo",
        input={"message": "hello world"},
    )
    result = dispatcher.dispatch(req)

    assert result.success is True
    assert result.output == {"echo": "hello world"}

    assert len(events) == 1
    event = events[0]
    assert event.capability_id == "echo"
    assert event.action == "echo"
    assert event.success is True


def test_dispatcher_unknown_capability_raises_not_found():
    registry = CapabilityRegistry()
    dispatcher = CapabilityDispatcher(registry)

    req = CapabilityRequest(capability_id="unknown", action="echo")
    with pytest.raises(CapabilityNotFoundError):
        dispatcher.dispatch(req)


def test_dispatcher_disabled_capability_raises_disabled():
    registry = CapabilityRegistry()
    echo = EchoCapability()
    registry.register(echo, status=CapabilityStatus.DISABLED)

    dispatcher = CapabilityDispatcher(registry)
    req = CapabilityRequest(capability_id="echo", action="echo", input={"message": "test"})

    with pytest.raises(CapabilityDisabledError):
        dispatcher.dispatch(req)


def test_dispatcher_unsupported_action():
    registry = CapabilityRegistry()
    echo = EchoCapability()
    registry.register(echo, status=CapabilityStatus.ENABLED)

    dispatcher = CapabilityDispatcher(registry)
    req = CapabilityRequest(capability_id="echo", action="unsupported", input={"message": "test"})

    with pytest.raises(UnsupportedActionError):
        dispatcher.dispatch(req)


def test_dispatcher_permission_denied():
    registry = CapabilityRegistry()
    rest = RestrictedCapability()
    registry.register(rest, status=CapabilityStatus.ENABLED)

    dispatcher = CapabilityDispatcher(registry)

    # Dispatch without context permission
    req = CapabilityRequest(capability_id="restricted", action="do_secret")
    ctx = CapabilityContext(request_id="req-1", permissions=[])

    with pytest.raises(PermissionDeniedError) as exc_info:
        dispatcher.dispatch(req, context=ctx)

    assert "secret.access" in exc_info.value.details["missing_permissions"]

    # Dispatch with permission granted
    ctx_ok = CapabilityContext(request_id="req-1", permissions=["secret.access"])
    res = dispatcher.dispatch(req, context=ctx_ok)
    assert res.success is True


def test_dispatcher_validation_error():
    registry = CapabilityRegistry()
    echo = EchoCapability()
    registry.register(echo, status=CapabilityStatus.ENABLED)

    dispatcher = CapabilityDispatcher(registry)
    req = CapabilityRequest(capability_id="echo", action="echo", input={})  # Missing 'message'

    with pytest.raises(CapabilityValidationError):
        dispatcher.dispatch(req)


def test_dispatcher_unexpected_execution_error_wrapped():
    registry = CapabilityRegistry()
    buggy = BuggyCapability()
    registry.register(buggy, status=CapabilityStatus.ENABLED)

    dispatcher = CapabilityDispatcher(registry)
    req = CapabilityRequest(capability_id="buggy", action="crash")

    with pytest.raises(CapabilityExecutionError) as exc_info:
        dispatcher.dispatch(req)

    assert "Unexpected internal crash" in str(exc_info.value)
