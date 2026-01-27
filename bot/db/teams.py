from __future__ import annotations

import secrets

import asyncpg

from bot.db.participants import _row_to_participant
from bot.models.participant import Participant
from bot.models.team import Team


def generate_team_id() -> str:
    return secrets.token_hex(4)


async def create_team(
    conn: asyncpg.Connection,
    name: str,
    captain_id: int,
) -> Team:
    team_id = generate_team_id()
    await conn.execute(
        "INSERT INTO teams (id, name, captain_id) VALUES ($1, $2, $3)",
        team_id, name, captain_id,
    )
    await conn.execute(
        "INSERT INTO team_members (team_id, participant_id) VALUES ($1, $2)",
        team_id, captain_id,
    )
    return Team(id=team_id, name=name, captain_id=captain_id)


async def get_team(conn: asyncpg.Connection, team_id: str) -> Team | None:
    row = await conn.fetchrow("SELECT * FROM teams WHERE id = $1", team_id)
    if row is None:
        return None
    members = await _get_members(conn, team_id)
    return Team(
        id=row["id"].strip(),
        name=row["name"],
        captain_id=row["captain_id"],
        members=members,
        created_at=row["created_at"],
    )


async def get_team_by_participant(conn: asyncpg.Connection, participant_id: int) -> Team | None:
    row = await conn.fetchrow(
        """
        SELECT t.* FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE tm.participant_id = $1
        """,
        participant_id,
    )
    if row is None:
        return None
    team_id = row["id"].strip()
    members = await _get_members(conn, team_id)
    return Team(
        id=team_id,
        name=row["name"],
        captain_id=row["captain_id"],
        members=members,
        created_at=row["created_at"],
    )


async def team_name_exists(conn: asyncpg.Connection, name: str) -> bool:
    val = await conn.fetchval("SELECT 1 FROM teams WHERE name = $1", name)
    return val is not None


async def add_member(conn: asyncpg.Connection, team_id: str, participant_id: int) -> None:
    await conn.execute(
        "INSERT INTO team_members (team_id, participant_id) VALUES ($1, $2)",
        team_id, participant_id,
    )


async def remove_member(conn: asyncpg.Connection, team_id: str, participant_id: int) -> None:
    await conn.execute(
        "DELETE FROM team_members WHERE team_id = $1 AND participant_id = $2",
        team_id, participant_id,
    )


async def member_count(conn: asyncpg.Connection, team_id: str) -> int:
    val = await conn.fetchval(
        "SELECT count(*) FROM team_members WHERE team_id = $1", team_id
    )
    return int(val)


async def delete_team(conn: asyncpg.Connection, team_id: str) -> None:
    await conn.execute("DELETE FROM teams WHERE id = $1", team_id)


async def set_captain(conn: asyncpg.Connection, team_id: str, new_captain_id: int) -> None:
    await conn.execute(
        "UPDATE teams SET captain_id = $1 WHERE id = $2",
        new_captain_id, team_id,
    )


async def _get_members(conn: asyncpg.Connection, team_id: str) -> list[Participant]:
    rows = await conn.fetch(
        """
        SELECT p.* FROM participants p
        JOIN team_members tm ON p.id = tm.participant_id
        WHERE tm.team_id = $1
        """,
        team_id,
    )
    return [_row_to_participant(r) for r in rows]
