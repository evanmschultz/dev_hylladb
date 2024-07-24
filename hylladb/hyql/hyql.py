from typing import Any, Literal, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

import hylladb.hyql.validators as validators
from hylladb.hyql.hyql_base.hyql_base_model import HyQLBaseModel
from hylladb.hyql.hyql_base.schema_model import SchemaModel
from hylladb.hyql.hyql_utilities import name_pattern, path_dict


class Condition(HyQLBaseModel):
    """
    A model for a single condition in a HyQL query.

    The left operand is always a path to a dictionary key, shelf, or section and the right operand can be a value or a path to a dictionary key,
    shelf, or section.

    The purpose of this model is to provide a way to define a single condition in a query, which can then be used in a group or filter expression.

    Attributes:
        - `left_path` (str): The path to the shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1`.
        - `operator` (str): The operator used to compare the left and right operands.
        - `right` (Any): The right operand of the condition, which can be a value or a path to a dictionary key, shelf, or section.
        - `right_is_path` (bool): A flag that indicates if the right operand is a path to a dictionary key, shelf, or section. Defaults to `False`.

    Raises:
        - `ValueError`: If the operator is not a valid operator in HyQL.
        - `ValueError`: If the `left` value is not a valid path string.
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

    left_path: str = Field(**path_dict)
    operator: str
    right: Any
    right_is_path: bool = False

    @field_validator("operator", mode="before")
    def _validate_operator(cls, value) -> str:
        """Validates the operator."""

        return validators.validate_operator(value)

    @model_validator(mode="after")
    def _validate_paths(cls, data) -> Any:
        """Validates the the `right` attribute is a path if `right_is_path` is True."""

        return validators.validate_right_is_path(data)


class ConditionDict(HyQLBaseModel):
    """
    ConditionDict is a model for a single condition in a HyQL query.

    The purpose of this model is to provide a way to define a single condition in a query, which can then be used in a group or filter expression.

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

    Notes:
        - The only reason this model exists is to allow for dictionary unpacking to a query model. If you are aware of a better way to do this
            without the need for this model, please create in issue in the repository and/or a pull request.
    """

    condition: Condition


class Group(HyQLBaseModel):
    """
    Group is a model for a group of conditions in a HyQL query.

    A group must always be a list of conditions, groups, or logical operators, where conditions or groups are separated by
    logical operators "AND" | "OR".

    The reason for this model is to allow for the definition of groups of conditions in a query, which can then be used in a filter expression.

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

        return validators.validate_group_format(value, [ConditionDict, Group])


class SortItem(HyQLBaseModel):
    """
    A model for a single sort item in a HyQL query.

    The purpose of this model is to provide a way to define a single sort item in a query, which can then be used in a checkout query.

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

    path: str = Field(**path_dict)
    order: str = Field("asc", pattern=r"^(asc|desc)$")


class SetSchema(HyQLBaseModel):
    """
    Sets or updates the schema for a section or the library.

    The schema is used to enforce data structure and types for all the `shelves` that are direct children of the section or library directory. This
    prevents badly formed data from being written to the database to ensure that what is held and recovered is always consistent and predictable.

    Attributes:
        - `path` (str | None): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`. If `None`, the schema will be set for the library.
        - `schema_model` (type[SchemaModel]): The schema for the section or library. Used to enforce data structure and types for all the `shelves`
            that are direct children of the section or library directory. If `None`, no shelf can be created as a direct child of the section
            or library directory.
            - NOTE: This is not an instance of the schema class, but the class itself.
        - `is_library` (bool): A flag that indicates if the schema is for the library. Defaults to `False`.

    Raises:
        - `ValueError`: If `path` is not `None` and `is_library` is `True`.
        - `ValueError`: If `path` is `None` and `is_library` is `False`.

    Examples:
        - Define a simple flat schema for a section:

        ```Python
        from hylladb.hyql import SetSchema
        from hylladb.hyql import SchemaModel

        # Define the schema for the shelves that are direct children to the section.
        class Animal(SchemaModel):
            name: str

        # Example set schema query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_set_schema: dict = {
            "path": "path1.sub_path1",
            "schema_model": Animal,
        }

        # Instantiate the model by unpacking the dict.
        set_schema = SetSchema(**hylladb_set_schema)

        # Pass it into the HyQL query method.
        ```

        - Define a more complex, nested schema for the library:

        ```Python
        from hylladb.hyql import SetSchema
        from hylladb.hyql import SchemaModel

        # Define the schema for the shelves that are direct children to the library.
        class UserStats(SchemaModel):
            age: int
            height: float

        class User(SchemaModel):
            name: str
            stats: UserStats

        # Example set schema query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_set_schema: dict = {
            "schema_model": User,
            "is_library": True,
        }

        # Instantiate the model by unpacking the dict.
        set_schema = SetSchema(**hylladb_set_schema)
        ```
    """

    path: str | None = Field(default=None, **path_dict)
    schema_model: type[SchemaModel] = Field(
        ..., description="The schema for the section or library."
    )
    is_library: bool = False

    @model_validator(mode="after")
    def _ensure_path_is_none_if_is_library(cls, data) -> Any:
        """Ensures that the path is None if the schema is for a library."""

        validators.ensure_path_is_none_if_is_library(data)


class BuildShelf(BaseModel):
    """
    A HyQL model used when building a shelf in HyllaDB.

    Shelves are the lowest building element of the database and are what are actually used to store data. They are always direct children of a section
    or library directory. Dictionaries all the way down, well, here is where the actual, strict python dictionary is stored.

    The purpose of this model is to provide a way to define a single shelf in a query, which can then be used in a build query.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `name` (str): The name of the shelf. Must follow the same naming conventions as a Python variable name, eg. `shelf_1`.
        - `data` (SchemaModel | None): The data to be written to the path.
            - If passing in data you must use a `SchemaModel` instance as defined by the
                `SchemaModel` class for the respective library or section the shelf is a direct child of.

        - `metadata` (dict[str, Any] | None): The metadata to be written to the path.

    Examples:
        ```python
        from hylladb.hyql import BuildShelf, SchemaModel

        class BookSchema(SchemaModel):
            title: str
            Author: str
            published_year: int

        data = BookSchema(
            title="Dune",
            author="Frank Herbert",
            published_year=1965
        )

        build_shelf = BuildShelf(
            path="library.books",
            name="sci_fi",
            data=data,
            metadata={"genre": "Science Fiction"}
        )
        ```
    """

    path: str = Field(**path_dict)
    name: str = Field(pattern=name_pattern)
    data: Any | None = None  # Must be a subclass of SchemaModel
    metadata: dict[str, Any] | None = None

    @field_validator("data")
    def validate_is_schema_model(cls, data) -> Any:
        """Validates that the data is a SchemaModel instance."""

        return validators.validate_is_schema_model(data)


class BuildSection(HyQLBaseModel):
    """
    A HyQL model used when building a section in HyllaDB.

    Sections are the second lowest building element of the database and are used to group shelves together. Sections are always direct children of a
    library or another section. They are used to enforce a schema on the shelves that are direct children of the section.

    The purpose of this model is to provide a way to define a single section in a query, which can then be used in a build query.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1.key_1`.
        - `name` (str): The name of the section. Must follow the same naming conventions as a Python variable name, eg. `section_1`.
        - `schema_model` (type[SchemaModel]): The schema for the section. Used to enforce data structure and types for all the `shelves` that are direct children
            of the section. If `None`, no shelf can be created as a direct child of the section.
        - `metadata` (dict[str, Any] | None): The metadata to be written to the path.
    """

    path: str = Field(**path_dict)
    name: str = Field(pattern=name_pattern)
    schema_model: type[SchemaModel]
    metadata: dict[str, Any] | None = None


class Write(HyQLBaseModel):
    """
    A model for inserting new data in a HyQL query.

    This query model is used to write new data to a specified path in the database. It is specifically designed for adding new
    data and does not update or overwrite existing data. In SQL, it would be similar to an INSERT operation. In MongoDB, it's
    comparable to the insertOne() method. In key-value stores, it's similar to a PUT operation for adding a new key-value pair,
    but unlike typical PUT operations, it won't update existing data.

    The purpose of this model is to provide a way to define a single write operation in a query, which can then be used to add
    new data to the database.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section where the new data will be inserted. Must be a
            dot-separated path string from the library directory, e.g., "section.shelf_1.key_1".
        - `data` (SchemaModel): The new data to be written to the specified path.

    Notes:
        - The `data` attribute requires a SchemaModel. This approach ensures type safety by enforcing that all data conforms
          to a predefined schema, reducing runtime errors and enhancing IDE suggestions.
        - This class is designed to prevent accidental overwrites of existing data. If you need to update existing data,
          use a separate update operation.

    Examples:
        ```Python
        from hylladb.hyql import Write, SchemaModel

        # Define the schema for the shelves that are direct children to the section.
        class Book(SchemaModel):
            id: int
            title: str
            author: str
            genre: str

        new_book = Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald", genre="Fiction")

        # Example write query. Can be done by instantiating the model directly or
        # by unpacking a dict to the model.
        hylladb_write: dict = {
            "path": "library.fiction.classics",
            "data": new_book,
        }

        # Instantiate the model by unpacking the dict.
        write = Write(**hylladb_write)

        # Pass it into the HyQL query method.
        ```
    """

    path: str = Field(**path_dict)
    data: Any  # Must be a subclass of SchemaModel

    @field_validator("data")
    def validate_is_schema_model(cls, data) -> Any:
        """Validates that the data is a SchemaModel instance."""

        return validators.validate_is_schema_model(data)


class CheckOut(HyQLBaseModel):
    """
    A model for a checkout query in HyQL.

    This model helps you retrieve data from specific shelves in the database (library). It allows you to specify the paths to the shelves, sections, or library
    you want to retrieve data from, as well as any filters, sorting, and limits you want to apply to the results.

    Attributes:
        - `path` (str | None): The path to the shelf, or section. Must be a dot separated path string from the library directory,
            eg. `section.shelf_1`.
            - If `None`, checkout is for the library directory.
            - If providing shelf names as the final part of the path, those shelves will be checked out, assuming they exist and pass the filter data.
        -   `checkout` (list[str | Literal["*all"]]): A list of shelf names to be checked out.
            -   If the list contains only '*all', all shelves will be checked out that match the filter data.
            -   If wishing to checkout specific shelves, provide a list of the shelf names you wish to checkout, or leave the default value of
                `["*all"]` to checkout all shelves that fit the filter data.
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
        "path": "section_1.sub_section_1",
        "checkout": ["shelf_1", "shelf_1.field2"],
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
    checkout = CheckOut(**hylladb_checkout)
    ```
    """

    path: str | None = Field(None, **path_dict)
    checkout: list[str | Literal["*all"]] = Field(
        ["*all"],
        description="A list of shelf names to be checked out. If the list contains only '*all', all shelves will be checked out.",
    )
    filters: list[Union["ConditionDict", "Group", str]] | None = None
    sort: list["SortItem"] | None = None
    limit: int | None = Field(None, ge=1)
    offset: int | None = Field(None, ge=0)


class Revise(HyQLBaseModel):
    """
    A model for a revise query in HyQL.

    This model is used to update existing data in a shelf. It allows you to specify conditions that must be met before the data is written.
    In SQL, it would be similar to an UPDATE query.

    Attributes:
        - `path` (str): The path to the dictionary key, shelf, or section. Must be a dot separated path string from the
            library directory, e.g., `section.shelf_1.key_1`.
        - `data` (SchemaModel): The data to be written or updated at the path. Must conform to the `schema_model` defined
            in the section.

    Notes:
        - The `data` attribute requires a SchemaModel. This approach ensures type safety by enforcing that all data
          conforms to a predefined schema, reducing runtime errors and enhancing IDE suggestions.

    Examples:
        ```Python
        from hylladb import HyllaDB
        from hylladb.hyql import Operators, Revise, CheckOut, Condition, ConditionDict, Group, SortItem
        from hylladb.hyql.hyql_base.schema_model import SchemaModel

        hylladb = HyllaDB()

        # User Schema previously defined.
        # class UserData(SchemaModel):
        #     field1: str
        #     field2: str

        # Define the condition for checking out user data.
        condition = Condition(
            left_path="section_1.sub_section_1.shelf_1.field1",
            operator="=",
            right="old_value1",
        )
        condition_dict = ConditionDict(condition=condition)

        # Example checkout query to get user data.
        checkout_query = CheckOut(
            path="section_1.sub_section_1",
            checkout=["shelf_1.field1", "shelf_1.field2"],
            filters=[condition_dict],
            sort=[SortItem(path="section_1.field1")],
            limit=1,
            offset=0
        )
        ```
    """

    path: str = Field(**path_dict)
    data: Any  # Must be a subclass of SchemaModel

    @field_validator("data", mode="before")
    def validate_is_schema_model(cls, data) -> Any:
        """Validates that the data is a SchemaModel instance."""

        return validators.validate_is_schema_model(data)

    # @field_validator("filters")
    # def _validate_filters_format(cls, value) -> list[Union[ConditionDict, Group, str]]:
    #     """Validates the format of the filters list."""
    #     return validators.validate_group_format(value, [ConditionDict, Group])


class Remove(HyQLBaseModel):
    """
    A model for a remove query in HyQL.

    This model is used to remove data from a shelf, or to remove the shelf itself. It is similar to the `Write` model, but allows you to specify
    conditions that must be met before the data is removed. In SQL it would be similar to a `DELETE` query with a `WHERE` clause.

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
        Remove(**hylladb_remove)
        ```
    """

    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    remove_shelf: bool = False
    remove_section: bool = False

    @model_validator(mode="after")
    def _validate_only_one_bool_is_true(cls, data) -> Any:
        """Ensures that only one of `remove_shelf` or `remove_section` is True."""

        validators.validate_only_one_bool_is_true(
            data, ("remove_shelf", "remove_section")
        )

    @field_validator("filters")
    def _validate_filters_format(cls, value) -> list[Union[ConditionDict, Group, str]]:
        """Validates the format of the filters list."""

        return validators.validate_group_format(value, [ConditionDict, Group])


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
        Reset(**hylladb_reset)
        ```
    """

    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    reset_shelf: bool = False
    reset_section: bool = False

    @model_validator(mode="after")
    def _validate_only_one_bool_is_true(cls, data) -> Any:
        """Ensures that only one of `reset_shelf` or `reset_section` is True."""

        validators.validate_only_one_bool_is_true(
            data, ("reset_shelf", "reset_section")
        )

    @field_validator("filters")
    def _validate_filters_format(cls, value) -> list[Union[ConditionDict, Group, str]]:
        """Validates the format of the filters list."""

        return validators.validate_group_format(value, [ConditionDict, Group])


class Transaction(HyQLBaseModel):
    """
    A model for a batch transaction in a HyQL query.

    This model allows for executing multiple queries in a single transaction. It supports a variety of query operations, such as `Write`, `Remove`, `Revise`, `CheckOut`, `BuildShelf`, `BuildSection`, `SetSchema`, and `Reset`.

    The purpose of this model is to provide a way to define a batch of queries, which can then be executed in a single transaction.

    Attributes:
        - `queries` (list[Union[Write, Remove, Revise, CheckOut, BuildShelf, BuildSection, SetSchema, Reset]]): A list of query operations to be executed in the transaction.

    Examples:
        ```Python
        from hylladb.hyql import Transaction, Write, Remove, CheckOut, SetSchema

        # Example transaction query. Can be done by instantiating the models directly or
        # by unpacking dicts to the models.
        hylladb_transaction: dict = {
            "queries": [
                {
                    "path": "path1.sub_path1",
                    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
                },
                {
                    "path": "path1.sub_path2",
                    "filters": [
                        {
                            "condition": {
                                "left": "path1.sub_path2.field1",
                                "operator": "==",
                                "right": "value2",
                            }
                        }
                    ],
                    "remove_shelf": True,
                },
                {
                    "checkout": [
                        {
                            "path": "section_1.sub_section_1",
                            "checkout": ["shelf_1.field1", "shelf_1.field2"],
                        },
                    ],
                    "filters": [
                        {
                            "condition": {
                                "left": "section_1.sub_section_1.shelf_1.field1",
                                "operator": ">=",
                                "right": 1,
                            }
                        }
                    ],
                    "sort": [{"path": "section_1.field1"}],
                    "limit": 10,
                    "offset": 0,
                },
            ]
        }

        # Instantiate the model by unpacking the dict.
        transaction = Transaction(**hylladb_transaction)

        # Pass it into the HyQL query method.
        ```
    """

    queries: list[
        Union[
            Write, Remove, Revise, CheckOut, BuildShelf, BuildSection, SetSchema, Reset
        ]
    ]
