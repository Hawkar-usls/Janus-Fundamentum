# R5 E10A — Cubic-Lineage Lift-Rank Growth and Construction Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__MERSENNE_PARENT_GROWTH_SOURCE_BOUND_INPUT__LIVE_LEAF_EXTRACTION_GAP_SURVIVES`

Immediate predecessors:
`PA-0013-CUBIC-LINEAGE-HIGHER-LIFT-LIVE-LEAF-SOURCE-AUDIT`
`NM-0018-ANCHORED-HIGHER-LIFT-FPT-TJOIN`

Governance repair target:
`NM-0019-TORUS-L7-LIFT-RANK-STRESS`

## G0 — why a new audit is mandatory

PA-0013 authorized the canonical semantic route

```
CUBIC_LINEAGE_HIGHER_LIFT_LIVE_LEAF
```

for local higher-lift optimization.

NM-0018 closed that local optimization gate conditionally:

```
explicit anchored q-lift
->
deterministic 2^O(q) poly(n) shortest-f.
```

The next mathematical object is different:

```
CUBIC_LINEAGE_LIFT_RANK_GROWTH_AND_CONSTRUCTION.
```

NM-0019 used this changed route before a matching pre-math audit existed.
The resulting pre-math/registry failures are correct governance stops.

This audit introduces the changed route and is the authorizing audit for
NM-0019.

## G1 — internal anti-duplication

Repository search at HEAD `775df48cd611b1a85e61bae3cbd5436a6636db71`
found no prior artifact containing any of:

```
2407.19898
Carmona-Pirez
Rule 60
Newman-Moore
```

Thus the Mersenne/Rule-60 source below is not already represented in the
current #510 patch.

Already sealed internally and not to be reopened:

- NM-0018: explicit anchored q-lift optimization is deterministic
  `2^O(q) poly(n)`;
- NM-0017: actual n=15 terminal leaf has high lift rank;
- NM-0019 finite control: the L=7 torus is an actual terminal S8 live leaf
  with `q_graph>=19`;
- random square cubic rank alone is not a lift-rank currency.

## G2 — Rule 60 / Newman-Moore source collision

Carmona-Pirez et al., arXiv:2407.19898v2 / published 2025, prove for every
Mersenne circumference

```
L=2^k-1
```

that every even Rule-60 initial row is L-periodic (Theorem 3.5).

They then prove that the square L x L Newman-Moore model has exactly

```
2^(L-1)
```

ground states (Theorem 4.1).

The paper explicitly notes that the Rule-60 periodicity proof itself is not
new and points to earlier Ducci-sequence work.  JANUS therefore claims no
novelty for this periodicity statement.

The Newman-Moore ground-state equations are the same three-term binary torus
constraint as

```
H_L = I + P_x + P_y
```

up to the harmless torus orientation/shear convention.

Consequently the source gives the exact nullity/rank identity

```
dim ker(H_L) = L-1,
rank(H_L)    = L^2-L+1.
```

Classification:
`MERSENNE_TORUS_NULLITY_AND_RANK=SOURCE_BOUND_AFTER_COORDINATE_IDENTIFICATION`.

## G3 — broader cellular-automaton language is also source-bound

Sfairopoulos et al. (2023), arXiv:2301.02826, use cellular automata to
characterize minimum-energy configurations of the Newman-Moore / triangular
plaquette model for arbitrary torus sizes.

Therefore:

```
torus constraint
<-> cellular automaton orbit
```

is established external language and must not be presented as a new JANUS
mechanism.

Classification:
`NEWMAN_MOORE_CA_TORUS_LANGUAGE=SOURCE_BOUND`.

## G4 — the new derived high-q parent consequence

For the extended cubic parent

```
M_L = M([H_L | 1])
```

the cubic star rows have weight four.

The remaining ingredient needed for the NM-0018 q_graph inequality is
`g*(M_L)=4`.

The proposed finite-field proof uses the exact source-bound facts:

1. the kernel is parametrized by the even initial-row space;
2. the Rule-60 coordinate functional is represented by
   `x^i(1+x)^j`;
3. over `GF(2^k)`, the Artin-Schreier image
   `alpha -> alpha^2+alpha` is exactly the trace-zero hyperplane;
4. `GF(2^k)^*` is cyclic of order `L=2^k-1`.

From these, for `k>=3`, all ordinary kernel-column signatures are nonzero
and pairwise distinct.

In the dual representation of the extended cocycle code the ordinary columns
are

```
(sig(e),1)
```

and the distinguished column is

```
f=(0,1).
```

Therefore cocycle weights one, two and three are impossible, while the cubic
star supplies weight four:

```
g*(M_L)=4.
```

Combining this with the already sealed NM-0018 inequality

```
q_graph(N)
>=
r(N)-floor((2|E(N)|-1)/g*(N))
```

gives for the literal Mersenne cubic parents

```
|E(M_L)| = L^2+1,
r(M_L)   = L^2-L+1,
g*(M_L)  = 4,

q_graph(M_L)
>=
(L^2-2L+3)/2
=
Omega(L^2)
=
Omega(|E|).
```

Examples:

```
L=7  -> q_graph>=19
L=15 -> q_graph>=99
L=31 -> q_graph>=451.
```

This is a **literal cubic-parent family** consequence.  It is not yet an
actual-live-leaf family theorem.

## G5 — coding-theory distance is not the missing terminality theorem

The Newman-Moore code is standardly described as a fractal binary code with
block length `L^2`, dimension `O(L)`, and distance on the
`L^(log_2 3)` scale.

This is useful as a finite/connectivity control, but the distance exponent is
strictly below two.  No source located in this audit turns that distance scale
alone into absence of every exact 3-separation of the associated matroid.

Freeze:

```
DISTANCE-ONLY TERMINALITY ROUTE
=
NO SOURCE CLOSURE LOCATED;
DO NOT PRIORITIZE.
```

## G6 — 3-separation literature does not close the Mersenne family

Oxley--Semple--Whittle and subsequent 3-connected-matroid work give general
tree/decomposition structure for nontrivial 3-separations and standard
uncrossing tools.

No source located in this audit specializes those theorems to the Mersenne
Newman-Moore / Rule-60 matroids in a way that proves:

```
no exact 3-separation for infinitely many L,
```

or that a canonical 1/2/3-sum decomposition contains a leaf carrying
superlogarithmic `q_graph).

Classification:
`MERSENNE_TORUS_TERMINALITY_OR_HIGH_Q_LEAF_EXTRACTION=SCOPED_GAP_SURVIVES`.

## G7 — no source lift-rank concentration theorem under 1/2/3 sums located

A targeted sweep of:

- m-lifts of graphic matroids;
- rank-k lift constructions;
- lifted-graphic matroids;
- 2/3-sum closure;
- perturbed-graphic structure;
- matroid 3-separation trees

located no theorem of the form

```
q_graph(parent)
<=
max_leaf q_graph
+
O(separator size)
```

or any equivalent statement strong enough to force a high-q leaf from the
high-q Mersenne parent.

Walsh and Bernstein--Walsh provide structural rank-k lift theory, not this
decomposition-concentration theorem.

Thus the attractive shortcut

```
high q_graph parent
=> automatically high q_graph decomposition leaf
```

is not source-bound and may not be assumed.

## G8 — exact audit decision

Known/source-bound:

```
Mersenne Rule-60 periodicity
Mersenne Newman-Moore ground-state count
exact nullity/rank of the torus constraint
general CA/torus language
general 3-separation tree language
higher-rank lift structural language
```

JANUS-derived but not a live-leaf exit:

```
Mersenne literal cubic parents:
g*=4
and
q_graph=Omega(|E|).
```

Still open:

```
either
an infinite/unbounded subsequence of those parents
is itself an S8-containing terminal live leaf,

or
canonical 1/2/3 decomposition leaves retain
q_graph=omega(log n_leaf).
```

Therefore:

```
PA-0014
CUBIC-LINEAGE
LIFT-RANK GROWTH AND CONSTRUCTION
SOURCE AUDIT
=
PASS_SCOPED_GAP_CONFIRMED
```

and

```
GLOBAL_SOLVER_PROMOTION
=
HOLD.
```

## G9 — authorized next gate

New mathematics is authorized only inside:

```
R5_E10A_MERSENNE_TORUS_LIVE_LEAF_EXTRACTION_GATE_V1
```

Input family:

```
M_L=M([I+P_x+P_y|1]),
L=2^k-1,
k>=3.
```

Source/derived input facts:

```
literal cubic origin,
rank=L^2-L+1,
cogirth=4,
q_graph>= (L^2-2L+3)/2.
```

Valid exits:

A. prove an unbounded subsequence is itself an actual S8-containing terminal
   leaf with no 1/2/exact-3 separation; or

B. give source-valid 1/2/3-sum decompositions and prove that some resulting
   unresolved live leaf retains `q_graph=omega(log n_leaf)`.

A parent-only high-q theorem is useful input/control but is **not** by itself
an exit from this gate.

## Mandatory anti-loop controls

Do not:

- re-prove Mersenne Rule-60 periodicity;
- re-prove the ground-state count by brute force;
- call the high-q parent family a high-q live-leaf family;
- infer terminality from code distance alone;
- assume lift-rank concentration under 1/2/3 sums without a theorem;
- use generic high-q matroids instead of literal cubic descendants;
- reopen the higher-lift local solver closed by NM-0018;
- promote the global E10 solver or P=NP.

## Scientific ceiling

```
PA-0014
=
PASS_SCOPED_GAP_CONFIRMED

MERSENNE LITERAL CUBIC PARENT q_graph
=
Omega(|E|)

UNBOUNDED ACTUAL LIVE-LEAF q_graph
=
NOT PROVED

LIFT-RANK CONCENTRATION UNDER DECOMPOSITION
=
NO SOURCE CLOSURE LOCATED

GLOBAL SOLVER PROMOTION
=
HOLD

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
