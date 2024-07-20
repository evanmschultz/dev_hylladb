from pathlib import Path

import pytest
from pydantic import ValidationError

from hylladb.db.models import ShelfModel
from hylladb.hyql import (
    BuildShelf,
    CheckOut,
    CheckOutItem,
    Condition,
    ConditionDict,
    Group,
    Remove,
    Reset,
    Revise,
    SetSchema,
    SortItem,
    Write,
)
from hylladb.hyql.enums import Operators
from hylladb.hyql.hyql import BuildSection
from hylladb.utilities.hylla_utilities import (
    get_shelf_path,
    get_validated_path_str,
    resolved_section_path,
)


# Mock utilities if necessary
def operator_validator(value):
    return value in [op.value for op in Operators]


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


# Condition Model Tests
def test_condition_valid():
    condition = Condition(left="path1.field1", operator=">", right=100)
    assert condition.left == "path1.field1"
    assert condition.operator == ">"
    assert condition.right == 100


def test_condition_invalid_operator():
    with pytest.raises(ValidationError):
        Condition(left="path1.field1", operator="invalid", right=100)


def test_condition_invalid_path():
    with pytest.raises(ValidationError):
        Condition(left="invalid path", operator=">", right=100)


def test_condition_both_paths_false():
    with pytest.raises(ValidationError):
        Condition(
            left="value1",
            operator=">",
            right="value2",
            left_is_path=False,
            right_is_path=False,
        )


# ConditionDict Model Tests
def test_condition_dict_valid():
    condition = Condition(left="path1.field1", operator=">", right=100)
    condition_dict = ConditionDict(condition=condition)
    assert condition_dict.condition == condition


# Group Model Tests
def test_group_valid():
    condition1 = ConditionDict(
        condition=Condition(left="path1.field1", operator=">", right=100)
    )
    condition2 = ConditionDict(
        condition=Condition(left="path2.field2", operator="<", right=200)
    )
    group = Group(group=[condition1, "OR", condition2])
    assert group.group == [condition1, "OR", condition2]


def test_group_invalid_format():
    with pytest.raises(ValidationError):
        Group(group="invalid")  # type: ignore


def test_group_empty_list():
    with pytest.raises(ValidationError):
        Group(group=[])


def test_group_invalid_operator():
    condition1 = ConditionDict(
        condition=Condition(left="path1.field1", operator=">", right=100)
    )
    with pytest.raises(ValidationError):
        Group(group=[condition1, "INVALID_OPERATOR"])


def test_group_consecutive_operators():
    condition1 = ConditionDict(
        condition=Condition(left="path1.field1", operator=">", right=100)
    )
    with pytest.raises(ValidationError):
        Group(group=[condition1, "AND", "OR"])


# CheckOutItem Model Tests
def test_checkout_item_valid():
    checkout_item = CheckOutItem(
        path="section_1.sub_section_1", checkout=["shelf_1.field1", "shelf_1.field2"]
    )
    assert checkout_item.path == "section_1.sub_section_1"
    assert checkout_item.checkout == ["shelf_1.field1", "shelf_1.field2"]


def test_checkout_item_invalid_checkout_empty():
    with pytest.raises(ValidationError):
        CheckOutItem(path="section_1.sub_section_1", checkout=[])


def test_checkout_item_invalid_checkout_all():
    with pytest.raises(ValidationError):
        CheckOutItem(
            path="section_1.sub_section_1", checkout=["*all", "shelf_1.field1"]
        )


# SortItem Model Tests
def test_sort_item_valid():
    sort_item = SortItem(path="section_1.field1", order="asc")
    assert sort_item.path == "section_1.field1"
    assert sort_item.order == "asc"


def test_sort_item_invalid_order():
    with pytest.raises(ValidationError):
        SortItem(path="section_1.field1", order="invalid")


# SetSchema Model Tests
def test_set_schema_valid():
    class MockShelfModel(ShelfModel):
        pass

    set_schema = SetSchema(path="path1", schema_model=MockShelfModel)
    assert set_schema.path == "path1"
    assert set_schema.schema_model == MockShelfModel


def test_set_schema_invalid_path():
    with pytest.raises(ValidationError):
        SetSchema(path="invalid path", schema_model=ShelfModel)


def test_set_schema_path_none_if_library():
    class MockShelfModel(ShelfModel):
        pass

    with pytest.raises(ValidationError):
        SetSchema(path="path1", schema_model=MockShelfModel, is_library=True)


# BuildShelf Model Tests
def test_build_shelf_valid():
    build_shelf = BuildShelf(
        path="section_1.shelf_1", name="shelf_1", data={"field1": "value1"}
    )
    assert build_shelf.path == "section_1.shelf_1"
    assert build_shelf.name == "shelf_1"
    assert build_shelf.data == {"field1": "value1"}


# BuildSection Model Tests
def test_build_section_valid():
    build_section = BuildSection(
        path="section_1", name="sub_section_1", schema_model=None
    )
    assert build_section.path == "section_1"
    assert build_section.name == "sub_section_1"
    assert build_section.schema_model is None


# Write Model Tests
def test_write_valid():
    write = Write(path="section_1.shelf_1", data={"field1": "value1"})
    assert write.path == "section_1.shelf_1"
    assert write.data == {"field1": "value1"}


# CheckOut Model Tests
def test_checkout_valid():
    checkout_item = CheckOutItem(
        path="section_1.sub_section_1", checkout=["shelf_1.field1"]
    )
    checkout = CheckOut(checkout=[checkout_item], limit=10, offset=0)
    assert checkout.checkout == [checkout_item]
    assert checkout.limit == 10
    assert checkout.offset == 0


# Revise Model Tests
def test_revise_valid():
    revise = Revise(path="section_1.shelf_1", data={"field1": "value1"})
    assert revise.path == "section_1.shelf_1"
    assert revise.data == {"field1": "value1"}


# Remove Model Tests
def test_remove_valid():
    remove = Remove(path="section_1.shelf_1", remove_shelf=True)
    assert remove.path == "section_1.shelf_1"
    assert remove.remove_shelf is True


def test_remove_both_flags_true():
    with pytest.raises(ValidationError):
        Remove(path="section_1.shelf_1", remove_shelf=True, remove_section=True)


# Reset Model Tests
def test_reset_valid():
    reset = Reset(path="section_1.shelf_1", reset_shelf=True)
    assert reset.path == "section_1.shelf_1"
    assert reset.reset_shelf is True


def test_reset_both_flags_true():
    with pytest.raises(ValidationError):
        Reset(path="section_1.shelf_1", reset_shelf=True, reset_section=True)
