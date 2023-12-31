"""commands.py"""
import random

# IMPORTS #
import discord
from discord import Reaction, User, Member, Guild
from discord.ext.commands import Bot

import json

import constants
import functions

from typing import List, Dict, Any
from types import UnionType


# Types
Channel: UnionType = discord.TextChannel | discord.Thread
Person: UnionType = User | Member


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


async def on_reaction_add(reaction: Reaction, user: Person):
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


async def claim(guild: Guild, channel: Channel, author: Person):
    with open('claimables.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)
    crate_data: Dict[str, Any] = data['crate']
    guild_id: str = str(guild.id)

    if not crate_data['unclaimed'][guild_id]:
        await channel.send("No crate to claim!")
        return

    # Make sure we're claiming it in the right channel, to avoid confusion
    if str(channel.id) != crate_data['current'][guild_id]['channel']:
        await channel.send("The crate is in a different channel. Claim it there!")
        return

    member_info: Member = guild.get_member(author.id)
    score: int = random.randint(10, 30)

    await channel.send(
        f"{member_info.display_name} claimed the crate."
        f" They got {score} coins!"
    )

    # Prepare and send edited message for the original crate message
    await functions.edit_crate_message(int(crate_data['current'][guild_id]['message']), channel, member_info)

    functions.update_crate_data(data, guild_id)


async def clam(guild: Guild, channel: Channel, author: Person):
    with open('claimables.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)
    clam_data: Dict[str, Any] = data['clam']
    guild_id: str = str(guild.id)

    if not clam_data['unclaimed'][guild_id]:
        await channel.send("No clam to claim!")
        return

    # Make sure we're claiming it in the right channel, to avoid confusion
    if str(channel.id) != clam_data['current'][guild_id]['channel']:
        await channel.send("The clam to claim is clearly elsewhere. Claim it there!")
        return

    member_info: Member = guild.get_member(author.id)

    await channel.send(
        f"{member_info.display_name} claimed the clam, clearing the clog of clams to claim."
    )

    # Prepare and send edited message for the original crate message
    await functions.edit_clam_message(int(clam_data['current'][guild_id]['message']), channel, member_info)

    functions.update_clam_data(data, guild_id)
