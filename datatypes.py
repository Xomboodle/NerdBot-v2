from typing import TypedDict


class Guild(TypedDict):
    id: int
    active: bool


class CurrentClaimable(TypedDict):
    current: int
    currentChannel: int


Guilds = list[Guild]
