"""Tests for discord_bot/util/role.py."""

from dataclasses import dataclass

import pytest

from discord_bot.util import (
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
    priority: int


__ANBU__ = RoleMock(542084251038908436, "#ANBU#", 0)
__KAGE__ = RoleMock(248898634924425216, "Kage", 1)
__JONIN__ = RoleMock(385159915918065664, "Jonin", 2)
__CHUNIN__ = RoleMock(686645319718404100, "Chunin", 3)
__GENIN__ = RoleMock(248898155867930624, "Genin", 4)
__EVERYONE__ = RoleMock(248897274002931722, "@everyone", 5)


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        ([__ANBU__], [__ANBU__.id]),
    ],
)
def test_role_id(roles, expected):
    """Tests the role_id() method."""
    assert role_id(roles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "expected"],
    argvalues=[
        ([__ANBU__], [__ANBU__.name]),
    ],
)
def test_role_name(roles, expected):
    """Tests the role_name() method."""
    assert role_name(roles) == expected


@pytest.mark.parametrize(
    argnames=["role_ids", "expected"],
    argvalues=[
        ([__ANBU__.id, __KAGE__.id], True),
        ([__ANBU__.id, 832366646576414782], False),
    ],
)
def test_valid_role_id(role_ids, expected):
    """Tests the valid_role_id() method."""
    assert valid_role_id(role_ids) == expected


@pytest.mark.parametrize(
    argnames=["role_names", "expected"],
    argvalues=[
        ([__ANBU__.name, __KAGE__.name], True),
        ([__ANBU__.name, "#ANBU123#"], False),
    ],
)
def test_valid_role_name(role_names, expected):
    """Tests the valid_role_name() method."""
    assert valid_role_name(role_names) == expected


@pytest.mark.parametrize(
    argnames=["roles", "wroles", "expected"],
    argvalues=[
        (
            [__ANBU__],
            [__ANBU__.id, __KAGE__.id],
            True,
        ),
        (
            [__JONIN__],
            [__ANBU__.id, __KAGE__.id],
            False,
        ),
    ],
)
def test_whitelisted_role_id(roles, wroles, expected):
    """Tests the whitelisted_role_id() method."""
    assert whitelisted_role_id(roles, wroles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "wroles", "expected"],
    argvalues=[
        (
            [__ANBU__],
            [__ANBU__.name, __KAGE__.name],
            True,
        ),
        (
            [__JONIN__],
            [__ANBU__.name, __KAGE__.name],
            False,
        ),
    ],
)
def test_whitelisted_role_name(roles, wroles, expected):
    """Tests the whitelisted_role_name() method."""
    assert whitelisted_role_name(roles, wroles) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__KAGE__], [__ANBU__.id, __KAGE__.id], True),
        ([__ANBU__], [__ANBU__.id, __KAGE__.id], False),
    ],
)
def test_greater_equal_role_id(roles, role_ids, expected):
    """Tests the greater_equal_role_id() method."""
    assert greater_equal_role_id(roles, role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__JONIN__], [__ANBU__.id, __KAGE__.id], True),
        ([__KAGE__], [__ANBU__.id, __KAGE__.id], False),
    ],
)
def test_greater_role_id(roles, role_ids, expected):
    """Tests the greater_role_id() method."""
    assert greater_role_id(roles, role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__KAGE__], [__KAGE__.id, __JONIN__.id], True),
        ([__JONIN__], [__KAGE__.id, __JONIN__.id], False),
    ],
)
def test_less_equal_role_id(roles, role_ids, expected):
    """Tests the less_equal_role_id() method."""
    assert less_equal_role_id(roles, role_ids) == expected


@pytest.mark.parametrize(
    argnames=["roles", "role_ids", "expected"],
    argvalues=[
        ([__ANBU__], [__KAGE__.id, __JONIN__.id], True),
        ([__KAGE__], [__KAGE__.id, __JONIN__.id], False),
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
                __EVERYONE__,
            ],
            [
                __ANBU__.priority,
                __KAGE__.priority,
                __JONIN__.priority,
                __CHUNIN__.priority,
                __GENIN__.priority,
                __EVERYONE__.priority,
            ],
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
                __EVERYONE__,
            ],
            __ANBU__.priority,
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
                __EVERYONE__,
            ],
            __EVERYONE__.priority,
        ),
    ],
)
def test_gpriority(roles, expected):
    """Tests the gpriority() method."""
    assert gpriority(roles) == expected
