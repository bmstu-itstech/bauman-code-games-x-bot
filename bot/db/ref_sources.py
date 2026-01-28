from __future__ import annotations

import asyncpg


async def ref_source_exists(conn: asyncpg.Connection, code: str) -> bool:
    row = await conn.fetchval(
        "SELECT 1 FROM ref_sources WHERE code = $1", code
    )
    return row is not None
