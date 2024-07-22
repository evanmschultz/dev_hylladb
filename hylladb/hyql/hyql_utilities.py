from hylladb.hyql.enums import Operators

path_pattern: str = r"^[A-Za-z0-9]+(?:[._][A-Za-z0-9]+)*$"
name_pattern: str = r"^[A-Za-z0-9]+(?:[_][A-Za-z0-9]+)*$"

path_dict: dict = {
    "pattern": path_pattern,
    "description": "HyQL path: a dot separated path the dictionary key, shelf, or section, eg. 'section.shelf.dict_key'",
}


def operator_validator(value: str) -> str:
    """
    Validates if a given string is a valid operator in HyQL based on the members of the Operators Enum.

    Args:
        - `value` (str): The string to be checked.

    Returns:
        - `str`: The string if it is a valid operator.

    Raises:
        - `ValueError`: If the string is not a valid operator.
    """

    if not Operators.is_valid_operator(value):
        raise ValueError(
            "\n    HyllaDB Error:\n"
            "        ---->"
            f"Invalid operator '{value}'. Allowed operators: {', '.join(op.value for op in Operators)}\n"
        )
    return value
