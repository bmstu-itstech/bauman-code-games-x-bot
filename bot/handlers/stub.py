from __future__ import annotations

from aiogram import Router
from aiogram.types import Message

from bot.templates import render

router = Router()


@router.message()
async def fallback(message: Message) -> None:
    await message.answer(render("registration_closed"), parse_mode="HTML")
