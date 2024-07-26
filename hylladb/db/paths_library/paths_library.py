import shelve
import signal
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Literal

from hylladb.hyql.hyql_base.schema_model import SchemaModel


class PathsLibrary:
    """
    PathsLibrary is a class for managing paths in a shelve-based library with robustness and data safety.

    This class includes and allows:
    - Signal handling for graceful shutdown
    - Context manager support
    - A basic transaction system

    Attributes:
        - `storage_path` (Path): The path to the shelve file.
        - `_shelve` (shelve.DbfilenameShelf): The open shelve database.
        - `_is_closed` (bool): Flag indicating whether the shelve file is closed.

    Examples:
        ```Python
        from pathlib import Path
        from pydantic import BaseModel

        class MyDataModel(BaseModel):
            name: str
            value: int

        # Use as a context manager
        with PathsLibrary(Path("path_to_shelve_file")) as library:
            # Perform operations within a transaction
            with library.transaction():
                library.create("path1", MyDataModel(name="test", value=123))
                library.update("path2", MyDataModel(name="updated", value=456))

        # The library is automatically closed when exiting the with block
        ```
    """

    def __init__(self, storage_path: Path) -> None:
        """
        Initializes the PathsLibrary with the specified path to the shelve file.

        Args:
            - `storage_path` (Path): The path to the shelve file.

        Raises:
            - `OSError`: If the parent directory cannot be created.
        """
        self.storage_path: Path = storage_path
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._shelve: shelve.Shelf = shelve.open(str(self.storage_path), writeback=True)
        self._is_closed = False

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _check_closed(self) -> None:
        """Checks if the shelve file is closed and raises an error if it is."""
        if self._is_closed:
            raise RuntimeError("Cannot operate on a closed PathsLibrary instance")

    def _signal_handler(self, signum, frame) -> None:
        """Handles termination signals by closing the library and exiting."""
        print("\nReceived termination signal. Closing PathsLibrary...")
        self.close()
        sys.exit(0)

    def create(self, path_key: str, value: SchemaModel) -> None:
        """
        Sets a new path key and its associated value.

        Args:
            - `path_key` (str): The key representing the path to set.
            - `value` (SchemaModel): The value to associate with the path key.

        Raises:
            - `ValueError`: If the path key already exists in the paths library.
        """
        self._check_closed()
        if path_key in self._shelve:
            raise ValueError(f"Path '{path_key}' already exists in paths library")
        self._shelve[path_key] = value

    def read(self, path_key: str) -> SchemaModel | None:
        """
        Retrieves the value associated with the given path key.

        Args:
            - `path_key` (str): The key representing the path to retrieve.

        Returns:
            - `Optional[SchemaModel]`: The value associated with the path key, or `None` if the key does not exist.
        """
        self._check_closed()
        return self._shelve.get(path_key, None)

    def update(self, path_key: str, value: SchemaModel) -> None:
        """
        Updates the value associated with an existing path key.

        Args:
            - `path_key` (str): The key representing the path to update.
            - `value` (SchemaModel): The new value to associate with the path key.

        Raises:
            - `ValueError`: If the path key does not exist in the paths library.
        """
        self._check_closed()
        if path_key not in self._shelve:
            raise ValueError(f"Path '{path_key}' does not exist in paths library")
        self._shelve[path_key] = value

    def delete(self, path_key: str) -> None:
        """
        Deletes the value associated with the given path key.

        Args:
            - `path_key` (str): The key representing the path to delete.

        Raises:
            - `ValueError`: If the path key does not exist in the paths library.
        """
        self._check_closed()
        if path_key not in self._shelve:
            raise ValueError(f"Path '{path_key}' does not exist in paths library")
        del self._shelve[path_key]

    def close(self) -> None:
        """Closes the shelve file."""
        if not self._is_closed:
            self._shelve.close()
            self._is_closed = True

    def __del__(self):
        """Ensures the shelve file is closed when the PathsLibrary object is deleted."""
        self.close()

    def __enter__(self):
        """Allows the class to be used as a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> Literal[False]:
        """Closes the library when exiting the context manager."""
        self.close()
        if exc_type is not None:
            print(f"An exception occurred: {exc_type.__name__}: {exc_value}")
        return False  # Propagate exceptions

    @contextmanager
    def transaction(self) -> Generator[None, Any, None]:
        """
        A context manager that provides basic transaction-like functionality.

        If an exception occurs within the transaction, all changes are rolled back.

        Usage:
            with library.transaction():
                library.create("path1", data1)
                library.update("path2", data2)
        """
        snapshot = dict(self._shelve)  # Create a shallow copy
        try:
            yield
        except Exception as e:
            print(f"Transaction failed: {e}")
            self._shelve.clear()
            self._shelve.update(snapshot)  # Rollback to snapshot
            raise
