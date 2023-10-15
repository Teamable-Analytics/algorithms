from typing import Dict, Any, List


def prune_dictionary_keys(
    dictionary: Dict[str, Any], keys_to_keep: List[str]
) -> Dict[str, Any]:
    return {key: value for key, value in dictionary.items() if key in keys_to_keep}
