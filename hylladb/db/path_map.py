from pydantic import BaseModel, PrivateAttr


class PathMapConsistencyError(Exception):
    """Raised when the internal state of PathMap is inconsistent."""


class PathMap(BaseModel):
    _keys_set: set[str] = PrivateAttr(set())
    _path_maps: dict[str, dict[str, str]] = PrivateAttr(dict())

    def add(self, path_key: str, path_map: dict[str, str]) -> "PathMap":
        if path_key in self._keys_set:
            raise KeyError(f"Path '{path_key}' already exists in the path map.")

        if not path_map.get("path") or not path_map.get("key_path"):
            raise ValueError(
                f"\n[bold][blue]Hylla[/blue][yellow]DB[/yellow] [red]Error:[/red][/bold]\n"
                f"[red]----[/]"
                f"Path map for '{path_key}' must contain a 'path' and 'key_path' key."
            )
        if not isinstance(path_map.get("path"), str) or not isinstance(
            path_map.get("key_path"), str
        ):
            raise TypeError(
                f"\n[bold][blue]Hylla[/blue][yellow]DB[/yellow] [red]Error:[/red][/bold]\n"
                f"[red]----> [/]"
                f"Path map for '{path_key}' must contain a 'path' and 'key_path' key with string values."
            )

        self._keys_set.add(path_key)
        self._path_maps[path_key] = path_map
        if len(self._keys_set) != len(self._path_maps):
            raise PathMapConsistencyError(
                "\n[bold][blue]Hylla[/blue][yellow]DB[/yellow] [red]Error:[/red][/bold]\n"
                "[red]----> [/red]"
                "The number of keys in the path map does not match the number of path maps. An error must have occurred"
                " while adding the path map or before. The database may be in an inconsistent state and corrupted.\n"
            )
        return self

    def get(self, path_key: str) -> dict[str, str]:
        if path_key not in self._keys_set:
            raise KeyError(f"Path '{path_key}' not found in the path map.")

        return self._path_maps[path_key]

    def update(self, path_key: str, path_map: dict[str, str]) -> "PathMap":
        if path_key not in self._keys_set:
            raise KeyError(f"Path '{path_key}' not found in the path map.")

        self._path_maps[path_key] = path_map
        return self

    def remove(self, path_key: str) -> "PathMap":
        if path_key not in self._keys_set:
            raise KeyError(f"Path '{path_key}' not found in the path map.")

        self._keys_set.remove(path_key)
        self._path_maps.pop(path_key)
        if len(self._keys_set) != len(self._path_maps):
            raise PathMapConsistencyError(
                "\n[bold][blue]Hylla[/blue][yellow]DB[/yellow] [red]Error:[/red][/bold]\n"
                "[red]----> [/red]"
                "The number of keys in the path map does not match the number of path maps. An error must have occurred"
                " while removing the path map or before. The database may be in an inconsistent state and corrupted.\n"
            )
        return self
