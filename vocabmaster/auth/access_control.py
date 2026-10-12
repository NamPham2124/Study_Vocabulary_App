"""Multi-tenant isolation and access control checks."""

from typing import Any, Dict


class AccessDeniedError(Exception):
    """Raised when user attempts to access or mutate an unowned resource."""
    pass


def enforce_ownership(
    resource: Dict[str, Any], user_id: str, resource_name: str = "resource"
) -> None:
    """Ensure that the resource belongs to the requesting user."""
    resource_user_id = resource.get("user_id")
    if not resource_user_id or resource_user_id != user_id:
        raise AccessDeniedError(
            f"Access denied: User {user_id} does not own this {resource_name}"
        )
