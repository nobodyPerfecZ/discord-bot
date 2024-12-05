"""Manager commands (whitelists) for the Discord bot."""

import asyncio
import logging

import discord
from discord.ext import commands

from discord_bot.checks import (
    check_author_whitelisted,
    check_less_equal_author,
    check_non_empty_list,
    check_text_channel_whitelisted,
    check_valid_command,
    check_valid_roles,
    check_valid_text_channels,
)
from discord_bot.util import (
    __ROLES__,
    __ROLES_PERMISSIONS__,
    __TEXT_CHANNELS__,
    __TEXT_CHANNELS_PERMISSIONS__,
    valid_role_id,
    valid_text_channel_id,
)

logger = logging.getLogger("discord")


class Manager(commands.Cog):
    """
    This class represents a suite of commands to add/change/set all parameters of the music bot.

    Attributes:
        wroles (dict[str, list[int]]):
            The list of role ids that are allowed to use the music bot

        wtext_channels (dict[str, list[int]]):
            The list of text channel ids where the music bot can be used

        kwargs (dict[str, Any]):
            Additional keyword arguments
    """

    def __init__(
        self,
        bot: commands.Bot,
        wroles: dict[str, list[int]],
        wtext_channels: dict[str, list[int]],
        **kwargs,
    ):

        if all(not valid_role_id(wrole) for wrole in wroles.values()):
            raise ValueError("wroles needs to be in __ROLES__!")
        if all(
            not valid_text_channel_id(wtext_channel)
            for wtext_channel in wtext_channels.values()
        ):
            raise ValueError("wtext_channels need to be in __TEXT_CHANNELS__!")
        if wroles.keys() != wtext_channels.keys():
            raise ValueError(
                "The keys of the wroles, wtext_channels need to be the same!"
            )
        if list(wroles.keys()) != sorted(wroles.keys()):
            raise ValueError("The keys of the wroles needs to be sorted!")
        if list(wtext_channels.keys()) != sorted(wtext_channels.keys()):
            raise ValueError("The keys of the wtext_channels needs to be sorted!")

        self.bot = bot
        self.wroles = wroles
        self.wtext_channels = wtext_channels
        self._roles_lock = asyncio.Lock()
        self._text_channels_lock = asyncio.Lock()
        self.kwargs = kwargs

    async def _before_help(self, ctx: commands.Context):
        """Checks for the help command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.wroles),
            check_text_channel_whitelisted(ctx, self.wtext_channels),
        )

    @commands.command(aliases=["Help"])
    async def help(self, ctx: commands.Context):
        """
        Sends the help message for the bot.
        """
        await self._before_help(ctx)

        embed = discord.Embed(title="List of commands:", color=discord.Color.blue())
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
            name="!volume <volume>",
            value="Changes the volume of the audio source.",
            inline=False,
        )
        embed.add_field(
            name="!timeout <timeout>",
            value="Changes the timeout of the bot.",
            inline=False,
        )
        embed.add_field(
            name="!role <command> <role_id1> <role_id2> ...",
            value="Whitelist the specified roles for the command.",
            inline=False,
        )
        embed.add_field(
            name="!text_channel <command> <text_channel_id1> <text_channel_id2> ...",
            value="Whitelist the specified text channels for the command.",
            inline=False,
        )
        embed.add_field(
            name="!permission <type>",
            value="Shows which roles or text channels can use each command.",
            inline=False,
        )
        embed.add_field(
            name="!id <type>",
            value="Shows role or text channel IDs.",
            inline=False,
        )
        embed.add_field(
            name="!help",
            value="Shows the list of commands.",
            inline=False,
        )

        await ctx.send(embed=embed)

    async def _before_id(self, ctx: commands.Context, command: str):
        """Checks for the id command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.wroles),
            check_text_channel_whitelisted(ctx, self.wtext_channels),
            check_valid_command(ctx, command, ["role", "text_channel"]),
        )

    @commands.command(aliases=["Id"])
    async def id(self, ctx: commands.Context, command: str):
        """
        Shows the ids of the roles / text channels of the discord server.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The type of ids to show
                "role": shows the ids of the roles
                "text_channel": shows the ids of the text channels
        """
        await self._before_id(ctx, command)

        if command == "role":
            names = list(map(lambda x: x[0], __ROLES__.values()))
            ids = list(__ROLES__.keys())
        else:
            names = list(__TEXT_CHANNELS__.values())
            ids = list(__TEXT_CHANNELS__.keys())

        output = "\n".join([f"{name}: {id}" for name, id in zip(names, ids)])
        await ctx.send(f"```\n{output}\n```")

    async def _before_permission(self, ctx: commands.Context, command: str):
        """Checks for the permission command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.wroles),
            check_text_channel_whitelisted(ctx, self.wtext_channels),
            check_valid_command(ctx, command, ["role", "text_channel"]),
        )

    @commands.command(aliases=["Permission"])
    async def permission(self, ctx: commands.Context, command: str):
        """
        Shows the permission matrix that displays for each command which roles / text channels are allowed to use it.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The type of permission matrix to show
                "role": shows the permission matrix for roles
                "text_channel": shows the permission matrix for text channels
        """
        await self._before_permission(ctx, command)

        if command == "role":
            wrapper = __ROLES__
            message = __ROLES_PERMISSIONS__
            whitelist = self.wroles
        else:
            wrapper = __TEXT_CHANNELS__
            message = __TEXT_CHANNELS_PERMISSIONS__
            whitelist = self.wtext_channels

        ids = list(wrapper.keys())
        cmds = list(whitelist.keys())
        permissions = [
            "✔️" if id in whitelist[cmd] else "✖️" for cmd in cmds for id in ids
        ]
        output = message.format(*permissions)
        await ctx.send(f"```\n{output}\n```")

    async def _before_role(self, ctx: commands.Context, command: str, roles: list[int]):
        """Checks for the role command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.wroles),
            check_text_channel_whitelisted(ctx, self.wtext_channels),
            check_valid_command(ctx, command, list(self.wroles.keys())),
            check_non_empty_list(ctx, roles),
            check_valid_roles(ctx, roles),
            check_less_equal_author(ctx, roles),
        )

    @commands.command(aliases=["Role"])
    async def role(self, ctx: commands.Context, command: str, *roles):
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
        await self._before_role(ctx, command, roles)

        async with self._roles_lock:
            if self.wroles[command] != roles:
                # Case: Whitelisted roles are changed
                self.wroles[command] = roles
                return await ctx.send("✅ Changed whitelisted roles!")
            # Case: Already using whitelisted roles
            return await ctx.send("⚠️ Already using whitelisted roles!")

    async def _before_text_channel(
        self, ctx: commands.Context, command: str, text_channels: list[int]
    ):
        """Checks for the text_channel command before performing it."""
        await asyncio.gather(
            check_author_whitelisted(ctx, self.wroles),
            check_text_channel_whitelisted(ctx, self.wtext_channels),
            check_valid_command(ctx, command, list(self.wtext_channels.keys())),
            check_non_empty_list(ctx, text_channels),
            check_valid_text_channels(ctx, text_channels),
        )

    @commands.command(aliases=["Text_channel"])
    async def text_channel(self, ctx: commands.Context, command: str, *text_channels):
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
        await self._before_text_channel(ctx, command, text_channels)

        async with self._text_channels_lock:
            if self.wtext_channels[command] != text_channels:
                # Case: Whitelisted text channels are changed
                self.wtext_channels[command] = text_channels
                return await ctx.send("✅ Changed whitelisted text channels!")
            # Case: Already using whitelisted text channels
            return await ctx.send("⚠️ Already using whitelisted text channels!")
