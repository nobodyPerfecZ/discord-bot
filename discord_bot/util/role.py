from discord import Role

# Wrapper from role ids to role names
role_id_to_name = {
    832366646576414780: "DJ",
    542084251038908436: "#ANBU#",
    248898634924425216: "Kage",
    385159915918065664: "Jonin",
    686645319718404100: "Chunin",
    248898155867930624: "Genin",
    560506852127801345: "#Hafensänger#",
    248897274002931722: "@everyone",
}

# Wrapper from role ids to priority values
# Lower values represents higher priorities
role_id_to_priority = {
    832366646576414780: 0,
    542084251038908436: 1,
    248898634924425216: 1,
    385159915918065664: 2,
    686645319718404100: 3,
    248898155867930624: 4,
    560506852127801345: 5,
    248897274002931722: 6,
}


def roles_valid(roles: list[str]) -> bool:
    """Returns True if all roles are valid."""
    return all(role in list(role_id_to_name.values()) for role in roles)


def roles_whitelisted(roles: list[Role], whitelisted_roles: list[str]) -> bool:
    """Returns True if at least one role is in the whitelisted roles."""
    return any(role in whitelisted_roles for role in role_names(roles))


def role_ids(roles: list[Role]) -> list[int]:
    """Returns the ids of the given roles."""
    return [role.id for role in roles]


def role_names(roles: list[Role]) -> list[str | None]:
    """Returns the names of the given roles."""
    return [role_id_to_name.get(role.id, None) for role in roles]


def priorities(roles: list[Role]) -> list[int]:
    """Returns the priority values of the given roles."""
    return [role_id_to_priority.get(role.id, 10) for role in roles]


def lowest_priority(roles: list[Role]) -> int:
    """Returns the lowest priority value (highest value) of the given roles."""
    return max(priorities(roles))


def highest_priority(roles: list[Role]) -> int:
    """Returns the highest priority value (lowest value) of the given roles."""
    return min(priorities(roles))
