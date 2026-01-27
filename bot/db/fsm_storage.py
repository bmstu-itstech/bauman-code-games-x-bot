from __future__ import annotations

import json
from typing import Any

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType

from bot.db.pool import get_pool


class PgFSMStorage(BaseStorage):
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        pool = get_pool()
        state_str = state.state if isinstance(state, State) else state
        await pool.execute(
            """
            INSERT INTO fsm_states (chat_id, user_id, state, data)
            VALUES ($1, $2, $3, '{}')
            ON CONFLICT (chat_id, user_id)
            DO UPDATE SET state = $3
            """,
            key.chat_id, key.user_id, state_str,
        )

    async def get_state(self, key: StorageKey) -> str | None:
        pool = get_pool()
        return await pool.fetchval(
            "SELECT state FROM fsm_states WHERE chat_id = $1 AND user_id = $2",
            key.chat_id, key.user_id,
        )

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        pool = get_pool()
        await pool.execute(
            """
            INSERT INTO fsm_states (chat_id, user_id, state, data)
            VALUES ($1, $2, NULL, $3::jsonb)
            ON CONFLICT (chat_id, user_id)
            DO UPDATE SET data = $3::jsonb
            """,
            key.chat_id, key.user_id, json.dumps(data),
        )

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        pool = get_pool()
        val = await pool.fetchval(
            "SELECT data FROM fsm_states WHERE chat_id = $1 AND user_id = $2",
            key.chat_id, key.user_id,
        )
        if val is None:
            return {}
        if isinstance(val, str):
            return json.loads(val)
        return dict(val)

    async def close(self) -> None:
        pass
