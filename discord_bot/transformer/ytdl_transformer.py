import discord

from discord_bot.audio import AudioSource

# Options for ffmpeg
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class YTDLVolumeTransformer(discord.PCMVolumeTransformer):
    """
    Represents a YouTube audio stream that can be played by a discord bot.

    Attributes:
        source (discord.AudioSource):
            The audio source to stream

        title (str):
            The title of the audio source

        yt_url (str):
            The YouTube URL

        audio_url (str):
            The audio stream URL

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
        yt_url: str,
        audio_url: str,
        priority: int,
        volume: int = 50
    ):
        super().__init__(original=source, volume=volume / 100)
        self.title = title
        self.yt_url = yt_url
        self.audio_url = audio_url
        self.priority = priority

    @classmethod
    def from_audio_source(
        cls,
        audio_source: AudioSource,
        volume: int = 50,
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
            discord.FFmpegPCMAudio(audio_source.audio_url, **ffmpeg_options),
            title=audio_source.title,
            yt_url=audio_source.yt_url,
            audio_url=audio_source.audio_url,
            priority=audio_source.priority,
            volume=volume,
        )
