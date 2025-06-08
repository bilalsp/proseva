import socket
from typing import Callable

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_db_session
from ._dto import HealthCheckResult, HealthStatus

NETWORK_ERRORS = (socket.gaierror, ConnectionRefusedError, TimeoutError, OSError)


def db_check(db_name: str) -> Callable:
    """It creates a health check dependency for a specific database.

    Args:
        db_name: The name of the database to check the health.

    Returns:
        A FastAPI dependency function that performs the health check and returns a `HealthCheckResult`
    """
    check_name = f"{db_name}_db_check"

    async def depends(
        session: AsyncSession = Depends(get_db_session(db_name=db_name)),
    ) -> HealthCheckResult:
        try:
            await session.execute(text("SELECT 1"))
            return HealthCheckResult(name=check_name, status=HealthStatus.OK)
        except SQLAlchemyError as ex:
            return HealthCheckResult(
                name=check_name, status=HealthStatus.ERROR, detail=str(ex)
            )
        except NETWORK_ERRORS:
            return HealthCheckResult(
                name=check_name,
                status=HealthStatus.ERROR,
                detail=f"The {db_name} database is unreachable.",
            )

    depends.__name__ = check_name
    depends.__doc__ = (
        f"Performs a health check on {db_name} database by executing a simple query."
    )
    return depends


# TODO:
def keycloak_check():
    ...
