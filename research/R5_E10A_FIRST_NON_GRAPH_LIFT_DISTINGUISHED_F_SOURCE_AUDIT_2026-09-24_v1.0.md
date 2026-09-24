# R5 E10A — First Non-Graph-Lift Distinguished-f Source Audit

Date: 2026-09-24

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED`

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

Strategic parent:
`R5_E10_S8_SPLITTER_INTERFACE_COMPRESSION_GATE_V1`

## Executive correction

The prior S8-containing survivor was too broad.

Several S8-containing / graph-like binary-matroid classes already admit polynomial
distinguished-circuit machinery once a graphical representation is available.
Therefore JANUS must absorb those classes before attempting any new contraction.

The source-bound terminal router is:

```
3-connected binary torso
        |
        +-- no S8 minor
        |      -> existing no-S8 shortest-f machinery
        |
        +-- graft representation
        |      -> graph cycle / T-join
        |
        +-- even-cycle representation
        |      -> parity-constrained T-join
        |
        +-- even-cut representation
               -> parity-constrained cut
```

The new mathematical target begins only after those lanes are removed.

## G0 — exact objects

The distinguished problem is singleton Space Cover:

```
given binary matroid M and f in E(M),
find minimum F subset E(M)-{f}
such that f in span(F).
```

Equivalently:

```
shortest_f(M) = 1 + min |F|.
```

For the JANUS cubic origin the ultimate query remains the lower-bound-tight test

```
shortest_f(M([I+P+Q | 1])) = n/3 + 1.
```

### Graph-lift rank language

A one-row lift of a graphic incidence representation has the form

```
[ B_G ]
[ sigma ]
```

and is the standard even-cycle / signed-graph representation.

The first not-source-closed rung tested by this audit is the singleton problem for
a graphic perturbation of rank at most two.

## G1 — internal anti-duplication

Repo-wide search covered:

- even-cycle / even-cut;
- graft;
- signed graph;
- Space Cover;
- perturbed graphic;
- group-labelled / group-labeled;
- lift rank.

No earlier Fundamentum artifact implementing this graph-lift terminal router or the
rank-2 singleton Space Cover frontier was located.

The existing E10 S8, trellis/min-plus, and maximum-weight controls remain parents.
This audit narrows them rather than opening a parallel carrier program.

## G2 — S8 is already graph-lift tractable

Use the standard binary S8 representation

```
A =
[ I4 | 0111 1011 1101 1111 ].
```

Apply the invertible row transform

```
r1' = r4
r2' = r3 + r4
r3' = r1 + r2
r4' = r2.
```

The result is

```
B =
0 0 0 1 1 1 1 1
0 0 1 1 0 0 1 0
1 1 0 0 1 1 0 0
----------------
0 1 0 0 1 0 1 1
```

Each column in the first three rows has weight one or two and hence is a column
of a reduced vertex-edge incidence matrix of a multigraph. The final row is a
signature.

Thus

```
S8 = ecycle(G,Sigma)
```

for the explicit signed multigraph reconstructed by the checker.

This is a finite row-equivalence certificate. No novelty claim is made.

## G3 — source-bound polynomial graph-like terminals

### A. Even-cycle

Guenin-Heo give polynomial recognition of even-cycle binary matroids from matrix
representations; their representation theory constructs signed-graph
representations. Even-cycle matroids are minor-closed.

For

```
M = ecycle(G,Sigma)
```

represented by reduced incidence rows plus one signature row, let the
distinguished ordinary edge f have endpoints u,v.

A set J not containing f spans f exactly when

```
boundary(J) = {u,v}
and
|J intersect Sigma| = 1_{f in Sigma} mod 2.
```

Hence shortest-f is a minimum-weight `{u,v}`-join with prescribed signature
parity, plus the distinguished element.

Cook-Espinoza-Goycoolea, Proposition 5.3, gives a polynomial algorithm for a
minimum-weight T-join with an odd or even number of marked/red edges:

```
O(2^|T| + |T|^2 |V|^2 + |V|^3).
```

Here `|T|=2`, so this is polynomial.

Therefore:

```
EVEN-CYCLE + REPRESENTATION
=
POLYNOMIAL DISTINGUISHED-f TERMINAL.
```

### B. Even-cut

Even-cut matroids are also recognizable in polynomial time and are minor-closed.

For a graft representation `ecut(G,T)`, a circuit is an inclusion-minimal
nonempty T-even cut. Requiring an ordinary graph edge `f=uv` in the circuit
means the cut separates u and v and has the required T-even parity.

Minimum `s-t` T-even cuts are polynomially computable by the
Grötschel-Lovász-Schrijver / parity-cut machinery.

Thus:

```
EVEN-CUT + REPRESENTATION
=
POLYNOMIAL DISTINGUISHED-f TERMINAL.
```

### C. Graft matroid

For a graft `(G,D)`, the associated binary matroid is represented by the
vertex-edge incidence matrix of `G` with one extra graft column equal to the
incidence vector of `D`.

Its circuits are:

- ordinary graph circuits; and
- the graft element together with an inclusion-minimal D-join.

If distinguished `f` is the graft element, shortest-f is one plus a minimum
D-join.

If distinguished `f=uv` is an ordinary graph edge, compare:

1. a shortest graph circuit through f; and
2. the graft element plus a minimum D-join forced through f, equivalently
   f plus a minimum `D symmetric-difference {u,v}`-join after f is removed.

Minimum T-join is polynomial by the Edmonds-Johnson matching reduction.

Therefore a supplied graft representation is another polynomial
distinguished-f terminal.

Recognition/reconstruction of an arbitrary graft representation is kept separate
from this solver statement; the solver lane may only fire when such a
representation is polynomially certified.

## G4 — first-exit localization

Even-cycle and even-cut matroids are minor-closed.

Hence along a Splitter sequence

```
M0, M1, ..., Mk
```

if `Mi` is even-cycle and `Mi+1` is not, no later matroid can re-enter the
even-cycle class, because `Mi+1` remains a minor of every later matroid.

The analogous statement holds for even-cut.

Thus the first extension/coextension that exits a minor-closed graph-lift class
is a legitimate localization point.

Firewall:

```
GRAFT
```

is retained as a polynomial terminal when certified, but this audit does not use
a minor-closed re-entry claim for the graft class.

## G5 — perturbed graphic / Space Cover collision

Fomin-Golovach-Lokshtanov-Saurabh-Zehavi define Space Cover exactly as spanning
terminal columns by a small nonterminal set.

Their 2019 perturbed-graphic result states:

- for every fixed perturbation rank r, Space Cover is FPT parameterized by k;
- Space Cover is NP-complete for perturbation rank at most 2 and at most two
  terminals;
- on general binary matroids the problem is W[1]-hard in k even with one terminal.

Crucial scope correction:

the published rank-2 NP-completeness construction uses the two-terminal regime.
The source does NOT justify transferring that result to the singleton
distinguished-f problem.

Conversely, the FPT algorithm for fixed r is exponential/superpolynomial in k
and therefore does not give a polynomial algorithm for the JANUS regime where
the target size grows linearly with n.

So the exact remaining first rung is:

```
rank <= 2 perturbed graphic
+
one distinguished terminal f
+
unit weights
+
JANUS lower-bound-tight origin where applicable.
```

No located source in this audit closes that exact problem.

## G6 — group-labelled-path caution

Iwata-Yamaguchi give a deterministic strongly polynomial algorithm for the
shortest non-zero path problem in group-labelled graphs.

That source is a useful donor, but a shortest group-labelled path is not
automatically the same object as a minimum parity/group-labelled T-join:
a T-join may contain cycle components in addition to its terminal path.

For one parity bit the stronger parity-T-join theorem above closes the gap.
For multiple label bits, JANUS may not replace the full singleton Space Cover
problem by a path problem without an exact reduction theorem.

Therefore:

```
FIXED FINITE GROUP SHORTEST PATH
!=
SOURCE-PROVED FIXED-LIFT-RANK
SINGLETON SPACE COVER SOLVER.
```

## Collision matrix

| JANUS object | External object | Status | Action |
| --- | --- | --- | --- |
| one signature row over graphic incidence | even-cycle matroid | EXACT_LANGUAGE_COLLISION | source-bind |
| shortest-f in even-cycle representation | parity-constrained T-join | STRONGER_KNOWN_RESULT | polynomial terminal |
| even-cut representation | elementary lift of cographic / graft cuts | EXACT_LANGUAGE_COLLISION | source-bind |
| shortest-f in even-cut representation | minimum s-t T-even cut | STRONGER_KNOWN_RESULT | polynomial terminal |
| graft representation | graphic matroid + graft column | EXACT_LANGUAGE_COLLISION | source-bind |
| shortest-f in supplied graft representation | T-join / graph cycle | STRONGER_KNOWN_RESULT | polynomial terminal |
| S8 as one-row graph lift | explicit even-cycle representation | EXACT_FINITE_CERTIFICATE | remove S8 itself from hard intuition |
| rank-r perturbed graphic Space Cover, fixed r | FPT in k | KNOWN_PARAMETERIZED_DONOR | not polynomial for k=Theta(n) |
| rank<=2, at most two terminals | NP-complete | KNOWN_BARRIER | do not transfer to singleton |
| general binary, one terminal | W[1]-hard in k | KNOWN_BARRIER | not specific to rank 2 |
| group-labelled shortest non-zero path | strongly polynomial | KNOWN_DONOR | does not by itself solve general T-join/span problem |
| rank<=2 perturbed graphic, one terminal | no closure located | SCOPED_GAP_SURVIVES | first exact new-math rung |

## Audit decision

```
GRAFT / EVEN-CYCLE / EVEN-CUT
DISTINGUISHED-f LANES
=
SOURCE-BOUND POLYNOMIAL TERMINALS

S8 ITSELF
=
EVEN-CYCLE FINITE CERTIFICATE
NOT HARD SURVIVOR

FIRST-NON-GRAPH-LIFT LOCALIZATION
=
VALID FOR MINOR-CLOSED
EVEN-CYCLE / EVEN-CUT LANES

FIXED-r GROUP-LABELLED-PATH
AS UNIVERSAL SINGLETON SOLVER
=
NOT SOURCE-PROVED

RANK-2 PERTURBED-GRAPHIC
SINGLETON SPACE COVER
=
SCOPED GAP SURVIVES
```

Decision:

```
PASS_SCOPED_GAP_CONFIRMED
```

Conceptual parent:

```
R5_E10A_FIRST_NON_GRAPH_LIFT_DISTINGUISHED_F_GATE_V1
```

The only new mathematics authorized by this receipt is:

```
R5_E10A_GRAPH_LIFT_RANK2_SINGLETON_SPACE_COVER_GATE_V1
```

First obligation:

determine whether singleton Space Cover on rank-at-most-two perturbed graphic
matroids has a polynomial exact algorithm/certificate, or whether a source-exact
hardness reduction already reaches the singleton case.

Any proposed algorithm must preserve the JANUS distinguished-f witness and may
not use the already-tombstoned full trellis/min-plus syndrome table.
