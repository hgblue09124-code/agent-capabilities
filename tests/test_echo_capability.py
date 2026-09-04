"""Tests for proof-of-concept Echo Capability."""

import pytest

from agent_capabilities.contracts import CapabilityContext, CapabilityRequest
from agent_capabilities.errors import CapabilityValidationError, UnsupportedActionError
from agent_capabilities.examples.echo import EchoCapability


def test_echo_capability_metadata():
    echo = EchoCapability()
    meta = echo.metadata
    assert meta.id == "echo"
    assert "echo" in meta.actions
    assert len(meta.permissions) == 0


def test_echo_capability_validation():
    echo = EchoCapability()

    # Valid request
    req_valid = CapabilityRequest(capability_id="echo", action="echo", input={"message": "hello"})
    echo.validate(req_valid)

    # Invalid action
    req_bad_action = CapabilityRequest(capability_id="echo", action="invalid", input={"message": "hello"})
    with pytest.raises(UnsupportedActionError):
        echo.validate(req_bad_action)

    # Missing message field
    req_missing = CapabilityRequest(capability_id="echo", action="echo", input={})
    with pytest.raises(CapabilityValidationError, match="Missing required field 'message'"):
        echo.validate(req_missing)

    # Non-string message
    req_bad_type = CapabilityRequest(capability_id="echo", action="echo", input={"message": 123})
    with pytest.raises(CapabilityValidationError, match="must be a string"):
        echo.validate(req_bad_type)


def test_echo_capability_determinism():
    echo = EchoCapability()
    ctx = CapabilityContext(request_id="req-123")
    req = CapabilityRequest(capability_id="echo", action="echo", input={"message": "repeat test"})

    res1 = echo.execute(req, ctx)
    res2 = echo.execute(req, ctx)

    assert res1.success is True
    assert res1.output == res2.output == {"echo": "repeat test"}
