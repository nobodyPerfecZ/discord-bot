import asyncio
from asyncio import AbstractEventLoop
from typing import Any

import discord
import yt_dlp
from discord import AudioSource
from yt_dlp import YoutubeDL

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ydl_options = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "noplaylist": True,
    "skip_download": True,
    "quiet": True,
}
ydl = YoutubeDL(ydl_options)


class YTDLSource(discord.PCMVolumeTransformer):
    """
    Represents a YouTube audio source that can be played by a discord bot.

    This class allows to adjust the volume of the audio.
    """

    def __init__(self, source: AudioSource, *, data: dict[str, Any], volume: float = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data["title"]
        self.url = data["url"]

    @classmethod
    async def from_url(cls, url: str, *, volume: float = 0.5, loop: AbstractEventLoop = None) -> "YTDLSource":
        """
        Construct a YTDLSource given the YouTube URL.

        Args:
            url (str):
                The URL of the YouTube video

            volume (float):
                The volume of the YTDLSource

            loop (AbstractEventLoop):
                The event loop to start the audio connection in the background

        Returns:
            YTDLSource:
                The audio source of the YouTube video
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        audio_source = data["url"]

        return cls(discord.FFmpegPCMAudio(audio_source, **ffmpeg_options), data=data, volume=volume)

    @staticmethod
    async def is_valid(url: str, loop: AbstractEventLoop = None) -> bool:
        """
        Checks whether the given YouTube URL is supported by YoutubeDL.

        Args:
            url (str):
                The URL of the YouTube video

            loop (AbstractEventLoop):
                The event loop to start the audio connection in the background

        Returns:
            bool:
                Returns True if the given url is supported, otherwise False
        """
        loop = loop or asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return True
        except yt_dlp.utils.YoutubeDLError:
            return False
