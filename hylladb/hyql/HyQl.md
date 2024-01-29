# HyQL (Hylla Query Language) - 'Hi-Quill'

Welcome to HyQL, the custom query language for HyllaDB, a database system that built with speed, flexibility, and customizability of data storage in mind. HyllaDB is engineered and inspired the ideology of an IKEA flat-pack, or rather lego or erector sets modularity, offering the necessary building blocks to construct a database tailored precisely to your needs.

At its core, it operates like a dictionary of dictionaries, with the added benefit of being able to store complex Python objects, including class instances, e.g., trained machine learning models from libraries like scikit-learn or tensorflow, along with more standard data types like lists, dictionaries, and more. This flexibility is a key feature of HyllaDB, allowing users to store data in a manner that best suits their needs. Similar in effect to NetworkX's documentation statement, “[It’s dictionaries all the way down.](https://networkx.org/documentation/stable/reference/introduction.html#id2)”

Just as LEGO bricks enable endless possibilities, HyllaDB provides the tools for users to build a database system that is as unique and adaptable as their data requires. This documentation introduces HyQL, emphasizing its key role in interacting with the dynamic architecture of HyllaDB and highlighting the system's speed and efficiency in data retrieval.

## Purpose and Inspiration

HyQL is a paradigm shift from traditional query languages, employing Pydantic models to articulate queries. This innovative approach, inspired by the Python [`glom` library's](https://glom.readthedocs.io/) handling of nested dictionaries and the versatility of [GraphQL](https://graphql.org/) queries, presents a method that is both flexible and user-friendly. HyQL's primary aim is to provide clarity in query construction, ensuring type safety, and maintaining integrity in data interaction, making HyllaDB an optimal choice for a wide range of applications.

## HyllaDB: A Modular Database System

HyllaDB is designed with a modular, layered structure, while taking inspiration from the organization of a library. Although, forgoing the Dewey Decimal System, HyllaDB's architecture is much more flexible and adaptable. The database is organized into three layers:

**Library**: The foundational layer, serving as the primary directory of the database.

**Sections**: These are akin to sections in a library, eg. Sciences, and then Physics. Yet, can also represent a specific 'bookcase' within a 'section' of a library. This allows for the organization of data in a structured yet flexible manner while allowing for fast read/write speeds, only dependent upon your system's I/O constraints.

**Shelves**: Resembling individual shelves, drawers, containers, or even books themselves, these shelve files hold data, be it flat or nested dictionaries. If your needs best fit it, you can forgo any use of 'sections' and simply store all your data in 'shelves' the 'library' directory, while still keeping a nested structure. Keep in mind this would be even more constrained by your system's I/O capabilities as more data would need to be serialized/deserialized upon each read/write.

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

---

As we delve deeper into the subsequent sections, we will explore the intricacies of constructing and executing queries with HyQL, maximizing the benefits of HyllaDB's modular design in your data storage and retrieval strategies.

## Overview of HyllaDB Structure

HyllaDB's architecture is meticulously designed to mirror the organization and efficiency of a well-structured library, providing a familiar yet innovative approach to data storage. This section will guide you through the fundamental layers of HyllaDB, illustrating how its unique structure enhances both flexibility and performance.

### **The Library:** Foundation of HyllaDB

At the base of HyllaDB's architecture lies the Library. This foundational layer serves as the primary directory of the database and acts as the entry point for all data interactions. Think of it as the main hall of a library, where every book, shelf, and section is catalogued and accessible.

**Centralized Hub:** The Library directory is the centralized hub for all data stored in HyllaDB, offering a unified view of your database's structure.

**Root Directory:** All sections and shelves are nested within this root directory, making it the starting point for any data retrieval or manipulation.

### **Sections:** Organizational Units within the Library

**Sections** in HyllaDB are akin to specific areas or bookcases in a traditional library. They offer a way to categorize and compartmentalize data, facilitating efficient organization and retrieval.

**Flexible Categorization:** Just as a library has sections for different genres or subjects, HyllaDB's sections allow for a logical grouping of related data.

**Nested Structure:** Sections can contain shelves, enabling a nested and hierarchical data structure that mirrors real-world data relationships.

### Shelves: The Core Data Containers

The heart of data storage in HyllaDB lies in the Shelves. These are the actual shelve files where your data resides, be it in flat or nested dictionaries.

**Versatile Storage:** Shelves can hold a wide range of data types, from simple key-value pairs to complex, nested structures.

**Direct Access:** Each shelf is directly accessible within its section, providing a streamlined approach to data retrieval and updates.

### Path Strings: Navigating the HyllaDB Architecture

A crucial component of interacting with HyllaDB is the use of path strings in HyQL. These strings are deliberately designed to represent the path to the desired data, whether it resides in a section, shelf, or a nested dictionary within a shelf.

**Intuitive Navigation:** Path strings allow for easy and precise navigation through the layers of the database, making data access straightforward.

**Unified Access Pattern:** Regardless of the data's location (section, shelf, or nested dictionary), the path string format remains consistent, ensuring a uniform access pattern.

### Harnessing the Power of HyllaDB's Structure

By understanding and utilizing the distinct layers of HyllaDB, users can create a database that not only reflects the complexity of their data but also enhances the efficiency of data access and manipulation. The modular nature of HyllaDB, combined with the intuitive and flexible nature of HyQL, could make it a useful software engineers or data professionals seeking to fast prototype, especially when persistence of complex `Python` objects are needed. Who knows, if enough interest is shown, HyllaDB, and by extension, HyQL, could become a viable alternative to the more traditional database systems for production use cases.

**Tailored Data Organization:** Users have the freedom to structure their database in a way that aligns with their specific data requirements and usage patterns.

**Optimized Data Retrieval:** The clear and logical structure of HyllaDB, coupled with the HyQLs flexibility in conjunction with its type safety and clear error messaging, ensures fast and accurate data retrieval, essential for applications that need performance and/or non-traditional data structures.

---

In the following sections, we will dive into the core concepts of HyQL, exploring how this unique query language leverages the robust structure of HyllaDB to offer unparalleled flexibility and efficiency in data querying.

# Core Concepts and Models of HyQL

Welcome to the heart of HyQL - the place where the 'how' of this language comes alive. In this section, we merge the core concepts with detailed model explanations, providing you with a clear picture of how HyQL functions and how its various components interact to facilitate querying in HyllaDB. Our journey into HyQL begins with understanding its key elements: path strings, filters, conditions, groups, and operators, and then delving into the specific models that make up the language.

## Key Terms and Concepts in HyQL

### Path Strings

**Definition:** A path string in HyQL is a dot-separated identifier that specifies the location of data within HyllaDB, much like a pathway through the database's structure.

**Function:** These strings navigate through the layers of the database, targeting data whether it’s in a section, shelf, or nested dictionary.

**Example:** "section1.shelf2.data_field" represents a path leading to data_field in shelf2 of section1.

### Filters

**Role:** Filters in HyQL are used to narrow down the data retrieved from the database based on specified criteria. > NOTE: Dependent upon how you structure your database in HyllaDB, you can do complex joins and filtering of data, similar to how you would in a relational database.

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

Each model in HyQL serves a specific purpose, from defining conditions to shaping entire queries. Here, we’ll explore each model, their attributes, and their role in crafting HyQL queries.

### <u>Condition Model</u>

**Purpose:** Defines a single comparison or logical statement.

**Attributes:** left, operator, right, left_is_path, right_is_path.

**Example:**

```python
from hylladb.hyql import Condition, Operators

# Define a condition using the `Pydantic` model
condition_example = Condition(left="section1.shelf2.data_field", operator=Operators.GREATER_THAN, right=100)
```

The left and right attributes can be either a value or a path string, depending on the `left_is_path` and `right_is_path` attributes. If `left_is_path` is True, the left attribute is a path string, and if `right_is_path` is True, the right attribute is a path string. If both are True, the condition is a path comparison, and if both are False, the condition is a value comparison. If only one is True, the condition is a mixed comparison.

Here is an example of a dictionary representation of a condition:

```python
from hylladb.hyql import Condition, Operators

# Define a condition as a dictionary
"condition": {
    "left": "name",
    # Note: the use of the Operators enum. The enum is just to make it easier to use the operators if you
    # don't remember the allowed string values off hand. This will be explained in more detail later.
    "operator": Operators.IN,
    "right": "path1.field2",
    "left_is_path": False,
    "right_is_path": True,
}

# Convert the dictionary to a Condition object by unpacking it as kwargs using the `**` operator
condition = Condition(**condition)
```

> NOTE: The structure of the condition object is meant to mirror the way you would write a condition in Python, e.g., `if name in path1.field2:`. It is meant to be flexible and intuitive, and allow you to construct complex conditions as you would if you were writing a Python script.

### <u>Group Model</u>

**Role:** Groups multiple Condition instances or other Group instances, using logical connectors.

**Structure:** Consists of a list containing Condition objects and logical operators, specifically the strings `AND` or `OR`. The structure of the list is as follows: `[Condition, "AND", Condition, "OR", Group]`. Conditions or Groups must always be separated by a logical operator.

**Example:**

```python
from hylladb.hyql import Condition, Group, Operators

# Define a group using the `Pydantic` model
group_example = Group(group=[condition_example, Operators.AND, another_condition])
```

Here is an example of a dictionary representation of a more complex 'nested' group:

```python
from hylladb.hyql import Group, Operators

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

# Convert the dictionary to a Group object by unpacking it as kwargs using the `**` operator
group = Group(**group)
```

> NOTE: The condition was not explicitly imported or defined as the model made the condition automatically while unpacking the dictionary. This is a feature of `Pydantic` that allows for the creation of nested models.

### <u>Filters</u>

As of now there is no explicit Filter model, as it is simply a list of Condition and Group objects. This may change in the future, but for now, it is just a list of Condition and Group objects. The structure of the list is as follows: `[Condition, "AND", Condition, "OR", Group]`. Conditions or Groups must always be separated by a logical operator. It still mirrors the logic of a Python script, e.g.,

```python
if (
    name in path1.field2
    and path2.field3 < path1.field2
    or path3.field4 == 100
):
    # do something
```

**Example of complex filters with a dictionary:**

```python
from hylladb.hyql import Operators, CheckOut
filters = [
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

# Add to CheckOut model. NOTE: This is not a working example as the ellipses are meant to only represent
# the rest of the model's attributes.
checkout = CheckOut(..., filters=filters)
```

> NOTE: As HyllaDB, and by extension HyQL is built on the idea of flexibility and modularity, the filters, groups, conditions, etc. you could construct is dependent upon how you structure your database.

### <u>CheckOutItem Model</u>

**Function:** Specifies the data fields to retrieve from a particular path.

**Key Fields:** `path`, `checkout`.

**Example:**

```python
checkout_item = CheckOutItem(path="section1.shelf2", checkout=["data_field1", "data_field2"])
```

**Example using a dictionary:**

```python
from hylladb.hyql import CheckOutItem

checkout_item = {
    "path": "section1.shelf2",
    "checkout": ["data_field1", "data_field2"],
}

# Convert the dictionary to a CheckOutItem object by unpacking it as kwargs using the `**` operator
checkout_item = CheckOutItem(**checkout_item)
```

## Operators

Before we continue and explain the models that actually make up HyQL, let's talk about the Operators.

First, practically all logical operators in Python are meant to work inside of a `Condition`, which by extension they fit into a `Group`, and by extension a `Filter`. HyQL is built with an Operators enum to help see all of the possible operators you can use in HyQL. The Operators enum is meant to be a convenience, as it is not required to use it. You can simply use the string representation of the operator, e.g., `">="` instead of `Operators.GREATER_THAN_OR_EQUAL`. So, don't worry about feeling like you need to use the enum, or, in cases where you are concerned about exact syntactical correctness, you can use the enum.

> NOTE: The Operators enum inherits from the `str` class, so you can use it as a string, e.g., `Operators.GREATER_THAN_OR_EQUAL == ">="` is `True`. Ensuring that you can exactly, and easily interchange the two based on your needs. Below is a simple example of how you can use the Operators enum.

```python
from hylladb.hyql import Operators

# This is the `Literal` string "not in" and will work exactly as the Python `not in` operator
operator = Operators.NOT_IN
```

More information on the allowed operations will be detailed in the documentation later. As for now, just use the Operators enum as a reference for the allowed operators and expect that they will work as they do in any Python script.

# HyQL Query Models: Crafting Queries in HyllaDB

In the previous sections, we introduced the foundational elements of HyQL. Now, let's explore the models that form the core of query operations in HyllaDB. These models - `Build`, `CheckOut`, `Write`, `Revise`, and `Remove` - are designed to handle the complete range of CRUD (Create, Read, Update, Delete) operations, allowing users to interact with their data in HyllaDB effectively.

## Build Query Model

The `Build` model in HyQL is used for creating new structures within HyllaDB. It is used to create new sections or shelves. In actuality, it creates a new directory (section), or a new database file (shelf) that you can in turn use to store data.

### Key Fields:

**path:** Specifies the location in the database where the data will be created.

**data:** The actual data to be stored. It can be a dictionary mapping keys to values.

**metadata:** Optional metadata associated with the data.

**is_section:** A boolean indicating if the path represents a section. If True, data must be None.

**Example:**

```python
from hylladb.hyql import Build

# Create a new section
build = Build(path="section1", is_section=True)
```

As a dictionary:

```python
from hylladb.hyql import Build

# Create a shelf, not a section
build_query: dict = {
    "path": "path1.sub_path1",
}

# Convert the dictionary to a Build object by unpacking it as kwargs using the `**` operator
built_model = Build(**build_query)
```

Use the Build model to initialize new sections or shelves in your database as a straightforward way to expand your data structure to fit your needs.

## Checkout Query Model

Checkout is the HyQL model used for reading (`select`ing or `get`ing) data from HyllaDB. It allows you to specify exactly what data you want to retrieve, as much or as little, making data access both efficient and precise.

### Key Fields:

**checkout:** A list of CheckoutItem objects, each specifying a path and the fields to retrieve from that path.

**filters:** Optional list of Condition or Group objects to filter the data being retrieved.

**sort:** Optional list of SortItem objects to order the results.

**limit:** An optional integer to limit the number of results returned.

**offset:** An optional integer indicating the number of results to skip (useful for pagination).

**Example using a dictionary:**

```Python
from hylladb.hyql import CheckOut

checkout_dict: dict = {
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

# Convert the dictionary to a CheckOut object by unpacking it as kwargs using the `**` operator
checkout = CheckOut(**checkout_dict)
```

## Write Query Model

`Write` in HyQL is used for creating data in an existing `shelf` in HyllaDB. It’s like adding pages in a book on your shelf.

### Key Fields:

**path:** Specifies the location in the database where the data will be created. This can be an empty shelf or a nested dictionary within a shelf.

> NOTE: If the path is not to an existing shelf or a key in the nested dictionary within an existing shelf, an error will be raised.

**data:** The actual data to be stored. It must be a dictionary.

**Example with dictionary:**

```python
from hylladb.hyql import Write

write_idea: dict = {
    "path": "path1.sub_path1",
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}

# Convert the dictionary to a Write object by unpacking it as kwargs using the `**` operator
write = Write(**write_idea)
```

**Example instantiating tbe model directly:**

```python
from hylladb.hyql import Write

write = Write(path="path1.sub_path1", data={"sub_path1.field1": "value1", "sub_path1.field2": "value2"})
```

## Revise Query Model

> NOTE: TODO: Add logic for updating metadata, make sure to include schema validation.

`Revise` in HyQL is used for updating data in an existing `shelf` in HyllaDB. It’s like editing a page in a book on your shelf.

### Key Fields:

**path:** Specifies the location in the database where the data will be updated. This can be a shelf or a nested dictionary within a shelf.

**data:** The actual data to be stored. It must be a dictionary.

**Example with dictionary:**

```python
from hylladb.hyql import Revise

revise_idea: dict = {
    "path": "path1.sub_path1",
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}

# Convert the dictionary to a Revise object by unpacking it as kwargs using the `**` operator
revise = Revise(**revise_idea)
```

**Example instantiating tbe model directly:**

```python
from hylladb.hyql import Revise

revise = Revise(path="path1.sub_path1", data={"sub_path1.field1": "value1", "sub_path1.field2": "value2"})
```

## Remove Query Model

`Remove` in HyQL is used for deleting data in an existing `shelf`, or `section` in HyllaDB.

> **NOTE:** Be mindful when using the remove model in a query as it will delete any data that is a child of the path. **For example:** if you remove a section, it will delete all the shelves in that section.

### Key Fields:

**path:** Specifies the location in the database where the data will be deleted. This can be a shelf or a nested dictionary within a shelf.

**filters:** Optional list of Condition or Group objects to filter the data being deleted.

**remove_shelf:** A boolean indicating if the path represents a shelf. If True, all data in the shelf will be deleted. If False, all data in the nested dictionary will be deleted.

**remove_section:** A boolean indicating if the path represents a section. If True, all data in the section will be deleted, including all of the shelves. If False, all data in the nested dictionary will be deleted.

**Example with dictionary:**

```python
from hylladb.hyql import Remove

remove_idea: dict = {
    "path": "path1.sub_path1",
    "remove_shelf": True,
}

# Convert the dictionary to a Remove object by unpacking it as kwargs using the `**` operator
remove = Remove(**remove_idea)
```

**Example instantiating tbe model directly:**

```python
from hylladb.hyql import Remove

remove = Remove(path="path1.sub_path1", remove_shelf=True)
```

# HyQL Query Execution
