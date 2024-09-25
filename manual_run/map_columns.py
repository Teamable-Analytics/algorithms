from typing import Dict, List
from manual_run.variables import Variables


class MapColumns:
    
    # Each list should define the possible options for each column containing a non-integer value

    @staticmethod
    def process_row(row: List[str], header_row: List[str]) -> Dict:
        column_options_int = Dict[str : List[int]] = {}
        for i, head in enumerate(header_row):
            if head in Variables.column_options: 
                if row[i] in Variables.column_options[head]:
                    int_value = Variables.column_options[head].index(row[i])
                else:
                    int_value = -1
                column_options_int[head] = []
                column_options_int[head].append(int_value)
            elif head == "zPos":
                score = 1 if float(row[i]) >= 0 else 0
                column_options_int["score"] = []
                column_options_int["score"].append(score)
                    
            return {
                column_options_int
            }
                












































    @staticmethod
    def process_row(row: List[str]) -> Dict:

        # Map text values to integers
        time_slot_map = {v: (i + 1) for i, v in enumerate(col_1_options)}
        tutor_preference_map = {v: (i + 1) for i, v in enumerate(col_2_options)}
        group_size_map = {v: (i + 1) for i, v in enumerate(col_3_options)}

        time_slot = time_slot_map.get(row[1], None)
        tutor_preference = tutor_preference_map.get(row[17], None)
        if row[18] == "":
            group_size = -1
        else:
            group_size = group_size_map.get(row[18], None)

        score = 1 if float(row[20]) >= 0 else 0

        return {
            "time_slot": time_slot,
            "tutor_preference": tutor_preference,
            "group_size": group_size,
            "score": score,
        }

    @staticmethod
    def revert_timeslot(time_slot: int) -> str:
        return ColumnOptions.col_1_options[time_slot - 1]

    @staticmethod
    def revert_tutor_preference(tutor_preference: int) -> str:
        return ColumnOptions.col_2_options[tutor_preference - 1]

    @staticmethod
    def revert_group_size(group_size: int) -> str:
        return ColumnOptions.col_3_options[group_size - 1]
