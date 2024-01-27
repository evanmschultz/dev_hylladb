from hylladb.hyql import (
    Write,
    Checkout,
    Revise,
    Remove,
)
from hylladb.hyql.hyql import LogicOperators

from rich import print


checkout_idea = {
    "checkout": [
        {
            "path": "path1.sub_path1",
            "checkout": ["sub_path1.field1", "sub_path1.field2"],
        },
        {
            "path": "path2",
            "checkout": ["*all"],
        },
    ],
    "filters": [
        {
            "condition": {
                "left": "path1.field1",
                "operator": ">=",
                "right": "value1",
            }
        },
        "AND",
        {
            "group": [
                {
                    "condition": {
                        "left": "path1.field2",
                        "operator": LogicOperators.GREATER_THAN,
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
    "sort": [{"path": "path1.field1", "order": "asc"}],
    "limit": 10,
    "offset": 0,
}

write_idea = {
    "path": "path1.sub_path1",
    "data": {"sub_path1.field1": "value1", "sub_path1.field2": "value2"},
}

revise_idea = {
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

remove_idea = {
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

print(Checkout(**checkout_idea))
print(Write(**write_idea))
print(Revise(**revise_idea))
print(Remove(**remove_idea))
