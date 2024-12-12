# How to run the priority algorithm:
## Files to update:
### attributes.py
This file represents the attributes that are used for the team formation. Each variable is assigned to a unique integer which is simply used as a key to represent it. Aslong are none of these are the same number you can assign any variable to any number you want (aside from numbers 3-6 as they are are used elsewhere).
### default_scenario.py
This file is where the diversity goals should be updated. By default the diversity goals are set to concentrate on student timeslot availability, diversify students on tutor preference, and diversify students on score. To set this file up you must figure out the diversity type of each attribute defined within the **attributes.py** file. The only diversity types you can choose from are "diversity" and "concentrate" (The diversity types can be found in `api/dataclasses/enums.py` if needed). The weight goal of the team formation must also be selected in terms of importance as they are all set to 0 by default. The weight goals are **requirement**, **social preference**, **diversity goal**, and **project preference** (this can be found in `benchmarking/evaluations/goals.py`). **Note that the name function is used to describe what the focus of goals is for the team formation.*
### data_provider.py
This file is where student information is pulled from the CSV and where each students data is proccessed. You will need to adjust the attributes inside of the Student object if you have changed any of the attributes being evaluated in the **attributes.py** file. The string within the processed_data dict (example: -> `processed_date["this_string_here"]`) is the header name in the `.CSV` of the column that relates to the attributes being evaluated. For example if I have an attribute called `TIMESLOT_AVAILABILITY` and in my `.CSV` file I have an column called 'Availability' which represents all of the time availibility options then I would modify the Attribute within the student object to be the following: 
```
Attributes.TIMESLOT_AVAILABILITY.value: [processed_data["Availability"]]
```
### variables.py
This file handles all of the variables that will likely need to be changed in order for the team formation to work. The **attributes_option** dict represents the each non-integer column from the CSV that needs to be considered for the team formation. The key should be the name of the specific column header in the CSV and the value it points to should be a list of every possible value that could be returned for this attribute. The **attribute_handler** dictionary is where you should put any numerical data that needs to be processed. Here you can directly apply any function to it that may need to be called (*ex: rounding to an int*). The **team_size** attribute must also be set on this page as it is used in the code to split up the teams into the desired size.
### manual_priority_run.py
This file handles the priority algorithm and returns the outputted CSV. In the start function make sure the **metrics** list is set to the metrics that you want to use for evaluation. Within the **create_csv** function the team size violation can be removed if it is not wanted. This is commented in the code so that it is clear what variable are able to be deleted if team size violation is not wanted. The `data_fields_input` variables must be populated with their original header values as this is used to convert them back into their original names rather then numbers. If the attributes were changed in the **attributes.py** file, these variables will be need to be changed to reflect that. Lastly, insure the **data_files** list at the end of the function is populated with the correct attributes used as these are the row to be return the in **result.csv** file.  
## input_cvs: 
- The CSV file you provide should be placed inside of the manual_run directory and given the title **input.csv** (unless otherwise changed in variables.py).

## new_csv_output:
- The outputted CSV file will be saved into the manual_run directory. It will be titled **result.csv** (unless otherwise changed in variables.py).

## How to run:
- In the root directory run:
```bash
python3 -m manual_run.manual_priority_run
```
