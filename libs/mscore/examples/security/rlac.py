from typing import Callable

from fastapi import APIRouter, Depends

from mscore import create_app
from mscore.dependencies import AuthenticationRequired, RowLevelSecurity
from mscore.security.rlac import ACE, Action, Authenticated, Everyone
from mscore.settings import AppSettings, get_settings

user_router = APIRouter()
USER_RESOURCE_ACL = [
    ACE(action=Action.Allow, principal=Authenticated, permissions="view"),
]


@user_router.get(
    "/users/{user_id}/based-on-static-acl",
    dependencies=[
        Depends(AuthenticationRequired),
        RowLevelSecurity("view", USER_RESOURCE_ACL),
    ],
)
def get_user_static_acl(user_id: int):
    return {"user_id": user_id}


@user_router.get("/users/{user_id}/based-on-dynamic-acl")
def get_user_dynamic_acl(
    user_id: int, assert_permission: Callable = RowLevelSecurity()
):
    principal = Authenticated if user_id == 1 else Everyone
    USER_RESOURCE_DAYNAMIC_ACL = [
        ACE(action=Action.Allow, principal=principal, permissions="view"),
    ]
    assert_permission("view", USER_RESOURCE_DAYNAMIC_ACL)
    return {"user_id": user_id}


#
# app
#
class TestAppSettings(AppSettings, env_file="examples/examples.env"):
    ...


settings: TestAppSettings = get_settings(TestAppSettings)

app = create_app(settings=settings)
app.include_router(router=user_router)
