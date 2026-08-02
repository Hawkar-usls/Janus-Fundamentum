# H118 — exact XOR-cycle local SAT/UNSAT twins

## Status

`FORMALIZING`, reproducibility `R3`.

This artifact proves the explicit construction used to attack H115. It does not
supply the high-treewidth obstruction still needed against H106.

## Construction

Fix a radius `R >= 0` and let

\[
L=8R+12.
\]

Use two disjoint variable cycles of length `L`. Every primal cycle edge carries
one XOR relation encoded by two binary clauses.

Equality:

\[
x_i=x_j
\quad\Longleftrightarrow\quad
(\neg x_i\lor x_j)\land(x_i\lor\neg x_j).
\]

Inequality:

\[
x_i\ne x_j
\quad\Longleftrightarrow\quad
(x_i\lor x_j)\land(\neg x_i\lor\neg x_j).
\]

Define `S_R` by putting two inequality edges at positions `0` and `L/2` in the
first cycle and no inequality edge in the second cycle.

Define `U_R` by putting one inequality edge at position `0` in each cycle.

## Satisfiability

Along a component, choose the first variable freely and propagate its value.
Crossing an equality edge preserves the value; crossing an inequality edge
flips it. The closing constraint is consistent exactly when the number of
inequality edges in that component is even.

`S_R` has component parities `(0,0)` modulo two and is satisfiable.

`U_R` has component parities `(1,1)` and is unsatisfiable.

## Exact local equality

Both formulas have:

- two cycles of equal length;
- exactly two inequality gadgets total;
- identical equality and inequality clause gadgets;
- marked edges separated by more than the visible range of a radius-`R`
  incidence ball.

A rooted radius-`R` signed incidence neighborhood therefore sees at most one
marked edge. For every possible root type and relative marked-edge position,
the two formulas contain the same number of roots of that type. All remaining
roots see the unmarked periodic cycle neighborhood. Hence the complete
multisets of rooted signed neighborhoods agree exactly.

The executable verifier constructs each rooted ball, computes an exact
edge-labelled canonical form by individualization-refinement, and compares the
full multisets:

```bash
python experiments/direct/xor_cycle_local_twins.py --self-test
```

## Treewidth

Each binary clause contains the endpoints of one cycle edge. Duplicate clauses
do not create additional primal edges. Thus the primal graph is exactly two
disjoint cycles and has treewidth at most two.

## Meaning

H118 solves the purely local construction task in a deliberately simple model:
exact local SAT/UNSAT twins exist at every fixed radius.

It simultaneously shows why this fact is insufficient for a locality lower
bound. Global assembly—specifically, whether the two marked edges lie in the
same connected component—remains visible to a global algorithm on a
low-treewidth graph.

## Claim boundary

H118 does not refute unrestricted algorithms or prove a lower bound against
H106. A successful H106 obstruction must additionally prevent a low-treewidth
output from retaining the decisive global assembly information.
