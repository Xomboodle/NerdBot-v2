"""commands.py"""

# IMPORTS #
import discord
from discord.ext.commands import Bot

import functions

from typing import List


# LISTEN EVENTS
async def on_ready(bot: Bot):
    with open('changelog.txt', 'r') as r_file:
        lines: List[str] = r_file.read().split('\n\n')
    # Check if there is a new update, applies markdown and returns
    recent_update: str = lines[0]
    with open('updated.txt', 'r') as r_file:
        updated_lines: str = r_file.read()
    if recent_update != updated_lines:
        with open('updated.txt', 'w') as w_file:
            w_file.write(recent_update)
        for guild in bot.guilds:
            channel: discord.TextChannel = guild.system_channel
            await channel.send(
                f"# NEW UPDATE:\n{functions.format_update(recent_update)}"
            )

