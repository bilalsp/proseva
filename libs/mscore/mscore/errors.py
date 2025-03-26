from fastapi import HTTPException, status

MSCoreUserError = Exception  # MSCoreUserError similar to PydanticUserError

ForbiddenError = Exception

AuthenticationRequiredError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)

InvalidTokenError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"},
)
