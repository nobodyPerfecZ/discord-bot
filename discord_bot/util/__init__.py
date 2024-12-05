from .role import (
    __DEFAULT_ROLE__,
    __ROLES__,
    __ROLES_PERMISSIONS__,
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
from .text_channel import (
    __TEXT_CHANNELS__,
    __TEXT_CHANNELS_PERMISSIONS__,
    text_channel_id,
    text_channel_name,
    valid_text_channel_id,
    valid_text_channel_name,
    whitelisted_text_channel_id,
    whitelisted_text_channel_name,
)

del role  # type: ignore[name-defined] # noqa: F821
del text_channel  # type: ignore[name-defined] # noqa: F821


__all__ = [
    "__DEFAULT_ROLE__",
    "__ROLES_PERMISSIONS__",
    "__ROLES__",
    "__TEXT_CHANNELS_PERMISSIONS__",
    "__TEXT_CHANNELS__",
    "gpriority",
    "greater_equal_role_id",
    "greater_role_id",
    "less_equal_role_id",
    "less_role_id",
    "lpriority",
    "priority",
    "role_id",
    "role_name",
    "text_channel_id",
    "text_channel_name",
    "valid_role_id",
    "valid_role_name",
    "valid_text_channel_id",
    "valid_text_channel_name",
    "whitelisted_role_id",
    "whitelisted_role_name",
    "whitelisted_text_channel_id",
    "whitelisted_text_channel_name",
]


assert __all__ == sorted(__all__)
