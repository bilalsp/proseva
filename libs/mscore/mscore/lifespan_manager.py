from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncIterator, Self

from fastapi import FastAPI
from starlette.types import Lifespan

if TYPE_CHECKING:
    from mscore.types import AppStateType, AppType


class LifespanManager:
    def __init__(self, lifespans: list[Lifespan[AppType]] | None = None, /) -> None:
        self.lifespans = lifespans or []

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[AppStateType]:
        state: dict[str, Any] = {}
        async with AsyncExitStack() as exit_stack:
            for lifespan in self.lifespans:
                sub_state = await exit_stack.enter_async_context(lifespan(app))
                if sub_state:
                    state.update(sub_state)
            yield state

    def add(self, lifespans: Lifespan[AppType] | list[Lifespan[AppType]]) -> Self:
        if not isinstance(lifespans, list):
            lifespans = [lifespans]
        self.lifespans.extend(lifespans)
        return self
