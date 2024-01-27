from hylladb.hyql import (
    Write,
    Checkout,
    Revise,
    Remove,
)

from rich import print

# Create
# create_query = Write(
#     path="parent_section.child_section.shelf_name",
#     data={"field1": "new value", "field2": {"subfield": "another value"}},
# )

# Read
# query = Checkout(
#     path="parent_section.child_section.shelf_name",
#     checkout=["field1", "field2.subfield"],
#     filter=FilterConditions(conditions=["field1 == 'value'"]),
#     sort=[SortCondition(key="field1", order="asc")],
#     limit=10,
#     offset=0,
# )

# Update
# update_query = Revise(
#     path="parent_section.child_section.shelf_name",
#     filters=FilterConditions(conditions=["field1 == 'old value'"]),
#     data={"field1": "updated value"},
# )

# # Delete
# delete_query = Remove(
#     path="parent_section.child_section.shelf_name",
#     filters=[
#         FilterConditions(
#             conditions=[
#                 "field1 == 'value to delete'",
#                 "field2 not in 'another value'",
#             ]
#         )
#     ],
# )

# print(create_query, "\n")
# print(query, "\n")
# print(update_query, "\n")
# print(delete_query)

# from hylladb.model_generator.auto_generate_models import (
#     generate_models,
#     User,
# )

# generate_models(User)

# from hylladb.generated_models import UserReturn_ID
# from uuid import uuid4

# print(UserReturn_ID(id=uuid4()))

# print(
#     "\n[bold][blue]Hylla[/blue][yellow]DB[/yellow] [red]Error:[/red][/bold]\n"
#     "[red]----> [/red]"
#     "The number of keys in the path map does not match the number of path maps. An error must have occurred"
#     " while removing the path map or before. The database may be in an inconsistent state and corrupted.\n"
# )

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
