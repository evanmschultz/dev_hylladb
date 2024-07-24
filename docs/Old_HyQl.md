Welcome to HyQL, the custom query language for HyllaDB, a database system built with speed, flexibility, and customizability of data storage in mind. HyllaDB is engineered and inspired by the ideology of an IKEA flat-pack, or rather LEGO or erector sets modularity, offering the necessary building blocks to construct a database tailored precisely to your needs.

At its core, it operates like a dictionary of dictionaries, with the added benefit of being able to store complex Python objects, including class instances, e.g., trained machine learning models from libraries like scikit-learn or tensorflow, along with more standard data types like lists, dictionaries, and more. This flexibility is a key feature of HyllaDB, allowing users to store data in a manner that best suits their needs. Similar in effect to NetworkX's documentation statement, "[It's dictionaries all the way down.](https://networkx.org/documentation/stable/reference/introduction.html#id2)"

Just as LEGO bricks enable endless possibilities, HyllaDB provides the tools for users to build a database system that is as unique and adaptable as their data requires. This documentation introduces HyQL, emphasizing its key role in interacting with the dynamic architecture of HyllaDB and highlighting the system's speed and efficiency in data retrieval.

## Purpose and Inspiration

HyQL is a paradigm shift from traditional query languages, employing Pydantic models to articulate queries. This innovative approach, inspired by the Python [`glom` library's](https://glom.readthedocs.io/) handling of nested dictionaries and the versatility of [GraphQL](https://graphql.org/) queries, presents a method that is both flexible and user-friendly. HyQL's primary aim is to provide clarity in query construction, ensuring type safety, and maintaining integrity in data interaction, making HyllaDB an optimal choice for a wide range of applications.

## HyllaDB: A Modular Database System

HyllaDB is designed with a modular, layered structure, while taking inspiration from the organization of a library. Although, forgoing the Dewey Decimal System, HyllaDB's architecture is much more flexible and adaptable. The database is organized into three layers:

**Library**: The foundational layer, serving as the primary directory of the database.

**Sections**: These are akin to sections in a library, e.g., Sciences, and then Physics. Yet, can also represent a specific 'bookcase' within a 'section' of a library. This allows for the organization of data in a structured yet flexible manner while allowing for fast read/write speeds, only dependent upon your system's I/O constraints.

**Shelves**: Resembling individual shelves, drawers, containers, or even books themselves, these shelf files hold data, be it flat or nested dictionaries. If your needs best fit it, you can forgo any use of 'sections' and simply store all your data in 'shelves' in the 'library' directory, while still keeping a nested structure. Keep in mind this would be even more constrained by your system's I/O capabilities as more data would need to be serialized/deserialized upon each read/write.

The architecture of HyllaDB, coupled with the intuitive navigation provided by HyQL's path strings, allows for swift and efficient data access and manipulation. This design not only facilitates ease of use but also optimizes lookup speeds, making data retrieval exceptionally fast.

## Speed and Flexibility

One of the core advantages of HyllaDB is its speed in data lookup and retrieval, a critical aspect in today's fast-paced digital environment. Whether you're dealing with simple data structures or complex nested objects, HyllaDB is engineered to provide quick and efficient access.

## Complex Python object storage

HyllaDB's use of the shelve module in Python allows for the storage of complex Python objects, including class instances, e.g., trained machine learning models from libraries like scikit-learn or tensorflow, along with more standard data types like lists, dictionaries, and more. This flexibility is a key feature of HyllaDB, allowing users to store data in a manner that best suits their needs.

> NOTE: It's crucial to be cautious of the security risks involved in shelving objects from untrusted sources, as this could lead to the execution of malicious code.

## Security Concerns and Best Practices

While HyllaDB's use of the shelve and pickle modules in Python offers incredible flexibility in storing complex Python objects, it also brings forth security considerations. Users should exercise caution, especially when dealing with class instances from untrusted sources, as there is a risk of executing malicious code during deserialization.

> NOTE: We have plans to create safeguards to solve the security issues involved with shelving or pickling objects from unknown sources. One idea slated for development and testing involves the use of Docker containers. The concept is to utilize one or multiple dedicated containers whose sole purpose is to shelve and unshelve objects. This sandboxing approach allows users to safely test if an object runs malicious code. If any such code is detected and it compromises the container, the container can be safely destroyed and spun up again. This containment strategy minimizes the risk to the main system. Post-detection, the questionable object can either be flattened into a safer but slower format or rejected entirely, depending on the severity of the threat. This method not only enhances security but also maintains the integrity and performance of the main HyllaDB system.

To navigate these waters safely, consider the following best practices:

**Trusted Sources**: Prioritize storing objects from reliable and trusted sources.

**Safe Serialization**: For objects with uncertain origins, consider alternative serialization methods like JSON, which, while safer, might impact the performance benefits of using shelve.

**Balancing Performance and Safety**: Be aware that safer serialization methods may lead to a trade-off in the speed of object reconstruction, akin to rebuilding a complex LEGO structure piece by piece.

By adhering to these guidelines, users can harness the full potential of HyllaDB and HyQL, balancing the benefits of a highly customizable database with the imperative of data security.

# Core Concepts and Models of HyQL

In this section, we merge the core concepts with detailed model explanations, providing you with a clear picture of how HyQL functions and how its various components interact to facilitate querying in HyllaDB. Our journey into HyQL begins with understanding its key elements: path strings, filters, conditions, groups, and operators, and then delving into the specific models that make up the language.

## Key Terms and Concepts in HyQL

### Path Strings

**Definition:** A path string in HyQL is a dot-separated identifier that specifies the location of data within HyllaDB, much like a pathway through the database's structure.

**Function:** These strings navigate through the layers of the database, targeting data whether it's in a section, shelf, or nested dictionary.

**Example:** "section1.shelf2.data_field" represents a path leading to data_field in shelf2 of section1.

### Filters

**Role:** Filters in HyQL are used to narrow down the data retrieved from the database based on specified criteria.

**Structure:** They consist of conditions and groups that define the criteria for filtering the data.

### Conditions

**Description:** A condition in HyQL represents a single comparison statement, which is a fundamental part of creating filters.

**Components:** Each condition comprises a left operand, an operator from the Operators enum, and a right operand. The operands can be values, paths, or a combination of both.

### Groups

**Purpose:** Groups in HyQL are used to combine multiple conditions or other groups, forming complex logical expressions.

**Logical Connectors:** Groups utilize logical operators like AND and OR from the Operators enum to articulate the relationship between different conditions.

### Operators

**Significance:** Operators in HyQL, defined in the Operators enum, are crucial for constructing conditions. They include basic comparison, string manipulation, collection handling, and logical operators.

**Examples:** Operators.EQUAL, Operators.CONTAINS, Operators.IN, Operators.AND, etc.

## Scaffolding Models

Each model in HyQL serves a specific purpose, from defining conditions to shaping entire queries. Here, we'll explore each model, their attributes, and their role in crafting HyQL queries.

### Condition Model

**Purpose:** Defines a single comparison or logical statement.

**Attributes:**

-   `left`: The left operand (value or path)
-   `operator`: The comparison operator
-   `right`: The right operand (value or path)
-   `left_is_path`: Boolean indicating if the left operand is a path
-   `right_is_path`: Boolean indicating if the right operand is a path

**Example:**

```python
from hylladb.hyql import Condition, Operators

condition_example = Condition(
    left="section1.shelf2.data_field",
    operator=Operators.GREATER_THAN,
    right=100
)
```

### ConditionDict Model

**Purpose:** Wraps a single Condition object, used for easier integration with other models.

**Attributes:**

-   `condition`: A Condition object

**Example:**

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

### Group Model

**Role:** Groups multiple Condition instances or other Group instances, using logical connectors.

**Structure:** Consists of a list containing ConditionDict objects, Group objects, and logical operators (strings "AND" or "OR").

**Example:**

```python
from hylladb.hyql import Condition, ConditionDict, Group, Operators

group_example = Group(group=[
    ConditionDict(condition=Condition(left="field1", operator=Operators.EQUAL, right=10)),
    "AND",
    ConditionDict(condition=Condition(left="field2", operator=Operators.GREATER_THAN, right=20))
])
```

### CheckOutItem Model

**Function:** Specifies the data fields to retrieve from a particular path.

**Key Fields:** `path`, `checkout`.

**Example:**

```python
from hylladb.hyql import CheckOutItem

checkout_item = CheckOutItem(
    path="section1.shelf2",
    checkout=["data_field1", "data_field2"]
)
```

### SetSchema Model

**Purpose:** Sets or updates the schema for a section or the library.

**Attributes:**

-   `path`: The path to the section (or None for library)
-   `schema_model`: The Pydantic model defining the schema
-   `is_library`: Boolean indicating if the schema is for the library

**Example:**

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

### BuildShelf Model

**Purpose:** Used to create a new shelf in HyllaDB.

**Attributes:**

-   `path`: The path where the shelf will be created
-   `name`: The name of the new shelf
-   `data`: Optional initial data for the shelf
-   `metadata`: Optional metadata for the shelf

**Example:**

```python
from hylladb.hyql import BuildShelf

build_shelf = BuildShelf(
    path="section1",
    name="new_shelf",
    data={"field1": "value1", "field2": "value2"}
)
```

### BuildSection Model

**Purpose:** Used to create a new section in HyllaDB.

**Attributes:**

-   `path`: The path where the section will be created
-   `name`: The name of the new section
-   `schema_model`: Optional schema model for the section
-   `metadata`: Optional metadata for the section

**Example:**

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

### Write Model

**Purpose:** Used to write or upsert data to an existing shelf in the database.

**Attributes:**

-   `path`: The path to the shelf or nested dictionary
-   `data`: The data to be written

**Example:**

```python
from hylladb.hyql import Write

write = Write(
    path="section1.shelf1",
    data={"field1": "new_value", "field2": 42}
)
```

### CheckOut Model

**Purpose:** Used to retrieve data from the database.

**Attributes:**

-   `checkout`: List of CheckOutItem objects
-   `filters`: Optional list of conditions or groups
-   `sort`: Optional list of SortItem objects
-   `limit`: Optional maximum number of results
-   `offset`: Optional number of results to skip

**Example:**

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

### Revise Model

**Purpose:** Used to update existing data in the database.

**Attributes:**

-   `path`: The path to the data to be updated
-   `filters`: Optional list of conditions or groups
-   `data`: The new data to be written

**Example:**

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

### Remove Model

**Purpose:** Used to remove data from the database.

**Attributes:**

-   `path`: The path to the data to be removed
-   `filters`: Optional list of conditions or groups
-   `remove_shelf`: Boolean indicating if the entire shelf should be removed
-   `remove_section`: Boolean indicating if the entire section should be removed

**Example:**

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

### Reset Model

**Purpose:** Used to reset (clear) data in a shelf or section without removing the structure itself.

**Attributes:**

-   `path`: The path to the shelf or section to be reset
-   `filters`: Optional list of conditions or groups
-   `reset_shelf`: Boolean indicating if a shelf should be reset
-   `reset_section`: Boolean indicating if a section should be reset

**Example:**

```python
from hylladb.hyql import Reset

reset = Reset(
    path="section1.shelf1",
    reset_shelf=True
)
```

### Transaction Model

**Purpose:** Allows for executing multiple queries in a single transaction.

**Attributes:**

-   `queries`: List of query operations to be executed in the transaction

**Example:**

```python
from hylladb.hyql import Transaction, Write, Remove

transaction = Transaction(
    queries=[
        Write(path="section1.shelf1", data={"field1": "new_value"}),
        Remove(path="section1.shelf2", remove_shelf=True)
    ]
)
```

## Conclusion

HyQL provides a flexible and powerful way to interact with HyllaDB. By understanding these core concepts and models, you can construct complex queries to efficiently store, retrieve, update, and delete data in your HyllaDB database. Remember that the modular nature of HyllaDB allows you to structure your data in a way that best suits your needs, and HyQL provides the tools to interact with that structure effectively.
