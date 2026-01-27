from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
import asyncpg

from bot.config import settings
from bot.keyboards import consent_kb, affiliation_kb
from bot.templates import render
from bot.validators import validate_full_name, validate_birthdate, validate_group
from bot.db import participants as db_part
from bot.db import teams as db_teams
from bot.handlers.menu import show_menu

router = Router()


class RegFSM(StatesGroup):
    consent = State()
    full_name = State()
    birthdate = State()
    affiliation_type = State()
    bmstu_group = State()
    other_university = State()


async def start_registration(message: Message, state: FSMContext) -> None:
    await state.set_state(RegFSM.consent)
    await message.answer(
        render("consent", pd_policy_url=settings.pd_policy_url),
        reply_markup=consent_kb(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(RegFSM.consent, F.data == "consent_agree")
async def on_consent(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await cb.message.edit_text(  # type: ignore[union-attr]
        render("consent_accepted", pd_policy_url=settings.pd_policy_url),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await state.set_state(RegFSM.full_name)
    await cb.message.answer(render("ask_full_name"), parse_mode="HTML")  # type: ignore[union-attr]


@router.message(RegFSM.full_name)
async def on_full_name(message: Message, state: FSMContext) -> None:
    err = validate_full_name(message.text or "")
    if err:
        await message.answer(err)
        return
    name = " ".join((message.text or "").split())
    await state.update_data(full_name=name)
    await state.set_state(RegFSM.birthdate)
    await message.answer(render("ask_birthdate"), parse_mode="HTML")


@router.message(RegFSM.birthdate)
async def on_birthdate(message: Message, state: FSMContext) -> None:
    result = validate_birthdate(message.text or "")
    if isinstance(result, str):
        await message.answer(result)
        return
    await state.update_data(birthdate=result.isoformat())
    await state.set_state(RegFSM.affiliation_type)
    await message.answer(
        render("ask_affiliation"), reply_markup=affiliation_kb(), parse_mode="HTML"
    )


@router.callback_query(RegFSM.affiliation_type, F.data == "aff_bmstu")
async def on_bmstu(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.update_data(affiliation_type="bmstu")
    await state.set_state(RegFSM.bmstu_group)
    await cb.message.answer(render("ask_bmstu_group"), parse_mode="HTML")  # type: ignore[union-attr]


@router.callback_query(RegFSM.affiliation_type, F.data == "aff_other")
async def on_other(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.update_data(affiliation_type="other")
    await state.set_state(RegFSM.other_university)
    await cb.message.answer(render("ask_university"), parse_mode="HTML")  # type: ignore[union-attr]


@router.message(RegFSM.bmstu_group)
async def on_group(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    err = validate_group(message.text or "")
    if err:
        await message.answer(err)
        return
    await state.update_data(bmstu_group=(message.text or "").strip())
    await _finish_registration(message, state, conn)


@router.message(RegFSM.other_university)
async def on_university(message: Message, state: FSMContext, conn: asyncpg.Connection) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Название вуза не может быть пустым.")
        return
    await state.update_data(university=text)
    await _finish_registration(message, state, conn)


async def _finish_registration(
    message: Message, state: FSMContext, conn: asyncpg.Connection
) -> None:
    import datetime

    data = await state.get_data()
    await db_part.create_participant(
        conn,
        tg_id=message.from_user.id,  # type: ignore[union-attr]
        username=message.from_user.username if message.from_user else None,
        full_name=data["full_name"],
        birthdate=datetime.date.fromisoformat(data["birthdate"]),
        affiliation_type=data["affiliation_type"],
        bmstu_group=data.get("bmstu_group"),
        university=data.get("university"),
    )

    await message.answer(
        render("registration_complete", full_name=data["full_name"]),
        parse_mode="HTML",
    )

    # Handle deep-link team join
    pending_team = data.get("pending_team_id")
    if pending_team:
        await _try_join_team(message, conn, pending_team)

    await state.clear()
    await show_menu(message, conn)


async def _try_join_team(
    message: Message, conn: asyncpg.Connection, team_id: str
) -> None:
    team = await db_teams.get_team(conn, team_id)
    if team is None:
        await message.answer(render("error_team_not_found"), parse_mode="HTML")
        return
    if len(team.members) >= 3:
        await message.answer(render("error_team_full"), parse_mode="HTML")
        return
    await db_teams.add_member(conn, team_id, message.from_user.id)  # type: ignore[union-attr]
    await message.answer(
        render("deep_link_after_reg", team_name=team.name),
        parse_mode="HTML",
    )
