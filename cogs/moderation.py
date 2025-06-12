from typing import List

from discord import Member
from discord.ext import commands
from discord.ext.commands import CommandError, CheckFailure
from discord.ext.commands.context import Context

from cogs.cog_template import CogTemplate
from datatypes import DefaultInput
from enums import ModerationType
from functions import (
    get_moderation_info,
    remove_moderation_info,
    set_moderation_info,
    validate_usertype,
)


manage_permissions_commands = ['bonk', 'unbonk']


class ModerationCog(CogTemplate):

    async def cog_check(self, ctx: Context) -> bool:
        # Check if user has relevant permissions for command used
        name, permissions = ctx.command.name, ctx.author.guild_permissions

        if name in manage_permissions_commands and permissions.manage_permissions:
            return True

        # Throws a CheckFailure error, which is handled by cog_command_error
        return False

    async def cog_command_error(self, ctx: Context, error: CommandError):
        channel = ctx.channel

        # Tell user command is restricted
        if isinstance(error, CheckFailure):
            await channel.send("You don't have permission for that!")

    @commands.command(aliases=['mute'])
    async def bonk(self, ctx: Context, member: Member | DefaultInput):
        channel, guild, moderator = ctx.channel, ctx.guild, ctx.author

        if member is None:
            await channel.send("No input given.")
            return

        if not validate_usertype(member, Member):
            await channel.send(f"{member} is not a valid input.")
            return

        permissions_revoked = []
        for text_channel in guild.text_channels:
            permissions = text_channel.permissions_for(member)
            # Only restrict channels they could message in before.
            if permissions.send_messages:
                permissions_revoked.append(text_channel.id)
                await text_channel.set_permissions(
                    member,
                    send_messages=False,
                    reason="Bonk!"
                )

        set_moderation_info(member.id,
                            guild.id,
                            moderator.id,
                            ModerationType.Mute,
                            permissions_revoked.__str__()
                            )

        await channel.send(f"<@!{member.id}> has been sent to jail.")

    @commands.command(aliases=['unmute'])
    async def unbonk(self, ctx: Context, member: Member | DefaultInput):
        channel, guild = ctx.channel, ctx.guild

        if member is None:
            await channel.send("No input given.")
            return

        if not validate_usertype(member, Member):
            await ctx.send(f"{member} is not a valid input.")
            return

        permissions_revoked: List[int] | bool = get_moderation_info(
            member.id,
            guild.id,
            ModerationType.Mute
        )

        # No permissions revoked.
        if isinstance(permissions_revoked, bool):
            await channel.send("Looks like I haven't changed that user's permissions at all. No changes needed!")
            return

        for text_channel in guild.text_channels:
            if text_channel.id in permissions_revoked:
                await text_channel.set_permissions(
                    member,
                    send_messages=True,
                    reason="Unbonk!"
                )

        remove_moderation_info(member.id, guild.id, ModerationType.Mute)
        await channel.send(f"<@!{member.id}> has been released from jail.")
