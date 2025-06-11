import os
from typing import Dict, Any

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

import functions
from cogs.cog_template import CogTemplate
from datatypes import Guilds

load_dotenv()


class NerdBot(Bot):

    def __init__(self):
        intents = discord.Intents.all()
        self.TOKEN = os.environ.get('TOKEN')
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        await self.add_cog(NerdCoreCog(self))


class NerdCoreCog(CogTemplate):

    @commands.Cog.listener()
    async def on_ready(self):
        await super().on_ready()

        changelog: Dict[str, Any]
        latest_key: str
        changelog, latest_key = functions.retrieve_changelog()

        all_guilds: Guilds | None = functions.get_all_guilds()
        all_guild_ids = [x["id"] for x in all_guilds]

        send_changelog = False
        for guild in self.bot.guilds:
            if all_guilds is None:
                break

            if guild.id not in all_guild_ids:
                functions.add_new_guild(guild.id)
                send_changelog = True
            elif not next((item for item in all_guilds if item["id"] == guild.id and item["active"]), False):
                functions.set_active_guild(guild.id)

            if not send_changelog:
                latest_sent: int | None = functions.get_guild_changelog_version(guild.id)
                if latest_sent is None:
                    break
                if latest_sent < int(latest_key):
                    send_changelog = True

            if send_changelog:
                send_changelog = False
                functions.set_guild_changelog_version(guild.id, int(latest_key))
                channel: discord.TextChannel = guild.system_channel
                if channel is not None:
                    await channel.send(
                        f"# NEW UPDATE:\n{functions.format_update(changelog[latest_key])}"
                    )


nerdbot = NerdBot()
nerdbot.run(nerdbot.TOKEN)

