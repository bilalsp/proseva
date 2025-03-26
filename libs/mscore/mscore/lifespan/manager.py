from __future__ import annotations

from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, AsyncContextManager, AsyncIterator, Callable, TypeAlias

from fastapi import FastAPI

TAppState: TypeAlias = dict[str, Any]
TLifespan: TypeAlias = Callable[[FastAPI], AsyncContextManager[TAppState]]


class LifespanManager:
    def __init__(self, lifespans: list[TLifespan] | None = None, /) -> None:
        self.lifespans = lifespans or []

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[TAppState]:
        state: dict[str, Any] = {}
        async with AsyncExitStack() as exit_stack:
            for lifespan in self.lifespans:
                sub_state = await exit_stack.enter_async_context(lifespan(app))
                if sub_state:
                    state.update(sub_state)
            yield state

    def add(self, lifespan: TLifespan) -> LifespanManager:
        self.lifespans.append(lifespan)
        return self

    def extend(self, lifespans: list[TLifespan]) -> LifespanManager:
        self.lifespans.extend(lifespans)
        return self
