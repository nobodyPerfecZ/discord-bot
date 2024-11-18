"""Utility functions for voice channels."""

from discord import VoiceChannel

__WHITELISTED_VOICE_CHANNELS__ = [
    248899126639591424,
    560510866056020008,
    1148500378158125107,
    1148500420973572096,
    712226034409275454,
    725417378623651920,
    714534557063446659,
    248902220446302219,
    248902352684318721,
    248901495058202634,
    248901340309225472,
    936729507937808414,
]
__VOICE_CHANNELS__ = {
    248899126639591424: "Admin Raum💂",
    560510866056020008: "Moderator Raum👲",
    1148500378158125107: "Gruppenraum #1🔒",
    1148500420973572096: "Gruppenraum #2🔓",
    712226034409275454: "Gruppenraum #1🔒",
    725417378623651920: "Gruppenraum #2🔓",
    248897274002931724: "Eingangshalle🚪",
    714534557063446659: "Geheime DxD Ecke🔞",
    248902220446302219: "Gaming Channel #1👾",
    248902352684318721: "Gaming Channel #2👾",
    248901495058202634: "Programming Ecke💻",
    248901340309225472: "Business Gespräche💲💹",
    936729507937808414: "Kinomodus🍿",
    248899298941468692: "Unterwegs zur Brücke🌉",
}


def voice_channel_id(channel: VoiceChannel) -> int:
    """Returns the id of the given voice channel."""
    return channel.id


def voice_channel_name(channel: VoiceChannel) -> str:
    """Returns the name of the given voice channel."""
    return channel.name


def valid_voice_channel_id(channel_ids: list[int]) -> bool:
    """Returns True if the channel ids are valid voice channels."""
    return all(channel_id in __VOICE_CHANNELS__ for channel_id in channel_ids)


def valid_voice_channel_name(channel_names: list[str]) -> bool:
    """Returns True if the channel names are valid voice channels."""
    return all(
        channel_name in __VOICE_CHANNELS__.values() for channel_name in channel_names
    )


def whitelisted_voice_channel_id(
    channel: VoiceChannel,
    whitelisted_channel_ids: list[int],
) -> bool:
    """Returns True if the channel is in the list of whitelisted channels."""
    return (
        valid_voice_channel_id(whitelisted_channel_ids)
        and voice_channel_id(channel) in whitelisted_channel_ids
    )


def whitelisted_voice_channel_name(
    channel: VoiceChannel,
    whitelisted_channel_names: list[str],
) -> bool:
    """Returns True if the channel is in the list of whitelisted channels."""
    return (
        valid_voice_channel_name(whitelisted_channel_names)
        and voice_channel_name(channel) in whitelisted_channel_names
    )
