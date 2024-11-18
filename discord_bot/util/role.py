"""Utility functions for roles."""

from discord import Role


__ROLES__ = {
    832366646576414780: ("DJ", 0),
    542084251038908436: ("#ANBU#", 1),
    248898634924425216: ("Kage", 1),
    385159915918065664: ("Jonin", 2),
    686645319718404100: ("Chunin", 3),
    248898155867930624: ("Genin", 4),
    560506852127801345: ("#Hafensänger#", 5),
    248897274002931722: ("@everyone", 6),
}


def role_id(role: Role) -> int:
    """Returns the id of the given role."""
    return role.id


def role_name(role: Role) -> str:
    """Returns the name of the given role."""
    return role.name


def valid_role_id(role_ids: list[int]) -> bool:
    """Returns True if the role ids are valid roles."""
    return all(role_id in __ROLES__ for role_id in role_ids)


def valid_role_name(role_names: list[str]) -> bool:
    """Returns True if the role names are valid roles."""
    return all(
        any(role_name == role for role, _ in __ROLES__.values())
        for role_name in role_names
    )


def whitelisted_role_id(
    roles: list[Role],
    whitelisted_role_ids: list[int],
) -> bool:
    """Returns True if the role is in the list of whitelisted roles."""
    return any(
        valid_role_id(whitelisted_role_ids) and role_id(role) in whitelisted_role_ids
        for role in roles
    )


def whitelisted_role_name(
    roles: list[Role],
    whitelisted_role_names: list[str],
) -> bool:
    """Returns True if the role is in the list of whitelisted roles."""
    return any(
        valid_role_name(whitelisted_role_names)
        and role_name(role) in whitelisted_role_names
        for role in roles
    )


def priority(roles: list[Role]) -> int | list[int]:
    """Returns the priority value of the given role."""
    return [__ROLES__.get(role.id, (None, 10))[1] for role in roles]


def lowest_priority(roles: list[Role]) -> int:
    """Returns the lowest priority value of the given roles."""
    return min(priority(roles))


def highest_priority(roles: list[Role]) -> int:
    """Returns the highest priority value of the given roles."""
    return max(priority(roles))
