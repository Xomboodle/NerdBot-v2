"""commands.py"""

# IMPORTS #
import discord
from discord import Reaction, User, Member, Guild, Message, Embed
from discord.ext.commands import Bot

import constants
import functions

from typing import Dict, Any, List, Tuple
from types import UnionType

import repository
from enums import ModerationType

# Types
Channel: UnionType = discord.TextChannel | discord.Thread
Person: UnionType = User | Member


# LISTEN EVENTS
async def on_ready(bot: Bot):
    changelog: Dict[str, Any]
    latest_key: str
    changelog, latest_key = functions.retrieve_changelog()

    all_guilds = functions.get_all_guilds()
    print(all_guilds)
    all_guild_ids = [x["id"] for x in all_guilds]

    send_changelog = False
    for guild in bot.guilds:
        if all_guilds is None:
            break

        # If guild has not yet been added to the DB
        if guild.id not in all_guild_ids:
            functions.add_new_guild(guild.id)
            send_changelog = True
        # If guild had been added to the DB, removed the bot, then rejoined. Should never be needed
        # due to on_guild_join, but better safe than sorry
        elif not next((item for item in all_guilds if item["id"] == guild.id and item["active"]), False):
            functions.set_active_guild(guild.id)

        # Encompasses rejoining guilds and pre-existing
        if not send_changelog:
            latest_sent = functions.get_guild_changelog_version(guild.id)
            if latest_sent is None:
                break
            if latest_sent < int(latest_key):
                send_changelog = True

        if send_changelog:
            send_changelog = False
            functions.set_guild_changelog_version(guild.id, int(latest_key))
            channel: discord.TextChannel = guild.system_channel
            await channel.send(
                f"# NEW UPDATE:\n{functions.format_update(changelog[latest_key])}"
            )


async def on_guild_join(guild: Guild):
    guild_result = functions.get_guild(guild.id)
    if guild_result is None:
        return

    # New guild
    if not guild_result:
        functions.add_new_guild(guild.id)
    # Rejoining so all the setup is already there
    else:
        functions.set_active_guild(guild.id)


async def on_reaction_add(reaction: Reaction, user: Person):
    guild_id = reaction.message.guild.id
    last_reactor = functions.get_last_reactor(guild_id)
    if last_reactor is None:
        return

    if not last_reactor:
        functions.set_last_reactor(guild_id, user.id)
    else:
        if user.id == last_reactor:
            return
        else:
            functions.set_last_reactor(guild_id, user.id)

    try:
        reaction_name: str = str(reaction.emoji.name)
    except AttributeError:
        reaction_name: str = reaction.emoji
    # Sends corresponding message based on reaction made.
    if reaction_name in constants.REACTION_IMAGES:
        await reaction.message.channel.send(constants.REACTION_IMAGES[reaction_name])


# CUSTOM COMMANDS
async def claim(guild: Guild, channel: Channel, author: Person):
    current_claimable = functions.get_current_coin_claimable(guild.id)
    if current_claimable is None:
        return

    print(current_claimable)
    if not current_claimable:
        await channel.send("No crate to claim!")
        return

    # Make sure we're claiming it in the right channel, to avoid confusion
    if channel.id != current_claimable["currentChannel"]:
        await channel.send("The crate is in a different channel. Claim it there!")
        return

    member_info: Member = guild.get_member(author.id)
    score: int = functions.get_random_number(10, 30)

    await channel.send(
        f"{member_info.display_name} claimed the crate."
        f" They got {score} coins!"
    )

    # Prepare and send edited message for the original crate message
    await functions.edit_crate_message(current_claimable["current"], channel, member_info)

    functions.update_coin_score(member_info.id, score)

    functions.set_current_coin_claimable(guild.id, None, None)
    functions.set_coin_last_caught(guild.id)


async def clam(guild: Guild, channel: Channel, author: Person):
    current_claimable = functions.get_current_clam_claimable(guild.id)
    if current_claimable is None:
        return

    if not current_claimable:
        await channel.send("No clam to claim!")
        return

    # Make sure we're claiming it in the right channel, to avoid confusion
    if channel.id != current_claimable["currentChannel"]:
        await channel.send("The clam to claim is clearly elsewhere. Claim it there!")
        return

    member_info: Member = guild.get_member(author.id)

    await channel.send(
        f"{member_info.display_name} claimed the clam, clearing the clog of clams to claim."
    )

    # Prepare and send edited message for the original crate message
    await functions.edit_clam_message(current_claimable["current"], channel, member_info)

    functions.update_clam_score(member_info.id)

    functions.set_current_clam_claimable(guild.id, None, None)
    functions.set_clam_last_caught(guild.id)


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

    chosen_insult: int = functions.get_random_number(0, len(constants.INSULTS)-1)
    insult_message: str = constants.INSULTS[chosen_insult].format(arg=user, arg2=f"<@!{author.id}>")

    await channel.send(insult_message)


async def meme(channel: Channel):
    meme_url: str = functions.get_meme()
    meme_embed: Embed = discord.Embed(title="", description="")
    meme_embed.set_image(url=meme_url)

    await channel.send(embed=meme_embed)


async def recent(channel: Channel):
    data: Dict[str, Any]
    latest_key: str
    data, latest_key = functions.retrieve_changelog()

    await channel.send(functions.format_update(data[latest_key]))


async def restrict(member: Member, moderator: Person, guild: Guild):
    permissions_revoked = []

    for channel in guild.text_channels:
        permissions = channel.permissions_for(member)
        # Only apply restriction on channels they could send messages in before
        # This is important so the bot doesn't grant send_message permissions to all channels for that user later
        if permissions.send_messages:
            permissions_revoked.append(channel.id)
            await channel.set_permissions(
                member,
                send_messages=False,
                reason="Bonk!"
            )
    functions.set_moderation_info(member.id, guild.id, moderator.id, ModerationType.Mute, permissions_revoked.__str__())


async def smite(channel: Channel, user: str, self: bool):
    if self:
        await channel.send(f"<@!{user}> was confused, and hurt themselves!")
    else:
        await channel.send(f"The gods dislike you, {user}. They smite you into oblivion.")


async def unrestrict(member: Member, guild: Guild) -> bool:
    permissions_revoked: list[int] | bool = functions.get_moderation_info(member.id, guild.id, ModerationType.Mute)
    # No permission revoked, so no changes to make
    if type(permissions_revoked) == bool:
        return False

    for channel in guild.text_channels:
        if channel.id in permissions_revoked:
            await channel.set_permissions(
                member,
                send_messages=True,
                reason="Unbonk!"
            )

    functions.remove_moderation_info(member.id, guild.id, ModerationType.Mute)

    return True


async def update(channel: Channel, version: str | None):
    if version is None:
        await recent(channel)
        return

    data: Dict[str, Any]
    data, _ = functions.retrieve_changelog()
    # Get the update versions in a list
    titles: List[Tuple[str, str]] = [(key, item['title']) for key, item in data.items()]
    # Check for likeness with user input
    key: str = functions.find_title(version, titles)
    if key == "-1":
        await channel.send("Hmm, I couldn't find a version like that!")
        return

    await channel.send(functions.format_update(data[key]))
