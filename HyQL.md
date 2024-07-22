# 🌐 🇸🇪 🔍 HyQL - Hylla Query Language

## Overview

HyQL (Hylla Query Language) is a querying language tailored for HyllaDB, enabling users to fetch and manipulate data through a structured, readable syntax. It is inspired by GraphQL and glom, focusing on simplicity and expressiveness.

## 🛠️ Core Components

### 1. Condition

Represents a single condition in a HyQL query.

```python
class Condition(HyQLBaseModel):
    left: Any
    operator: str
    right: Any
    left_is_path: bool = True
    right_is_path: bool = False
```

### 2. ConditionDict

A wrapper for a single condition.

```python
class ConditionDict(HyQLBaseModel):
    condition: Condition
```

### 3. Group

Represents a group of conditions in a HyQL query.

```python
class Group(HyQLBaseModel):
    group: list[Union[ConditionDict, "Group", str]]
```

### 4. CheckOutItem

Represents a single checkout item in a HyQL query.

```python
class CheckOutItem(HyQLBaseModel):
    path: str | None = Field(default=None, **hyql_utils.path_dict)
    checkout: list[str] | list[Literal["*all"]] = Field(
        ["*all"],
        description="A list of keys to be checked out. If the list contains only '*all', all keys will be checked out.",
    )
```

### 5. SortItem

Represents a single sort item in a HyQL query.

```python
class SortItem(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    order: str = Field("asc", pattern=r"^(asc|desc)$")
```

## 📊 Query Types

### 1. CheckOut

Used for retrieving data from HyllaDB.

```python
class CheckOut(HyQLBaseModel):
    checkout: list[CheckOutItem]
    filters: list[ConditionDict | Group | str] | None = None
    sort: list[SortItem] | None = None
    limit: int | None = Field(None, ge=1)
    offset: int | None = Field(None, ge=0)
```

### 2. Write

Used for writing data to HyllaDB.

```python
class Write(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    data: dict[str, Any]
```

### 3. Revise

Used for updating existing data in HyllaDB.

```python
class Revise(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    data: dict[str, Any]
```

### 4. Remove

Used for removing data from HyllaDB.

```python
class Remove(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    remove_shelf: bool = False
    remove_section: bool = False
```

### 5. Reset

Used for resetting data in HyllaDB.

```python
class Reset(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    reset_shelf: bool = False
    reset_section: bool = False
```

### 6. SetSchema

Used for setting or updating the schema for a section or the library.

```python
class SetSchema(HyQLBaseModel):
    path: str | None = Field(default=None, **hyql_utils.path_dict)
    schema_model: type[ShelfModel] = Field(
        ..., description="The schema for the section or library."
    )
    is_library: bool = False
```

### 7. BuildShelf

Used for building a new shelf in HyllaDB.

```python
class BuildShelf(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    name: str = Field(pattern=r"^[A-Za-z0-9]+(?:[_][A-Za-z0-9]+)*$")
    data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
```

### 8. BuildSection

Used for building a new section in HyllaDB.

```python
class BuildSection(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    name: str = Field(pattern=r"^[A-Za-z0-9]+(?:[_][A-Za-z0-9]+)*$")
    schema_model: ShelfModel | None
    metadata: dict[str, Any] | None = None
```

## 🔍 Query Processing Steps

1. **Parsing:** The HyQL query is parsed and broken down into its components (paths, fields, filters).
2. **Validation:** The query is validated against the appropriate model (e.g., CheckOut, Write, Revise).
3. **Path Resolution:** The specified path is navigated to locate the target shelf or section.
4. **Data Retrieval/Manipulation:** Depending on the query type, data is fetched, written, updated, or removed.
5. **Filter Application:** Any filter conditions are applied to the retrieved or affected data.
6. **Response Formation:** The final step where the data, conforming to the structure of the query, is compiled and returned.

## 💡 Best Practices and Usage Tips

1. **Clarity:** Keep queries as clear and concise as possible.
2. **Field Selection:** In CheckOut queries, request only the fields you need to optimize performance.
3. **Filtering:** Use filters judiciously to retrieve or affect specific data subsets.
4. **Path Accuracy:** Ensure that the paths in your queries accurately reflect the structure of your HyllaDB.
5. **Schema Consistency:** When using SetSchema, ensure that your schema model is consistent with the data you plan to store.
6. **Error Handling:** Always handle potential errors, especially when dealing with filters that might not match any data.
7. **Limit and Offset:** Use these in CheckOut queries to paginate through large datasets efficiently.

## 📦 Example Usage

For each query type, we'll demonstrate how to construct the query both by using the classes directly and by using dictionary unpacking.

### SetSchema

```python
from hylladb.db.models import ShelfModel
from hylladb.hyql import SetSchema

# Define the schema
class AnimalSchema(ShelfModel):
    name: str

# Using classes directly
set_schema_query = SetSchema(
    path="path1.sub_path1",
    schema_model=AnimalSchema
)

# Using dictionary unpacking
set_schema_dict = {
    "path": "path1.sub_path1",
    "schema_model": AnimalSchema,
}
set_schema_query = SetSchema(**set_schema_dict)

print(set_schema_query)
```

This sets a schema for the "path1.sub_path1" path using the AnimalSchema.

### BuildShelf

```python
from hylladb.hyql import BuildShelf

# Using classes directly
build_shelf_query = BuildShelf(
    path="path1.sub_path1",
    name="name1",
    data={"sub_path1.field1": "value1", "sub_path1.field2": "value2"}
)

# Using dictionary unpacking
build_shelf_dict = {
    "path": "path1.sub_path1",
    "name": "name1",
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}
build_shelf_query = BuildShelf(**build_shelf_dict)

print(build_shelf_query)
```

This builds a new shelf named "name1" at "path1.sub_path1" with the specified data.

### CheckOut

```python
from hylladb.hyql import CheckOut, CheckOutItem, Condition, ConditionDict, Group, SortItem, Operators

# Using classes directly
checkout_query = CheckOut(
    checkout=[
        CheckOutItem(
            path="section_1.sub_section_1",
            checkout=["shelf_1.field1", "shelf_1.field2"]
        ),
        CheckOutItem(
            path="section_2",
            checkout=["*all"]
        )
    ],
    filters=[
        ConditionDict(
            condition=Condition(
                left="path1.field1",
                operator=">=",
                right=1
            )
        ),
        "AND",
        Group(
            group=[
                ConditionDict(
                    condition=Condition(
                        left="name",
                        operator=Operators.IN,
                        right="path1.field2",
                        left_is_path=False,
                        right_is_path=True
                    )
                ),
                "OR",
                ConditionDict(
                    condition=Condition(
                        left="path2.field3",
                        operator="<",
                        right="path1.field2",
                        right_is_path=True
                    )
                )
            ]
        )
    ],
    sort=[SortItem(path="path1.field1")],
    limit=10,
    offset=0
)

# Using dictionary unpacking
checkout_dict = {
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
checkout_query = CheckOut(**checkout_dict)

print(checkout_query)
```

This complex checkout query demonstrates nested conditions, multiple checkouts, sorting, and pagination.

### Write

```python
from hylladb.hyql import Write

# Using classes directly
write_query = Write(
    path="path1.sub_path1",
    data={"sub_path1.field1": "value1", "sub_path1.field2": "value2"}
)

# Using dictionary unpacking
write_dict = {
    "path": "path1.sub_path1",
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}
write_query = Write(**write_dict)

print(write_query)
```

This writes new data to "path1.sub_path1".

### Revise

```python
from hylladb.hyql import Revise, Condition, ConditionDict, Group

# Using classes directly
revise_query = Revise(
    path="path1.sub_path1",
    filters=[
        ConditionDict(
            condition=Condition(
                left="path1.field1",
                operator="==",
                right="value1"
            )
        ),
        "AND",
        Group(
            group=[
                ConditionDict(
                    condition=Condition(
                        left="path1.field2",
                        operator=">",
                        right=100
                    )
                ),
                "OR",
                ConditionDict(
                    condition=Condition(
                        left="path2.field3",
                        operator="<",
                        right="path1.field2",
                        right_is_path=True
                    )
                )
            ]
        )
    ],
    data={"sub_path1.field1": "value1", "sub_path1.field2": "value2"}
)

# Using dictionary unpacking
revise_dict = {
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
revise_query = Revise(**revise_dict)

print(revise_query)
```

This revises data at "path1.sub_path1" based on complex filter conditions.

### Remove

```python
from hylladb.hyql import Remove, Condition, ConditionDict, Group

# Using classes directly
remove_query = Remove(
    path="path1.sub_path1",
    filters=[
        ConditionDict(
            condition=Condition(
                left="path1.field1",
                operator="==",
                right="value1"
            )
        ),
        "AND",
        Group(
            group=[
                ConditionDict(
                    condition=Condition(
                        left="path1.field2",
                        operator=">",
                        right=100
                    )
                ),
                "OR",
                ConditionDict(
                    condition=Condition(
                        left="path2.field3",
                        operator="<",
                        right="path1.field2",
                        right_is_path=True
                    )
                )
            ]
        )
    ]
)

# Using dictionary unpacking
remove_dict = {
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
remove_query = Remove(**remove_dict)

print(remove_query)
```

This removes data from "path1.sub_path1" based on the specified filters.

### Reset

```python
from hylladb.hyql import Reset, Condition, ConditionDict

# Using classes directly
reset_query = Reset(
    path="path1.sub_path1",
    filters=[
        ConditionDict(
            condition=Condition(
                left="path1.field1",
                operator="==",
                right="value1"
            )
        )
    ],
    reset_shelf=True
)

# Using dictionary unpacking
reset_dict = {
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
reset_query = Reset(**reset_dict)

print(reset_query)
```

This resets the shelf at "path1.sub_path1" based on the specified filter.

## 🔀 Combining Query Types

In practice, you might need to combine multiple query types to achieve complex operations. Here's an example of how you might use multiple query types in sequence:

```python
from hylladb.db.models import ShelfModel
from hylladb.hyql import SetSchema, BuildShelf, Write, CheckOut

# Define a schema
class BookSchema(ShelfModel):
    title: str
    author: str
    year: int

# Set the schema
set_schema_query = SetSchema(
    path="library.fiction",
    schema_model=BookSchema
)

# Build a new shelf
build_shelf_query = BuildShelf(
    path="library.fiction",
    name="sci_fi",
    data={"title": "Dune", "author": "Frank Herbert", "year": 1965}
)

# Write additional data
write_query = Write(
    path="library.fiction.sci_fi",
    data={"genre": "Science Fiction"}
)

# Check out the data
checkout_query = CheckOut(
    checkout=[
        CheckOutItem(
            path="library.fiction.sci_fi",
            checkout=["*all"]
        )
    ]
)

# In a real application, you would execute these queries against your HyllaDB instance and handle the results appropriately.
```

This example demonstrates how you might set up a schema, build a shelf, write additional data, and then retrieve that data, all using different HyQL query types.

## 🧠 Advanced Usage

### Dynamic Query Building

HyQL's flexibility allows for dynamic query building, which can be useful in scenarios where the query structure needs to be determined at runtime. Here's an example:

```python
def build_dynamic_checkout(paths, conditions):
    checkout_items = [CheckOutItem(path=path, checkout=["*all"]) for path in paths]

    filters = []
    for i, condition in enumerate(conditions):
        filters.append(ConditionDict(condition=Condition(**condition)))
        if i < len(conditions) - 1:
            filters.append("AND")

    return CheckOut(
        checkout=checkout_items,
        filters=filters
    )

# Usage
paths = ["library.fiction", "library.non_fiction"]
conditions = [
    {"left": "year", "operator": ">", "right": 2000},
    {"left": "rating", "operator": ">=", "right": 4.5}
]

dynamic_query = build_dynamic_checkout(paths, conditions)
print(dynamic_query)
```

This function allows you to build a checkout query dynamically based on a list of paths and conditions.

## 🎭 Error Handling

When working with HyQL, it's important to handle potential errors gracefully. Here are some common errors you might encounter and how to handle them:

1. **ValidationError**: This occurs when the data doesn't match the schema.

```python
from pydantic import ValidationError

try:
    checkout_query = CheckOut(**checkout_dict)
except ValidationError as e:
    print(f"Invalid query structure: {e}")
```

2. **ValueError**: This might occur if you provide invalid values, like a negative limit.

```python
try:
    checkout_query = CheckOut(
        checkout=[CheckOutItem(path="library", checkout=["*all"])],
        limit=-1
    )
except ValueError as e:
    print(f"Invalid value in query: {e}")
```

3. **KeyError**: This could happen if you're trying to access a key that doesn't exist in your data structure.

```python
try:
    result = execute_query(checkout_query)
    print(result['non_existent_key'])
except KeyError as e:
    print(f"Trying to access non-existent key: {e}")
```

Always wrap your HyQL operations in appropriate try-except blocks to handle errors gracefully and provide meaningful feedback.

## 🏁 Conclusion

HyQL provides a powerful and flexible way to interact with HyllaDB. By understanding its components and how to construct queries, you can efficiently retrieve, manipulate, and manage your data. Remember to always validate your queries, handle errors appropriately, and consider the structure of your data when designing your queries.

As you become more familiar with HyQL, you'll find that it offers a balance between simplicity and expressiveness, allowing you to perform complex operations with clean, readable code. Happy querying!
