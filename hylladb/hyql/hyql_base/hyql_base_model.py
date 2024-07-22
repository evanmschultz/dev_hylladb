from pydantic import BaseModel, ConfigDict


class HyQLBaseModel(BaseModel, validate_assignment=True):
    """
    A base model for HyQL models.

    This model is used to set the default config for all HyQL models, namely `extra="forbid"` so an error is raised if
    an invalid field is passed to the model.
    """

    model_config = ConfigDict(extra="forbid")
