from discord.ext import commands
from discord.ext.commands import Cog, Bot


class CogTemplate(Cog):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(type(self).__name__, "connected.")
