"""embeds.py"""

import discord
from discord import Embed


def generate_help_embed(prefix: str) -> Embed:
    help_embed: Embed = discord.Embed(
        title=f"Command Help (Prefix {prefix})",
        color=discord.Color.blurple()
    )
    help_embed.add_field(
        name="bonk <user>",
        value="```Send a user to jail. Requires Manages Permissions to use.```"
    )
    help_embed.add_field(
        name="claim",
        value="```Claim a crate if there is one available.```"
    )
    help_embed.add_field(
        name="clam",
        value="```Claim a clam if there's a clam to claim.```"
    )
    help_embed.add_field(
        name="coins",
        value="```See how many coins you have, and weep in despair when they are all gone.```"
    )
    help_embed.add_field(
        name="help",
        value="```It's what you're doing now.```"
    )
    help_embed.add_field(
        name="highscore",
        value="```See who's better, or worse, at gambling their life savings.```"
    )
    help_embed.add_field(
        name="insult <user>",
        value="```Will violently attack the mentioned user (for legal reasons this is a joke).```"
    )
    help_embed.add_field(
        name="meme",
        value="```Displays a meme from r/memes.```"
    )
    help_embed.add_field(
        name="recent",
        value="```Check the most recent update the bot has, in case you missed it.```"
    )
    help_embed.add_field(
        name="helprpg",
        value="```View commands related to adventuring.```"
    )
    help_embed.add_field(
        name="rps <option[rock,paper,scissors]> <bet>",
        value="```A simple game of rock, paper, scissors.```"
    )
    help_embed.add_field(
        name="prefix <prefix>",
        value="```Change the bot command prefix to something else. Requires bot ownership / being on the whitelist.```"
    )
    help_embed.add_field(
        name="smite <user>",
        value="```Summon the power of the gods on some poor unfortunate soul.```"
    )
    help_embed.add_field(
        name="unbonk <user>",
        value="```Release a user from jail. Requires Manages Permissions.```"
    )
    help_embed.add_field(
        name="update",
        value="```See a bunch of more recent updates in one long, horrible list.```"
    )

    return help_embed
