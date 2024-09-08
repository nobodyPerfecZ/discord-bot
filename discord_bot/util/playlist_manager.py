import heapq
from typing import Optional


class AudioFile:
    """
    This class represents an audio file (item) of the Playlist manager.

    Attributes:
        priority (int):
            The priority of the audio file (lower values represents higher priorities)

        url (str):
            The YouTube url to extract the audio file
    """

    def __init__(self, priority: int, url: str):
        self.priority = priority
        self.url = url

    def __lt__(self, other: "AudioFile") -> bool:
        if isinstance(other, AudioFile):
            return self.priority < other.priority
        raise NotImplementedError

    def __gt__(self, other: "AudioFile") -> bool:
        if isinstance(other, AudioFile):
            return self.priority > other.priority
        raise NotImplementedError

    def __eq__(self, other: "AudioFile") -> bool:
        if isinstance(other, AudioFile):
            return self.priority == other.priority and self.url == other.url
        raise NotImplementedError

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url[:27] + "..." if len(self.url) > 30 else self.url


class PlaylistManager:
    """
    This class manages a playlist of audio files.
    """

    # TODO: Add an optional parameter to decide if you want to use a priority queue or normal queue

    def __init__(self, maxlen: Optional[int] = None):
        self._playlist = []
        self._maxlen = maxlen

    def empty(self) -> bool:
        """
        Checks whether the playlist has no audio files stored.

        Returns:
            bool:
                True if the playlist is empty otherwise False
        """
        return len(self) == 0

    def full(self) -> bool:
        """
        Checks whether the playlist has reached the maximum amount of stored audio files.

        Returns:
            bool:
                True if the playlist is full otherwise False
        """
        if self._maxlen is None:
            return False
        else:
            return len(self) == self._maxlen

    def clear(self):
        """
        Removes all stored audio files from the playlist.

        Returns:
            bool:
                True if the playlist is empty otherwise False
        """
        self._playlist = []

    def add(self, audio: AudioFile):
        """
        Adds an audio file to the playlist.

        Args:
            audio (AudioFile):
                The new item to be added

        Raises:
            ValueError:
                If the maximum amount of audio files are already stored
        """
        if self._maxlen is not None and len(self) >= self._maxlen:
            raise ValueError(
                "The playlist has reached the maximum limit of audio sources!"
            )
        heapq.heappush(self._playlist, audio)

    def pop(self) -> AudioFile:
        """
        Removes and returns the next audio file from the playlist.

        Returns:
            AudioFile:
                The next audio file from the playlist
        """
        audio = heapq.heappop(self._playlist)
        return audio

    def remove(self, n: int = 1):
        """
        Removes the next n audio files from the playlist.

        Args:
            n (int):
                The number of next audio files to be removed

        Raises:
            ValueError:
                If n not in (1; len(playlist))
        """
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
