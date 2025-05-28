from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_engine_from_config,
    async_sessionmaker,
)

from mscore.db.settings import DatabaseSettings


#
# base-class
#
class BaseDatabaseManager(ABC):
    @property
    @abstractmethod
    def db_name(self) -> str:
        ...

    @abstractmethod
    async def dispose(self) -> None:
        ...

    @abstractmethod
    def session(self) -> AsyncGenerator[AsyncSession, None]:
        ...


#
# PostgreSQL
#
class PostgresDatabaseManager(BaseDatabaseManager):
    def __init__(self, settings: DatabaseSettings, /, **kwargs):
        """It helps to manage the SQLAlchemy engine as well as session."""
        engine_config = settings.model_dump(mode="json")
        application_name = engine_config.pop("application_name")
        timeout = engine_config.pop("timeout")
        self._engine = async_engine_from_config(
            configuration=engine_config,
            prefix="",
            connect_args={
                "server_settings": {"application_name": application_name},
                "timeout": timeout,
            },
            **kwargs,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        self._db_name = settings.url.path.strip("/")

    @property
    def db_name(self) -> str:
        return self._db_name

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_maker() as session:
            yield session

    async def dispose(self) -> None:
        """Dispose connection pool used by the AsyncEngine."""
        await self._engine.dispose()


#
# Apache AGE
#
class ApacheAgeDatabaseManager(BaseDatabaseManager):
    ...


#
# Neo4j
#
class Neo4jDatabaseManager(BaseDatabaseManager):
    ...
