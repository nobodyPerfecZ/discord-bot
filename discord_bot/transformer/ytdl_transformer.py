import discord

from discord_bot.audio import AudioSource

# Options for ffmpeg
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class YTDLVolumeTransformer(discord.PCMVolumeTransformer):
    """
    Represents an audio stream of a YouTube video that can be played by a discord bot.

    Attributes:
        source (discord.AudioSource):
            The audio source to stream

        title (str):
            The title of the YouTube video

        user (str):
            The user who requested the audio stream

        yt_url (str):
            The URL of the YouTube video

        audio_url (str):
            The URL of the audio stream

        priority (int):
            The priority of the audio source

        volume (int):
            The volume of the audio source
    """

    def __init__(
        self,
        source: discord.AudioSource,
        *,
        title: str,
        user: str,
        yt_url: str,
        audio_url: str,
        priority: int,
        volume: int,
    ):
        super().__init__(original=source, volume=volume / 100)
        self.title = title
        self.user = user
        self.yt_url = yt_url
        self.audio_url = audio_url
        self.priority = priority

    @classmethod
    async def from_audio_source(
        cls,
        audio_source: AudioSource,
        volume: int,
    ) -> "YTDLVolumeTransformer":
        """
        Construct a YTDLVolumeTransformer given the audio source.

        Args:
            audio_source (AudioSource):
                The audio source to stream

            volume (int):
                The volume of the audio source

        Returns:
            YTDLVolumeTransformer:
                The audio stream of the YouTube video
        """
        return cls(
            discord.FFmpegPCMAudio(audio_source.stream_url, **ffmpeg_options),
            title=audio_source.title,
            user=audio_source.user,
            yt_url=audio_source.yt_url,
            audio_url=audio_source.stream_url,
            priority=audio_source.priority,
            volume=volume,
        )
