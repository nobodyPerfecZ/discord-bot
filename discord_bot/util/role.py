"""Utility functions for roles."""

from discord import Role


__ROLES__ = {
    542084251038908436: ("#ANBU#", 0),
    248898634924425216: ("Kage", 1),
    385159915918065664: ("Jonin", 2),
    686645319718404100: ("Chunin", 3),
    248898155867930624: ("Genin", 4),
    560506852127801345: ("#Hafensänger#", 5),
    248897274002931722: ("@everyone", 6),
}


__DEFAULT_ROLE__ = (None, max(priority for _, priority in __ROLES__.values()) + 1)


def role_id(roles: list[Role]) -> list[int]:
    """Returns the ids of the given roles."""
    return list(map(lambda role: role.id, roles))


def role_name(roles: list[Role]) -> list[str]:
    """Returns the names of the given roles."""
    return list(map(lambda role: role.name, roles))


def valid_role_id(role_ids: list[int]) -> bool:
    """Returns True if the role ids are valid roles."""
    return all(role_id in __ROLES__ for role_id in role_ids)


def valid_role_name(role_names: list[str]) -> bool:
    """Returns True if the role names are valid roles."""
    valid_role_names = [role for role, _ in __ROLES__.values()]
    return all(role_name in valid_role_names for role_name in role_names)


def whitelisted_role_id(
    roles: list[Role],
    whitelisted_roles: list[int],
) -> bool:
    """Returns True if the role is in the list of whitelisted roles."""
    return any(role in whitelisted_roles for role in role_id(roles))


def whitelisted_role_name(
    roles: list[Role],
    whitelisted_roles: list[str],
) -> bool:
    """Returns True if the role is in the list of whitelisted roles."""
    return any(role in whitelisted_roles for role in role_name(roles))


def greater_equal_role_id(roles: list[Role], role_ids: list[int]) -> bool:
    """Returns True if the priority of the given roles is higher than or equal to the given roles."""
    return all(
        lpriority(roles) >= __ROLES__.get(role_id, __DEFAULT_ROLE__)[1]
        for role_id in role_ids
    )


def greater_role_id(roles: list[Role], role_ids: list[int]) -> bool:
    """Returns True if the priority of the given roles is higher than the given roles."""
    return all(
        lpriority(roles) > __ROLES__.get(role_id, __DEFAULT_ROLE__)[1]
        for role_id in role_ids
    )


def less_equal_role_id(roles: list[Role], role_ids: list[int]) -> bool:
    """Returns True if the priority of the given roles is lower than or equal to the given roles."""
    return all(
        lpriority(roles) <= __ROLES__.get(role_id, __DEFAULT_ROLE__)[1]
        for role_id in role_ids
    )


def less_role_id(roles: list[Role], role_ids: list[int]) -> bool:
    """Returns True if the priority of the given roles is lower than the given roles."""
    return all(
        lpriority(roles) < __ROLES__.get(role_id, __DEFAULT_ROLE__)[1]
        for role_id in role_ids
    )


def priority(roles: list[Role]) -> list[int]:
    """Returns the priority value of the given roles."""
    return [__ROLES__.get(role.id, __DEFAULT_ROLE__)[1] for role in roles]


def lpriority(roles: list[Role]) -> int:
    """Returns the lowest priority value of the given roles."""
    return min(priority(roles))


def gpriority(roles: list[Role]) -> int:
    """Returns the highest priority value of the given roles."""
    return max(priority(roles))
