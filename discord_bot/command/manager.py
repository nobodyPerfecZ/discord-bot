"""Manager commands (whitelists) for the Discord bot."""

import asyncio
import logging
from typing import Dict, List

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

logger = logging.getLogger("discord")


class Manager(commands.Cog):
    """
    A suite of commands to manage the music bot.

    Attributes:
        wroles (Dict[str, List[int]]):
            The list of role ids that are allowed to use the music bot

        wtext_channels (Dict[str, List[int]]):
            The list of text channel ids where the music bot can be used

        kwargs:
            Additional keyword arguments
    """

    def __init__(
        self,
        bot: commands.Bot,
        wroles: Dict[str, List[int]],
        wtext_channels: Dict[str, List[int]],
        **kwargs,
    ):
        if wroles.keys() != wtext_channels.keys():
            raise ValueError(
                "The keys of the wroles, wtext_channels need to be the same!"
            )

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
        """Sends the help message for the bot."""
        await self._before_help(ctx)

        embed = discord.Embed(title="List of commands:", color=discord.Color.blue())

        embed.add_field(
            name="!add <url>",
            value="Adds a YouTube audio source to the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!help",
            value="Displays a list of available commands.",
            inline=False,
        )
        embed.add_field(
            name="!id <type>",
            value="Displays role or text channel IDs.",
            inline=False,
        )
        embed.add_field(
            name="!join",
            value="Makes the bot join the author's current voice channel.",
            inline=False,
        )
        embed.add_field(
            name="!leave",
            value="Disconnects the bot from the voice channel.",
            inline=False,
        )
        embed.add_field(
            name="!pause",
            value="Pauses the currently playing audio source.",
            inline=False,
        )
        embed.add_field(
            name="!permission <type>",
            value="Displays the roles allowed to use each command or the text "
            + " channels where each command can be used.",
            inline=False,
        )
        embed.add_field(
            name="!play",
            value="Starts playing the audio source from the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!reset",
            value="Stops the currently played audio source and clears the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!role <cmd> <id1> ... <idN>",
            value="Whitelists specified roles for a command.",
            inline=False,
        )
        embed.add_field(
            name="!show <n>",
            value="Lists the audio sources in the playlist.",
            inline=False,
        )
        embed.add_field(
            name="!skip",
            value="Skips the currently playing audio source.",
            inline=False,
        )
        embed.add_field(
            name="!text_channel <cmd> <id1> ... <idN>",
            value="Whitelists specified text channels for a command.",
            inline=False,
        )
        embed.add_field(
            name="!timeout <ts>",
            value="Adjusts the bot's timeout duration.",
            inline=False,
        )
        embed.add_field(
            name="!volume <vol>",
            value="Modifies the playback volume of the audio source.",
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
            header = "**Role ID to Name:**"
            wrapper = {role.id: role for role in reversed(ctx.guild.roles)}
        else:
            header = "***Text Channel ID to Name:***"
            wrapper = {
                text_channel.id: text_channel
                for text_channel in ctx.guild.text_channels
            }

        messages = []
        max_length = len(str(max(wrapper, key=lambda x: len(str(x))))) + 3
        for id in wrapper:
            line = f"•{id}: ".ljust(max_length) + f"{wrapper[id].name}"
            messages.append(line)
        output = "\n".join(messages)
        await ctx.send(f"{header}\n```\n{output}\n```")

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
        Shows for each command which roles / text channels are allowed to use.

        Args:
            ctx (commands.Context):
                The context of the command.

            command (str):
                The type of permission to show:
                - "role": shows the permission matrix for roles.
                - "text_channel": shows the permission matrix for text channels.
        """
        await self._before_permission(ctx, command)

        if command == "role":
            header = "**Whitelisted Roles:**"
            wrapper = {role.id: role for role in reversed(ctx.guild.roles)}
            whitelist = self.wroles
        else:
            header = "**Whitelisted Text Channels:**"
            wrapper = {
                text_channel.id: text_channel
                for text_channel in reversed(ctx.guild.text_channels)
            }
            whitelist = self.wtext_channels

        messages = []
        max_length = (
            len(self.bot.command_prefix) + len(max(whitelist, key=lambda x: len(x))) + 3
        )
        for cmd in whitelist:
            line = f"•{self.bot.command_prefix}{cmd}: ".ljust(max_length)
            items = [wrapper[item].name for item in whitelist[cmd] if item in wrapper]
            if items:
                line += " ".join(items)
            else:
                line += "---"
            messages.append(line)
        output = "\n".join(messages)
        await ctx.send(f"{header}\n```\n{output}\n```")

    async def _before_role(self, ctx: commands.Context, command: str, roles: List[int]):
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
        self, ctx: commands.Context, command: str, text_channels: List[int]
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

            *text_channels (List[int]):
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
