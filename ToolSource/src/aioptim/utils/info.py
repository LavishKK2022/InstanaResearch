"""
A utility class to store the supported technologies and their associated
infrastructure.
"""

from aioptim.services.parser import JavaParser, PythonParser

HEADERS = ["language", "extension", "technology", "parser"]

TABLE = [
    ["Python", "py", "pythonRuntimePlatform", PythonParser()],
    ["Java", "java", "springbootApplicationContainer", JavaParser()]
]


def get_col(col_header):
    """
    Extracts the complete row, based on the header.

    Args:
        col_header: The column header for the table

    Raises:
        LookupError: If can not locate requested paramters.

    Returns:
        List of rows in the data table
    """
    try:
        index = HEADERS.index(col_header)
    except ValueError:
        raise LookupError(f"Missing data for {col_header}")
    return [row[index] for row in TABLE]


def get_row(value):
    """
    Retrives the row, if a certain value is inside it

    Args:
        value: The value to check

    Raises:
        LookupError: If the row does not exist

    Returns:
        Row with associated value
    """
    for row in TABLE:
        if value in row:
            return row
    raise LookupError(f"Could not find {value} in parameters table.")


def details(arg1, arg2):
    """
    Retrieves details, regardless of the order of metrics.

    Args:
        arg1: Element in the table or header
        arg2: Element in the table or header

    Raises:
        LookupError: If details cannot be found, anywhere in the table

    Returns:
        The associated row with arg1, arg2 data
    """
    try:
        if arg1 in HEADERS:
            return get_row(arg2)[HEADERS.index(arg1)]
        return get_row(arg1)[HEADERS.index(arg2)]
    except Exception:
        raise LookupError(
            f"Could not find {arg1}, {arg2} in parameters table."
        )
