from typing import Dict, List

from manual_run.variables import Variables


class MapColumns:
    @staticmethod
    def process_row(row: List[str], header_row: List[str]) -> Dict:
        attribute_options_int = Dict[str : List[int]] = {}
        for i, head in enumerate(header_row):
            if head in Variables.attribute_options:
                int_value = -1
                if row[i] in Variables.attribute_options[head]:
                    int_value = Variables.attribute_options[head].index(row[i])
            elif head in Variables.attribute_handlers:
                int_value = Variables.attribute_handlers[head](row[i])
            attribute_options_int[head] = int_value

        return attribute_options_int

    @staticmethod
    def revert_timeslot(time_slot: int) -> str:
        return Variables.attribute_options["Q8"][time_slot]

    @staticmethod
    def revert_tutor_preference(tutor_preference: int) -> str:
        return Variables.attribute_options["Q4"][tutor_preference]

    @staticmethod
    def revert_group_size(group_size: int) -> str:
        return Variables.attribute_options["Q5"][group_size]
