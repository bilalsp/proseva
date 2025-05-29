#
# Row-level access control (RLAC) / Row-level Permission (aka record-level permission)
#
import functools
from enum import Enum
from typing import Any, Callable, Literal

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

from ..externals.fastapi import SecurityAcl, params
from ..schemas import CurrentUser
from ._errors import MSCoreUserError


class Action(Enum):
    Allow: str = "allow"
    Deny: str = "deny"

    def __repr__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return repr(self)


class Principal(BaseModel, frozen=True):
    key: str
    value: str

    def __repr__(self) -> str:
        return f"{self.key}:{self.value}"

    def __str__(self) -> str:
        return repr(self)


class SystemPrincipal(Principal, frozen=True):
    key: Literal["system"] = "system"


class UserPrincipal(Principal, frozen=True):
    key: Literal["user"] = "user"


class RolePrincipal(Principal, frozen=True):
    key: Literal["role"] = "role"


class _AllPermissions(BaseModel):
    def __contains__(self, item: Any) -> bool:
        return True

    def __repr__(self) -> str:
        return "*"

    def __str__(self) -> str:
        return repr(self)


class ACE(BaseModel, frozen=True):
    """Access Control Entity (ACE)."""

    action: Action
    principal: Principal
    permissions: str | set[str] | _AllPermissions


# aliases
Everyone = SystemPrincipal(value="everyone")
Authenticated = SystemPrincipal(value="authenticated")
AllPermissions = _AllPermissions()
ALLOW_ALL = ACE(action=Action.Allow, principal=Everyone, permissions=AllPermissions)
DENY_ALL = ACE(action=Action.Deny, principal=Everyone, permissions=AllPermissions)


class RowLevelAccessControl:
    def __init__(
        self, user_principals_func: Callable[[CurrentUser | None], list[Principal]]
    ) -> None:
        """Declarative security system to determines whether current user has access
            to certain resources (authorization).

        Args:
            user_principals_func: Function which should provide current user's principals.
        """
        self.user_principals_func = user_principals_func

    def __call__(
        self, required_permission: str | None = None, resource: Any | None = None
    ) -> params.SecurityAcl:
        if (required_permission is None) ^ (resource is None):
            raise MSCoreUserError("either provide both parameters or none of them.")

        def _permission_dependency(
            principals: list[Principal] = Depends(self.user_principals_func),
        ) -> Callable[[str, Any], None] | None:
            if required_permission is None:
                return functools.partial(self.assert_permission, principals)
            return self.assert_permission(
                principals=principals,
                required_permission=required_permission,
                resource=resource,
            )

        return SecurityAcl(_permission_dependency, acl=self.get_acl(resource))

    @staticmethod
    def assert_permission(
        principals: list[Principal], required_permission: str, resource: Any
    ) -> None:
        """Raise exception if given principals does not have required permission to access given resource."""
        if not RowLevelAccessControl.has_permission(
            principals=principals,
            required_permission=required_permission,
            resource=resource,
        ):
            acl = RowLevelAccessControl.get_acl(resource=resource)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Current user does not have sufficient permissions to access this resource. "
                    f"User must be allowed in this acl {acl} with '{required_permission}' permission."
                ),
            )

    @staticmethod
    def has_permission(
        principals: list[Principal], required_permission: str, resource: Any
    ) -> bool:
        """Check given principals have required permission to access given resource."""
        acl = RowLevelAccessControl.get_acl(resource=resource)
        for ace in acl:
            action, principal, permissions = ace.action, ace.principal, ace.permissions

            if isinstance(permissions, str):
                permissions = {permissions}

            if (
                principal in principals
                and action == Action.Allow
                and required_permission in permissions
            ):
                return True
        return False

    @staticmethod
    def get_acl(resource: Any) -> list[ACE]:
        """Returns the ACL(access control list) associated to given resource."""
        acl = getattr(resource, "__acl__", resource)
        acl = acl() if callable(acl) else acl
        return acl if isinstance(acl, list) else []
