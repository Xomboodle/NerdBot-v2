"""main.py"""

# IMPORTS #
import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

from webserver import keep_alive

import commands as customs

import functions

import constants

# Set the variables in .env file as environment variables
load_dotenv()

# Token requires environment variable, which uses os import.
# By general rule, we want to avoid having imports in constants.py, except for typing,
# so this will be set here instead.
TOKEN: str = os.environ.get('TOKEN')

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


try:
    keep_alive()
    bot.run(TOKEN)
except discord.errors.HTTPException:
    os.system('kill 1')
