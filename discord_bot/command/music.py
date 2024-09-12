import asyncio
import logging
from enum import IntEnum

import discord
import yt_dlp
from discord.ext import commands, tasks

from discord_bot.audio import AudioSource, Playlist
from discord_bot.member.role import get_highest_priority
from discord_bot.transformer import YTDLVolumeTransformer

logger = logging.getLogger("discord")


class MusicState(IntEnum):
    """
    This class represents different states of an audio player.

    Attributes:
        DISCONNECT (int):
            The audio player is disconnected from the voice channel

        CONNECT (int):
            The audio player is connected to the voice channel (and does not play/pause any audio stream)

        PLAY (int):
            The audioplayer is playing an audio stream

        PAUSE (int):
            The audio player is pausing an audio stream
    """

    DISCONNECT = 1
    CONNECT = 2
    PLAY = 3
    PAUSE = 4


class Music(commands.Cog):
    """
    This class represents a suite of commands to control a music bot in a Discord Server.

    Attributes:
        bot (commands.Bot):
            The discord client to handle the commands

        disconnect_timeout (int):
            The time in seconds, where the bot leaves the server and resets its playlist

        volume (int):
            The starting volume with a value in between of 0 and 100
    """

    def __init__(
        self,
        bot: commands.Bot,
        disconnect_timeout: int = 600,
        volume: int = 50,
    ):
        if volume < 0 or volume > 100:
            raise ValueError("Volume needs to be in between of 0 and 100!")
        if disconnect_timeout < 0:
            raise ValueError(
                "Disconnect timeout needs to be higher than or equal to 0!"
            )

        self.bot = bot
        self.playlist = Playlist()
        self.music_state = MusicState.DISCONNECT
        self.disconnect_timeout = disconnect_timeout
        self.disconnect_time = 0
        self.start_volume = volume
        self.curr_volume = volume
        self.disconnect.start()

    @staticmethod
    async def _check_author_voice(ctx: commands.Context):
        """Raises an error if the author is not in a voice channel."""
        if ctx.author.voice is None:
            # Case: Author is not in a voice channel
            await ctx.send("❌ Please join a voice channel, before using this command!")
            raise commands.CommandError("Author is not connected to a voice channel!")

    @staticmethod
    async def _check_bot_voice(ctx: commands.Context):
        """Raises an error if the bot is not in a voice channel."""
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            await ctx.send(
                "❌ Please connect me to a voice channel, before using this command!"
            )
            raise commands.CommandError("Bot is not connected to a voice channel!")

    @staticmethod
    async def _check_author_and_bot_voice(ctx: commands.Context):
        """Raises an error if the author and the bot are not in the same voice channel."""
        if ctx.author.voice.channel != ctx.voice_client.channel:
            # Case: Author is not in a voice channel
            await ctx.send(
                "❌ Please join to the same voice channel as me, before using this command!"
            )
            raise commands.CommandError(
                "Author and Bot are not in the same voice channel!"
            )

    @staticmethod
    async def _check_bot_streaming(ctx: commands.Context):
        """Raises an error if the bot is not streaming (playing/pausing) and audio stream."""
        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            # Case: Bot does not play/pause any song
            await ctx.send("❌ Please play a song, before using this command!")
            raise commands.CommandError("Bot does not play/pause any song!")

    @tasks.loop(seconds=30)
    async def disconnect(self):
        """
        Background Tasks to handle the disconnect timeout.

        After the bot reached disconnect_timeout it will leave the server and resets its playlist and volume.
        """
        if (
            self.disconnect_timeout == 0
            or self.music_state == MusicState.DISCONNECT
            or self.music_state == MusicState.PLAY
        ):
            # Case: Disable the background task
            self.disconnect_time = 0
            return

        # Case: Bot is currently pausing or connected to a voice channel
        self.disconnect_time += 30

        if self.disconnect_time >= self.disconnect_timeout:
            # Case: Timeout has reached
            # Disconnect the bot from the voice channel
            self.music_state = MusicState.DISCONNECT
            await self.bot.voice_clients[0].disconnect(force=False)

            # Clear the playlist
            self.playlist.clear()

            # Set the volume to standard
            self.curr_volume = self.start_volume

            # Reset the disconnect time
            self.disconnect_time = 0

    async def _play_next(self, ctx: commands.Context):
        """
        Plays the next song in the playlist.

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        if (
            self.music_state == MusicState.DISCONNECT
            or self.music_state == MusicState.CONNECT
        ):
            # Case: Bot never played/paused a song before
            return

        if self.playlist.empty():
            self.music_state = MusicState.CONNECT
            return await ctx.send("⚠️ The playlist no longer contains any songs!")

        # Get the voice client
        voice_client = ctx.voice_client

        # Play the next song
        player = YTDLVolumeTransformer.from_audio_source(
            audio_source=self.playlist.pop(),
            volume=self.curr_volume,
        )
        voice_client.play(
            player,
            after=lambda _: asyncio.run_coroutine_threadsafe(
                coro=self._play_next(ctx),
                loop=self.bot.loop,
            ),
        )
        self.music_state = MusicState.PLAY
        await ctx.send(f"✅ Next playing {player.title}!")

    @commands.command(aliases=["Join"])
    async def join(self, ctx: commands.Context):
        """
        Joins to the current voice channel of the author.

        This command ensures that the bot is joining the current voice channel of the author.

        Unusual cases being treated:
            - If author is not in a voice channel, then a warning message will be sent
            - If bot is in another voice channel, then it will move to voice channel and stops playing music
            - If bot is already in the current voice channel, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        author_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            self.music_state = MusicState.CONNECT
            await author_channel.connect()
            return await ctx.send(f"✅ Moved to {author_channel}!")
        else:
            # Case: Bot is in a voice channel
            bot_channel = ctx.voice_client.channel
            if author_channel == bot_channel:
                # Case: Bot is in the same voice channel as the author
                return await ctx.send(f"⚠️ Stayed in {bot_channel}!")

            # Case: Bot is not in the same voice channel as the author
            if ctx.voice_client.is_playing():
                # Case: Bot is currently playing - pause the music
                self.music_state = MusicState.PAUSE
                ctx.voice_client.pause()

            await ctx.voice_client.move_to(author_channel)
            return await ctx.send(f"✅ Moved from {bot_channel} to {author_channel}!")

    @join.before_invoke
    async def before_join(self, ctx: commands.Context):
        """
        Checks for the join command before performing it.

         Unusual cases being treated:
            - If author is not in a voice channel, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)

    @commands.command(aliases=["Leave"])
    async def leave(self, ctx: commands.Context):
        """
        Leaves the voice channel.

        This command ensures that the bot is leaving the voice channel.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        channel = ctx.voice_client.channel
        self.music_state = MusicState.DISCONNECT
        await ctx.voice_client.disconnect(force=False)
        return await ctx.send(f"✅ Left {channel}!")

    @leave.before_invoke
    async def before_leave(self, ctx: commands.Context):
        """
        Checks for the leave command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)

    @commands.command(aliases=["Add"])
    async def add(self, ctx: commands.Context, url: str):
        """
        Adds a song (YouTube URL) to the playlist.

        This command ensures that the given YouTube URL is added to the playlist.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If given url is not supported, then it will not be added to the playlist and a warning message will
              be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)

            url (str):
                The URL of the YouTube video to be added to the playlist
        """
        # Get the highest priority (lowest value) of the author's roles
        priority = get_highest_priority(ctx.author.roles)

        # Get the audio source from the given url
        try:
            audio_source = await AudioSource.from_url(
                yt_url=url,
                priority=priority,
                loop=self.bot.loop,
            )
        except yt_dlp.utils.YoutubeDLError:
            return await ctx.send(f"❌ Please try a different URL than {url}!")

        # Add the audio file to the playlist
        self.playlist.add(audio_source)
        await ctx.send(f"✅ Added {audio_source.title} to the playlist!")

    @add.before_invoke
    async def before_add(self, ctx: commands.Context):
        """
        Checks for the add command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)

    @commands.command(aliases=["Play"])
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

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        if ctx.voice_client.is_playing():
            # Case: Bot already plays music
            return await ctx.send(f"⚠️ Already playing {ctx.voice_client.source.title}!")

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            self.music_state = MusicState.PLAY
            ctx.voice_client.resume()
            return await ctx.send(f"✅ Resuming {ctx.voice_client.source.title}!")

        if self.playlist.empty():
            # Case: There is no music in the playlist
            return await ctx.send(
                "❌ Please add a song to the playlist, before using this command!"
            )

        # Start playing the next song from the playlist
        player = YTDLVolumeTransformer.from_audio_source(
            audio_source=self.playlist.pop(),
            volume=self.curr_volume,
        )
        self.music_state = MusicState.PLAY
        ctx.voice_client.play(
            player,
            after=lambda _: asyncio.run_coroutine_threadsafe(
                coro=self._play_next(ctx),
                loop=self.bot.loop,
            ),
        )
        await ctx.send(f"✅ Playing {player.title}!")

    @play.before_invoke
    async def before_play(self, ctx: commands.Context):
        """
        Checks for the play command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)

    @commands.command(aliases=["Pause"])
    async def pause(self, ctx: commands.Context):
        """
        Pauses the current played song.

        This command ensures that the bot pauses the playback of the current played song.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot does not play/pause any song, then a warning message will be sent
            - If bot already pauses a song, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        if ctx.voice_client.is_playing():
            # Case: Bot does not play a song
            self.music_state = MusicState.PAUSE
            ctx.voice_client.pause()
            return await ctx.send(f"✅ Paused {ctx.voice_client.source.title}!")

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            return await ctx.send(f"⚠️ Already paused {ctx.voice_client.source.title}!")

    @pause.before_invoke
    async def before_pause(self, ctx: commands.Context):
        """
        Checks for the pause command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot does not play/pause any song, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)
        await Music._check_bot_streaming(ctx)

    @commands.command(aliases=["Skip"])
    async def skip(self, ctx: commands.Context):
        """
        Skips the current played song.

        This command ensures that the bot skips the current played song and continues to play the next song from the
        playlist.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot does not play/pause any song, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        # Stop playing the current music (removes the audio stream and skip to the next one)
        ctx.voice_client.stop()

    @skip.before_invoke
    async def before_skip(self, ctx: commands.Context):
        """
        Checks for the skip command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot does not play/pause any song, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)
        await Music._check_bot_streaming(ctx)

    @commands.command(aliases=["Remove"])
    async def remove(self, ctx: commands.Context, n: int):
        """
        Removes the first n songs from the playlist (not included currently playing).

        This command ensures that the next n songs will be removed from the playlist.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If playlist does not have at least n songs, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)

            n (int):
                The number of next songs to be removed
        """
        if self.playlist.empty():
            return await ctx.send(
                "❌ Please add a song to the playlist, before using this command!"
            )

        if n <= 0 or n > len(self.playlist):
            return await ctx.send(
                f"❌ Please choose a number of songs to delete between 1 and {len(self.playlist)}!"
            )

        await self.bot.loop.run_in_executor(None, lambda: self.playlist.remove(n=n))
        return await ctx.send(f"✅ Removed {n} songs from the playlist!")

    @remove.before_invoke
    async def before_remove(self, ctx: commands.Context):
        """
        Checks for the remove command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)

    @commands.command(aliases=["Reset"])
    async def reset(self, ctx: commands.Context):
        """
        Stops the current song and clears the playlist.

        This command ensures that the bot stops the current audio playback and the playlist will be reset.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
        """
        # Clear the playlist
        self.music_state = MusicState.CONNECT
        self.playlist.clear()

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            # Case: Bot plays/pause a song
            ctx.voice_client.stop()

        await ctx.send("✅ Reset playlist!")

    @reset.before_invoke
    async def before_reset(self, ctx: commands.Context):
        """
        Checks for the reset command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)

    @commands.command(aliases=["Show"])
    async def show(self, ctx: commands.Context):
        """
        Displays the songs in the playlist (and currently played song).

        This command ensures that the bot will show the playlist including the currently played song.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
        """
        embed = discord.Embed(title="🎶 Playlist 🎶", color=discord.Color.blue())

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            # Case: Bot plays/pause a song
            embed.add_field(
                name=f"🎶 {ctx.voice_client.source.title}",
                value=ctx.voice_client.source.yt_url,
            )

        for i, audio_source in enumerate(self.playlist, 1):
            embed.add_field(
                name=f"{i}. {audio_source.title}",
                value=audio_source.yt_url,
                inline=False,
            )

        await ctx.send(embed=embed)

    @show.before_invoke
    async def before_show(self, ctx: commands.Context):
        """
        Checks for the show command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)

    @commands.command(aliases=["Volume"])
    async def volume(self, ctx: commands.Context, volume: int):
        """
        Changes the volume of the audio playback.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If volume is not in (0, 100) then a warning message will be sent.

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)

            volume (int):
                The volume of the audio playback
        """
        if volume < 0 or volume > 100:
            return await ctx.send("❌ Please choose a volume between 0 and 100!")

        if self.curr_volume != volume:
            # Case: New volume is not the same as before
            self.curr_volume = volume
            ctx.voice_client.source.volume = self.curr_volume / 100
            return await ctx.send(f"✅ Changed volume to {self.curr_volume}!")
        # Case: New volume is the same as before
        await ctx.send(f"⚠️ Already used volume {self.curr_volume}!")

    @volume.before_invoke
    async def before_volume(self, ctx: commands.Context):
        """
        Checks for the volume command before performing it.

        Unusual cases being treated:
            - If bot is not in a voice channel, then a warning message will be sent
            - If author is not in the same voice channel as the bot, then a warning message will be sent
            - If bot does not play/pause any song, then a warning message will be sent

        Args:
            ctx (commands.Context):
                The discord context (will be added automatically)
        """
        await Music._check_author_voice(ctx)
        await Music._check_bot_voice(ctx)
        await Music._check_author_and_bot_voice(ctx)
        await Music._check_bot_streaming(ctx)
