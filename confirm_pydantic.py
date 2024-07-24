from typing import Annotated, Any, Type, get_type_hints

from pydantic import Field, ValidationInfo, create_model, field_validator
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from rich import print

from hylladb.hyql.hyql_base.schema_model import SchemaModel


# Define the base class
class Animal(SchemaModel):
    name: str = Field(default_factory=lambda: "Roger")


# Define classes inheriting from the base class
class Dog(Animal):
    breed: str
    is_dog: bool


class Husky(Dog):
    # model_config = ConfigDict(extra="allow")

    is_husky: bool | None | str = True


class Cat(Animal):
    favorite_toy: str


class Zoo(SchemaModel):
    animals: Any

    @field_validator("animals")
    def validate_animals(cls, v) -> Animal:
        if not issubclass(v.__class__, Animal):
            raise ValueError("The animals field must be an instance of Animal.")

        return v


class NestedModel(SchemaModel):
    nested_field: int


class MainModel(SchemaModel):
    main_field: str
    nested_model: NestedModel


# def extract_model_schema(model_class: type[SchemaModel]) -> dict[str, Any]:
#     """
#     Extracts the schema of a given SchemaModel class recursively.

#     Args:
#         - `model_class` (type[SchemaModel]): The SchemaModel class whose schema is to be extracted.

#     Returns:
#         - `dict[str, Any]`: A dictionary representation of the schema, mapping field names to their types or nested schemas.

#     Raises:
#         - `None`: This function does not raise any exceptions.
#     """

#     schema: dict[str, Any] = {}
#     for field_name, field_type in get_type_hints(model_class).items():
#         if issubclass(field_type, SchemaModel):
#             schema[field_name] = extract_model_schema(field_type)
#         else:
#             schema[field_name] = field_type  # Store the actual type object
#     return schema


# def validate_value_with_schema(
#     model_class: type[SchemaModel], path: str, value: Any
# ) -> bool:
#     """
#     Validates if a given value matches the expected type in the schema at a specified path.

#     Args:
#         - `model_class` (type[SchemaModel]): The SchemaModel class whose schema is used for validation.
#         - `path` (str): The dot-separated path to the field in the schema.
#         - `value` (Any): The value to be checked against the schema.

#     Returns:
#         - `bool`: `True` if the value matches the expected type in the schema, otherwise `False`.

#     Raises:
#         - `PathAccessError`: If the specified path is not found in the schema.
#         - `KeyError`: If there is an error accessing the schema dictionary.
#     """

#     schema = extract_model_schema(model_class)
#     try:
#         expected_type = glom(schema, Path(*path.split(".")))
#         return isinstance(value, expected_type)
#     except (PathAccessError, KeyError):
#         return False


def generate_submodels(model: type[SchemaModel]) -> dict[str, type[SchemaModel]]:
    submodels: dict[str, type[SchemaModel]] = {}
    for field_name, field_info in model.model_fields.items():
        submodel_name: str = f"{model.__name__}__{field_name.title()}"

        # Extract the annotation and default value
        annotation: Any = field_info.annotation

        # Create the submodel
        submodels[field_name] = create_model(
            __model_name=submodel_name,
            __base__=(SchemaModel,),
            **{field_name: (annotation, field_info)},
        )  # type: ignore
    return submodels


def generate_submodel_code_string(model: type[SchemaModel], submodel_name: str) -> str:
    field_info: FieldInfo = model.model_fields[submodel_name]
    raw_annotation: type[Any] | None = field_info.annotation
    if hasattr(raw_annotation, "__name__"):
        annotation: str = raw_annotation.__name__  # type: ignore
    else:
        annotation = str(raw_annotation)

    default: Any = field_info.get_default(call_default_factory=True)

    model_code: str = ""
    if default is not PydanticUndefined:
        model_code = (
            f"class {submodel_name}:\n    {submodel_name}: {annotation} = {default}"
        )
    else:
        model_code = f"class {submodel_name}:\n    {submodel_name}: {annotation}"

    return model_code


# fields = extract_fields(Husky)
submodels: dict[str, type[SchemaModel]] = generate_submodels(Husky)

# Display the generated submodels
# for name, submodel in submodels.items():
#     print(name, submodel.model_json_schema())

# You can now use the generated submodels
# print(submodels["name"](name="Rex"))
# print(submodels["breed"](breed="German Shepherd"))
# print(submodels["is_dog"](is_dog=True))
# print(submodels["is_husky"].model_fields)
print(generate_submodel_code_string(submodels["name"], submodel_name="name"))
print(generate_submodel_code_string(submodels["is_husky"], "is_husky"))
print(generate_submodel_code_string(submodels["breed"], "breed"))

submodel: type[SchemaModel] | None = submodels.get("name")
if submodel:
    print(submodel.model_config)

print(Husky(name="Rex", breed="German Shepherd", is_dog=True, is_husky=True))

husky = Husky(name="Rex", breed="German Shepherd", is_dog=True, is_husky=True)
print(husky)


# schema test
class MySchema(SchemaModel):
    name: str
    age: int
    is_active: bool
    nested: NestedModel


class MyInheritedSchema(MySchema):
    is_inherited: bool


from hylladb.hyql import SetSchema

SetSchema(path="path1.sub_path1", schema_model=MySchema)
SetSchema(path="path1.sub_path2", schema_model=MyInheritedSchema)

zoo = Zoo(
    animals=Husky(name="Rex", breed="German Shepherd", is_dog=True, is_husky=True)
)
