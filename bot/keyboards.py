from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def consent_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Даю согласие", callback_data="consent_agree")],
    ])


def affiliation_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="МГТУ им. Баумана", callback_data="aff_bmstu")],
        [InlineKeyboardButton(text="Другой вуз", callback_data="aff_other")],
    ])


def main_menu_kb(in_team: bool, has_foncode: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if in_team:
        rows.append([InlineKeyboardButton(text="Моя команда", callback_data="team_info")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def foncode_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data="foncode_confirm")],
        [InlineKeyboardButton(text="Изменить", callback_data="foncode_retry")],
    ])


def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Меню", callback_data="menu")],
    ])
