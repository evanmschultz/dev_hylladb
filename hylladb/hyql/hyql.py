import re
from typing import Any, Literal, LiteralString, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from hylladb.db.models import ShelfModel
from hylladb.hyql.enums import Operators
import hylladb.hyql.hyql_utilities as hyql_utils


class HyQLBaseModel(BaseModel, validate_assignment=True):
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
        - `left` (str): The left operand of the condition, which can be a value or a path to a dictionary key, shelf, or section.
        - `operator` (str): The operator used to compare the left and right operands.
        - `right` (Any): The right operand of the condition, which can be a value or a path to a dictionary key, shelf, or section.
        - `left_is_path` (bool): A flag that indicates if the left operand is a path to a dictionary key, shelf, or section. Defaults to `True`.
        - `right_is_path` (bool): A flag that indicates if the right operand is a path to a dictionary key, shelf, or section. Defaults to `False`.


    Raises:
        - `ValueError`: If the operator is not a valid operator in HyQL.
        - `ValueError`: If the `left_is_path` flag is set to True but the `left` value is not a valid path string.
        - `ValueError`: If the `right_is_path` flag is set to True but the `right` value is not a valid path string.

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
        """Validates the operator."""
        if not hyql_utils.operator_validator(value):
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"Invalid operator '{value}'. Allowed operators: {', '.join(op.value for op in Operators)}\n"
            )
        return value

    @model_validator(mode="after")
    def _validate_paths(cls, data) -> Any:
        """Validates the paths.

        Either `left`, `right`, or both must be a valid path strings and the `is_path_*` flags must match.
        """
        pattern: LiteralString = hyql_utils.path_dict["pattern"]
        if not data.right_is_path and not data.left_is_path:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"Invalid condition format. At least one `is_path_*` boolean flag must be set to `True.\n"
            )

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
        - `condition` (Condition): The condition object.

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
        - `group` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.

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
        """Validates the format of the group list."""

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
        - `path` (str | None): The path to the shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1`.
            - If `None`, checkout is for the library directory.
        - `checkout` (list[str] | list[Literal['*all']]): A list of paths, keys, sections, or shelves to be checked out.


    Raises:
        - `ValueError`: If `checkout` is not a list.
        - `ValueError`: If `checkout` is an empty list.
        - `ValueError`: If `checkout` contains an item that is not a string.
        - `ValueError`: If `checkout` contains an item that is not a valid path string.
        - `ValueError`: If `checkout` contains more than one item and one of the items is '*all'.

    Examples:
        ```Python
        # Example checkout query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        checkout_item: dict = {
                "path": "section_1.sub_section_1",
                "checkout": ["shelf_1.field1", "shelf_1.field2"],
            },

        # Instantiate the model by unpacking the dict.
        checkout = Checkout(**checkout_item)
        ```
    """

    path: str | None = Field(**hyql_utils.path_dict)
    # shelf_name: str | None = Field(None, pattern=hyql_utils.checkout_pattern)
    checkout: list[str] | list[Literal["*all"]] = Field(
        ["*all"],
        description="A list of keys to be checked out. If the list contains only '*all', all keys will be checked out.",
    )

    @field_validator("checkout")
    def _validate_checkout_format(cls, value: list[str]) -> list[str]:
        """Validates the format of the checkout list."""

        if len(value) == 0:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"The value of a checkout item cannot be an empty list.\n"
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

    # @model_validator(mode="after")
    # def _validate_if_shelf_name_checkout_all(self) -> "CheckOutItem":
    #     if not self.shelf_name:
    #         if len(self.checkout) > 1 or self.checkout[0] != "*all":
    #             raise ValueError(
    #                 "\n    HyllaDB Error:\n"
    #                 "        ---->"
    #                 f"Invalid checkout format. If the checkout item is for a section or the library, the checkout list must contain only '*all'.\n"
    #             )
    #     return self


class SortItem(HyQLBaseModel):
    """
    A model for a single sort item in a HyQL query.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `order` (str): The sort order, either 'asc' for ascending or 'desc' for descending.

    Raises:
        - `ValueError`: If `order` is not 'asc' or 'desc'.

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

    path: str = Field(**hyql_utils.path_dict)
    order: str = Field("asc", pattern=r"^(asc|desc)$")


class SetSchema(HyQLBaseModel):
    """
    Sets or updates the schema for a section or the library.

    Attributes:
        - `path` (str | None): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`. If `None`, the schema will be set for the library.
        - `schema` (type[ShelfModel] | None): The schema for the section or library. Used to enforce data structure and types for all the `shelves` that are direct children
            of the section or library directory. If `None`, no shelf can be created as a direct child of the section or library directory.
            - NOTE: This is not an instance of the schema class, but the class itself.
        - `is_library` (bool): A flag that indicates if the schema is for the library. Defaults to `False`.

    Raises:
        - `ValueError`: If `path` is not `None` and `is_library` is `True`.
        - `ValueError`: If `path` is `None` and `is_library` is `False`.

    Examples:
        - Define a simple flat schema for a section:

        ```Python
        from hylladb.hyql import SetSchema
        from hylladb.hyql import HyQLSchema

        # Define the schema for the shelves that are direct children to the section.
        class Animal(HyQLSchema):
            name: str

        # Example set schema query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_set_schema: dict = {
            "path": "path1.sub_path1",
            "schema": Animal,
        }

        # Instantiate the model by unpacking the dict.
        set_schema = SetSchema(**hylladb_set_schema)

        # Pass it into the HyQL query method.
        ```

        - Define a more complex, nested schema for the library:

        ```Python
        from hylladb.hyql import SetSchema
        from hylladb.hyql import ShelfModel

        # Define the schema for the shelves that are direct children to the library.
        class UserStats(ShelfModel):
            age: int
            height: float

        class User(ShelfModel):
            name: str
            stats: UserStats

        # Example set schema query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_set_schema: dict = {
            "schema": User,
            "is_library": True,
        }

        # Instantiate the model by unpacking the dict.
        set_schema = SetSchema(**hylladb_set_schema)
        ```
    """

    path: str | None = Field(**hyql_utils.path_dict)
    schema: type[ShelfModel] | None
    is_library: bool = False

    @model_validator(mode="after")
    def _ensure_path_is_none_if_is_library(cls, data) -> Any:
        """Ensures that the path is None if the schema is for a library."""

        if data.is_library and data.path:
            raise ValueError(
                "\n    HyllaDB Error:\n"
                "        ---->"
                f"The `path` field must be None if `is_library` is True.\n"
            )


class BuildShelf(HyQLBaseModel):
    """
    A HyQL model used when building a shelf in HyllaDB.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `name` (str): The name of the shelf. Must follow the same naming conventions as a Python variable name, eg. `shelf_1`.
        - `data` (dict[str, Any] | None): The data to be written to the path. If passing in data must conform to the `schema` defined in the section.
        - `metadata` (dict[str, Any] | None): The metadata to be written to the path.

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

    path: str = Field(**hyql_utils.path_dict)
    name: str = Field(pattern=r"^[A-Za-z0-9]+(?:[_][A-Za-z0-9]+)*$")
    data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class BuildSection(HyQLBaseModel):
    """
    A HyQL model used when building a section in HyllaDB.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `name` (str): The name of the section. Must follow the same naming conventions as a Python variable name, eg. `section_1`.
        - `schema` (Schema | None): The schema for the section. Used to enforce data structure and types for all the `shelves` that are direct children
            of the section. If `None`, no shelf can be created as a direct child of the section.
        - `metadata` (dict[str, Any] | None): The metadata to be written to the path.
    """

    path: str = Field(**hyql_utils.path_dict)
    name: str = Field(pattern=r"^[A-Za-z0-9]+(?:[_][A-Za-z0-9]+)*$")
    schema: ShelfModel | None
    metadata: dict[str, Any] | None = None


class Write(HyQLBaseModel):
    """
    A model for a single write item in a HyQL query.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `data` (dict[str, Any]): The data to be written to the path.

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

    path: str = Field(**hyql_utils.path_dict)
    data: dict[str, Any]


class CheckOut(HyQLBaseModel):
    """
    A model for a checkout query in HyQL.

    Attributes:
        - `checkout` (list[CheckoutItem]): A list of checkout items.
        - `filters` (list[ConditionDict | Group | str] | None): A list of conditions, groups, or logical operators.
        - `sort` (list[SortItem] | None): A list of sort items.
        - `limit` (int | None): The maximum number of results to return.
        - `offset` (int | None): The number of results to skip.

    Raises:
        - `ValueError`: If `limit` is less than 1.
        - `ValueError`: If `offset` is less than 0.

    Examples:
       ```Python
        # Import the Operators Enum if you want to use the enum values instead of strings as a guide.
        from hylladb.hyql import Operators

        # Example checkout query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_checkout: dict = {
        "checkout": [
            {
                "path": "section_1.sub_section_1",
                "checkout": ["shelf_1.field1", "shelf_1.field2"],
            },
            {
                "path": "section_2",
                "checkout": ["*all"],
            },
        ],
        "filters": [
            {
                "condition": {
                    "left": "section_1.sub_section_1.shelf_1.field1",
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
                            "right": "section_1.sub_section_1.shelf_1.field2",
                            "left_is_path": False,
                            "right_is_path": True,
                        }
                    },
                    "OR",
                    {
                        "condition": {
                            "left": "section_2.shelf_1.field3",
                            "operator": "<",
                            "right": "section_1.sub_section_1.shelf_1.field2",
                            "right_is_path": True,
                        }
                    },
                ]
            },
        ],
        "sort": [{"path": "section_1.field1"}],
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
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
        - `data` (dict[str, Any]): The data to be written to the path.

    Raises:
        - `ValueError`: If the path is the `metadata` and the `schema` key is missing from the `data` dictionary.

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

    path: str = Field(**hyql_utils.path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    data: dict[str, Any]


class Remove(HyQLBaseModel):
    """
    A model for a remove query in HyQL.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
        - `remove_shelf` (bool): A flag that indicates if the shelf should be removed. Defaults to `False`.
        - `remove_section` (bool): A flag that indicates if the section should be removed. Defaults to `False`.

    Raises:
        - `ValueError`: If `remove_shelf` and `remove_section` are both `True`. Only one of them can be `True` per query.

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

    path: str = Field(**hyql_utils.path_dict)
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
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `filters` (list[ConditionDict | Group | str]): A list of conditions, groups, or logical operators.
        - `reset_shelf` (bool): A flag that indicates if the shelf should be reset. Defaults to `False`.
        - `reset_section` (bool): A flag that indicates if the section should be reset. Defaults to `False`.

    Notes:
        - This will not affect the metadata of the shelf or section. If you wish to reset the metadata, use the Revise model after the Reset model.

    Raises:
        - `ValueError`: If `reset_shelf` and `reset_section` are both `True`. Only one of them can be `True` per query.

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

    path: str = Field(**hyql_utils.path_dict)
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
