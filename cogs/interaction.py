from discord import Embed
from discord.ext import commands
from discord.ext.commands.context import Context

from cogs.cog_template import CogTemplate
from constants import INSULTS
from datatypes import DefaultInput
from functions import get_random_number, get_meme


class InteractionCog(CogTemplate):

    @commands.command()
    async def insult(self, ctx: Context, user: DefaultInput = None):
        channel, message, author = ctx.channel, ctx.message, ctx.message.author

        if user is None:
            await channel.send("At least choose someone to insult!")
            return

        await message.delete()

        chosen_insult: int = get_random_number(0, len(INSULTS)-1)
        insult_message: str = INSULTS[chosen_insult].format(arg=user, arg2=f"<@!{author.id}>")

        await channel.send(insult_message)

    @commands.command()
    async def meme(self, ctx: Context):
        channel = ctx.channel

        meme_url: str = get_meme()
        meme_embed: Embed = Embed(title="", description="")
        meme_embed.set_image(url=meme_url)

        await channel.send(embed=meme_embed)

    @commands.command()
    async def smite(self, ctx: Context, user: DefaultInput = None):
        channel, author_id = ctx.channel, ctx.message.author.id

        is_self: bool = True if user is None else False

        if is_self:
            await channel.send(f"<@!{author_id}> was confused, and hurt themselves!")
        else:
            await channel.send(f"The gods dislike you, {user}. They smite you into oblivion.")
