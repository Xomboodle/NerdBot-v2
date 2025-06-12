from types import UnionType
from typing import TypedDict

import discord


class Guild(TypedDict):
    id: int
    active: bool


class CurrentClaimable(TypedDict):
    current: int
    currentChannel: int


Guilds = list[Guild]

Channel: UnionType = discord.TextChannel | discord.Thread
Person: UnionType = discord.User | discord.Member
DefaultInput: UnionType = str | None
