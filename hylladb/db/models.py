from pydantic import BaseModel, ConfigDict


class ShelfModel(BaseModel, validate_assignment=True):
    """A model for defining the schema allowed in a shelf."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
