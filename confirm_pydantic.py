from pydantic import ConfigDict
from rich import print

from hylladb.db.models import SchemaModel


# Define the base class
class Animal(SchemaModel):
    name: str


# Define classes inheriting from the base class
class Dog(Animal):
    breed: str
    is_dog: bool


class Cat(Animal):
    favorite_toy: str


# Define a class with a field that accepts instances of Animal or its subclasses
class Zoo(SchemaModel):
    # model_config = ConfigDict(extra="allow")
    animal: Animal  # Accepts instances of Animal or any subclass of Animal


# Now you can create instances of Zoo with either Dog or Cat instances
zoo1 = Zoo(animal=Dog(name="Rex", breed="German Shepherd", is_dog=True))
zoo2 = Zoo(
    animal=Cat(name="Whiskers", favorite_toy="String"),
)

print(zoo1)
print(zoo2)

# # Throws an error because validate assignment is True in the Schema base class
# zoo1.animal.name = 123  # type: ignore
# print(zoo1)

# from typing import Any, get_type_hints, Type

# from hylladb.db.models import HyQLSchema


# class NestedModel(HyQLSchema):
#     nested_field: int


# class MainModel(HyQLSchema):
#     main_field: str
#     nested_model: NestedModel


# def extract_model_schema(model_class: Type[HyQLSchema]) -> dict[str, Any]:
#     schema: dict[str, Any] = {}
#     for field_name, field_type in get_type_hints(model_class).items():
#         # Check if the field is a Pydantic model
#         if issubclass(field_type, HyQLSchema):
#             schema[field_name] = extract_model_schema(field_type)
#         else:
#             schema[field_name] = str(field_type)
#     return schema


# schema: dict[str, Any] = extract_model_schema(MainModel)
# print(schema)

from typing import Any, Type, get_type_hints

from glom import Path, PathAccessError, glom

from hylladb.db.models import SchemaModel


class NestedModel(SchemaModel):
    nested_field: int


class MainModel(SchemaModel):
    main_field: str
    nested_model: NestedModel


def extract_model_schema(model_class: Type[SchemaModel]) -> dict[str, Any]:
    schema: dict[str, Any] = {}
    for field_name, field_type in get_type_hints(model_class).items():
        if issubclass(field_type, SchemaModel):
            schema[field_name] = extract_model_schema(field_type)
        else:
            schema[field_name] = field_type  # Store the actual type object
    return schema


def validate_value_with_schema(
    model_class: Type[SchemaModel], path: str, value: Any
) -> bool:
    schema = extract_model_schema(model_class)
    try:
        expected_type = glom(schema, Path(*path.split(".")))
        return isinstance(value, expected_type)
    except (PathAccessError, KeyError):
        return False


schema = extract_model_schema(MainModel)
print(schema)

# Example usage
path = "nested_model.nested_field"
value = "123"  # or any value you want to check
is_valid = validate_value_with_schema(MainModel, path, value)
print(f"Value is valid: {is_valid}")
