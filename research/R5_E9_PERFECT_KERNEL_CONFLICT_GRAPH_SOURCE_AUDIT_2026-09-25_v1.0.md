# R5 E9 — Perfect-Kernel Conflict-Graph / Perfect-Graph Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__NO_SOLVER_PROMOTION`

Parent source audit:
`PA-0001-PERFECT-KERNEL`

Current residual:
`R5_E9_NONABELIAN_PHASE_INCONSISTENT_PERFECT_KERNEL_GATE_V1`

## G0 — Exact object being audited

For the cubic source, normalize the incidence matrix as

```
A = I + P + Q,
```

with every row and every column of `A` of weight three.  A Boolean witness is

```
Ax = 1.
```

Equivalently it is a perfect kernel / three-translate tiling under PA-0001.

Define the conflict graph `C(A)`:
- one vertex for every Boolean variable / column of A;
- two vertices are adjacent iff the corresponding columns meet in some row
  (equivalently, the two variables occur in a common exact-one clause).

The audit question is whether known conflict-graph / perfect-graph machinery
already closes this cubic residual, or supplies a legitimate polynomial island
and a sharper obstruction language.

## G1 — Internal anti-duplication

Repository-first replay found several adjacent but nonidentical predecessors:

- `R5_E9_1IN3_DUAL_HYPERGRAPH_MATCHING_THRESHOLD`:
  exact cover / perfect hypermatching, with rank <=2 collapsing to ordinary matching.
- `R5_E9_BALANCED_BICOLORING_AND_ODD_HOLE_INTERACTION_FRONTIER` and
  `R5_E9_SIGNED_BALANCED_QUOTIENT_AND_HOLE_INTERACTION_TORSION`:
  balanced / signed-balanced polynomial islands for transformed NAE/syndrome fibers.
- `R5_E9_KETTANI_TREEWIDTH_COUNTERFAMILY_AUDIT`:
  the same associated/conflict graph viewpoint appears, but the claimed universal
  bounded-treewidth route is explicitly falsified by the triangular-torus family.
- `R5_E9_INSTANCE_SPECIFIC_TRACTABLE_ARCHIPELAGO_COMPOSITION_FRONTIER`:
  warns that isolated tractable graph/CSP islands are not a universal algorithm
  without an exact interaction theorem.

No artifact was found that source-binds the direct cubic conflict graph to the
general perfect-graph recognition + maximum-stable-set machinery.

Therefore this audit is a cross-route reconciliation, not a fresh carrier hunt.

## G2 — Exact cubic bridge

Let the cubic instance have n variables and n clauses.  (Both sides have total
incidence 3n.)

For an independent set X of `C(A)`, the supports of the selected columns of A
are pairwise disjoint.  Every selected column has support size three.  Hence

```
|X| <= n/3.
```

If `Ax=1`, the true-variable set is independent and covers every row exactly
once, hence has size n/3.

Conversely, if `C(A)` has an independent set X of size n/3, the selected
columns have 3|X|=n pairwise-disjoint row incidences and therefore cover every
one of the n rows exactly once.

Thus

```
Ax=1 has a Boolean solution
iff
alpha(C(A)) = n/3.
```

The witness maps are literal: the maximum independent set is the set of true
variables.

This bridge is elementary.  Clausal/associated-graph language for positive
one-in-three SAT is established in Denman--Foster (2009), and the same
alpha=n/3 observation also appears in later cubic-monotone associated-graph
work.  JANUS does not claim novelty for the representation itself.

## G3 — Source-bound perfect-graph machinery

### Polynomial recognition

Chudnovsky--Cornuéjols--Liu--Seymour--Vušković,
*Recognizing Berge Graphs*, Combinatorica 25(2) (2005), give a polynomial
algorithm (O(n^9) in the paper) to recognize Berge graphs.

Chudnovsky--Robertson--Seymour--Thomas,
*The Strong Perfect Graph Theorem*, Annals of Mathematics 164 (2006), prove

```
perfect
iff
Berge
iff
no induced odd hole and no induced odd antihole.
```

Therefore perfectness of the conflict graph is polynomially recognizable, and
failure has the canonical odd-hole / odd-antihole obstruction language.

### Polynomial maximum stable set

Grötschel--Lovász--Schrijver,
*Polynomial Algorithms for Perfect Graphs* (1984), give polynomial algorithms
for weighted stable set, clique, coloring and clique cover on perfect graphs.

Consequently:

```
C(A) perfect
->
compute alpha(C(A)) in polynomial time
->
decide Ax=1 exactly by alpha(C(A)) = n/3
->
reconstruct the Boolean witness from the stable set.
```

This is a genuine exact P-island.

## G4 — Relation to balanced-matrix work

Balanced 0/1 matrices are a classical polynomial set-partitioning island:
Berge / Fulkerson--Hoffman--Oppenheim integrality gives an integral
set-partitioning polytope whenever the balanced relaxation is nonempty.
For the present 3-regular square A, x=(1/3)1 is always fractionally feasible,
so balanced A is automatically YES.

JANUS already contains balanced and signed-balanced interaction artifacts in
other E9 coordinates.  This audit therefore treats balancedness as
SOURCE-BOUND / INTERNAL-REUSE, not as a new theorem.

No claim is made here that the direct balanced-matrix island and the
perfect-conflict-graph island coincide exactly.

## G5 — What public sources do NOT give

The general cubic class is not made easy by the conflict graph representation.
Positive one-in-three SAT with occurrence bound >=3 is NP-complete
(Denman--Foster 2009), and exact cover / perfect matching in 3-uniform
3-regular hypergraphs is the classical RXC3 hard layer.

Perfect-graph algorithms therefore remove a polynomially recognizable island;
they do not solve arbitrary imperfect conflict graphs.

No located source supplies an exact contraction of every odd-hole/odd-antihole
cubic conflict obstruction that preserves the n/3 stable-set target and
reconstructs an exact-one witness in polynomial total state.

## G6 — Scoped authorization

The surviving JANUS-specific opportunity is not

```
"maximum independent set is easy"
```

but:

```
exploit the extra cubic exact-cover triangle geometry
inside an imperfect conflict graph.
```

New mathematics is authorized only for:

```
R5_E9_PERFECT_CONFLICT_GRAPH_OBSTRUCTION_GATE_V1
```

inside the unchanged PA-0001 semantic route.

The first legitimate theorem target is to combine:

1. the exact `alpha=n/3` cubic bridge;
2. polynomial perfect-graph recognition / solving;
3. the source obstruction `odd hole or odd antihole`;
4. JANUS-specific degree and clause-triangle constraints;

without turning general maximum independent set into an assumed oracle.

## Audit verdict

```
DIRECT CUBIC CONFLICT-GRAPH NORMAL FORM
=
SOURCE-BOUND / ELEMENTARY RECONCILIATION

PERFECT CONFLICT GRAPH
=
POLYNOMIAL EXACT ISLAND

BALANCED DIRECT INCIDENCE
=
SOURCE-BOUND POLYNOMIAL ISLAND / INTERNAL REUSE

GENERAL IMPERFECT CONFLICT GRAPH
=
NOT CLOSED

NEXT SCOPED GATE
=
R5_E9_PERFECT_CONFLICT_GRAPH_OBSTRUCTION_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
