from __future__ import annotations

import asyncpg


async def get_ref_code(conn: asyncpg.Connection, code: str) -> str | None:
    return await conn.fetchval(
        "SELECT code FROM ref_sources WHERE LOWER(code) = LOWER($1)", code
    )
