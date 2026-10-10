# R5 E10A — End-to-End Decomposition Solver Composition / Coverage Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__GLOBAL_SOLVER_PROMOTION_HOLD`

Immediate predecessor:
`NM-0016-BOUNDARY-METRIC-CLOSURE`

## G0 — end-to-end object

The top-level cubic-origin object is

```
M([H|f]),
H=I+P+Q over GF(2),
f=1,
```

with the original exact decision target

```
shortest_f = n/3 + 1.
```

The local E10A chain now contains:

```
NM-0012  literal distinguished-torso placement invariant
NM-0013  distinguished two-row exact solver
NM-0014  nondistinguished single-root 2/Delta/Y lifting
NM-0015  multi-interface active-star/support bound
NM-0016  exact nonnegative boundary-table compilation and witness binding
```

This audit asks whether these local theorems, plus source-bound decomposition
terminals, cover **every** live component class arising from the original
cubic parent.

## G1 — internal coverage audit

Covered:

1. exact cubic Exact-One / all-ones-coset / distinguished-`f` reformulation;
2. source-standard 1/2/3-sum decomposition whenever the relevant separation is
   present;
3. source-bound no-`S8) shortest-circuit machinery;
4. certified graphic / even-cycle / even-cut / graft terminals;
5. exact 2/Delta3/Y interface semantics;
6. distinguished two-row torsos satisfying NM-0012;
7. nondistinguished single-root interface lifting;
8. multi-interface star support accumulation;
9. mixed nonnegative child-table compilation;
10. polynomial witness reconstruction, conditional on a local solver.

No current artifact proves the missing class-coverage statement:

```
EVERY REMAINING
3-CONNECTED S8-CONTAINING
CUBIC-LINEAGE LIVE TORSO

IS CONSTRUCTIVELY REPRESENTABLE AS

[ B_G ]
[  S  ]

with rank(S modulo cut(G)) <= 2.
```

The current repository also contains no materialized source decomposition tree
or corpus of actual E10 leaf matrices on which this coverage claim has been
empirically certified.

## G2 — canonical external language

Huynh's thesis gives the exact standard language.

A matroid `N` is an `m`-lift of a graphic matroid if it has a
representation

```
N = M_F([A;B]),
```

where `B` is a signed incidence matrix of a graph and `A` has `m` rows.

Thus the JANUS two-row representation is exactly the binary `m<=2` case.

Define the JANUS coverage parameter

```
q_graph(N)
=
minimum m such that N is a binary m-lift
of a graphic matroid on the same ground set.
```

Equivalently,

```
q_graph(N)
=
min codim_{C*(N)} U
```

over graphic cut spaces `U subseteq C*(N)`.

The notation `q_graph` is JANUS-local; the canonical external class name is
`m-lift of a graphic matroid`.

A solver certificate requires more than existential membership: it must
construct the graph `G`, the graphic incidence block `B_G`, and the at-most
two signature rows.

## G3 — public source exhaustion

### S1 — m-lift language is source-bound

Huynh defines `m`-lifts exactly by the representation `[A;B]` above and
associates the binary case with `GF(2)^m`-labelled graphs.

The class of binary `m`-lifts of graphic matroids is well-quasi-ordered under
minors for each fixed `m`.

This is structural language, not a theorem that every binary matroid or every
cubic-origin torso has bounded `m`.

Classification:
`M_LIFT_GRAPHIC_LANGUAGE=SOURCE_BOUND`.

### S2 — one-row lift algorithms do not close m=2

The Guenin--Stuive flow work uses `lift` in the elementary binary sense:
one row is appended to a graphic representation, giving an even-cycle matroid.

Its polynomial single-commodity-flow machinery therefore does not prove
recognition, representation construction, or shortest-`f` optimization for an
arbitrary two-row `m=2` lift.

Classification:
`ELEMENTARY_ONE_ROW_LIFT_ALGORITHM=SOURCE_BOUND_ADJACENT_ONLY`.

### S3 — recognition is not automatic from abstract membership

Recognition literature for lifted-graphic/frame matroids shows that graphical
representation questions are genuine algorithmic objects rather than free
normal forms.  In the rank-oracle model, Chen--Whittle prove strong limitations
on recognition by polynomially many rank evaluations.

For binary signed-graphic/even-cycle matroids, dedicated representation and
recognition algorithms exist, illustrating that constructive representation
must be proved separately.

No located source gives a polynomial constructive recognition theorem for the
exact binary `m<=2` class sufficient to replace a missing lineage-coverage
theorem.

Classification:
`CONSTRUCTIVE_TWO_ROW_RECOGNITION=NO_EXACT_CLOSURE_LOCATED`.

### S4 — general binary 1/2/3 decomposition is not a basic-leaf theorem

Truemper gives polynomial machinery to find a 1-, 2-, or 3-sum decomposition
when the corresponding separation exists, or to certify that no such
decomposition exists.

This does not assert that an arbitrary 3-connected binary residual eventually
lands in a graphic/cographic/low-lift basic class.

The celebrated full basic-leaf theorem of this form is special to regular
matroids: Seymour decomposes regular matroids into graphic, cographic, and
`R10` pieces using 1/2/3-sums.

The current cubic-origin matroids are binary but are not assumed regular.

Classification:
`GENERAL_BINARY_SUM_FINDING=SOURCE_BOUND__NO_TWO_ROW_LEAF_COVERAGE`.

### S5 — no-S8 machinery has exact scope

The source-bound shortest-circuit-basis / distinguished-circuit machinery used
earlier applies to the binary no-`S8)-minor class.

It supplies no automatic classification of an `S8`-containing 3-connected
leaf as a two-row graphic lift.

Classification:
`NO_S8_TERMINAL=SOURCE_BOUND__S8_LIVE_CLASS_UNCOVERED`.

### S6 — low-rank perturbation structure is adjacent, not this theorem

Modern finite-field matroid structure theory frequently places highly
connected members of proper minor-closed classes near graphic or cographic
matroids via bounded-rank perturbations.

But:

```
low-rank additive perturbation
!=
m appended signature rows,
```

and no source located in this audit specializes those structure theorems to

```
exact cubic M([I+P+Q|1]) descendants
-> constructively q_graph<=2.
```

Classification:
`LOW_RANK_PERTURBATION_STRUCTURE=ADJACENT_DONOR_ONLY`.

## G4 — end-to-end coverage table

```
CUBIC EXACT-ONE
<-> Hx=1 + |x|=n/3
=
PASS

<-> shortest_f=n/3+1
=
PASS

1/2/3 decomposition when applicable
=
SOURCE-BOUND

no-S8 components
=
SOURCE-BOUND POLYNOMIAL

certified graph-like terminals
=
SOURCE-BOUND / PASS

2/Delta/Y interface semantics
=
PASS

distinguished two-row local solve
=
PASS NM-0013

nondistinguished single-root lifting
=
PASS NM-0014

multi-interface support
=
PASS NM-0015

mixed conditioned costs
=
PASS NM-0016

witness reconstruction
=
PASS CONDITIONAL ON COVERED LOCAL CLASS

BUT

EVERY REMAINING CUBIC-LINEAGE
3-CONNECTED S8-CONTAINING LIVE TORSO
HAS CONSTRUCTIVE q_graph<=2
=
NOT PROVED
```

## Audit decision

```
PA-0012
E10 END-TO-END DECOMPOSITION SOLVER
COMPOSITION / COVERAGE AUDIT
=
PASS_SCOPED_GAP_CONFIRMED

GLOBAL_SOLVER_PROMOTION
=
HOLD
```

The uncovered class is:

```
CUBIC-LINEAGE
S8-CONTAINING
3-CONNECTED
NON-TWO-ROW / UNKNOWN-LIFT-RANK
LIVE TORSO.
```

New mathematics is authorized only inside:

```
R5_E10A_CUBIC_LINEAGE_LIVE_TORSO_GRAPHIC_LIFT_CODIMENSION_COVERAGE_GATE_V1
```

## Two admissible exits

### A — coverage theorem

Prove a polynomial constructive theorem:

```
every unresolved literal cubic-lineage live torso N
has q_graph(N)<=2,
```

and output an explicit witness

```
[B_G;S],
rank(S modulo cut(G))<=2.
```

Existential membership without construction is insufficient.

### B — first lineage falsifier

Produce an **actual source-valid decomposition leaf** `N` descended from an
explicit cubic parent

```
M([I+P+Q|1])
```

such that:

```
N is 3-connected,
N contains S8,
N is not already a source-bound terminal,
q_graph(N)>=3.
```

The parent, decomposition/placement certificate and the `q_graph>=3`
certificate must all be explicit.

A generic binary or generic two-row counterexample is not admissible.

## First implementation obligation

Before searching B, materialize actual decomposition leaves.

The present repository has theorem artifacts about source decomposition but no
machine-readable E10 decomposition tree / leaf-matrix corpus.

Therefore the first finite-control tool should:

1. generate small exact cubic parents `[I+P+Q|1]`;
2. apply a certified 1/2/3-sum decomposition routine or independently
   certificate a terminal leaf;
3. export every leaf matrix and provenance;
4. run a small exact `q_graph<=2` recognizer/falsifier on those leaves.

This is an experimental falsifier path, not a replacement for the coverage
theorem.

## Mandatory anti-loop controls

Do not:

- assume PA-0005's two-row widening is lineage coverage;
- use arbitrary minor universality from NM-0011 as literal leaf coverage;
- confuse additive perturbation rank with appended-row lift number;
- treat one-row lifted-graphic recognition/flow algorithms as an `m=2`
  theorem;
- infer a regular-matroid basic-leaf theorem for arbitrary binary matroids;
- accept existential `q_graph<=2` without constructing `G,S`;
- use a generic high-`q_graph` matroid as a lineage falsifier;
- claim a full deterministic cubic solver or `P=NP` before this gate closes.

## Scientific ceiling

```
LOCAL E10A TWO-ROW SOLVER CHAIN
=
CLOSED CONDITIONAL BRANCH

END-TO-END COMPONENT COVERAGE
=
OPEN

q_graph<=2 FOR EVERY LIVE CUBIC LEAF
=
NOT PROVED

POLYNOMIAL [B_G;S] CONSTRUCTION FOR EVERY LIVE CUBIC LEAF
=
NOT PROVED

GLOBAL E10 SOLVER PROMOTION
=
HOLD

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
