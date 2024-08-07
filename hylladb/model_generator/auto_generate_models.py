"""
Script is for an experimental idea to automatically generate models for all possible combinations of fields in a
Pydantic model. This would allow for easy retrieval of data from HyllaDB along with IDE support.

Example:
    ```Python
    from hylladb.model_generator.auto_generate_models import (
        generate_models,
        User,
    )

    generate_models(User)
    # Go to hylladb/model_generator/generated_models.py to see the generated models
"""

from collections import defaultdict
import inspect
from pathlib import Path
from types import ModuleType
from uuid import UUID, uuid4
from typing import Any
from itertools import combinations

from pydantic import BaseModel, create_model, Field
from rich import print


class HyllaBaseModel(BaseModel):
    """
    The base model for all Hylla models. Inherit from this class to create a your own models to use with HyllaDB.

    The `id` field is the only required field when and defaults to a UUID4, but can be overwritten with your own types
    to best suit your database needs.
    """

    id: UUID = Field(default_factory=lambda: str(uuid4()))


class User(BaseModel):
    id: UUID = Field(default_factory=lambda: uuid4(), description="Unique identifier")
    name: str
    email: str = "123"
    age: HyllaBaseModel


# Function to create subset models for each combination of fields
def _create_subset_models(model: type[BaseModel]) -> list[type[BaseModel]]:
    # if "id" not in model.__annotations__:
    #     raise ValueError(f"The model {model.__name__} is missing an 'id' field.")

    field_names = list(model.__annotations__.keys())
    subset_models: list[type[BaseModel]] = []

    print(f"Generating subset models for {model.__name__}...")

    # Create 'r-length' combinations of fields starting with the non-empty subsets (r=1) to the subsets with len(fields) - 1
    for r in range(1, len(field_names)):
        for field_combo in combinations(field_names, r):
            if "id" not in field_combo:
                continue  # Ensure 'id' is always part of the combination

            field_info: dict[str, Any] = _gather_field_info(
                field_combo, model.__annotations__
            )
            capitalized_fields: list[str] = field_info["capitalized_fields"]
            field_descriptions: list[str] = field_info["field_descriptions"]
            field_definitions: dict[str, Any] = field_info["field_definitions"]

            subset_model_name: str = _generate_model_name(
                model.__name__, capitalized_fields
            )
            subset_model_docstring: str = _generate_docstring(
                model.__name__, field_descriptions
            )
            subset_model: type[BaseModel] = create_model(
                subset_model_name,
                __base__=BaseModel,
                __doc__=subset_model_docstring,
                __module__=model.__module__,
                **field_definitions,
            )
            subset_models.append(subset_model)

    print(f"Generated {len(subset_models)} subset models for {model.__name__}.")
    return subset_models


def _gather_field_info(
    field_combo: tuple[str, ...], model_annotations: dict[str, Any]
) -> dict[str, Any]:
    field_definitions: dict[str, Any] = {}
    field_descriptions: list[str] = []
    capitalized_fields: list[str] = []
    for field in field_combo:
        field_type: Any | None = model_annotations.get(field)
        if field_type:
            field_definitions[field] = (field_type, Field(...))

        field_description: str = (
            f"{field}: `{field_type.__name__}`" if field_type else field
        )
        field_descriptions.append(field_description)

        # Capitalize field name for the model name
        capitalized_field = (
            field.capitalize() if field.lower() != "id" else field.upper()
        )
        capitalized_fields.append(capitalized_field)

    return {
        "field_definitions": field_definitions,
        "field_descriptions": field_descriptions,
        "capitalized_fields": capitalized_fields,
    }


def _generate_model_name(model_name: str, capitalized_fields: list[str]) -> str:
    return f"{model_name}Return_{'_'.join(capitalized_fields)}"


def _generate_docstring(model_name: str, field_descriptions: list[str]) -> str:
    return (
        f"An autogenerated class representing a subset of the {model_name} model.\n\n"
        f"Used as a return type from HyllaDB. Allows for easy retrieval of data along with IDE support.\n\n"
        f"Attributes:\n- " + "\n- ".join(field_descriptions)
    )


def _get_imports(model: type[BaseModel]) -> str:
    imports = defaultdict(set)
    for field_type in model.__annotations__.values():
        module: ModuleType | None = inspect.getmodule(field_type)
        if module and module.__name__ != "builtins":
            imports[module.__name__].add(field_type.__name__)

    import_statements: list[str] = []
    for module, types in imports.items():
        import_statements.append(f"from {module} import {', '.join(sorted(types))}")

    return "\n".join(import_statements)


def _format_docstring(docstring: str | None) -> str:
    if docstring:
        docstring_lines: list[str] = docstring.strip().split("\n")
        formatted_docstring: str = "\n".join(
            ['    """'] + ["    " + line for line in docstring_lines] + ['    """']
        )
    else:
        formatted_docstring = ""

    return formatted_docstring


def _model_to_code(model: type[BaseModel]) -> str:
    # Retrieve the model's docstring, if available
    docstring: str = _format_docstring(model.__doc__)

    # Format field definitions
    fields_str = "\n    ".join(
        f"{name}: {field_type.__name__}"
        for name, field_type in model.__annotations__.items()
    )

    # Combine into full class definition
    return f"class {model.__name__}(BaseModel):\n{docstring}\n\n    {fields_str}\n"


def _get_dir_path() -> Path:
    # Identify the directory of the current script (__file__) and navigate to the desired folder
    base_path: Path = Path(__file__).parent.parent
    dir_path: Path = base_path / "generated_models"
    dir_path.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    return dir_path


def _write_init_file(models: list[type[BaseModel]]) -> None:
    # Define the output path
    dir_path: Path = _get_dir_path()
    init_file_path = dir_path / "__init__.py"

    # Write to the file
    with open(init_file_path, "w") as init_file:
        init_file.write(f"from hylladb.generated_models.generated_models import (\n")
        for model in models:
            init_file.write(f"    {model.__name__},\n")
        init_file.write(")\n")

    print(f"__init__.py created at {init_file_path}")


def _write_code_to_file(subset_models: list[type[BaseModel]]) -> None:
    # Define the output path
    dir_path: Path = _get_dir_path()
    file_path: Path = dir_path / "generated_models.py"

    # Track model names for __init__.py
    model_names: list[str] = []
    # Write to the file
    with open(file_path, "w") as file:
        print(f"Writing to {file_path}...")
        file.write("from pydantic import BaseModel\n\n")
        all_imports: set[str] = set()
        code_str: str = ""
        for model in subset_models:
            model_imports = _get_imports(model).split("\n")
            all_imports.update(model_imports)
            model_code = _model_to_code(model)
            code_str += model_code + "\n\n"
            model_names.append(model.__name__)  # Add model name to the list

        file.write("\n".join(sorted(all_imports)) + "\n\n" + code_str)
    print(f"Models written to {file_path}")


def generate_models(model: type[BaseModel]) -> None:
    subset_models: list[type[BaseModel]] = _create_subset_models(model)
    _write_code_to_file(subset_models)
    _write_init_file(subset_models)
