from discord import Role

# Wrapper from roles to priority value
# Lower values represents higher priorities
roles_to_priority_wrapper = {
    "DJ": 0,
    "#ANBU#": 1,
    "Kage": 1,
    "Jonin": 2,
    "Chunin": 3,
    "Genin": 4,
    "#Hafensänger#": 5,
    "@everyone": 6,
}


def get_priorities(roles: list[Role]) -> list[int]:
    """Returns the priority values of the given roles."""
    return [roles_to_priority_wrapper.get(role, 10) for role in roles]


def get_lowest_priority(roles: list[Role]) -> int:
    """Returns the lowest priority value of the given roles."""
    return max(get_priorities(roles))


def get_highest_priority(roles: list[Role]) -> int:
    """Returns the highest priority value of the given roles."""
    return min(get_priorities(roles))
