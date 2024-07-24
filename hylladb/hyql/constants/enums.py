from enum import Enum


class BasicComparisonOperators(str, Enum):
    """
    This Enum defines the basic comparison operators used in HyQL.

    It provides a set of operators specifically designed for basic comparison within query conditions and is meant to be
    used as a guide when you are uncertain of the operator syntax of HyQL.

    Members:
        `EQUAL` (str): Represents the '==' operator for equality.
        `NOT_EQUAL` (str): Represents the '!=' operator for inequality.
        `GREATER_THAN` (str): Represents the '>' operator for greater than comparisons.
        `LESS_THAN` (str): Represents the '<' operator for less than comparisons.
        `GREATER_THAN_OR_EQUAL` (str): Represents the '>=' operator for greater than or equal to comparisons.
        `LESS_THAN_OR_EQUAL` (str): Represents the '<=' operator for less than or equal to comparisons.
    """

    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="


class StringOperators(str, Enum):
    """
    This Enum classifies string-based operators for use in HyQL queries.

    It provides a set of operators specifically designed for string comparison and manipulation within query conditions
    and is meant to be used as a guide when you are uncertain of the operator syntax of HyQL.

    Members:
        `CONTAINS` (str): Checks if a given substring is present within a string.
        `STARTS_WITH` (str): Evaluates if a string starts with a specified substring.
        `ENDS_WITH` (str): Determines if a string ends with a certain substring.
        `MATCHES` (str): Used for regex pattern matching within a string.
    """

    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"


class CollectionOperators(str, Enum):
    """
    This Enum identifies operators specific to collection-based queries in HyQL.

    These operators are useful for performing various operations on collections like lists, sets, and dictionaries within
    HyQL conditions. They are designed to enhance the flexibility and capability of collection handling in queries.

    Members:
        `IN` (str): Checks if an element is present within a collection.
        `NOT_IN` (str): Determines if an element is not part of a collection.
        `ANY` (str): Returns true if any element in a collection meets a certain condition.
        `ALL` (str): Ensures that all elements in a collection satisfy a specified condition.
        `NONE` (str): Verifies that no elements in a collection match a given condition.
        `LENGTH_EQUAL` (str): Compares if the length of a collection is equal to a specific value.
        `LENGTH_GREATER_THAN` (str): Checks if the length of a collection is greater than a certain value.
        `LENGTH_LESS_THAN` (str): Assesses if the length of a collection is less than a specified value.
    """

    IN = "in"
    NOT_IN = "not in"
    ANY = "any"
    ALL = "all"
    NONE = "none"
    LENGTH_EQUAL = "length_eq"
    LENGTH_GREATER_THAN = "length_gt"
    LENGTH_LESS_THAN = "length_lt"


class LogicalOperators(str, Enum):
    """
    This Enum categorizes logical operators used in HyQL to combine or invert conditions.

    Logical operators are fundamental in constructing complex logical expressions in query conditions, allowing for more nuanced and precise data retrieval.

    Members:
        `AND` (str): Logical AND operator, used to ensure all combined conditions are true.
        `OR` (str): Logical OR operator, used when any of the combined conditions being true is sufficient.
        `NOT` (str): Logical NOT operator, used to invert the result of a condition.
    """

    AND = "and"
    OR = "or"
    NOT = "not"


class IdentityOperators(str, Enum):
    """
    This Enum contains operators for identity and type checks in HyQL.

    These operators are particularly useful for type validation and identity comparison, enhancing the robustness and specificity of query conditions.

    Members:
        `IS` (str): Checks if two references point to the same object.
        `IS_NOT` (str): Determines if two references do not point to the same object.
        `IS_INSTANCE` (str): Verifies if an object is an instance of a specified class or type.
    """

    IS = "is"
    IS_NOT = "is not"
    IS_INSTANCE = "isinstance"


# class BitwiseOperators(str, Enum):
#     BITWISE_AND = "&"
#     BITWISE_OR = "|"
#     BITWISE_XOR = "^"
#     BITWISE_NOT = "~"


class NumericOperators(str, Enum):
    """
    This Enum represents operators tailored for numeric comparisons in HyQL.

    They are essential for performing more intricate numeric condition checks, such as comparing absolute values, within HyQL queries.

    Members:
        `ABS_EQUAL` (str): Checks if the absolute value of a number is equal to a given value.
        `ABS_GREATER_THAN` (str): Compares if the absolute value of a number is greater than a specified value.
        `ABS_LESS_THAN` (str): Determines if the absolute value of a number is less than a certain value.
    """

    ABS_EQUAL = "abs_eq"
    ABS_GREATER_THAN = "abs_gt"
    ABS_LESS_THAN = "abs_lt"


class DateTimeOperators(str, Enum):
    """
    This Enum encapsulates operators for date and time comparisons in HyQL.

    These operators are vital for queries that involve date and time criteria, allowing precise temporal data filtering and comparison.

    Members:
        `DATE_EQUAL` (str): Checks if a date is exactly equal to a specified date.
        `DATE_BEFORE` (str): Determines if a date occurs before a given date.
        `DATE_AFTER` (str): Assesses if a date happens after a certain date.
        `DATE_WITHIN` (str): Verifies if a date falls within a specified time frame.
    """

    DATE_EQUAL = "date_eq"
    DATE_BEFORE = "date_before"
    DATE_AFTER = "date_after"
    DATE_WITHIN = "date_within"


class Operators(str, Enum):
    """
    This Enum class provides a comprehensive collection of operators used in HyQL for various types of comparisons and
    logical operations. It integrates basic comparison, string manipulation, collection handling, logical, identity
    type, numeric, and date-time operators.

    It is meant to be used as a guide when you are uncertain of the operator syntax of HyQL. If you want easier access to
    operators of a specific type, you can import the following Enums: `BasicComparison`, `StringOperators`,
    `CollectionOperators`, `LogicalOperators`, `IdentityTypeOperators`, `NumericOperators`, and `DateTimeOperators`.

    Members:
        # Basic Comparison Operators
        `EQUAL` (str): Represents the '==' operator for equality comparison.
        `NOT_EQUAL` (str): Represents the '!=' operator for inequality comparison.
        `GREATER_THAN` (str): Represents the '>' operator for greater than comparisons.
        `LESS_THAN` (str): Represents the '<' operator for less than comparisons.
        `GREATER_THAN_OR_EQUAL` (str): Represents the '>=' operator for greater than or equal to comparisons.
        `LESS_THAN_OR_EQUAL` (str): Represents the '<=' operator for less than or equal to comparisons.

        # String Operators
        `CONTAINS` (str): Checks if a given substring is present within a string.
        `STARTS_WITH` (str): Evaluates if a string starts with a specified substring.
        `ENDS_WITH` (str): Determines if a string ends with a certain substring.
        `MATCHES` (str): Used for regex pattern matching within a string.

        # Collection Operators
        `IN` (str): Checks if an element is present within a collection.
        `NOT_IN` (str): Determines if an element is not part of a collection.
        `ANY` (str): Returns true if any element in a collection meets a certain condition.
        `ALL` (str): Ensures that all elements in a collection satisfy a specified condition.
        `NONE` (str): Verifies that no elements in a collection match a given condition.
        `LENGTH_EQUAL` (str): Compares if the length of a collection is equal to a specific value.
        `LENGTH_GREATER_THAN` (str): Checks if the length of a collection is greater than a certain value.
        `LENGTH_LESS_THAN` (str): Assesses if the length of a collection is less than a specified value.

        # Logical Operators
        `AND` (str): Logical AND operator, used to ensure all combined conditions are true.
        `OR` (str): Logical OR operator, used when any of the combined conditions being true is sufficient.
        `NOT` (str): Logical NOT operator, used to invert the result of a condition.

        # Identity Type Operators
        `IS` (str): Checks if two references point to the same object.
        `IS_NOT` (str): Determines if two references do not point to the same object.
        `IS_INSTANCE` (str): Verifies if an object is an instance of a specified class or type.

        # Numeric Operators
        `ABS_EQUAL` (str): Checks if the absolute value of a number is equal to a given value.
        `ABS_GREATER_THAN` (str): Compares if the absolute value of a number is greater than a specified value.
        `ABS_LESS_THAN` (str): Determines if the absolute value of a number is less than a certain value.

        # DateTime Operators
        `DATE_EQUAL` (str): Checks if a date is exactly equal to a specified date.
        `DATE_BEFORE` (str): Determines if a date occurs before a given date.
        `DATE_AFTER` (str): Assesses if a date happens after a certain date.
        `DATE_WITHIN` (str): Verifies if a date falls within a specified time frame.
    """

    # Basic comparison operators
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    # String operators
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"
    # Collection operators
    IN = "in"
    NOT_IN = "not in"
    ANY = "any"
    ALL = "all"
    NONE = "none"
    LENGTH_EQUAL = "length_eq"
    LENGTH_GREATER_THAN = "length_gt"
    LENGTH_LESS_THAN = "length_lt"
    # Logical operators
    AND = "and"
    OR = "or"
    NOT = "not"
    # Identity type operators
    IS = "is"
    IS_NOT = "is not"
    IS_INSTANCE = "isinstance"
    # # Bitwise operators
    # BITWISE_AND = "&"
    # BITWISE_OR = "|"
    # BITWISE_XOR = "^"
    # BITWISE_NOT = "~"
    # Numeric operators
    ABS_EQUAL = "abs_eq"
    ABS_GREATER_THAN = "abs_gt"
    ABS_LESS_THAN = "abs_lt"
    # DateTime operators
    DATE_EQUAL = "date_eq"
    DATE_BEFORE = "date_before"
    DATE_AFTER = "date_after"
    DATE_WITHIN = "date_within"

    @classmethod
    def is_valid_operator(cls, value: str) -> bool:
        """
        Checks if a given string is a valid operator in HyQL based on the members of the LogicOperators Enum.

        Args:
            `value` (str): The string to be checked.

        Returns:
            `bool`: True if the string is a valid operator, False otherwise.
        """
        return any(value == op for op in cls)
