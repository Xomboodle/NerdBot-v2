import os
from typing import Dict, Any

import discord
from discord import Guild, Reaction, Message
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

from cogs.collectible import CollectibleCog
from constants import REACTION_IMAGES
from functions import (
    add_new_guild,
    format_update,
    get_all_guilds,
    get_guild,
    get_guild_changelog_version,
    get_last_reactor,
    respond_to_message,
    retrieve_changelog,
    set_active_guild,
    set_guild_changelog_version,
    set_last_reactor,
    validate_author
)
from cogs.cog_template import CogTemplate
from datatypes import Guilds, Person

load_dotenv()

#


class NerdBot(Bot):

    def __init__(self):
        intents = discord.Intents.all()
        self.TOKEN = os.environ.get('TOKEN')
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.cogs_to_load = [
            CollectibleCog(self)
        ]

    async def setup_hook(self) -> None:
        for cog in self.cogs_to_load:
            await self.add_cog(cog)
        # Intentionally load last
        await self.add_cog(NerdCoreCog(self))


class NerdCoreCog(CogTemplate):

    @commands.Cog.listener()
    async def on_ready(self):
        await super().on_ready()

        changelog: Dict[str, Any]
        latest_key: str
        changelog, latest_key = retrieve_changelog()

        all_guilds: Guilds | None = get_all_guilds()
        all_guild_ids = [x["id"] for x in all_guilds]

        send_changelog = False
        for guild in self.bot.guilds:
            if all_guilds is None:
                break

            if guild.id not in all_guild_ids:
                add_new_guild(guild.id)
                send_changelog = True
            elif not next((item for item in all_guilds if item["id"] == guild.id and item["active"]), False):
                set_active_guild(guild.id)

            if not send_changelog:
                latest_sent: int | None = get_guild_changelog_version(guild.id)
                if latest_sent is None:
                    break
                if latest_sent < int(latest_key):
                    send_changelog = True

            if send_changelog:
                send_changelog = False
                set_guild_changelog_version(guild.id, int(latest_key))
                channel: discord.TextChannel = guild.system_channel
                if channel is not None:
                    await channel.send(
                        f"# NEW UPDATE:\n{format_update(changelog[latest_key])}"
                    )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        guild_result: Guild | bool | None = get_guild(guild.id)
        if guild_result is None:
            return

        # New guild
        if not guild_result:
            add_new_guild(guild.id)
        # Bot is rejoining guild
        else:
            set_active_guild(guild.id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Person):
        guild_id: int = reaction.message.guild.id
        last_reactor = get_last_reactor(guild_id)
        if last_reactor is None:
            return

        # Spam prevention
        if not last_reactor:
            set_last_reactor(guild_id, user.id)
        elif last_reactor != user.id:
            set_last_reactor(guild_id, user.id)
        else:
            return

        if isinstance(reaction.emoji, str):
            reaction_name: str = reaction.emoji
        else:
            reaction_name: str = reaction.emoji.name

        if reaction_name in REACTION_IMAGES:
            await reaction.message.channel.send(REACTION_IMAGES[reaction_name])

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        message_content: str = message.content.lower()

        # Ignore own messages
        if validate_author(message.author, self.bot):
            return

        await respond_to_message(message.channel, message_content, self.bot)


nerdbot = NerdBot()
nerdbot.run(nerdbot.TOKEN)
