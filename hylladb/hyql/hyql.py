from abc import ABC
import re
from typing import Any, Literal, LiteralString, Protocol, Union, runtime_checkable
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# Define a Protocol as a type hint


class ConditionsEnum:
    _is_base_comparison: bool = True


class BasicComparison(ConditionsEnum, Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="


class StringOperators(ConditionsEnum, Enum):
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"


class CollectionOperators(ConditionsEnum, Enum):
    IN = "in"
    NOT_IN = "not in"
    ANY = "any"
    ALL = "all"
    NONE = "none"
    LENGTH_EQUAL = "length_eq"
    LENGTH_GREATER_THAN = "length_gt"
    LENGTH_LESS_THAN = "length_lt"


class LogicalOperators(ConditionsEnum, Enum):
    AND = "and"
    OR = "or"
    NOT = "not"


class IdentityTypeOperators(ConditionsEnum, Enum):
    IS = "is"
    IS_NOT = "is not"
    IS_INSTANCE = "isinstance"


class BitwiseOperators(ConditionsEnum, Enum):
    BITWISE_AND = "&"
    BITWISE_OR = "|"
    BITWISE_XOR = "^"
    BITWISE_NOT = "~"


class NumericOperators(ConditionsEnum, Enum):
    ABS_EQUAL = "abs_eq"
    ABS_GREATER_THAN = "abs_gt"
    ABS_LESS_THAN = "abs_lt"


class DateTimeOperators(ConditionsEnum, Enum):
    DATE_EQUAL = "date_eq"
    DATE_BEFORE = "date_before"
    DATE_AFTER = "date_after"
    DATE_WITHIN = "date_within"


class LogicOperators(ConditionsEnum, Enum):
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
    # Bitwise operators
    BITWISE_AND = "&"
    BITWISE_OR = "|"
    BITWISE_XOR = "^"
    BITWISE_NOT = "~"
    # Numeric operators
    ABS_EQUAL = "abs_eq"
    ABS_GREATER_THAN = "abs_gt"
    ABS_LESS_THAN = "abs_lt"
    # DateTime operators
    DATE_EQUAL = "date_eq"
    DATE_BEFORE = "date_before"
    DATE_AFTER = "date_after"
    DATE_WITHIN = "date_within"

    @staticmethod
    def allowed_operators() -> LiteralString:
        return " | ".join(member.value for member in LogicOperators)


# class FilterConditions(BaseModel):
#     conditions: list[str] | None = Field(
#         default=None,
#         description="HyQL filter conditions",
#     )

#     @field_validator("conditions")
#     def validate_condition(cls, values) -> list[str]:
#         pattern: LiteralString = (
#             r"^[A-Za-z0-9_]+\s(" + "|".join([op.value for op in Condition]) + r")\s.+$"
#         )

#         for i, condition in enumerate(values):
#             if not re.match(pattern, condition):
#                 allowed_operators: LiteralString = Condition.allowed_operators()
#                 raise ValueError(
#                     f"Invalid condition format at index {i}: {condition}. Allowed format: <`field`> < {allowed_operators} > <`value`>"
#                 )
#         return values


# class SortCondition(BaseModel):
#     key: str
#     order: Literal["asc", "desc"] = Field(default="asc")


# query_idea = {
#     "checkout": [
#         {
#             "path": "path1.sub_path1",
#             "checkout": ["sub_path1.field1", "sub_path1.field2"],
#         },
#         {
#             "path": "path2",
#             "checkout": ["*all"],
#         },
#     ],
#     "filters": [
#         {
#             "condition": {
#                 "left": "path1.field1",
#                 "operator": "==",
#                 "right": "value1",
#             }
#         },
#         "AND",
#         {
#             "group": [
#                 {
#                     "condition": {
#                         "left": "path1.field2",
#                         "operator": ">",
#                         "right": 100,
#                     }
#                 },
#                 "OR",
#                 {
#                     "condition": {
#                         "left": "path2.field3",
#                         "operator": "<",
#                         "right": "path1.field2",
#                         "right_is_path": True,
#                     }
#                 },
#             ]
#         },
#     ],
#     "sort": [{"path": "path1.field1", "order": "asc"}],
#     "limit": 10,
#     "offset": 0,
# }


# class HyllaPath(BaseModel):
#     path: str = Field(
#         pattern=r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*$", description="HyQL path: a dot separated path the dictionary key, shelf, or section, eg. 'section.shelf.dict_key'"
#     )


# class HyllaPath(BaseModel):
#     path: str = Field(
#         pattern=r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*$", description="HyQL path: a dot separated path the dictionary key, shelf, or section, eg. 'section.shelf.dict_key'"
#     )

path_dict: dict = {
    "pattern": r"^[A-Za-z0-9]+(?:[._][A-Za-z0-9]+)*$",
    "description": "HyQL path: a dot separated path the dictionary key, shelf, or section, eg. 'section.shelf.dict_key'",
}


def operator_validator(value) -> str:
    if value not in LogicOperators.allowed_operators():
        raise ValueError(
            f"Invalid operator '{value}'. Allowed operators: {LogicOperators.allowed_operators()}"
        )
    return value


class Condition(BaseModel):
    left: str = Field(**path_dict)
    operator: str
    right: Any
    right_is_path: bool = False

    @field_validator("operator", mode="before")
    def validate_operator(cls, value) -> str:
        if value not in LogicOperators.allowed_operators() or not value:
            raise ValueError(
                f"Invalid operator '{value}'. Allowed operators: {LogicOperators.allowed_operators()}"
            )
        return value

    @model_validator(mode="after")
    def validate_right(cls, data) -> Any:
        if data.right_is_path:
            pattern: LiteralString = path_dict["pattern"]
            if not isinstance(data.right, str):
                raise ValueError(
                    f"When the `right_is_path` flag is set to True, the `right` value must be a valid path string for HyllaDB."
                    " Example format: 'section.shelf.dict_key'."
                )
            if not re.match(pattern, str(data.right)):
                raise ValueError(
                    f"The value `{data.right}` does not match the required pattern. Example format: 'section.shelf.dict_key'."
                )
        return data


class ConditionDict(BaseModel):
    condition: Condition


class KeyBasedCondition(BaseModel):
    left: str = Field(**path_dict)
    operator: str
    right: Any
    # right_is_path: bool = False

    @field_validator("operator")
    def validate_operator(cls, value) -> str:
        if value not in LogicOperators.allowed_operators():
            raise ValueError(
                f"Invalid operator '{value}'. Allowed operators: {LogicOperators.allowed_operators()}"
            )
        return value


class Group(BaseModel):
    group: list[Union[ConditionDict, "Group", str]]


class GroupDict(BaseModel):
    group: list[Union[ConditionDict, Group, str]]


class CheckoutItem(BaseModel):
    path: str = Field(**path_dict)
    checkout: list[str]


class SortItem(BaseModel):
    path: str = Field(**path_dict)
    order: str


class Write(BaseModel):
    path: str = Field(**path_dict)
    data: dict[str, Any]


class Checkout(BaseModel):
    checkout: list[CheckoutItem]
    filters: list[ConditionDict | GroupDict | str]
    sort: list[SortItem]
    limit: int
    offset: int


class Revise(BaseModel):
    path: str = Field(**path_dict)
    filters: list[ConditionDict | GroupDict | str]
    data: dict[str, Any]


class Remove(BaseModel):
    path: str = Field(**path_dict)
    filters: list[ConditionDict | GroupDict | str]
