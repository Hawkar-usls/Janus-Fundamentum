# R5 E10A — Two-Row Graph-Lift Distinguished-f Source Audit

Date: 2026-09-24

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED`

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

Strategic parent:
`R5_E10A_FIRST_NON_GRAPH_LIFT_DISTINGUISHED_F_GATE_V1`

## G0 — exact frozen representation

This audit intentionally separates **row-lift dimension** from additive
perturbation rank.

The input representation is literally

```
A =
[ B_G ]
[ S   ],
```

where:

- `B_G` is a reduced binary vertex-edge incidence matrix of an undirected
  multigraph `G`;
- `S in GF(2)^(2 x E)` consists of exactly two signature rows;
- every element is therefore an edge `e=ab` carrying a label
  `lambda(e) in GF(2)^2`.

For a distinguished element `f=uv`, a set `J subseteq E-{f}` spans `f`
exactly when

```
boundary(J) = {u,v}
and
sum_{e in J} lambda(e) = lambda(f) in GF(2)^2.
```

Thus shortest-`f` is the minimum-cardinality `{u,v}`-join with a prescribed
`GF(2)^2` label, plus one for `f`.

This is the exact two-signature-row graph-lift object. It is **not**
`I(G)+P, rank(P)<=2`.

## G1 — internal anti-duplication

Fundamentum searches included:

- parity T-join;
- two parity constraints;
- group-labelled / group-labeled T-join;
- homology T-join;
- rank-k graphic lift;
- GF(2)^2;
- cycle labels;
- Space Cover;
- exact / parity matching.

No earlier artifact closing this exact two-row graph-lift distinguished-`f`
problem was located.

The following parents remain source-bound and must not be repeated:

- ordinary graphic shortest-`f`;
- one-row even-cycle / parity T-join;
- full trellis/min-plus conditional syndrome tables;
- additive rank-2 perturbed-graphic Space Cover (PA-0004).

## G2 — canonical external names

Primary canonical language:

- minimum-weight `T`-join with a prescribed finite-abelian-group label;
- group-constrained circulation;
- graphic rank-`k` lift / group-labeled graph lift;
- parity/congruency-constrained combinatorial optimization.

The exact group here is

```
Gamma = GF(2)^2.
```

Walsh's rank-`k` lift work supplies source context for higher-rank lifts of
graphic matroids and their relation to group-labeled graphs. It is structural
background, not by itself a shortest-`f` algorithm.

## G3 — source exhaustion

### S1 — rank-one baseline

For one signature row, the problem is the source-bound even-cycle lane:
minimum distinguished circuit reduces to a `{u,v}`-join with one prescribed
parity. Cook–Espinoza–Goycoolea give a polynomial algorithm for minimum-weight
odd/even `T`-join with nonnegative weights. Therefore row-lift dimension one
is already a deterministic polynomial terminal.

### S2 — finite-group constrained TU / circulation

Nägele–Santiago–Zenklusen and subsequent group-constrained extensions formulate
Group-Constrained Circulation:

```
minimum-cost integral circulation
subject to
sum_a eta(a) x_a = g in a finite abelian group.
```

For network-matrix GCTU with a finite abelian group and unary encoded objectives,
the cited source gives a strongly polynomial **randomized** algorithm. The
randomization is inherited from exact-length circulation / exact-cost perfect
matching machinery.

Consequently, once the two-row distinguished-`f` problem is represented as a
`GF(2)^2`-constrained `{u,v}`-join / circulation, there is a source-backed
randomized-polynomial route.

For every fixed number `r` of signature rows, the same mechanism uses a fixed
finite group `GF(2)^r` (plus standard flow bookkeeping) and therefore gives a
fixed-`r` randomized-polynomial lane.

This does **not** establish deterministic P.

### S3 — exact matching derandomization firewall

Exact Matching has had a randomized polynomial algorithm since the
Mulmuley–Vazirani–Vazirani line, while a deterministic polynomial algorithm
remains open. Current 2023–2026 work continues to state that derandomization is
open and supplies deterministic algorithms only for restricted classes or
relaxations.

This source fact explains why the group-constrained circulation theorem is
randomized. It does **not** prove that the present two-row T-join subclass is
equivalent to Exact Matching, and JANUS must not claim such an equivalence
without a reduction.

### S4 — group-labelled shortest path is not enough

Iwata–Yamaguchi give a deterministic strongly polynomial shortest non-zero path
algorithm for finite abelian group-labeled graphs.

A `{u,v}`-join with a prescribed total group label may contain Eulerian cycle
components in addition to the terminal path. Therefore the path theorem alone
does not close the group-constrained T-join problem.

### S5 — one-parity T-join caution

Schlotter–Sebő further emphasize that path and T-join parity problems have
different complexity behavior. This reinforces the firewall against replacing
the T-join by a path without a proof.

## G4 — collision matrix

| JANUS object | External object | Classification | Action |
| --- | --- | --- | --- |
| one signature row | even-cycle / signed-graph matroid | STRONGER_KNOWN_RESULT | deterministic poly terminal |
| two signature rows | GF(2)^2-labelled T-join | EXACT_LANGUAGE_COLLISION | use canonical language |
| fixed-r signature rows | finite-group-labelled graphic lift | KNOWN_STRUCTURAL_DONOR | source-bind Walsh |
| group-constrained circulation | GCTU/GCC | STRONGER_KNOWN_RANDOMIZED_RESULT | randomized terminal only |
| generic deterministic exact-matching derandomization | Exact Matching | OPEN_EXTERNAL_BARRIER | do not assume |
| shortest non-zero group-labelled path | path donor | KNOWN_DONOR_ONLY | does not replace T-join |
| additive rank-2 perturbed graphic | I(G)+P | DIFFERENT_REPRESENTATION | PA-0004 reserve, do not conflate |
| deterministic two-row distinguished-f solve | no closure located | SCOPED_GAP_SURVIVES | new math only here |

## Audit decision

```
ROW-LIFT r=0
=
DETERMINISTIC P

ROW-LIFT r=1
=
DETERMINISTIC P

FIXED ROW-LIFT r>=2
=
SOURCE-BACKED RANDOMIZED POLY
VIA FINITE-GROUP CIRCULATION

DETERMINISTIC r=2
=
NO CLOSURE LOCATED

ADDITIVE PERTURBATION RANK
!=
ROW-LIFT DIMENSION
```

Decision:

```
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1
```

The first allowed brick is deliberately narrow:

1. prove the exact two-row distinguished-`f` to finite-group-circulation bridge
   with polynomial witness reconstruction;
2. source-bind the resulting randomized solver;
3. then seek a **deterministic** special algorithm or contraction for this
   `GF(2)^2` T-join subclass, without full trellis/min-plus tables.

A randomized solver is useful as a control and terminal for RP-style experiments,
but it does not satisfy JANUS's deterministic `P` contract.
