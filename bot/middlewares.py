from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from bot.db.pool import get_pool

logger = logging.getLogger(__name__)

# All valid FSM state strings
_VALID_STATES: set[str | None] = {None}


def register_valid_states() -> None:
    from bot.handlers.registration import RegFSM
    from bot.handlers.team_create import CreateTeamFSM
    from bot.handlers.team_join import JoinTeamFSM

    for group in (RegFSM, CreateTeamFSM, JoinTeamFSM):
        for state in group.__all_states__:
            _VALID_STATES.add(state.state)


class DbMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        pool = get_pool()
        async with pool.acquire() as conn:
            data["conn"] = conn
            return await handler(event, data)


class FSMResetMiddleware(BaseMiddleware):
    """Reset FSM to initial state if the persisted state is invalid."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        state: FSMContext | None = data.get("state")
        if state is not None:
            current = await state.get_state()
            if current not in _VALID_STATES:
                logger.warning("Invalid FSM state %r — resetting to initial", current)
                await state.clear()
        return await handler(event, data)
