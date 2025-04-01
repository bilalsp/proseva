from typing import AsyncGenerator, Callable

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from mscore.types import DatabaseMangerType


#
# fastapi dependency
#
def get_db_session(db_name: str) -> Callable:
    async def depends(request: Request) -> AsyncGenerator[AsyncSession, None]:
        db_manager: DatabaseMangerType = getattr(request.state, f"{db_name}_db_manager")
        async with db_manager.session() as session:
            yield session

    return depends
