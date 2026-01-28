from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import asyncpg

from bot.db import participants as db_part
from bot.db import teams as db_teams
from bot.db import ref_sources as db_ref
from bot.handlers.menu import show_menu
from bot.handlers.registration import start_registration
from bot.templates import render
from bot.validators import validate_team_id

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep(
    message: Message, command: CommandObject, state: FSMContext, conn: asyncpg.Connection
) -> None:
    arg = (command.args or "").strip().lower()
    participant = await db_part.get_participant(conn, message.from_user.id)  # type: ignore[union-attr]

    is_ref = await db_ref.ref_source_exists(conn, arg)

    if participant is None:
        if is_ref:
            await state.update_data(pending_ref_code=arg)
        elif validate_team_id(arg) is None:
            await state.update_data(pending_team_id=arg)
        await start_registration(message, state)
        return

    if is_ref or validate_team_id(arg) is not None:
        await show_menu(message, conn)
        return

    team_id = arg

    existing = await db_teams.get_team_by_participant(conn, participant.id)
    if existing:
        await message.answer(render("error_already_in_team"), parse_mode="HTML")
        await show_menu(message, conn)
        return

    team = await db_teams.get_team(conn, team_id)
    if team is None:
        await message.answer(render("error_team_not_found"), parse_mode="HTML")
        await show_menu(message, conn)
        return

    if len(team.members) >= 3:
        await message.answer(render("error_team_full"), parse_mode="HTML")
        await show_menu(message, conn)
        return

    await db_teams.add_member(conn, team_id, participant.id)
    await message.answer(
        render("team_joined", team_name=team.name), parse_mode="HTML"
    )
    await show_menu(message, conn)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    participant = await db_part.get_participant(conn, message.from_user.id)  # type: ignore[union-attr]
    if participant is None:
        await start_registration(message, state)
    else:
        await show_menu(message, conn)
