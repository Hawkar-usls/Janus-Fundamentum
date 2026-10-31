# R5 E9 — Prescribed C10 Polynomial-Degree 2-Group Cover Theorem Candidate

Date: 2026-09-27

Status:
`THEOREM_CANDIDATE__NOT_LEDGER_PROMOTED`

Depends on:
- `R5_E9_HIGH_NULLITY_PHASE_FAIL_EXPLICIT_FAMILY_THEOREM_2026-09-26_v1.0`
- `R5_E9_POLYSIZE_2GROUP_FIXED_GIRTH_COVER_THEOREM_2026-09-26_v1.0`
- `R5_E9_PHASE_COVER_PRESERVATION_2026-09-26_v1.0`
- `R5_E9_HIGH_GIRTH_ODD_HOLE_SPARSE_ATTACHMENT_NEGATIVE_CONTROL_2026-09-26_v1.0`
- `R5_E9_CONFLICT_ODD_HOLE_COVERAGE_SELECTOR_CONSERVATION_2026-09-25_v1.0`

Finite regression:
`experiments/r5_e9_prescribed_c10_cover_regression.py`

Governance boundary:
`DO_NOT_ASSIGN_NM_NUMBER_UNTIL_PA0029_NM0033_BOOTSTRAP_AND_GOVERNANCE_ARE_RESOLVED`

Global boundary:
`P_VS_NP = OPEN`

## 1. Candidate theorem

Let H be a finite connected graph of maximum degree at most a fixed constant
Delta. Suppose H contains a specified simple 10-cycle C.

Candidate claim: there is a deterministic polynomial-time construction of a
connected finite cover

```
H_tilde -> H
```

such that

```
girth(H_tilde) = 10,
H_tilde contains a lift of the specified C,
cover degree is a power of 2 and is n^O(1).
```

The hidden constant depends only on the fixed girth target 10 and fixed degree
bound Delta.

If H is a cubic bipartite incidence graph, those local properties are
preserved by the cover.

This file is deliberately a theorem candidate, not a promoted JANUS theorem.
The finite checker below tests explicit family geometry and constant
accounting; it is not a substitute for proof review.

## 2. Explicit prescribed C10 in the A'_m family

For every m>=3, use the family

```
A'_m = I + P + Q'
Omega_m = Z_3 x Z_m.
```

Rows are R(r,a), columns are V(r,a), and

```
P(r,a) = (r+1 mod 3,a).
```

Before the swap,

```
Q(0,a) = (2,a+1),
Q(1,a) = (0,a),
Q(2,a) = (1,a).
```

Q' swaps the Q-images of (0,0) and (2,2).

For every m>=3 the following alternating incidence cycle is simple:

```
V(1,2)
R(1,2)
V(2,2)
R(0,1)
V(0,1)
R(2,1)
V(2,1)
R(2,2)
V(0,2)
R(0,2)
V(1,2).
```

The finite regression checks this directly for every m=3,...,128.

The five relevant row supports are

```
R(1,2): V(1,2), V(2,2), V(0,2)
R(0,1): V(0,1), V(1,1), V(2,2)
R(2,1): V(2,1), V(0,1), V(1,1)
R(2,2): V(2,2), V(0,2), V(2,1)
R(0,2): V(0,2), V(1,2), V(2,3 mod m).
```

Thus the previous `SPECIFIED_10_CYCLE` existence gap is explicit at the base
family level.

## 3. Force the selected cycle to close in every voltage coordinate

Orient the ten distinct cycle edges as

```
e1,e2,...,e10
```

around C.

For a voltage group K, choose the voltages on e1,...,e9 freely and impose

```
alpha(e10)
=
(alpha(e1) alpha(e2) ... alpha(e9))^-1.
```

Therefore the net voltage around C is identity.

Consequently every lift of a starting vertex of C closes after ten lifted
edges. If all cycles of length <10 are excluded, this closed lift is a simple
10-cycle and forces

```
girth(H_tilde)=10.
```

The problem is therefore reduced to showing that this dependent voltage
relation does not make a shorter base nonbacktracking word identically trivial.

## 4. 10-systole lemma for the dependent generator

Let

```
F = F(e1,...,e9, other independent edge variables)
A = e1 e2 ... e9
z = A^-1.
```

View the Cayley graph of F with respect to its free basis as a tree T. Add the
generator z. A z-edge is a shortcut whose unique T-geodesic has length 9 and
is a left translate of the path

```
1, e1, e1e2, ..., e1e2...e9.
```

### Lemma

No nontrivial reduced word in the enlarged alphabet

```
{free basis generators and inverses, z, z^-1}
```

of length <10 represents the identity in F.

### Proof candidate

The nine labels e1,...,e9 on the displayed T-path are pairwise distinct.

Two distinct left translates of this path cannot share an undirected T-edge.
Indeed an overlapping edge fixes its free-basis label. Since every label
occurs at one position only, it fixes the position in both translates; equality
of the corresponding initial vertex then fixes the translating element.
Opposite orientation cannot give a second positively labelled traversal of the
same free-tree edge.

Take a shortest reduced identity word in the enlarged alphabet and view it as
a shortest closed walk in the enlarged Cayley graph. It may be taken to be a
simple cycle, so it never uses one shortcut edge twice.

Suppose it uses k>=1 shortcut edges. Replace every shortcut by its unique
length-9 T-geodesic. The associated geodesics are distinct left translates
and hence are pairwise edge-disjoint.

The resulting walk is closed in the tree T. Every one of the 9k tree-edge
traversals introduced by the shortcut replacements must be balanced by a
traversal in the opposite direction. Because the shortcut geodesics are
edge-disjoint, those balancing traversals must contribute at least 9k
ordinary tree-edge steps from the original cycle.

Hence the original enlarged cycle has length at least

```
k + 9k = 10k >= 10.
```

If k=0, the alleged nontrivial reduced closed walk lies entirely in a tree,
which is impossible.

Therefore no reduced identity word has length <10. The displayed relator

```
z e1 e2 ... e9 = 1
```

has length exactly 10, so the enlarged generating set has systole exactly 10.

This is the key new proof obligation relative to the existing fixed-girth
cover theorem.

## 5. Every dangerous short walk remains a nontrivial bounded word

A base nonbacktracking closed walk W of length <10 reads a reduced word in the
oriented edge variables.

Substitute the dependent cycle-edge variable e10 by

```
(e1...e9)^-1.
```

Section 4 says the result is still nontrivial.

The original word has length at most 9. Each dependent letter expands to
length 9, hence a safe uniform bound is

```
substituted word length <= 9*9 = 81.
```

This bound is independent of n.

## 6. One fixed finite 2-group separates every substituted short pattern

Up to renaming its distinct variables, there are only finitely many nontrivial
free words of length at most 81.

For each such word w, residual finiteness of free groups by finite 2-groups
provides a finite 2-group K_w and an evaluation on which w is nonidentity.

Take the finite direct product

```
K = product_w K_w.
```

K is one fixed finite 2-group, independent of H and n, with the property that
every relevant abstract word pattern has at least one assignment in K on
which it is nonidentity.

If B=|K| and a word contains at most 81 distinct variables, a uniform random
assignment to those variables therefore satisfies the conservative bound

```
Pr[w != 1] >= B^-81 =: epsilon > 0,
Pr[w = 1] <= q := 1-epsilon < 1.
```

The constant may be enormous; only its independence from n is used.

External source boundary: the group-theoretic donor fact is the classical
theorem that free groups are residually finite p-groups for every prime p.
The existing fixed-girth theorem already source-binds this input. A modern
open-access statement is I. Emmanouil, "Residually nilpotent groups of
homological dimension 1", Bulletin of the London Mathematical Society (2025),
DOI 10.1112/blms.70140.

## 7. O(log n) product coordinates kill every short closed walk

For fixed Delta and girth target 10, the number M of rooted nonbacktracking
closed base walks of length <10 is O(n). The existing NM-0030 donor gives,
for Delta=3,

```
M <= 1533 n.
```

Choose t independent K-valued voltage coordinates, always defining the
dependent e10 coordinate from e1,...,e9 as in Section 3.

For any one dangerous W,

```
Pr[W survives all t coordinates with identity voltage] <= q^t.
```

By the union bound,

```
Pr[some dangerous W survives] <= M q^t.
```

Taking

```
t > log(M)/(-log q)
```

makes this probability <1. Therefore an assignment exists with no lifted
cycle of length <10.

Since t=O(log n),

```
|K|^t = n^O(1).
```

Because K is a finite 2-group, this regular cover has 2-power degree.

## 8. Deterministic construction by conditional expectation

The previous existence proof can be derandomized without an oracle.

Expose the independent edge voltages one variable at a time in each K
coordinate. The e10 value is never independently exposed; it is recomputed
from the nine prescribed C-edge values.

For a partially exposed coordinate and one dangerous word, at most 81
distinct independent variables are relevant. K and 81 are fixed constants.
Its exact conditional probability of evaluating to identity can therefore be
computed by exhaustive enumeration over at most

```
|K|^81
```

constant-many completions.

At every exposure step, average conditional expectation over all possible
K-values equals the expectation before exposure. Select a value that does
not increase the expected number of surviving bad walks.

After a complete coordinate, repeat for O(log n) coordinates. Equivalently,
one may expose all variables of all coordinates in one conditional-expectation
process.

The number of bad walks and exposed variables is polynomial in n; all
per-event exhaustive factors depend only on fixed K and 81. Hence the
construction is deterministic polynomial time in the standard asymptotic
sense.

No SAT oracle or existential "choose the good assignment" step is used.

## 9. Connected component extraction keeps the prescribed C10

The full regular voltage cover can be disconnected.

Take the connected component containing any chosen lift of a vertex of C.
Because H is connected, the component projects onto every base vertex and is
itself a connected cover of H.

Its fibre degree is the order of a subgroup of the finite 2-group K^t, hence
is again a power of 2 and no larger than |K|^t.

The net voltage of C is identity in every coordinate. Therefore the lift of
C starting at the chosen lifted vertex closes inside this same component.
No cycle shorter than ten exists, so this component still contains the
prescribed simple C10 and has girth exactly 10.

## 10. JANUS consequence if the proof candidate survives review

Apply the construction to the explicit A'_m family.

The 2-power cover degree is coprime to 3, so the existing coprime-cover theorem
is intended to preserve the Z3 phase-FAIL property. Covering also preserves
the cubic incidence local structure and lifts the exact-one witness machinery
already source-bound in the branch.

Most importantly, the specified base incidence C10 now survives into a
girth-10 cover.

The existing high-girth odd-hole control then converts that incidence C10
into an induced conflict C5. The selector-conservation control supplies:
- unique selector ports for the C5 edges,
- all five C5 vertices are claw centers,
- no outside port dominates two or more C5 vertices.

Thus this candidate closes the previously explicit

```
SPECIFIED_10_CYCLE / SPARSE_ODD_HOLE_GEOMETRY
```

gap if and only if the proof above passes theorem/governance review.

It does not prove P=NP.

## 11. Epistemic firewall

```
FINITE_REGRESSION
!=
THEOREM_PROOF

THEOREM_CANDIDATE
!=
JANUS_LEDGER_PROMOTION

HARD_FAMILY_CONSTRUCTION
!=
UNIVERSAL_POLYNOMIAL_SAT_ALGORITHM

P_VS_NP
=
OPEN
```

The next algorithmic frontier is the universal-selector/progress problem. Any
claim that a satisfiable instance always has a good next branch is useless
unless the branch is computable in polynomial time without querying SAT.
