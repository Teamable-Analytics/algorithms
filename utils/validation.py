from typing import Any, List


def is_unique(items: List[Any], attr: str = None):
    """
    Checks if a list of anything contains unique elements (within the list).
    If attr is given, checks if they each have unique 'attr', where attr is an attribute of item's type.

    NOTE: Assumes that if attr is given, all dicts/objects in items have that 'attr' defined.
    """
    if not attr:
        return len(set(items)) == len(items)

    types_of_items = set([type(item) for item in items])
    if len(types_of_items) > 1:
        raise ValueError("All items should be of the same type.")

    # cast back to list to access by index
    if list(types_of_items)[0] == dict:
        item_attrs = [item[attr] for item in items if item[attr]]
    else:
        item_attrs = [getattr(item, attr) for item in items if getattr(item, attr)]

    return len(set(item_attrs)) == len(item_attrs)
