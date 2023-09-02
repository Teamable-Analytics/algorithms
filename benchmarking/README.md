### Structure
#### /data
- providers to generate mock students for testing purposes
- stores any static data we are also using for testing
  - any stored static data will need accompanying Providers to be used within simulations

#### /evaluations
- graphing module
- the metrics upon which we evaluate algorithm performance (see [/METRICS.md](../METRICS.md))
- scenarios: representations of an instructor's goals when forming teams
  - we will be creating scenarios and seeing how each algorithm performs on them

#### /runs
- completed segments of code that produce the graphs/values needed to answer a given research question
  - i.e. "how does each algorithm perform when our goal is to diversify 1 attribute?"
  - i.e. "how does each algorithm perform when our goal is to diversify 1 attribute and we vary class size?"

#### /simulation
- the service that allows for simulating all the algorithms running and calculating the metrics you asked for