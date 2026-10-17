# R5 E9 — Boben `(v_3)` Reduction vs Exact-One Semantic Audit

Date: 2026-09-27

Status:
`STRUCTURAL_DONOR_ACCEPTED__NAIVE_SEMANTIC_IMPORT_FALSIFIED`

Scientific ceiling:

```text
Boben reduction theorem for connected (v_3) graphs = ACCEPTED AS STRUCTURAL GRAPH THEORY.
Single-step Exact-One/SAT preservation                 = FALSE IN BOTH DIRECTIONS.
Universal polynomial Exact-One solver                  = NOT PROVED.
E8_D1                                                   = EMPTY.
P_VS_NP                                                 = OPEN.
```

External source:
- Marko Boben, **Reductions of (v_3) configurations**, arXiv:math/0505136.
- Boben proves that every connected bipartite cubic graph of girth at least 6 can be reduced, through connected graphs of the same class, to the Heawood graph (Fano configuration) or the Pappus graph.

Executable replay:
- `experiments/r5_e9_boben_reduction_semantic_audit.py`

## 1. Why Boben is exactly relevant structurally

The JANUS cubic-linear carrier has a Levi graph that is

```text
bipartite
+ cubic
+ girth >= 6.
```

This is exactly Boben's `(v_3)` graph class.

A B-reduction removes one row-side vertex and one column-side vertex and reconnects their remaining neighbors by a perfect matching so that the graph remains bipartite, cubic and girth at least 6.

Boben's theorem is therefore a genuine structural reduction theorem for the entire frozen cubic-linear carrier class.

However, a structural graph reduction is not automatically an Exact-One semantic reduction.

## 2. Exact local semantic obstruction

Use the General-Factor form

```text
row/line vertex    : K={1}
column/point vertex: K={0,3}.
```

Equivalently, at a point/column the three incident factor bits are all equal to one Boolean variable, while at a row/line exactly one of its three incident bits equals one.

Consider the adjacent (A-reduction) case. Let the removed point and line share internal bit `s`. Let `a,b` be the other two point-side incidence bits and `c,d` the other two line-side incidence bits. Contracting the removed pair gives the exact four-boundary relation

```text
R(a,b,c,d)
= exists s: EQ3(a,b,s) AND EXACT1_3(c,d,s).
```

Its satisfying tuples are exactly

```text
(0,0,1,0)
(0,0,0,1)
(1,1,0,0).
```

This relation is not the product of two ordinary equality-wire relations along either of Boben's two possible reconnection pairings. In particular, it has three tuples and both paired coordinates vary, so it cannot be represented as a Cartesian product of two independent binary edge relations.

Thus replacing the removed vertices by ordinary Levi edges discards semantic correlation.

For the nonadjacent B-reduction the removed point and removed line contribute an even clearer six-boundary product

```text
EQ3(a1,a2,a3) AND EXACT1_3(b1,b2,b3),
```

which likewise is not encoded by three ordinary equality incidences after arbitrary pairing.

Therefore Boben's graph reduction requires an additional exact semantic state/annotation theorem before it can enter a SAT solver.

## 3. Explicit SAT -> UNSAT legal reduction

Take the normalized `9_3` carrier

```text
p = [4,6,8,1,7,2,3,0,5]
q = [2,0,6,4,5,3,7,8,1]
A = I+P+Q.
```

Row supports are

```text
0: {0,2,4}
1: {0,1,6}
2: {2,6,8}
3: {1,3,4}
4: {4,5,7}
5: {2,3,5}
6: {3,6,7}
7: {0,7,8}
8: {1,5,8}
```

The carrier is connected, square, cubic and linear.

Exact exhaustive Boolean replay gives one Exact-One witness:

```text
selected columns = {1,2,7}.
```

Now perform a legal adjacent Boben reduction by row `0` and column `2`.

The remaining neighbors are

```text
row 0, excluding column 2: columns [0,4]
column 2, excluding row 0: rows [2,5].
```

Reconnect

```text
row 2 -> old column 4
row 5 -> old column 0.
```

After deleting row 0 / column 2 and relabeling, the reduced `8_3` row supports are

```text
{0,1,5}
{3,5,7}
{1,2,3}
{3,4,6}
{0,2,4}
{2,5,6}
{0,6,7}
{1,4,7}
```

The reduced graph is again connected, square, cubic and linear, hence a legal `(v_3)` graph reduction.

Exact Boolean enumeration gives

```text
original witness count = 1
reduced witness count  = 0.
```

Therefore

```text
Boben reduction can map SAT -> UNSAT.
```

## 4. Explicit UNSAT -> SAT legal reduction

Take the normalized `10_3` carrier

```text
p = [5,0,4,2,9,1,7,3,6,8]
q = [3,2,7,6,0,4,9,8,1,5]
A = I+P+Q.
```

Row supports are

```text
{0,3,5}
{0,1,2}
{2,4,7}
{2,3,6}
{0,4,9}
{1,4,5}
{6,7,9}
{3,7,8}
{1,6,8}
{5,8,9}
```

It is connected, square, cubic and linear. Exhaustive Boolean replay gives no Exact-One witness.

Perform the legal adjacent Boben reduction by row `2` and column `2`. The remaining neighbor pairing is

```text
old row 1 -> old column 7
old row 3 -> old column 4.
```

After deletion/relabeling, the reduced `9_3` supports are

```text
{0,2,4}
{0,1,6}
{2,3,5}
{0,3,8}
{1,3,4}
{5,6,8}
{2,6,7}
{1,5,7}
{4,7,8}
```

Again the reduced graph is connected, square, cubic and linear.

Exact enumeration gives one reduced witness:

```text
selected reduced columns = {1,2,8}.
```

Hence

```text
Boben reduction can map UNSAT -> SAT.
```

## 5. Consequence for the universal search

The structural theorem is valuable but the following shortcut is now forbidden:

```text
reduce every cubic-linear Levi graph to Fano/Pappus
+ solve only the terminal graph
=> solve the original Exact-One instance.
```

That implication is false without additional semantic state.

What remains potentially powerful is a **semantic lift** of Boben reduction. A valid lift must carry enough information to represent the contracted local tensor/correlation and prove that state complexity stays polynomial over an arbitrary reduction sequence.

The critical new gate is therefore

```text
R5_E9_BOBEN_SEMANTIC_LIFT_STATE_GROWTH_GATE_V1.
```

Acceptable outcomes:

```text
A. find a finite/ polynomial-size closed signature algebra under all Boben reductions and prove exact witness reconstruction;
B. prove a polynomial bound on signature growth for the JANUS constraint pair EQ3 / EXACT1_3;
C. produce a family on which any proposed signature basis grows superpolynomially / leaves the claimed closure;
D. identify a known Holant/tensor reduction theorem that exactly supplies the missing bounded semantic state.
```

No claim of polynomiality is admitted merely from the existence of the graph reduction sequence.

## 6. Frozen status

```text
BOBEN STRUCTURAL REDUCTION THEOREM          = APPLICABLE TO THE CARRIER GRAPH CLASS
NAIVE SINGLE-INSTANCE SAT PRESERVATION      = FALSIFIED
SAT -> UNSAT LEGAL STEP                     = VERIFIED
UNSAT -> SAT LEGAL STEP                     = VERIFIED
LOCAL ORDINARY-EDGE FACTORIZATION           = FALSIFIED
BOUNDED SEMANTIC-LIFT STATE ALGEBRA          = OPEN
UNIVERSAL POLYNOMIAL EXACT-ONE SOLVER        = OPEN
E8_D1                                        = EMPTY
P_VS_NP                                      = OPEN
```
