from typing import TypeVar

from fastapi import FastAPI

from mscore.db.managers import BaseDatabaseManager

AppType = TypeVar("AppType", bound=FastAPI)
AppStateType = TypeVar("AppStateType", bound=dict)
DatabaseMangerType = TypeVar("DatabaseMangerType", bound="BaseDatabaseManager")
