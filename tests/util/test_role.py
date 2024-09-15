import unittest
from unittest.mock import MagicMock

from discord_bot.util.role import (
    highest_priority,
    lowest_priority,
    priorities,
    role_ids,
    role_names,
    roles_valid,
    roles_whitelisted,
)


class TestRole(unittest.TestCase):
    """Tests all methods under role.py."""

    def setUp(self):
        self.roles1 = [
            MagicMock(id=832366646576414780),
            MagicMock(id=542084251038908436),
            MagicMock(id=248898634924425216),
            MagicMock(id=385159915918065664),
            MagicMock(id=686645319718404100),
            MagicMock(id=248898155867930624),
            MagicMock(id=560506852127801345),
            MagicMock(id=248897274002931722),
        ]
        self.roles2 = [
            MagicMock(id=385159915918065664),
            MagicMock(id=686645319718404100),
            MagicMock(id=248898155867930624),
            MagicMock(id=560506852127801345),
            MagicMock(id=248897274002931722),
        ]

        self.whitelisted_roles1 = ["DJ", "#ANBU#", "Kage"]
        self.whitelisted_roles2 = ["DJ", "#ANBU#", "Test123"]

    def test_roles_valid(self):
        """Tests the roles_valid() method."""
        self.assertTrue(roles_valid(self.whitelisted_roles1))
        self.assertFalse(roles_valid(self.whitelisted_roles2))

    def test_roles_whitelisted(self):
        """Tests the roles_whitelisted() method."""
        self.assertTrue(roles_whitelisted(self.roles1, self.whitelisted_roles1))
        self.assertFalse(roles_whitelisted(self.roles2, self.whitelisted_roles1))

    def test_role_ids(self):
        """Tests the role_ids() method."""
        self.assertEqual(
            [
                832366646576414780,
                542084251038908436,
                248898634924425216,
                385159915918065664,
                686645319718404100,
                248898155867930624,
                560506852127801345,
                248897274002931722,
            ],
            role_ids(self.roles1),
        )
        self.assertEqual(
            [
                385159915918065664,
                686645319718404100,
                248898155867930624,
                560506852127801345,
                248897274002931722,
            ],
            role_ids(self.roles2),
        )

    def test_role_names(self):
        """Tests the role_names() method."""
        self.assertEqual(
            [
                "DJ",
                "#ANBU#",
                "Kage",
                "Jonin",
                "Chunin",
                "Genin",
                "#Hafensänger#",
                "@everyone",
            ],
            role_names(self.roles1),
        )

        self.assertEqual(
            [
                "Jonin",
                "Chunin",
                "Genin",
                "#Hafensänger#",
                "@everyone",
            ],
            role_names(self.roles2),
        )

    def test_priorities(self):
        """Tests the priorities() method."""
        self.assertEqual(
            [0, 1, 1, 2, 3, 4, 5, 6],
            priorities(self.roles1),
        )

        self.assertEqual(
            [2, 3, 4, 5, 6],
            priorities(self.roles2),
        )

    def test_lowest_priority(self):
        """Tests the lowest_priority() method."""
        self.assertEqual(6, lowest_priority(self.roles1))
        self.assertEqual(6, lowest_priority(self.roles2))

    def test_highest_priority(self):
        """Tests the highest_priority() method."""
        self.assertEqual(0, highest_priority(self.roles1))
        self.assertEqual(2, highest_priority(self.roles2))


if __name__ == "__main__":
    unittest.main()
