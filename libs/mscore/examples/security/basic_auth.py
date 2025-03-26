"""
[REFERENCE]
- fastapi = "0.110.0"
- https://fastapi.tiangolo.com/advanced/security/http-basic-auth/
"""
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

#
# dependencies
#
security = HTTPBasic()


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"test"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"pwd"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


#
# routes
#
router = APIRouter()


@router.get("/users/me")
def read_current_user(
    username: Annotated[str, Depends(get_current_username)],
) -> dict[str, str]:
    return {"username": username}


#
# app
#
app = FastAPI()
app.include_router(router=router)
