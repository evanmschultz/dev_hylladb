from hylladb.hyql import (
    HyWrite,
    HyCheckout,
    HyRevise,
    HyRemove,
    FilterConditions,
    SortCondition,
)

from rich import print

# Create
create_query = HyWrite(
    path="parent_section.child_section.shelf_name",
    data={"field1": "new value", "field2": {"subfield": "another value"}},
)

# Read
query = HyCheckout(
    path="parent_section.child_section.shelf_name",
    checkout=["field1", "field2.subfield"],
    filter=FilterConditions(conditions=["field1 == 'value'"]),
    sort=[SortCondition(key="field1", order="asc")],
    limit=10,
    offset=0,
)

# Update
update_query = HyRevise(
    path="parent_section.child_section.shelf_name",
    filters=FilterConditions(conditions=["field1 == 'old value'"]),
    update_data={"field1": "updated value"},
)

# Delete
delete_query = HyRemove(
    path="parent_section.child_section.shelf_name",
    filters=[
        FilterConditions(
            conditions=[
                "field1 == 'value to delete'",
                "field2 not in 'another value'",
            ]
        )
    ],
)

print(create_query, "\n")
print(query, "\n")
print(update_query, "\n")
print(delete_query)

from hylladb.model_generator.auto_generate_models import (
    generate_models,
    User,
)

generate_models(User)

from hylladb.generated_models import UserReturn_ID
from uuid import uuid4

print(UserReturn_ID(id=uuid4()))
