"""Manager commands (whitelists) for the Discord bot."""

import asyncio
import logging

import discord
from discord.ext import commands

from discord_bot.checks import (
    check_author_whitelisted,
    check_less_equal_author,
    check_text_channel_whitelisted,
    check_valid_command,
    check_valid_roles,
    check_valid_text_channels,
    check_valid_voice_channels,
    check_voice_channel_whitelisted,
)
from discord_bot.util.role import valid_role_id
from discord_bot.util.text_channel import valid_text_channel_id
from discord_bot.util.voice_channel import valid_voice_channel_id

logger = logging.getLogger("discord")


class Manager(commands.Cog):
    """
    This class represents a suite of commands to add/change/set all parameters of the music bot.

    Attributes:
        whitelisted_roles (dict[str, list[int]]):
            The list of role ids that are allowed to use the music bot

        whitelisted_text_channels (dict[str, list[int]]):
            The list of text channel ids where the music bot can be used

        whitelisted_voice_channels (dict[str, list[int]]):
            The list of voice channel ids where the music bot can be used

        kwargs (dict[str, Any]):
            Additional keyword arguments
    """

    def __init__(
        self,
        bot: commands.Bot,
        whitelisted_roles: dict[str, list[int]],
        whitelisted_text_channels: dict[str, list[int]],
        whitelisted_voice_channels: dict[str, list[int]],
        **kwargs,
    ):

        if all(
            not valid_role_id(whitelisted_role)
            for whitelisted_role in whitelisted_roles.values()
        ):
            raise ValueError("whitelisted_roles needs to be in __ROLES__!")
        if all(
            not valid_text_channel_id(whitelisted_text_channel)
            for whitelisted_text_channel in whitelisted_text_channels.values()
        ):
            raise ValueError(
                "whitelisted_text_channels need to be in __TEXT_CHANNELS__!"
            )
        if all(
            not valid_voice_channel_id(whitelisted_voice_channel)
            for whitelisted_voice_channel in whitelisted_voice_channels.values()
        ):
            raise ValueError(
                "whitelisted_voice_channels need to be in __VOICE_CHANNELS__!"
            )
        if (
            whitelisted_roles.keys() != whitelisted_text_channels.keys()
            or whitelisted_roles.keys() != whitelisted_voice_channels.keys()
            or whitelisted_text_channels.keys() != whitelisted_voice_channels.keys()
        ):
            raise ValueError(
                "The keys of the whitelisted_roles, whitelisted_text_channels, whitelisted_voice_channels need to be the same!"
            )

        self.bot = bot
        self.whitelisted_roles = whitelisted_roles
        self.whitelisted_text_channels = whitelisted_text_channels
        self.whitelisted_voice_channels = whitelisted_voice_channels
        self._roles_lock = asyncio.Lock()
        self._text_channels_lock = asyncio.Lock()
        self._voice_channels_lock = asyncio.Lock()
        self.kwargs = kwargs

    async def _before_whitelisted_roles(
        self, ctx: commands.Context, command: str, roles: list[int]
    ):
        """Checks for the whitelisted_roles command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.whitelisted_roles),
            check_text_channel_whitelisted(ctx, self.whitelisted_text_channels),
            check_voice_channel_whitelisted(ctx, self.whitelisted_voice_channels),
            check_valid_command(
                ctx,
                command,
                self.whitelisted_roles,
                self.whitelisted_text_channels,
                self.whitelisted_voice_channels,
            ),
            check_valid_roles(ctx, roles),
            check_less_equal_author(ctx, roles),
        )

    @commands.command(aliases=["Whitelisted_role"])
    async def whitelisted_role(self, ctx: commands.Context, command: str, *roles):
        """
        Sets the whitelisted roles for a specific command.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The command to set the new whitelisted roles

            *roles (list[int]):
                The list of role ids to be whitelisted
        """
        roles = list(map(int, roles))
        await self._before_whitelisted_roles(ctx, command, roles)

        async with self._roles_lock:
            if self.whitelisted_roles[command] != roles:
                # Case: Whitelisted roles are changed
                self.whitelisted_roles[command] = roles
                return await ctx.send("✅ Changed whitelisted roles!")
            # Case: Already using whitelisted roles
            return await ctx.send("⚠️ Already using whitelisted roles!")

    async def _before_whitelisted_text_channels(
        self, ctx: commands.Context, command: str, text_channels: list[int]
    ):
        """Checks for the whitelisted_text_channels command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.whitelisted_roles),
            check_text_channel_whitelisted(ctx, self.whitelisted_text_channels),
            check_voice_channel_whitelisted(ctx, self.whitelisted_voice_channels),
            check_valid_command(
                ctx,
                command,
                self.whitelisted_roles,
                self.whitelisted_text_channels,
                self.whitelisted_voice_channels,
            ),
            check_valid_text_channels(ctx, text_channels),
        )

    @commands.command(aliases=["Whitelisted_text_channel"])
    async def whitelisted_text_channel(
        self, ctx: commands.Context, command: str, *text_channels
    ):
        """
        Sets the whitelisted text channels for a specific command.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The command to set the new whitelisted text channels

            *text_channels (list[int]):
                The list of text channel ids to be whitelisted
        """
        text_channels = list(map(int, text_channels))
        await self._before_whitelisted_text_channels(ctx, command, text_channels)

        async with self._text_channels_lock:
            if self.whitelisted_text_channels[command] != text_channels:
                # Case: Whitelisted text channels are changed
                self.whitelisted_text_channels[command] = text_channels
                return await ctx.send("✅ Changed whitelisted text channels!")
            # Case: Already using whitelisted text channels
            return await ctx.send("⚠️ Already using whitelisted text channels!")

    async def _before_whitelisted_voice_channels(
        self, ctx: commands.Context, command: str, voice_channels: list[int]
    ):
        """Checks for the whitelisted_voice_channels command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.whitelisted_roles),
            check_text_channel_whitelisted(ctx, self.whitelisted_text_channels),
            check_voice_channel_whitelisted(ctx, self.whitelisted_voice_channels),
            check_valid_command(
                ctx,
                command,
                self.whitelisted_roles,
                self.whitelisted_text_channels,
                self.whitelisted_voice_channels,
            ),
            check_valid_voice_channels(ctx, voice_channels),
        )

    @commands.command(aliases=["Whitelisted_voice_channel"])
    async def whitelisted_voice_channel(
        self, ctx: commands.Context, command: str, *voice_channels
    ):
        """
        Sets the whitelisted voice channels for a specific command.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The command to set the new whitelisted voice channels

            *voice_channels (list[int]):
                The list of voice channel ids to be whitelisted
        """
        voice_channels = list(map(int, voice_channels))
        await self._before_whitelisted_voice_channels(ctx, command, voice_channels)

        async with self._voice_channels_lock:
            if self.whitelisted_voice_channels[command] != voice_channels:
                # Case: Whitelisted voice channels are changed
                self.whitelisted_voice_channels[command] = voice_channels
                return await ctx.send("✅ Changed whitelisted voice channels!")
            # Case: Already using whitelisted voice channels
            return await ctx.send("⚠️ Already using whitelisted voice channels!")

    @staticmethod
    def help_information() -> discord.Embed | None:
        """Returns the help information of the manager commands."""
        return None
