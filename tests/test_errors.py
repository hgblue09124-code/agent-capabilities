"""Tests for typed capability error model."""

import pytest

from agent_capabilities.errors import (
    CapabilityDisabledError,
    CapabilityError,
    CapabilityExecutionError,
    CapabilityLifecycleError,
    CapabilityNotFoundError,
    CapabilityValidationError,
    PermissionDeniedError,
    UnsupportedActionError,
)


def test_base_capability_error_to_dict():
    err = CapabilityError("Something went wrong", details={"code": 500})
    d = err.to_dict()
    assert d["error_type"] == "CapabilityError"
    assert d["message"] == "Something went wrong"
    assert d["details"] == {"code": 500}


def test_typed_errors_details():
    not_found = CapabilityNotFoundError("cap1")
    assert not_found.details["capability_id"] == "cap1"

    disabled = CapabilityDisabledError("cap1")
    assert disabled.details["capability_id"] == "cap1"

    lifecycle_err = CapabilityLifecycleError("cap1", "REGISTERED", "ENABLED")
    assert lifecycle_err.details["current_status"] == "REGISTERED"
    assert lifecycle_err.details["target_status"] == "ENABLED"

    unsupported = UnsupportedActionError("cap1", "invalid_action")
    assert unsupported.details["action"] == "invalid_action"

    perm_err = PermissionDeniedError("cap1", ["filesystem.write"])
    assert perm_err.details["missing_permissions"] == ["filesystem.write"]

    val_err = CapabilityValidationError("cap1", "act1", "Invalid input")
    assert val_err.details["capability_id"] == "cap1"

    cause = ValueError("Invalid argument")
    exec_err = CapabilityExecutionError("cap1", "act1", "Execution failed", cause=cause)
    assert exec_err.__cause__ == cause
    assert exec_err.details["cause_type"] == "ValueError"
