# Algorithms

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### Dependencies

- **Python 3.8**

### Setup

1. Clone this project.
   ```
    git clone git@github.com:Teamable-Analytics/algorithms.git
   ```
2. Install all dependencies.
   ```
   python3 -m pip install -r requirements.txt
   ```
3. Initialize submodules.
   ```
   git submodule update --init --recursive
   ```
4. You're good to go!
   > Be sure to read any directory-specific README.md and CONVENTION.md files before starting to work.

### Local Run (without Canvas)

To generate teams locally from a JSON payload, without Canvas, Django or a database:

```
python -m pip install -r requirements-local.txt
python -m local_run --input <payload.json> --output <result.json> --seed 1
```

Setup, the sample test run and the input/output format are documented in the
[project documentation](https://teamprojekt-msi-bit-ss26.github.io/documentation/) under "Umsetzung".

### Metrics

For detailed descriptions of each of the metrics we evaluate our algorithms with respect to, please
see [METRICS.md](./METRICS.md).

### Format/Lint Code

In order to format your code for this project, run:

```
python3 -m black .
```

**Note:** If you just want to check if your formatting is accurate without modifying any files,
run `python3 -m black . --check` instead.

### Run Tests

In order to run the test suite, run the following command in your terminal:

```
python3 -m unittest discover tests
```

### Structure

#### /ai

- todo: the logic for each of our algorithms
- todo: the api that serves these algorithms

#### /dataclasses

- dataclasses, types, and enums used in the rest of the repository

#### /old

- everything that this repository used to be

#### /benchmarking

- the tools used to run simulations using our algorithms and benchmark them
- also contains the code to re-generate the benchmarks we use frequently
- contains helpers that allow benchmarking experiments to mock running an algorithm

