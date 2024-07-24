from rich import print
from hylladb.hyql import (
    BuildShelf,
    CheckOut,
    Operators,
    Remove,
    Revise,
    Write,
    SetSchema,
    Transaction,
    Condition,
    ConditionDict,
    Group,
    SortItem,
)
from hylladb.hyql.hyql_base.schema_model import SchemaModel


class AnimalSchema(SchemaModel):
    name: str


set_schema_idea = {
    "path": "path1.sub_path1",
    "schema_model": AnimalSchema,
}

build_shelf_idea = {
    "path": "path1.sub_path1",
    "name": "name1",
    "data": AnimalSchema(name="value1"),
}

build_section_idea = {
    "path": "section_1.sub_section_1",
    "name": "name1",
    "schema_model": AnimalSchema,
}

checkout_idea = {
    "path": "section_1.sub_section_1",
    "checkout": ["shelf_1.field1", "shelf_1.field2"],
    "filters": [
        ConditionDict(
            condition=Condition(
                left_path="path1.field1",
                operator=">=",
                right=1,
            )
        ),
        "AND",
        Group(
            group=[
                ConditionDict(
                    condition=Condition(
                        left_path="name",
                        operator=Operators.IN,
                        right="path1.field2",
                        right_is_path=True,
                    )
                ),
                "OR",
                ConditionDict(
                    condition=Condition(
                        left_path="path2.field3",
                        operator="<",
                        right="path1.field2",
                        right_is_path=True,
                    )
                ),
            ]
        ),
    ],
    "sort": [SortItem(path="path1.field1", order="asc")],
    "limit": 10,
    "offset": 0,
}

write_idea = {
    "path": "path1.sub_path1",
    "data": AnimalSchema(name="value1"),
}

revise_idea = {
    "path": "path1.sub_path1",
    "data": AnimalSchema(name="new_value1"),
}


remove_idea = {
    "path": "path1.sub_path1",
    "filters": [
        ConditionDict(
            condition=Condition(
                left_path="path1.field1",
                operator="==",
                right="value1",
            )
        ),
        "AND",
        Group(
            group=[
                ConditionDict(
                    condition=Condition(
                        left_path="path1.field2",
                        operator=">",
                        right=100,
                    )
                ),
                "OR",
                ConditionDict(
                    condition=Condition(
                        left_path="path2.field3",
                        operator="<",
                        right="path1.field2",
                        right_is_path=True,
                    )
                ),
            ]
        ),
    ],
}

print(SetSchema(**set_schema_idea))
print(BuildShelf(**build_shelf_idea))
print(CheckOut(**checkout_idea))
print(Write(**write_idea))
print(Revise(**revise_idea))
print(Remove(**remove_idea))

# Create a transaction with all the above queries
transaction_idea = {
    "queries": [
        Write(**write_idea),
        Remove(**remove_idea),
        Revise(**revise_idea),
        CheckOut(**checkout_idea),
        BuildShelf(**build_shelf_idea),
        SetSchema(**set_schema_idea),
    ]
}

print(Transaction(**transaction_idea))
