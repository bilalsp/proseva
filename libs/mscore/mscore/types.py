from typing import TypeVar

from fastapi import FastAPI

from mscore.db.managers import BaseDatabaseManager

AppType = TypeVar("AppType", bound=FastAPI)
DatabaseMangerType = TypeVar("DatabaseMangerType", bound="BaseDatabaseManager")
