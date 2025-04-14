"""Music commands for the Discord bot."""

import asyncio
import logging

import discord
import yt_dlp
from discord.ext import commands

from discord_bot.audio import AudioSource, Playlist
from discord_bot.checks import (
    check_author_voice_channel,
    check_author_whitelisted,
    check_bot_streaming,
    check_bot_voice_channel,
    check_same_voice_channel,
    check_text_channel_whitelisted,
    check_valid_n,
    check_valid_url,
    check_valid_volume,
)
from discord_bot.transformer import YTDLVolumeTransformer
from discord_bot.util import remove_emojis, truncate

logger = logging.getLogger("discord")

# Options for youtube-dl
ydl_options = {
    "format": "bestaudio/best",
    "keepvideo": False,
    "extractaudio": True,
    "noplaylist": True,
    "skip_download": True,
    "quiet": True,
    "default_search": "ytsearch",
}
ydl = yt_dlp.YoutubeDL(ydl_options)


class Music(commands.Cog):
    """
    A suite of commands to control a music bot in a Discord Server.

    Attributes:
        bot (commands.Bot):
            The discord client to handle the commands

        volume (int):
            The starting volume with a value in between of 0 and 100

        kwargs:
            Additional keyword arguments
    """

    def __init__(
        self,
        bot: commands.Bot,
        volume: int = 50,
        **kwargs,
    ):
        if volume < 0 or volume > 100:
            raise ValueError("volume needs to be in between of 0 and 100!")

        self.bot = bot
        self.curr_volume = volume
        self.playlist = Playlist()
        self.should_leave = False
        self.kwargs = kwargs

    async def _before_add(self, ctx: commands.Context, url_or_search: str):
        """Checks for the add command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
            check_valid_url(ctx, url_or_search),
        )

    @commands.command(aliases=["Add"])
    async def add(self, ctx: commands.Context, *url_or_search):
        """
        Adds an audio source (YouTube URL) to the playlist.

        Args:
            ctx (commands.Context):
                The discord context

            url_or_search (str):
                Either the URL of the YouTube Video or a search term
        """
        async with ctx.typing():
            url_or_search = " ".join(url_or_search)
            await self._before_add(ctx, url_or_search)

            # Get the lowest priority (lpriority) of the author's roles
            __ROLES__ = {
                role.id: (priority, role)
                for priority, role in enumerate(reversed(ctx.guild.roles))
            }
            __AUTHOR_ROLES__ = {
                role.id: __ROLES__[role.id] for role in ctx.author.roles
            }
            lpriority = min(
                [__AUTHOR_ROLES__[role_id][0] for role_id in __AUTHOR_ROLES__]
            )

            # Extract the title of the YouTube video
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, lambda: ydl.extract_info(url_or_search)
            )

            if "entries" in data:
                # Case: Searched for a video
                data = data["entries"][0]

            # Remove emojis from the title
            data["title"] = remove_emojis(data["title"])
            data["title"] = truncate(data["title"], 100)

            # Create the audio source
            audio_source = AudioSource(
                title=data["title"],
                user=ctx.author.name,
                stream_url=data["url"],
                yt_url=data["original_url"],
                priority=lpriority,
            )

            # Add the audio file to the playlist
            await self.playlist.add(audio_source)

            await ctx.send(
                f"✅ Added [{audio_source.title}]({audio_source.yt_url}) to the "
                "playlist!"
            )

    async def _before_join(self, ctx: commands.Context):
        """Checks for the leave command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
        )

    @commands.command(aliases=["Join"])
    async def join(self, ctx: commands.Context):
        """
        Joins the voice channel of the author.

        Args:
            ctx (commands.Context):
                The discord context
        """
        async with ctx.typing():
            await self._before_join(ctx)

            author_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                # Case: Bot is not in a voice channel
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
                    ctx.voice_client.pause()

                await ctx.voice_client.move_to(author_channel)
                return await ctx.send(
                    f"✅ Moved from {bot_channel} to {author_channel}!"
                )

    async def _before_leave(self, ctx: commands.Context):
        """Checks for the leave command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
        )

    @commands.command(aliases=["Leave"])
    async def leave(self, ctx: commands.Context):
        """
        Leaves the voice channel.

        Args:
            ctx (commands.Context):
                The discord context
        """
        async with ctx.typing():
            await self._before_leave(ctx)

            # Safe the current voice channel
            voice_channel = ctx.voice_client.channel

            # Clear the playlist
            await self.playlist.clear()

            # Reset the disconnect time
            self.bot.get_cog("Disconnect").curr_timeout = 0

            # Set the flag to leave the voice channel
            self.should_leave = True

            # Disconnect the bot from the voice channel
            await ctx.voice_client.disconnect(force=False)

            return await ctx.send(f"✅ Left {voice_channel}!")

    async def _before_pause(self, ctx: commands.Context):
        """Checks for the pause command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
            check_bot_streaming(ctx),
        )

    @commands.command(aliases=["Pause"])
    async def pause(self, ctx: commands.Context):
        """
        Pauses the currently played audio source.

        Args:
            ctx (commands.Context):
                The discord context
        """
        async with ctx.typing():
            await self._before_pause(ctx)

            if ctx.voice_client.is_playing():
                # Case: Bot plays an audio source
                ctx.voice_client.pause()
                title = ctx.voice_client.source.title
                yt_url = ctx.voice_client.source.yt_url
                return await ctx.send(f"✅ Paused [{title}]({yt_url})!")

            if ctx.voice_client.is_paused():
                # Case: Bot is paused
                title = ctx.voice_client.source.title
                yt_url = ctx.voice_client.source.yt_url
                return await ctx.send(f"⚠️ Already paused [{title}]({yt_url})!")

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
            title = player.title
            yt_url = player.yt_url
            await ctx.send(f"✅ Next playing [{title}]({yt_url})!")
        except yt_dlp.utils.YoutubeDLError:
            title = audio_source.title
            yt_url = audio_source.yt_url
            await ctx.send(
                f"❌ Video [{title}]({yt_url}) is unavailable, trying to play next from"
                " the playlist!"
            )
            return await self._play_next(ctx)

    async def _before_play(self, ctx: commands.Context):
        """Checks for the play command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
        )

    @commands.command(aliases=["Play"])
    async def play(self, ctx: commands.Context):
        """
        Starts playing the audio source from the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        async with ctx.typing():
            await self._before_play(ctx)

            if ctx.voice_client.is_playing():
                # Case: Bot already plays music
                title = ctx.voice_client.source.title
                yt_url = ctx.voice_client.source.yt_url
                return await ctx.send(f"⚠️ Already playing [{title}]({yt_url})!")

            if ctx.voice_client.is_paused():
                # Case: Bot is paused
                ctx.voice_client.resume()
                title = ctx.voice_client.source.title
                yt_url = ctx.voice_client.source.yt_url
                return await ctx.send(f"✅ Resuming [{title}]({yt_url})!")

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
                )
                ctx.voice_client.play(
                    player,
                    after=lambda _: asyncio.run_coroutine_threadsafe(
                        coro=self._play_next(ctx),
                        loop=self.bot.loop,
                    ),
                )
                title = player.title
                yt_url = player.yt_url
                await ctx.send(f"✅ Playing [{title}]({yt_url})!")
            except yt_dlp.utils.YoutubeDLError:
                title = audio_source.title
                yt_url = audio_source.yt_url
                await ctx.send(
                    f"❌ Video [{title}]({yt_url}) is unavailable, trying to play next "
                    "from the playlist!"
                )
                return await self.play(ctx)

    async def _before_reset(self, ctx: commands.Context):
        """Checks for the reset command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
        )

    @commands.command(aliases=["Reset"])
    async def reset(self, ctx: commands.Context):
        """
        Stops the currently played audio source and clears the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        async with ctx.typing():
            await self._before_reset(ctx)

            # Clear the playlist
            await self.playlist.clear()

            # Reset the disconnect time
            self.bot.get_cog("Disconnect").curr_timeout = 0

            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                # Case: Bot plays/pause a song
                ctx.voice_client.stop()

            await ctx.send("✅ Reset playlist!")

    async def _before_show(self, ctx: commands.Context, n: int):
        """Checks for the show command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
            check_valid_n(ctx, n),
        )

    @commands.command(aliases=["Show"])
    async def show(self, ctx: commands.Context, n: int = 5):
        """
        Shows the audio sources from the playlist.

        Args:
            ctx (commands.Context):
                The discord context

            n (int):
                The number of audio sources to show
        """
        async with ctx.typing():
            await self._before_show(ctx, n)

            embed = discord.Embed(title="🎶 Playlist 🎶", color=discord.Color.blue())

            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                # Case: Bot plays/pause a song
                user = ctx.voice_client.source.user
                title = ctx.voice_client.source.title
                yt_url = ctx.voice_client.source.yt_url
                embed.add_field(
                    name=f"👤 {user}",
                    value=f"🎶 [{title}]({yt_url})",
                    inline=False,
                )

            async for i, audio_source in self.playlist.iterate():
                if i >= n:
                    # Case: Number of audio sources to show is reached
                    break
                user = audio_source.user
                title = audio_source.title
                yt_url = audio_source.yt_url
                embed.add_field(
                    name=f"👤 {user}",
                    value=f"{i+1}. [{title}]({yt_url})",
                    inline=False,
                )

            await ctx.send(embed=embed)

    async def _before_skip(self, ctx: commands.Context):
        """Checks for the skip command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_author_voice_channel(ctx),
            check_bot_voice_channel(ctx),
            check_same_voice_channel(ctx),
            check_bot_streaming(ctx),
        )

    @commands.command(aliases=["Skip"])
    async def skip(self, ctx: commands.Context):
        """
        Skips the currently played audio source in the playlist.

        Args:
            ctx (commands.Context):
                The discord context
        """
        async with ctx.typing():
            await self._before_skip(ctx)

            # Calls the after function (_play_next) of the couroutine
            ctx.voice_client.stop()

    async def _before_volume(self, ctx: commands.Context, volume: int):
        """Checks for the volume command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_whitelisted(ctx, manager.wroles),
            check_text_channel_whitelisted(ctx, manager.wtext_channels),
            check_valid_volume(ctx, volume),
        )

    @commands.command(aliases=["Volume"])
    async def volume(self, ctx: commands.Context, volume: int):
        """
        Set the volume of the bot.

        Args:
            ctx (commands.Context):
                The discord context

            volume (int):
                The new volume in between of 0 and 100
        """
        async with ctx.typing():
            await self._before_volume(ctx, volume)

            if self.curr_volume != volume:
                # Case: New volume is not the same as before
                self.curr_volume = volume
                if ctx.voice_client and (
                    ctx.voice_client.is_playing() or ctx.voice_client.is_paused()
                ):
                    # Case: Bot plays/pause a song
                    ctx.voice_client.source.volume = self.curr_volume / 100
                return await ctx.send(f"✅ Changed volume to {self.curr_volume}!")
            # Case: New volume is the same as before
            return await ctx.send(f"⚠️ Already using volume of {self.curr_volume}!")
