"""Capability invocation dispatcher and execution records."""

import time
import uuid
from typing import Callable, List, Optional

from agent_capabilities.contracts.context import CapabilityContext
from agent_capabilities.contracts.events import ExecutionRecord
from agent_capabilities.contracts.lifecycle import CapabilityStatus
from agent_capabilities.contracts.request import CapabilityRequest
from agent_capabilities.contracts.result import CapabilityResult
from agent_capabilities.errors import (
    CapabilityDisabledError,
    CapabilityError,
    CapabilityExecutionError,
    CapabilityNotFoundError,
    CapabilityValidationError,
    PermissionDeniedError,
    UnsupportedActionError,
)
from agent_capabilities.permissions.model import check_permissions
from agent_capabilities.registry.registry import CapabilityRegistry


class CapabilityDispatcher:
    """Invocation boundary responsible for validating and dispatching capability requests."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry
        self._event_listeners: List[Callable[[ExecutionRecord], None]] = []

    def add_event_listener(self, listener: Callable[[ExecutionRecord], None]) -> None:
        """Register a callback to receive ExecutionRecord events."""
        self._event_listeners.append(listener)

    def dispatch(
        self, request: CapabilityRequest, context: Optional[CapabilityContext] = None
    ) -> CapabilityResult:
        """Dispatch a capability invocation request.

        Workflow:
        1. Context resolution
        2. Resolve capability from registry
        3. Lifecycle check (must be AVAILABLE or ENABLED)
        4. Action check
        5. Permission boundary check
        6. Input validation (call capability.validate)
        7. Execution (call capability.execute)
        8. Record event & return CapabilityResult

        Typed errors raised during validation/permission/execution are wrapped or returned as failed CapabilityResult or re-raised depending on level.
        Note: The dispatcher handles framework-level validation cleanly. Unexpected exceptions during execution are wrapped in CapabilityExecutionError or captured in result.
        """
        start_time = time.time()
        req_ctx = context or request.context or CapabilityContext(request_id=str(uuid.uuid4()))
        cap_id = request.capability_id
        action = request.action

        try:
            # 1. Resolve capability
            capability = self.registry.get(cap_id)

            # 2. Lifecycle check
            if capability.status == CapabilityStatus.DISABLED:
                raise CapabilityDisabledError(cap_id)

            # 3. Action check
            metadata = capability.metadata
            if action not in metadata.actions:
                raise UnsupportedActionError(cap_id, action)

            # 4. Permission boundary check
            # Check if required permissions by capability for this action/overall are met by context
            is_permitted, missing_perms = check_permissions(
                required_permissions=metadata.permissions,
                granted_permissions=req_ctx.permissions,
            )
            if not is_permitted:
                raise PermissionDeniedError(cap_id, list(missing_perms))

            # 5. Input validation
            capability.validate(request)

            # 6. Execute capability
            result = capability.execute(request, req_ctx)

            duration = time.time() - start_time
            self._emit_record(
                ExecutionRecord(
                    request_id=req_ctx.request_id,
                    capability_id=cap_id,
                    action=action,
                    timestamp=start_time,
                    duration_seconds=duration,
                    success=result.success,
                    caller=req_ctx.caller,
                    error_type=result.error.get("error_type") if result.error else None,
                    error_message=result.error.get("message") if result.error else None,
                    metadata=result.metadata,
                )
            )
            return result

        except CapabilityError as exc:
            duration = time.time() - start_time
            self._emit_record(
                ExecutionRecord(
                    request_id=req_ctx.request_id,
                    capability_id=cap_id,
                    action=action,
                    timestamp=start_time,
                    duration_seconds=duration,
                    success=False,
                    caller=req_ctx.caller,
                    error_type=exc.__class__.__name__,
                    error_message=exc.message,
                    metadata=exc.details,
                )
            )
            raise exc

        except Exception as exc:
            # Unexpected execution or framework error
            duration = time.time() - start_time
            exec_err = CapabilityExecutionError(
                capability_id=cap_id,
                action=action,
                message=f"Unexpected error during execution of '{cap_id}': {str(exc)}",
                cause=exc,
            )
            self._emit_record(
                ExecutionRecord(
                    request_id=req_ctx.request_id,
                    capability_id=cap_id,
                    action=action,
                    timestamp=start_time,
                    duration_seconds=duration,
                    success=False,
                    caller=req_ctx.caller,
                    error_type=exec_err.__class__.__name__,
                    error_message=exec_err.message,
                    metadata=exec_err.details,
                )
            )
            raise exec_err from exc

    def _emit_record(self, record: ExecutionRecord) -> None:
        for listener in self._event_listeners:
            try:
                listener(record)
            except Exception:
                pass
