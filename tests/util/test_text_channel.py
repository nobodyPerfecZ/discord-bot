"""Tests for discord_bot/util/text_channel.py."""

from dataclasses import dataclass

import pytest

from discord_bot.util.text_channel import (
    text_channel_id,
    text_channel_name,
    valid_text_channel_id,
    valid_text_channel_name,
    whitelisted_text_channel_id,
    whitelisted_text_channel_name,
)


@dataclass
class TextChannelMock:
    """Mock class for TextChannel."""

    id: int
    name: str


__CHAT__ = TextChannelMock(248897274002931722, "chat☕")
__MUSIC__ = TextChannelMock(725622500846993530, "music🎼")
__CHALLENGES__ = TextChannelMock(684681937155260433, "challenges📰")
__FINANZEN__ = TextChannelMock(769280458688167966, "finanzen💰")
__UNISTUFF__ = TextChannelMock(463446126776025088, "unistuff📎")
__INVITE__ = TextChannelMock(725461496036982914, "invite📌")
__ANIMERECOMMENDATION__ = TextChannelMock(368795981124468745, "animerecommendation")
__BOTTEST__ = TextChannelMock(899013316364632104, "bottest")


@pytest.mark.parametrize(
    argnames="channel",
    argvalues=[__CHAT__],
)
def test_text_channel_id(channel):
    """Tests the text_channel_id() method."""
    assert text_channel_id(channel) == channel.id


@pytest.mark.parametrize(
    argnames="channel",
    argvalues=[__CHAT__],
)
def test_text_channel_name(channel):
    """Tests the text_channel_name() method."""
    assert text_channel_name(channel) == channel.name


@pytest.mark.parametrize(
    argnames=["channel_ids", "expected"],
    argvalues=[
        ([248897274002931722, 725622500846993530], True),
        ([248897274002931722, 899013316364632109], False),
    ],
)
def test_valid_text_channel_id(channel_ids, expected):
    """Tests the valid_text_channel_id() method."""
    assert valid_text_channel_id(channel_ids) == expected


@pytest.mark.parametrize(
    argnames=["channel_names", "expected"],
    argvalues=[
        (["chat☕", "music🎼"], True),
        (["chat☕", "chat123☕"], False),
    ],
)
def test_valid_text_channel_name(channel_names, expected):
    """Tests the valid_text_channel_name() method."""
    assert valid_text_channel_name(channel_names) == expected


@pytest.mark.parametrize(
    argnames=["channel", "whitelisted_channel_ids", "expected"],
    argvalues=[
        (__CHAT__, [248897274002931722, 725622500846993530], True),
        (__CHALLENGES__, [248897274002931722, 725622500846993530], False),
    ],
)
def test_whitelisted_text_channel_id(channel, whitelisted_channel_ids, expected):
    """Tests the whitelisted_text_channel_id() method."""
    assert whitelisted_text_channel_id(channel, whitelisted_channel_ids) == expected


@pytest.mark.parametrize(
    argnames=["channel", "whitelisted_channel_ids", "expected"],
    argvalues=[
        (__CHAT__, ["chat☕", "music🎼"], True),
        (__CHALLENGES__, ["chat☕", "music🎼"], False),
    ],
)
def test_whitelisted_text_channel_name(channel, whitelisted_channel_ids, expected):
    """Tests the whitelisted_text_channel_name() method."""
    assert whitelisted_text_channel_name(channel, whitelisted_channel_ids) == expected
