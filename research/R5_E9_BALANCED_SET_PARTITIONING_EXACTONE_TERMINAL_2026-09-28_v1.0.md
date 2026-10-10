# R5 E9 — Balanced set-partitioning Exact-One terminal

Date: 2026-09-28

Status: `JANUS_SOURCE_BOUND_POLYNOMIAL_TERMINAL__BALANCED_CUBIC_EXACTONE`

Scientific ceiling:

```text
THIS IS A DETERMINISTIC POLYNOMIAL TERMINAL FOR THE BALANCED SUBCLASS.
IT DOES NOT SOLVE THE UNBALANCED RESIDUAL.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A` be the 0/1 clause-by-variable incidence matrix of a cubic Positive Exact-One instance. Thus every row has exactly three ones; in the linear-cubic source every column also has exactly three ones and distinct rows intersect in at most one column.

The decision/search target is

```text
A x = 1,
x in {0,1}^n.
```

Consider the nonnegative set-partitioning polytope

```text
P(A) = {x in R^n : A x = 1, x >= 0}.
```

Because every row of `A` has sum three,

```text
x* = (1/3) 1
```

belongs to `P(A)`. Hence `P(A)` is nonempty for every source instance.

Also, for every `x in P(A)`, each coordinate satisfies `x_j <= 1` because column `j` occurs in at least one row whose nonnegative coordinates sum to one. Thus `P(A)` is bounded on the source carrier.

## 2. Balanced-matrix donor theorem

A 0/1 matrix is balanced iff it contains no square submatrix of odd order having exactly two ones in every row and every column.

Classical results of Berge / Fulkerson--Hoffman--Oppenheim imply:

> If `A` is balanced, then the set-partitioning polytope
> `P(A)={x>=0:Ax=1}` is integral.

Polynomial-time recognition of balanced 0/1 matrices is known (Conforti--Cornuejols--Kapoor--Vuskovic and predecessors).

These are external source theorems; JANUS uses them as donors rather than claiming novelty.

## 3. Main terminal theorem

### Theorem BST-1

If the cubic Exact-One incidence matrix `A` is balanced, then the instance is satisfiable and a Boolean witness is deterministically constructible in polynomial time.

### Proof

`x*=(1/3)1` proves `P(A)` is nonempty. Balancedness makes `P(A)` integral, so every vertex of `P(A)` is integral.

Because `P(A)` is bounded and nonempty, it has a vertex. Let `z` be any integral vertex. Since `z>=0` and every source row satisfies

```text
sum_{j in row} z_j = 1,
```

each coordinate occurring in that row is an integer in `{0,1}`. Every source variable occurs in at least one row, hence

```text
z in {0,1}^n
```

and `Az=1`. Thus `z` is an Exact-One witness. QED.

## 4. Deterministic polynomial witness construction

The theorem is constructive without enumerating vertices.

1. Recognize balancedness in polynomial time.
2. On a balanced input, use polynomial-time rational linear programming on `P(A)`.
3. To force an explicit vertex deterministically, lexicographically optimize coordinates: minimize `x_1`; fix its optimum, then minimize `x_2`, and so on. Each step is one polynomial-time LP over a face of the same integral polytope.
4. After at most `n` LP calls, the remaining face is a singleton vertex `z`.
5. Output `z`; by BST-1 it is Boolean and satisfies every source row exactly once.

All coefficients have constant input bit-size and each added fixing equation uses a rational optimum of polynomial encoding length. Since the polytope is integral, the fixed coordinate values are integers.

A standard LP implementation returning a basic optimal solution can replace the lexicographic construction; the sequential formulation makes the proof independent of such an implementation convention.

## 5. Constructive unbalanced certificate

Balancedness recognition is not merely a YES island. If `A` is unbalanced, an explicit forbidden submatrix can be obtained in polynomial time using the recognition algorithm as an oracle:

- repeatedly test deletion of a row; permanently delete it whenever unbalancedness remains;
- then do the same for columns;
- stop when no row or column can be deleted while preserving unbalancedness.

There are only `O(n)` successful/dead deletion tests per side. The resulting inclusion-minimal unbalanced submatrix must itself be a square odd-order matrix with exactly two ones in each row and each column; otherwise its proper forbidden submatrix would contradict minimality.

Thus the router returns either:

```text
BALANCED -> polynomial Exact-One witness,
UNBALANCED -> explicit odd cycle submatrix obstruction.
```

## 6. Hypergraph / Levi interpretation

The forbidden odd square submatrix is exactly a strong odd cycle in the hypergraph sense.

Equivalently, in the bipartite Levi representation it is a cycle using an odd number of clause vertices and an odd number of variable vertices, hence total length

```text
4k+2.
```

The selected row/column submatrix has degree two on both shores, so each connected component is a chordless cycle in the selected bipartite subgraph. Since the total square order is odd, at least one component has odd shore size and therefore length `4k+2`.

Conversely any such strong odd cycle supplies the forbidden odd square submatrix.

Thus on the source carrier:

```text
A balanced
iff
no strong odd cycle
iff
no forbidden 4k+2 Levi cycle submatrix.
```

This is the exact set-partitioning balancedness notion; it must not be confused with the older mixed D1/D2/D3 NAE/bicoloring balanced-fiber theorem.

## 7. Interaction with current JANUS route

The new polynomial router is:

```text
linear-cubic Exact-One instance A
    |
    +-- A balanced
    |      -> SAT + witness in polynomial time
    |
    +-- A unbalanced
           -> construct explicit strong odd-cycle obstruction
           -> pass only this branch to the residual global-contraction machinery
```

Therefore every genuinely hard residual can now be assumed to contain a source-certified strong odd cycle.

This is stronger than using odd holes only as diagnostic geometry: balanced instances leave the hard core completely because SAT is automatic.

## 8. Anti-loop interaction with old balanced-bicoloring artifact

The predecessor `R5_E9_BALANCED_BICOLORING_AND_ODD_HOLE_INTERACTION_FRONTIER_2026-09-23_v1.0.md` concerns a different mixed NAE fiber with D1 pair rows and D2/D3 ternary rows.

The present theorem acts directly on the original Exact-One set-partitioning system `Ax=1`. Its positive conclusion follows from integrality of `P(A)`, not from NAE bicoloring.

Do not merge the two statements or transfer the old denominator-13 counterexample to this set-partitioning theorem.

## 9. New residual gate

Freeze:

```text
R5_E9_UNBALANCED_STRONG_ODD_CYCLE_GLOBAL_CONTRACTION_GATE_V1
```

Input:
- connected linear cubic Positive Exact-One;
- all admitted <=3-edge separator contractions already available;
- balanced recognition returns NO;
- an explicit strong odd-cycle / odd square submatrix certificate is available.

Required next progress:
- an exact polynomial contraction using the certified strong odd cycle and its third-incidence boundary, or
- a source-specific polynomial syndrome representation for the same unbalanced core, or
- another proved polynomial terminal.

Forbidden:
- branch over all assignments on the cycle;
- treat unbalancedness alone as UNSAT;
- assume independent parity defects for overlapping odd cycles;
- reuse mixed-NAE bicoloring arguments as if they solved set partitioning.

## 10. Ceiling

```text
BALANCED RECOGNITION = POLYNOMIAL / SOURCE DONOR
BALANCED CUBIC EXACT-ONE = ALWAYS SAT
BALANCED WITNESS CONSTRUCTION = DETERMINISTIC POLYNOMIAL
UNBALANCED CERTIFICATE = POLYNOMIALLY EXTRACTABLE
HARD RESIDUAL CONTAINS STRONG ODD CYCLE = PROVED
UNBALANCED RESIDUAL SOLVER = OPEN
UNIVERSAL POLYNOMIAL DECIDER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
