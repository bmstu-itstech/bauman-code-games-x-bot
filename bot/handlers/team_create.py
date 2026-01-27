from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
import asyncpg

from bot.db import teams as db_teams
from bot.handlers.menu import show_menu
from bot.keyboards import back_to_menu_kb
from bot.templates import render
from bot.validators import validate_team_name

router = Router()


class CreateTeamFSM(StatesGroup):
    name = State()


@router.callback_query(F.data == "team_create")
async def on_create(cb: CallbackQuery, state: FSMContext, conn: asyncpg.Connection) -> None:
    await cb.answer()
    existing = await db_teams.get_team_by_participant(conn, cb.from_user.id)
    if existing:
        await cb.message.answer(render("error_already_in_team"), parse_mode="HTML")  # type: ignore[union-attr]
        return
    await state.set_state(CreateTeamFSM.name)
    await cb.message.answer(render("create_team_name"), parse_mode="HTML")  # type: ignore[union-attr]


@router.message(CreateTeamFSM.name)
async def on_team_name(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    name = (message.text or "").strip()
    err = validate_team_name(name)
    if err:
        await message.answer(err)
        return
    if await db_teams.team_name_exists(conn, name):
        await message.answer(render("error_team_name_taken"), parse_mode="HTML")
        return

    team = await db_teams.create_team(conn, name, message.from_user.id)  # type: ignore[union-attr]
    bot_me = await message.bot.me()  # type: ignore[union-attr]
    await message.answer(
        render("team_created", team_name=team.name, team_id=team.id, bot_username=bot_me.username),
        parse_mode="HTML",
    )
    await state.clear()
    await show_menu(message, conn)
