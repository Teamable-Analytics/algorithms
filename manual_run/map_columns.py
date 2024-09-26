from typing import Dict, List

from manual_run.variables import Variables


class MapColumns:
    @staticmethod
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

    @staticmethod
    def revert_timeslot(time_slot: int) -> str:
        time_slot_list = Variables.attribute_options["Q8"]
        if time_slot < len(time_slot_list):
            return time_slot_list[time_slot]
        else:
            return ""

    @staticmethod
    def revert_tutor_preference(tutor_preference: int) -> str:
        tutor_list = Variables.attribute_options["Q4"]
        if tutor_preference < len(tutor_list):
            return tutor_list[tutor_preference]
        else:
            return ""

    @staticmethod
    def revert_group_size(group_size: int) -> str:
        group_size_list = Variables.attribute_options["Q5"]
        if group_size < len(group_size_list):
            return group_size_list[group_size]
        else:
            return ""
