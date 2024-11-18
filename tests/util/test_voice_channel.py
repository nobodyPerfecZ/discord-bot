"""Tests for discord_bot/util/voice_channel.py."""

from dataclasses import dataclass

import pytest

from discord_bot.util.voice_channel import (
    valid_voice_channel_id,
    valid_voice_channel_name,
    voice_channel_id,
    voice_channel_name,
    whitelisted_voice_channel_id,
    whitelisted_voice_channel_name,
)


@dataclass
class VoiceChannelMock:
    """Mock class for VoiceChannel."""

    id: int
    name: str


@pytest.mark.parametrize(
    argnames="channel",
    argvalues=[
        VoiceChannelMock(248899126639591424, "Admin Raum💂"),
    ],
)
def test_voice_channel_id(channel):
    """Tests the voice_channel_id() method."""
    assert voice_channel_id(channel) == channel.id


@pytest.mark.parametrize(
    argnames="channel",
    argvalues=[
        VoiceChannelMock(248899126639591424, "Admin Raum💂"),
    ],
)
def test_voice_channel_name(channel):
    """Tests the voice_channel_name() method."""
    assert voice_channel_name(channel) == channel.name


@pytest.mark.parametrize(
    argnames=["channel_ids", "expected"],
    argvalues=[
        ([248899126639591424, 560510866056020008], True),
        ([248899126639591424, 560510866056020009], False),
    ],
)
def test_valid_voice_channel_id(channel_ids, expected):
    """Tests the valid_voice_channel_id() method."""
    assert valid_voice_channel_id(channel_ids) == expected


@pytest.mark.parametrize(
    argnames=["channel_names", "expected"],
    argvalues=[
        (["Admin Raum💂", "Moderator Raum👲"], True),
        (["Admin Raum💂", "Admin Rau23mm💂"], False),
    ],
)
def test_valid_voice_channel_name(channel_names, expected):
    """Tests the valid_voice_channel_name() method."""
    assert valid_voice_channel_name(channel_names) == expected


@pytest.mark.parametrize(
    argnames=["channel", "whitelisted_channel_ids", "expected"],
    argvalues=[
        (
            VoiceChannelMock(248899126639591424, "Admin Raum💂"),
            [248899126639591424, 560510866056020008],
            True,
        ),
        (
            VoiceChannelMock(1148500378158125107, "Gruppenraum #1🔒"),
            [248899126639591424, 560510866056020008],
            False,
        ),
    ],
)
def test_whitelisted_voice_channel_id(channel, whitelisted_channel_ids, expected):
    """Tests the whitelisted_voice_channel_id() method."""
    assert whitelisted_voice_channel_id(channel, whitelisted_channel_ids) == expected


@pytest.mark.parametrize(
    argnames=["channel", "whitelisted_channel_ids", "expected"],
    argvalues=[
        (
            VoiceChannelMock(248899126639591424, "Admin Raum💂"),
            ["Admin Raum💂", "Moderator Raum👲"],
            True,
        ),
        (
            VoiceChannelMock(1148500378158125107, "Gruppenraum #1🔒"),
            ["Admin Raum💂", "Moderator Raum👲"],
            False,
        ),
    ],
)
def test_whitelisted_voice_channel_name(channel, whitelisted_channel_ids, expected):
    """Tests the whitelisted_voice_channel_name() method."""
    assert whitelisted_voice_channel_name(channel, whitelisted_channel_ids) == expected
