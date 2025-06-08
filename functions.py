"""functions.py"""
import logging
from typing import Dict, Any, List, Tuple

from datetime import datetime

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

import repository

from classes import Error

from enums import ErrorType, Claimable, ModerationType

from datatypes import Guilds, Guild as RepoGuild, CurrentClaimable


def get_all_guilds() -> Guilds | None:
    result = repository.get_all_guilds()
    if isinstance(result, Error) and result.Status == ErrorType.MySqlException:
        logging.error(result.Message)
        return None

    return result


def get_guild(guild_id: int) -> RepoGuild | bool | None:
    result = repository.get_guild(guild_id)
    if isinstance(result, Error) and result.Status == ErrorType.MySqlException:
        logging.error(result.Message)
        return None

    if result is None:
        return False

    return result


def add_new_guild(guild_id: int) -> bool:
    result = repository.add_guild(guild_id)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def set_active_guild(guild_id: int) -> bool:
    result = repository.set_active_guild(guild_id)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def get_guild_changelog_version(guild_id: int) -> int | None:
    result = repository.get_guild_changelog_version(guild_id)
    if isinstance(result, Error) and result.Status == ErrorType.MySqlException:
        logging.error(result.Message)
        return None

    return result


def set_guild_changelog_version(guild_id: int, version: int) -> bool:
    result = repository.set_guild_changelog_version(guild_id, version)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def get_last_reactor(guild_id: int) -> int | bool | None:
    result = repository.get_last_reactor(guild_id)
    if isinstance(result, Error) and result.Status == ErrorType.MySqlException:
        logging.error(result.Message)
        return None

    if result is None:
        return False

    return result


def set_last_reactor(guild_id: int, user_id: int) -> bool:
    result = repository.set_last_reactor(guild_id, user_id)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def get_current_coin_claimable(guild_id: int) -> CurrentClaimable | bool | None:
    result = repository.get_current_claimable(guild_id, Claimable.Coin)
    if isinstance(result, Error) and result.Status == ErrorType.MySqlException:
        logging.error(result.Message)
        return None

    if result["current"] is None:
        return False

    return result


def set_current_coin_claimable(guild_id: int, message_id: int | None, channel_id: int | None) -> bool:
    result = repository.set_current_claimable(guild_id, Claimable.Coin, message_id, channel_id)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def get_current_clam_claimable(guild_id: int) -> CurrentClaimable | bool | None:
    result = repository.get_current_claimable(guild_id, Claimable.Clam)
    if isinstance(result, Error) and result.Status == ErrorType.MySqlException:
        logging.error(result.Message)
        return None

    if result["current"] is None:
        return False

    return result


def set_current_clam_claimable(guild_id: int, message_id: int | None, channel_id: int | None) -> bool:
    result = repository.set_current_claimable(guild_id, Claimable.Clam, message_id, channel_id)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def retrieve_changelog() -> Tuple[Dict[str, Any], str]:
    with open('changelog.json', 'r') as r_file:
        data: Dict[str, Any] = json.load(r_file)

    latest_key: str = sorted([*data.keys()], key=lambda item: int(item), reverse=True)[0]

    return data, latest_key


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


async def generate_crate(guild_id: int,
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

    embed_message: Message = await channel.send(embed=crate_embed)

    repository.set_current_claimable(guild_id, Claimable.Coin, embed_message.id, channel.id)


async def generate_clam(guild_id: int,
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

    embed_message: Message = await channel.send(embed=clam_embed)

    repository.set_current_claimable(guild_id, Claimable.Clam, embed_message.id, channel.id)


async def generate_claimable(guild: Guild,
                             channel: TextChannel | Thread):
    generate: List[bool] = [False, False]  # [Crate, Clam]

    """
        Two checks carried out to determine whether a crate or clam is allowed to spawn:
        1) There are no unclaimed crates/clams available
        2) The last crate/clam was claimed more than 15 minutes ago
    """
    now: float = time.time()
    coin_last_caught: datetime | Error = repository.get_last_caught(guild.id, Claimable.Coin)
    if isinstance(coin_last_caught, Error):
        coin_last_caught.log()
        return
    coin_last_caught_timestamp: float = coin_last_caught.timestamp()
    coin_unclaimed: CurrentClaimable = repository.get_current_claimable(guild.id, Claimable.Coin)
    clam_last_caught: datetime | Error = repository.get_last_caught(guild.id, Claimable.Clam)
    if isinstance(clam_last_caught, Error):
        clam_last_caught.log()
        return
    clam_last_caught_timestamp: float = clam_last_caught.timestamp()
    clam_unclaimed: CurrentClaimable = repository.get_current_claimable(guild.id, Claimable.Clam)

    generate[0] = (now - coin_last_caught_timestamp >= constants.FIFTEEN_MINUTES) and \
                  (coin_unclaimed["current"] is None)
    generate[1] = (now - clam_last_caught_timestamp >= constants.FIFTEEN_MINUTES) and \
                  (clam_unclaimed["current"] is None)

    number: int = random.randint(1, 20)
    if number == 1 and generate[0]:
        await generate_crate(guild.id, channel)
    elif number == 2 and generate[1]:
        await generate_clam(guild.id, channel)


async def respond_to_message(channel: TextChannel | Thread, content: str, bot: Bot):
    for word in constants.SWEARS:
        if word in content:
            await channel.send("Ooh, do you kiss your momma with that mouth?")
            break

    # Specific cases
    if re.findall(r'\bwork\b', content):
        response: str = constants.WORK_RESPONSES[random.randint(0, len(constants.WORK_RESPONSES)-1)]
        await channel.send(response)
    elif re.findall('inspire me', content):
        inspiration = inspirobot.generate()
        await channel.send(inspiration.url)
    elif bot.command_prefix == content or re.findall('nerdbot', content):
        response: str = constants.NERD_RESPONSES[random.randint(0, len(constants.NERD_RESPONSES)-1)]
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


def get_coin_score(member_id: int) -> int | bool:
    member_score: int = repository.get_user_score(member_id, Claimable.Coin)
    if isinstance(member_score, Error) and member_score.Status == ErrorType.MySqlException:
        logging.error(member_score.Message)
        return False

    return member_score


def update_coin_score(member_id: int, score: int) -> bool:
    member_score: int = get_coin_score(member_id)

    member_score += score
    result = repository.set_user_score(member_id, member_score, Claimable.Coin)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def set_coin_last_caught(guild_id: int) -> bool:
    # Only called once caught, so time is always "now"
    result = repository.set_last_caught(guild_id, Claimable.Coin, datetime.now())
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def get_clam_score(member_id: int) -> int | bool:
    member_score: int = repository.get_user_score(member_id, Claimable.Clam)
    if isinstance(member_score, Error) and member_score.Status == ErrorType.MySqlException:
        logging.error(member_score.Message)
        return False

    return member_score


def update_clam_score(member_id: int):
    member_score: int = get_clam_score(member_id)

    member_score += 1
    result = repository.set_user_score(member_id, member_score, Claimable.Clam)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def set_clam_last_caught(guild_id: int) -> bool:
    # Only called once caught, so time is always "now"
    result = repository.set_last_caught(guild_id, Claimable.Clam, datetime.now())
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


async def get_leaderboard(guild: Guild, channel: TextChannel | Thread, coins: bool):
    guild_members = [member.id for member in guild.members]
    top_ten = repository.get_top_group_scores(guild_members, Claimable.Coin if coins else Claimable.Clam)
    if isinstance(top_ten, Error) and top_ten.Status == ErrorType.MySqlException:
        logging.error(top_ten.Message)
        return

    leaderboard_embed: discord.Embed = discord.Embed(
        title=f"{'Coins' if coins else 'Clams'} leaderboard",
        color=discord.Color.red()
    )

    # Display top 10
    for count, record in enumerate(top_ten):
        user: Member | None = guild.get_member(record[0])

        leaderboard_embed.add_field(
            name=f"{count+1} {user.nick if user.nick is not None else user.display_name}",
            value=f"{record[1]} {'coins' if coins else 'clams'}",
            inline=False
        )

    await channel.send(embed=leaderboard_embed)


def get_random_number(start: int, end: int) -> int:
    result: int = random.randint(start, end)
    return result


def get_meme() -> str:
    reddit_memes: RedditMemes = meme_get.RedditMemes()
    memes: List[Meme] = reddit_memes.get_memes(100)
    result: str = memes[get_random_number(0, 99)].get_pic_url()

    return result


def set_moderation_info(user_id: int,
                        guild_id: int,
                        moderator_id: int,
                        moderation_type: ModerationType,
                        extra: str | None = None):
    result: Error = repository.set_user_moderation_info(user_id, guild_id, moderator_id, moderation_type, extra)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def get_moderation_info(user_id: int,
                        guild_id: int,
                        moderation_type: ModerationType):
    result: list[int] | None | Error = repository.get_user_moderation_info(user_id, guild_id, moderation_type)
    if isinstance(result, Error) and result.Status == ErrorType.MySqlException:
        logging.error(result.Message)
        return None

    if result is None:
        return False

    return result


def remove_moderation_info(user_id: int,
                           guild_id: int,
                           moderation_type: ModerationType):
    result: Error = repository.remove_user_moderation_info(user_id, guild_id, moderation_type)
    if result.Status == ErrorType.NoError:
        return True

    logging.error(result.Message)
    return False


def find_title(version: str, titles: List[Tuple[str, str]]) -> str:
    for title in titles:
        if re.search(version.lower(), title[1].lower()) is not None:
            return title[0]
    else:
        return "-1"
