import pytest
from pydantic import ValidationError

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
from hylladb.hyql.hyql import BuildSection
from hylladb.hyql.hyql_base.schema_model import SchemaModel


# Condition Model Tests
def test_condition_valid() -> None:
    """
    Test creating a valid Condition model.
    Ensures that a Condition object with valid inputs is created successfully.
    """
    condition = Condition(left_path="path1.field1", operator=">", right=100)
    assert condition.left_path == "path1.field1"
    assert condition.operator == ">"
    assert condition.right == 100


def test_condition_invalid_operator() -> None:
    """
    Test creating a Condition model with an invalid operator.
    Ensures that a ValidationError is raised for an invalid operator.
    """
    with pytest.raises(ValueError):
        Condition(left_path="path1.field1", operator="invalid", right=100)


def test_condition_invalid_left_path() -> None:
    """
    Test creating a Condition model with an invalid left path.
    Ensures that a ValidationError is raised for an invalid left path string.
    """
    with pytest.raises(ValidationError):
        Condition(left_path="invalid path", operator=">", right=100)


def test_condition_invalid_right_path() -> None:
    """
    Test creating a Condition model with an invalid right path.
    Ensures that a ValidationError is raised for an invalid right path string when right_is_path is True.
    """
    with pytest.raises(ValidationError):
        Condition(
            left_path="path1.field1",
            operator=">",
            right="invalid path",
            right_is_path=True,
        )


# ConditionDict Model Tests
def test_condition_dict_valid() -> None:
    """
    Test creating a valid ConditionDict model.
    Ensures that a ConditionDict object with a valid Condition is created successfully.
    """
    condition = Condition(left_path="path1.field1", operator=">", right=100)
    condition_dict = ConditionDict(condition=condition)
    assert condition_dict.condition == condition


# Group Model Tests
def test_group_valid() -> None:
    """
    Test creating a valid Group model.
    Ensures that a Group object with valid conditions and operators is created successfully.
    """
    condition1 = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    condition2 = ConditionDict(
        condition=Condition(left_path="path2.field2", operator="<", right=200)
    )
    group = Group(group=[condition1, "OR", condition2])
    assert group.group == [condition1, "OR", condition2]


def test_group_invalid_format() -> None:
    """
    Test creating a Group model with an invalid format.
    Ensures that a ValidationError is raised for an invalid group format.
    """
    with pytest.raises(ValidationError):
        Group(group="invalid")  # type: ignore


def test_group_empty_list() -> None:
    """
    Test creating a Group model with an empty list.
    Ensures that a ValidationError is raised for an empty group list.
    """
    with pytest.raises(ValidationError):
        Group(group=[])


def test_group_invalid_operator() -> None:
    """
    Test creating a Group model with an invalid logical operator.
    Ensures that a ValidationError is raised for an invalid logical operator in the group list.
    """
    condition1 = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    with pytest.raises(ValidationError):
        Group(group=[condition1, "INVALID_OPERATOR"])


def test_group_consecutive_operators() -> None:
    """
    Test creating a Group model with consecutive logical operators.
    Ensures that a ValidationError is raised for consecutive logical operators in the group list.
    """
    condition1 = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    with pytest.raises(ValidationError):
        Group(group=[condition1, "AND", "OR"])


# CheckOutItem Model Tests
def test_checkout_item_valid() -> None:
    """
    Test creating a valid CheckOutItem model.
    Ensures that a CheckOutItem object with valid inputs is created successfully.
    """
    checkout_item = CheckOutItem(
        path="section_1.sub_section_1", checkout=["shelf_1.field1", "shelf_1.field2"]
    )
    assert checkout_item.path == "section_1.sub_section_1"
    assert checkout_item.checkout == ["shelf_1.field1", "shelf_1.field2"]


def test_checkout_item_invalid_checkout_empty() -> None:
    """
    Test creating a CheckOutItem model with an empty checkout list.
    Ensures that a ValidationError is raised for an empty checkout list.
    """
    with pytest.raises(ValidationError):
        CheckOutItem(path="section_1.sub_section_1", checkout=[])


def test_checkout_item_invalid_checkout_all() -> None:
    """
    Test creating a CheckOutItem model with both '*all' and other items in the checkout list.
    Ensures that a ValidationError is raised if '*all' is not the only item in the list.
    """
    with pytest.raises(ValidationError):
        CheckOutItem(
            path="section_1.sub_section_1", checkout=["*all", "shelf_1.field1"]
        )


# SortItem Model Tests
def test_sort_item_valid() -> None:
    """
    Test creating a valid SortItem model.
    Ensures that a SortItem object with valid inputs is created successfully.
    """
    sort_item = SortItem(path="section_1.field1", order="asc")
    assert sort_item.path == "section_1.field1"
    assert sort_item.order == "asc"


def test_sort_item_invalid_order() -> None:
    """
    Test creating a SortItem model with an invalid order.
    Ensures that a ValidationError is raised for an invalid sort order.
    """
    with pytest.raises(ValidationError):
        SortItem(path="section_1.field1", order="invalid")


# CheckOut Model Tests


def test_checkout_valid_filters_with_condition_dict() -> None:
    """
    Test creating a valid CheckOut model with filters containing ConditionDict.
    Ensures that a CheckOut object with valid ConditionDict filters is created successfully.
    """
    condition_dict = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    checkout_item = CheckOutItem(
        path="section_1.sub_section_1", checkout=["shelf_1.field1"]
    )
    checkout = CheckOut(
        checkout=[checkout_item], filters=[condition_dict], limit=10, offset=0
    )
    assert checkout.filters == [condition_dict]


def test_checkout_valid_filters_with_group() -> None:
    """
    Test creating a valid CheckOut model with filters containing Group.
    Ensures that a CheckOut object with valid Group filters is created successfully.
    """
    condition_dict1 = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    condition_dict2 = ConditionDict(
        condition=Condition(left_path="path2.field2", operator="<", right=200)
    )
    group = Group(group=[condition_dict1, "OR", condition_dict2])
    checkout_item = CheckOutItem(
        path="section_1.sub_section_1", checkout=["shelf_1.field1"]
    )
    checkout = CheckOut(checkout=[checkout_item], filters=[group], limit=10, offset=0)
    assert checkout.filters == [group]


def test_checkout_invalid_filters_format() -> None:
    """
    Test creating a CheckOut model with invalid filters format.
    Ensures that a ValidationError is raised for invalid filters format.
    """
    checkout_item = CheckOutItem(
        path="section_1.sub_section_1", checkout=["shelf_1.field1"]
    )
    with pytest.raises(ValidationError):
        CheckOut(
            checkout=[checkout_item], filters=["invalid_filter"], limit=10, offset=0
        )


# SetSchema Model Tests
def test_set_schema_valid() -> None:
    """
    Test creating a valid SetSchema model.
    Ensures that a SetSchema object with valid inputs is created successfully.
    """

    class MockShelfModel(SchemaModel):
        pass

    set_schema = SetSchema(path="path1", schema_model=MockShelfModel)
    assert set_schema.path == "path1"
    assert set_schema.schema_model == MockShelfModel


def test_set_schema_invalid_path() -> None:
    """
    Test creating a SetSchema model with an invalid path.
    Ensures that a ValidationError is raised for an invalid path string.
    """
    with pytest.raises(ValidationError):
        SetSchema(path="invalid path", schema_model=SchemaModel)


def test_set_schema_path_none_if_library() -> None:
    """
    Test creating a SetSchema model with a path when is_library is True.
    Ensures that a ValidationError is raised if path is not None when is_library is True.
    """

    class MockShelfModel(SchemaModel):
        pass

    with pytest.raises(ValidationError):
        SetSchema(path="path1", schema_model=MockShelfModel, is_library=True)


# BuildShelf Model Tests
def test_build_shelf_valid() -> None:
    """
    Test creating a valid BuildShelf model.
    Ensures that a BuildShelf object with valid inputs is created successfully.
    """
    build_shelf = BuildShelf(
        path="section_1.shelf_1", name="shelf_1", data={"field1": "value1"}
    )
    assert build_shelf.path == "section_1.shelf_1"
    assert build_shelf.name == "shelf_1"
    assert build_shelf.data == {"field1": "value1"}


# BuildSection Model Tests
def test_build_section_valid() -> None:
    """
    Test creating a valid BuildSection model.
    Ensures that a BuildSection object with valid inputs is created successfully.
    """
    build_section = BuildSection(
        path="section_1", name="sub_section_1", schema_model=None
    )
    assert build_section.path == "section_1"
    assert build_section.name == "sub_section_1"
    assert build_section.schema_model is None


# Write Model Tests
def test_write_valid() -> None:
    """
    Test creating a valid Write model.
    Ensures that a Write object with valid inputs is created successfully.
    """
    write = Write(path="section_1.shelf_1", data={"field1": "value1"})
    assert write.path == "section_1.shelf_1"
    assert write.data == {"field1": "value1"}


# CheckOut Model Tests
def test_checkout_valid() -> None:
    """
    Test creating a valid CheckOut model.
    Ensures that a CheckOut object with valid inputs is created successfully.
    """
    checkout_item = CheckOutItem(
        path="section_1.sub_section_1", checkout=["shelf_1.field1"]
    )
    checkout = CheckOut(checkout=[checkout_item], limit=10, offset=0)
    assert checkout.checkout == [checkout_item]
    assert checkout.limit == 10
    assert checkout.offset == 0


def test_revise_valid_filters_with_condition_dict() -> None:
    """
    Test creating a valid Revise model with filters containing ConditionDict.
    Ensures that a Revise object with valid ConditionDict filters is created successfully.
    """
    condition_dict = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    revise = Revise(
        path="section_1.shelf_1", filters=[condition_dict], data={"field1": "value1"}
    )
    assert revise.filters == [condition_dict]


def test_revise_valid_filters_with_group() -> None:
    """
    Test creating a valid Revise model with filters containing Group.
    Ensures that a Revise object with valid Group filters is created successfully.
    """
    condition_dict1 = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    condition_dict2 = ConditionDict(
        condition=Condition(left_path="path2.field2", operator="<", right=200)
    )
    group = Group(group=[condition_dict1, "OR", condition_dict2])
    revise = Revise(
        path="section_1.shelf_1", filters=[group], data={"field1": "value1"}
    )
    assert revise.filters == [group]


def test_revise_invalid_filters_format() -> None:
    """
    Test creating a Revise model with invalid filters format.
    Ensures that a ValidationError is raised for invalid filters format.
    """
    with pytest.raises(ValidationError):
        Revise(
            path="section_1.shelf_1",
            filters=["invalid_filter"],
            data={"field1": "value1"},
        )


def test_revise_valid() -> None:
    """
    Test creating a valid Revise model.
    Ensures that a Revise object with valid inputs is created successfully.
    """
    revise = Revise(path="section_1.shelf_1", data={"field1": "value1"})
    assert revise.path == "section_1.shelf_1"
    assert revise.data == {"field1": "value1"}


def test_remove_valid_filters_with_condition_dict() -> None:
    """
    Test creating a valid Remove model with filters containing ConditionDict.
    Ensures that a Remove object with valid ConditionDict filters is created successfully.
    """
    condition_dict = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    remove = Remove(
        path="section_1.shelf_1", filters=[condition_dict], remove_shelf=True
    )
    assert remove.filters == [condition_dict]


def test_remove_valid_filters_with_group() -> None:
    """
    Test creating a valid Remove model with filters containing Group.
    Ensures that a Remove object with valid Group filters is created successfully.
    """
    condition_dict1 = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    condition_dict2 = ConditionDict(
        condition=Condition(left_path="path2.field2", operator="<", right=200)
    )
    group = Group(group=[condition_dict1, "OR", condition_dict2])
    remove = Remove(path="section_1.shelf_1", filters=[group], remove_shelf=True)
    assert remove.filters == [group]


def test_remove_invalid_filters_format() -> None:
    """
    Test creating a Remove model with invalid filters format.
    Ensures that a ValidationError is raised for invalid filters format.
    """
    with pytest.raises(ValidationError):
        Remove(path="section_1.shelf_1", filters=["invalid_filter"], remove_shelf=True)


def test_remove_valid() -> None:
    """
    Test creating a valid Remove model.
    Ensures that a Remove object with valid inputs is created successfully.
    """
    remove = Remove(path="section_1.shelf_1", remove_shelf=True)
    assert remove.path == "section_1.shelf_1"
    assert remove.remove_shelf is True
    assert remove.remove_section is False


def test_remove_both_flags_true() -> None:
    """
    Test creating a Remove model with both remove_shelf and remove_section set to True.
    Ensures that a ValidationError is raised if both remove_shelf and remove_section are True.
    """
    with pytest.raises(ValidationError):
        Remove(path="section_1.shelf_1", remove_shelf=True, remove_section=True)


def test_reset_valid_filters_with_condition_dict() -> None:
    """
    Test creating a valid Reset model with filters containing ConditionDict.
    Ensures that a Reset object with valid ConditionDict filters is created successfully.
    """
    condition_dict = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    reset = Reset(path="section_1.shelf_1", filters=[condition_dict], reset_shelf=True)
    assert reset.filters == [condition_dict]


def test_reset_valid_filters_with_group() -> None:
    """
    Test creating a valid Reset model with filters containing Group.
    Ensures that a Reset object with valid Group filters is created successfully.
    """
    condition_dict1 = ConditionDict(
        condition=Condition(left_path="path1.field1", operator=">", right=100)
    )
    condition_dict2 = ConditionDict(
        condition=Condition(left_path="path2.field2", operator="<", right=200)
    )
    group = Group(group=[condition_dict1, "OR", condition_dict2])
    reset = Reset(path="section_1.shelf_1", filters=[group], reset_shelf=True)
    assert reset.filters == [group]


def test_reset_invalid_filters_format() -> None:
    """
    Test creating a Reset model with invalid filters format.
    Ensures that a ValidationError is raised for invalid filters format.
    """
    with pytest.raises(ValidationError):
        Reset(path="section_1.shelf_1", filters=["invalid_filter"], reset_shelf=True)


def test_reset_valid() -> None:
    """
    Test creating a valid Reset model.
    Ensures that a Reset object with valid inputs is created successfully.
    """
    reset = Reset(path="section_1.shelf_1", reset_shelf=True)
    assert reset.path == "section_1.shelf_1"
    assert reset.reset_shelf is True
    assert reset.reset_section is False


def test_reset_both_flags_true() -> None:
    """
    Test creating a Reset model with both reset_shelf and reset_section set to True.
    Ensures that a ValidationError is raised if both reset_shelf and reset_section are True.
    """
    with pytest.raises(ValidationError):
        Reset(path="section_1.shelf_1", reset_shelf=True, reset_section=True)
