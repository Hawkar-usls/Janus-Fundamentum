# R5 E10A — Cubic-Lineage Higher-Lift Live-Leaf Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__HIGHER_LIFT_LOCAL_SOLVER_AND_LIFT_RANK_GROWTH_GAP_SURVIVE`

Immediate predecessor:
`NM-0017-CUBIC-LINEAGE-QGRAPH-GE3-PARENT-LEAF-FALSIFIER`

## G0 — changed object

NM-0017 falsifies universal two-row coverage with an actual cubic-origin source-valid terminal leaf

```
M = M([I+P+P^4 | 1]), n=15,
```

satisfying

```
3-connected,
no exact 3-separation,
S8 minor,
q_graph >= 3.
```

Therefore the live object is no longer the two-row class.  The source audit asks:

1. what is known for supplied `m`-lift representations with `m>=3`;
2. whether fixed-`m` recognition/construction is source-bound;
3. whether a deterministic shortest-`f` solver is already known;
4. whether an alternative standard representation class covers the NM-0017 leaf;
5. whether cubic origin implies any source-known uniform bound on `m`.

No new higher-lift mathematics is allowed before this audit.

## G1 — canonical language

Huynh defines an `m`-lift of a graphic matroid by a representation

```
M = M_F([A;B]),
```

where `B` is a signed incidence matrix of a graph and `A` has exactly `m` rows.

In the binary case this is precisely a `GF(2)^m`-labelled graph representation.

Thus the JANUS parameter

```
q_graph(N)
```

is the minimum `m` for which such an `m`-lift representation exists.

This terminology is source-bound.

## G2 — source exhaustion

### S1 — fixed-m representation gives a fixed finite group-labelled optimization problem

If an explicit representation

```
[B_G;S],  S in GF(2)^(m x E)
```

is supplied, shortest-`f` reduces exactly to a `GF(2)^m`-labelled
`{u,v}`-join / group-constrained circulation, as already proved internally by
the GCC bridge.

Nägele et al. prove a strongly polynomial **randomized** algorithm for
group-constrained circulation / network-matrix GCTU with any finite abelian
group and unary objectives.

For fixed `m`, `|GF(2)^m|=2^m` is constant, so this is a source-backed
randomized polynomial terminal.

If `m` grows with the input, this source route has explicit dependence on
the group size; the reductions construct objects of size proportional to
`|G|`.  Therefore it does not supply a uniform polynomial algorithm in
the bit-length `m` when `m` is unbounded.

Classification:
`SUPPLIED_FIXED_M_LIFT_OPTIMIZATION=SOURCE_BOUND_RANDOMIZED_POLYNOMIAL`.

### S2 — one-row special algorithms do not extend automatically

Binary elementary lifts of graphic matroids are the one-row / even-cycle /
signed-graphic regime.

Dedicated recognition/representation and flow algorithms exist for this
elementary case.

These sources do not state an algorithm for arbitrary `m)-row lifts with
`m>=2`.

Classification:
`M_EQ_1_RECOGNITION_AND_OPTIMIZATION=SOURCE_BOUND_SPECIAL_CASE`.

### S3 — higher-rank lift theory is structural, not a recognition/solver theorem

Walsh constructs rank-`k` matroid lifts and studies when group-labelled graph
lifts of rank `k>=2` exist.

Bernstein--Walsh prove that the general rank-`k` lift construction captures
representable matroid lifts.

These papers give a structural theory of higher-rank lifts.  They do not
supply:

- polynomial recognition of a binary matrix as an `m)-lift of some graph for
  arbitrary fixed `m>=2`;
- construction of the underlying graph and label rows from an arbitrary binary
  matrix;
- deterministic minimum distinguished circuit for the supplied higher-lift
  representation.

Classification:
`HIGHER_RANK_LIFT_STRUCTURE=SOURCE_BOUND__ALGORITHMIC_GAP_SURVIVES`.

### S4 — lifted-graphic recognition literature is elementary-lift literature

The standard matroid class named `lifted-graphic` is the elementary
(one-rank) lift of a graphic matroid / biased-graph lift matroid.

Recognition results and limitations for lifted-graphic matroids therefore must
not be read as recognition results for arbitrary appended-row `m)-lifts.

Binary signed-graphic recognition likewise addresses the one-row signed-graph
language.

Classification:
`LIFTED_GRAPHIC_RECOGNITION_NOT_GENERAL_M_LIFT_RECOGNITION`.

### S5 — low-rank additive perturbations remain a different representation

Fomin et al. study binary matrices

```
I(G)+P, rank(P)<=r.
```

For fixed `r`, Space Cover is FPT in the solution size `k`; the same work
contains hardness for nearby parameter regimes.

This is not the appended-row representation

```
[B_G;S].
```

The source therefore neither solves nor classifies the NM-0017 higher-lift
leaf.

Classification:
`ADDITIVE_PERTURBED_GRAPHIC=ADJACENT_DIFFERENT_REPRESENTATION`.

### S6 — group-labelled linkage/minor algorithms are not shortest-f optimization

Huynh gives polynomial algorithms for fixed finite-group labelled minor/linkage
questions.

Those algorithms assume the group-labelled graph representation is already
given and address feasibility/minor structure, not minimum-weight prescribed
boundary-group `T`-join / shortest distinguished circuit.

Classification:
`FIXED_GROUP_LINKAGE_AND_MINOR_TESTING=SOURCE_BOUND_ADJACENT_ONLY`.

### S7 — no source uniform lift-rank bound for cubic lineage located

No source located in this audit proves that every literal terminal descendant
of

```
M([I+P+Q|1])
```

has

```
q_graph <= C
```

for a universal constant `C`, nor even `q_graph=O(log n)`, together with a
polynomial construction of the representation.

NM-0017 already proves that `C=2` is false.

Classification:
`CUBIC_LINEAGE_LIFT_RANK_BOUND=SCOPED_GAP_SURVIVES`.

## G3 — exact source collision matrix

```
canonical m-lift language
=
SOURCE-BOUND

supplied fixed-m higher lift
-> GF(2)^m labelled T-join/GCC
=
SOURCE-BOUND RANDOMIZED POLY

m=1 deterministic recognition/flow
=
SOURCE-BOUND

general m>=2 constructive recognition
=
NO EXACT CLOSURE LOCATED

general m>=2 deterministic shortest-f
=
NO EXACT SOURCE CLOSURE LOCATED

additive low-rank perturbation
=
DIFFERENT REPRESENTATION

uniform cubic-lineage q_graph bound
=
NO SOURCE CLOSURE LOCATED
```

## G4 — anti-loop consequences

Do not:

- treat `lifted-graphic` in the standard literature as arbitrary `m)-lift;
- reopen the two-row `GF(2)^2` literature as if it covered the new leaf;
- claim Walsh/Bernstein structural lift theory as an optimization algorithm;
- replace appended-row lift rank by additive perturbation rank;
- infer polynomiality for unbounded `m` from a fixed finite-group GCC theorem;
- search for a generic high-`m` matroid instead of actual cubic-lineage leaves.

## Audit decision

```
PA-0013
CUBIC-LINEAGE HIGHER-LIFT
LIVE-LEAF SOURCE AUDIT
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E10A_HIGHER_LIFT_STAR_SUPPORT_PARAMETERIZATION_GATE_V1
```

The first permitted question is deliberately narrower than a generic
higher-lift solver:

> Given an explicit `m)-lift representation of a distinguished cubic-lineage
> real torso that retains the NM-0010 / NM-0012 bounded common-`f` cocycle
> spanning family, does that promise reduce shortest-`f` to
> `2^{O(m)} poly(n)` deterministic ordinary T-join instances?

If yes, the global frontier changes again from

```
"solve m>=3"
```

to

```
"how fast can q_graph grow along actual cubic-lineage live leaves,
and can an m-lift representation be constructed in time polynomial
in the original input plus 2^{O(m)}?"
```

## Scientific ceiling

```
NM-0017 ACTUAL q_graph>=3 LEAF
=
BOUND

FIXED-m SUPPLIED REPRESENTATION
=
RANDOMIZED POLY SOURCE-BOUND

DETERMINISTIC HIGHER-LIFT STAR-SUPPORT SOLVER
=
NOT YET PROVED

UNIFORM / LOGARITHMIC CUBIC-LINEAGE q_graph BOUND
=
NOT PROVED

CONSTRUCTIVE HIGHER-LIFT REPRESENTATION
=
NOT PROVED

GLOBAL SOLVER PROMOTION
=
HOLD

P_VS_NP
=
OPEN
```
