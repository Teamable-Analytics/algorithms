# Diversify Gender Min 2 Priority Algorithm Report

## Diversify Gender Min 2

The first set of runs was done with the following constants:

- max keep = 3
- max spread = 3
- max iterate = 300
- max time = 20
- ratio of female students = 0.4
- number of students = 200
- number of teams = 40

These constants were picked for several reasons:

1. Most of them are the baseline constants which had previously been benchmarked.
2. For the diversify gender min 2, the algorithm could place exactly two female students on each team.
3. The constants would not interfere with each other. For example, the max time can interfere with max iterate, as the

For each of the following runs, the baseline constant was used except for one variable, which was incrementally varied
across some range. The range is included with the graphs and information about the run.

In each run, the following algorithm configurations were benchmarked:
- Default Random Algorithm
- Default Weight Algorithm
- Default Priority Algorith (three random swap mutations)
- Priority Algorithm with one Local Max Mutation and two Random Swap Mutations
- Priority Algorithm with one Local Max Random Mutation and two Random Swap Mutations
- Priority Algorithm with one Local Max Double Random Mutation and two Random Swap Mutations
- Priority Algorithm with three Local Max Double Random Mutations
- Priority Algorithm with one Robinhood mutation and two Random Swap Mutations
- Priority Algorithm with one Robinhood Holistic mutation and two Random Swap Mutations

Note: the number of mutations is equal to the maximum spread variable, so these configs will change slightly when that
variable is varied.

### Class Size Run

This run varied the size of the class from 20 to 400 students in increments of 20.

![Varied Class Size Runtimes](../diversify_gender_min_2/graphs/class_size/run_times_base.png)

- The run time for this graph look mostly consistent other than a few seemingly random spikes from the default priority
algorithm and the local max priority configurations. 
- My guess would be that for some reason, the operating system scheduled the tasks poorly, or something else related to
it; however, this should still be investigated to double-check because with a number of trials set so high, I would have 
expected the line to be nearly entirely smooth
- Also, the local max algorithms seem to level off around 20 seconds, which was the cap; however, I think this is likely 
due to the algorithm reaching the maximum number of possible iterations (300), so there would be no need for the 
algorithm to run any longer. Subsequent graphs support this
- For the spike in the double random, I think this might be 

![Varied Class Size Gini](../diversify_gender_min_2/graphs/class_size/average_gini_adjusted_scale.png)

- the gini index was for some reason quite varied with the class size
- for all the configurations other than weight, it seemed to stay within around a 0.55 to 0.6 range, while the weight
algorithm plateaued at about 0.47

![Varied Class Size Priorities Satisfied](../diversify_gender_min_2/graphs/class_size/priorities_satisfied_base.png)

- the priority satisfaction score was very jagged, and other than the random algorithm, seemed to follow no particular
pattern
- I looked briefly at the output team sets, and the teams seem to be decent, but I think it could be useful to query the
json documents with some library to get the exact number of teams that satisfy the constraint at each class size
- This would hopefully let us get a better idea if the teams were relatively consistent, and this had to do with the
metric or scoring function, or if there is some sort of strange issue with different class sizes

![Varied Class Size Priorities Satisfied No Robinhood](../diversify_gender_min_2/graphs/class_size/priorities_satisfied_no_robinhood.png)

- From this graph, we can se that the weight algorithm does slightly worse on average

### Note About Subsequent Runs

- for the subsequent runs, the priority algorithm basically offered no improvement over the weight algorithm
- the weight algorithm basically achieved a near perfect score, and the priority algorithm was essentially unable to 
improve the teams in any meaningful way
- a smaller class size should be investigated, as that is where priority seems to do better, as well as a more complex
set of goals, including project requirements and preferences

### Max Keep Run

This run varied the maximum number of nodes to keep from the output nodes for the priority algorithm.
This was varied between 1 and 10.

![Varied Class Size Runtimes](../diversify_gender_min_2/graphs/max_keep/run_times.png)

![Varied Class Size Gini](../diversify_gender_min_2/graphs/max_keep/average_gini_adjusted_scale.png)

![Varied Class Size Priorities Satisfied](../diversify_gender_min_2/graphs/max_keep/priorities_satisfied.png)

### Max Spread Run

![Varied Class Size Runtimes](../diversify_gender_min_2/graphs/max_spread/run_times.png)

![Varied Class Size Gini](../diversify_gender_min_2/graphs/max_spread/average_gini_adjusted_scale.png)

![Varied Class Size Priorities Satisfied](../diversify_gender_min_2/graphs/max_spread/priorities_satisfied.png)

### Max Time Run

![Varied Class Size Runtimes](../diversify_gender_min_2/graphs/max_time/run_times.png)

![Varied Class Size Gini](../diversify_gender_min_2/graphs/max_time/average_gini_adjusted_scale.png)

![Varied Class Size Priorities Satisfied](../diversify_gender_min_2/graphs/max_time/priorities_satisfied.png)

### Max Iterations Run

![Varied Class Size Runtimes](../diversify_gender_min_2/graphs/num_iterations/run_times.png)

![Varied Class Size Gini](../diversify_gender_min_2/graphs/num_iterations/average_gini_adjusted_scale.png)

![Varied Class Size Priorities Satisfied](../diversify_gender_min_2/graphs/num_iterations/priorities_satisfied.png)

### Summary
