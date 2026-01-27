from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery
import asyncpg

from bot.db import teams as db_teams
from bot.keyboards import main_menu_kb
from bot.templates import render

router = Router()


@router.callback_query(F.data == "team_leave")
async def on_leave(cb: CallbackQuery, conn: asyncpg.Connection) -> None:
    await cb.answer()
    user_id = cb.from_user.id
    team = await db_teams.get_team_by_participant(conn, user_id)
    if team is None:
        await cb.message.answer(render("error_not_in_team"), parse_mode="HTML")  # type: ignore[union-attr]
        return

    await db_teams.remove_member(conn, team.id, user_id)
    remaining = await db_teams.member_count(conn, team.id)

    if remaining == 0:
        await db_teams.delete_team(conn, team.id)
    elif user_id == team.captain_id:
        new_team = await db_teams.get_team(conn, team.id)
        if new_team and new_team.members:
            await db_teams.set_captain(conn, team.id, new_team.members[0].id)

    await cb.message.answer(render("team_left"), parse_mode="HTML")  # type: ignore[union-attr]
    team_after = await db_teams.get_team_by_participant(conn, user_id)
    await cb.message.answer(  # type: ignore[union-attr]
        render("main_menu"),
        reply_markup=main_menu_kb(in_team=team_after is not None),
        parse_mode="HTML",
    )
