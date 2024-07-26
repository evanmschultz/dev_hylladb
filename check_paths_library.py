from pathlib import Path
from hylladb.db.paths_library import PathsLibrary
from hylladb.hyql import SchemaModel


# Import PathsLibrary locally within the function or method to avoid circular import issues
class MyDataModel(SchemaModel):
    name: str
    value: int


def main():
    # Use as a context manager
    library = PathsLibrary(
        Path("example")
    )  # Ensure paths_library_path is a Path object
    # Perform operations within a transaction
    with library.transaction():
        # Check if path1 exists before creating it
        if not library.read("path1"):
            library.create("path1", MyDataModel(name="test", value=123))
        else:
            print("path1 already exists, updating instead")
            library.update("path1", MyDataModel(name="test", value=123))

        # Check if path2 exists before creating it
        if not library.read("path2"):
            library.create("path2", MyDataModel(name="initial", value=0))
        else:
            print("path2 already exists, updating instead")
            library.update("path2", MyDataModel(name="initial", value=0))

        library.update("path2", MyDataModel(name="updated", value=456))

    # The library is automatically closed when exiting the with block


if __name__ == "__main__":
    main()
