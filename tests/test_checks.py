"""Tests for discord_bot/checks.py."""

from dataclasses import dataclass, replace
from typing import List

import pytest
from discord.ext import commands

from discord_bot.checks import (
    check_author_admin,
    check_author_voice_channel,
    check_author_whitelisted,
    check_bot_streaming,
    check_bot_voice_channel,
    check_less_equal_author,
    check_non_empty_list,
    check_same_voice_channel,
    check_text_channel_whitelisted,
    check_valid_command,
    check_valid_n,
    check_valid_roles,
    check_valid_text_channels,
    check_valid_timeout,
    check_valid_url,
    check_valid_volume,
)


@dataclass
class RoleMock:
    """Mock class for ctx.author.roles."""

    id: int
    name: str


@dataclass
class VoiceChannelMock:
    """Mock class for ctx.author.voice.channel."""

    id: int
    name: str


@dataclass
class TextChannelMock:
    """Mock class for ctx.channel."""

    id: int
    name: str


@dataclass
class GuildPermissionMock:
    """Mock class for ctx.author.guild_permissions."""

    administrator: bool


@dataclass
class VoiceMock:
    """Mock class for ctx.author.voice."""

    channel: VoiceChannelMock


@dataclass
class AuthorMock:
    """Mock class for ctx.author."""

    voice: VoiceMock | None
    roles: List[RoleMock]
    guild_permissions: GuildPermissionMock


@dataclass
class VoiceClientMock:
    """Mock class for ctx.voice_client."""

    channel: VoiceChannelMock
    playing: bool
    paused: bool

    def is_playing(self):
        """Mock is_playing method."""
        return self.playing

    def is_paused(self):
        """Mock is_paused method."""
        return self.paused


@dataclass
class CommandMock:
    """Mock class for ctx.command."""

    name: str


@dataclass
class GuildMock:
    """Mock class for ctx.guild."""

    roles: List[RoleMock]
    text_channels: List[TextChannelMock]


@dataclass
class ContextMock:
    """Mock class for ctx."""

    author: AuthorMock
    channel: TextChannelMock
    command: CommandMock
    guild: GuildMock | None
    voice_client: VoiceClientMock | None

    async def send(self, message):
        """Mock send method."""
        return message


__CTX__ = ContextMock(
    author=AuthorMock(
        voice=VoiceMock(
            channel=VoiceChannelMock(id=248902220446302219, name="Gaming Channel #1👾")
        ),
        roles=[RoleMock(id=542084251038908436, name="#ANBU#")],
        guild_permissions=GuildPermissionMock(administrator=True),
    ),
    channel=TextChannelMock(id=725622500846993530, name="music🎼"),
    command=CommandMock(name="play"),
    guild=GuildMock(
        roles=[
            RoleMock(id=248897274002931722, name="@everyone"),
            RoleMock(id=248898155867930624, name="Genin"),
            RoleMock(id=686645319718404100, name="Chunin"),
            RoleMock(id=385159915918065664, name="Jonin"),
            RoleMock(id=248898634924425216, name="Kage"),
            RoleMock(id=542084251038908436, name="#ANBU#"),
        ],
        text_channels=[
            TextChannelMock(id=248897274002931722, name="chat☕"),
            TextChannelMock(id=725622500846993530, name="music🎼"),
            TextChannelMock(id=725461496036982914, name="invite📌"),
            TextChannelMock(id=368795981124468745, name="animerecommendation"),
            TextChannelMock(id=899013316364632104, name="bottest"),
        ],
    ),
    voice_client=VoiceClientMock(
        channel=VoiceChannelMock(id=248902220446302219, name="Gaming Channel #1👾"),
        playing=True,
        paused=False,
    ),
)


@pytest.mark.asyncio
async def test_check_author_voice_channel_with_invalid_ctx():
    """Tests check_author_voice_channel() function with invalid ctx."""
    ctx = replace(__CTX__, author=replace(__CTX__.author, voice=None))

    with pytest.raises(commands.CommandError):
        await check_author_voice_channel(ctx)


@pytest.mark.asyncio
async def test_check_author_voice_channel_with_valid_ctx():
    """Tests check_author_voice_channel() function with valid ctx."""
    ctx = __CTX__

    await check_author_voice_channel(ctx)


@pytest.mark.asyncio
async def test_check_bot_voice_channel_with_invalid_ctx():
    """Tests check_bot_voice_channel() function with invalid ctx."""
    ctx = replace(__CTX__, voice_client=None)

    with pytest.raises(commands.CommandError):
        await check_bot_voice_channel(ctx)


@pytest.mark.asyncio
async def test_check_bot_voice_channel_with_valid_ctx():
    """Tests check_bot_voice_channel() function with valid ctx."""
    ctx = __CTX__

    await check_bot_voice_channel(ctx)


@pytest.mark.asyncio
async def test_check_bot_streaming_with_invalid_ctx():
    """Tests check_bot_streaming() function with invalid ctx."""
    ctx = replace(__CTX__, voice_client=replace(__CTX__.voice_client, playing=False))

    with pytest.raises(commands.CommandError):
        await check_bot_streaming(ctx)


@pytest.mark.asyncio
async def test_check_bot_streaming_with_valid_ctx():
    """Tests check_bot_streaming() function with valid ctx."""
    ctx = __CTX__

    await check_bot_streaming(ctx)


@pytest.mark.asyncio
async def test_check_same_voice_channel_with_invalid_ctx():
    """Tests check_same_voice_channel() function with invalid ctx."""
    ctx = replace(
        __CTX__,
        voice_client=replace(
            __CTX__.voice_client,
            channel=VoiceChannelMock(id=248902352684318721, name="Gaming Channel #2👾"),
        ),
    )

    with pytest.raises(commands.CommandError):
        await check_same_voice_channel(ctx)


@pytest.mark.asyncio
async def test_check_same_voice_channel_with_valid_ctx():
    """Tests check_same_voice_channel() function with valid ctx."""
    ctx = __CTX__

    await check_same_voice_channel(ctx)


@pytest.mark.asyncio
async def test_check_author_admin_with_invalid_ctx():
    """Tests check_author_admin() function with invalid ctx."""
    ctx = replace(
        __CTX__,
        author=replace(
            __CTX__.author, guild_permissions=GuildPermissionMock(administrator=False)
        ),
    )

    with pytest.raises(commands.CommandError):
        await check_author_admin(ctx)


@pytest.mark.asyncio
async def test_check_author_admin_with_valid_ctx():
    """Tests check_author_admin() function with valid ctx."""
    ctx = __CTX__

    await check_author_admin(ctx)


@pytest.mark.asyncio
async def test_check_author_whitelisted_with_invalid_ctx():
    """Tests check_author_whitelisted() function with invalid ctx."""
    ctx = replace(
        __CTX__,
        author=replace(
            __CTX__.author, roles=[RoleMock(id=385159915918065664, name="Jonin")]
        ),
    )
    wroles = {"play": [542084251038908436, 248898634924425216]}

    with pytest.raises(commands.CommandError):
        await check_author_whitelisted(ctx, wroles)


@pytest.mark.asyncio
async def test_check_author_whitelisted_with_valid_ctx():
    """Tests check_author_whitelisted() function with valid ctx."""
    ctx = __CTX__
    wroles = {"play": [542084251038908436, 248898634924425216]}

    await check_author_whitelisted(ctx, wroles)


@pytest.mark.asyncio
async def test_check_text_channel_whitelisted_with_invalid_ctx():
    """Tests check_text_channel_whitelisted() function with invalid ctx."""
    ctx = replace(
        __CTX__, channel=TextChannelMock(id=684681937155260433, name="challenges📰")
    )
    wtext_channels = {"play": [248897274002931722, 725622500846993530]}

    with pytest.raises(commands.CommandError):
        await check_text_channel_whitelisted(ctx, wtext_channels)


@pytest.mark.asyncio
async def test_check_text_channel_whitelisted_with_valid_ctx():
    """Tests check_text_channel_whitelisted() function with valid ctx."""
    ctx = __CTX__
    wtext_channels = {"play": [248897274002931722, 725622500846993530]}

    await check_text_channel_whitelisted(ctx, wtext_channels)


@pytest.mark.asyncio
async def test_check_non_empty_list_with_invalid_list():
    """Tests check_non_empty_list() function with invalid list."""
    ctx = __CTX__
    array = []

    with pytest.raises(commands.CommandError):
        await check_non_empty_list(ctx, array)


@pytest.mark.asyncio
async def test_check_non_empty_list_with_valid_list():
    """Tests check_non_empty_list() function with valid list."""
    ctx = __CTX__
    array = [1, 2, 3]

    await check_non_empty_list(ctx, array)


@pytest.mark.asyncio
async def test_check_valid_n_with_invalid_n():
    """Tests check_valid_n() function with invalid n."""
    ctx = __CTX__
    n = -1

    with pytest.raises(commands.CommandError):
        await check_valid_n(ctx, n)


@pytest.mark.asyncio
async def test_check_valid_n_with_valid_n():
    """Tests check_valid_n() function with valid n."""
    ctx = __CTX__
    n = 5

    await check_valid_n(ctx, n)


@pytest.mark.asyncio
async def test_check_valid_url_with_invalid_url():
    """Tests check_valid_url() function with invalid url."""
    ctx = __CTX__
    url = "https://www.test1234.com/watch?v=123456789"

    with pytest.raises(commands.CommandError):
        await check_valid_url(ctx, url)


@pytest.mark.asyncio
async def test_check_valid_url_with_valid_url():
    """Tests check_valid_url() function with valid url."""
    ctx = __CTX__
    url = "https://www.youtube.com/watch?v=123456789"

    await check_valid_url(ctx, url)


@pytest.mark.asyncio
async def test_check_valid_volume_with_invalid_volume():
    """Tests check_valid_volume() function with invalid volume."""
    ctx = __CTX__
    volume = 101

    with pytest.raises(commands.CommandError):
        await check_valid_volume(ctx, volume)


@pytest.mark.asyncio
async def test_check_valid_volume_with_valid_volume():
    """Tests check_valid_volume() function with valid volume."""
    ctx = __CTX__
    volume = 100

    await check_valid_volume(ctx, volume)


@pytest.mark.asyncio
async def test_check_valid_timeout_with_invalid_timeout():
    """Tests check_valid_timeout() function with invalid timeout."""
    ctx = __CTX__
    timeout = -1

    with pytest.raises(commands.CommandError):
        await check_valid_timeout(ctx, timeout)


@pytest.mark.asyncio
async def test_check_valid_timeout_with_valid_timeout():
    """Tests check_valid_timeout() function with valid timeout."""
    ctx = __CTX__
    timeout = 0

    await check_valid_timeout(ctx, timeout)


@pytest.mark.asyncio
async def test_check_valid_command_with_invalid_command():
    """Tests check_valid_command() function with invalid command."""
    ctx = __CTX__
    cmd = "skip"
    cmds = ["play"]

    with pytest.raises(commands.CommandError):
        await check_valid_command(ctx, cmd, cmds)


@pytest.mark.asyncio
async def test_check_valid_command_with_valid_command():
    """Tests check_valid_command() function with valid command."""
    ctx = __CTX__
    cmd = "play"
    cmds = ["play"]

    await check_valid_command(ctx, cmd, cmds)


@pytest.mark.asyncio
async def test_check_valid_roles_with_invalid_roles():
    """Tests check_valid_roles() function with invalid roles."""
    ctx = __CTX__
    role_ids = [542084251038908436, 248898634924425123]

    with pytest.raises(commands.CommandError):
        await check_valid_roles(ctx, role_ids)


@pytest.mark.asyncio
async def test_check_valid_roles_with_valid_roles():
    """Tests check_valid_roles() function with valid roles."""
    ctx = __CTX__
    roles = [542084251038908436, 248898634924425216]

    await check_valid_roles(ctx, roles)


@pytest.mark.asyncio
async def test_check_valid_text_channels_with_invalid_text_channels():
    """Tests check_valid_text_channels() function with invalid text channels."""
    ctx = __CTX__
    text_channels = [248897274002931722, 725622500846993123]

    with pytest.raises(commands.CommandError):
        await check_valid_text_channels(ctx, text_channels)


@pytest.mark.asyncio
async def test_check_valid_text_channels_with_valid_text_channels():
    """Tests check_valid_text_channels() function with valid text channels."""
    ctx = __CTX__
    text_channels = [248897274002931722, 725622500846993530]

    await check_valid_text_channels(ctx, text_channels)


@pytest.mark.asyncio
async def test_check_less_equal_author_with_invalid_ctx():
    """Tests check_less_equal_author() function with invalid ctx."""
    ctx = replace(
        __CTX__,
        author=replace(
            __CTX__.author, roles=[RoleMock(id=248898634924425216, name="Kage")]
        ),
    )
    role_ids = [542084251038908436, 248898634924425216]

    with pytest.raises(commands.CommandError):
        await check_less_equal_author(ctx, role_ids)


@pytest.mark.asyncio
async def test_check_less_equal_author_with_valid_ctx():
    """Tests check_less_equal_author() function with invalid ctx."""
    ctx = __CTX__
    role_ids = [542084251038908436, 248898634924425216]

    await check_less_equal_author(ctx, role_ids)
