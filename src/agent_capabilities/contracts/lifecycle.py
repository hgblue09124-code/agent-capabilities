"""Capability lifecycle definitions."""

from enum import Enum
from typing import Set


class CapabilityStatus(str, Enum):
    """Lifecycle statuses for a capability."""

    REGISTERED = "REGISTERED"
    AVAILABLE = "AVAILABLE"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


# Map of allowed status transitions: current_status -> set of allowed next statuses
ALLOWED_TRANSITIONS: dict[CapabilityStatus, Set[CapabilityStatus]] = {
    CapabilityStatus.REGISTERED: {CapabilityStatus.AVAILABLE, CapabilityStatus.DISABLED},
    CapabilityStatus.AVAILABLE: {CapabilityStatus.ENABLED, CapabilityStatus.DISABLED},
    CapabilityStatus.ENABLED: {CapabilityStatus.DISABLED},
    CapabilityStatus.DISABLED: {CapabilityStatus.ENABLED, CapabilityStatus.AVAILABLE},
}


def can_transition(current: CapabilityStatus, target: CapabilityStatus) -> bool:
    """Check if transitioning from current to target status is valid."""
    if current == target:
        return True
    return target in ALLOWED_TRANSITIONS.get(current, set())
