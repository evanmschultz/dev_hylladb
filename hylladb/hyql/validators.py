from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Literal, LiteralString, Type, Union

if TYPE_CHECKING:
    from hylladb.hyql.hyql import ConditionDict, Group

import hylladb.hyql.hyql_utilities as hyql_utils
from hylladb.hyql.enums import Operators


def validate_group_format(
    value: list[Union[ConditionDict, Group, str]],
    class_types: list[Union[Type[ConditionDict], Type[Group]]],
) -> list[Union[ConditionDict, Group, str]]:
    """Validates the format of the group list."""

    def _validate_is_list(value) -> None:
        """Ensure the value is a list."""
        if not isinstance(value, list):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                "The value of a group must be a list of conditions, groups, or logical operators. Example format: ['condition', 'AND', 'group']\n"
            )

    def _validate_not_empty(value: list) -> None:
        """Ensure the list is not empty."""
        if len(value) == 0:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                "The value of a group cannot be an empty list.\n"
            )

    _validate_is_list(value)
    _validate_not_empty(value)

    def _validate_logical_operator(item: str, index: int, value: list) -> None:
        """Validate the logical operator in the list."""
        if item not in ["AND", "OR"]:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"Invalid operator '{item}'. Allowed operators for groups: 'AND' | 'OR'.\n"
            )
        if index == 0 or index == len(value) - 1:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                "Logical operators must be between conditions or groups, not at the ends.\n"
            )

    def _validate_item_type(item: Any, index: int) -> None:
        """Validate the type of the item in the list."""
        if not any(isinstance(item, class_type) for class_type in class_types):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"Invalid item type at position {index}. Expected ConditionDict, Group, or a logical operator string.\n"
            )

    def _validate_consecutive_types(
        index: int, value: Any, previous_value: Any
    ) -> None:
        """Ensure that logical operators are not consecutive."""
        if index > 0 and isinstance(value, str) == isinstance(previous_value, str):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                "Invalid Group format. Conditions or Groups must be separated by logical operators 'AND' | 'OR'. "
                "Input has two consecutive type in a row.\n"
            )

    for i, item in enumerate(value):
        if isinstance(item, str):
            _validate_logical_operator(item, i, value)
        else:
            _validate_item_type(item, i)

        _validate_consecutive_types(i, item, value[i - 1])

    return value


def validate_operator(value: str) -> str:
    """Validates the operator."""
    if not hyql_utils.operator_validator(value):
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            f"Invalid operator '{value}'. Allowed operators: {', '.join(op.value for op in Operators)}\n"
        )
    return value


def validate_paths(data: Any) -> None:
    """Validates the paths."""
    pattern: LiteralString = hyql_utils.path_dict["pattern"]

    if not isinstance(getattr(data, "left"), str) or not re.match(
        pattern, str(getattr(data, "left"))
    ):
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            "The `left` value must be a valid path string for HyllaDB."
            " Example format: 'section.shelf.dict_key'.\n"
        )
    if getattr(data, "right_is_path"):
        if not isinstance(getattr(data, "right"), str) or not re.match(
            pattern, str(getattr(data, "right"))
        ):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                "When the `right_is_path` flag is set to True, the `right` value must be a valid path string for HyllaDB."
                " Example format: 'section.shelf.dict_key'.\n"
            )
    return data


def validate_checkout_format(value: list[str]) -> list[str]:
    """Validates the format of the checkout list."""

    if len(value) == 0:
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            "The value of a checkout item cannot be an empty list.\n"
        )

    for i, item in enumerate(value):
        if item == "*all":
            if len(value) > 1:
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"Invalid item type at position {i}. '*all' must be the only item in the list.\n"
                )
        else:
            if not re.match(hyql_utils.path_pattern, item):
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"Invalid item type at position {i}. Expected a valid path string, eg. eg. `key_1`.\n"
                )
    return value


def ensure_path_is_none_if_is_library(data) -> Any:
    """Ensures that the path is None if the schema is for a library."""

    if data.is_library and data.path:
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            "The `path` field must be None if `is_library` is True.\n"
        )


def validate_only_one_bool_is_true(
    data: Any,
    bool_keys: (
        tuple[Literal["remove_shelf"], Literal["remove_section"]]
        | tuple[Literal["reset_shelf"], Literal["reset_section"]]
    ),
) -> None:
    """Ensures that only one of the boolean fields is True."""
    if sum(getattr(data, key) for key in bool_keys) > 1:
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            f"Only one of {', '.join(bool_keys)} can be True.\n"
        )
