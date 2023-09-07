## MockStudentProviderSettings

A variety of settings are available for generating a set of mock students.
I hope that `number_of_students`, `number_of_friends`, and `number_of_enemies`
are self-explanatory, but 2 latter arguments just mentioned are "per student" as a note.

### `attribute_ranges`

A dictionary of ids mapping to a list of possible values that a student can have for that attribute.
Values are either integers or enums (explained further down).
When students are being created, a random value from this list will be selected.

We can also pass a list of tuples, where each tuple denotes (value, % chance of that value).

```python
attributes_ranges = {
    1: [(5, 0.2), (10, 0.8)],
}  # implies a set of students where 20% have [5] for attribute_id=1 and 80% have [10]
```

 ---
Purely for convenience, you are allowed to use enums instead of integers in this list.
Read up of `Enum` in python but tldr; it means this:

```python
# what it would have looked like
attributes_ranges = {
    1: [Gpa.A.value, Gpa.B.value],
}

# what this now looks like (avoiding the extra .value)
attributes_ranges = {
    1: [Gpa.A, Gpa.B],
}

# NOTE: this also works
attributes_ranges = {
    1: [(Gpa.A, 0.2), (Gpa.B, 0.8)],
}
```

This is only done for values within the list though, and keys that are from enums will still need to use the `.value`
annoyance.

```python
attribute_ranges = {
    ScenarioAttribute.GPA.value: [1, 2, 3]
}  # works

attribute_ranges = {
    ScenarioAttribute.GPA: [1, 2, 3]
}  # will not work
```

- The type hints from your IDE should make the above difference obvious with warnings.

### `friend_distribution`

The 2 options are "cluster" and "random".
Read the paper for further details but tldr; random is random and cluster implies "friend groups" where each person is
friends with each other person in that cluster.

With "random" it is possible to randomly be both friends and enemies with someone.

### `num_values_per_attribute`

Details how many values to select from `attribute_ranges`, per attribute.
The selection is performed without replacement.

You can either set a:

1. static value that defines how many values to select per student or,
2. a min-max range tuple (e.g. `(1, 4)`)

```python
# each student will have exactly 3 values chosen for attribute_id=2
# each student will have between 4 and 5 values chosen for attribute_id=2
num_values_per_attribute = {
    1: 3,
    2: (4, 5),
}

# NOTE: that the value you give for `num_values_per_attribute` per attribute must
# be <= the number of options defined in `attribute_ranges` for that same attribute.
```

**Example 1:** If you wanted to mock students selecting a ranked list of preferred projects to work on, then we want the mock
students to randomly pick all 3 available values, but pick *exactly* 3 of them.

**Example 2:** If you wanted to mock students selecting which blocks of time in the day they are free to collaborate, then
maybe there are 24 possible values and we want them to select between 3 and 16 of them randomly.

