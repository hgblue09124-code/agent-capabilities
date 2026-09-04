"""Capability invocation dispatcher and execution records."""

import logging
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
    CapabilityNotReadyError,

    CapabilityNotFoundError,
    CapabilityValidationError,
    PermissionDeniedError,
    UnsupportedActionError,
)
from agent_capabilities.permissions.model import check_permissions
from agent_capabilities.registry.registry import CapabilityRegistry

logger = logging.getLogger(__name__)


class CapabilityDispatcher:
    """Invocation boundary responsible for validating and dispatching capability requests."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        on_observer_error: Optional[Callable[[Exception, ExecutionRecord], None]] = None,
    ) -> None:
        self.registry = registry
        self._event_listeners: List[Callable[[ExecutionRecord], None]] = []
        self._on_observer_error = on_observer_error or self._default_observer_error_handler
        self._observer_errors: List[tuple[Exception, ExecutionRecord]] = []

    def _default_observer_error_handler(self, exc: Exception, record: ExecutionRecord) -> None:
        """Default handler for observer exceptions. Records error without hiding it."""
        logger.error(
            "Observer error handling ExecutionRecord for capability '%s', action '%s': %s",
            record.capability_id,
            record.action,
            exc,
            exc_info=True,
        )
        self._observer_errors.append((exc, record))

    @property
    def observer_errors(self) -> List[tuple[Exception, ExecutionRecord]]:
        """Return list of observer errors recorded during dispatch operations."""
        return list(self._observer_errors)

    def add_event_listener(self, listener: Callable[[ExecutionRecord], None]) -> None:
        """Register a callback to receive ExecutionRecord events."""
        self._event_listeners.append(listener)

    def dispatch(
        self, request: CapabilityRequest, context: Optional[CapabilityContext] = None
    ) -> CapabilityResult:
        """Dispatch a capability invocation request."""
        start_time = time.time()
        req_ctx = context or request.context or CapabilityContext(request_id=str(uuid.uuid4()))
        cap_id = request.capability_id
        action = request.action

        try:
            # 1. Resolve capability
            capability = self.registry.get(cap_id)

            # 2. Lifecycle check (ONLY ENABLED IS EXECUTABLE)
            if capability.status == CapabilityStatus.DISABLED:
                raise CapabilityDisabledError(cap_id)
            elif capability.status != CapabilityStatus.ENABLED:
                raise CapabilityNotReadyError(cap_id, capability.status.value)

            # 3. Action check
            metadata = capability.metadata
            if action not in metadata.actions:
                raise UnsupportedActionError(cap_id, action)

            # 4. Permission boundary check
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
            except Exception as exc:
                try:
                    self._on_observer_error(exc, record)
                except Exception as handler_exc:
                    logger.critical(
                        "Observer error handler failed: %s (original observer error: %s)",
                        handler_exc,
                        exc,
                        exc_info=True,
                    )
