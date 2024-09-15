import unittest
from unittest.mock import MagicMock

from discord_bot.util.channel import channel_name, channel_whitelisted, channels_valid


class TestChannel(unittest.TestCase):
    """Tests all methods under channel.py."""

    def setUp(self):
        self.channel1 = MagicMock(id=248897274002931722)
        self.channel2 = MagicMock(id=725622500846993530)

        self.whitelisted_channels1 = ["music🎼", "bottest"]
        self.whitelisted_channels2 = ["music🎼", "Test123"]

    def test_channels_valid(self):
        """Tests the channels_valid() method."""
        self.assertTrue(channels_valid(self.whitelisted_channels1))
        self.assertFalse(channels_valid(self.whitelisted_channels2))

    def test_channel_whitelisted(self):
        """Tests the channel_whitelisted() method."""
        self.assertFalse(channel_whitelisted(self.channel1, self.whitelisted_channels1))
        self.assertTrue(channel_whitelisted(self.channel2, self.whitelisted_channels1))

    def test_channel_name(self):
        """Tests the channel_name() method."""
        self.assertEqual("chat☕", channel_name(self.channel1))
        self.assertEqual("music🎼", channel_name(self.channel2))


if __name__ == "__main__":
    unittest.main()
