"""Manager commands (whitelists) for the Discord bot."""

import logging

import discord
from discord.ext import commands

from discord_bot.util.role import valid_role_id, whitelisted_role_id
from discord_bot.util.text_channel import (
    valid_text_channel_id,
    whitelisted_text_channel_id,
)
from discord_bot.util.voice_channel import (
    valid_voice_channel_id,
    whitelisted_voice_channel_id,
)

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
    """

    def __init__(
        self,
        bot: commands.Bot,
        whitelisted_roles: dict[str, list[int]],
        whitelisted_text_channels: dict[str, list[int]],
        whitelisted_voice_channels: dict[str, list[int]],
        **kwargs
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

        self.bot = bot
        self.whitelisted_roles = whitelisted_roles
        self.whitelisted_text_channels = whitelisted_text_channels
        self.whitelisted_voice_channels = whitelisted_voice_channels

    async def _check_author_role_is_whitelisted(self, ctx: commands.Context):
        """Raises an error if the author does not have the required role."""
        if not whitelisted_role_id(
            ctx.author.roles, self.whitelisted_roles[ctx.command.name]
        ):
            # Case: Author does not have the required role
            await ctx.send("❌ You do not have the required role to use this command!")
            raise commands.CommandError("Author does not have the required role!")

    async def _check_text_channel_is_whitelisted(self, ctx: commands.Context):
        """Raises an error if the command is not executed in the required text channel."""
        if not whitelisted_text_channel_id(
            ctx.channel, self.whitelisted_text_channels[ctx.command.name]
        ):
            # Case: Command is not executed in the required text channel
            await ctx.send("❌ Please use this command in the required text channel!")
            raise commands.CommandError(
                "Command is not executed in the required text channel!"
            )

    async def _check_voice_channel_is_whitelisted(self, ctx: commands.Context):
        """Raises an error if the command is not executed in the required voice channel."""
        if not whitelisted_voice_channel_id(
            ctx.author.voice.channel, self.whitelisted_voice_channels[ctx.command.name]
        ):
            # Case: Command is not executed in the required text channel
            await ctx.send("❌ Please use this command in the required voice channel!")
            raise commands.CommandError(
                "Command is not executed in the required voice channel!"
            )

    @staticmethod
    def help_information() -> discord.Embed | None:
        """Returns the help information of the manager commands."""
        return None
