import asyncio
import logging
from asyncio import AbstractEventLoop
from typing import Any

import discord
import yt_dlp.utils
from discord import AudioSource
from discord.ext import commands
from yt_dlp import YoutubeDL

from discord_bot.command.music_state import MusicState
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
        self.music_state = MusicState.DISCONNECT
        self.volume = 0.5

    async def next(self, ctx: commands.Context):
        """
        Plays the next song in the playlist.
        """
        if self.music_state != MusicState.PLAY and self.music_state != MusicState.PAUSE:
            # Case: Bot never played/paused a song before
            return

        if self.playlist.empty():
            return await ctx.send("Playlist is empty!")

        # Get the voice client
        voice_client = ctx.voice_client

        # Play the next song
        player = await YTDLSource.from_url(self.playlist.pop().url, volume=self.volume, loop=self.bot.loop)
        voice_client.play(player, after=lambda _: asyncio.run_coroutine_threadsafe(self.next(ctx), self.bot.loop))
        self.music_state = MusicState.PLAY
        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def join(self, ctx: commands.Context):
        """
        Joins to the current voice channel.

        This command ensures that the bot is joining the current voice channel of the author.

        Unusual cases being treated:
            - If author is not in a voice channel, then a warning message will be sent
            - If bot is in another voice channel, then it will move to voice channel and stops playing music
            - If bot is already in the current voice channel, then a warning message will be sent
        """
        author_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            await author_channel.connect()
            self.music_state = MusicState.CONNECT
            return await ctx.send(f"Moved to {author_channel}!")
        else:
            # Case: Bot is in a voice channel
            bot_channel = ctx.voice_client.channel
            if author_channel == bot_channel:
                # Case: Bot is in the same voice channel as the author
                return await ctx.send(f"Stayed in {bot_channel}!")

            # Case: Bot is not in the same voice channel as the author
            if ctx.voice_client.is_playing():
                # Case: Bot is currently playing - pause the music
                ctx.voice_client.pause()
                self.music_state = MusicState.PAUSE

            await ctx.voice_client.move_to(author_channel)
            return await ctx.send(f"Moved from {bot_channel} to {author_channel}!")

    @commands.command()
    async def leave(self, ctx: commands.Context):
        """
        Leaves the voice channel.

        This command ensures that the bot is leaving the voice channel.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
        """
        channel = ctx.voice_client.channel
        await ctx.voice_client.disconnect(force=False)
        self.music_state = MusicState.DISCONNECT
        return await ctx.send(f"Left {channel}!")

    @commands.command()
    async def add(self, ctx: commands.Context, *, url: str):
        """
        Adds a song (YouTube URL) to the playlist.

        This command ensures that the given YouTube URL is added to the playlist.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If given url is not supported, then it will not be added to the playlist and a warning message will
              be sent

        Args:
            url (str):
                The URL of the YouTube video to be added to the playlist
        """
        if not await YTDLSource.is_valid(url):
            # Case: The url is not supported
            return await ctx.send(f"Your given url {url} is not supported!")

        # Create the audio file and assign it with the highest priority
        priority = min([to_priority(role.name) for role in ctx.author.roles])
        audio_file = AudioFile(priority=priority, url=url)

        # Add the audio file to the playlist
        self.playlist.add(audio_file)
        await ctx.send(f"Added to the playlist: {url}!")

    @commands.command()
    async def play(self, ctx: commands.Context):
        """
        Start playing the next song from the playlist.

        This command ensures that the bot starts the audio playback by playing the first song from the playlist.#

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot is already playing songs, then a warning message will be sent
            - If bot is paused, then it will resume playing the current song
            - If playlist is empty, then a warning message will be sent
        """
        if ctx.voice_client.is_playing():
            # Case: Bot already plays music
            return await ctx.send(f"Currently playing: {ctx.voice_client.source.title}!")

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            ctx.voice_client.resume()
            self.music_state = MusicState.PLAY
            return await ctx.send(f"Resume playing: {ctx.voice_client.source.title}!")

        if self.playlist.empty():
            # Case: There is no music in the playlist
            return await ctx.send("Playlist is empty!")

        # Start playing the next song from the playlist
        player = await YTDLSource.from_url(self.playlist.pop().url, volume=self.volume, loop=self.bot.loop)
        ctx.voice_client.play(
            player,
            after=lambda _: asyncio.run_coroutine_threadsafe(self.next(ctx), self.bot.loop)
        )
        self.music_state = MusicState.PLAY
        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def pause(self, ctx: commands.Context):
        """
        Pauses the current played song.

        This command ensures that the bot pauses the playback of the current played song.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot does not play/pause any song, then a warning message will be sent
            - If bot already pauses a song, then a warning message will be sent
        """
        if ctx.voice_client.is_playing():
            # Case: Bot does not play a song
            ctx.voice_client.pause()
            self.music_state = MusicState.PAUSE
            return await ctx.send(f"Paused: {ctx.voice_client.source.title}!")

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            return await ctx.send(f"Still paused: {ctx.voice_client.source.title}!")

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """
        Skips the current played song.

        This command ensures that the bot skips the current played song and continues to play the next song from the
        playlist.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot does not play/pause any song, then a warning message will be sent
        """
        # Stop playing the current music (removes the audio stream and skip to the next one)
        ctx.voice_client.stop()

    @commands.command()
    async def remove(self, ctx: commands.Context, n: int):
        """
        Removes the first n songs from the playlist.

        This command ensures that the next n songs will be removed from the playlist.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If playlist does not have at least n songs, then a warning message will be sent

        Args:
            n (int):
                The number of next songs to be removed
        """
        if self.playlist.empty():
            return await ctx.send("Playlist is empty!")

        if n <= 0 or n > len(self.playlist):
            return await ctx.send(f"n should be in between of 1 and {len(self.playlist)}!")

        await self.bot.loop.run_in_executor(None, lambda: self.playlist.remove(n=n))
        return await ctx.send(f"{n} songs are removed from the playlist!")

    @commands.command()
    async def reset(self, ctx: commands.Context):
        """
        Stops the current song and clears the playlist.

        This command ensures that the bot stops the current audio playback and the playlist will be reset.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
        """
        # Clear the playlist
        self.playlist.clear()
        self.music_state = MusicState.CONNECT

        if ctx.voice_client.is_playing() or ctx.voice_client.is_pausing():
            # Case: Bot plays/pause a song
            ctx.voice_client.stop()

        await ctx.send("Playlist is reset!")

    @commands.command()
    async def show(self, ctx: commands.Context):
        """
        Displays the songs in the playlist (and currently played song).

        This command ensures that the bot will show the playlist including the currently played song.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
        """
        summary = "Playlist:\n"
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            summary += f"Currently playing: {ctx.voice_client.source.title}\n"
        for i, audio in enumerate(self.playlist, 1):
            summary += f"{i}. {str(audio)}\n"

        if summary == "Playlist:\n":
            return await ctx.send("Playlist is empty!")
        await ctx.send(summary)

    @commands.command()
    async def volume(self, ctx: commands.Context, volume: int):
        """
        Changes the volume of the audio playback.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If volume is not in (0, 100) then a warning message will be sent.

        Args:
            volume (int):
                The volume of the audio playback
        """
        if volume < 0 or volume > 100:
            return await ctx.send("Volume needs to be in between of 0 and 100!")

        # Change the volume of the audio playback
        self.volume = volume / 100
        ctx.voice_client.source.volume = self.volume
        await ctx.send(f"Changed volume to {volume}!")

    @join.before_invoke
    async def check_author_voice(self, ctx: commands.Context):
        if ctx.author.voice is None:
            # Case: Author is not in a voice channel
            await ctx.send("You need to be connected to a voice channel, before using this command!")
            raise commands.CommandError("Author is not connected to a voice channel!")

    @leave.before_invoke
    @add.before_invoke
    @play.before_invoke
    @remove.before_invoke
    @reset.before_invoke
    @show.before_invoke
    async def check_author_and_client_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            await ctx.send("I need to be connected to a voice channel, before using this command!")
            raise commands.CommandError("Bot is not connected to a voice channel!")

        if ctx.author.voice is None or ctx.author.voice.channel != ctx.voice_client.channel:
            # Case: Author is not in a voice channel
            await ctx.send(
                "You need to be connected to the same voice channel as me, before using this command!"
            )
            raise commands.CommandError("Author and bot are not in the same voice channel!")

    @pause.before_invoke
    @skip.before_invoke
    async def check_author_client_voice_and_source(self, ctx: commands.Context):
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            await ctx.send("I need to be connected to a voice channel, before using this command!")
            raise commands.CommandError("Bot is not connected to a voice channel!")

        if ctx.author.voice is None or ctx.author.voice.channel != ctx.voice_client.channel:
            # Case: Author is not in a voice channel
            await ctx.send(
                "You need to be connected to the same voice channel as me, before using this command!"
            )
            raise commands.CommandError("Author and bot are not in the same voice channel!")

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_playing():
            # Case: Bot does not play/pause any song
            await ctx.send(
                "You need to play/pause a song, before using this command!"
            )
            raise commands.CommandError("Bot does not play/pause any song!")
