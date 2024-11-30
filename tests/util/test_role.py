"""Tests for discord_bot/util/role.py."""

from dataclasses import dataclass

import pytest

from discord_bot.util.role import (
    gpriority,
    greater_equal_role_id,
    greater_role_id,
    less_equal_role_id,
    less_role_id,
    lpriority,
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


__ANBU__ = RoleMock(542084251038908436, "#ANBU#")
__KAGE__ = RoleMock(248898634924425216, "Kage")
__JONIN__ = RoleMock(385159915918065664, "Jonin")
__CHUNIN__ = RoleMock(686645319718404100, "Chunin")
__GENIN__ = RoleMock(248898155867930624, "Genin")
__HAFENSAENGER__ = RoleMock(560506852127801345, "#Hafensänger#")
__EVERYONE__ = RoleMock(248897274002931722, "@everyone")


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        ([__ANBU__], [542084251038908436]),
    ],
)
def test_role_id(roles, expected):
    """Tests the role_id() method."""
    assert role_id(roles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        ([__ANBU__], ["#ANBU#"]),
    ],
)
def test_role_name(roles, expected):
    """Tests the role_name() method."""
    assert role_name(roles) == expected


@pytest.mark.parametrize(
    argnames=["role_ids", "expected"],
    argvalues=[
        ([542084251038908436, 542084251038908436], True),
        ([542084251038908436, 832366646576414782], False),
    ],
)
def test_valid_role_id(role_ids, expected):
    """Tests the valid_role_id() method."""
    assert valid_role_id(role_ids) == expected


@pytest.mark.parametrize(
    argnames=["role_names", "expected"],
    argvalues=[
        (["#ANBU#", "Kage"], True),
        (["#ANBU#", "#ANBU123#"], False),
    ],
)
def test_valid_role_name(role_names, expected):
    """Tests the valid_role_name() method."""
    assert valid_role_name(role_names) == expected


@pytest.mark.parametrize(
    argnames=["roles", "whitelisted_roles", "expected"],
    argvalues=[
        (
            [__ANBU__],
            [542084251038908436, 248898634924425216],
            True,
        ),
        (
            [__JONIN__],
            [542084251038908436, 248898634924425216],
            False,
        ),
    ],
)
def test_whitelisted_role_id(roles, whitelisted_roles, expected):
    """Tests the whitelisted_role_id() method."""
    assert whitelisted_role_id(roles, whitelisted_roles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "whitelisted_roles", "expected"],
    argvalues=[
        (
            [__ANBU__],
            ["#ANBU#", "Kage"],
            True,
        ),
        (
            [__JONIN__],
            ["#ANBU#", "Kage"],
            False,
        ),
    ],
)
def test_whitelisted_role_name(roles, whitelisted_roles, expected):
    """Tests the whitelisted_role_name() method."""
    assert whitelisted_role_name(roles, whitelisted_roles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__KAGE__], [542084251038908436, 248898634924425216], True),
        ([__ANBU__], [542084251038908436, 248898634924425216], False),
    ],
)
def test_greater_equal_role_id(roles, role_ids, expected):
    """Tests the greater_equal_role_id() method."""
    assert greater_equal_role_id(roles, role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__JONIN__], [542084251038908436, 248898634924425216], True),
        ([__KAGE__], [542084251038908436, 248898634924425216], False),
    ],
)
def test_greater_role_id(roles, role_ids, expected):
    """Tests the greater_role_id() method."""
    assert greater_role_id(roles, role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__KAGE__], [248898634924425216, 385159915918065664], True),
        ([__JONIN__], [248898634924425216, 385159915918065664], False),
    ],
)
def test_less_equal_role_id(roles, role_ids, expected):
    """Tests the less_equal_role_id() method."""
    assert less_equal_role_id(roles, role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__ANBU__], [248898634924425216, 385159915918065664], True),
        ([__KAGE__], [248898634924425216, 385159915918065664], False),
    ],
)
def test_less_role_id(roles, role_ids, expected):
    """Tests the less_role_id() method."""
    assert less_role_id(roles, role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        (
            [
                __ANBU__,
                __KAGE__,
                __JONIN__,
                __CHUNIN__,
                __GENIN__,
                __HAFENSAENGER__,
                __EVERYONE__,
            ],
            [0, 1, 2, 3, 4, 5, 6],
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
                __ANBU__,
                __KAGE__,
                __JONIN__,
                __CHUNIN__,
                __GENIN__,
                __HAFENSAENGER__,
                __EVERYONE__,
            ],
            0,
        ),
    ],
)
def test_lpriority(roles, expected):
    """Tests the lpriority() method."""
    assert lpriority(roles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        (
            [
                __ANBU__,
                __KAGE__,
                __JONIN__,
                __CHUNIN__,
                __GENIN__,
                __HAFENSAENGER__,
                __EVERYONE__,
            ],
            6,
        ),
    ],
)
def test_gpriority(roles, expected):
    """Tests the gpriority() method."""
    assert gpriority(roles) == expected
