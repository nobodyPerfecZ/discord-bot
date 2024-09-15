from discord import TextChannel, VoiceChannel

# Wrapper from channels ids to channel names
channel_id_to_name = {
    # Text Channels
    248897274002931722: "chat☕",
    725622500846993530: "music🎼",
    684681937155260433: "challenges📰",
    769280458688167966: "finanzen💰",
    463446126776025088: "unistuff📎",
    725461496036982914: "invite📌",
    368795981124468745: "animerecommendation",
    899013316364632104: "bottest",
}


def channels_valid(channels: list[str]) -> bool:
    """Returns True if the channels are valid."""
    return all(channel in list(channel_id_to_name.values()) for channel in channels)


def channel_whitelisted(
    channel: TextChannel | VoiceChannel, whitelisted_channels: list[str]
) -> bool:
    """Returns True if the channel is in the list of whitelisted channels."""
    return channel_name(channel) in whitelisted_channels


def channel_name(channel: TextChannel | VoiceChannel) -> str | None:
    """Returns the name of the given channel."""
    return channel_id_to_name.get(channel.id, None)
