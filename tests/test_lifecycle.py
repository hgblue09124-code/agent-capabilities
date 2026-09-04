"""Tests for Capability lifecycle management."""

import pytest

from agent_capabilities.contracts.lifecycle import CapabilityStatus, can_transition
from agent_capabilities.examples.echo import EchoCapability
from agent_capabilities.registry.registry import CapabilityRegistry


def test_can_transition_rules():
    assert can_transition(CapabilityStatus.REGISTERED, CapabilityStatus.AVAILABLE)
    assert can_transition(CapabilityStatus.AVAILABLE, CapabilityStatus.ENABLED)
    assert can_transition(CapabilityStatus.ENABLED, CapabilityStatus.DISABLED)
    assert can_transition(CapabilityStatus.DISABLED, CapabilityStatus.ENABLED)
    assert can_transition(CapabilityStatus.REGISTERED, CapabilityStatus.REGISTERED)

    # Invalid transitions
    assert not can_transition(CapabilityStatus.REGISTERED, CapabilityStatus.ENABLED)


def test_registry_lifecycle_status_transitions():
    registry = CapabilityRegistry()
    echo = EchoCapability()
    registry.register(echo, status=CapabilityStatus.REGISTERED)

    assert echo.status == CapabilityStatus.REGISTERED

    registry.set_status("echo", CapabilityStatus.AVAILABLE)
    assert echo.status == CapabilityStatus.AVAILABLE

    registry.enable("echo")
    assert echo.status == CapabilityStatus.ENABLED

    registry.disable("echo")
    assert echo.status == CapabilityStatus.DISABLED
