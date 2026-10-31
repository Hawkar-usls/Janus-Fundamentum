# R5 E9 — Polynomial-Degree 2-Group Fixed-Girth Cover Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__RESIDUAL_2_AND_P_GIRTH_FIXING_DONORS_SOURCE_BOUND__POLY_DEGREE_FIXED_GIRTH_COMBINATION_SCOPED`

Immediate predecessor:
`NM-0029-COPRIME-COVER-PHASE-PERSISTENCE`

## G0 — exact changed object

NM-0029 proves that every labelled cover of degree coprime to three preserves
the Z3 phase obstruction, and in particular every 2-group / 2-power cover does.
It also proves upward persistence of noncommutativity and preservation of
superlog rational nullity under polynomial cover degree.

The changed question is therefore purely geometric/quantitative:

> Given a connected bounded-degree edge-coloured incidence graph H on n
> vertices and a fixed target girth g (here g=10), can one construct a
> 2-power-sheeted labelled graph cover with girth at least g and cover degree
> polynomial in n?

The polynomial degree requirement is essential. Mere existence of arbitrarily
large-girth finite covers is insufficient for the nullity scaling gate.

## G1 — internal anti-duplication

Repository-first search covered:

- PA-0025 graph-cover/nullity audit;
- PA-0026/NM-0029 cover transfer and phase persistence;
- 2-lift old/new spectrum;
- high-girth cover donors.

No artifact was found proving a polynomial-in-base-size bound for fixed target
girth using a 2-group / 2-power cover.

## G2 — source-bound donors

### S1 — free groups are residually finite p-groups

Free groups are residually finite p-groups for every prime p.  This is a
classical fact; modern open references explicitly restate it.

Consequently, for every finite set W of nontrivial reduced words in a fixed
free group, there is a finite p-group quotient in which every word in W remains
nontrivial (take a finite direct product of individual separating quotients).

Classification:

```
FREE GROUP RESIDUAL-p
=
SOURCE-BOUND.
```

### S2 — p-group / girth-fixing covers

Koberda--Suciu explicitly use finite p-group covers of graphs and call covers
whose base graph attains a prescribed girth threshold "girth-fixing p-covers".

This source-binds the qualitative p-cover mechanism.

Classification:

```
FINITE p-GROUP GIRTH-FIXING COVER LANGUAGE
=
SOURCE-BOUND.
```

### S3 — voltage / permutation lift formalism

Standard voltage-graph and modern graph-lift sources represent a finite cover
by a constant fibre and edge permutations / voltages.  Hoory's graph-lift work
uses exactly this language while studying girth.

Classification:

```
VOLTAGE / FIBRE-PERMUTATION COVER FORMALISM
=
SOURCE-BOUND.
```

## G3 — what the sources do NOT automatically give

The qualitative statement

```
for every finite graph and fixed g
there exists a finite p-cover of girth >= g
```

does not by itself bound the cover degree as the base graph varies.

Likewise, iterating arbitrary 2-lifts can make girth grow, but a sequence of
many 2-lifts may have exponential total degree.

For the JANUS nullity accounting we specifically need, for fixed g=10,

```
cover_degree <= n^C
```

for one constant C independent of the input graph.

No located source in this targeted pass states this exact quantitative theorem
for arbitrary growing bounded-degree bases and 2-group deck groups.

## G4 — finite short-word pattern observation

For fixed g, every nonbacktracking closed walk of length <g determines a
nontrivial reduced word of length <g in the oriented base-edge labels.

Up to renaming the at most g-1 edge variables, there are only finitely many
such reduced word patterns.

Residual-2 therefore supplies one fixed finite 2-group K_g such that none of
those finitely many word patterns is an identity law on K_g.

This observation combines only source-bound residual-2 with finiteness at
fixed g.  The quantitative use of repeated independent K_g coordinates is the
scoped theorem target authorized below.

## G5 — authorized theorem target

A legitimate new theorem may prove:

```
FIXED g, fixed Delta
=>
every n-vertex max-degree-Delta graph
has a regular 2-group cover
with girth >= g
and degree n^O_{g,Delta}(1).
```

The preferred proof route is:

1. list all nonbacktracking closed walks of length <g; there are O(n) for fixed
   g,Delta;
2. use random K_g edge voltages;
3. every fixed short walk has a constant positive probability of receiving
   nonidentity voltage;
4. use O(log n) independent voltage coordinates, giving deck group K_g^t;
5. union-bound all short walks;
6. optionally derandomize by conditional expectation because g and K_g are
   fixed constants.

A connected component of the derived regular cover is itself a connected
2-power-sheeted cover with the same girth lower bound.

## G6 — important remaining odd-hole issue

A cover of girth strictly larger than ten need not contain an incidence
10-cycle, so it need not supply the conflict C5 required by the exact NM-0028
sparse-hole control.

Therefore even a PASS on the polynomial 2-group girth theorem does NOT yet
complete the filtered survivor family.

The separate remaining obligation is:

```
preserve / force some incidence cycle of length 2 mod 4,
preferably a 10-cycle,
while eliminating all shorter cycles.
```

## Audit decision

```
PA-0027
POLY-DEGREE 2-GROUP FIXED-GIRTH COVER AUDIT
=
PASS_SCOPED_GAP_CONFIRMED

RESIDUAL-2 FREE GROUPS
=
SOURCE-BOUND

p-GROUP GIRTH-FIXING COVER LANGUAGE
=
SOURCE-BOUND

VOLTAGE / GRAPH-LIFT FORMALISM
=
SOURCE-BOUND

POLYNOMIAL COVER DEGREE FOR FIXED GIRTH
=
NO SOURCE CLOSURE LOCATED

NEW MATH AUTHORIZED
=
R5_E9_POLYSIZE_2GROUP_FIXED_GIRTH_COVER_GATE_V1

10-CYCLE / ODD-HOLE PRESERVATION
=
SEPARATE OPEN OBLIGATION

D1
=
EMPTY

P_VS_NP
=
OPEN
```
