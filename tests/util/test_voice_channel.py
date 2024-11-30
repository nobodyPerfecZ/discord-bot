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


__ADMIN_RAUM__ = VoiceChannelMock(248899126639591424, "Admin Raum💂")
__MODERATOR_RAUM__ = VoiceChannelMock(560510866056020008, "Moderator Raum👲")
__GRUPPENRAUM_1__ = VoiceChannelMock(1148500378158125107, "Gruppenraum #1🔒")
__GRUPPENRAUM_2__ = VoiceChannelMock(1148500420973572096, "Gruppenraum #2🔓")
__GRUPPENRAUM_3__ = VoiceChannelMock(712226034409275454, "Gruppenraum #1🔒")
__GRUPPENRAUM_4__ = VoiceChannelMock(725417378623651920, "Gruppenraum #2🔓")
__EINGANGSHALLE__ = VoiceChannelMock(248897274002931724, "Eingangshalle🚪")
__GEHEIME_DXD_ECKE__ = VoiceChannelMock(714534557063446659, "Geheime DxD Ecke🔞")
__GAMING_CHANNEL_1__ = VoiceChannelMock(248902220446302219, "Gaming Channel #1👾")
__GAMING_CHANNEL_2__ = VoiceChannelMock(248902352684318721, "Gaming Channel #2👾")
__PROGRAMMING_ECKE__ = VoiceChannelMock(248901495058202634, "Programming Ecke💻")
__BUSINESS_GESPRACHE__ = VoiceChannelMock(248901340309225472, "Business Gespräche💲💹")
__KINOMODUS__ = VoiceChannelMock(936729507937808414, "Kinomodus🍿")
__UNTERWEGS_ZUR_BRUCKE__ = VoiceChannelMock(
    248899298941468692, "Unterwegs zur Brücke🌉"
)


@pytest.mark.parametrize(
    argnames="channel",
    argvalues=[__ADMIN_RAUM__],
)
def test_voice_channel_id(channel):
    """Tests the voice_channel_id() method."""
    assert voice_channel_id(channel) == channel.id


@pytest.mark.parametrize(
    argnames="channel",
    argvalues=[__ADMIN_RAUM__],
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
        (__ADMIN_RAUM__, [248899126639591424, 560510866056020008], True),
        (__GRUPPENRAUM_1__, [248899126639591424, 560510866056020008], False),
    ],
)
def test_whitelisted_voice_channel_id(channel, whitelisted_channel_ids, expected):
    """Tests the whitelisted_voice_channel_id() method."""
    assert whitelisted_voice_channel_id(channel, whitelisted_channel_ids) == expected


@pytest.mark.parametrize(
    argnames=["channel", "whitelisted_channel_ids", "expected"],
    argvalues=[
        (__ADMIN_RAUM__, ["Admin Raum💂", "Moderator Raum👲"], True),
        (__GRUPPENRAUM_1__, ["Admin Raum💂", "Moderator Raum👲"], False),
    ],
)
def test_whitelisted_voice_channel_name(channel, whitelisted_channel_ids, expected):
    """Tests the whitelisted_voice_channel_name() method."""
    assert whitelisted_voice_channel_name(channel, whitelisted_channel_ids) == expected
