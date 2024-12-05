"""Utility functions for text channels."""

from discord import TextChannel

__TEXT_CHANNELS__ = {
    248897274002931722: "chat☕",
    725622500846993530: "music🎼",
    725461496036982914: "invite📌",
    368795981124468745: "animerecommendation",
    899013316364632104: "bottest",
}

__TEXT_CHANNELS_PERMISSIONS__ = """
                chat☕ music🎼 invite📌 animerecommendation bottest
add              {}     {}     {}              {}           {}
help             {}     {}     {}              {}           {}
id               {}     {}     {}              {}           {}
join             {}     {}     {}              {}           {}
leave            {}     {}     {}              {}           {}
pause            {}     {}     {}              {}           {}
permission       {}     {}     {}              {}           {}
play             {}     {}     {}              {}           {}
reset            {}     {}     {}              {}           {}
role             {}     {}     {}              {}           {}
show             {}     {}     {}              {}           {}
skip             {}     {}     {}              {}           {}
text_channel     {}     {}     {}              {}           {}
timeout          {}     {}     {}              {}           {}
volume           {}     {}     {}              {}           {}
"""


def text_channel_id(channel: TextChannel) -> int:
    """Returns the id of the given text channel."""
    return channel.id


def text_channel_name(channel: TextChannel) -> str:
    """Returns the name of the given text channel."""
    return channel.name


def valid_text_channel_id(channel_ids: list[int]) -> bool:
    """Returns True if the channel ids are valid text channels."""
    return all(channel_id in __TEXT_CHANNELS__ for channel_id in channel_ids)


def valid_text_channel_name(channel_names: list[str]) -> bool:
    """Returns True if the channel names are valid text channels."""
    return all(
        channel_name in __TEXT_CHANNELS__.values() for channel_name in channel_names
    )


def whitelisted_text_channel_id(
    channel: TextChannel, whitelisted_channel: list[int]
) -> bool:
    """Returns True if the channel is in the list of whitelisted channels."""
    return (
        valid_text_channel_id(whitelisted_channel)
        and text_channel_id(channel) in whitelisted_channel
    )


def whitelisted_text_channel_name(
    channel: TextChannel, whitelisted_channel: list[str]
) -> bool:
    """Returns True if the channel is in the list of whitelisted channels."""
    return (
        valid_text_channel_name(whitelisted_channel)
        and text_channel_name(channel) in whitelisted_channel
    )
