# Wrapper from roles to priority value (lower values represents higher priorities).
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


def to_priority(role: str, default: int = 10) -> int:
    """
    Returns the priority given the discord role.

    The default value is returned if the discord role does not exist.

    Args:
        role (str):
            The role of the discord server

        default (int):
            The default priority if the role does not exist

    Returns:
        int:
            The priority to the given discord role
    """
    return roles_to_priority_wrapper.get(role, default)
