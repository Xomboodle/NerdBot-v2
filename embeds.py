"""embeds.py"""

import discord
from discord import Embed


def generate_help_embed(prefix: str = '!', page: int = 0) -> Embed:
    help_embed: Embed = discord.Embed(
        title=f"Command Help (Prefix {prefix})",
        color=discord.Color.blurple()
    )

    match page:
        case 0:
            core_help(help_embed)
        case 1:
            interaction_help(help_embed)
        case 2:
            collectible_help(help_embed)
        case 3:
            moderation_help(help_embed)
        case _:
            core_help(help_embed)

    return help_embed


def core_help(embed: Embed):
    embed.description = "Core commands:"
    embed.add_field(
        name="help",
        value="```It's what you're doing now.```"
    )
    embed.add_field(
        name="recent",
        value="```Check the most recent update the bot has, in case you missed it.```"
    )
    embed.add_field(
        name="update <version>",
        value="```See any update of your choosing. Enter a version, and Nerdbot will try to find the closest result.```"
    )


def interaction_help(embed: Embed):
    embed.description = "Interaction commands:"
    embed.add_field(
        name="insult <user>",
        value="```Will violently attack the mentioned user (for legal reasons this is a joke).```"
    )
    embed.add_field(
        name="meme",
        value="```Displays a meme from r/memes.```"
    )
    embed.add_field(
        name="smite <user>",
        value="```Summon the power of the gods on some poor unfortunate soul.```"
    )


def collectible_help(embed: Embed):
    embed.description = "Collectible commands:"
    embed.add_field(
        name="claim",
        value="```Claim a crate if there is one available.```"
    )
    embed.add_field(
        name="clam",
        value="```Claim a clam if there's a clam to claim.```"
    )
    embed.add_field(
        name="clams",
        value="```Clear your clogged cloud of ...cloughts... with your collection of clams.```"
    )
    embed.add_field(
        name="clamscore",
        value="```Like highscore, but for clams.```"
    )
    embed.add_field(
        name="coins",
        value="```See how many coins you have, and weep in despair when they are all gone.```"
    )
    embed.add_field(
        name="highscore",
        value="```See who's better, or worse, at gambling their life savings.```"
    )


def moderation_help(embed: Embed):
    embed.description = "Moderation commands. Will require certain permissions."
    embed.add_field(
        name="bonk <user>",
        value="```See mute command.```"
    )
    embed.add_field(
        name="mute <user>",
        value="```Send a user to jail. Requires Manages Permissions to use.```"
    )
    embed.add_field(
        name="unbonk <user>",
        value="```See unmute command```"
    )
    embed.add_field(
        name="unmute <user>",
        value="```Release a user from jail. Requires Manages Permissions.```"
    )
