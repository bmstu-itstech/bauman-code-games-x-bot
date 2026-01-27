from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
import asyncpg

from bot.db import teams as db_teams
from bot.keyboards import main_menu_kb
from bot.templates import render

router = Router()


async def show_menu(message: Message, conn: asyncpg.Connection) -> None:
    user_id = message.from_user.id  # type: ignore[union-attr]
    team = await db_teams.get_team_by_participant(conn, user_id)
    await message.answer(
        render("main_menu"),
        reply_markup=main_menu_kb(in_team=team is not None),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu")
async def on_menu(cb: CallbackQuery, conn: asyncpg.Connection) -> None:
    await cb.answer()
    user_id = cb.from_user.id
    team = await db_teams.get_team_by_participant(conn, user_id)
    await cb.message.answer(  # type: ignore[union-attr]
        render("main_menu"),
        reply_markup=main_menu_kb(in_team=team is not None),
        parse_mode="HTML",
    )
