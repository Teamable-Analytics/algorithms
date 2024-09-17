from enum import Enum
from typing import Dict, List


class Attributes(Enum):
    SCORE = 0
    TUTOR_PREFERENCE = 1
    GROUP_SIZE = 2

    @staticmethod
    def process_row(row: List[str]) -> Dict:
        """
        Process a row of the CSV file and map non-integer attributes to integers.

        Args:
            row (List[str]): A row from the CSV file containing student data.

        Returns:
            Dict: A dictionary with processed attributes for the student.
        """
        col_1_options = ['In-person before or after class', 'In-person nights or weekends', 'On zoom']
        col_2_options = ['I am looking for a classmate to tutor me in BIOC 202', 'I am open to being a peer tutor or having a classmate tutor me in BIOC 202. I am uncertain if I should sign up as a tutor or tutee', 'I am interested in being a peer tutor in BIOC 202']
        col_3_options = ['1', '2 to 3', '3+']

        # Process timeslot (column 1)
        if row[1] == col_1_options[0]:
            timeslot = 1
        elif row[1] == col_1_options[1]:
            timeslot = 2
        elif row[1] == col_1_options[2]:
            timeslot = 3
        else:
            raise ValueError(f"Invalid timeslot: {row[1]}")

        # Process tutor preference (column 2)
        if row[2] == col_2_options[0]:
            tutor_preference = 1
        elif row[2] == col_2_options[1]:
            tutor_preference = 2
        elif row[2] == col_2_options[2]:
            tutor_preference = 3
        else:
            raise ValueError(f"Invalid tutor preference: {row[2]}")

        # Process group size (column 3)
        if row[3] == col_3_options[0]:
            group_size = 1
        elif row[3] == col_3_options[1]:
            group_size = 2
        elif row[3] == col_3_options[2]:
            group_size = 3
        else:
            group_size = -1

        # Process score (column 4)
        score = float(row[4])
        score = 1 if score >= 0 else 0

        return {
            "timeslot": timeslot,
            "tutor_preference": tutor_preference,
            "group_size": group_size,
            "score": score
        }
