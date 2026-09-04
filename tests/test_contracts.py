"""Tests for core contract dataclasses and interfaces."""

from agent_capabilities.contracts import (
    CapabilityContext,
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResult,
    CapabilityStatus,
    ExecutionRecord,
)


def test_capability_context_immutable_and_defaults():
    ctx = CapabilityContext(request_id="req-123", permissions=["filesystem.read"])
    assert ctx.request_id == "req-123"
    assert "filesystem.read" in ctx.permissions
    assert ctx.caller is None
    assert ctx.metadata == {}


def test_capability_request_and_result_serialization():
    req = CapabilityRequest(
        capability_id="test_cap",
        action="test_action",
        input={"key": "value"},
    )
    assert req.capability_id == "test_cap"
    assert req.action == "test_action"
    assert req.input == {"key": "value"}

    res = CapabilityResult(
        success=True,
        output={"result": 42},
        metadata={"cost": 0},
    )
    res_dict = res.to_dict()
    assert res_dict["success"] is True
    assert res_dict["output"] == {"result": 42}
    assert res_dict["error"] is None


def test_execution_record():
    record = ExecutionRecord(
        request_id="req-1",
        capability_id="echo",
        action="echo",
        timestamp=1000.0,
        duration_seconds=0.01,
        success=True,
    )
    assert record.request_id == "req-1"
    assert record.success is True
