from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
import asyncpg

from bot.db import participants as db_participants
from bot.handlers.menu import show_menu
from bot.keyboards import foncode_confirm_kb
from bot.templates import render
from bot.validators import validate_foncode_id

router = Router()


class FoncodeFSM(StatesGroup):
    enter_id = State()
    confirm = State()


@router.callback_query(F.data == "foncode_start")
async def on_foncode_start(cb: CallbackQuery, state: FSMContext, conn: asyncpg.Connection) -> None:
    await cb.answer()
    participant = await db_participants.get_participant(conn, cb.from_user.id)
    if participant and participant.foncode_id is not None:
        return
    await state.set_state(FoncodeFSM.enter_id)
    await cb.message.answer(render("ask_foncode_id"), parse_mode="HTML")  # type: ignore[union-attr]


@router.message(FoncodeFSM.enter_id)
async def on_enter_id(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    err = validate_foncode_id(raw)
    if err:
        await message.answer(err)
        return
    await state.update_data(foncode_id=raw)
    await state.set_state(FoncodeFSM.confirm)
    await message.answer(
        render("foncode_confirm", foncode_id=raw),
        reply_markup=foncode_confirm_kb(),
        parse_mode="HTML",
    )


@router.callback_query(FoncodeFSM.confirm, F.data == "foncode_confirm")
async def on_confirm(cb: CallbackQuery, state: FSMContext, conn: asyncpg.Connection) -> None:
    await cb.answer()
    data = await state.get_data()
    foncode_id = data["foncode_id"]
    await db_participants.set_foncode_id(conn, cb.from_user.id, foncode_id)
    await state.clear()
    await cb.message.answer(  # type: ignore[union-attr]
        render("foncode_saved", foncode_id=foncode_id), parse_mode="HTML"
    )
    await show_menu(cb.message, conn)  # type: ignore[arg-type]


@router.callback_query(FoncodeFSM.confirm, F.data == "foncode_retry")
async def on_retry(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(FoncodeFSM.enter_id)
    await cb.message.answer(render("ask_foncode_id"), parse_mode="HTML")  # type: ignore[union-attr]
