"""commands.py"""
import random

# IMPORTS #
import discord
from discord import Reaction, User, Member, Guild, Message
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
    data: Dict[str, Any] = functions.retrieve_guild_data()
    recent_update: str
    update: str
    recent_update, update = functions.retrieve_changelog_update()
    for guild in bot.guilds:
        # Set up data storage for guild if this is the first time the bot is operational in it, but had
        # already joined
        if str(guild.id) not in data.keys():
            data[str(guild.id)] = {
                "crateboard": {},
                "clamboard": {}
            }
        if recent_update != update:
            functions.write_to_updated(recent_update)
            channel: discord.TextChannel = guild.system_channel
            await channel.send(
                f"# NEW UPDATE:\n{functions.format_update(recent_update)}"
            )
    functions.write_to_guild_data(data)


async def on_guild_join(guild: Guild):
    data: Dict[str, Any] = functions.retrieve_guild_data()

    data[str(guild.id)] = {
        "crateboard": {},
        "clamboard": {}
    }

    functions.write_to_guild_data(data)


async def on_reaction_add(reaction: Reaction, user: Person):
    data: Dict[str, Any] = functions.retrieve_guild_data()
    guild_id: str = str(reaction.message.guild.id)
    if "lastReactUser" not in data[guild_id].keys():
        data[guild_id]['lastReactUser'] = user.id
    else:
        if user.id == data[guild_id]['lastReactUser']:
            return
        else:
            data[guild_id]['lastReactUser'] = user.id
    functions.write_to_guild_data(data)

    try:
        reaction_name: str = str(reaction.emoji.name)
    except AttributeError:
        reaction_name: str = reaction.emoji
    # Sends corresponding message based on reaction made.
    if reaction_name in constants.REACTION_IMAGES:
        await reaction.message.channel.send(constants.REACTION_IMAGES[reaction_name])


async def claim(guild: Guild, channel: Channel, author: Person):
    data: Dict[str, Any] = functions.retrieve_claimables_data()
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

    functions.update_score(guild_id, member_info.id, score)

    functions.update_crate_data(data, guild_id)


async def clam(guild: Guild, channel: Channel, author: Person):
    data: Dict[str, Any] = functions.retrieve_claimables_data()
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

    functions.update_clam_score(guild_id, member_info.id)

    functions.update_clam_data(data, guild_id)


async def coins(guild: Guild, channel: Channel, author: Person):
    data: Dict[str, Any] = functions.retrieve_guild_data()
    guild_id: str = str(guild.id)
    author_id: str = str(author.id)

    # In case no coins have been won or claimed from crates
    if data[guild_id]['crateboard'][author_id] is None:
        data[guild_id]['crateboard'][author_id] = 10
        functions.write_to_guild_data(data)

    await channel.send(
        f"You have **{data[guild_id]['crateboard'][author_id]}** coins!"
    )


async def clams(guild: Guild, channel: Channel, author: Person):
    data: Dict[str, Any] = functions.retrieve_guild_data()
    guild_id: str = str(guild.id)
    author_id: str = str(author.id)

    # In case no clams have been won or claimed from crates
    if data[guild_id]['clamboard'][author_id] is None:
        data[guild_id]['clamboard'][author_id] = 0
        functions.write_to_guild_data(data)

    await channel.send(
        f"You have **{data[guild_id]['clamboard'][author_id]}** clams!"
    )


async def insult(channel: Channel, message: Message, author: Person, user: str):
    # Delete command call for anonymity
    await message.delete()

    chosen_insult: int = random.randint(0, len(constants.INSULTS)-1)
    insult_message: str = constants.INSULTS[chosen_insult].format(arg=user, arg2=f"<@!{author.id}>")

    await channel.send(insult_message)
