from pydantic import BaseModel, ConfigDict


class SchemaModel(BaseModel):
    """
    A model for defining the schema allowed in a shelf.

    This model is used to create a schema for all the shelves that are direct children a given library or section.

    Example:
    ```python
    from hylladb.hyql import SchemaModel, SetSchema

    # Define the schema for the Animal inheriting from SchemaModel and defining the attributes and their types.
    class AnimalSchema(SchemaModel):
        name: str

    # Set the schema for the path1.sub_path1 section to the AnimalSchema.
    set_schema_dict: dict = {
        "path": "path1.sub_path1",
        "schema_model": AnimalSchema,
    }
    SetSchema(**set_schema_dict)
    ```
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
        revalidate_instances="always",
        strict=True,
    )
