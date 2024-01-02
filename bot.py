"""main.py"""

# IMPORTS #
import os

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands.context import Context

from dotenv import load_dotenv

from webserver import keep_alive

import commands as customs

import functions

import embeds

# Set the variables in .env file as environment variables
load_dotenv()

# Token requires environment variable, which uses os import.
# By general rule, we want to avoid having imports in constants.py, except for typing,
# so this will be set here instead.
TOKEN: str = os.environ.get('TOKEN')

# region Setup
"""
    Setting up the bot. Includes permissions, activity display on the profile,
    and the bot itself.
"""
# Permissions
intents = discord.Intents.all()
# Bot activity
activity = discord.Activity(type=discord.ActivityType.playing,
                            name="you for a fool")
# The bot
bot = commands.Bot(command_prefix='?', activity=activity,
                   help_command=None, intents=intents)

# Uses command prefix, so needs that set first
HELP = embeds.generate_help_embed(bot.command_prefix)
# endregion


# region Listen Events
@bot.listen()
async def on_ready():
    await customs.on_ready(bot=bot)


@bot.listen()
async def on_guild_join(guild: discord.Guild):
    await customs.on_guild_join(guild)


@bot.listen()
async def on_message(message: discord.Message):
    message_content: str = message.content.lower()

    # Don't check messages sent by the bot itself
    if functions.validate_author(message.author, bot):
        return

    await functions.generate_claimable(message.guild, message.channel)

    await functions.respond_to_message(message.channel, message_content, bot)


@bot.listen()
async def on_reaction_add(reaction: discord.Reaction, user: discord.User | discord.Member):
    await customs.on_reaction_add(reaction, user)
# endregion


@bot.command()
@has_permissions(manage_permissions=True)
async def bonk(ctx: Context, member: discord.Member):
    if not functions.validate_usertype(member, type(discord.Member)):
        await ctx.send(f"{member} is an invalid input.")
        return
    # Restrict user
    for channel in ctx.guild.text_channels:
        # Convert member to user role
        user: discord.User = await bot.fetch_user(member.id)
        permissions = channel.overwrites_for(user)
        permissions.update(send_messages=False)
        await channel.set_permissions(
            member,
            overwrite=permissions,
            reason="Bonk!"
        )
    await ctx.send(f"<@!{member.id} has been sent to jail.")


@bot.command()
async def claim(ctx: Context):
    await customs.claim(ctx.guild, ctx.channel, ctx.author)


@bot.command()
async def clam(ctx: Context):
    await customs.clam(ctx.guild, ctx.channel, ctx.author)


@bot.command()
async def help(ctx: Context):
    await ctx.channel.send(embed=HELP)


@bot.command()
async def highscore(ctx: Context):
    await functions.get_leaderboard(ctx.guild, ctx.channel, True)


@bot.command()
async def clamscore(ctx: Context):
    await functions.get_leaderboard(ctx.guild, ctx.channel, False)


try:
    keep_alive()
    bot.run(TOKEN)
except discord.errors.HTTPException:
    os.system('kill 1')
