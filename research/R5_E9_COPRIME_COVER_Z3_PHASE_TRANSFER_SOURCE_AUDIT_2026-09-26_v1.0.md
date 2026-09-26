# R5 E9 — Coprime-Cover Z3 Phase Transfer Source Audit

Date: 2026-09-26

Authority:
`SOURCE_AUDIT_ONLY__TRANSFER_DONOR_SOURCE_BOUND__JANUS_LABELLED_PHASE_SPECIALIZATION_SCOPED`

Immediate parent:
`PA-0025-FILTERED-HIGH-NULLITY-GRAPH-COVER-SOURCE-AUDIT`

## G0 — changed object

PA-0025 isolates the exact question whether a graph cover can repair the JANUS
Z3 phase obstruction while preserving the other filtered promises.

The precise labelled cover data are:

```
pi : Omega_tilde -> Omega
pi P_tilde = P pi
pi Q_tilde = Q pi
```

with constant fiber size m.

The phase equation downstairs is

```
phi(Pi)=phi(i)+1
phi(Qi)=phi(i)-1
```

over F_3, and the same labelled equations are imposed upstairs.

The source question is whether standard covering-space transfer already gives
the relevant obstruction persistence when m is invertible mod 3.

## G1 — internal anti-duplication

Repository-first search covered:

- R5_E9_Z3_PHASE_COBBOUNDARY_ISLAND;
- PA-0025 graph-cover/nullity audit;
- 2-lift old/new spectrum and old-kernel inheritance;
- high-girth lift donors.

No existing artifact states or proves:

```
3 does not divide m
AND
cover phase PASS
=>
base phase PASS,
```

nor the exact sharp degree-3 repair construction.

## G2 — source-bound donors

### S1 — transfer for finite-sheeted covers

Hatcher, Algebraic Topology, Section 3.G, defines transfer for an n-sheeted
cover by summing over all lifts.  The standard identity says that transfer
composed with pullback is multiplication by the covering degree.

Consequently, with coefficients in a ring where n is a unit, pullback on
cohomology is injective.

Classification:

```
FINITE-COVER TRANSFER / DEGREE MULTIPLICATION
=
SOURCE-BOUND.
```

For F_3 coefficients, this gives exactly the expected coprime-to-3 firewall at
the cohomological level.

### S2 — graph lifts as fiber permutations

Hoory, *On the Girth of Graph Lifts* (2024/2025 revision), uses the standard
description of a finite graph lift by a constant fiber and a permutation on
the fiber for each directed base edge.

This matches the JANUS labelled-cover formalism used here.

Classification:

```
FINITE GRAPH LIFT AS FIBER PERMUTATIONS
=
SOURCE-BOUND.
```

### S3 — 2-lifts and old spectral sector

Bilu--Linial and the signed-graph literature source-bind the old/new spectral
decomposition for 2-lifts.  PA-0025 already imported this.

It is relevant only to nullity accounting; it does not itself prove the Z3
phase statement.

## G3 — exact JANUS specialization

The transfer identity strongly suggests, and a direct fiber-sum proof can test,
the following statement:

```
if gcd(m,3)=1,
then
phase(base) iff phase(cover).
```

The forward direction is trivial pullback.

The reverse direction is the scoped specialization: average/sum an upstairs
phase over each fiber and divide by m in F_3.

This is best classified as a JANUS elementary corollary of source-bound transfer,
not as new cohomology theory.

## G4 — sharpness question

The transfer theorem also predicts that degree divisible by 3 is the only place
where a mod-3 obstruction can disappear.

A separate exact question remains:

> Does every phase-FAIL labelled base admit an explicit connected 3-sheeted
> labelled cover that becomes phase-PASS?

The canonical voltage assignment

```
P_tilde(i,t)=(P(i),t+1)
Q_tilde(i,t)=(Q(i),t-1)
```

is the natural candidate.

No checked source in this pass states this exact JANUS sharpness theorem in the
two-permutation perfect-kernel normalization.

## G5 — scaling corollaries to audit

Two further cover facts are elementary and must be accounted for explicitly:

1. If the lifted permutations commute, their projections commute.  Therefore
   base noncommutativity persists to every labelled cover.

2. Old rational kernel vectors lift fiber-constantly.  Hence
   `d_tilde >= d_base`.  If a family has
   `d_base=omega(log n)` and cover degree `m<=n^C`, then
   `d_tilde=omega(log(nm))`.

The first is elementary functoriality.  The second combines the source-bound
old-kernel fact with elementary asymptotic accounting.

## Audit decision

```
PA-0026
COPRIME-COVER Z3 PHASE TRANSFER
=
PASS_SCOPED_GAP_CONFIRMED

TRANSFER / DEGREE MULTIPLICATION
=
SOURCE-BOUND

GRAPH-LIFT FIBER-PERMUTATION FORMALISM
=
SOURCE-BOUND

COPRIME-TO-3 PHASE PERSISTENCE
=
AUTHORIZED JANUS SPECIALIZATION

SHARP CONNECTED 3-COVER REPAIR
=
AUTHORIZED KILLER TEST

POLYNOMIAL-DEGREE COVER SUPERLOG ACCOUNTING
=
AUTHORIZED COROLLARY CHECK

NEXT
=
R5_E9_COPRIME_COVER_PHASE_PERSISTENCE_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN
```
