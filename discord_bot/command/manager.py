"""Manager commands for the Discord bot."""

import asyncio
import logging
from typing import Dict, List

import discord
from discord.ext import commands

from discord_bot.checks import (
    check_author_id_blacklisted,
    check_author_role_blacklisted,
    check_less_equal_author,
    check_text_channel_blacklisted,
    check_valid_author_ids,
    check_valid_author_roles,
    check_valid_command,
    check_valid_text_channels,
    check_valid_voice_channels,
    check_voice_channel_blacklisted,
)

logger = logging.getLogger("discord")


class Manager(commands.Cog):
    """
    A suite of commands for managing the bot.

    Attributes:
        users (Dict[str, List[int]]):
            The dictionary of blacklisted users for each command

        roles (Dict[str, List[int]]):
            The dictionary of blacklisted roles for each command

        text_channels (Dict[str, List[int]]):
            The dictionary of blacklisted text channels for each command

        voice_channels (Dict[str, List[int]]):
            The dictionary of blacklisted voice channels for each command

        kwargs:
            Additional keyword arguments
    """

    def __init__(
        self,
        bot: commands.Bot,
        users: Dict[str, List[int]],
        roles: Dict[str, List[int]],
        text_channels: Dict[str, List[int]],
        voice_channels: Dict[str, List[int]],
        **kwargs,
    ):
        if users.keys() != roles.keys():
            raise ValueError("The keys of the users and roles need to be the same!")
        if roles.keys() != text_channels.keys():
            raise ValueError(
                "The keys of the roles and text_channels need to be the same!"
            )
        if text_channels.keys() != voice_channels.keys():
            raise ValueError(
                "The keys of the text_channels and voice_channels need to be the same!"
            )

        self.bot = bot
        self.users = users
        self.roles = roles
        self.text_channels = text_channels
        self.voice_channels = voice_channels
        self.kwargs = kwargs

        self._users_lock = asyncio.Lock()
        self._roles_lock = asyncio.Lock()
        self._text_channels_lock = asyncio.Lock()
        self._voice_channels_lock = asyncio.Lock()

    async def _before_help(self, ctx: commands.Context):
        """Checks for the help command before performing it."""
        await asyncio.gather(
            check_author_id_blacklisted(ctx, self.users),
            check_author_role_blacklisted(ctx, self.roles),
            check_text_channel_blacklisted(ctx, self.text_channels),
            check_voice_channel_blacklisted(ctx, self.voice_channels),
        )

    @commands.command(aliases=["Help"])
    async def help(self, ctx: commands.Context):
        """Sends the help message for the bot."""
        async with ctx.typing():
            await self._before_help(ctx)

            embed = discord.Embed(title="List of commands:", color=discord.Color.blue())

            embed.add_field(
                name=f"{self.bot.command_prefix}add <url or query>",
                value="Adds a YouTube audio source to the playlist.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}blacklist",
                value="Shows the blacklists for each command.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}chat <message>",
                value="Chats with the bot.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}help",
                value="Displays a list of available commands.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}id",
                value="Shows the IDs in the current discord server.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}join",
                value="Makes the bot join the author's current voice channel.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}leave",
                value="Disconnects the bot from the voice channel.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}pause",
                value="Pauses the currently playing audio source.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}play",
                value="Starts playing the audio source from the playlist.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}reset",
                value="Stops the currently played audio source and clears the "
                + "playlist.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}role <cmd or all> <id1> ... <idN>",
                value="Blacklists specified roles for a command.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}show <n>",
                value="Lists the first `n` audio sources in the playlist.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}skip",
                value="Skips the currently playing audio source.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}text_channel <cmd or all> "
                + "<id1> ... <idN>",
                value="Blacklists specified text channels for a command.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}timeout <ts>",
                value="Adjusts the bot's timeout duration.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}user <cmd or all> <id1> ... <idN>",
                value="Blacklists specified users for a command.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}voice_channel <cmd or all> "
                + "<id1> ... <idN>",
                value="Blacklists specified voice channels for a command.",
                inline=False,
            )
            embed.add_field(
                name=f"{self.bot.command_prefix}volume <vol>",
                value="Modifies the playback volume of the audio source.",
                inline=False,
            )

            await ctx.send(embed=embed)

    async def _before_id(self, ctx: commands.Context):
        """Checks for the id command before performing it."""
        await asyncio.gather(
            check_author_id_blacklisted(ctx, self.users),
            check_author_role_blacklisted(ctx, self.roles),
            check_text_channel_blacklisted(ctx, self.text_channels),
            check_voice_channel_blacklisted(ctx, self.voice_channels),
        )

    @commands.command(aliases=["Id"])
    async def id(self, ctx: commands.Context):
        """
        Shows the IDs in the current discord server.

        This includes:
            - users
            - roles
            - text channels
            - voice channels

        Args:
            ctx (commands.Context):
                The context of the command
        """

        def message(header: str, items: List) -> str:
            """Returns the message to be sent."""
            wrapper = {item.id: item for item in items}
            max_length = len(str(max(wrapper, key=lambda x: len(str(x))))) + 3
            messages = [
                f"•{id}: ".ljust(max_length) + f"{wrapper[id].name}" for id in wrapper
            ]
            output = "\n".join(messages)
            return f"{header}\n```\n{output}\n```"

        async with ctx.typing():
            await self._before_id(ctx)

            if ctx.author.voice:
                user_message = message(
                    "**User ID to Name:**", ctx.author.voice.channel.members
                )
                await ctx.send(user_message)

            role_message = message("**Role ID to Name:**", reversed(ctx.guild.roles))
            await ctx.send(role_message)

            tc_message = message(
                "***Text Channel ID to Name:***", ctx.guild.text_channels
            )
            await ctx.send(tc_message)

            vc_message = message(
                "***Voice Channel ID to Name:***", ctx.guild.voice_channels
            )
            await ctx.send(vc_message)

    async def _before_blacklist(self, ctx: commands.Context):
        """Checks for the blacklist command before performing it."""
        await asyncio.gather(
            check_author_id_blacklisted(ctx, self.users),
            check_author_role_blacklisted(ctx, self.roles),
            check_text_channel_blacklisted(ctx, self.text_channels),
            check_voice_channel_blacklisted(ctx, self.voice_channels),
        )

    @commands.command(aliases=["Blacklist"])
    async def blacklist(self, ctx: commands.Context):
        """
        Shows the blacklists for each command.

        This includes:
            - users
            - roles
            - text channels
            - voice channels

        Args:
            ctx (commands.Context):
                The context of the command.
        """

        def message(header: str, items: List, blacklist: Dict[str, List[int]]) -> str:
            """Returns the message to be sent."""
            wrapper = {item.id: item for item in items}
            max_length = (
                len(self.bot.command_prefix)
                + len(max(blacklist, key=lambda x: len(x)))
                + 3
            )
            messages = []
            for cmd in blacklist:
                line = f"•{self.bot.command_prefix}{cmd}: ".ljust(max_length)
                items = [
                    wrapper[item].name for item in blacklist[cmd] if item in wrapper
                ]
                if items:
                    line += " ".join(items)
                else:
                    line += "---"
                messages.append(line)
            output = "\n".join(messages)
            return f"{header}\n```\n{output}\n```"

        async with ctx.typing():
            await self._before_blacklist(ctx)
            user_message = message(
                "**Blacklisted Users:**", ctx.guild.members, self.users
            )
            role_message = message(
                "**Blacklisted Roles:**", reversed(ctx.guild.roles), self.roles
            )
            tc_message = message(
                "**Blacklisted Text Channels:**",
                ctx.guild.text_channels,
                self.text_channels,
            )
            vc_message = message(
                "**Blacklisted Voice Channels:**",
                ctx.guild.voice_channels,
                self.voice_channels,
            )

            await ctx.send(user_message)
            await ctx.send(role_message)
            await ctx.send(tc_message)
            await ctx.send(vc_message)

    async def _before_user(self, ctx: commands.Context, command: str, users: List[int]):
        """Checks for the user command before performing it."""
        await asyncio.gather(
            check_author_id_blacklisted(ctx, self.users),
            check_author_role_blacklisted(ctx, self.roles),
            check_text_channel_blacklisted(ctx, self.text_channels),
            check_voice_channel_blacklisted(ctx, self.voice_channels),
            check_valid_command(ctx, command, list(self.users.keys())),
            check_valid_author_ids(ctx, users),
        )

    @commands.command(aliases=["User"])
    async def user(self, ctx: commands.Context, command: str, *users):
        """
        Sets the blacklisted users for a specific command.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The command to set the new blacklisted users

            *users (list[int]):
                The list of user ids to be blacklisted
        """
        async with ctx.typing():
            users = list(map(int, users))
            await self._before_user(ctx, command, users)

            async with self._users_lock:
                if command == "all":
                    # Case: All commands should be changed
                    for cmd in self.users:
                        self.users[cmd] = users
                    return await ctx.send(
                        "✅ Changed blacklisted users for all commands!"
                    )
                else:
                    # Case: Specific command should be changed
                    if self.users[command] != users:
                        # Case: Blacklisted users are changed
                        self.users[command] = users
                        return await ctx.send("✅ Changed blacklisted users!")
                    # Case: Already using blacklisted users
                    return await ctx.send("⚠️ Already using blacklisted users!")

    async def _before_role(self, ctx: commands.Context, command: str, roles: List[int]):
        """Checks for the role command before performing it."""
        await asyncio.gather(
            check_author_id_blacklisted(ctx, self.users),
            check_author_role_blacklisted(ctx, self.roles),
            check_text_channel_blacklisted(ctx, self.text_channels),
            check_voice_channel_blacklisted(ctx, self.voice_channels),
            check_valid_command(ctx, command, list(self.roles.keys())),
            check_valid_author_roles(ctx, roles),
            check_less_equal_author(ctx, roles),
        )

    @commands.command(aliases=["Role"])
    async def role(self, ctx: commands.Context, command: str, *roles):
        """
        Sets the blacklisted roles for a specific command.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The command to set the new blacklisted roles

            *roles (list[int]):
                The list of role ids to be blacklisted
        """
        async with ctx.typing():
            roles = list(map(int, roles))
            await self._before_role(ctx, command, roles)

            async with self._roles_lock:
                if command == "all":
                    # Case: All commands should be changed
                    for cmd in self.roles:
                        self.roles[cmd] = roles
                        return await ctx.send(
                            "✅ Changed blacklisted roles for all commands!"
                        )
                else:
                    # Case: Specific command should be changed
                    if self.roles[command] != roles:
                        # Case: Blacklisted roles are changed
                        self.roles[command] = roles
                        return await ctx.send("✅ Changed blacklisted roles!")
                    # Case: Already using blacklisted roles
                    return await ctx.send("⚠️ Already using blacklisted roles!")

    async def _before_text_channel(
        self, ctx: commands.Context, command: str, text_channels: List[int]
    ):
        """Checks for the text_channel command before performing it."""
        await asyncio.gather(
            check_author_id_blacklisted(ctx, self.users),
            check_author_role_blacklisted(ctx, self.roles),
            check_text_channel_blacklisted(ctx, self.text_channels),
            check_voice_channel_blacklisted(ctx, self.voice_channels),
            check_valid_command(ctx, command, list(self.text_channels.keys())),
            check_valid_text_channels(ctx, text_channels),
        )

    @commands.command(aliases=["Text_channel"])
    async def text_channel(self, ctx: commands.Context, command: str, *text_channels):
        """
        Sets the blacklisted text channels for a specific command.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The command to set the new blacklisted text channels

            *text_channels (List[int]):
                The list of text channel ids to be blacklisted
        """
        async with ctx.typing():
            text_channels = list(map(int, text_channels))
            await self._before_text_channel(ctx, command, text_channels)

            async with self._text_channels_lock:
                if command == "all":
                    # Case: All commands should be changed
                    for cmd in self.text_channels:
                        self.text_channels[cmd] = text_channels
                        return await ctx.send(
                            "✅ Changed blacklisted text channels for all commands!"
                        )
                else:
                    # Case: Specific command should be changed
                    if self.text_channels[command] != text_channels:
                        # Case: Blacklisted text channels are changed
                        self.text_channels[command] = text_channels
                        return await ctx.send("✅ Changed blacklisted text channels!")
                    # Case: Already using blacklisted text channels
                    return await ctx.send("⚠️ Already using blacklisted text channels!")

    async def _before_voice_channel(
        self, ctx: commands.Context, command: str, voice_channels: List[int]
    ):
        """Checks for the voice_channel command before performing it."""
        await asyncio.gather(
            check_author_id_blacklisted(ctx, self.users),
            check_author_role_blacklisted(ctx, self.roles),
            check_text_channel_blacklisted(ctx, self.text_channels),
            check_voice_channel_blacklisted(ctx, self.voice_channels),
            check_valid_command(ctx, command, list(self.voice_channels.keys())),
            check_valid_voice_channels(ctx, voice_channels),
        )

    @commands.command(aliases=["Voice_channel"])
    async def voice_channel(self, ctx: commands.Context, command: str, *voice_channels):
        """
        Sets the blacklisted voice channels for a specific command.

        Args:
            ctx (commands.Context):
                The context of the command

            command (str):
                The command to set the new blacklisted voice channels

            *voice_channels (List[int]):
                The list of voice channel ids to be blacklisted
        """
        async with ctx.typing():
            voice_channels = list(map(int, voice_channels))
            await self._before_voice_channel(ctx, command, voice_channels)

            async with self._voice_channels_lock:
                if command == "all":
                    # Case: All commands should be changed
                    for cmd in self.voice_channels:
                        self.voice_channels[cmd] = voice_channels
                        return await ctx.send(
                            "✅ Changed blacklisted voice channels for all commands!"
                        )
                else:
                    # Case: Specific command should be changed
                    if self.voice_channels[command] != voice_channels:
                        # Case: Blacklisted voice channels are changed
                        self.voice_channels[command] = voice_channels
                        return await ctx.send("✅ Changed blacklisted voice channels!")
                    # Case: Already using blacklisted voice channels
                    return await ctx.send("⚠️ Already using blacklisted voice channels!")
