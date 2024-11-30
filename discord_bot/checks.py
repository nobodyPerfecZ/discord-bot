"""Checks for the discord bot."""

from discord.ext import commands

from discord_bot.util.role import less_equal_role_id, valid_role_id, whitelisted_role_id
from discord_bot.util.text_channel import (
    valid_text_channel_id,
    whitelisted_text_channel_id,
)
from discord_bot.util.voice_channel import (
    valid_voice_channel_id,
    whitelisted_voice_channel_id,
)


async def check_public_text_channel(ctx: commands.Context):
    """Raises an error if the text is written in a private text channel."""
    if ctx.guild is None:
        # Case: Message is written in a private text channel
        await ctx.send("❌ Please use this command in a public text channel!")
        raise commands.CommandError("Text is written in a private text channel!")


async def check_author_voice_channel(ctx: commands.Context):
    """Raises an error if the author is not in a voice channel."""
    if ctx.author.voice is None:
        # Case: Author is not in a voice channel
        await ctx.send("❌ Please join a voice channel, before using this command!")
        raise commands.CommandError("Author is not connected to a voice channel!")


async def check_bot_voice_channel(ctx: commands.Context):
    """Raises an error if the bot is not in a voice channel."""
    if ctx.voice_client is None:
        # Case: Bot is not in a voice channel
        await ctx.send(
            "❌ Please connect me to a voice channel, before using this command!"
        )
        raise commands.CommandError("Bot is not connected to a voice channel!")


async def check_bot_streaming(ctx: commands.Context):
    """Raises an error if the bot is not streaming an audio."""
    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
        # Case: Bot is not playing/pausing an audio stream
        await ctx.send("❌ Please play a song, before using this command!")
        raise commands.CommandError("Bot does not play/pause any song!")


async def check_same_voice_channel(ctx: commands.Context):
    """Raises an error if the author and the bot are not in the same voice channel."""
    if ctx.author.voice.channel != ctx.voice_client.channel:
        # Case: Author and bot are not in the same voice channel
        await ctx.send(
            "❌ Please join to the same voice channel as me, before using this command!"
        )
        raise commands.CommandError("Author and Bot are not in the same voice channel!")


async def check_author_admin(ctx: commands.Context):
    """Raises an error if the author is not an admin."""
    if not ctx.author.guild_permissions.administrator:
        # Case: Author is not an admin
        await ctx.send(
            "❌ You do not have the required Administrator permissions to use this command!"
        )
        raise commands.CommandError(
            "Author does not have the required administrator permission!"
        )


async def check_author_whitelisted(
    ctx: commands.Context, whitelisted_roles: dict[str, list[int]]
):
    """Raises an error if the author is not whitelisted."""
    if not whitelisted_role_id(ctx.author.roles, whitelisted_roles[ctx.command.name]):
        # Case: Author is not whitelisted
        await ctx.send("❌ You do not have the required role to use this command!")
        raise commands.CommandError("The role of the author is not whitelisted!")


async def check_text_channel_whitelisted(
    ctx: commands.Context, whitelisted_text_channels: dict[str, list[int]]
):
    """Raises an error if the text channel is not whitelisted."""
    if not whitelisted_text_channel_id(
        ctx.channel, whitelisted_text_channels[ctx.command.name]
    ):
        # Case: Command is not executed in the required text channel
        await ctx.send("❌ Please use this command in the required text channel!")
        raise commands.CommandError(
            "The text channel of the command is not whitelisted!"
        )


async def check_voice_channel_whitelisted(
    ctx: commands.Context, whitelisted_voice_channels: dict[str, list[int]]
):
    """Raises an error if the voice channel is not whitelisted."""
    if not whitelisted_voice_channel_id(
        ctx.author.voice.channel, whitelisted_voice_channels[ctx.command.name]
    ):
        # Case: Command is not executed in the required text channel
        await ctx.send("❌ Please use this command in the required voice channel!")
        raise commands.CommandError(
            "The voice channel of the author is not whitelisted!"
        )


async def check_non_empty_list(ctx: commands.Context, array: list):
    """Raises an error if the list is empty."""
    if not array:
        # Case: List is empty
        await ctx.send("❌ Please provide a non-empty list!")
        raise commands.CommandError("The list is empty!")


async def check_valid_url(ctx: commands.Context, url: str):
    """Raises an error if the URL is not a valid YouTube URL."""
    if not url.startswith("https://www.youtube.com"):
        # Case: URL is not a valid YouTube URL
        await ctx.send(f"❌ Please try a different URL than ``{url}``!")
        raise commands.CommandError("URL is not a valid YouTube URL!")


async def check_valid_volume(ctx: commands.Context, volume: int):
    """Raises an error if the volume is not in between of 0 and 100."""
    if volume < 0 or volume > 100:
        # Case: Volume is not in between of 0 and 100
        await ctx.send("❌ Please choose a volume between 0 and 100!")
        raise commands.CommandError("Volume is not in between of 0 and 100!")


async def check_valid_timeout(ctx: commands.Context, timeout: int):
    """Raises an error if the timeout is not higher than or equal to 0."""
    if timeout < 0:
        # Case: timeout is not higher than 0
        await ctx.send("❌ Please choose a timeout higher than or equal to 0!")
        raise commands.CommandError("timeout is not higher than or equal to 0!")


async def check_valid_command(
    ctx: commands.Context,
    command: str,
    whitelisted_roles: dict[str, list[int]],
    whitelisted_text_channels: dict[str, list[int]],
    whitelisted_voice_channels: dict[str, list[int]],
):
    """Raises an error if the command is not valid."""
    if (
        command not in whitelisted_roles
        or command not in whitelisted_text_channels
        or command not in whitelisted_voice_channels
    ):
        # Case: Command is not valid
        await ctx.send("❌ Please provide a valid command!")
        raise commands.CommandError("The command is not valid!")


async def check_valid_roles(ctx: commands.Context, roles: list[int]):
    """Raises an error if the roles are not valid."""
    if not valid_role_id(roles):
        # Case: Roles are not valid
        await ctx.send("❌ Please provide valid role ids!")
        raise commands.CommandError("The role ids are not valid!")


async def check_valid_text_channels(ctx: commands.Context, text_channels: list[int]):
    """Raises an error if the text channels are not valid."""
    if not valid_text_channel_id(text_channels):
        # Case: Text channel ids are not valid
        await ctx.send("❌ Please provide valid text channel ids!")
        raise commands.CommandError("The text channel ids are not valid!")


async def check_valid_voice_channels(ctx: commands.Context, voice_channels: list[int]):
    """Raises an error if the voice channels are not valid."""
    if not valid_voice_channel_id(voice_channels):
        # Case: Voice channel ids are not valid
        await ctx.send("❌ Please provide valid voice channel ids!")
        raise commands.CommandError("The voice channel ids are not valid!")


async def check_less_equal_author(ctx: commands.Context, roles: list[int]):
    """Raises an error if the author role is higher than the given roles."""
    if not less_equal_role_id(ctx.author.roles, roles):
        # Case: Author role is higher than the given roles
        await ctx.send("❌ Your role is lower than the given roles!")
        raise commands.CommandError("Author role is lower than the given roles!")
