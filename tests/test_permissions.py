"""Tests for permission model and boundary enforcement."""

import pytest

from agent_capabilities.permissions.model import check_permissions


def test_permission_granted_when_all_required_present():
    required = ["filesystem.read", "filesystem.write"]
    granted = ["filesystem.read", "filesystem.write", "network.read"]

    is_ok, missing = check_permissions(required, granted)
    assert is_ok is True
    assert len(missing) == 0


def test_permission_denied_when_required_missing():
    required = ["filesystem.read", "filesystem.write"]
    granted = ["filesystem.read"]

    is_ok, missing = check_permissions(required, granted)
    assert is_ok is False
    assert missing == {"filesystem.write"}


def test_extra_granted_permissions_do_not_affect_result():
    required = ["filesystem.read"]
    granted = ["filesystem.read", "admin.all"]

    is_ok, missing = check_permissions(required, granted)
    assert is_ok is True
    assert len(missing) == 0
