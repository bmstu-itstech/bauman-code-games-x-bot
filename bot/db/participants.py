from __future__ import annotations

import datetime

import asyncpg

from bot.models.participant import Participant


async def get_participant(conn: asyncpg.Connection, tg_id: int) -> Participant | None:
    row = await conn.fetchrow(
        "SELECT * FROM participants WHERE id = $1", tg_id
    )
    if row is None:
        return None
    return _row_to_participant(row)


async def create_participant(
    conn: asyncpg.Connection,
    tg_id: int,
    username: str | None,
    full_name: str,
    birthdate: datetime.date,
    affiliation_type: str,
    bmstu_group: str | None = None,
    university: str | None = None,
) -> None:
    await conn.execute(
        """
        INSERT INTO participants (id, username, full_name, birthdate, affiliation_type, bmstu_group, university)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        tg_id, username, full_name, birthdate, affiliation_type, bmstu_group, university,
    )


def _row_to_participant(row: asyncpg.Record) -> Participant:
    return Participant(
        id=row["id"],
        username=row["username"],
        full_name=row["full_name"],
        birthdate=row["birthdate"],
        affiliation_type=row["affiliation_type"],
        bmstu_group=row["bmstu_group"],
        university=row["university"],
        created_at=row["created_at"],
    )
