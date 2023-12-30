"""commands.py"""

# IMPORTS #
import discord
from discord import Reaction, User, Member, Guild
from discord.ext.commands import Bot

import json

import constants
import functions

from typing import List, Dict, Any


# LISTEN EVENTS
async def on_ready(bot: Bot):
    with open('guilddata.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)
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
            # Set up data storage for guild if this is the first time the bot is operational in it, but had
            # already joined
            if str(guild.id) not in data.keys():
                data[str(guild.id)] = {}
            channel: discord.TextChannel = guild.system_channel
            await channel.send(
                f"# NEW UPDATE:\n{functions.format_update(recent_update)}"
            )
        with open('guilddata.json', 'w') as w_file:
            json.dump(data, w_file)


async def on_guild_join(guild: Guild):
    with open('guilddata.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)

    data[str(guild.id)] = {}

    with open('guilddata.json', 'w') as w_file:
        json.dump(data, w_file)


async def on_reaction_add(reaction: Reaction, user: User | Member):
    with open('guilddata.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)
    guild_id = str(reaction.message.guild.id)
    if "lastReactUser" not in data[guild_id].keys():
        data[guild_id]['lastReactUser'] = user.id
    else:
        if user.id == data[guild_id]['lastReactUser']:
            return
        else:
            data[guild_id]['lastReactUser'] = user.id
    with open('guilddata.json', 'w') as w_file:
        json.dump(data, w_file)

    try:
        reaction_name = str(reaction.emoji.name)
    except AttributeError:
        reaction_name = reaction.emoji
    # Sends corresponding message based on reaction made.
    if reaction_name in constants.REACTION_IMAGES:
        await reaction.message.channel.send(constants.REACTION_IMAGES[reaction_name])
