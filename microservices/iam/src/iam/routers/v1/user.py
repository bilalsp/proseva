from typing import Annotated
from fastapi import APIRouter, Depends
from mscore.security.rlac import Principal
from mscore.dependencies import get_token, get_current_user, get_current_user_principals, RowLevelSecurity
from mscore.schemas import CurrentUser

test_router = APIRouter()


@test_router.get("/unprotected-endpoint")
async def unprotected_endpoint(): ...


@test_router.get("/protected-endpoint", dependencies=[Depends(get_token)])
async def protected_endpoint(): ...


@test_router.get("/active-user")
async def get_current_user(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    """ """
    return user


@test_router.get("/active-user-principals")
async def get_principals(principals: Annotated[list[Principal], Depends(get_current_user_principals)]) -> list[str]:
    """ """
    return map(str, principals)


class UserService:
    def __init__(self, assert_access = RowLevelSecurity()) -> None:
        self.assert_access = assert_access
    
    def get_user(self, user_id):
        from pydantic import BaseModel
        class User(BaseModel):
            name: str
            
            def __acl__():
                return []

        resource = User(name="dummy_name")
        # Does current-user have permission to view this resource??
        self.assert_access("view", resource)



from mscore.security.rlac import ALLOW_ALL

@test_router.get("/users/{user_id}", dependencies=[RowLevelSecurity("view", [ALLOW_ALL])])
def get_user(user_id: int, service: UserService = Depends()):
    return service.get_user(user_id)
