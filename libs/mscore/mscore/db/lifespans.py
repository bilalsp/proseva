from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from mscore.types import AppType, DatabaseMangerType


class DatabaseLifespan:
    def __init__(self, database_manager: DatabaseMangerType, /) -> None:
        self.database_manager = database_manager

    @asynccontextmanager
    async def __call__(
        self, app: AppType
    ) -> AsyncGenerator[dict[str, DatabaseMangerType], None]:
        db_name = self.database_manager.db_name
        yield {f"{db_name}_db_manager": self.database_manager}
        await self.database_manager.dispose()
