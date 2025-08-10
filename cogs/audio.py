import os
from os.path import isfile, join
from pathlib import Path

from discord import VoiceChannel, VoiceClient, FFmpegOpusAudio, HTTPException
from discord.ext import commands
from discord.ext.commands.context import Context
from mutagen import File

from cogs.cog_template import CogTemplate
from datatypes import DefaultInput
from enums import TrackSortType
from embeds import generate_tracklist_embed, generate_playing_embed
from paginator import Paginator


class AudioCog(CogTemplate):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @commands.command()
    async def join(self, ctx: Context):
        if ctx.voice_client:
            await ctx.send("Already in a voice channel!")
            return

        if ctx.author.voice is None:
            await ctx.send("You need to join a voice channel first!")
            return
        voice_channel: VoiceChannel = ctx.author.voice.channel

        await voice_channel.connect()

    @commands.command()
    async def leave(self, ctx: Context):
        if ctx.voice_client is None:
            await ctx.send("I'm not in a voice channel!")
            return

        # ctx.voice_client technically returns VoiceProtocol, but it can
        # be assigned as a VoiceClient, which gives us the audio functionality
        voice_client: VoiceClient = ctx.voice_client
        if voice_client.is_playing():
            # This may throw up an ffmpeg message in the console, but it can be
            # ignored
            voice_client.stop()
        await voice_client.disconnect()

    @commands.command()
    async def play(self, ctx: Context):
        if not ctx.voice_client:
            await ctx.send("I'm not in a voice channel!")
            return

        voice_client: VoiceClient = ctx.voice_client
        audio = FFmpegOpusAudio(f"audiofiles/{ctx.guild.id}/example_audio.mp3")
        voice_client.play(audio)
        playing = generate_playing_embed(f"audiofiles/{ctx.guild.id}/example_audio.mp3")
        await ctx.send(embed=playing)

    @commands.command()
    async def stop(self, ctx: Context):
        if ctx.voice_client:
            vc: VoiceClient = ctx.voice_client
            if vc.is_playing():
                vc.stop()

    @commands.command()
    async def add(self, ctx: Context, name: DefaultInput):
        if ctx.message.attachments.__len__() == 0:
            await ctx.send("Please attach an audio file.")
            return

        file = ctx.message.attachments[0]
        if file.content_type.find("audio") == -1:
            await ctx.send("Please attach audio files only!")

        if not os.path.isdir("audiofiles"):
            os.mkdir("audiofiles")

        if not os.path.isdir(f"audiofiles/{ctx.guild.id}"):
            os.mkdir(f"audiofiles/{ctx.guild.id}")

        audio_dir = Path(f"audiofiles/{ctx.guild.id}")

        if name is not None:
            file_ext = file.filename.split(".")[-1]
            filename = name + "." + file_ext
        else:
            filename = file.filename

        save_path = audio_dir / filename

        try:
            await file.save(save_path)
            await ctx.send("Track added!")
        except HTTPException:
            await ctx.send("Track failed to upload.")

    @commands.command()
    async def tracklist(self, ctx: Context, sort_type: int = 0):
        filepath = f"audiofiles/{ctx.guild.id}"
        audiofiles = [file for file in os.listdir(filepath) if isfile(join(filepath, file))]

        match sort_type:
            case TrackSortType.AlphabeticalAsc.value:
                audiofiles.sort()
            case TrackSortType.AlphabeticalDes.value:
                audiofiles.sort(reverse=True)
            case TrackSortType.DurationAsc.value:
                audiofiles.sort(key=lambda f: File(join(filepath, f)).info.length)
            case TrackSortType.DurationDes.value:
                audiofiles.sort(key=lambda f: File(join(filepath, f)).info.length, reverse=True)

        # Split into pages of items
        audiofiles_bins = [audiofiles[x:x + 10] for x in range(0, len(audiofiles), 10)]

        tracklist_paginator = Paginator(generate_tracklist_embed,
                                        len(audiofiles_bins),
                                        {'audioFiles': audiofiles_bins}
                                        )

        tracklist_paginator.message = await ctx.channel.send(
            embed=tracklist_paginator.call().set_footer(text=f"Page 1 of {tracklist_paginator.max_page}"),
            view=tracklist_paginator
        )
