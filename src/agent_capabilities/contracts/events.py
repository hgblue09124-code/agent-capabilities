"""Observability events and execution records."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ExecutionRecord:
    """Lightweight structured event recording a capability invocation."""

    request_id: str
    capability_id: str
    action: str
    timestamp: float
    duration_seconds: float
    success: bool
    caller: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
