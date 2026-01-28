from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass
class Participant:
    id: int
    username: str | None
    full_name: str
    birthdate: datetime.date
    affiliation_type: str  # "bmstu" | "other"
    bmstu_group: str | None = None
    university: str | None = None
    ref_code: str | None = None
    created_at: datetime.datetime | None = None
