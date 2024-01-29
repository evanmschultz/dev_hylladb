import re
from typing import Any, Literal, LiteralString, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from hylladb.hyql.enums import Operators


path_dict: dict = {
    "pattern": r"^[A-Za-z0-9]+(?:[._][A-Za-z0-9]+)*$",
    "description": "HyQL path: a dot separated path the dictionary key, shelf, or section, eg. 'section.shelf.dict_key'",
}


def _operator_validator(value: str) -> str:
    """
    Validates if a given string is a valid operator in HyQL based on the members of the Operators Enum.

    Args:
        `value` (str): The string to be checked.

    Returns:
        `str`: The string if it is a valid operator.

    Raises:
        `ValueError`: If the string is not a valid operator.
    """
    if not Operators.is_valid_operator(value):
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            f"Invalid operator '{value}'. Allowed operators: {', '.join(op.value for op in Operators)}\n"
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

    Examples:
        ```Python
        # Import the Operators Enum if you want to use the enum values instead of strings as a guide, and the Condition model
        # if you want to instantiate the model directly as opposed to unpacking a dict to a query model.
        from hylladb.hyql import Operators

        # Example condition. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_condition: dict = {
            "left": "path1.field2",
            "operator": ">",
            "right": 100,
        }

        # Instantiate the model by unpacking the dict.
        condition = Condition(**hylladb_condition)
        ```
    """

    left: Any
    operator: str
    right: Any
    left_is_path: bool = True
    right_is_path: bool = False

    @field_validator("operator", mode="before")
    def _validate_operator(cls, value) -> str:
        if not _operator_validator(value):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"Invalid operator '{value}'. Allowed operators: {', '.join(op.value for op in Operators)}\n"
            )
        return value

    @model_validator(mode="after")
    def _validate_right(cls, data) -> Any:
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

    Examples:
        ```Python
        # Only useful when you want to create a Condition object directly as opposed to unpacking a dictionary to a query model.
        from hylladb.hyql import Condition, ConditionDict

        # Example condition. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_condition: dict = {
            "left": "path1.field2",
            "operator": ">",
            "right": 100,
        }

        # Instantiate the model by unpacking the dict.
        condition = Condition(**hylladb_condition)

        # Instantiate the model by unpacking the dict.
        condition_dict = ConditionDict(condition=condition)
        ```
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


class CheckOutItem(HyQLBaseModel):
    """
    A model for a single checkout item in a HyQL query.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `checkout` (list[str] | list[Literal['*all']]): A list of fields to be checked out.

    Raises:
        `ValueError`: If `checkout` is not a list.
        `ValueError`: If `checkout` is an empty list.
        `ValueError`: If `checkout` contains an item that is not a string.
        `ValueError`: If `checkout` contains an item that is not a valid path string.
        `ValueError`: If `checkout` contains more than one item and one of the items is '*all'.

    Examples:
        ```Python
        # Example checkout query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_checkout: dict = {
            "checkout": [
                {
                    "path": "path1.sub_path1",
                    "checkout": ["sub_path1.field1", "sub_path1.field2"],
                },
                {
                    "path": "path2",
                    "checkout": ["*all"],
                },
            ],
            "filters": [
                {
                    "condition": {
                        "left": "path1.field1",
                        "operator": ">=",
                        "right": 1,

                    }
                },
            ],
            "sort": [{"path": "path1.field1"}],
            "limit": 10,
            "offset": 0,
        }

        # Instantiate the model by unpacking the dict.
        checkout = Checkout(**hylladb_checkout)
        ```
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

    Raises:
        `ValueError`: If `order` is not 'asc' or 'desc'.

    Examples:
        ```Python
        from hylladb.hyql import SortItem, Checkout

        # Example sort item. Can be done by instantiating the model directly or
        # by unpacking a dict to a query model.

        hylladb_sort_item: dict = {
            "path": "path1.field1",
            "order": "asc",
        }

        # Instantiate the model by unpacking the dict.
        sort_item = SortItem(**hylladb_sort_item)

        # Add to a query model. NOTE: the ellipsis is used to denote other fields in the query model, not as a guide to instantiating the model.
        checkout_query = Checkout(
            ...,
            sort=[sort_item],
        )
        ```
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

    Examples:
        ```Python
        from hylladb.hyql import Build

        # Example build query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_build: dict = {
            "path": "path1.sub_path1",
            "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
        }

        # Instantiate the model by unpacking the dict.
        build = Build(**hylladb_build)

        # Pass it into the HyQL query method.
        ```
    """

    path: str = Field(**path_dict)
    metadata: dict[str, Any] | None = None
    is_section: bool = False


class Write(HyQLBaseModel):
    """
    A model for a single write item in a HyQL query.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `data` (dict[str, Any]): The data to be written to the path.

    Examples:
        ```Python
        from hylladb.hyql import Write

        # Example write query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_write: dict = {
            "path": "path1.sub_path1",
            "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
        }

        # Instantiate the model by unpacking the dict.
        write = Write(**hylladb_write)

        # Pass it into the HyQL query method.
        ```
    """

    path: str = Field(**path_dict)
    data: dict[str, Any]


class CheckOut(HyQLBaseModel):
    """
    A model for a checkout query in HyQL.

    Attributes:
        `checkout` (list[CheckoutItem]): A list of checkout items.
        `filters` (list[ConditionDict | Group | str] | None): A list of conditions, groups, or logical operators.
        `sort` (list[SortItem] | None): A list of sort items.
        `limit` (int | None): The maximum number of results to return.
        `offset` (int | None): The number of results to skip.

    Raises:
        `ValueError`: If `limit` is less than 1.
        `ValueError`: If `offset` is less than 0.

    Examples:
       ```Python
        # Import the Operators Enum if you want to use the enum values instead of strings as a guide.
        from hylladb.hyql import Operators

        # Example checkout query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_checkout: dict = {
        "checkout": [
            {
                "path": "path1.sub_path1",
                "checkout": ["sub_path1.field1", "sub_path1.field2"],
            },
            {
                "path": "path2",
                "checkout": ["*all"],
            },
        ],
        "filters": [
            {
                "condition": {
                    "left": "path1.field1",
                    "operator": ">=",
                    "right": 1,
                }
            },
            "AND",
            {
                "group": [
                    {
                        "condition": {
                            "left": "name",
                            "operator": Operators.IN,
                            "right": "path1.field2",
                            "left_is_path": False,
                            "right_is_path": True,
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
            },
        ],
        "sort": [{"path": "path1.field1"}],
        "limit": 10,
        "offset": 0,
    }

    # Instantiate the model by unpacking the dict.
    checkout = Checkout(**hylladb_checkout)
    ```
    """

    checkout: list[CheckOutItem]
    filters: list[ConditionDict | Group | str] | None = None
    sort: list[SortItem] | None = None
    limit: int | None = Field(None, ge=1)
    offset: int | None = Field(None, ge=0)


class Revise(HyQLBaseModel):
    """
    A model for a revise query in HyQL.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
        `data` (dict[str, Any]): The data to be written to the path.

    Raises:
        `ValueError`: If the path is the `metadata` and the `schema` key is missing from the `data` dictionary.

    Examples:
        ```Python
        # Import the Operators Enum if you want to use the enum values instead of strings as a guide.
        from hylladb.hyql import Operators

        # Example revise query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_revise: dict = {
            "path": "path1.sub_path1",
            "filters": [
                {
                    "condition": {
                        "left": "path1.field1",
                        "operator": "==",
                        "right": "value1",
                    }
                },
                "AND",
                {
                    "group": [
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
                },
            ],
            "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
        }

        # Instantiate the model by unpacking the dict.
        revise = Revise(**hylladb_revise)
        ```
    """

    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    data: dict[str, Any]

    @model_validator(mode="after")
    def _validate_dict(cls, data) -> Any:
        if len(data.data) == 0:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"The `data` field cannot be empty.\n"
            )

    @model_validator(mode="after")
    def _validate_path_is_metadata(cls, data) -> Any:
        if data.path.endswith("metadata"):
            if not data.data.get("schema"):
                raise ValueError(
                    "\n    HyllaDB Error:\n"
                    "        ---->"
                    f"The `schema` field is required when revising metadata.\n"
                )


class Remove(HyQLBaseModel):
    """
    A model for a remove query in HyQL.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
        `remove_shelf` (bool): A flag that indicates if the shelf should be removed. Defaults to `False`.
        `remove_section` (bool): A flag that indicates if the section should be removed. Defaults to `False`.

    Raises:
        `ValueError`: If `remove_shelf` and `remove_section` are both `True`. Only one of them can be `True` per query.

    Examples:
        ```Python
        from hylladb.hyql import Remove

        # Define the remove query dictionary, can also be done by simply instantiating the model directly.
        hylladb_remove: dict = {
        "path": "path1.sub_path1",
        "filters": [
                {
                    "condition": {
                        "left": "path1.field1",
                        "operator": "==",
                        "right": "value1",
                    }
                },
                "AND",
                {
                    "group": [
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
                },
            ],
        }

        # Instantiate the model by unpacking the dict.
        Remove(**remove_idea)
        ```
    """

    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    remove_shelf: bool = False
    remove_section: bool = False

    @model_validator(mode="after")
    def _validate_only_one_bool_is_true(cls, data) -> Any:
        if data.remove_shelf and data.remove_section:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"Only one of `remove_shelf` or `remove_section` can be True.\n"
            )


class Reset(HyQLBaseModel):
    """
    A model for a reset query in HyQL.

    This will remove all of the data in the shelf or section, but will not remove the shelf or section itself.

    Attributes:
        `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
        `reset_shelf` (bool): A flag that indicates if the shelf should be reset. Defaults to `False`.
        `reset_section` (bool): A flag that indicates if the section should be reset. Defaults to `False`.

    Notes:
        This will not affect the metadata of the shelf or section. If you wish to reset the metadata, use the Revise model after the Reset model.

    Raises:
        `ValueError`: If `reset_shelf` and `reset_section` are both `True`. Only one of them can be `True` per query.

    Examples:
        ```Python
        from hylladb.hyql import Reset

        # Define the reset query dictionary, can also be done by simply instantiating the model directly.
        hylladb_reset: dict = {
        "path": "path1.sub_path1",
        "filters": [
                {
                    "condition": {
                        "left": "path1.field1",
                        "operator": "==",
                        "right": "value1",
                    }
                }
            ],
        "reset_shelf": True,
        }

        # Instantiate the model by unpacking the dict.
        Reset(**reset_idea)
        ```
    """

    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    reset_shelf: bool = False
    reset_section: bool = False

    @model_validator(mode="after")
    def _validate_only_one_bool_is_true(cls, data) -> Any:
        if data.reset_shelf and data.reset_section:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"Only one of `reset_shelf` or `reset_section` can be True.\n"
            )
