import asyncio
import heapq
from dataclasses import dataclass, field


@dataclass(order=True)
class AudioSource:
    """
    Represents an audio source (item) from a YouTube video.

    Attributes:
        title (str):
            The title of the YouTube video.

        user (str):
            The user who requested the YouTube video.

        stream_url (str):
            The URL of the audio stream.

        yt_url (str):
            The URL of the YouTube video.

        priority (int):
            The priority of the audio file.
            Lower values represents higher priorities.
    """

    title: str = field(compare=False)
    user: str = field(compare=False)
    stream_url: str = field(compare=False)
    yt_url: str = field(compare=False)
    priority: int


class Playlist:
    """Represents a playlist of audio sources."""

    def __init__(self, max_size: int | None = None):
        self._playlist = []
        self._max_size = max_size
        self._lock = asyncio.Lock()

    async def empty(self) -> bool:
        """Checks whether the playlist has no audio sources stored."""
        async with self._lock:
            return len(self._playlist) == 0

    async def full(self) -> bool:
        """Checks whether the playlist has reached the max amount of audio sources."""
        async with self._lock:
            if self._max_size is None:
                return False
            else:
                return len(self._playlist) == self._max_size

    async def clear(self):
        """Removes all stored audio sources from the playlist."""
        async with self._lock:
            self._playlist = []

    async def add(self, audio_source: AudioSource):
        """Adds an audio source to the playlist."""
        async with self._lock:
            if self._max_size is not None and len(self._playlist) >= self._max_size:
                raise ValueError(
                    "The playlist has reached the maximum limit of audio sources!"
                )
            heapq.heappush(self._playlist, audio_source)

    async def pop(self) -> AudioSource:
        """Removes and returns the next audio source from the playlist."""
        async with self._lock:
            return heapq.heappop(self._playlist)

    async def iterate(self):
        """Asynchronously iterates over all items in the playlist."""
        async with self._lock:
            playlist = heapq.nsmallest(len(self._playlist), self._playlist)
            for i, item in enumerate(playlist, 0):
                yield i, item
