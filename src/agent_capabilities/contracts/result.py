"""Capability result definition."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class CapabilityResult:
    """Result returned by a capability execution."""

    success: bool
    output: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the result."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }
