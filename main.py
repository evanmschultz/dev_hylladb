from hylladb.db.models import ShelfModel
from hylladb.hyql import (
    BuildShelf,
    Write,
    CheckOut,
    Revise,
    Remove,
    Operators,
)


from rich import print

from hylladb.hyql.hyql import SetSchema


class AnimalSchema(ShelfModel):
    name: str


set_schema_idea: dict = {
    "path": "path1.sub_path1",
    "schema": AnimalSchema,
}


build_shelf_idea: dict = {
    "path": "path1.sub_path1",
    "name": "name1",
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}


checkout_idea: dict = {
    "checkout": [
        {
            "path": "section_1.sub_section_1",
            "checkout": ["shelf_1.field1", "shelf_1.field2"],
        },
        {
            "path": "section_2",
            "checkout": ["*all"],
        },
    ],
    "filters": [
        {
            "condition": {
                "left": "path1.field1",
                "operator": ">=",
                "right": 1,
            }
        },
        "AND",
        {
            "group": [
                {
                    "condition": {
                        "left": "name",
                        "operator": Operators.IN,
                        "right": "path1.field2",
                        "left_is_path": False,
                        "right_is_path": True,
                    }
                },
                "OR",
                {
                    "condition": {
                        "left": "path2.field3",
                        "operator": "<",
                        "right": "path1.field2",
                        "right_is_path": True,
                    }
                },
            ]
        },
    ],
    "sort": [{"path": "path1.field1"}],
    "limit": 10,
    "offset": 0,
}

write_idea: dict = {
    "path": "path1.sub_path1",
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}

revise_idea: dict = {
    "path": "path1.sub_path1",
    "filters": [
        {
            "condition": {
                "left": "path1.field1",
                "operator": "==",
                "right": "value1",
            }
        },
        "AND",
        {
            "group": [
                {
                    "condition": {
                        "left": "path1.field2",
                        "operator": ">",
                        "right": 100,
                    }
                },
                "OR",
                {
                    "condition": {
                        "left": "path2.field3",
                        "operator": "<",
                        "right": "path1.field2",
                        "right_is_path": True,
                    }
                },
            ]
        },
    ],
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}

remove_idea: dict = {
    "path": "path1.sub_path1",
    "filters": [
        {
            "condition": {
                "left": "path1.field1",
                "operator": "==",
                "right": "value1",
            }
        },
        "AND",
        {
            "group": [
                {
                    "condition": {
                        "left": "path1.field2",
                        "operator": ">",
                        "right": 100,
                    }
                },
                "OR",
                {
                    "condition": {
                        "left": "path2.field3",
                        "operator": "<",
                        "right": "path1.field2",
                        "right_is_path": True,
                    }
                },
            ]
        },
    ],
}

print(SetSchema(**set_schema_idea))
print(BuildShelf(**build_shelf_idea))
print(CheckOut(**checkout_idea))
print(Write(**write_idea))
print(Revise(**revise_idea))
print(Remove(**remove_idea))
