# R5 E10A — Top-Plateau to Optimal-Face Correct-Parity Matching

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_BRIDGE_AFTER_AUDIT__UNIT_POSITIVE_ORIGIN__NO_GENERAL_BCPM_CLAIM`

Authorizing audit:
`PA-0005-TWO-ROW-GRAPH-LIFT`

Continuation of:
`NM-0006-GF2-SQUARED-PAIRWISE-PARITY-COLLAPSE`

Parent scope:
`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1`

Checker:
`experiments/r5_e10a_top_plateau_optimal_face_parity.py`

## 1. Input inherited from pairwise-parity collapse

For a fixed terminal pair `s,t`, let

```
m_g
```

be the minimum weight of a simple `s-t` path whose edge-label XOR is
`g in GF(2)^2`.

The preceding JANUS theorem deterministically computes all six pair minima

```
mu_{a,b}=min(m_a,m_b).
```

Let

```
M=max_{a<b} mu_{a,b}.
```

For a feasible target label `c` with `R_c=M`, the only unresolved question is

```
m_c=M
or
m_c>M.
```

The latter can happen for at most one label.

This artifact treats the **unit-positive JANUS path instances** inherited from
the two-row graph-lift/T-join origin.  It does not claim the reduction below for
arbitrary zero/negative edge-weight refinements without the stated parity
bookkeeping.

## 2. Choose one plateau pair

Choose `d != c` such that

```
mu_{c,d}=M.
```

There is a unique nonzero linear functional

```
chi:GF(2)^2 -> GF(2)
```

whose affine fiber containing `c` is exactly `{c,d}`.

Choose a second linear functional `psi` with

```
psi(c) != psi(d).
```

The pair-class problem is therefore:

```
minimize path weight
subject to chi(total label)=chi(c).
```

Inside that class, `psi(total label)` distinguishes `c` from `d`.

## 3. One-bit XOR parity -> ordinary odd path

For each original edge `e`:

- if `chi(lambda(e))=1`, keep it as one edge;
- if `chi(lambda(e))=0`, subdivide it into two edges.

Put the original positive weight on one designated carrier edge and zero on the
other subdivision edge.  Put the refined bit `psi(lambda(e))` only on the
positive carrier edge.

Then the parity of the number of transformed edges in a path equals
`chi(total label)`, while the XOR of refined bits on carrier edges equals
`psi(total label)`.

If the required first parity is even, append one zero-weight, refined-bit-zero
terminal edge so that the target becomes an odd-path problem.

Thus the pair-class optimum `M` is exactly a minimum-weight odd simple path in
the transformed graph.

## 4. Source-bound odd-path -> perfect-matching reduction

Jüttner--Király--Mendoza-Cadena--Pap--Schlotter--Yamaguchi, Theorem 12,
use the standard two-copy construction:

- create a copy of the transformed graph;
- add zero-weight vertical edges `v-v'`;
- remove the copied terminal vertices;
- a constrained odd path alternates between original/copy edges and becomes a
  perfect matching.

With no additional position constraints, the construction specializes to the
ordinary nonnegative odd-path problem.

Mark as **red** both copies of every positive carrier edge whose refined bit is
one.  All zero subdivision edges and all vertical edges are blue.

For a path `Q`, the corresponding matching `M_Q` satisfies

```
w(M_Q)=w(Q)
```

and

```
redParity(M_Q)=psi(label(Q)).
```

## 5. Reverse parity preservation at the optimum

The source reverse map takes a perfect matching and decomposes its projected
ordinary edges into:

- one odd terminal path `Q`;
- even cycles;
- possible doubled/single auxiliary edges,

and proves

```
w(Q) <= w(Matching).
```

For the present JANUS origin, every original path edge has strictly positive
(unit) weight.  Every edge carrying the refined red bit is placed on a positive
carrier edge.  Zero-weight subdivision/vertical gadget edges carry refined bit
zero.

Let `N` be a **minimum-weight** matching of weight `M`.  The reverse path
has weight at most `M`, while `M` is already the minimum pair-class path
weight.  Therefore its reverse path has weight exactly `M`.

Any removed projected component containing a positive carrier edge would have
positive weight and would make the reverse path strictly cheaper, impossible.
Hence every removed zero-weight component has refined parity zero.

Therefore exactly

```
redParity(N)=psi(label(Q)).
```

Consequently:

```
there is a c-labelled path of weight M
iff
the minimum-weight perfect-matching face
contains a matching of parity psi(c).
```

This is the exact top-plateau transfer.

## 6. Canonical residual

Define the scoped object

```
OPTIMAL-FACE CORRECT PARITY MATCHING
```

for the auxiliary matching instances produced above:

given a weighted general graph, a red-edge set, and a known minimum weight
`W`, decide whether **some minimum-weight perfect matching** has the required
red parity.

Then the JANUS top plateau satisfies

```
m_c=M
iff
OFCPM(aux(c,d)) = YES.
```

If the answer is NO, pairwise-parity collapse implies

```
m_c>M
```

and `c` is the unique strict maximum label class.

## 7. Source audit and collision matrix

El Maalouly--Steiner--Wulf prove deterministic polynomial **Correct Parity
Matching (CPM)** for general graphs via Lovász' linear-hull theorem.

They also prove deterministic polynomial **Bounded Correct Parity Matching
(BCPM)** for bipartite graphs, while general-graph BCPM remains open in their
work and in Murakami--Yamaguchi's follow-up.

This does not close OFCPM:

- CPM ignores the minimum-weight face;
- general BCPM is strictly broader than the present optimum-face question;
- the auxiliary odd-path matching graph is generally non-bipartite.

A tempting bipartite shortcut is invalid.  For bipartite matching, the union of
all minimum-weight matching edges has the property that every perfect matching
of that union graph is minimum-weight.  This follows because the Birkhoff face
is defined only by degree equations and zeroed nonnegativity coordinates.

For general graphs, the perfect-matching polytope also has odd-cut/blossom
inequalities.  Therefore the minimum face cannot in general be represented by
only deleting non-optimal edges.

The correct source-bound structural language is complementary slackness:

```
minimum matching
=
tight edges
+
every positive-dual odd set crossed exactly once.
```

The positive-dual odd sets may be chosen laminar by standard weighted-blossom
machinery.

No located source in this re-audit gives a deterministic parity algorithm
specifically for this minimum-weight face with its laminar blossom constraints.

## 8. Free deterministic early exits

Ordinary deterministic MWPM already gives two cheap diagnostics.

Let `r(M)` be the number of red edges.  With a sufficiently large multiplier
`B`, optimize lexicographically using

```
B*w + r
```

and

```
B*w - r.
```

This yields the minimum and maximum red counts among primary-optimal matchings.

If either extreme has the desired parity, OFCPM is immediately YES.

These extremes do not solve the general case: an opposite-parity optimum may
lie between same-parity extremes.

## 9. New exact frontier

The active child is

```
R5_E10A_OPTIMAL_FACE_BLOSSOM_PARITY_GATE_V1
```

Input:

- the general auxiliary perfect-matching graph produced by the one-bit
  parity-path reduction;
- one minimum-weight perfect matching;
- an optimal weighted-matching dual with a laminar positive-blossom family;
- one secondary red parity.

Target:

```
deterministically decide whether
the minimum-weight face contains
the required parity,
and reconstruct such a matching.
```

Allowed attack:

- tight-edge graph;
- laminar blossom contraction/decomposition;
- Lovász CPM / linear-hull machinery on exact contracted pieces;
- two-state parity summaries.

Forbidden:

- deleting non-optimal edges and pretending the graph is bipartite;
- assuming general BCPM;
- assuming Exact Matching derandomization;
- full trellis/min-plus syndrome tables;
- relying on the quarantined Du-2026 claim.

## 10. Scientific ceiling

```
TOP PLATEAU -> OPTIMAL-FACE PARITY
=
PROVED FOR UNIT-POSITIVE JANUS ORIGIN

GENERAL CPM
=
DETERMINISTIC P / SOURCE-BOUND

BIPARTITE BCPM
=
DETERMINISTIC P / SOURCE-BOUND

GENERAL BCPM
=
OPEN EXTERNAL BARRIER

OPTIMAL-FACE BLOSSOM PARITY
=
NOT CLOSED BY LOCATED SOURCES

D1
=
EMPTY

P_VS_NP
=
OPEN
```
