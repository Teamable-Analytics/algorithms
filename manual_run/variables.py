from typing import Dict, List


class Variables:
    # The number of student must match the number of students in the input CSV file
    num_students = 26
    team_size = 4
    
    # Each dictionary should define the name of the column and each possible options for each column containing a non-integer value
    column_options = Dict[str : List[str]] = {
        "Q8": ["In-person before or after class", "In-person nights or weekends", "On zoom",],
        "Q4": ["I am looking for a classmate to tutor me in BIOC 202", "I am open to being a peer tutor or having a classmate tutor me in BIOC 202. I am uncertain if I should sign up as a tutor or tutee", "I am interested in being a peer tutor in BIOC 202"],
        "Q5": ["1", "2 to 3", "3+"]
    }
    
    
    
    # Enter the name of the columns from the provided CSV file
    data_fields = [
            ["ResponseId", "Q8", "Q4", "Q5", "zPos"]
        ]
    
    # Enter the name of the inputted CSV file
    input_csv_file = "input.csv"
    
    # Selected the name of the outputted CSV file
    output_file_name = "result.csv"
    
    