# How to run the weight algorithm:

## input_cvs: 
- The **input_csv** folder is where you should put CSV files that you would like to run the weight algorithm on. The weight algorithm can only be run on one CSV file at a time but you may have as many csv files inside of the **input_csv** file as you would like.

## new_csv_output:
- The **new_csv_output** folder is where the final CSV file will go after the algorithm has been run on it. Empty this folder each time you run the algorithm otherwise any remaining CSV file will get overwritten.

## How to run:
- In the root directory run:
```bash
pip install faker
```
```bash
python3 -m benchmarking.runs.csv_weight_run_revised.weight_run_revised
```