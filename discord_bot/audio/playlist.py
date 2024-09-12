import asyncio
import heapq
from asyncio import AbstractEventLoop
from dataclasses import dataclass, field

import yt_dlp

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


@dataclass(order=True)
class AudioSource:
    """
    This class represents an audio file (item) of the Playlist manager.

    Attributes:
        title (str):
            The title of the audio file

        yt_url (str):
            The YouTube URL

        audio_url (str):
            The audio stream URL

        priority (int):
            The priority of the audio file.
            Lower values represents higher priorities
    """

    title: str = field(compare=False)
    yt_url: str = field(compare=False)
    audio_url: str = field(compare=False)
    priority: int

    @classmethod
    async def from_url(
        cls,
        yt_url: str,
        priority: int,
        loop: AbstractEventLoop = None,
    ) -> "AudioSource":
        """
        Construct a AudioSource given the YouTube URL.

        Args:
            yt_url (str):
                The URL of the YouTube video

            priority (int):
                The priority of the audio file

            loop (AbstractEventLoop | None):
                The event loop to start the audio connection in the background

        Returns:
            AudioSource:
                The audio source of the YouTube video
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ydl.extract_info(yt_url, download=False)
        )

        return cls(
            title=data["title"],
            yt_url=yt_url,
            audio_url=data["url"],
            priority=priority,
        )

    def __str__(self):
        return self.yt_url

    def __repr__(self):
        return self.yt_url[:27] + "..." if len(self.yt_url) > 30 else self.yt_url


class Playlist:
    """A class that manages a playlist of audio sources."""

    def __init__(self, max_size: int | None = None):
        self._playlist = []
        self._max_size = max_size

    def empty(self) -> bool:
        """
        Checks whether the playlist has no audio files stored.

        Returns:
            bool:
                True if the playlist is empty otherwise False
        """
        return len(self) == 0

    def full(self) -> bool:
        """Checks whether the playlist has reached the maximum amount of stored audio files."""
        if self._max_size is None:
            return False
        else:
            return len(self) == self._max_size

    def clear(self):
        """Removes all stored audio sources from the playlist."""
        self._playlist = []

    def add(self, audio_source: AudioSource):
        """Adds an audio source to the playlist."""
        if self._max_size is not None and len(self) >= self._max_size:
            raise ValueError(
                "The playlist has reached the maximum limit of audio sources!"
            )
        heapq.heappush(self._playlist, audio_source)

    def pop(self) -> AudioSource:
        """Removes and returns the next audio source from the playlist."""
        return heapq.heappop(self._playlist)

    def remove(self, n: int = 1):
        """Removes the next n audio sources from the playlist."""
        if n <= 0 or n > len(self):
            raise ValueError(
                "The argument 'n' must be a non-negative, non-zero number and smaller than the current size!"
            )

        for _ in range(n):
            self.pop()

    def __len__(self):
        return self._playlist.__len__()

    def __iter__(self):
        return self._playlist.__iter__()

    def __getitem__(self, item):
        return self._playlist.__getitem__(item)

    def __str__(self):
        return self._playlist.__str__()

    def __repr__(self):
        return self._playlist.__repr__()
