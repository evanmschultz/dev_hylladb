import pytest

from hylladb.utilities.hylla_utilities import (
    get_shelf_path,
    get_validated_path_str,
    resolved_section_path,
)


# Utility Function Tests
def test_get_validated_path_str():
    assert get_validated_path_str("section.shelf") == "section/shelf"
    with pytest.raises(ValueError):
        get_validated_path_str("invalid|path|with|special|chars")


def test_resolved_section_path(tmp_path):
    library_path = tmp_path
    (library_path / "section" / "shelf").mkdir(parents=True)
    assert (
        resolved_section_path("section.shelf", library_path)
        == library_path / "section/shelf"
    )
    with pytest.raises(ValueError):
        resolved_section_path("invalid.path", library_path)


def test_get_shelf_path(tmp_path):
    library_path = tmp_path
    (library_path / "section" / "shelf").mkdir(parents=True)
    assert (
        get_shelf_path("section.shelf", library_path) == library_path / "section/shelf"
    )
    with pytest.raises(ValueError):
        get_shelf_path("invalid.path", library_path)
