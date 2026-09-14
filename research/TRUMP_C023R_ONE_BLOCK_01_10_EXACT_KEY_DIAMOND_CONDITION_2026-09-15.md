# C023R — One-block 01/10 exact historical-key diamond condition

Authority: `EXACT_TRANSITION_LEMMA__NO_SCIENTIFIC_PROMOTION`  
Method: `STRICT_CODE_BOUND_COMBINATORICS__NO_HEURISTICS`

## Frozen transition operator

For any nonterminal historical cache key `K`, define:

1. `R(K)` = frozen deterministic `resolution_trace(K, width_limit, attempt_budget, addition_budget)` output;
2. `P(K)` = exhaustive deterministic post-unit propagation of `R(K)`;
3. `v(K)` = frozen `branch_variable(P(K))`;
4. for branch value `b in {0,1}`, let `I_b(K)=simplify_one(P(K),v(K),b)`;
5. if `I_b(K)` is nonconflicting, let `T_b(K)` be the next pre-unit-propagated canonical cache key reached from `I_b(K)`.

`T_b` is a partial deterministic transition because a branch may terminate by direct conflict or unit contradiction before a cache key is formed.

## Theorem B1 — exact two-step diamond criterion

Let `a` and `b` be two coordinates of one MAJ3 edge block. There is an exact two-step historical-key diamond from a common nonterminal key `K` with arms

`a=0 -> b=1`

and

`a=1 -> b=0`

if and only if all of the following hold:

1. `v(K)=a`;
2. `T_0(K)` and `T_1(K)` both exist as nonterminal cache keys;
3. `v(T_0(K))=v(T_1(K))=b`;
4. the second-step transitions both exist; and
5. byte-exact key equality holds:

`T_1(T_0(K)) = T_0(T_1(K))`.

Proof. Conditions 1–4 are exactly the frozen control-flow requirements for the two labeled length-two branch paths to exist. The historical cache identifies states if and only if their canonical pre-local-Resolution keys are byte-identical. Therefore condition 5 is exactly the merge condition. No weaker semantic equality is sufficient. QED.

## Corollary B1.1 — source MAJ3 equality is necessary context, not a cache proof

For the pure source MAJ3 block, assigning two fixed coordinates `01` or `10` yields the same remaining-coordinate function. Hence, after those two assignments, the pure source contribution of that block can agree.

However, historical child inputs contain clauses inherited from the deterministic local Resolution passes performed before and between those assignments. Thus source-gadget equality does not imply condition 5.

## Definition — exact inherited fingerprint difference

For a candidate B1 configuration define

`Delta_K(a,b) = symmetric_difference(T_1(T_0(K)), T_0(T_1(K)))`

when both keys exist.

Then:

- `Delta_K(a,b)=empty` iff the exact two-step key diamond exists;
- any clause in `Delta_K(a,b)` is an explicit surviving historical fingerprint distinguishing the two source-colliding histories.

This is an exact clause-set object, not a heuristic signature.

## Theorem B2 — frozen local Resolution is not generally permutation-equivariant

The historical `resolution_trace` processes pivots in increasing numeric variable order and terminates when either its attempt budget or addition budget is exhausted. Therefore variable renaming does not in general commute with the transition.

A concrete infinite counterfamily can be defined as follows. For `m>32`, use pairwise distinct private variables and the CNF union

- `(1 OR x_i)` for `i=1..m`;
- `(not 1 OR y_j)` for `j=1..m`;
- `(2 OR u_i)` for `i=1..m`;
- `(not 2 OR v_j)` for `j=1..m`,

with all private variables appearing only in the displayed polarity and all four private-variable sets disjoint.

There are `4m` width-two clauses and `8m` literal occurrences. The policy attempt budget is `max(64,32m)` and the addition budget is `max(8,m)=m`.

At pivot 1, the first positive/negative family supplies `m^2` candidate pairs and at least `m` distinct non-tautological width-two resolvents before pivot 2 is reached, so the addition budget is exhausted while processing pivot 1. Thus no pivot-2 resolvents are added.

Now rename only variables 1 and 2, leaving all private variables fixed. The same deterministic algorithm processes the old pivot-2 family first and exhausts the addition budget there. The renamed output therefore contains the `u_i/v_j`-family resolvents rather than the renamed image of the original `x_i/y_j` output.

Hence for this frozen budgeted algorithm

`resolution_trace(pi(F)) != pi(resolution_trace(F))`

for that renaming `pi`.

This proves that gadget coordinate symmetry cannot be imported through the historical local-Resolution pass without a separate context-specific proof.

## Consequence for MAJ3 serial diamonds

Any proof of linearly many 01/10 diamonds on the frozen q=4 Morgenstern family must establish the exact B1 transition equality for a symbolic infinite family of contexts, or establish a stronger invariant implying it. MAJ3 coordinate symmetry by itself is insufficient.

Conversely, a PASS-side fingerprint theorem may use nonempty `Delta_K(a,b)` clauses as exact witnesses that particular semantic collision bits remain encoded in the historical key.

## Gate result

`ONE_BLOCK_01_10_HISTORICAL_KEY_COLLISION_CONDITION = CLOSED_EXACTLY`.

`GENERAL_LINEAR_DIAMOND_PACKING = OPEN`.

`GENERAL_NEAR_INJECTIVE_FINGERPRINT = OPEN`.

`P_VS_NP = OPEN`.
