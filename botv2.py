import os
from typing import Dict, Any, List, Tuple

import discord
from discord import Guild, Reaction, Message
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.context import Context
from dotenv import load_dotenv

from cogs.collectible import CollectibleCog
from cogs.interaction import InteractionCog
from cogs.moderation import ModerationCog
from constants import REACTION_IMAGES
from embeds import generate_help_embed
from functions import (
    add_new_guild,
    find_title,
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
from datatypes import Guilds, Person, DefaultInput

load_dotenv()


class NerdBot(Bot):

    def __init__(self):
        intents = discord.Intents.all()
        self.TOKEN = os.environ.get('TOKEN')
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.cogs_to_load = [
            CollectibleCog(self),
            InteractionCog(self),
            ModerationCog(self)
        ]

    async def setup_hook(self) -> None:
        for cog in self.cogs_to_load:
            await self.add_cog(cog)
        # Intentionally load last
        await self.add_cog(NerdCoreCog(self))


class NerdCoreCog(CogTemplate):
    """
    The core cog. Will always be enabled in every guild the bot is a part of.
    """
    def __init__(self, bot: NerdBot):
        super().__init__(bot)
        self.changelog: Dict[str, Any] = {}
        self.latest_key: str = ""

    @commands.Cog.listener()
    async def on_ready(self):
        await super().on_ready()

        self.changelog, self.latest_key = retrieve_changelog()

        all_guilds: Guilds | None = get_all_guilds()
        all_guild_ids = [x["id"] for x in all_guilds]

        send_changelog = False
        for guild in self.bot.guilds:
            if all_guilds is None:
                break

            # Not yet in DB
            if guild.id not in all_guild_ids:
                add_new_guild(guild.id)
                send_changelog = True
            # If in DB, removed bot, then rejoined.
            elif not next((item for item in all_guilds if item["id"] == guild.id and item["active"]), False):
                set_active_guild(guild.id)

            # If in DB and changelog version is outdated.
            if not send_changelog:
                latest_sent: int | None = get_guild_changelog_version(guild.id)
                if latest_sent is None:
                    break
                if latest_sent < int(self.latest_key):
                    send_changelog = True

            if send_changelog:
                send_changelog = False
                set_guild_changelog_version(guild.id, int(self.latest_key))
                channel: discord.TextChannel = guild.system_channel
                if channel is not None:
                    await channel.send(
                        f"# NEW UPDATE:\n{format_update(self.changelog[self.latest_key])}"
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

    @commands.command()
    async def help(self, ctx: Context):
        channel = ctx.channel

        help_embed = generate_help_embed(prefix=self.bot.command_prefix)
        await channel.send(embed=help_embed)

    @commands.command()
    async def update(self, ctx: Context, search: DefaultInput = None):
        channel = ctx.channel

        # Essentially calling recent
        if search is None:
            await channel.send(format_update(self.changelog[self.latest_key]))
            return

        titles: List[Tuple[str, str]] = [
            (key, item['title']) for key, item in self.changelog.items()
        ]
        key: str = find_title(search, titles)
        if key == "-1":
            await channel.send("Hmm, I couldn't find a version like that!")
            return

        await channel.send(format_update(self.changelog[key]))

    @commands.command()
    async def recent(self, ctx: Context):
        channel = ctx.channel

        await channel.send(format_update(self.changelog[self.latest_key]))


nerdbot = NerdBot()
nerdbot.run(nerdbot.TOKEN)
