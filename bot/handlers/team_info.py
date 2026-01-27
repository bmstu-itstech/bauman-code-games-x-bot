from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery
import asyncpg

from bot.db import teams as db_teams
from bot.keyboards import back_to_menu_kb
from bot.templates import render

router = Router()


@router.callback_query(F.data == "team_info")
async def on_info(cb: CallbackQuery, conn: asyncpg.Connection) -> None:
    await cb.answer()
    team = await db_teams.get_team_by_participant(conn, cb.from_user.id)
    if team is None:
        await cb.message.answer(render("error_not_in_team"), parse_mode="HTML")  # type: ignore[union-attr]
        return
    await cb.message.answer(  # type: ignore[union-attr]
        render(
            "team_info",
            team_name=team.name,
            members=team.members,
            captain_id=team.captain_id,
            is_ready=team.is_ready,
        ),
        reply_markup=back_to_menu_kb(),
        parse_mode="HTML",
    )
