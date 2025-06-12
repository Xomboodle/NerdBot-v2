from discord import Message, Member, Embed
from discord.ext import commands
from discord.ext.commands.context import Context

from cogs.cog_template import CogTemplate
from functions import (
    edit_clam_message,
    edit_crate_message,
    generate_claimable,
    get_clam_score,
    get_coin_score,
    get_current_clam_claimable,
    get_current_coin_claimable,
    get_leaderboard,
    get_random_number,
    set_clam_last_caught,
    set_coin_last_caught,
    set_current_clam_claimable,
    set_current_coin_claimable,
    update_clam_score,
    update_coin_score,
    validate_author,
)


class CollectibleCog(CogTemplate):

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if validate_author(message.author, self.bot):
            return

        await generate_claimable(message.guild, message.channel)

    @commands.command()
    async def claim(self, ctx: Context):
        guild, channel, author = ctx.guild, ctx.channel, ctx.author

        current_claimable = get_current_coin_claimable(guild.id)
        if current_claimable is None:
            return

        if not current_claimable:
            await channel.send("No crate to claim!")
            return

        # Claim only in the same channel as the collectible
        if channel.id != current_claimable["currentChannel"]:
            await channel.send("The crate is in a different channel. Claim it there!")
            return

        member_info: Member = guild.get_member(author.id)
        score: int = get_random_number(10, 30)

        await channel.send(
            f"{member_info.display_name} claimed the crate."
            f" They got {score} coins!"
        )

        # Edit original crate message
        await edit_crate_message(current_claimable["current"], channel, member_info)

        update_coin_score(member_info.id, score)

        set_current_coin_claimable(guild.id, None, None)
        set_coin_last_caught(guild.id)

    @commands.command()
    async def clam(self, ctx: Context):
        guild, channel, author = ctx.guild, ctx.channel, ctx.author

        current_claimable = get_current_clam_claimable(guild.id)
        if current_claimable is None:
            return

        if not current_claimable:
            await channel.send("No claim to claim!")
            return

        # Claim in the same channel as the collectible
        if channel.id != current_claimable["currentChannel"]:
            await channel.send("The clam is clearly elsewhere. Claim it there!")
            return

        member_info: Member = guild.get_member(author.id)

        await channel.send(
            f"{member_info.display_name} claimed the clam, clearing the clog of"
            f" clams to claim."
        )

        # Edit original clam message
        await edit_clam_message(current_claimable["current"], channel, member_info)

        update_clam_score(member_info.id)

        set_current_clam_claimable(guild.id, None, None)
        set_clam_last_caught(guild.id)

    @commands.command()
    async def coins(self, ctx: Context):
        channel, author = ctx.channel, ctx.author

        score = get_coin_score(author.id)
        await channel.send(
            f"You have **{score}** coins!"
        )

    @commands.command()
    async def clams(self, ctx: Context):
        channel, author = ctx.channel, ctx.author

        score = get_clam_score(author.id)
        await channel.send(
            f"You've claimed **{score}** clams!"
        )

    @commands.command()
    async def clamscore(self, ctx: Context):
        guild, channel = ctx.guild, ctx.channel

        leaderboard: Embed = get_leaderboard(guild, False)
        await channel.send(embed=leaderboard)

    @commands.command()
    async def highscore(self, ctx: Context):
        guild, channel = ctx.guild, ctx.channel

        leaderboard: Embed = get_leaderboard(guild, True)
        await channel.send(embed=leaderboard)
