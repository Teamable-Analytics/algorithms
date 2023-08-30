# Algorithm Sandbox

## Metrics

### Friend/Enemy Satisfaction
* Symbols
    * $n =$ number of the students numbered ${1, 2, ..., n}$
    * $m =$ number of the teams numbered ${1, 2, ..., m}$
    * $T_i=$ team $i$
    * $f =$ total number of the friend preferences expressed by all individuals
    * $f_i =$ number of friend preferences expressed by student $i$
    * $fs =$ total number of friend preferences across all individuals that are satisfied
    * $fs_i =$ number of friend preferences that are satisfied for student $i$
    * $e =$ total number of the enemy preferences expressed by all individuals
    * $e_i =$ number of the enemy preferences expressed by student $i$
    * $es =$ total number of enemy preferences across all individuals that are satisfied
        * an enemy preference is satisfied if A indicates B to be an enemy and B is not in A's team
    * $es_i =$ number of enemy preferences that are satisfied for student $i$
* Metrics
    * Percentage of satisfactions, S
        * Friends $${fs \over f} * 100$$
        * Enemies $${es \over e} * 100$$
    * Average satisfactions, $\bar{S}$
        * Friends $${{\sum\limits_{i=1}^n {fs_i \over f_i} }\over n}$$
        * Enemies $${{\sum\limits_{i=1}^n {es_i \over e_i} }\over n}$$
    * Number of strictly happy people, SHP: A person is considered strictly happy if all their friends are in their team.
        * Friends $${|\{i: f_i = fs_i\}|}$$
        * Enemies $${|\{i: e_i = es_i\}|}$$
    * Number of strictly happy teams, SHT: A team is considered strictly happy if all the members of the team are all strictly happy.
        * Fiends $${|\{i: \forall j \in T_i : fs_j=f_j\}|}$$
        * Enemies $${|\{i: \forall j \in T_i : es_j=e_j\}|}$$
    * Number of happy people, SP: A person is happy if they have no friend preferences or at least one friend preference is satisfied.
        * Friends $${|\{i: f_i = 0 \lor fs_i > 0\}|}$$
        * Enemies $${|\{i: e_i = 0 \lor es_i > 0\}|}$$
    * Number of happy teams (HT) that have ...
        * At least 1 happy person, HT-1P
            * Friends $${|\{i: \exists j \in T_i : (f_j = 0 \lor fs_j > 0) \}|}$$
            * Enemies $${|\{i: \exists j \in T_i : (e_j = 0 \lor es_j > 0) \}|}$$
        * At least 1 strictly happy person, HT-1SHP
            * Friends $${|\{i: \exists j \in T_i : (fs_j=f_j) \}|}$$
            * Enemies $${|\{i: \exists j \in T_i : (es_j=e_j) \}|}$$
        * Every person is happy, HT-All
            * Friends $${|\{i: \forall j \in T_i : (f_j = 0 \lor fs_j > 0) \}|}$$
            * Enemies $${|\{i: \forall j \in T_i : (e_j = 0 \lor es_j > 0) \}|}$$
        * Every person is strictly happy, HT-?
            * Friends $${|\{i: \forall j \in T_i : (fs_j=f_j) \}|}$$
            * Enemies $${|\{i: \forall j \in T_i : (es_j=e_j) \}|}$$

### Priority Satisfaction
* Symbols
    * $P_i =$ the $i^{th}$ priority from ${1, 2, ..., k}$
    * $S(P_i, T_j)=1$ if the team $T_j$ has satisfied priority $P_i$, else $S(P_i, T_j)=0$
    * $W_i=$ the weight of the priority $P_i$ (all priorities must have weights associataed)
* The order of the priorities are defined by weights that are exponentially ordered:
    * Weights are defined as: $$W_i={2^{k-i}\over {2^k-1}}$$
    * Satisfaction Score, PSS-EW $$\sum\limits_{i=1}^k \sum\limits_{j=1}^m W_i * S(P_i, T_j)$$
* The order of the priorities are defined by weights that are linearly ordered:
    * Weights $$W_i = k+1-i$$
    * Satisfaction Score (same as above) PSS-LW
* Number of fully satisfied priorities (fully means all teams satisfy that priority)
    * FSS $$\max(x: \forall i\lt x : \forall j\lt m: S(P_i, T_j)=1)$$
