import re
from typing import Any

import pytest
from pydantic import ValidationError

from hylladb.hyql.enums import Operators
from hylladb.hyql.hyql import Condition, ConditionDict, Group
from hylladb.hyql.validators import (
    ensure_path_is_none_if_is_library,
    validate_checkout_format,
    validate_group_format,
    validate_only_one_bool_is_true,
    validate_operator,
    validate_paths,
)


# validate_group_format Tests
def test_validate_group_format_valid() -> None:
    """Test validate_group_format with valid input."""
    condition_dict = ConditionDict(
        condition=Condition(left="path1.field1", operator=">", right=100)
    )
    group = Group(group=[condition_dict, "OR", condition_dict])
    result = validate_group_format(
        [condition_dict, "AND", group], [ConditionDict, Group]
    )
    assert result == [condition_dict, "AND", group]


def test_validate_group_format_invalid_operator() -> None:
    """Test validate_group_format with invalid operator."""
    condition_dict = ConditionDict(
        condition=Condition(left="path1.field1", operator=">", right=100)
    )
    with pytest.raises(ValueError):
        validate_group_format(
            [condition_dict, "INVALID_OPERATOR", condition_dict], [ConditionDict, Group]
        )


def test_validate_group_format_consecutive_operators() -> None:
    """Test validate_group_format with consecutive operators."""
    condition_dict = ConditionDict(
        condition=Condition(left="path1.field1", operator=">", right=100)
    )
    with pytest.raises(ValueError):
        validate_group_format([condition_dict, "AND", "OR"], [ConditionDict, Group])


def test_validate_group_format_empty_list() -> None:
    """Test validate_group_format with empty list."""
    with pytest.raises(ValueError):
        validate_group_format([], [ConditionDict, Group])


# validate_operator Tests
def test_validate_operator_valid_return() -> None:
    """Test that validate_operator returns the input when valid."""
    assert validate_operator(">") == ">"
    assert validate_operator("<") == "<"


def test_validate_operator_error_message() -> None:
    """Test the error message content for invalid input."""
    invalid_operator = "INVALID_OPERATOR"
    expected_error_message = (
        "\n    HyllaDB Error:\n"
        "        ---->"
        f"Invalid operator '{invalid_operator}'. Allowed operators: {', '.join(op.value for op in Operators)}\n"
    )
    with pytest.raises(ValueError, match=re.escape(expected_error_message)):
        validate_operator(invalid_operator)


def test_validate_operator_all_valid_operators() -> None:
    """Test validate_operator with all valid operators."""
    for op in Operators:
        assert validate_operator(op.value) == op.value


# validate_paths Tests
def test_validate_paths_valid() -> None:
    """Test validate_paths with valid paths."""
    condition = Condition(
        left="section.shelf.dict_key",
        operator=">",
        right="section.shelf.dict_key",
        right_is_path=True,
    )
    assert validate_paths(condition) == condition


# validate_checkout_format Tests
def test_validate_checkout_format_valid() -> None:
    """Test validate_checkout_format with valid input."""
    assert validate_checkout_format(["shelf_1.field1", "shelf_1.field2"]) == [
        "shelf_1.field1",
        "shelf_1.field2",
    ]


def test_validate_checkout_format_empty_list() -> None:
    """Test validate_checkout_format with empty list."""
    with pytest.raises(ValueError):
        validate_checkout_format([])


def test_validate_checkout_format_invalid_item() -> None:
    """Test validate_checkout_format with invalid item."""
    with pytest.raises(ValueError):
        validate_checkout_format(["invalid item"])


def test_validate_checkout_format_all_not_alone() -> None:
    """Test validate_checkout_format with '*all' not alone in list."""
    with pytest.raises(ValueError):
        validate_checkout_format(["*all", "shelf_1.field1"])


# ensure_path_is_none_if_is_library Tests
class MockData:
    def __init__(self, is_library: bool, path: str | None) -> None:
        self.is_library: bool = is_library
        self.path: str | None = path


def test_ensure_path_is_none_if_is_library_valid() -> None:
    """Test ensure_path_is_none_if_is_library with valid input."""
    data = MockData(is_library=True, path=None)
    assert ensure_path_is_none_if_is_library(data) is None


def test_ensure_path_is_none_if_is_library_invalid() -> None:
    """Test ensure_path_is_none_if_is_library with invalid input."""
    data = MockData(is_library=True, path="section.shelf")
    with pytest.raises(ValueError):
        ensure_path_is_none_if_is_library(data)


# validate_only_one_bool_is_true Tests
class MockBoolData:
    def __init__(self, remove_shelf: bool, remove_section: bool) -> None:
        self.remove_shelf: bool = remove_shelf
        self.remove_section: bool = remove_section


def test_validate_only_one_bool_is_true_valid() -> None:
    """Test validate_only_one_bool_is_true with valid input."""
    data = MockBoolData(remove_shelf=True, remove_section=False)
    assert (
        validate_only_one_bool_is_true(data, ("remove_shelf", "remove_section")) is None
    )


def test_validate_only_one_bool_is_true_both_true() -> None:
    """Test validate_only_one_bool_is_true with both booleans true."""
    data = MockBoolData(remove_shelf=True, remove_section=True)
    with pytest.raises(ValueError):
        validate_only_one_bool_is_true(data, ("remove_shelf", "remove_section"))
