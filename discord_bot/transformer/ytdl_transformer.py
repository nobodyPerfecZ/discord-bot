import asyncio

import discord
import yt_dlp

from discord_bot.audio import AudioSource

# Options for ffmpeg
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

# Options for youtube-dl
ydl_options = {
    "format": "bestaudio/best",
    "keepvideo": False,
    "extractaudio": True,
    "noplaylist": True,
    "skip_download": True,
    "quiet": True,
}
ydl = yt_dlp.YoutubeDL(ydl_options)


class YTDLVolumeTransformer(discord.PCMVolumeTransformer):
    """
    Represents an audio stream of a YouTube video that can be played by a discord bot.

    Attributes:
        source (discord.AudioSource):
            The audio source to stream

        title (str):
            The title of the YouTube video

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
        yt_url: str,
        audio_url: str,
        priority: int,
        volume: int,
    ):
        super().__init__(original=source, volume=volume / 100)
        self.title = title
        self.yt_url = yt_url
        self.audio_url = audio_url
        self.priority = priority

    @classmethod
    async def from_audio_source(
        cls,
        audio_source: AudioSource,
        volume: int,
        loop: asyncio.AbstractEventLoop = None,
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
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ydl.extract_info(audio_source.yt_url)
        )

        return cls(
            discord.FFmpegPCMAudio(data["url"], **ffmpeg_options),
            title=data["title"],
            yt_url=audio_source.yt_url,
            audio_url=data["url"],
            priority=audio_source.priority,
            volume=volume,
        )
