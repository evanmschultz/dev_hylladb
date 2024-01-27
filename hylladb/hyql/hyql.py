import re
from enum import Enum
from typing import Any, Literal, LiteralString, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    field_validator,
    model_validator,
)


class BasicComparison(str, Enum):
    """
    This Enum defines the basic comparison operators used in HyQL.

    It provides a set of operators specifically designed for basic comparison within query conditions and is meant to be
    used as a guide when you are uncertain of the operator syntax of HyQL.

    Members:
        `EQUAL` (str): Represents the '==' operator for equality.
        `NOT_EQUAL` (str): Represents the '!=' operator for inequality.
        `GREATER_THAN` (str): Represents the '>' operator for greater than comparisons.
        `LESS_THAN` (str): Represents the '<' operator for less than comparisons.
        `GREATER_THAN_OR_EQUAL` (str): Represents the '>=' operator for greater than or equal to comparisons.
        `LESS_THAN_OR_EQUAL` (str): Represents the '<=' operator for less than or equal to comparisons.
    """

    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="


class StringOperators(str, Enum):
    """
    This Enum classifies string-based operators for use in HyQL queries.

    It provides a set of operators specifically designed for string comparison and manipulation within query conditions
    and is meant to be used as a guide when you are uncertain of the operator syntax of HyQL.

    Members:
        `CONTAINS` (str): Checks if a given substring is present within a string.
        `STARTS_WITH` (str): Evaluates if a string starts with a specified substring.
        `ENDS_WITH` (str): Determines if a string ends with a certain substring.
        `MATCHES` (str): Used for regex pattern matching within a string.
    """

    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"


class CollectionOperators(str, Enum):
    """
    This Enum identifies operators specific to collection-based queries in HyQL.

    These operators are useful for performing various operations on collections like lists, sets, and dictionaries within
    HyQL conditions. They are designed to enhance the flexibility and capability of collection handling in queries.

    Members:
        `IN` (str): Checks if an element is present within a collection.
        `NOT_IN` (str): Determines if an element is not part of a collection.
        `ANY` (str): Returns true if any element in a collection meets a certain condition.
        `ALL` (str): Ensures that all elements in a collection satisfy a specified condition.
        `NONE` (str): Verifies that no elements in a collection match a given condition.
        `LENGTH_EQUAL` (str): Compares if the length of a collection is equal to a specific value.
        `LENGTH_GREATER_THAN` (str): Checks if the length of a collection is greater than a certain value.
        `LENGTH_LESS_THAN` (str): Assesses if the length of a collection is less than a specified value.
    """

    IN = "in"
    NOT_IN = "not in"
    ANY = "any"
    ALL = "all"
    NONE = "none"
    LENGTH_EQUAL = "length_eq"
    LENGTH_GREATER_THAN = "length_gt"
    LENGTH_LESS_THAN = "length_lt"


class LogicalOperators(str, Enum):
    """
    This Enum categorizes logical operators used in HyQL to combine or invert conditions.

    Logical operators are fundamental in constructing complex logical expressions in query conditions, allowing for more nuanced and precise data retrieval.

    Members:
        `AND` (str): Logical AND operator, used to ensure all combined conditions are true.
        `OR` (str): Logical OR operator, used when any of the combined conditions being true is sufficient.
        `NOT` (str): Logical NOT operator, used to invert the result of a condition.
    """

    AND = "and"
    OR = "or"
    NOT = "not"


class IdentityTypeOperators(str, Enum):
    """
    This Enum contains operators for identity and type checks in HyQL.

    These operators are particularly useful for type validation and identity comparison, enhancing the robustness and specificity of query conditions.

    Members:
        `IS` (str): Checks if two references point to the same object.
        `IS_NOT` (str): Determines if two references do not point to the same object.
        `IS_INSTANCE` (str): Verifies if an object is an instance of a specified class or type.
    """

    IS = "is"
    IS_NOT = "is not"
    IS_INSTANCE = "isinstance"


# class BitwiseOperators(str, Enum):
#     BITWISE_AND = "&"
#     BITWISE_OR = "|"
#     BITWISE_XOR = "^"
#     BITWISE_NOT = "~"


class NumericOperators(str, Enum):
    """
    This Enum represents operators tailored for numeric comparisons in HyQL.

    They are essential for performing more intricate numeric condition checks, such as comparing absolute values, within HyQL queries.

    Members:
        `ABS_EQUAL` (str): Checks if the absolute value of a number is equal to a given value.
        `ABS_GREATER_THAN` (str): Compares if the absolute value of a number is greater than a specified value.
        `ABS_LESS_THAN` (str): Determines if the absolute value of a number is less than a certain value.
    """

    ABS_EQUAL = "abs_eq"
    ABS_GREATER_THAN = "abs_gt"
    ABS_LESS_THAN = "abs_lt"


class DateTimeOperators(str, Enum):
    """
    This Enum encapsulates operators for date and time comparisons in HyQL.

    These operators are vital for queries that involve date and time criteria, allowing precise temporal data filtering and comparison.

    Members:
        `DATE_EQUAL` (str): Checks if a date is exactly equal to a specified date.
        `DATE_BEFORE` (str): Determines if a date occurs before a given date.
        `DATE_AFTER` (str): Assesses if a date happens after a certain date.
        `DATE_WITHIN` (str): Verifies if a date falls within a specified time frame.
    """

    DATE_EQUAL = "date_eq"
    DATE_BEFORE = "date_before"
    DATE_AFTER = "date_after"
    DATE_WITHIN = "date_within"


class LogicOperators(str, Enum):
    """
    This Enum class provides a comprehensive collection of operators used in HyQL for various types of comparisons and
    logical operations. It integrates basic comparison, string manipulation, collection handling, logical, identity
    type, numeric, and date-time operators.

    It is meant to be used as a guide when you are uncertain of the operator syntax of HyQL. If you want easier access to
    operators of a specific type, you can import the following Enums: `BasicComparison`, `StringOperators`,
    `CollectionOperators`, `LogicalOperators`, `IdentityTypeOperators`, `NumericOperators`, and `DateTimeOperators`.

    Members:
        # Basic Comparison Operators
        `EQUAL` (str): Represents the '==' operator for equality comparison.
        `NOT_EQUAL` (str): Represents the '!=' operator for inequality comparison.
        `GREATER_THAN` (str): Represents the '>' operator for greater than comparisons.
        `LESS_THAN` (str): Represents the '<' operator for less than comparisons.
        `GREATER_THAN_OR_EQUAL` (str): Represents the '>=' operator for greater than or equal to comparisons.
        `LESS_THAN_OR_EQUAL` (str): Represents the '<=' operator for less than or equal to comparisons.

        # String Operators
        `CONTAINS` (str): Checks if a given substring is present within a string.
        `STARTS_WITH` (str): Evaluates if a string starts with a specified substring.
        `ENDS_WITH` (str): Determines if a string ends with a certain substring.
        `MATCHES` (str): Used for regex pattern matching within a string.

        # Collection Operators
        `IN` (str): Checks if an element is present within a collection.
        `NOT_IN` (str): Determines if an element is not part of a collection.
        `ANY` (str): Returns true if any element in a collection meets a certain condition.
        `ALL` (str): Ensures that all elements in a collection satisfy a specified condition.
        `NONE` (str): Verifies that no elements in a collection match a given condition.
        `LENGTH_EQUAL` (str): Compares if the length of a collection is equal to a specific value.
        `LENGTH_GREATER_THAN` (str): Checks if the length of a collection is greater than a certain value.
        `LENGTH_LESS_THAN` (str): Assesses if the length of a collection is less than a specified value.

        # Logical Operators
        `AND` (str): Logical AND operator, used to ensure all combined conditions are true.
        `OR` (str): Logical OR operator, used when any of the combined conditions being true is sufficient.
        `NOT` (str): Logical NOT operator, used to invert the result of a condition.

        # Identity Type Operators
        `IS` (str): Checks if two references point to the same object.
        `IS_NOT` (str): Determines if two references do not point to the same object.
        `IS_INSTANCE` (str): Verifies if an object is an instance of a specified class or type.

        # Numeric Operators
        `ABS_EQUAL` (str): Checks if the absolute value of a number is equal to a given value.
        `ABS_GREATER_THAN` (str): Compares if the absolute value of a number is greater than a specified value.
        `ABS_LESS_THAN` (str): Determines if the absolute value of a number is less than a certain value.

        # DateTime Operators
        `DATE_EQUAL` (str): Checks if a date is exactly equal to a specified date.
        `DATE_BEFORE` (str): Determines if a date occurs before a given date.
        `DATE_AFTER` (str): Assesses if a date happens after a certain date.
        `DATE_WITHIN` (str): Verifies if a date falls within a specified time frame.
    """

    # Basic comparison operators
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    # String operators
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"
    # Collection operators
    IN = "in"
    NOT_IN = "not in"
    ANY = "any"
    ALL = "all"
    NONE = "none"
    LENGTH_EQUAL = "length_eq"
    LENGTH_GREATER_THAN = "length_gt"
    LENGTH_LESS_THAN = "length_lt"
    # Logical operators
    AND = "and"
    OR = "or"
    NOT = "not"
    # Identity type operators
    IS = "is"
    IS_NOT = "is not"
    IS_INSTANCE = "isinstance"
    # # Bitwise operators
    # BITWISE_AND = "&"
    # BITWISE_OR = "|"
    # BITWISE_XOR = "^"
    # BITWISE_NOT = "~"
    # Numeric operators
    ABS_EQUAL = "abs_eq"
    ABS_GREATER_THAN = "abs_gt"
    ABS_LESS_THAN = "abs_lt"
    # DateTime operators
    DATE_EQUAL = "date_eq"
    DATE_BEFORE = "date_before"
    DATE_AFTER = "date_after"
    DATE_WITHIN = "date_within"

    @classmethod
    def is_valid_operator(cls, value: str) -> bool:
        """
        Checks if a given string is a valid operator in HyQL based on the members of the LogicOperators Enum.

        Args:
            `value` (str): The string to be checked.

        Returns:
            `bool`: True if the string is a valid operator, False otherwise.
        """
        return any(value == op for op in cls)


path_dict: dict = {
    "pattern": r"^[A-Za-z0-9]+(?:[._][A-Za-z0-9]+)*$",
    "description": "HyQL path: a dot separated path the dictionary key, shelf, or section, eg. 'section.shelf.dict_key'",
}


def _operator_validator(value: str) -> str:
    """
    Validates if a given string is a valid operator in HyQL based on the members of the LogicOperators Enum.

    Args:
        `value` (str): The string to be checked.

    Returns:
        `str`: The string if it is a valid operator.

    Raises:
        `ValueError`: If the string is not a valid operator.
    """
    if not LogicOperators.is_valid_operator(value):
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            f"Invalid operator '{value}'. Allowed operators: {', '.join(op.value for op in LogicOperators)}\n"
        )
    return value


class HyQLBaseModel(BaseModel):
    """
    A base model for HyQL models.

    This model is used to set the default config for all HyQL models, namely `extra="forbid"` so an error is raised if
    an invalid field is passed to the model.
    """

    model_config = ConfigDict(extra="forbid")


class Condition(HyQLBaseModel):
    """
    A model for a single condition in a HyQL query.

    If the left operand is not a path to a dictionary key, shelf, or section, the `left_is_path` flag must be set to False.
    Similarly, if the right operand is a path to a dictionary key, shelf, or section, the `right_is_path` flag must be set to True.

    Attributes:
        `left` (str): The left operand of the condition, which can be a value or a path to a dictionary key, shelf, or section.
        `operator` (str): The operator used to compare the left and right operands.
        `right` (Any): The right operand of the condition, which can be a value or a path to a dictionary key, shelf, or section.
        `left_is_path` (bool): A flag that indicates if the left operand is a path to a dictionary key, shelf, or section. Defaults to `True`.
        `right_is_path` (bool): A flag that indicates if the right operand is a path to a dictionary key, shelf, or section. Defaults to `False`.


    Raises:
        `ValueError`: If the operator is not a valid operator in HyQL.
        `ValueError`: If the `left_is_path` flag is set to True but the `left` value is not a valid path string.
        `ValueError`: If the `right_is_path` flag is set to True but the `right` value is not a valid path string.
    """

    left: Any
    operator: str
    right: Any
    left_is_path: bool = True
    right_is_path: bool = False

    @field_validator("operator", mode="before")
    def validate_operator(cls, value) -> str:
        return _operator_validator(value)

    @model_validator(mode="after")
    def validate_right(cls, data) -> Any:
        pattern: LiteralString = path_dict["pattern"]
        if data.left_is_path:
            if not isinstance(data.left, str) or not re.match(pattern, str(data.left)):
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"When the `left_is_path` flag is set to True, the `left` value must be a valid path string for HyllaDB."
                    " Example format: 'section.shelf.dict_key'.\n"
                )
        if data.right_is_path:
            if not isinstance(data.right, str) or not re.match(
                pattern, str(data.right)
            ):
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"When the `right_is_path` flag is set to True, the `right` value must be a valid path string for HyllaDB."
                    " Example format: 'section.shelf.dict_key'.\n"
                )
        return data


class ConditionDict(HyQLBaseModel):
    """
    ConditionDict is a model for a single condition in a HyQL query.

    Attributes:
        `condition` (Condition): The condition object.
    """

    condition: Condition


class Group(HyQLBaseModel):
    """
    Group is a model for a group of conditions in a HyQL query.

    A group must always be a list of conditions, groups, or logical operators, where conditions or groups are separated by
    logical operators "AND" | "OR".

    Attributes:
        `group` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.

    Examples:
        ```Python
        "group_dict": [
                {
                    "condition": {
                        "left": "path1.field2",
                        "operator": ">",
                        "right": 100,
                    }
                },
                "OR",
                {
                    "condition": {
                        "left": "path2.field3",
                        "operator": "<",
                        "right": "path1.field2",
                        "right_is_path": True,
                    }
                },
            ]

        group = Group(**group_dict)
        ```
    """

    group: list[Union[ConditionDict, "Group", str]]

    @field_validator("group")
    def _validate_group_format(cls, value) -> list[Union[ConditionDict, "Group", str]]:
        if not isinstance(value, list):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"The value of a group must be a list of conditions, groups, or logical operators. Example format: ['condition', 'AND', 'group']\n"
            )
        if len(value) == 0:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"The value of a group cannot be an empty list.\n"
            )

        for i, item in enumerate(value):
            if isinstance(item, str):
                if item not in ["AND", "OR"]:
                    raise ValueError(
                        "\n    HyllaDB Error:\n"
                        "        ---->"
                        f"Invalid operator '{item}'. Allowed operators for groups: 'AND' | 'OR'.\n"
                    )
                if i == 0 or i == len(value) - 1:
                    raise ValueError(
                        "\n    HyllaDB Error:\n"
                        "        ---->"
                        f"Invalid group format. A group must always be a list of conditions, groups, or logical operators, "
                        "where conditions or groups are separated by logical operators 'AND' | 'OR'.\n"
                    )
            elif not isinstance(item, (ConditionDict, Group)):
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"Invalid item type at position {i}. Expected ConditionDict, Group, or a logical operator string."
                )

            if i > 0 and isinstance(item, str) == isinstance(value[i - 1], str):
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"Invalid Group format. Conditions or Groups must be separated by logical operators 'AND' | 'OR'. "
                    f"Input has two consecutive type({type(item)}) in a row.\n"
                )

        return value


class CheckoutItem(HyQLBaseModel):
    """
    A model for a single checkout item in a HyQL query.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `checkout` (list[str] | list[Literal['*all']]): A list of fields to be checked out.
    """

    path: str = Field(**path_dict)
    checkout: list[str] | list[Literal["*all"]] = Field(
        ["*all"],
        description="A list of fields to be checked out. If the list contains only '*all', all fields will be checked out.",
    )

    @field_validator("checkout")
    def _validate_checkout_format(cls, value) -> list[str]:
        if not isinstance(value, list):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"The value of a checkout item must be a list of fields to be checked out. Example format: ['field1', 'field2']\n"
            )
        if len(value) == 0:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"The value of a checkout item cannot be an empty list.\n"
            )

        for i, item in enumerate(value):
            if not isinstance(item, str):
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"Invalid item type at position {i}. Expected str.\n"
                )
            if item == "*all":
                if len(value) > 1:
                    raise ValueError(
                        "\n    HyllaDB Error:\n"
                        "        ---->"
                        f"Invalid item type at position {i}. '*all' must be the only item in the list.\n"
                    )
            else:
                if not re.match(path_dict["pattern"], item):
                    raise ValueError(
                        "\n    HyllaDB Error:\n"
                        "        ---->"
                        f"Invalid item type at position {i}. Expected a valid path string, eg. eg. `section.shelf_1.key_1`.\n"
                    )
        return value


class SortItem(HyQLBaseModel):
    """
    A model for a single sort item in a HyQL query.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `order` (str): The sort order, either 'asc' for ascending or 'desc' for descending.
    """

    path: str = Field(**path_dict)
    order: str = Field("asc", pattern=r"^(asc|desc)$")


class Build(HyQLBaseModel):
    """
    A model for a build query in HyQL.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `data` (dict[str, Any] | None): The data to be written to the path. If `is_section` is True, data must be `None`.
        `metadata` (dict[str, Any] | None): The metadata to be written to the path.
        `is_section` (bool): A flag that indicates if the path is a section. Defaults to `False`.

    Raises:
        `ValueError`: If `is_section` is True but `data` is not None.
    """

    path: str = Field(**path_dict)
    data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    is_section: bool = False

    @model_validator(mode="after")
    def validate_path(cls, data) -> Any:
        if data.is_section:
            if data.data is not None:
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"When creating a `section`, the `data` field must be None.\n"
                )


class Write(HyQLBaseModel):
    """
    A model for a single write item in a HyQL query.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `data` (dict[str, Any]): The data to be written to the path.
    """

    path: str = Field(**path_dict)
    data: dict[str, Any]


class Checkout(HyQLBaseModel):
    """
    A model for a checkout query in HyQL.

    Attributes:
        `checkout` (list[CheckoutItem]): A list of checkout items.
        `filters` (list[ConditionDict | Group | str] | None): A list of conditions, groups, or logical operators.
        `sort` (list[SortItem] | None): A list of sort items.
        `limit` (int | None): The maximum number of results to return.
        `offset` (int | None): The number of results to skip.
    """

    checkout: list[CheckoutItem]
    filters: list[ConditionDict | Group | str] | None = None
    sort: list[SortItem] | None = None
    limit: int | None = None
    offset: int | None = None


class Revise(HyQLBaseModel):
    """
    A model for a revise query in HyQL.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
        `data` (dict[str, Any]): The data to be written to the path.
    """

    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str]
    data: dict[str, Any]


class Remove(HyQLBaseModel):
    """
    A model for a remove query in HyQL.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
    """

    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str]
