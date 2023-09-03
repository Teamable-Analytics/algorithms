# Algorithms

### Setup

1. Clone this project.
   ```
    git clone git@github.com:Teamable-Analytics/algorithms.git
   ```
2. Install all dependencies.
   ```
   python3 -m pip3 install -r requirements.txt
   ```
3. You're good to go!
   > Be sure to read any directory-specific README.md and CONVENTION.md files before starting to work.

### Metrics

For detailed descriptions of each of the metrics we evaluate our algorithms with respect to, please
see [METRICS.md](./METRICS.md).

### Run Tests

In order to run the test suite, run the following command in your terminal:

```
python3 -m unittest discover tests
```

### Structure

#### /ai

- contains helpers that allow benchmarking experiments to mock running an algorithm
- todo: the logic for each of our algorithms
- todo: the api that serves these algorithms

#### /models

- dataclasses, types, and enums used in the rest of the repository

#### /old

- everything that this repository used to be

#### /benchmarking

- the tools used to run simulations using our algorithms and benchmark them
- also contains the code to re-generate the benchmarks we use frequently

