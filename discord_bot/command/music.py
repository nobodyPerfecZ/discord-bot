"""Music commands for the Discord bot."""

# pylint: disable=W0212

import asyncio
import logging

import discord
import yt_dlp
from discord.ext import commands, tasks

from discord_bot.audio import AudioSource, Playlist
from discord_bot.transformer import YTDLVolumeTransformer
from discord_bot.util.role import lowest_priority

logger = logging.getLogger("discord")


class Music(commands.Cog):
    """
    This class represents a suite of commands to control a music bot in a Discord Server.

    Attributes:
        bot (commands.Bot):
            The discord client to handle the commands

        volume (int):
            The starting volume with a value in between of 0 and 100

        disconnect_timeout (int):
            The time in seconds, where the bot leaves the server and resets its playlist
    """

    def __init__(
        self,
        bot: commands.Bot,
        volume: int = 50,
        disconnect_timeout: int = 600,
        **kwargs,
    ):
        if volume < 0 or volume > 100:
            raise ValueError("volume needs to be in between of 0 and 100!")
        if disconnect_timeout < 0:
            raise ValueError(
                "disconnect_timeout needs to be higher than or equal to 0!"
            )

        self.bot = bot

        # Initial/Current volume of the music player
        self.start_volume = volume
        self.curr_volume = volume

        # End/Current disconnect timeout of the music player
        self.end_disconnect_timeout = disconnect_timeout
        self.curr_disconnect_timeout = 0

        # Initial state of the music player
        self.playlist = Playlist()

        # List of keys for the set command
        self.keys = ["volume", "disconnect_timeout"]

        # Flag to leave the voice channel
        self.should_leave = False

        # Start the background tasks
        self.disconnect.start()

    async def _check_text_in_guild(self, ctx: commands.Context):
        """Raises an error if the text is written in a private text channel."""
        if ctx.guild is None:
            # Case: Message is written in a private text channel
            await ctx.send("❌ Please use this command in a public text channel!")
            raise commands.CommandError("Text is written in a private text channel!")

    async def _check_author_in_voice_channel(self, ctx: commands.Context):
        """Raises an error if the author is not in a voice channel."""
        if ctx.author.voice is None:
            # Case: Author is not in a voice channel
            await ctx.send("❌ Please join a voice channel, before using this command!")
            raise commands.CommandError("Author is not connected to a voice channel!")

    async def _check_bot_in_voice_channel(self, ctx: commands.Context):
        """Raises an error if the bot is not in a voice channel."""
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
            await ctx.send(
                "❌ Please connect me to a voice channel, before using this command!"
            )
            raise commands.CommandError("Bot is not connected to a voice channel!")

    async def _check_author_bot_in_same_voice_channel(self, ctx: commands.Context):
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

    async def _check_valid_url(self, ctx: commands.Context, url: str):
        """Raises an error if the URL is not a valid YouTube URL."""
        if not url.startswith("https://www.youtube.com"):
            # Case: URL is not a valid YouTube URL
            await ctx.send(f"❌ Please try a different URL than ``{url}``!")
            raise commands.CommandError("URL is not a valid YouTube URL!")

    async def _check_valid_volume(self, ctx: commands.Context, volume: int):
        """Raises an error if the volume is not in between of 0 and 100."""
        if volume < 0 or volume > 100:
            # Case: Volume is not in between of 0 and 100
            await ctx.send("❌ Please choose a volume between 0 and 100!")
            raise commands.CommandError("Volume is not in between of 0 and 100!")

    async def _check_valid_disconnect_timeout(
        self, ctx: commands.Context, disconnect_timeout: int
    ):
        """Raises an error if the disconnect timeout is not higher than or equal to 0."""
        if disconnect_timeout < 0:
            # Case: Disconnect timeout is not higher than 0
            await ctx.send(
                "❌ Please choose a disconnect timeout higher than or equal to 0!"
            )
            raise commands.CommandError(
                "Disconnect timeout is not higher than or equal to 0!"
            )

    async def _check_valid_key(self, ctx: commands.Context, key: str):
        """Raises an error if the key is not valid."""
        if key not in self.keys:
            # Case: Key is not valid
            await ctx.send("❌ Please choose a valid key!")
            raise commands.CommandError("Key is not valid!")

    async def _check_valid_value(
        self, ctx: commands.Context, key: str, values: tuple[str, ...]
    ):
        """Raises an error if the value for key is not valid."""
        if key == "volume":
            try:
                volume = int(values[0])
            except Exception as e:
                await ctx.send(f"❌ Please choose a valid value for {key}!")
                raise commands.CommandError(f"Value for key={key} is not valid!") from e
            await self._check_valid_volume(ctx, volume)

        elif key == "disconnect_timeout":
            try:
                disconnect_timeout = int(values[0])
            except Exception as e:
                await ctx.send(f"❌ Please choose a valid value for {key}!")
                raise commands.CommandError(f"Value for key={key} is not valid!") from e
            await self._check_valid_disconnect_timeout(ctx, disconnect_timeout)

    @tasks.loop(seconds=60)
    async def disconnect(self):
        """Background Task to handle the disconnect timeout."""
        if (
            self.end_disconnect_timeout == 0
            or len(self.bot.voice_clients) == 0
            or self.bot.voice_clients[0].is_playing()
        ):
            # Case: Reset the disconnect timeout
            self.curr_disconnect_timeout = 0
            return

        # Case: Bot is currently pausing or connected to a voice channel
        self.curr_disconnect_timeout += 60

        if self.curr_disconnect_timeout >= self.end_disconnect_timeout:
            # Case: Timeout has reached

            # Clear the playlist
            await self.playlist.clear()

            # Set the volume to standard
            self.curr_volume = self.start_volume

            # Reset the disconnect time
            self.curr_disconnect_timeout = 0

            # Disconnect the bot from the voice channel
            await self.bot.voice_clients[0].disconnect(force=False)

    async def _before_join(self, ctx: commands.Context):
        """Checks for the leave command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
        )

    @commands.command(aliases=["Join"])
    async def join(self, ctx: commands.Context):
        """
        Joins the voice channel of the author.

        Args:
            ctx (commands.Context):
                The discord context
        """
        await self._before_join(ctx=ctx)

        author_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            # Case: Bot is not in a voice channel
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
                ctx.voice_client.pause()

            await ctx.voice_client.move_to(author_channel)
            return await ctx.send(
                f"✅ Moved from ``{bot_channel}`` to ``{author_channel}``!"
            )

    async def _before_leave(self, ctx: commands.Context):
        """Checks for the leave command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
        )

    @commands.command(aliases=["Leave"])
    async def leave(self, ctx: commands.Context):
        """
        Leaves the voice channel.

        Args:
            ctx (commands.Context):
                The discord context
        """
        await self._before_leave(ctx=ctx)

        # Safe the current voice channel
        voice_channel = ctx.voice_client.channel

        # Clear the playlist
        await self.playlist.clear()

        # Set the volume to standard
        self.curr_volume = self.start_volume

        # Reset the disconnect time
        self.curr_disconnect_timeout = 0

        # Set the flag to leave the voice channel
        self.should_leave = True

        # Disconnect the bot from the voice channel
        await ctx.voice_client.disconnect(force=False)

        return await ctx.send(f"✅ Left ``{voice_channel}``!")

    async def _before_add(self, ctx: commands.Context, *, url: str):
        """Checks for the add command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
            self._check_valid_url(ctx, url),
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
        await self._before_add(ctx=ctx, url=url)

        # Get the lowest priority of the author's roles
        priority = lowest_priority(ctx.author.roles)

        # Create the audio source
        audio_source = AudioSource(yt_url=url, priority=priority)

        # Add the audio file to the playlist
        await self.playlist.add(audio_source)

        await ctx.send(f"✅ Added ``{audio_source.yt_url}`` to the playlist!")

    async def _play_next(self, ctx: commands.Context):
        """Plays the next song in the playlist."""
        if self.should_leave:
            # Case: Bot should leave the voice channel
            self.should_leave = False
            return

        if await self.playlist.empty():
            return await ctx.send("⚠️ The playlist no longer contains any songs!")

        # Play the next song
        audio_source = await self.playlist.pop()
        try:
            player = await YTDLVolumeTransformer.from_audio_source(
                audio_source=audio_source,
                volume=self.curr_volume,
            )
            ctx.voice_client.play(
                player,
                after=lambda _: asyncio.run_coroutine_threadsafe(
                    coro=self._play_next(ctx),
                    loop=self.bot.loop,
                ),
            )
            await ctx.send(f"✅ Next playing {player.title}!")
        except yt_dlp.utils.YoutubeDLError:
            await ctx.send(
                f"❌ Video ``{audio_source.yt_url}`` is unavailable, trying to play the next from the playlist!"
            )
            return await self._play_next(ctx)

    async def _before_play(self, ctx: commands.Context):
        """Checks for the play command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
        )

    @commands.command(aliases=["Play"])
    async def play(self, ctx: commands.Context):
        """
        Starts playing the audio source from the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        await self._before_play(ctx=ctx)

        if ctx.voice_client.is_playing():
            # Case: Bot already plays music
            return await ctx.send(
                f"⚠️ Already playing ``{ctx.voice_client.source.title}``!"
            )

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            ctx.voice_client.resume()
            return await ctx.send(f"✅ Resuming ``{ctx.voice_client.source.title}``!")

        if await self.playlist.empty():
            # Case: There is no music in the playlist
            return await ctx.send(
                "❌ Please add a song to the playlist, before using this command!"
            )

        # Start playing the next song from the playlist
        audio_source = await self.playlist.pop()
        try:
            player = await YTDLVolumeTransformer.from_audio_source(
                audio_source=audio_source,
                volume=self.curr_volume,
                loop=self.bot.loop,
            )
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

    async def _before_pause(self, ctx: commands.Context):
        """Checks for the pause command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
            self._check_bot_is_streaming(ctx),
        )

    @commands.command(aliases=["Pause"])
    async def pause(self, ctx: commands.Context):
        """
        Pauses the currently played audio source.

        Args:
            ctx (commands.Context):
                The discord context
        """
        await self._before_pause(ctx=ctx)

        if ctx.voice_client.is_playing():
            # Case: Bot plays an audio source
            ctx.voice_client.pause()
            return await ctx.send(f"✅ Paused ``{ctx.voice_client.source.title}``!")

        if ctx.voice_client.is_paused():
            # Case: Bot is paused
            return await ctx.send(
                f"⚠️ Already paused ``{ctx.voice_client.source.title}``!"
            )

    async def _before_skip(self, ctx: commands.Context):
        """Checks for the skip command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
            self._check_bot_is_streaming(ctx),
        )

    @commands.command(aliases=["Skip"])
    async def skip(self, ctx: commands.Context):
        """
        Skips the currently played audio source in the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        await self._before_skip(ctx=ctx)

        # Calls the after function (_play_next) of the couroutine
        ctx.voice_client.stop()

    async def _before_reset(self, ctx: commands.Context):
        """Checks for the reset command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
        )

    @commands.command(aliases=["Reset"])
    async def reset(self, ctx: commands.Context):
        """
        Stops the currently played audio source and clears the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        await self._before_reset(ctx=ctx)

        # Clear the playlist
        await self.playlist.clear()

        # Set the volume to standard
        self.curr_volume = self.start_volume

        # Reset the disconnect time
        self.curr_disconnect_timeout = 0

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            # Case: Bot plays/pause a song
            ctx.voice_client.stop()

        await ctx.send("✅ Reset playlist!")

    async def _before_show(self, ctx: commands.Context):
        """Checks for the show command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
        )

    @commands.command(aliases=["Show"])
    async def show(self, ctx: commands.Context):
        """
        Shows the audio sources from the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        await self._before_show(ctx=ctx)

        embed = discord.Embed(title="🎶 Playlist 🎶", color=discord.Color.blue())

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            # Case: Bot plays/pause a song
            embed.add_field(
                name=f"🎶 {ctx.voice_client.source.title}",
                value=ctx.voice_client.source.yt_url,
            )

        async for i, audio_source in self.playlist.iterate():
            embed.add_field(
                name=f"{i+1}. Song",
                value=audio_source.yt_url,
                inline=False,
            )

        await ctx.send(embed=embed)

    async def _before_set(
        self, ctx: commands.Context, key: str, values: tuple[str, ...]
    ):
        """Checks for the set command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            manager._check_author_role_is_whitelisted(ctx),
            manager._check_text_channel_is_whitelisted(ctx),
            manager._check_voice_channel_is_whitelisted(ctx),
            self._check_text_in_guild(ctx),
            self._check_author_in_voice_channel(ctx),
            self._check_bot_in_voice_channel(ctx),
            self._check_author_bot_in_same_voice_channel(ctx),
            self._check_valid_key(ctx, key),
            self._check_valid_value(ctx, key, values),
        )

    @commands.command(aliases=["Set"])
    async def set(self, ctx: commands.Context, key: str, *values):
        """
        Changes the value of the key.

        Args:
            ctx (commands.Context):
                The discord context

            key (str):
                The key to change

            values (tuple[str, ...]):
                The new values
        """
        await self._before_set(ctx=ctx, key=key, values=values)

        if key == "volume":
            volume = int(values[0])
            if self.curr_volume != volume:
                # Case: New volume is not the same as before
                self.curr_volume = volume
                if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    # Case: Bot plays/pause a song
                    ctx.voice_client.source.volume = self.curr_volume / 100
                return await ctx.send(f"✅ Changed volume to ``{self.curr_volume}``!")
            # Case: New volume is the same as before
            return await ctx.send(f"⚠️ Already using volume ``{self.curr_volume}``!")

        elif key == "disconnect_timeout":
            disconnect_timeout = int(values[0])
            if self.end_disconnect_timeout != disconnect_timeout:
                # Case: New disconnect timeout is not the same as before
                self.end_disconnect_timeout = disconnect_timeout
                self.curr_disconnect_timeout = 0
                return await ctx.send(
                    f"✅ Changed disconnect timeout to ``{self.end_disconnect_timeout}``!"
                )
            # Case: New disconnect timeout is the same as before
            return await ctx.send(
                f"⚠️ Already using disconnect timeout ``{self.end_disconnect_timeout}``!"
            )

    @staticmethod
    def help_information() -> discord.Embed | None:
        """Returns the help information of the music commands."""
        embed = discord.Embed(title="Music:", color=discord.Color.blue())
        embed.add_field(
            name="!join", value="Joins the voice channel of the author.", inline=False
        )
        embed.add_field(name="!leave", value="Leaves the voice channel.", inline=False)
        embed.add_field(
            name="!add <url>",
            value="Adds an audio source (YouTube URL) to the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!play",
            value="Starts playing the audio source from the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!pause",
            value="Pauses the currently played audio source.",
            inline=False,
        )
        embed.add_field(
            name="!skip",
            value="Skips the currently played audio source in the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!reset",
            value="Stops the currently played audio source and clears the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!show",
            value="Shows the audio sources from the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!set <key> <value1> ...",
            value="Changes the configuration of the music player.",
            inline=False,
        )
        return embed
