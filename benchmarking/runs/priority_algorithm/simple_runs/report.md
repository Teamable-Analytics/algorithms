# Findings

## Five Diversity Constraints

### Scenario

Constraints:
- Diversify gender min 2
- Diversify gpa min 2
- Diversify age min 2
- Diversify major min 2
- Diversify race min 2

Students were hard coded in order to guarantee a max score of 1.0 and to ensure that the solution is not trivial.

Gender: Male, GPA: A, Age: 20, Major: CompSci, Race: European \
Gender: Female, GPA: B, Age: 20, Major: Math, Race: African \
Gender: Female GPA: B, Age: 21, Major: Math, Race: European \
Gender: Male, GPA: A, Age: 21, Major: CompSci, Race: African \
Gender: Female, GPA: A, Age: 20, Major: Math, Race: European \
Gender: Female, GPA: B, Age: 21, Major: Math, Race: European \
Gender: Male, GPA: B, Age: 21, Major: CompSci, Race: African \
Gender: Male, GPA: A, Age: 20, Major: CompSci, Race: African \
Gender: Male, GPA: B, Age: 20, Major: Math, Race: European \
Gender: Female, GPA: B, Age: 21, Major: CompSci, Race: African \
Gender: Male, GPA: A, Age: 20, Major: Math, Race: African \
Gender: Female, GPA: A, Age: 21, Major: CompSci, Race: European

### Findings

Below we see the results of this run:

<img height='360px' src='imgs/img.png' alt="imgs/img.png">
<img height='360px' src='imgs/img_1.png' alt="imgs/img_1.png">
<br>
<img height='360px' src='imgs/img_2.png' alt="imgs/img_2.png">
<img height="360px" src="imgs/img_3.png" alt="imgs/img_3.png">

We see that the weight start helps a lot, so it's going to be better to look at the random start in order to see how well the priority algorithm does by itself.

Even with only 3 iterations, priority is able to pretty much solve the scenario

<img alt="imgs/img_4.png" height="" src="imgs/img_4.png" width="400"/>

And with 5 iterations, it has the max score with all but the worst settings:

<img alt="imgs/img_6.png" src="imgs/img_6.png" width="400"/>

**The most interesting results are with only 1 iteration.**

We see a clear correlation between higher `MAX_SPREAD` and a higher score, but the same is not true of `MAX_KEEP`

<img alt="imgs/img_7.png" src="imgs/img_7.png" height="400"/>
<img alt="imgs/img_8.png" src="imgs/img_8.png" height="400"/>

We see the same thing in the 3 iteration graph:

<img alt="imgs/img_9.png" height="400" src="imgs/img_9.png"/>
<img alt="imgs/img_10.png" height="400" src="imgs/img_10.png"/>
