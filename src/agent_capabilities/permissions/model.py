"""Permission model and boundary enforcement logic."""

from typing import Iterable, Set, Union


def check_permissions(
    required_permissions: Iterable[str],
    granted_permissions: Iterable[str],
) -> tuple[bool, set[str]]:
    """Check if all required permissions are present in granted permissions.

    Returns:
        (is_granted, missing_permissions_set)
    """
    req_set = set(required_permissions)
    granted_set = set(granted_permissions)
    missing = req_set - granted_set
    return len(missing) == 0, missing
