# 🏛️📚🔎 HyQL - Hylla Query Language

## Overview

HyQL (Hylla Query Language) is a querying language tailored for HyllaDB, enabling users to fetch and manipulate data through a structured, readable syntax. It is inspired by GraphQL and the Python `glom` library, focusing on simplicity and expressiveness.

## 🌟 Inspiration and Philosophy

HyQL represents a departure from traditional query languages by employing Pydantic models to articulate queries. This approach, drawing inspiration from the Python `glom` library's handling of nested dictionaries and the versatility of GraphQL queries, aims to provide clarity in query construction, ensure type safety, and maintain integrity in data interaction.

HyllaDB, the database system for which HyQL is designed, is built with a focus on speed, flexibility, and customizability of data storage. Its architecture is inspired by modular systems, offering building blocks to construct a database tailored to specific needs.

## 🏗️ HyllaDB Architecture

HyllaDB is organized into three primary layers:

1. **Library**: The foundational layer, serving as the primary directory of the database.
2. **Sections**: Analogous to sections in a library, these allow for structured organization of data.
3. **Shelves**: Representing individual storage units, these hold data in the form of flat or nested dictionaries.

This modular structure, coupled with HyQL's intuitive path strings, allows for efficient data access and manipulation. The architecture of HyllaDB, coupled with the intuitive navigation provided by HyQL's path strings, allows for swift and efficient data access and manipulation.

Certainly. Here's a brief section explaining dictionary unpacking with a simple example:

## Dictionary Unpacking

All HyQL models support dictionary unpacking for instantiation. This allows you to create model instances directly from dictionaries, which can be particularly useful when working with data from various sources or when constructing queries dynamically.

Example:

```python
from hylladb.hyql import CheckOut, CheckOutItem

# Create a dictionary with the query parameters
checkout_dict = {
    "checkout": [
        {
            "path": "section_1.shelf_1",
            "checkout": ["field1", "field2"]
        }
    ],
    "limit": 10
}

# Instantiate the CheckOut model using dictionary unpacking
checkout_query = CheckOut(**checkout_dict)
```

This approach is equivalent to manually specifying each parameter but can be more convenient and flexible in many scenarios.

## 🛠️ Core Components

### 1. Condition

Represents a single condition in a HyQL query.

```python
class Condition(HyQLBaseModel):
    left: str
    operator: str
    right: Any
    right_is_path: bool = False
```

Example:

```python
from hylladb.hyql import Condition, Operators

condition_example = Condition(
    left="section1.shelf2.data_field",
    operator=Operators.GREATER_THAN,
    right=100
)
```

> Note: Remember that all models support dictionary unpacking for instantiation. See the 'Dictionary Unpacking' section for more details.

### 2. ConditionDict

A wrapper for a single condition.

```python
class ConditionDict(HyQLBaseModel):
    condition: Condition
```

Example:

```python
from hylladb.hyql import Condition, ConditionDict, Operators

condition = Condition(
    left="name",
    operator=Operators.IN,
    right="path1.field2",
    left_is_path=False,
    right_is_path=True
)
condition_dict = ConditionDict(condition=condition)
```

### 3. Group

Represents a group of conditions in a HyQL query.

```python
class Group(HyQLBaseModel):
    group: list[Union[ConditionDict, "Group", str]]
```

Example:

```python
from hylladb.hyql import Condition, ConditionDict, Group, Operators

group_example = Group(group=[
    ConditionDict(condition=Condition(left="field1", operator=Operators.EQUAL, right=10)),
    "AND",
    ConditionDict(condition=Condition(left="field2", operator=Operators.GREATER_THAN, right=20))
])
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

Example:

```python
from hylladb.hyql import CheckOutItem

checkout_item = CheckOutItem(
    path="section1.shelf2",
    checkout=["data_field1", "data_field2"]
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

Example:

```python
from hylladb.hyql import CheckOut, CheckOutItem, Condition, ConditionDict, Operators

checkout = CheckOut(
    checkout=[CheckOutItem(path="section1.shelf1", checkout=["field1", "field2"])],
    filters=[
        ConditionDict(condition=Condition(left="field1", operator=Operators.EQUAL, right="value"))
    ],
    limit=10,
    offset=0
)
```

### 2. Write

Used for writing data to HyllaDB.

```python
class Write(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    data: dict[str, Any]
```

Example:

```python
from hylladb.hyql import Write

write = Write(
    path="section1.shelf1",
    data={"field1": "new_value", "field2": 42}
)
```

### 3. Revise

Used for updating existing data in HyllaDB.

```python
class Revise(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    data: dict[str, Any]
```

Example:

```python
from hylladb.hyql import Revise, Condition, ConditionDict, Operators

revise = Revise(
    path="section1.shelf1",
    filters=[
        ConditionDict(condition=Condition(left="field1", operator=Operators.EQUAL, right="old_value"))
    ],
    data={"field1": "new_value", "field2": 42}
)
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

Example:

```python
from hylladb.hyql import Remove, Condition, ConditionDict, Operators

remove = Remove(
    path="section1.shelf1",
    filters=[
        ConditionDict(condition=Condition(left="field1", operator=Operators.EQUAL, right="value"))
    ],
    remove_shelf=False
)
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

Example:

```python
from hylladb.hyql import Reset

reset = Reset(
    path="section1.shelf1",
    reset_shelf=True
)
```

### 6. SetSchema

Used for setting or updating the schema for a section or the library.

```python
class SetSchema(HyQLBaseModel):
    path: str | None = Field(default=None, **hyql_utils.path_dict)
    schema_model: type[SchemaModel] = Field(
        ..., description="The schema for the section or library."
    )
    is_library: bool = False
```

Example:

```python
from hylladb.hyql import SetSchema, SchemaModel

class UserSchema(SchemaModel):
    name: str
    age: int

set_schema = SetSchema(
    path="users",
    schema_model=UserSchema
)
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

Example:

```python
from hylladb.hyql import BuildShelf

build_shelf = BuildShelf(
    path="section1",
    name="new_shelf",
    data={"field1": "value1", "field2": "value2"}
)
```

### 8. BuildSection

Used for building a new section in HyllaDB.

```python
class BuildSection(HyQLBaseModel):
    path: str = Field(**hyql_utils.path_dict)
    name: str = Field(pattern=r"^[A-Za-z0-9]+(?:[_][A-Za-z0-9]+)*$")
    schema_model: SchemaModel | None
    metadata: dict[str, Any] | None = None
```

Example:

```python
from hylladb.hyql import BuildSection, SchemaModel

class SectionSchema(SchemaModel):
    field1: str
    field2: int

build_section = BuildSection(
    path="library",
    name="new_section",
    schema_model=SectionSchema
)
```

### 9. Transaction

Used for executing multiple queries in a single transaction.

```python
class Transaction(HyQLBaseModel):
    queries: list[
        Union[
            Write, Remove, Revise, CheckOut, BuildShelf, BuildSection, SetSchema, Reset
        ]
    ]
```

Example:

```python
from hylladb.hyql import Transaction, Write, Remove

transaction = Transaction(
    queries=[
        Write(path="section1.shelf1", data={"field1": "new_value"}),
        Remove(path="section1.shelf2", remove_shelf=True)
    ]
)
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
8. **Transactions:** Use the Transaction model to group multiple operations that should be executed atomically.

## 🔀 Combining Query Types

In practice, you might need to combine multiple query types to achieve complex operations. Here's an example of how you might use multiple query types in sequence:

```python
from hylladb.hyql import SetSchema, BuildSection, BuildShelf, Write, CheckOut, SchemaModel

# Define a schema
class BookSchema(SchemaModel):
    title: str
    author: str
    year: int

# Set the schema
set_schema_query = SetSchema(
    path="library",
    schema_model=BookSchema
)

# Build a new section
build_section_query = BuildSection(
    path="library",
    name="fiction",
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

This example demonstrates how you might set up a schema, build a section, build a shelf, write additional data, and then retrieve that data, all using different HyQL query types.

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

## 🚀 Performance Considerations

HyllaDB is designed with performance in mind, and HyQL queries are optimized for efficient data retrieval and manipulation. However, there are some considerations to keep in mind:

1. **Path Depth**: Deeper paths may require more time to resolve. Try to keep your data structure as flat as reasonably possible.

2. **Filter Complexity**: Complex filters with multiple nested conditions may impact query performance. Use them judiciously and consider breaking complex queries into simpler ones when possible.

3. **Data Volume**: When dealing with large datasets, make use of the `limit` and `offset` parameters in CheckOut queries to implement pagination and reduce the amount of data transferred in a single query.

4. **Indexing**: While not explicitly part of HyQL, proper indexing of your data in HyllaDB can significantly improve query performance. Consider the most common access patterns when designing your data structure.

## 🔐 Security Considerations

While HyllaDB offers flexibility in storing complex Python objects, users should be cautious when dealing with objects from untrusted sources. Consider the following best practices:

1. **Trusted Sources**: Prioritize storing objects from reliable and trusted sources.

2. **Safe Serialization**: For objects with uncertain origins, consider alternative serialization methods like JSON, which, while safer, might impact the performance benefits of using shelve.

3. **Input Validation**: Always validate and sanitize input data before storing it in HyllaDB, especially when dealing with user-supplied data.

4. **Access Control**: Implement appropriate access control mechanisms at the application level to ensure that users can only access and modify data they are authorized to.

5. **Encryption**: Consider encrypting sensitive data before storing it in HyllaDB, especially if the database is stored in a shared or potentially accessible location.

## 📦 Complex Python Object Storage

HyllaDB's use of the shelve module in Python allows for the storage of complex Python objects, including class instances like trained machine learning models from libraries such as scikit-learn or tensorflow. This flexibility is a key feature of HyllaDB, allowing users to store data in a manner that best suits their needs.

Example of storing a trained model:

```python
from sklearn.ensemble import RandomForestClassifier
from hylladb.hyql import Write

# Train your model
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Store the trained model in HyllaDB
write_query = Write(
    path="models.random_forest",
    data={"model": clf}
)

# Execute the write query...
```

While this capability offers great flexibility, it's important to be aware of the security implications, as mentioned in the security considerations section.

## 🔄 Versioning and Migration

As your data model evolves, you may need to update schemas or migrate data. While HyQL doesn't provide built-in migration tools, you can use its features to implement versioning and migration strategies:

1. **Schema Versioning**: Include a version field in your schemas to track changes over time.

```python
class BookSchemaV2(SchemaModel):
    version: int = 2
    title: str
    author: str
    year: int
    genre: str  # New field added in version 2
```

2. **Data Migration**: Use CheckOut, Revise, and Write queries in combination to migrate data from one schema version to another.

```python
# Fetch all books with the old schema
old_books = CheckOut(
    checkout=[CheckOutItem(path="library.books", checkout=["*all"])]
)

# Update each book to the new schema
for book in old_books:
    updated_book = {**book, "version": 2, "genre": "Unknown"}
    Revise(
        path=f"library.books.{book['id']}",
        data=updated_book
    )
```

3. **Backward Compatibility**: When possible, design schema changes to be backward compatible to ease the migration process.

## 🧪 Testing HyQL Queries

Testing your HyQL queries is crucial for ensuring the reliability of your data operations. Here are some strategies for effective testing:

1. **Unit Testing**: Write unit tests for individual query types, ensuring they produce the expected results.

```python
def test_checkout_query():
    query = CheckOut(
        checkout=[CheckOutItem(path="test_section", checkout=["field1", "field2"])]
    )
    result = execute_query(query)
    assert "field1" in result[0]
    assert "field2" in result[0]
```

2. **Integration Testing**: Test the interaction between different query types in a controlled environment.

3. **Mock Database**: Use a mock or in-memory database for testing to avoid affecting production data.

4. **Edge Cases**: Test with empty results, large datasets, and complex nested structures to ensure robustness.

5. **Performance Testing**: For critical queries, consider implementing performance tests to ensure they meet your speed requirements.

## 📚 Best Practices for Schema Design

When designing schemas for your HyllaDB sections, consider the following best practices:

1. **Keep it Simple**: Start with a simple schema and add complexity only as needed.

2. **Use Appropriate Data Types**: Leverage Pydantic's type system to ensure data integrity.

3. **Consider Query Patterns**: Design your schema with your most common query patterns in mind.

4. **Avoid Deep Nesting**: While HyllaDB supports nested structures, excessive nesting can complicate queries and impact performance.

5. **Use Meaningful Names**: Choose clear, descriptive names for fields to improve code readability.

Example of a well-designed schema:

```python
from pydantic import BaseModel, Field
from datetime import datetime

class Author(BaseModel):
    name: str
    birth_year: int

class Book(SchemaModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    author: Author
    published_date: datetime
    genres: list[str] = []
    in_stock: bool = True
    price: float
```

## 🏁 Conclusion

HyQL provides a powerful and flexible way to interact with HyllaDB. By understanding its components and how to construct queries, you can efficiently retrieve, manipulate, and manage your data. Remember that the modular nature of HyllaDB allows you to structure your data in a way that best suits your needs, and HyQL provides the tools to interact with that structure effectively.

As you become more familiar with HyQL, you'll find that it offers a balance between simplicity and expressiveness, allowing you to perform complex operations with clean, readable code. The addition of the Transaction model allows for atomic operations, further enhancing the capabilities of your database interactions.

Continue to explore the various query types and their combinations to unlock the full potential of HyllaDB in your applications. Happy querying!
