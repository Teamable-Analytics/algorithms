from typing import Dict, List

col_1_options = [
    "In-person before or after class",
    "In-person nights or weekends",
    "On zoom",
]
col_2_options = [
    "I am looking for a classmate to tutor me in BIOC 202",
    "I am open to being a peer tutor or having a classmate tutor me in BIOC 202. I am uncertain if I should sign up as a tutor or tutee",
    "I am interested in being a peer tutor in BIOC 202",
]
col_3_options = ["1", "2 to 3", "3+"]

class ColumnOptions:
    
    # Each list should define the possible options for each column containing a non-integer value


    @staticmethod
    def process_row(row: List[str]) -> Dict:

        # Map text values to integers
        time_slot_map = {v: (i + 1) for i, v in enumerate(col_1_options)}
        tutor_preference_map = {v: (i + 1) for i, v in enumerate(ColumnOptions.col_2_options)}
        group_size_map = {v: (i + 1) for i, v in enumerate(ColumnOptions.col_3_options)}

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
