import re
from typing import Any, Literal, LiteralString
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ConditionOperator(Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    AND = "and"
    OR = "or"
    IN = "in"
    NOT_IN = "not in"

    @staticmethod
    def allowed_operators():
        return " | ".join(member.value for member in ConditionOperator)


class FilterConditions(BaseModel):
    conditions: list[str] | None = Field(
        default=None,
        description="HyQL filter conditions",
    )

    @field_validator("conditions")
    def validate_condition(cls, values) -> list[str]:
        pattern: LiteralString = (
            r"^[A-Za-z0-9_]+\s("
            + "|".join([op.value for op in ConditionOperator])
            + r")\s.+$"
        )

        for i, condition in enumerate(values):
            if not re.match(pattern, condition):
                allowed_operators = ConditionOperator.allowed_operators()
                raise ValueError(
                    f"Invalid condition format at index {i}: {condition}. Allowed format: <`field`> < {allowed_operators} > <`value`>"
                )
        return values


class SortCondition(BaseModel):
    key: str
    order: Literal["asc", "desc"] = Field(default="asc")


class HyWrite(BaseModel):
    path: str = Field(
        pattern=r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*$", description="HyQL path"
    )
    data: dict[str, Any]


class HyCheckout(BaseModel):
    path: str
    checkout: list[str]
    filter: FilterConditions | None = None
    sort: list[SortCondition] | None = None
    limit: int | None = None
    offset: int | None = None


class HyRevise(BaseModel):
    path: str
    filters: FilterConditions
    update_data: dict[str, Any]


class HyRemove(BaseModel):
    path: str
    filters: list[FilterConditions]


if __name__ == "__main__":
    # Create
    create_query = HyWrite(
        path="parent_section.child_section.shelf_name",
        data={"field1": "new value", "field2": {"subfield": "another value"}},
    )

    # Read
    query = HyCheckout(
        path="parent_section.child_section.shelf_name",
        checkout=["field1", "field2.subfield"],
        filter=FilterConditions(conditions=["field1 == 'value'"]),
        sort=[SortCondition(key="field1", order="asc")],
        limit=10,
        offset=0,
    )

    # Update
    update_query = HyRevise(
        path="parent_section.child_section.shelf_name",
        filters=FilterConditions(conditions=["field1 == 'old value'"]),
        update_data={"field1": "updated value"},
    )

    # Delete
    delete_query = HyRemove(
        path="parent_section.child_section.shelf_name",
        filters=[
            FilterConditions(
                conditions=[
                    "field1 == 'value to delete'",
                    "field2 not_in 'another value'",
                ]
            )
        ],
    )
