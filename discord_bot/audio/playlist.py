import heapq
from dataclasses import dataclass, field


@dataclass(order=True)
class AudioSource:
    """
    Represents an audio source (item) from a YouTube video.

    Attributes:
        yt_url (str):
            The URL of the YouTube video

        priority (int):
            The priority of the audio file.
            Lower values represents higher priorities
    """

    yt_url: str = field(compare=False)
    priority: int


class Playlist:
    """Represents a playlist of audio sources."""

    def __init__(self, max_size: int | None = None):
        self._playlist = []
        self._max_size = max_size

    def empty(self) -> bool:
        """Checks whether the playlist has no audio sources stored."""
        return len(self) == 0

    def full(self) -> bool:
        """Checks whether the playlist has reached the maximum amount of stored audio sources."""
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
