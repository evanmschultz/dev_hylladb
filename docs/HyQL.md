# 🏛️📚🔎 HyQL - Hylla Query Language

## Overview

HyQL (Hylla Query Language) is a querying language tailored for HyllaDB, enabling users to fetch and manipulate data through a structured, readable syntax. It is inspired by [GraphQL](https://graphql.org/) and the Python [`glom`](https://glom.readthedocs.io/en/latest/) library, focusing on simplicity and expressiveness.

## 🌟 Inspiration and Philosophy

HyQL represents a departure from traditional query languages by employing Pydantic models to articulate queries. Its approach aims to provide clarity in query construction, ensure type safety, and maintain integrity in data interaction.

HyllaDB, the database system for which HyQL is designed, is built with a focus on speed, flexibility, and customizability of data storage. Its architecture is inspired by modular systems, offering building blocks to construct a database tailored to specific needs, image Lego blocks or Ikea flat-pack furniture.

## 🏗️ HyllaDB Architecture

HyllaDB is organized into three primary layers:

1. **Library**: The foundational layer, serving as the primary directory of the database.
2. **Sections**: Analogous to sections in a library, these allow for structured organization of data.
3. **Shelves**: Representing individual storage units, these hold data in the form of flat or nested dictionaries.

This modular structure, coupled with HyQL's intuitive path strings, allows for efficient data access and manipulation. The architecture of HyllaDB, coupled with the intuitive navigation provided by HyQL's path strings, allows for swift and efficient data access and manipulation.

For a more in-depth explanation and usage of HyllaDB, refer to the [HyllaDB documentation](HyllaDB.md).

## 📔 Note on Dictionary Unpacking

All HyQL models support dictionary unpacking for instantiation, but don't require it. This allows you to create model instances directly from dictionaries, which can be particularly useful when working with data from various sources or when constructing queries dynamically.

**Example:**

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

### 1. SchemaModel

`SchemaModel` is a base class for defining schemas for all the shelves that are direct children of libraries or sections in HyllaDB. It inherits from Pydantic's `BaseModel` and provides additional functionality for defining data models.

```python
class SchemaModel(BaseModel, validate_assignment=True):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
```

It enforces strict type checking and disallows extra fields not explicitly defined in the schema inheriting from it. This ensures data integrity and consistency when interacting with the database. You will never be surprised by the data you retrieve, and explicit and clear errors will be thrown when trying to write data that doesn't conform to the schema.

The `arbitrary_types_allowed=True` configuration allows for the storage of complex Python objects, including instances of custom classes, in HyllaDB. This flexibility is a key feature of HyllaDB, enabling users to store a wide range of data types, which can include things like machine learning models, custom data structures, fully built out graphs, eg. Networkx, or any other Python object.

In traditional relational databases, this would be similar to defining a table schema. However, in HyllaDB, these schemas are more flexible and can be applied to nested data structures. In document databases like MongoDB, this would be similar to enforcing a schema on collections, but with stricter typing.

**Example:**

```python
from hylladb.hyql import SchemaModel, SetSchema

class AnimalSchema(SchemaModel):
    name: str
    age: int
    species: str

# Set the schema for the path1.sub_path1 section to the AnimalSchema
set_schema_dict = {
    "path": "path1.sub_path1",
    "schema_model": AnimalSchema,
}
SetSchema(**set_schema_dict)
```

### 2. Condition

The `Condition` class represents a single condition in a HyQL query. It is used to define filtering criteria for queries.

```python
class Condition(HyQLBaseModel):
    left_path: str = Field(**path_dict)
    operator: str
    right: Any
    right_is_path: bool = False
```

In SQL databases, this would be equivalent to a WHERE clause condition. In MongoDB, it's similar to the query operators in find() methods. The key difference in HyllaDB is the use of path strings to navigate nested data structures, which is more similar to JSON path expressions.

**Attributes:**

-   `left_path` (str): The path to the shelf or section. Must be a dot-separated path string from the library directory.
    -   eg. "section_1.shelf_1.key_1"
-   `operator` (str): The operator used to compare the left and right operands.
-   `right` (Any): The right operand of the condition, which can be a value or a path.
-   `right_is_path` (bool): A flag indicating if the right operand is a path. Defaults to `False`.

**Example:**

```python
from hylladb.hyql import Condition, Operators

condition = Condition(
    left_path="books.sci_fi.rating",
    operator=Operators.GREATER_THAN, # This is equivalent to the ">", which would be an equally valid input for the `operator` attribute
    right=4.5
)
```

### 3. ConditionDict

`ConditionDict` is a wrapper for a single condition, used to simplify the creation of condition lists in queries.

```python
class ConditionDict(HyQLBaseModel):
    condition: Condition
```

This doesn't have a direct equivalent in traditional databases. It's a structural element specific to HyQL that helps in organizing complex query conditions. In SQL, this might be represented as part of a complex WHERE clause.

> **Note**: The both the `ConditionDict` and the `Condition` classes are necessary when writing a query that requires filtering. As of now, the only reason for the existence of the `ConditionDict` class is to allow for dictionary unpacking of complex nested dictionaries when creating a query, more akin to what you would see with [GraphQL](https://graphql.org/). This is a design choice to make the query creation process more intuitive and user-friendly.
>
> If you know a better way to achieve this, please create an Issue or make a Pull Request.

**Example:**

```python
from hylladb.hyql import Condition, ConditionDict, Operators

condition = Condition(
    left_path="books.sci_fi.published_year",
    operator=Operators.GREATER_THAN,
    right=2000
)
condition_dict = ConditionDict(condition=condition)
```

### 4. Group

The `Group` class represents a group of conditions in a HyQL query, allowing for complex filtering logic.

```python
class Group(HyQLBaseModel):
    group: list[Union[ConditionDict, "Group", str]]
```

This is similar to using parentheses to group conditions in SQL WHERE clauses. In MongoDB, it's akin to using $and and $or operators to combine multiple conditions. The key difference in HyQL is the explicit structure provided by the Group class.

**Example:**

```python
from hylladb.hyql import Condition, ConditionDict, Group, Operators

group = Group(group=[
    ConditionDict(condition=Condition(left_path="books.sci_fi.rating", operator=Operators.GREATER_THAN, right=4.0)),
    "AND",
    ConditionDict(condition=Condition(left_path="books.sci_fi.published_year", operator=Operators.GREATER_THAN, right=2010))
])
```

> **Note**: When using groups you provide a list that contains either `ConditionDict` instances, `Group` instances, or strings representing logical operators. The strings can be either "AND" or "OR" and must be only used to separate two instances of either `ConditionDict` or `Group`.
>
> Currently, there is no enum for this as it feels it would be redundant and unnecessary. If you feel that this is a mistake, please create an Issue or make a Pull Request.

### 5. SortItem

`SortItem` represents a single sort item in a HyQL query, used to specify the sorting order of query results.

```python
class SortItem(HyQLBaseModel):
    path: str = Field(**path_dict)
    order: str = Field("asc", pattern=r"^(asc|desc)$")
```

This is equivalent to the ORDER BY clause in SQL or the sort() method in MongoDB. The main difference is the use of path strings to specify the sort field, which allows for sorting on nested attributes.

**Attributes:**

-   `path` (str): The path to the field to sort by.
-   `order` (str): The sort order, either 'asc' for ascending or 'desc' for descending.

**Example:**

```python
from hylladb.hyql import SortItem

sort_item = SortItem(path="books.sci_fi.published_year", order="desc")
```

## ⚙️ Operators

HyQL provides a set of optional operator enums to facilitate the construction of query conditions. These enums offer a type-safe way to specify operators, while making it easier to add a filter without memorizing syntax. They can also be used interchangeably with their string representations.

### Types of Operators

1. **BasicComparisonOperators**: For basic comparisons (e.g., equality, inequality)
2. **StringOperators**: For string-specific operations (e.g., contains, starts_with)
3. **CollectionOperators**: For operations on collections (e.g., in, not in, any)
4. **LogicalOperators**: For combining conditions (e.g., and, or, not)
5. **IdentityOperators**: For identity and type checks (e.g., is, is not)
6. **NumericOperators**: For numeric comparisons (e.g., abs_eq, abs_gt)
7. **DateTimeOperators**: For date and time comparisons (e.g., date_eq, date_before)
8. **Operators**: An enum that combines all the above operators for convenience

### Usage Examples

You can use either the enum member or its string representation in conditions:

```python
from hylladb.hyql import Condition, Operators, StringOperators

# Using enum
condition1 = Condition(
    left_path="books.rating",
    operator=Operators.GREATER_THAN, # This is equivalent to the string ">", or BasicComparisonOperators.GREATER_THAN
    right=4.5
)

# Using string
condition2 = Condition(
    left_path="books.title",
    operator="contains", # This is equivalent to Operators.CONTAINS, StringOperators.CONTAINS
    right="Python"
)

# All are valid and equivalent to their respective operations
```

This flexibility allows you to use whichever format you find more convenient or readable in your code. The enum provides the benefit of autocomplete and type checking in IDEs, while strings offer a more concise syntax.

## 📊 Query Types

### 1. SetSchema

`SetSchema` is used for setting or updating the schema for a section or the library.

> **Note**: When creating a section, or allowing a library to have shelves as direct children, it is necessary to set a schema for the section or library. This is to ensure that the data stored in the shelves conforms to a specific structure, which can be enforced by the schema.

```python
class SetSchema(HyQLBaseModel):
    path: str | None = Field(default=None, **path_dict)
    schema_model: type[SchemaModel] = Field(
        ..., description="The schema for the section or library."
    )
    is_library: bool = False
```

This operation doesn't have a direct equivalent in traditional SQL databases, where schemas are typically defined when creating tables. It's more similar to schema validation in MongoDB, but with stronger typing. In HyllaDB, it allows for dynamic schema updates and application to nested data structures.

**Attributes:**

-   `path` (str | None): The path to the section. If `None`, the schema will be set for the library.
-   `schema_model` (type[SchemaModel]): The schema for the section or library.
-   `is_library` (bool): A flag indicating if the schema is for the library. Defaults to `False`.

**Example:**

```python
from hylladb.hyql import SetSchema, SchemaModel

class BookSchema(SchemaModel):
    title: str
    author: str
    published_year: int

set_schema = SetSchema(
    path="library.books",
    schema_model=BookSchema
)
```

### 2. BuildShelf

`BuildShelf` is used for creating a new shelf in HyllaDB.

```python
class BuildShelf(HyQLBaseModel):
    path: str = Field(**path_dict)
    name: str = Field(pattern=name_pattern)
    data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
```

This is somewhat analogous to creating a new table in SQL databases or a new collection in MongoDB. In HyllaDB, shelves are the primary storage units for data and the reason complex data structures can be stored.

> **Note**: This uses the `python` `shelve` module and file format. This can introduce security risks if you are not careful with the data you store in the shelves. Please take precautions when storing `python` objects from untrusted sources, or users as the code could be run on your machine when the object is loaded.

**Attributes:**

-   `path` (str): The path to the section where the shelf will be created. Must be a dot-separated path string from the library directory.
    -   eg. `"section_1.shelf_1.key_1"`
-   `name` (str): The name of the new shelf. Must follow python naming conventions.
    -   eg. `"sci_fi"`
-   `data` (SchemaModel | None): The data to be written to the path.
    -   If passing in data you must use a `SchemaModel` instance as defined by the `SchemaModel` class for the respective library or section the shelf is a direct child of.
-   `metadata` (dict[str, Any] | None): Additional metadata you wish for the shelf.

**Example:**

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

### 3. BuildSection

`BuildSection` is used for creating a new section in HyllaDB. Sections are used to organize related shelves and enforce a common schema. They are akin to different sections of a library which will store books on similar topics.

```python
class BuildSection(HyQLBaseModel):
    path: str = Field(**path_dict)
    name: str = Field(pattern=name_pattern)
    schema_model: SchemaModel | None
    metadata: dict[str, Any] | None = None
```

Sections in HyllaDB are similar to `tables` in SQL databases, but with added flexibility and the ability to enforce a schema at the section level. This means that you can organize related data in a structured manner and define specific data types for each section. In MongoDB, creating a new section with a specific schema is similar to creating a new collection. In a key-value store, it is similar to creating a new namespace or bucket. Sections in HyllaDB provide a powerful way to organize and manage your data effectively while allowing for flexibility, nesting, schema enforcement, and can be adapted to your specific use case.

**Attributes:**

-   `path` (str): The path where the new section will be created.
-   `name` (str): The name of the new section.
-   `schema_model` (SchemaModel | None): The schema for the new section.
-   `metadata` (dict[str, Any] | None): Additional metadata for the section.

**Example:**

```python
from hylladb.hyql import BuildSection, SchemaModel

class BookSchema(SchemaModel):
    title: str
    author: str
    published_year: int

build_section = BuildSection(
    path="library",
    name="books",
    schema_model=BookSchema,
    metadata={"description": "All books in the library"}
)
```

### 4. Write

Used for writing data to HyllaDB.

```python
class Write(HyQLBaseModel):
    path: str = Field(**path_dict)
    data: SchemaModel
```

**Attributes:**

-   `path` (str): The path to the dictionary key, shelf, or section in HyllaDB.
    -   It must be a dot-separated path string from the library directory, e.g., "section.shelf_1".
-   `data` (SchemaModel): The data to be written or upserted to the specified path. This must be an instance of a SchemaModel, which defines the structure and types of the data being written.

> **Note**: The use of `SchemaModel` ensures that the data being written conforms to a specific schema, providing type safety and data integrity. This is a key feature of HyllaDB that allows for structured data storage and retrieval.
>
> It will however reduce some flexibility as you will need to always pass in the entire data structure, even if you only want to update a single field. This is a trade-off for the type safety and data integrity that the `SchemaModel` provides.
>
> When defining schemas for the shelves in sections or libraries keep this trade-off in mind as too much nesting at the shelf level will result in a lot of data being transferred, increasing time complexity and potentially reducing performance.

The Write class in HyQL is designed for inserting new data, similar to certain operations found in different database systems. In SQL databases, it's comparable to an INSERT operation for adding new records. In MongoDB, it's akin to the insertOne() method for creating new documents. In key-value stores, it resembles a PUT operation when adding a new key-value pair, but unlike typical PUT operations, it won't update existing data.

The Write class in HyQL is specifically for adding new data to the specified path in the database. This approach prevents accidental overwrites of existing data, ensuring that updates are always intentional and handled separately.

**Example:**

Here's an example of how to use the Write class:

```python
from hylladb.hyql import Write, SchemaModel

# Define a schema for the data
class BookSchema(SchemaModel):
    title: str
    author: str
    year: int

# Create an instance of the schema with data
book_data = BookSchema(title="1984", author="George Orwell", year=1949)

# Create a Write instance
write_query = Write(
    path="library.fiction.dystopian",
    data=book_data
)

# The write_query can now be executed using the appropriate method in HyllaDB
# For example: execute_query(write_query)
```

In this example, we define a `BookSchema` that specifies the structure of our data. We then create an instance of this schema with specific book data. Finally, we create a `Write` instance, specifying the path where we want to write the data in our HyllaDB structure, and the data itself. This `Write` instance can then be executed to perform the actual write operation in the database.

### 5. CheckOut

`CheckOut` is used for retrieving data from HyllaDB.

```python
class CheckOut(HyQLBaseModel):
    path: str | None = Field(None, **path_dict)
    checkout: list[str | Literal["*all"]] = Field(
        ["*all"],
        description="A list of shelf names to be checked out. If the list contains only '*all', all shelves will be checked out that match the filter data.",
    )
    filters: list[Union["ConditionDict", "Group", str]] | None = None
    sort: list["SortItem"] | None = None
    limit: int | None = Field(None, ge=1)
    offset: int | None = Field(None, ge=0)
```

This is equivalent to a SELECT statement in SQL, a find() operation in MongoDB, or a GET operation in key-value stores. The key differences are the use of path strings to navigate nested data structures.
This will give you the entire data object, or objects, in the structure defined by the schema model, for the specified path and shelves.

**Attributes:**

-   path (str | None): The path to the shelf or section to check out from. If None, the entire library will be checked out.

    -   It must be a dot-separated path string from the library directory, e.g., "section.shelf_1".

-   checkout (list[str | Literal["*all"]]): A list of shelf names to be checked out.

    -   If the list contains only '\*all', all shelves will be checked out that match the filter data.
    -   If wishing to checkout specific shelves, provide a list of the shelf names you wish to checkout, or leave the default value of ["*all"] to checkout all shelves that fit the filter data.

-   filters (list[Union["ConditionDict", "Group", str]] | None): Conditions to filter the data.
-   sort (list["SortItem"] | None): Sorting instructions for the results.
-   limit (int | None): The maximum number of results to return.
-   offset (int | None): The number of results to skip.

> Note: When checking out a shelf, the entire SchemaModel object defined for that shelf in the library or section will be returned. It is not possible to checkout individual keys from a shelf.

**Example:**

```python
    from hylladb.hyql import CheckOut, CheckOutItem, Condition, ConditionDict, SortItem, Operators

    checkout = CheckOut(
        path="library.books",
        checkout=["sci_fi", "fantasy"],
        filters=[
        ConditionDict(condition=Condition(
        left_path="published_year",
        operator=Operators.GREATER_THAN,
        right=2000
        ))
        ],
        sort=[SortItem(path="published_year", order="desc")],
        limit=10,
        offset=0
    )

```

This example will checkout the data from the shelves in the 'sci_fi' and 'fantasy' sections from the 'books' section of the library, filtering for books published after 2000, sorted by publication year in descending order, and limiting the results to 10 items starting from the beginning of the result set.

### 6. Revise

`Revise` is used for updating existing data in HyllaDB.

```python
class Revise(HyQLBaseModel):
    path: str = Field(**path_dict)
    data: SchemaModel
```

This is similar to an UPDATE statement in SQL or an update() operation in MongoDB. The main difference is that Revise operates on a specific path and uses a SchemaModel to ensure type safety and data integrity.

**Attributes:**

-   `path` (str): The path to the shelf or section to be updated.
-   `data` (SchemaModel): The updated data conforming to the defined schema.

**Example:**

```python
from hylladb.hyql import Revise, SchemaModel

class BookSchema(SchemaModel):
    title: str
    author: str
    published_year: int
    rating: float

updated_book = BookSchema(
    title="Leaves of Grass",
    author="Walt Whitman",
    published_year=1855,
    rating=4.8
)

revise = Revise(
    path="library.books.poetry.leaves_of_grass",
    data=updated_book
)
```

In this example, if a book with the path "library.books.poetry.leaves_of_grass" exists, it will be updated with the new data.

**Notes:**

-   The `Revise` model is used to update existing data in a shelf. It allows you to specify conditions that must be met before the data is written.
-   The `data` attribute requires a SchemaModel. This approach ensures type safety by enforcing that all data conforms to a predefined schema, reducing runtime errors and enhancing IDE suggestions.

### 7. Remove

`Remove` is used for removing data from HyllaDB.

```python
class Remove(HyQLBaseModel):
    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    remove_shelf: bool = False
    remove_section: bool = False
```

This is equivalent to a DELETE statement in SQL or a remove() operation in MongoDB. The key differences are the use of path strings to specify the data to be removed and the ability to remove entire shelves or sections.

**Attributes:**

-   `path` (str): The path to the shelf or section to remove data from.
-   `filters` (list[ConditionDict | Group | str] | None): Conditions to determine which data to remove.
-   `remove_shelf` (bool): Flag to remove the entire shelf.
-   `remove_section` (bool): Flag to remove the entire section.

**Example:**

```python
from hylladb.hyql import Remove, Condition, ConditionDict, Operators

remove = Remove(
    path="library.books.sci_fi",
    filters=[
        ConditionDict(condition=Condition(
            left_path="rating",
            operator=Operators.LESS_THAN,
            right=3.0
        ))
    ],
    remove_shelf=False
)
```

### 8. Reset

`Reset` is used for resetting data in HyllaDB.

```python
class Reset(HyQLBaseModel):
    path: str = Field(**path_dict)
    filters: list[ConditionDict | Group | str] | None = None
    reset_shelf: bool = False
    reset_section: bool = False
```

This operation doesn't have a direct equivalent in traditional databases. It's similar to a TRUNCATE statement in SQL, but with more granular control. In HyllaDB, you can reset specific shelves or sections, optionally based on filter conditions.

**Attributes:**

-   `path` (str): The path to the shelf or section to reset.
-   `filters` (list[ConditionDict | Group | str] | None): Conditions to determine which data to reset.
-   `reset_shelf` (bool): Flag to reset the entire shelf.
-   `reset_section` (bool): Flag to reset the entire section.

**Example:**

```python
from hylladb.hyql import Reset

reset = Reset(
    path="library.books.sci_fi",
    reset_shelf=True
)
```

...

### 9. Transaction

`Transaction` is used for executing multiple queries in a single transaction.

```python
class Transaction(HyQLBaseModel):
    queries: list[
        Union[
            Write, Remove, Revise, CheckOut, BuildShelf, BuildSection, SetSchema, Reset
        ]
    ]
```

This is similar to database transactions in SQL or multi-document transactions in MongoDB. The key difference is that HyllaDB transactions can include a variety of operation types, including schema modifications and structural changes.

**Attributes:**

-   `queries` (list[Union[Write, Remove, Revise, CheckOut, BuildShelf, BuildSection, SetSchema, Reset]]): A list of query operations to be executed in the transaction.

**Example:**

```python
from hylladb.hyql import Transaction, Write, Remove, CheckOut, SchemaModel, Condition, ConditionDict, Operators

class BookSchema(SchemaModel):
    title: str
    author: str
    published_year: int

new_book = BookSchema(title="Neuromancer", author="William Gibson", published_year=1984)

transaction = Transaction(
    queries=[
        Write(path="library.books.sci_fi.neuromancer", data=new_book),
        Remove(path="library.books.sci_fi", filters=[
            ConditionDict(condition=Condition(
                left_path="rating",
                operator=Operators.LESS_THAN,
                right=2.0
            ))
        ]),
        CheckOut(path="library.books.sci_fi", checkout=["*all"], limit=5)
    ]
)
```

This transaction adds a new book, removes low-rated books, and then retrieves the top 5 books from the sci-fi section. In a traditional SQL database, this would require multiple separate statements within a transaction block. In MongoDB, it would be similar to a multi-document transaction, but the schema modifications and hierarchical nature of the data in HyllaDB allow for more complex operations within a single transaction.

# ⚖️ Comparison with Traditional Database Systems

HyQL and HyllaDB offer a unique approach to database querying and management that combines elements from SQL, NoSQL, and Key-Value databases while introducing its own innovations. Here's a comprehensive comparison:

1. **Hierarchical Data Structure**:

    - HyllaDB: Uses a hierarchical system of libraries, sections, and shelves.
    - Traditional: SQL uses flat table structures; NoSQL often uses document-based structures.
    - Benefit: Allows for more intuitive organization of complex, nested data.

2. **Path-based Querying**:

    - HyQL: Uses dot-notation paths to navigate through the data hierarchy.
    - Traditional: SQL uses table.column notation; MongoDB uses dot notation for nested documents.
    - Benefit: More similar to JSON path expressions, intuitive for complex data structures.

3. **Schema Flexibility**:

    - HyllaDB: Enforces schemas but allows more flexibility than SQL. Schemas can be applied at different levels and updated dynamically.
    - Traditional: SQL has rigid schemas; many NoSQL databases are schemaless.
    - Benefit: Balances structure with flexibility, allowing for evolving data models.

4. **Query Structure**:

    - HyQL: Queries are structured as Python objects.
    - Traditional: SQL uses string-based queries; MongoDB uses JSON-like queries.
    - Benefit: Provides strong typing and validation at the query level.

5. **Unified Query Types**:

    - HyQL: Operations like Write, Remove, and CheckOut use a unified interface.
    - Traditional: SQL has separate syntax for SELECT, INSERT, UPDATE, and DELETE.
    - Benefit: Simplifies the API and reduces the learning curve.

6. **Transactional Capabilities**:

    - HyllaDB: Transactions can include structural and schema changes alongside data operations.
    - Traditional: Typically limited to data operations within a single database.
    - Benefit: Allows for more comprehensive and consistent database updates.

7. **Type Safety**:

    - HyQL: Leverages Pydantic models for strong type checking and data validation.
    - Traditional: SQL provides some type safety; NoSQL typically has limited type checking.
    - Benefit: Reduces runtime errors and improves data integrity.

8. **Complex Object Storage**:
    - HyllaDB: Can store complex Python objects, including class instances like ML models.
    - Traditional: Limited to basic data types or requires serialization.
    - Benefit: Allows for more flexible and powerful data storage options.

While HyQL and HyllaDB offer these unique features, it's important to consider your project's specific needs when choosing a database system. This approach may be particularly well-suited for applications dealing with complex, hierarchical data structures where type safety and query predictability are crucial.

## 🔍 Query Processing Steps

1. **Parsing:** The HyQL query is parsed and broken down into its components (paths, fields, filters).
2. **Validation:** The query is validated against the appropriate model (e.g., CheckOut, Write, Revise).
3. **Path Resolution:** The specified path is navigated to locate the target shelf or section.
4. **Data Retrieval/Manipulation:** Depending on the query type, data is fetched, written, updated, or removed.
5. **Filter Application:** Any filter conditions are applied to the retrieved or affected data.
6. **Response Formation:** The final step where the data, conforming to the structure of the query, is compiled and returned and returned as the full key/shelf (row with SQL) data according to the schema model.

## 💡 Best Practices and Usage Tips

1. **Clarity:** Keep queries as clear and concise as possible.
2. **Field Selection:** In CheckOut queries, request only the fields you need to optimize performance.
3. **Filtering:** Use filters judiciously to retrieve or affect specific data subsets.
4. **Path Accuracy:** Ensure that the paths in your queries accurately reflect the structure of your HyllaDB.
5. **Schema Consistency:** When using SetSchema, ensure that your schema model is consistent with the data you plan to store.
6. **Error Handling:** Always handle potential errors, especially when dealing with filters that might not match any data.
7. **Limit and Offset:** Use these in CheckOut queries to paginate through large datasets efficiently.
8. **Transactions:** Use the Transaction model to group multiple operations that should be executed atomically.
9. **Safety:** Always keep in mind that the nature of shelve models opens up vulnerabilities and complex object storage should only come from trusted sources or sandboxed and tested before storage.

## 🎭 Error Handling

When working with HyQL, it's important to handle potential errors gracefully. HyQL is basically a strongly typed query language. When designing your application keep in mind how Pydantic handles type checking and error handling.

> Add examples and best practices here...

## 🚀 Performance Considerations

HyllaDB is designed with performance in mind, and HyQL queries are optimized for efficient data retrieval and manipulation. However, there are some considerations to keep in mind:

1. **Path Depth**: Deeper paths may require more time to resolve. Try to keep your data structure as flat as reasonably possible. This can also work in the inverse as you will be retrieving all the data at once, so in very certain cases, a deeper path may be more efficient when it comes to specific retrieval, especially as you can nest schema models.

2. **Filter Complexity**: Complex filters with multiple nested conditions may impact query performance. Use them judiciously and consider breaking complex queries into simpler ones when possible.

3. **Data Volume**: When dealing with large datasets, make use of the `limit` and `offset` parameters in CheckOut queries to implement pagination and reduce the amount of data transferred in a single query.

## 🔐 Security Considerations

While HyllaDB offers flexibility in storing complex Python objects, users should be cautious when dealing with objects from untrusted sources. Consider the following best practices:

> **Note:** HyllaDB is an experimental, thought-experiment database system and should not be used in production environments without extensive testing and security considerations.
>
> Maybe in the future, this will change, but as of now, it is not recommended to use HyllaDB in production environments.

1. **Trusted Sources**: Prioritize storing objects from reliable and trusted sources.

2. **Safe Serialization**: For objects with uncertain origins, consider flattening the object, storing it as a string, or otherwise. These, while safer, might impact the performance benefits of using shelve. Shelve is best suited, as of now, for situations where you control the complex python objects stored and use the rest of the database functionality to store more standard data types that may be created by outside sources.

    > **Note:** Standard data types are unlikely to present security risks. For instance, a `str` representation of a python class object is unlikely to run when retrieved from the database, yet, this will reduce the performance benefits of using shelve.

3. **Input Validation**: Always validate and sanitize input data before storing it in HyllaDB, especially when dealing with user-supplied data.

4. **Access Control**: Implement appropriate access control mechanisms at the application level to ensure that users can only access and modify data they are authorized to.

5. **Encryption**: Consider encrypting sensitive data before storing it in HyllaDB, especially if the database is stored in a shared or potentially accessible location.

## 📦 Complex Python Object Storage

HyllaDB's use of the shelve module in Python allows for the storage of complex Python objects, including class instances like trained machine learning models from libraries such as scikit-learn or tensorflow. This flexibility is a key feature of HyllaDB, allowing users to store data in a manner that best suits their needs.

**Example of storing a trained model:**

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

As your data model evolves, you may need to update schemas or migrate data. While HyQL doesn't provide built-in migration tools, as of now, you can use its features to implement versioning and migration strategies:

1. **Schema Versioning**: Include a version field in your schemas to track changes over time.

**Example:**

```python
class BookSchemaV2(SchemaModel):
    version: int = 2
    title: str
    author: str
    year: int
    genre: str  # New field added in version 2
```

2. **Data Migration**: Use CheckOut, Revise, and Write queries in combination to migrate data from one schema version to another.

**Example:**

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

Testing your HyQL queries is crucial for ensuring the reliability of your data operations.

<!-- Here are some strategies for effective testing: -->
<!--
1. **Unit Testing**: Write unit tests for individual query types, ensuring they produce the expected results.

**Example:**

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

5. **Performance Testing**: For critical queries, consider implementing performance tests to ensure they meet your speed requirements. -->

## 📚 Best Practices for Schema Design

When designing schemas for your HyllaDB sections, consider the following best practices:

1. **Keep it Simple**: Start with a simple schema and add complexity only as needed.

    1. Only nest data as deep as necessary to prevent excessive path depth, processing overhead, and potential performance issues.
    2. Relationships, references, and foreign keys can be created with nesting if desired. # How do we make relationships more simple without explicit nesting?

2. **Use Appropriate Data Types**: Leverage Pydantic's type system to ensure data integrity.

3. **Consider Query Patterns**: Design your schema with your most common query patterns in mind.

4. **Use Meaningful Names**: Choose clear, descriptive names for fields to improve code readability.

**Example of a well-designed schema:**

```python
from datetime import datetime

from pydantic import Field
from hylladb.hyql import SchemaModel

class Author(SchemaModel):
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

# 🏁 Conclusion

HyQL (Hylla Query Language) and HyllaDB represent a novel approach to database management, offering a heretofore unseen blend of features from SQL, NoSQL, and Key-Value paradigms while introducing new and unique concepts. As we've explored throughout this documentation, HyQL provides a powerful and flexible way to interact with data, particularly suited for complex, hierarchical structures.

> **Note:** HyllaDB is an experimental, thought-experiment database system and should not be used in production environments without extensive testing and security considerations.
>
> Its use of the `shelve` module can introduce security risks if not used carefully. Please take precautions when storing complex Python objects from untrusted sources.
>
> In the future, HyllaDB may evolve to address these concerns and provide a more robust and secure database solution.

## Key takeaways include:

1. **Complex Object Storage**: The ability to store and retrieve complex Python objects, including machine learning models and graph instances, offers unique possibilities for data management, especially for research, tinkering, prototyping, and at-home projects.

2. **Hierarchical Structure and Path-based Querying**: HyQL's intuitive navigation of nested data structures.

3. **Balance of Schema Flexibility and Type Safety**: By leveraging Pydantic models, HyQL offers dynamic schema updates while maintaining strong type checking and data validation.

4. **Unified Query Interface**: The consolidation of various operations under a single interface simplifies database interactions.

While these features provide significant advantages, it's crucial to consider performance implications, particularly regarding path depth, filter complexity, and data volume. Additionally, users should be mindful of security considerations, especially when storing complex objects from untrusted sources.

HyQL and HyllaDB also offer flexibility in terms of versioning and data migration, though they require manual implementation of these strategies as, currently, there is no automated way to handle version control and migration. The testing methodologies and schema design best practices outlined in this documentation are essential for developing robust applications with HyQL.

Hopefully, the system's design philosophy of combining simplicity with expressiveness allows for clean, readable code even in complex operations even though it goes against common known practices and as such adds a complexity of its own due to its learning curve.

In conclusion, HyQL and HyllaDB represent a novel and powerful approach to database management. Who knows, maybe HyQL, will prove to be a valuable addition to your data management toolkit, offering a unique combination of flexibility, type safety, and intuitive data structuring.

Why not give it a try?
