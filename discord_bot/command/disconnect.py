"""Disconnect Background task for the Discord bot."""

import asyncio
import logging

from discord.ext import commands, tasks

from discord_bot.checks import (
    check_author_id_blacklisted,
    check_author_role_blacklisted,
    check_text_channel_blacklisted,
    check_valid_timeout,
    check_voice_channel_blacklisted,
)

logger = logging.getLogger("discord")


class Disconnect(commands.Cog):
    """
    This class represents the background task to handle the timeout of the music bot.

    Attributes:
        bot (commands.Bot):
            The discord client to handle the commands

        timeout (int):
            The time in seconds, where the bot leaves the server and resets its playlist

        kwargs:
            Additional keyword arguments
    """

    def __init__(
        self,
        bot: commands.Bot,
        timeout: int = 600,
        **kwargs,
    ):
        if timeout < 0:
            raise ValueError("timeout needs to be higher than or equal to 0!")

        self.kwargs = kwargs
        self.bot = bot
        self.end_timeout = timeout
        self.curr_timeout = 0

        # Start the background task
        self.disconnect.start()

    @tasks.loop(seconds=60)
    async def disconnect(self):
        """Background Task to handle the timeout."""
        if (
            (self.end_timeout == 0)
            or (len(self.bot.voice_clients) == 0)
            or (self.bot.voice_clients[0].is_playing())
        ):
            # Case: Reset the timeout
            self.curr_timeout = 0
            return

        # Case: Bot is currently pausing or connected to a voice channel
        self.curr_timeout += 60

        if self.curr_timeout >= self.end_timeout:
            # Case: timeout has reached

            # Clear the playlist
            await self.bot.get_cog("Music").playlist.clear()

            # Reset the disconnect time
            self.curr_timeout = 0

            # Disconnect the bot from the voice channel
            await self.bot.voice_clients[0].disconnect(force=False)

    async def _before_timeout(self, ctx: commands.Context, timeout: int):
        """Checks for the timeout command before performing it."""
        manager = self.bot.get_cog("Manager")
        await asyncio.gather(
            check_author_id_blacklisted(ctx, manager.users),
            check_author_role_blacklisted(ctx, manager.roles),
            check_text_channel_blacklisted(ctx, manager.text_channels),
            check_voice_channel_blacklisted(ctx, manager.voice_channels),
            check_valid_timeout(ctx, timeout),
        )

    @commands.command(aliases=["Timeout"])
    async def timeout(self, ctx: commands.Context, timeout: int):
        """
        Set the timeout of the bot.

        Args:
            ctx (commands.Context):
                The discord context

            timeout (int):
                The new timeout in seconds
        """
        async with ctx.typing():
            await self._before_timeout(ctx, timeout)

            if self.end_timeout != timeout:
                # Case: New timeout is not the same as before
                self.end_timeout = timeout
                self.curr_timeout = 0
                return await ctx.send(f"✅ Changed timeout to {self.end_timeout}!")
            # Case: New timeout is the same as before
            return await ctx.send(f"⚠️ Already using timeout of {self.end_timeout}!")
