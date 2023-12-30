"""functions.py"""
import discord
from discord import User, Member, Guild, Embed, TextChannel, Thread, Message
from discord.ext.commands import Bot

import json

import random

import time

from typing import Dict, Any, List

import constants


def format_update(text: str) -> str:
    # Need to get the title of the update and set as a heading
    heading: str = text.split('\n')[0]
    subheading: str = text.split('\n-')[0].replace(heading + "\n", "")

    changelog: str = text.replace(heading, f"## {heading}")
    changelog = changelog.replace(subheading, f"_{subheading}_\n")

    return changelog


def validate_author(user: User | Member,
                    bot: Bot) -> bool:
    return user == bot.user


async def generate_crate(guild_id: str,
                         claimables: Dict[str, Any],
                         channel: TextChannel | Thread):
    crate_embed: Embed = discord.Embed(
        title='A wild loot crate appeared!',
        color=discord.Color.green()
    )
    crate_embed.set_image(url=constants.CRATE_IMAGE)
    crate_embed.add_field(
        name='Grab it quick!',
        value='Type `!claim` to collect the crate.',
        inline=False
    )
    claimables['crate']['unclaimed'][guild_id] = True
    embed_message: Message = await channel.send(embed=crate_embed)
    claimables['crate']['current'][guild_id] = str(embed_message.id)

    with open('claimables.json', 'w') as w_file:
        json.dump(claimables, w_file)


async def generate_clam(guild_id: str,
                        claimables: Dict[str, Any],
                        channel: TextChannel | Thread):
    clam_embed = discord.Embed(
        title="A wild clam appeared!",
        color=discord.Color.blue()
    )
    clam_embed.set_image(url=constants.CLAM_IMAGE)
    clam_embed.add_field(
        name="Legit or quit.",
        value="Type `!clam` to claim the clam.",
        inline=False
    )

    claimables['clam']['unclaimed'][guild_id] = True
    claimables['clam']['current'][guild_id] = await channel.send(embed=clam_embed)

    with open('claimables.json', 'w') as w_file:
        json.dump(claimables, w_file)


async def generate_claimable(guild: Guild,
                             channel: TextChannel | Thread):
    with open('claimables.json', 'r') as r_file:
        claimables: Dict[str, Any] = json.load(r_file)

    generate: List[bool] = [False, False]  # [Crate, Clam]
    guild_id: str = str(guild.id)

    # Need to check if there is a claimable that is currently unclaimed
    # First need to check if a message has been sent in the guild after the bot
    # has joined it
    if guild_id not in claimables['crate']['unclaimed'].keys():
        generate = [True, True]
        claimables['crate']['unclaimed'][guild_id] = False
        claimables['clam']['unclaimed'][guild_id] = False
        claimables['crate']['current'][guild_id] = ""
        claimables['clam']['current'][guild_id] = ""
        claimables['crate']['lastCaught'][guild_id] = ""
        claimables['clam']['lastCaught'][guild_id] = ""

    """
        Two checks carried out to determine whether a crate or clam is allowed to spawn:
        1) There are no unclaimed crates/clams available
        2) The last crate/clam was claimed more than 15 minutes ago
    """
    now: float = time.time()
    generate[0] = (now - int(claimables['crate']['lastCaught'][guild_id] or 0) >= constants.FIFTEEN_MINUTES) and \
                  (not claimables['crate']['unclaimed'][guild_id])
    generate[1] = (now - int(claimables['clam']['lastCaught'][guild_id] or 0) >= constants.FIFTEEN_MINUTES) and \
                  (not claimables['clam']['unclaimed'][guild_id])

    number: int = random.randint(1, 25)
    if number == 1 and generate[0]:
        await generate_crate(guild_id, claimables, channel)
    elif number == 2 and generate[1]:
        await generate_clam(guild_id, claimables, channel)
