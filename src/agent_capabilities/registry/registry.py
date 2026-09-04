"""Thread-safe Capability Registry."""

import threading
from typing import Dict, List, Optional

from agent_capabilities.contracts.capability import Capability
from agent_capabilities.contracts.lifecycle import CapabilityStatus, can_transition
from agent_capabilities.errors import (
    CapabilityError,
    CapabilityLifecycleError,
    CapabilityNotFoundError,
)


class CapabilityRegistry:
    """Registry responsible for capability registration, lookup, and lifecycle management."""

    def __init__(self) -> None:
        self._capabilities: Dict[str, Capability] = {}
        self._lock = threading.RLock()

    def register(self, capability: Capability, status: CapabilityStatus = CapabilityStatus.REGISTERED) -> None:
        """Register a new capability.

        Raises:
            CapabilityError: If capability ID is already registered.
        """
        cap_id = capability.metadata.id
        with self._lock:
            if cap_id in self._capabilities:
                raise CapabilityError(f"Capability '{cap_id}' is already registered.")
            capability.status = status
            self._capabilities[cap_id] = capability

    def unregister(self, capability_id: str) -> None:
        """Unregister a capability by ID.

        Raises:
            CapabilityNotFoundError: If capability ID is not registered.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise CapabilityNotFoundError(capability_id)
            del self._capabilities[capability_id]

    def get(self, capability_id: str) -> Capability:
        """Get a capability by ID.

        Raises:
            CapabilityNotFoundError: If capability ID is not registered.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise CapabilityNotFoundError(capability_id)
            return self._capabilities[capability_id]

    def list(self, status: Optional[CapabilityStatus] = None) -> List[Capability]:
        """List registered capabilities, optionally filtered by status."""
        with self._lock:
            if status is None:
                return list(self._capabilities.values())
            return [cap for cap in self._capabilities.values() if cap.status == status]

    def set_status(self, capability_id: str, target_status: CapabilityStatus) -> None:
        """Transition a capability to a new lifecycle status.

        Raises:
            CapabilityNotFoundError: If capability ID is not registered.
            CapabilityLifecycleError: If the status transition is invalid.
        """
        with self._lock:
            capability = self.get(capability_id)
            current_status = capability.status
            if not can_transition(current_status, target_status):
                raise CapabilityLifecycleError(capability_id, current_status.value, target_status.value)
            capability.status = target_status

    def enable(self, capability_id: str) -> None:
        """Enable a capability."""
        self.set_status(capability_id, CapabilityStatus.ENABLED)

    def disable(self, capability_id: str) -> None:
        """Disable a capability."""
        self.set_status(capability_id, CapabilityStatus.DISABLED)
