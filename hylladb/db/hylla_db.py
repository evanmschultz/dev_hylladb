import shelve
from enum import StrEnum
from pathlib import Path

from hylladb.hyql.hyql import BuildSection, BuildShelf


class PathType(StrEnum):
    SECTION = "section"
    SHELF = "shelf"


class HyllaDB:
    def __init__(self, library_path: Path) -> None:
        self._library_path: Path = library_path
        self._ensure_library_directory()
        self._paths: dict[str, PathType] = self._load_paths()

    def build_section(self, hyql: BuildSection) -> None:
        """
        Adds a new section to the library.
        """

        if not isinstance(hyql, BuildSection):
            if not isinstance(hyql, dict):
                raise ValueError(
                    "The 'build_section' method requires a 'BuildSection' instance or a dictionary."
                )
            hyql = BuildSection(**hyql)

        section_path_str: str = hyql.path + "." + hyql.name
        if section_path_str in self._paths:
            raise ValueError(
                f"Section '{hyql.name}' already exists in the path {hyql.path}."
            )

        self._add_path({section_path_str: PathType.SECTION})

        if hyql.schema_model:
            # Add shelf for the section schema
            # Add path for the schema
            pass

        if hyql.metadata:
            # Add shelf for the section metadata
            # Add path for the metadata
            pass

    def build_shelf(self, hyql: BuildShelf) -> None:
        """
        Adds a new shelf to the library.
        """
        if hyql.path in self._paths:
            raise ValueError(
                f"Shelf '{hyql.name}' already exists in the path '{hyql.path}'."
            )

        self._add_path({hyql.path: PathType.SHELF})

        # Make shelve file for the shelf
        if hyql.data:
            # Unpack data into shelf
            pass

        if hyql.metadata:
            # Add path for the metadata
            # Add metadata to a key named 'metadata' in the shelf
            pass

    def _add_path(self, path_dict: dict[str, PathType]) -> None:
        """
        Adds the given path to the paths shelf.
        """
        self._paths.update(**path_dict)
        paths_file = str(self._library_path / "paths")

        with shelve.open(paths_file, flag="w") as paths_shelf:
            paths_shelf.update(path_dict)

            if len(self._paths) != len(paths_shelf):
                # Raise an error indicating the database has somehow been corrupted
                raise ValueError("Failed to add path to the paths shelf.")

    def _remove_path(self, path: str) -> None:
        """
        Removes the given path from the paths shelf.
        """
        paths_file = str(self._library_path / "paths")

        with shelve.open(paths_file, flag="w") as paths_shelf:
            del paths_shelf[path]

    def _ensure_library_directory(self) -> None:
        """
        Ensures the library directory exists, creating it if necessary.
        """
        self._library_path.mkdir(parents=True, exist_ok=True)

    def _load_paths(self) -> dict[str, PathType]:
        """
        Loads the `paths` shelve file into memory from the library_path if it exists, otherwise creates a new one.
        """
        paths_file = str(self._library_path / "paths")

        with shelve.open(paths_file, flag="c") as paths_shelf:
            if len(paths_shelf) == 0:
                paths_shelve_dict: dict = {}
            else:
                paths_shelve_dict = dict(paths_shelf)

        return paths_shelve_dict
