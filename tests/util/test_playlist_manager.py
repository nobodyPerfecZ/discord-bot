import unittest

from discord_bot.util import AudioFile, PlaylistManager


class TestPlaylistManager(unittest.TestCase):
    """Tests the class PlaylistManager."""

    def setUp(self):
        self.maxlen = 10
        self.playlist = PlaylistManager(maxlen=self.maxlen)
        self.audio = AudioFile(
            priority=1, url="https://www.youtube.com/watch?v=BaW_jenozKc"
        )

    def test_empty(self):
        """Tests the method empty()."""
        # Check if the playlist is empty
        self.assertTrue(self.playlist.empty())

        # Fill in the playlist with one value
        self.playlist.add(self.audio)

        # Check if the playlist is not empty
        self.assertFalse(self.playlist.empty())

    def test_full(self):
        """Tests the method full()."""
        # Check if the playlist is not full
        self.assertFalse(self.playlist.full())

        # Fill in the playlist to the maximum allowed size
        for _ in range(self.maxlen):
            self.playlist.add(self.audio)

        # Check if the playlist is full
        self.assertTrue(self.playlist.full())

    def test_clear(self):
        """Tests the method clear()."""
        # Fill in the playlist to the maximum allowed size
        for _ in range(self.maxlen):
            self.playlist.add(self.audio)

        # Clear the playlist
        self.playlist.clear()

        # Check if the playlist has no audios stored
        self.assertEqual(0, len(self.playlist))

    def test_add(self):
        """Tests the method add()."""
        self.playlist.add(self.audio)

        # Check some properties
        self.assertEqual(1, len(self.playlist))
        self.assertEqual(self.audio, self.playlist.pop())

    def test_pop(self):
        """Tests the method pop() with return_stream=False."""
        for _ in range(self.maxlen):
            self.playlist.add(self.audio)

        audio = self.playlist.pop()

        self.assertEqual(self.audio, audio)

    def test_remove(self):
        """Tests the method remove()."""
        for _ in range(self.maxlen):
            self.playlist.add(self.audio)

        self.playlist.remove(n=self.maxlen)

        self.assertEqual(0, len(self.playlist))


if __name__ == "__main__":
    unittest.main()
