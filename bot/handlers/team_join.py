from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
import asyncpg

from bot.db import teams as db_teams
from bot.handlers.menu import show_menu
from bot.templates import render
from bot.validators import validate_team_id

router = Router()


class JoinTeamFSM(StatesGroup):
    team_id = State()


@router.callback_query(F.data == "team_join")
async def on_join(cb: CallbackQuery, state: FSMContext, conn: asyncpg.Connection) -> None:
    await cb.answer()
    existing = await db_teams.get_team_by_participant(conn, cb.from_user.id)
    if existing:
        await cb.message.answer(render("error_already_in_team"), parse_mode="HTML")  # type: ignore[union-attr]
        return
    await state.set_state(JoinTeamFSM.team_id)
    await cb.message.answer(render("join_team_id"), parse_mode="HTML")  # type: ignore[union-attr]


@router.message(JoinTeamFSM.team_id)
async def on_team_id(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    raw = (message.text or "").strip().lower()
    err = validate_team_id(raw)
    if err:
        await message.answer(err)
        return

    team = await db_teams.get_team(conn, raw)
    if team is None:
        await message.answer(render("error_team_not_found"), parse_mode="HTML")
        return
    if len(team.members) >= 3:
        await message.answer(render("error_team_full"), parse_mode="HTML")
        return

    await db_teams.add_member(conn, raw, message.from_user.id)  # type: ignore[union-attr]
    await message.answer(
        render("team_joined", team_name=team.name), parse_mode="HTML"
    )
    await state.clear()
    await show_menu(message, conn)
