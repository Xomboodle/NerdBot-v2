"""functions.py"""
import discord
from discord import User, Member, Guild, Embed, TextChannel, Thread, Message
from discord.ext.commands import Bot

import json

import random

import time

from typing import Dict, Any, List

import re

import inspirobot

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


def validate_usertype(user: Any, usertype: Any):
    return isinstance(user, usertype)


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
    claimables['crate']['current'][guild_id]['message'] = str(embed_message.id)
    claimables['crate']['current'][guild_id]['channel'] = str(channel.id)

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
    embed_message: Message = await channel.send(embed=clam_embed)
    claimables['clam']['current'][guild_id]['message'] = str(embed_message.id)
    claimables['clam']['current'][guild_id]['channel'] = str(channel.id)

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
        claimables['crate']['current'][guild_id] = {}
        claimables['clam']['current'][guild_id] = {}
        claimables['crate']['lastCaught'][guild_id] = 0
        claimables['clam']['lastCaught'][guild_id] = 0

    """
        Two checks carried out to determine whether a crate or clam is allowed to spawn:
        1) There are no unclaimed crates/clams available
        2) The last crate/clam was claimed more than 15 minutes ago
    """
    now: float = time.time()
    generate[0] = (now - claimables['crate']['lastCaught'][guild_id] >= constants.FIFTEEN_MINUTES) and \
                  (not claimables['crate']['unclaimed'][guild_id])
    generate[1] = (now - claimables['clam']['lastCaught'][guild_id] >= constants.FIFTEEN_MINUTES) and \
                  (not claimables['clam']['unclaimed'][guild_id])

    number: int = random.randint(1, 3)
    if number == 1 and generate[0]:
        await generate_crate(guild_id, claimables, channel)
    elif number == 2 and generate[1]:
        await generate_clam(guild_id, claimables, channel)


async def respond_to_message(channel: TextChannel | Thread, content: str, bot: Bot):
    for word in constants.SWEARS:
        if word in content:
            await channel.send("Ooh, do you kiss your momma with that mouth?")
            break

    # Specific cases
    if re.findall('work', content):
        await channel.send("WORK?! You should be gaming!")
    elif re.findall('inspire me', content):
        inspiration = inspirobot.generate()
        await channel.send(inspiration.url)
    elif bot.command_prefix == content or re.findall('nerdbot', content):
        response: str = constants.NERD_RESPONSES[random.randint(0, len(constants.NERD_RESPONSES))]
        await channel.send(response)


async def edit_crate_message(message_id: int, channel: TextChannel | Thread, member: Member):
    message: discord.Message = await channel.fetch_message(message_id)

    claim_embed: discord.Embed = discord.Embed(
        title="Crate claimed!",
        color=discord.Color.green()
    )
    claim_embed.add_field(
        name="",
        value=f"{member.display_name} claimed this crate."
    )

    await message.edit(embed=claim_embed)


async def edit_clam_message(message_id: int, channel: TextChannel | Thread, member: Member):
    message: discord.Message = await channel.fetch_message(message_id)

    claim_embed: discord.Embed = discord.Embed(
        title="Clam claimed!",
        color=discord.Color.green()
    )
    claim_embed.add_field(
        name="",
        value=f"{member.display_name} claimed this clam."
    )

    await message.edit(embed=claim_embed)


def update_crate_data(data: Dict[str, Any], guild_id: str):
    data['crate']['unclaimed'][guild_id] = False
    data['crate']['lastCaught'][guild_id] = time.time()
    data['crate']['current'][guild_id] = {}
    data['crate']['total'] += 1

    with open('claimables.json', 'w') as w_file:
        json.dump(data, w_file)


def update_clam_data(data: Dict[str, Any], guild_id: str):
    data['clam']['unclaimed'][guild_id] = False
    data['clam']['lastCaught'][guild_id] = time.time()
    data['clam']['current'][guild_id] = {}
    data['clam']['total'] += 1

    with open('claimables.json', 'w') as w_file:
        json.dump(data, w_file)


def update_score(guild_id: str, member_id: int, score: int):
    with open('guilddata.json', 'r') as r_file:
        data = json.load(r_file)
    try:
        member_score: int = data[guild_id]['crateboard'][str(member_id)]
    except KeyError:  # User has not had a score before now
        member_score: int = 10
    member_score += score
    data[guild_id]['crateboard'][str(member_id)] = member_score

    with open('guilddata.json', 'w') as w_file:
        json.dump(data, w_file)


def update_clam_score(guild_id: str, member_id: int):
    with open('guilddata.json', 'r') as r_file:
        data = json.load(r_file)

    try:
        member_score: int = data[guild_id]['clamboard'][str(member_id)]
        data[guild_id]['clamboard'][str(member_id)] = member_score + 1
    except KeyError:  # User has not claimed a clam before
        data[guild_id]['clamboard'][str(member_id)] = 1

    with open('guilddata.json', 'w') as w_file:
        json.dump(data, w_file)
