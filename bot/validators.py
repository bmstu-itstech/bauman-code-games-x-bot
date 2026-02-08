from __future__ import annotations

import re
import datetime

_FULL_NAME_RE = re.compile(r"^[а-яА-ЯёЁ-]+(\s+[а-яА-ЯёЁ-]+)+$")
_GROUP_RE = re.compile(
    r"^((((ФМОП-)?(ИУ|ИБМ|МТ|СМ|БМТ|РЛ|Э|РК|ФН|Л|СГН|ВУЦ|УЦ|ИСОТ|РКТ|АК|ПС|РТ|ЛТ|К|ЮР|ОЭ|ТА|ТБД|ТИ|ТД|ТИП|ТКС|ТМО|ТМР|ТР|ТСА|ТСР|ТСС|ТУ|ТУС|ТЭ)"
    r"[1-9]\d?)|(ЮР(\.ДК)?))(К)?[ИЦ]?-(((1[0-2])|(\d))((\d)|(.\d\d+))([АМБ]?(В)?)))$"
)
_TEAM_ID_RE = re.compile(r"^[a-z0-9]{6}$")


def validate_full_name(value: str) -> str | None:
    value = " ".join(value.split())
    if not _FULL_NAME_RE.match(value):
        return "ФИО должно содержать минимум 2 слова и только кириллицу/дефис."
    return None


def validate_birthdate(value: str) -> datetime.date | str:
    try:
        dt = datetime.datetime.strptime(value.strip(), "%d.%m.%Y").date()
    except ValueError:
        return "Неверный формат даты. Используйте ДД.ММ.ГГГГ."
    today = datetime.date.today()
    age = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
    if age < 17 or age > 25:
        return "Возраст должен быть от 17 до 25 лет."
    return dt


def validate_group(value: str) -> str | None:
    if not _GROUP_RE.match(value.strip().upper()):
        return "Неверный формат группы. Пример: ИУ7-63Б."
    return None


def validate_team_id(value: str) -> str | None:
    if not _TEAM_ID_RE.match(value.strip().lower()):
        return "ID команды должен содержать 6 символов (a-z, 0-9)."
    return None


def validate_team_name(value: str) -> str | None:
    name = value.strip()
    if not name:
        return "Название команды не может быть пустым."
    if len(name) > 31:
        return "Название команды не должно превышать 31 символ."
    return None
