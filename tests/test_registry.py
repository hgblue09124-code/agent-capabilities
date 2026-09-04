"""Tests for CapabilityRegistry."""

import pytest

from agent_capabilities.contracts.lifecycle import CapabilityStatus
from agent_capabilities.errors import CapabilityError, CapabilityNotFoundError
from agent_capabilities.examples.echo import EchoCapability
from agent_capabilities.registry.registry import CapabilityRegistry


def test_register_get_and_list():
    registry = CapabilityRegistry()
    echo = EchoCapability()

    registry.register(echo, status=CapabilityStatus.ENABLED)
    retrieved = registry.get("echo")
    assert retrieved is echo

    caps = registry.list()
    assert len(caps) == 1
    assert caps[0] is echo

    enabled_caps = registry.list(status=CapabilityStatus.ENABLED)
    assert len(enabled_caps) == 1

    disabled_caps = registry.list(status=CapabilityStatus.DISABLED)
    assert len(disabled_caps) == 0


def test_duplicate_registration_raises_error():
    registry = CapabilityRegistry()
    echo = EchoCapability()

    registry.register(echo)
    with pytest.raises(CapabilityError, match="already registered"):
        registry.register(echo)


def test_get_unknown_capability_raises_error():
    registry = CapabilityRegistry()
    with pytest.raises(CapabilityNotFoundError):
        registry.get("nonexistent")


def test_unregister_capability():
    registry = CapabilityRegistry()
    echo = EchoCapability()

    registry.register(echo)
    registry.unregister("echo")

    with pytest.raises(CapabilityNotFoundError):
        registry.get("echo")


def test_unregister_unknown_raises_error():
    registry = CapabilityRegistry()
    with pytest.raises(CapabilityNotFoundError):
        registry.unregister("unknown")
