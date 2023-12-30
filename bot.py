"""main.py"""

# IMPORTS #
import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

from webserver import keep_alive

import commands as customs

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


try:
    keep_alive()
    bot.run(TOKEN)
except discord.errors.HTTPException:
    os.system('kill 1')
