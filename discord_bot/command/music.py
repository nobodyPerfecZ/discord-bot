import asyncio
import logging
from enum import IntEnum

import discord
import yt_dlp
from discord.ext import commands, tasks

from discord_bot.audio import AudioSource, Playlist
from discord_bot.transformer import YTDLVolumeTransformer
from discord_bot.util.channel import channel_whitelisted, channels_valid
from discord_bot.util.role import highest_priority, roles_valid, roles_whitelisted

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

        whitelisted_roles (list[str]):
            The list of role names that are allowed to use the music bot

        whitelisted_text_channels (list[str]):
            The list of text channel names where the music bot can be used

        disconnect_timeout (int):
            The time in seconds, where the bot leaves the server and resets its playlist

        volume (int):
            The starting volume with a value in between of 0 and 100
    """

    def __init__(
        self,
        bot: commands.Bot,
        whitelisted_roles: list[str],
        whitelisted_text_channels: list[str],
        volume: int = 50,
        disconnect_timeout: int = 600,
    ):
        if not roles_valid(whitelisted_roles):
            raise ValueError(
                "Whitelisted roles need to be in the role_id_to_name_priority_wrapper!"
            )
        if not channels_valid(whitelisted_text_channels):
            raise ValueError(
                "Whitelisted text channels need to be in the channel_id_to_name_priority!"
            )
        if volume < 0 or volume > 100:
            raise ValueError("Volume needs to be in between of 0 and 100!")
        if disconnect_timeout < 0:
            raise ValueError(
                "Disconnect timeout needs to be higher than or equal to 0!"
            )

        self.bot = bot

        self.whitelisted_roles = whitelisted_roles
        self.whitelisted_text_channels = whitelisted_text_channels

        # Initial/Current volume of the music player
        self.start_volume = volume
        self.curr_volume = volume

        # End/Current disconnect timeout of the music player
        self.end_disconnect_timeout = disconnect_timeout
        self.curr_disconnect_timeout = 0

        # Initial state of the music player
        self.playlist = Playlist()
        self.music_state = MusicState.DISCONNECT

        # Start the background tasks
        self.disconnect.start()

    async def _check_author_in_voice_channel(self, ctx: commands.Context):
        """Raises an error if the author is not in a voice channel."""
        if ctx.author.voice is None:
            # Case: Author is not in a voice channel
            await ctx.send("❌ Please join a voice channel, before using this command!")
            raise commands.CommandError("Author is not connected to a voice channel!")

    async def _check_author_role_whitelisted(self, ctx: commands.Context):
        """Raises an error if the author does not have the required role."""
        if not roles_whitelisted(ctx.author.roles, self.whitelisted_roles):
            # Case: Author does not have the required role
            await ctx.send("❌ You do not have the required role to use this command!")
            raise commands.CommandError("Author does not have the required role!")

    async def _check_bot_in_voice_channel(self, ctx: commands.Context):
        """Raises an error if the bot is not in a voice channel."""
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            await ctx.send(
                "❌ Please connect me to a voice channel, before using this command!"
            )
            raise commands.CommandError("Bot is not connected to a voice channel!")

    async def _check_author_bot_in_same_voice(self, ctx: commands.Context):
        """Raises an error if the author and the bot are not in the same voice channel."""
        if ctx.author.voice.channel != ctx.voice_client.channel:
            # Case: Author and bot are not in the same voice channel
            await ctx.send(
                "❌ Please join to the same voice channel as me, before using this command!"
            )
            raise commands.CommandError(
                "Author and Bot are not in the same voice channel!"
            )

    async def _check_bot_is_streaming(self, ctx: commands.Context):
        """Raises an error if the bot is not streaming an audio."""
        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            # Case: Bot is not playing/pausing an audio stream
            await ctx.send("❌ Please play a song, before using this command!")
            raise commands.CommandError("Bot does not play/pause any song!")

    async def _check_text_channel_whitelisted(self, ctx: commands.Context):
        """Raises an error if the command is not executed in the required text channel."""
        if not channel_whitelisted(ctx.channel, self.whitelisted_text_channels):
            # Case: Command is not executed in the required text channel
            await ctx.send("❌ Please use this command in the required text channel!")
            raise commands.CommandError(
                "Command is not executed in the required text channel!"
            )

    @tasks.loop(seconds=60)
    async def disconnect(self):
        """Background Task to handle the disconnect timeout."""
        if (
            self.end_disconnect_timeout == 0
            or self.music_state == MusicState.DISCONNECT
            or self.music_state == MusicState.PLAY
        ):
            # Case: Reset the disconnect timeout
            self.curr_disconnect_timeout = 0
            return

        # Case: Bot is currently pausing or connected to a voice channel
        self.curr_disconnect_timeout += 60

        if self.curr_disconnect_timeout >= self.end_disconnect_timeout:
            # Case: Timeout has reached

            # Set the music state to disconnect
            self.music_state = MusicState.DISCONNECT

            # Clear the playlist
            self.playlist.clear()

            # Set the volume to standard
            self.curr_volume = self.start_volume

            # Reset the disconnect time
            self.curr_disconnect_timeout = 0

            # Disconnect the bot from the voice channel
            await self.bot.voice_clients[0].disconnect(force=False)

    @commands.command(aliases=["Join"])
    async def join(self, ctx: commands.Context):
        """
        Joins to the current voice channel of the author.

        Args:
            ctx (commands.Context):
                The discord context
        """
        author_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            self.music_state = MusicState.CONNECT
            await author_channel.connect()
            return await ctx.send(f"✅ Moved to ``{author_channel}``!")
        else:
            # Case: Bot is in a voice channel
            bot_channel = ctx.voice_client.channel
            if author_channel == bot_channel:
                # Case: Bot is in the same voice channel as the author
                return await ctx.send(f"⚠️ Stayed in ``{bot_channel}``!")

            # Case: Bot is not in the same voice channel as the author
            if ctx.voice_client.is_playing():
                # Case: Bot is currently playing - pause the music
                self.music_state = MusicState.PAUSE
                ctx.voice_client.pause()

            await ctx.voice_client.move_to(author_channel)
            return await ctx.send(
                f"✅ Moved from ``{bot_channel}`` to ``{author_channel}``!"
            )

    @join.before_invoke
    async def before_join(self, ctx: commands.Context):
        """Checks for the leave command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
        )

    @commands.command(aliases=["Leave"])
    async def leave(self, ctx: commands.Context):
        """
        Leaves the voice channel.

        Args:
            ctx (commands.Context):
                The discord context
        """
        channel = ctx.voice_client.channel

        # Set the music state to disconnect
        self.music_state = MusicState.DISCONNECT

        # Clear the playlist
        self.playlist.clear()

        # Set the volume to standard
        self.curr_volume = self.start_volume

        # Reset the disconnect time
        self.curr_disconnect_timeout = 0

        # Disconnect the bot from the voice channel
        await ctx.voice_client.disconnect(force=False)

        return await ctx.send(f"✅ Left ``{channel}``!")

    @leave.before_invoke
    async def before_leave(self, ctx: commands.Context):
        """Checks for the leave command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
        )

    @commands.command(aliases=["Add"])
    async def add(self, ctx: commands.Context, *, url: str):
        """
        Adds an audio source (YouTube URL) to the playlist.

        Args:
            ctx (commands.Context):
                The discord context

            url (str):
                The URL of the YouTube video
        """
        if not url.startswith("https://www.youtube.com"):
            # Case: URL is not a valid YouTube URL
            return await ctx.send(f"❌ Please try a different URL than ``{url}``!")

        # Get the highest priority (lowest value) of the author's roles
        priority = highest_priority(ctx.author.roles)

        # Create the audio source
        audio_source = AudioSource(yt_url=url, priority=priority)

        # Add the audio file to the playlist
        self.playlist.add(audio_source)

        await ctx.send(f"✅ Added ``{audio_source.yt_url}`` to the playlist!")

    @add.before_invoke
    async def before_add(self, ctx: commands.Context):
        """Checks for the add command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
        )

    async def _play_next(self, ctx: commands.Context):
        """Plays the next song in the playlist."""
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
        audio_source = self.playlist.pop()
        try:
            player = await YTDLVolumeTransformer.from_audio_source(
                audio_source=audio_source,
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
        except yt_dlp.utils.YoutubeDLError:
            await ctx.send(
                f"❌ Video ``{audio_source.yt_url}`` is unavailable, trying to play the next from the playlist!"
            )
            return await self._play_next(ctx)

    @commands.command(aliases=["Play"])
    async def play(self, ctx: commands.Context):
        """
        Start playing the next audio song from the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        if ctx.voice_client.is_playing():
            # Case: Bot already plays music
            return await ctx.send(
                f"⚠️ Already playing ``{ctx.voice_client.source.title}``!"
            )

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            self.music_state = MusicState.PLAY
            ctx.voice_client.resume()
            return await ctx.send(f"✅ Resuming ``{ctx.voice_client.source.title}``!")

        if self.playlist.empty():
            # Case: There is no music in the playlist
            return await ctx.send(
                "❌ Please add a song to the playlist, before using this command!"
            )

        # Start playing the next song from the playlist
        audio_source = self.playlist.pop()
        try:
            player = await YTDLVolumeTransformer.from_audio_source(
                audio_source=audio_source,
                volume=self.curr_volume,
                loop=self.bot.loop,
            )
            self.music_state = MusicState.PLAY
            ctx.voice_client.play(
                player,
                after=lambda _: asyncio.run_coroutine_threadsafe(
                    coro=self._play_next(ctx),
                    loop=self.bot.loop,
                ),
            )
            await ctx.send(f"✅ Playing ``{player.title}``!")
        except yt_dlp.utils.YoutubeDLError:
            await ctx.send(
                f"❌ Video ``{audio_source.yt_url}`` is unavailable, trying to play the next from the playlist!"
            )
            return await self.play(ctx)

    @play.before_invoke
    async def before_play(self, ctx: commands.Context):
        """Checks for the play command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
        )

    @commands.command(aliases=["Pause"])
    async def pause(self, ctx: commands.Context):
        """
        Pauses the current played audio source.

        Args:
            ctx (commands.Context):
                The discord context
        """
        if ctx.voice_client.is_playing():
            # Case: Bot plays an audio source
            self.music_state = MusicState.PAUSE
            ctx.voice_client.pause()
            return await ctx.send(f"✅ Paused ``{ctx.voice_client.source.title}``!")

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            return await ctx.send(
                f"⚠️ Already paused ``{ctx.voice_client.source.title}``!"
            )

    @pause.before_invoke
    async def before_pause(self, ctx: commands.Context):
        """Checks for the pause command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
            self._check_bot_is_streaming(ctx),
        )

    @commands.command(aliases=["Skip"])
    async def skip(self, ctx: commands.Context):
        """
        Skips the currently playing audio source in the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        # Calls the after function (_play_next) of the couroutine
        ctx.voice_client.stop()

    @skip.before_invoke
    async def before_skip(self, ctx: commands.Context):
        """Checks for the skip command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
            self._check_bot_is_streaming(ctx),
        )

    @commands.command(aliases=["Reset"])
    async def reset(self, ctx: commands.Context):
        """
        Stops the currently playing audio source and clears the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """

        # Set the music state to connect
        self.music_state = MusicState.CONNECT

        # Clear the playlist
        self.playlist.clear()

        # Set the volume to standard
        self.curr_volume = self.start_volume

        # Reset the disconnect time
        self.curr_disconnect_timeout = 0

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            # Case: Bot plays/pause a song
            ctx.voice_client.stop()

        await ctx.send("✅ Reset playlist!")

    @reset.before_invoke
    async def before_reset(self, ctx: commands.Context):
        """Checks for the reset command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
        )

    @commands.command(aliases=["Show"])
    async def show(self, ctx: commands.Context):
        """
        Displays the audio sources from the playlist.

        Args:
            ctx (commands.Context):
                The discord context
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
                name=f"{i}. Song",
                value=audio_source.yt_url,
                inline=False,
            )

        await ctx.send(embed=embed)

    @show.before_invoke
    async def before_show(self, ctx: commands.Context):
        """Checks for the show command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
        )

    @commands.command(aliases=["Volume"])
    async def volume(self, ctx: commands.Context, *, volume: int):
        """
        Changes the volume of the audio playback.

        Args:
            ctx (commands.Context):
                The discord context

            volume (int):
                The volume of the audio playback
        """
        if volume < 0 or volume > 100:
            return await ctx.send("❌ Please choose a volume between 0 and 100!")

        if self.curr_volume != volume:
            # Case: New volume is not the same as before
            self.curr_volume = volume
            ctx.voice_client.source.volume = self.curr_volume / 100
            return await ctx.send(f"✅ Changed volume to ``{self.curr_volume}``!")
        # Case: New volume is the same as before
        await ctx.send(f"⚠️ Already using volume ``{self.curr_volume}``!")

    @volume.before_invoke
    async def before_volume(self, ctx: commands.Context):
        """Checks for the volume command before performing it."""
        await asyncio.gather(
            self._check_author_role_whitelisted(ctx),
            self._check_text_channel_whitelisted(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice(ctx),
            self._check_bot_is_streaming(ctx),
        )
