import unittest

from discord_bot.util import to_priority


class TestRole(unittest.TestCase):
    """Tests all methods under role.py."""

    def test_to_priority(self):
        """Tests the __init__() method."""
        priority1 = to_priority("DJ", default=10)
        priority2 = to_priority("#ANBU#", default=10)
        priority3 = to_priority("Kage", default=10)
        priority4 = to_priority("Jonin", default=10)
        priority5 = to_priority("Chunin", default=10)
        priority6 = to_priority("Genin", default=10)
        priority7 = to_priority("#Hafensänger#", default=10)
        priority8 = to_priority("@everyone", default=10)
        priority9 = to_priority("Test123", default=10)

        self.assertEqual(0, priority1)
        self.assertEqual(1, priority2)
        self.assertEqual(1, priority3)
        self.assertEqual(2, priority4)
        self.assertEqual(3, priority5)
        self.assertEqual(4, priority6)
        self.assertEqual(5, priority7)
        self.assertEqual(6, priority8)
        self.assertEqual(10, priority9)


if __name__ == "__main__":
    unittest.main()
