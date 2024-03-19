import asyncio
import logging
from asyncio import AbstractEventLoop
from typing import Any

import discord
import yt_dlp.utils
from discord import AudioSource
from discord.ext import commands
from discord.utils import get
from yt_dlp import YoutubeDL

from discord_bot.util.playlist_manager import AudioFile, PlaylistManager
from discord_bot.util.role import to_priority

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ydl_options = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "noplaylist": True,
    "skip_download": True,
    "quiet": True,
}
ydl = YoutubeDL(ydl_options)

logger = logging.getLogger('discord')


class YTDLSource(discord.PCMVolumeTransformer):
    """
    Represents a YouTube audio source that can be played by a discord bot.

    This class allows to adjust the volume of the audio.

    Attributes:
    """

    def __init__(self, source: AudioSource, *, data: dict[str, Any], volume: float = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data["title"]
        self.url = data["url"]

    @classmethod
    async def from_url(cls, url: str, *, volume: float = 0.5, loop: AbstractEventLoop = None) -> "YTDLSource":
        """
        Construct a YTDLSource given the YouTube URL.

        Args:
            url (str):
                The URL of the YouTube video

            volume (float):
                The volume of the YTDLSource

            loop (AbstractEventLoop):
                The event loop to start the audio connection in the background

        Returns:
            YTDLSource:
                The audio source of the YouTube video
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        audio_source = data["url"]

        return cls(discord.FFmpegPCMAudio(audio_source, **ffmpeg_options), data=data, volume=volume)

    @staticmethod
    async def is_valid(url: str, loop: AbstractEventLoop = None) -> bool:
        """
        Checks whether the given YouTube URL is supported by YoutubeDL.

        Args:
            url (str):
                The URL of the YouTube video

            loop (AbstractEventLoop):
                The event loop to start the audio connection in the background

        Returns:
            bool:
                Returns True if the given url is supported, otherwise False
        """
        loop = loop or asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return True
        except yt_dlp.utils.YoutubeDLError:
            return False


class Music(commands.Cog):
    """
    This class represents a suite of commands to control a music bot in a Discord Server.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.playlist = PlaylistManager()
        self.volume = 0.5

    async def next(self, ctx: commands.Context, e):
        """
        Plays the next song in the playlist.
        """
        if self.playlist.empty():
            return await ctx.send("The playlist is empty!")

        # Get the voice client
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)

        # Stop playing the music
        voice_client.stop()

        # Play the next song
        player = await YTDLSource.from_url(self.playlist.pop().url, volume=self.volume, loop=self.bot.loop)
        voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.next(ctx, e), self.bot.loop))
        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def join(self, ctx: commands.Context):
        """
        Joins to the current voice channel.

        This command ensures that the bot is joining the current voice channel of the author.

        - If author is in no voice channel, then nothing happens.
        - If bot is in another voice channel, then it will move to the current voice channel.
        - If bot is already in the current voice channel, then noting happens.
        """
        if ctx.author.voice is None:
            # Case: Author is not in a voice channel
            return await ctx.send("You need to be in a voice channel!")

        author_channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            # Case: Bot is already in a voice channel
            bot_channel = ctx.voice_client.channel

            if author_channel == bot_channel:
                # Case: Bot is in the same channel with the author
                return await ctx.send(f"Stayed in '{bot_channel}'")

            # Case: Bot is not in the same channel with the author

            if ctx.voice_client.is_playing():
                # Case: Bot is currently playing
                ctx.voice_client.pause()
            await ctx.voice_client.move_to(author_channel)
            return await ctx.send(f"Moved from '{bot_channel}' to '{author_channel}'!")

        # Case: Bot is in no voice channel
        await ctx.send(f"Moved to '{author_channel}'!")
        await author_channel.connect()

    @commands.command(name="leave", help="Leaves the voice channel")
    async def leave(self, ctx: commands.Context):
        """
        This command ensures that the bot is leaving the voice channel.

        - If bot is not in a voice channel, then nothing happens.
        """
        if ctx.voice_client is not None:
            bot_channel = ctx.voice_client.channel
            await ctx.voice_client.disconnect(force=False)
            return await ctx.send(f"Left '{bot_channel}'!")
        await ctx.send(f"I need to be in a voice channel, before i can leave it!")

    @commands.command()
    async def add(self, ctx: commands.Context, *, url: str):
        """
        Adds a song (YouTube URL) to the playlist.

        This command ensures that the given YouTube URL is added to the playlist.
        If the given YouTube URL is not supported by YoutubeDL, then it will not be added to the playlist.

        Arguments:
            url (str):
                The URL of the YouTube video to be added to the playlist
        """
        # Check if the given url is valid
        is_valid = await YTDLSource.is_valid(url)
        if not is_valid:
            # Case: The url is not supported by YTDL
            return await ctx.send(f"Not supported by YTDL: '{url}'!")

        # Create the audio file with the priority
        priority = min([to_priority(role.name) for role in ctx.author.roles])
        audio_file = AudioFile(priority=priority, url=url)

        # Add the audio file to the playlist
        self.playlist.add(audio_file)
        await ctx.send(f"Added to the playlist: '{url}'!")

    @commands.command()
    async def play(self, ctx: commands.Context):
        """
        Start playing the next song from the playlist.

        This command ensures that the bot starts the audio playback by playing the first song from the playlist.
        If bot is not in a voice channel, then nothing happens.
        If bot is already playing songs, then nothing happens.
        If bot is paused, then it will resume playing the current song.
        If playlist is empty, then noting happens.
        """
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            return await ctx.send("I need to be in a voice channel, before i can play a song!")

        if ctx.voice_client.is_playing():
            # Case: Bot already plays music
            return await ctx.send("I am currently playing a song!")

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            ctx.voice_client.resume()
            return await ctx.send("Resume playing the current song!")

        if self.playlist.empty():
            # Case: There is no music in the playlist
            return await ctx.send("The playlist is empty!")

        # Start playing the next song from the playlist
        player = await YTDLSource.from_url(self.playlist.pop().url, volume=self.volume, loop=self.bot.loop)
        ctx.voice_client.play(
            player,
            after=lambda e: asyncio.run_coroutine_threadsafe(self.next(ctx, e), self.bot.loop)
        )
        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def pause(self, ctx: commands.Context):
        """
        Pauses the current played song.

        This command ensures that the bot pauses the playback of the current played song.
        If bot is not in a voice channel, then nothing happens.
        If bot is paused, then nothing happens.
        """
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            return await ctx.send("I need to be in a voice channel, before i can pause a song!")

        if not ctx.voice_client.is_playing():
            # Case: Bot does not play a song
            return await ctx.send("I need to play a song, before i can pause it!")

        # Case: Bot does play a song
        ctx.voice_client.pause()
        await ctx.send("Paused!")

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """
        Skips the current played song

        This command ensures that the bot skips the current played song and continues to play the next song from the
        playlist.
        If bot is not in a voice channel, then nothing happens.
        If bot is not playing/pausing a song, then nothing happens.
        If playlist is empty, then nothing happens.
        """
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            return await ctx.send("I need to be in a voice channel, before i can skip any song!")

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            # Case: Bot does not play any music
            return await ctx.send("I need to play/pause a song, before i can skip them!")

        # Stop playing the current music (and skip to the next one)
        ctx.voice_client.stop()

    @commands.command()
    async def remove(self, ctx: commands.Context, n: int):
        """
        Removes the first n songs from the playlist.

        This command ensures that the next n songs will be removed from the playlist.
        If the playlist does not have at least n songs, then nothing happens.

        Args:
            n (int):
                The number of next songs to be removed
        """
        try:
            await self.bot.loop.run_in_executor(None, lambda: self.playlist.remove(n=n))
            return await ctx.send(f"The next {n} songs are removed!")
        except ValueError:
            return await ctx.send(
                "No songs are removed, because your number does not match with the length of the playlist!"
            )

    @commands.command()
    async def reset(self, ctx: commands.Context):
        """
        Stops the current song and clears the playlist.

        This command ensures that the bot stops the current audio playback and the playlist will be reset.
        """
        # Clear the playlist
        self.playlist.clear()

        if ctx.voice_client:
            # Case: Bot is in a voice channel
            ctx.voice_client.stop()

        await ctx.send("The playlist is cleared!")

    @commands.command()
    async def show(self, ctx: commands.Context):
        """
        Displays the songs in the playlist (and currently played song).

        This command ensures that the bot will show the playlist including the currently played song.
        If playlist is empty, then nothing happens.
        If bot is not playing/pause a song, then it will only show the playlist.
        """
        summary = "Playlist:\n"
        if ctx.voice_client is not None and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            summary += f"Currently playing: {ctx.voice_client.source.title}\n"
        for i, audio in enumerate(self.playlist, 1):
            summary += f"{i}. {str(audio)}\n"

        if summary == "Playlist:\n":
            return await ctx.send("The playlist is empty!")
        await ctx.send(summary)

    @commands.command()
    async def volume(self, ctx: commands.Context, volume: int):
        """
        Changes the volume of the audio playback.

        If bot is not in a voice channel, then nothing happens.
        If bot is not playing/paused a song, then nothing happens.
        If volume is not in (0, 100) then nothing happens.

        Args:
            volume (int):
                The volume of the audio playback
        """
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            return await ctx.send("I need to be in a voice channel, before i can change the volume!")

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            # Case: Bot does not play/pause a song
            return await ctx.send("I need to play/pause a song, before i can change the volume!")

        if volume < 0 or volume > 100:
            return await ctx.send("The volume needs to be in between of 0 and 100!")

        # Change the volume of the audio playback
        self.volume = volume / 100
        ctx.voice_client.source.volume = self.volume
        await ctx.send(f"Changed volume to {volume}")
