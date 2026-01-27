from __future__ import annotations

import datetime
from dataclasses import dataclass, field

from bot.models.participant import Participant


@dataclass
class Team:
    id: str
    name: str
    captain_id: int
    members: list[Participant] = field(default_factory=list)
    created_at: datetime.datetime | None = None

    @property
    def is_ready(self) -> bool:
        return len(self.members) == 3
