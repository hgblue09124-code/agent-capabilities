"""Typed capability error model."""

from typing import Any, Optional


class CapabilityError(Exception):
    """Base exception for all capability layer errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Return a machine-readable dictionary representation of the error."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class CapabilityNotFoundError(CapabilityError):
    """Raised when a requested capability ID is not found in the registry."""

    def __init__(self, capability_id: str, message: Optional[str] = None) -> None:
        msg = message or f"Capability '{capability_id}' not found."
        super().__init__(msg, details={"capability_id": capability_id})


class CapabilityDisabledError(CapabilityError):
    """Raised when an action is requested on a disabled capability."""

    def __init__(self, capability_id: str, message: Optional[str] = None) -> None:
        msg = message or f"Capability '{capability_id}' is disabled."
        super().__init__(msg, details={"capability_id": capability_id})


class CapabilityLifecycleError(CapabilityError):
    """Raised when an invalid lifecycle state transition is attempted."""

    def __init__(
        self, capability_id: str, current_status: str, target_status: str, message: Optional[str] = None
    ) -> None:
        msg = message or f"Invalid status transition for '{capability_id}': {current_status} -> {target_status}."
        super().__init__(
            msg,
            details={
                "capability_id": capability_id,
                "current_status": current_status,
                "target_status": target_status,
            },
        )


class CapabilityNotReadyError(CapabilityLifecycleError):
    """Raised when dispatching a capability that is not yet enabled (e.g. REGISTERED or AVAILABLE)."""

    def __init__(self, capability_id: str, status: str, message: Optional[str] = None) -> None:
        msg = message or f"Capability '{capability_id}' is not ready for execution (current status: {status}). Must be ENABLED."
        super().__init__(capability_id, current_status=status, target_status="ENABLED", message=msg)


class UnsupportedActionError(CapabilityError):
    """Raised when a capability does not support the requested action."""

    def __init__(self, capability_id: str, action: str, message: Optional[str] = None) -> None:
        msg = message or f"Capability '{capability_id}' does not support action '{action}'."
        super().__init__(msg, details={"capability_id": capability_id, "action": action})


class PermissionDeniedError(CapabilityError):
    """Raised when caller lacks required permissions for a capability execution."""

    def __init__(self, capability_id: str, missing_permissions: list[str], message: Optional[str] = None) -> None:
        msg = message or f"Permission denied for '{capability_id}'. Missing required permissions: {missing_permissions}."
        super().__init__(
            msg,
            details={
                "capability_id": capability_id,
                "missing_permissions": missing_permissions,
            },
        )


class CapabilityValidationError(CapabilityError):
    """Raised when input validation for a capability request fails."""

    def __init__(self, capability_id: str, action: str, message: str, details: Optional[dict[str, Any]] = None) -> None:
        all_details = {"capability_id": capability_id, "action": action}
        if details:
            all_details.update(details)
        super().__init__(message, details=all_details)


class CapabilityExecutionError(CapabilityError):
    """Raised when an error occurs during execution of a capability."""

    def __init__(
        self,
        capability_id: str,
        action: str,
        message: str,
        cause: Optional[Exception] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        all_details = {"capability_id": capability_id, "action": action}
        if details:
            all_details.update(details)
        if cause:
            all_details["cause_type"] = cause.__class__.__name__
            all_details["cause_message"] = str(cause)
        super().__init__(message, details=all_details)
        self.__cause__ = cause
