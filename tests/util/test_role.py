"""Tests for discord_bot/util/role.py."""

from dataclasses import dataclass

import pytest

from discord_bot.util.role import (
    highest_priority,
    lowest_priority,
    priority,
    role_id,
    role_name,
    valid_role_id,
    valid_role_name,
    whitelisted_role_id,
    whitelisted_role_name,
)


@dataclass
class RoleMock:
    """Mock class for Role."""

    id: int
    name: str


@pytest.mark.parametrize(
    argnames="role",
    argvalues=[
        RoleMock(832366646576414780, "DJ"),
    ],
)
def test_role_id(role):
    """Tests the role_id() method."""
    assert role_id(role) == role.id


@pytest.mark.parametrize(
    argnames="role",
    argvalues=[
        RoleMock(832366646576414780, "DJ"),
    ],
)
def test_role_name(role):
    """Tests the role_name() method."""
    assert role_name(role) == role.name


@pytest.mark.parametrize(
    argnames=["role_ids", "expected"],
    argvalues=[
        ([832366646576414780, 542084251038908436], True),
        ([832366646576414780, 832366646576414782], False),
    ],
)
def test_valid_role_id(role_ids, expected):
    """Tests the valid_role_id() method."""
    assert valid_role_id(role_ids) == expected


@pytest.mark.parametrize(
    argnames=["role_names", "expected"],
    argvalues=[
        (["DJ", "#ANBU#"], True),
        (["DJ", "DJ123"], False),
    ],
)
def test_valid_role_name(role_names, expected):
    """Tests the valid_role_name() method."""
    assert valid_role_name(role_names) == expected


@pytest.mark.parametrize(
    argnames=["roles", "whitelisted_role_ids", "expected"],
    argvalues=[
        (
            [RoleMock(832366646576414780, "DJ")],
            [832366646576414780, 542084251038908436],
            True,
        ),
        (
            [RoleMock(248898634924425216, "Kage")],
            [832366646576414780, 542084251038908436],
            False,
        ),
    ],
)
def test_whitelisted_role_id(roles, whitelisted_role_ids, expected):
    """Tests the whitelisted_role_id() method."""
    assert whitelisted_role_id(roles, whitelisted_role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "whitelisted_role_names", "expected"],
    argvalues=[
        (
            [RoleMock(832366646576414780, "DJ")],
            ["DJ", "#ANBU#"],
            True,
        ),
        (
            [RoleMock(248898634924425216, "Kage")],
            ["DJ", "#ANBU#"],
            False,
        ),
    ],
)
def test_whitelisted_role_name(roles, whitelisted_role_names, expected):
    """Tests the whitelisted_role_name() method."""
    assert whitelisted_role_name(roles, whitelisted_role_names) == expected


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        (
            [
                RoleMock(832366646576414780, "DJ"),
                RoleMock(542084251038908436, "#ANBU#"),
                RoleMock(248898634924425216, "Kage"),
                RoleMock(385159915918065664, "Jonin"),
                RoleMock(686645319718404100, "Chunin"),
                RoleMock(248898155867930624, "Genin"),
                RoleMock(560506852127801345, "#Hafensänger#"),
                RoleMock(248897274002931722, "@everyone"),
            ],
            [0, 1, 1, 2, 3, 4, 5, 6],
        ),
    ],
)
def test_priority(roles, expected):
    """Tests the priority() method."""
    assert priority(roles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        (
            [
                RoleMock(832366646576414780, "DJ"),
                RoleMock(542084251038908436, "#ANBU#"),
                RoleMock(248898634924425216, "Kage"),
                RoleMock(385159915918065664, "Jonin"),
                RoleMock(686645319718404100, "Chunin"),
                RoleMock(248898155867930624, "Genin"),
                RoleMock(560506852127801345, "#Hafensänger#"),
                RoleMock(248897274002931722, "@everyone"),
            ],
            0,
        ),
    ],
)
def test_lowest_priority(roles, expected):
    """Tests the lowest_priority() method."""
    assert lowest_priority(roles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        (
            [
                RoleMock(832366646576414780, "DJ"),
                RoleMock(542084251038908436, "#ANBU#"),
                RoleMock(248898634924425216, "Kage"),
                RoleMock(385159915918065664, "Jonin"),
                RoleMock(686645319718404100, "Chunin"),
                RoleMock(248898155867930624, "Genin"),
                RoleMock(560506852127801345, "#Hafensänger#"),
                RoleMock(248897274002931722, "@everyone"),
            ],
            6,
        ),
    ],
)
def test_highest_priority(roles, expected):
    """Tests the highest_priority() method."""
    assert highest_priority(roles) == expected
