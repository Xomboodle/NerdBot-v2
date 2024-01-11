"""functions.py"""
import discord
from discord import User, Member, Guild, Embed, TextChannel, Thread, Message
from discord.ext.commands import Bot

import json
import random
import time
import re
import inspirobot

import meme_get
from meme_get.memesites import RedditMemes, Meme

import constants

from typing import Dict, Any, List, Tuple


def retrieve_guild_data() -> Dict[str, Any]:
    with open('guilddata.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)

    return data


def retrieve_changelog() -> Tuple[Dict[str, Any], str]:
    with open('changelog.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)

    latest_key: str = sorted([*data.keys()], key=lambda item: int(item), reverse=True)[0]

    return data, latest_key


def retrieve_claimables_data() -> Dict[str, Any]:
    with open('claimables.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)

    return data


def write_to_guild_data(data: Dict[str, Any]):
    with open('guilddata.json', 'w') as w_file:
        json.dump(data, w_file)


def write_to_changelog(data: Dict[str, Any]):
    with open('changelog.json', 'w') as w_file:
        json.dump(data, w_file)


def write_to_claimables(data: Dict[str, Any]):
    with open('claimables.json', 'w') as w_file:
        json.dump(data, w_file)


def format_update(data: Dict[str, Any]) -> str:
    # Need to get the title of the update and set as a heading
    heading: str = data['title']
    subheading: str = data['content']['subtext']

    update: str = f"## {heading}\n_{subheading}_\n\n"
    for key in data['content']['items'].keys():
        update += f"- {data['content']['items'][key]}\n"

    return update


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

    write_to_claimables(claimables)


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

    write_to_claimables(claimables)


async def generate_claimable(guild: Guild,
                             channel: TextChannel | Thread):
    claimables: Dict[str, Any] = retrieve_claimables_data()

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

    number: int = random.randint(1, 20)
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

    write_to_claimables(data)


def update_clam_data(data: Dict[str, Any], guild_id: str):
    data['clam']['unclaimed'][guild_id] = False
    data['clam']['lastCaught'][guild_id] = time.time()
    data['clam']['current'][guild_id] = {}
    data['clam']['total'] += 1

    write_to_claimables(data)


def update_score(guild_id: str, member_id: int, score: int):
    data: Dict[str, Any] = retrieve_guild_data()
    try:
        member_score: int = data[guild_id]['crateboard'][str(member_id)]
    except KeyError:  # User has not had a score before now
        member_score: int = 10
    member_score += score
    data[guild_id]['crateboard'][str(member_id)] = member_score

    write_to_guild_data(data)


def update_clam_score(guild_id: str, member_id: int):
    data: Dict[str, Any] = retrieve_guild_data()

    try:
        member_score: int = data[guild_id]['clamboard'][str(member_id)]
        data[guild_id]['clamboard'][str(member_id)] = member_score + 1
    except KeyError:  # User has not claimed a clam before
        data[guild_id]['clamboard'][str(member_id)] = 1

    write_to_guild_data(data)


async def get_leaderboard(guild: Guild, channel: TextChannel | Thread, coins: bool):
    data: Dict[str, Any] = retrieve_guild_data()
    guild_data: Dict = data[str(guild.id)]['crateboard' if coins else 'clamboard']

    leaderboard: Dict[str, int] = dict(
        sorted(guild_data.items(), key=lambda item: item[1], reverse=True)
    )
    users: List[str] = [*leaderboard]
    leaderboard_embed: discord.Embed = discord.Embed(
        title=f"{'Coins' if coins else 'Clams'} leaderboard",
        color=discord.Color.red()
    )

    # Display top 10
    position: int = 0
    skipped: int = 0
    while position < 10:
        try:
            user: Member | None = guild.get_member(int(users[position+skipped]))
            if user is None:
                # User may not exist, but we still need to get up to 10 users if they exist later
                skipped += 1
                continue
        except IndexError:  # Not enough server members have got on the leaderboard
            break

        leaderboard_embed.add_field(
            name=f"{position+1} {user.display_name}",
            value=f"{leaderboard[str(user.id)]} {'coins' if coins else 'clams'}",
            inline=False
        )

        position += 1

    await channel.send(embed=leaderboard_embed)


def get_random_number(start: int, end: int) -> int:
    result: int = random.randint(start, end)
    return result


def get_meme() -> str:
    reddit_memes: RedditMemes = meme_get.RedditMemes()
    memes: List[Meme] = reddit_memes.get_memes(100)
    result: str = memes[get_random_number(0, 99)].get_pic_url()

    return result
