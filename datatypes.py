from typing import TypedDict


class Guild(TypedDict):
    id: int
    active: bool


Guilds = list[Guild]
