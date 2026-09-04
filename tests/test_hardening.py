"""Comprehensive hardening and regression test suite for V1 requirements."""

import concurrent.futures
import pytest

from agent_capabilities.contracts import (
    CapabilityContext,
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResult,
    CapabilityStatus,
)
from agent_capabilities.errors import (
    CapabilityDisabledError,
    CapabilityExecutionError,
    CapabilityNotReadyError,
    PermissionDeniedError,
)
from agent_capabilities.execution.dispatcher import CapabilityDispatcher
from agent_capabilities.examples.echo import EchoCapability
from agent_capabilities.registry.registry import CapabilityRegistry


# --- 1. Exception Semantics & Observer Error Handling Tests ---

def test_observer_error_does_not_fail_capability_execution():
    registry = CapabilityRegistry()
    echo = EchoCapability()
    registry.register(echo, status=CapabilityStatus.ENABLED)

    dispatcher = CapabilityDispatcher(registry)

    def failing_listener(record):
        raise RuntimeError("Observer database down!")

    dispatcher.add_event_listener(failing_listener)

    req = CapabilityRequest(capability_id="echo", action="echo", input={"message": "test"})
    result = dispatcher.dispatch(req)

    assert result.success is True
    assert result.output == {"echo": "test"}
    assert len(dispatcher.observer_errors) == 1
    err, rec = dispatcher.observer_errors[0]
    assert isinstance(err, RuntimeError)
    assert str(err) == "Observer database down!"
    assert rec.capability_id == "echo"


# --- 2. Context & Metadata Immutability Tests ---

def test_capability_context_immutability():
    ctx = CapabilityContext(
        request_id="req-1",
        permissions=["filesystem.read"],
        metadata={"env": "prod"},
        cancellation_info={"timeout": 10},
    )

    # Attempting mutation on permissions set/frozenset should fail
    with pytest.raises(AttributeError):
        ctx.permissions.add("filesystem.write")

    # Attempting mutation on metadata dict proxy should fail
    with pytest.raises(TypeError):
        ctx.metadata["env"] = "dev"

    # Attempting mutation on cancellation_info dict proxy should fail
    with pytest.raises(TypeError):
        ctx.cancellation_info["timeout"] = 0


def test_capability_metadata_immutability():
    meta = CapabilityMetadata(
        id="cap-1",
        name="Cap 1",
        version="1.0.0",
        description="Test",
        actions=["act1"],
        permissions=["perm1"],
        metadata={"k": "v"},
    )

    with pytest.raises(TypeError):
        meta.metadata["k"] = "v2"


# --- 3. Lifecycle State Dispatch Enforcement Tests ---

def test_dispatch_from_all_lifecycle_states():
    registry = CapabilityRegistry()
    echo = EchoCapability()
    registry.register(echo, status=CapabilityStatus.REGISTERED)

    dispatcher = CapabilityDispatcher(registry)
    req = CapabilityRequest(capability_id="echo", action="echo", input={"message": "hello"})

    # Dispatch from REGISTERED -> fails with CapabilityNotReadyError
    with pytest.raises(CapabilityNotReadyError):
        dispatcher.dispatch(req)

    # Transition REGISTERED -> AVAILABLE -> fails with CapabilityNotReadyError
    registry.set_status("echo", CapabilityStatus.AVAILABLE)
    with pytest.raises(CapabilityNotReadyError):
        dispatcher.dispatch(req)

    # Transition AVAILABLE -> ENABLED -> succeeds
    registry.enable("echo")
    res = dispatcher.dispatch(req)
    assert res.success is True

    # Transition ENABLED -> DISABLED -> fails with CapabilityDisabledError
    registry.disable("echo")
    with pytest.raises(CapabilityDisabledError):
        dispatcher.dispatch(req)

    # Re-enable DISABLED -> ENABLED -> succeeds again
    registry.enable("echo")
    res2 = dispatcher.dispatch(req)
    assert res2.success is True


# --- 4. Contract Input Validation Tests ---

def test_invalid_contract_constructors():
    with pytest.raises(ValueError, match="request_id must be a non-empty string"):
        CapabilityContext(request_id="")

    with pytest.raises(ValueError, match="id must be a non-empty string"):
        CapabilityMetadata(id="", name="n", version="1", description="d")

    with pytest.raises(ValueError, match="capability_id must be a non-empty string"):
        CapabilityRequest(capability_id="", action="a")

    with pytest.raises(ValueError, match="action must be a non-empty string"):
        CapabilityRequest(capability_id="c", action="")

    with pytest.raises(ValueError, match="success must be a boolean"):
        CapabilityResult(success="not_a_bool")


# --- 5. Concurrent Registry Safety Tests ---

def test_concurrent_registry_access():
    registry = CapabilityRegistry()

    def worker(i):
        cap = EchoCapability()
        # Modifying metadata ID dynamically for concurrency test
        object.__setattr__(cap.metadata, "id", f"echo_{i}")
        registry.register(cap, status=CapabilityStatus.ENABLED)
        return registry.get(f"echo_{i}").metadata.id

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 20
    assert len(registry.list()) == 20
