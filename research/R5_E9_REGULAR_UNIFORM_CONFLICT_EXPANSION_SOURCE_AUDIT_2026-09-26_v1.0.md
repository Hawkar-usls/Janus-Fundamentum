# R5 E9 — Regular-Uniform Conflict Expansion / Critical-Set Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__DOUBLE_COUNT_LEMMA_NOT_SOURCE_CLOSED`

Immediate parent:
`PA-0022-CONTEXTUAL-CONFLICT-GRAPH-MIS-KERNELIZATION`

## G0 — exact changed object

PA-0022 imports critical-independent-set / crown reductions as known contextual
MIS-kernelization donors.

Before using them on the literal cubic Exact-One source, test whether the source
geometry can support the required positive deficiency at all.

The exact object is the 2-section / conflict graph of an r-uniform, d-regular
hypergraph, specialized afterward to the cubic source r=d=3.

For an independent set I in the conflict graph, ask for an exact lower bound on

```
|N(I)|.
```

If the source already forces expansion larger than |I|, then the classical
critical-set / crown lane is vacuous before any representation-changing
reduction.

## G1 — internal anti-duplication

Repository-first search covered:

- NM-0022 conflict-graph alpha=n/3 bridge;
- PA-0022 MIS-kernelization donor audit;
- existing matching / linear autarky and witness-dominance artifacts;
- rank-3 exact-cover / hypermatching normalization;
- Kettani associated-graph negative control.

No artifact was found proving a uniform independent-neighborhood expansion
factor for the literal 3-uniform 3-regular source conflict graph, or deriving
critical-set / crown extinction from such a factor.

## G2 — adjacent public literature

### S1 — regular-uniform strong independent sets

Cohen--Perkins--Sarantis--Tetali,
*On the number of independent sets in uniform, regular, linear hypergraphs*,
European Journal of Combinatorics 99 (2022), 103401,
arXiv:2001.00653, study weak and strong independent sets in regular uniform
hypergraphs, including the r=3 strong-independent-set regime.

This source-binds the surrounding regular-hypergraph / strong-independent-set
language.

The targeted pass did not locate the exact neighborhood-expansion statement

```
|N(I)| >= (r-1)|I|
```

for every strong independent set in every r-uniform d-regular hypergraph,
nor the specific critical-set/crown consequence used here.

Classification:

```
REGULAR-UNIFORM STRONG-INDEPENDENT-SET LANGUAGE
=
SOURCE-BOUND ADJACENT DONOR

EXACT NEIGHBORHOOD DOUBLE-COUNT / CRITICAL-SET EXTINCTION
=
NO SOURCE CLOSURE LOCATED.
```

### S2 — critical independent sets

Butenko--Trukhanov (ORL 2007) source-bind the polynomial critical-independent-set
reduction used by PA-0022.

Their machinery becomes a negative control here: if every nonempty independent
set has strictly negative difference

```
|I|-|N(I)|,
```

then the empty set is the unique maximum-difference independent set and the
reduction has no nonempty source move.

### S3 — crowns

Classical vertex-cover crown decompositions require a nonempty independent crown
C whose neighborhood/head can be saturated into C by a matching; in particular

```
|N(C)| <= |C|.
```

Therefore any source theorem forcing

```
|N(C)| >= 2|C|
```

kills the classical crown lane immediately.

## G3 — scoped question authorized

The remaining theorem target is elementary and source-specific:

> In an r-uniform d-regular source hypergraph, prove or falsify that every
> conflict-graph independent set expands by factor at least r-1.

For the cubic source this becomes:

```
|N(I)| >= 2|I|.
```

The proof, if valid, must be direct incidence counting and must not assume
linearity, girth, planarity, or a satisfiable witness.

## Audit decision

```
PA-0023
REGULAR-UNIFORM CONFLICT EXPANSION AUDIT
=
PASS_SCOPED_GAP_CONFIRMED

REGULAR HYPERGRAPH INDEPENDENT-SET LITERATURE
=
SOURCE-BOUND ADJACENT

CRITICAL-SET / CROWN THEORY
=
SOURCE-BOUND DONOR

EXACT EXPANSION / EXTINCTION LEMMA
=
NO SOURCE CLOSURE LOCATED

NEW MATH AUTHORIZED ONLY INSIDE
=
R5_E9_CUBIC_CONFLICT_INDEPENDENT_EXPANSION_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
