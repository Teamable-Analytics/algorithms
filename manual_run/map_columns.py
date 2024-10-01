from typing import Dict, List

from manual_run.variables import Variables


def process_row(row: List[str], header_row: List[str]) -> Dict:
    """Convert the non-integer values in the CSV file to integer values

    Args:
        row (List[str]): current row to be processed into teh correct integer values
        header_row (List[str]): the header row of the CSV file

    Returns:
        Dict: a dictionary containing the list of integer values of the
        combined attribute_options and attribute_handlers maps in variables.py
    """
    attribute_options_int: Dict[str, List[int]] = {}
    for i, head in enumerate(header_row):
        int_value = -1
        if head in Variables.attribute_options:
            if row[i] in Variables.attribute_options[head]:
                int_value = Variables.attribute_options[head].index(row[i])
            attribute_options_int[head] = int_value
        elif head in Variables.attribute_handlers:
            int_value = Variables.attribute_handlers[head](row[i])
            attribute_options_int[head] = int_value
    return attribute_options_int


def revert_value(attribute_key: str, value: int) -> str:
    """Revert integer value to the original string based on the attribute key."""
    if attribute_key in Variables.attribute_options:
        options = Variables.attribute_options[attribute_key]
        if value < len(options):
            return options[value]
    return ""
