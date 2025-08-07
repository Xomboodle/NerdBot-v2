from discord import VoiceChannel, VoiceClient, FFmpegOpusAudio
from discord.ext import commands
from discord.ext.commands.context import Context


import embeds
from cogs.cog_template import CogTemplate


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
        audio = FFmpegOpusAudio("example_audio.mp3")
        voice_client.play(audio)
        playing = embeds.generate_playing_embed("example_audio.mp3")
        await ctx.send(embed=playing)

    @commands.command()
    async def stop(self, ctx: Context):
        if ctx.voice_client:
            vc: VoiceClient = ctx.voice_client
            if vc.is_playing():
                vc.stop()

