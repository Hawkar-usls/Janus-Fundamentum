# R5 E10A — Nondistinguished Torso / Virtual-Interface Propagation Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__2SUM_DELTA3_YSUM_MUST_BE_SEPARATED`

Immediate predecessor:
`NM-0013-ANCHORED-COCYCLE-SWITCHING-CONSTANT-SUPPORT-TJOIN-SOLVER`

## G0 — changed scope

NM-0013 closes the distinguished real-torso optimization gate.

The next unresolved object is a **nondistinguished** decomposition side:
the original parent distinguished element `f` does not lie in its real ground set `A`.

NM-0010 gives a parent cocycle-star basis
`D_i` with `f in D_i` and `|D_i|=4`.
After puncturing to `A`,

```
C*(P)|A = span {D_i intersect A},
|D_i intersect A| <= 3.
```

What is not source-bound is whether those real-side generators lift through
the virtual 2/3-sum separator to a uniformly bounded cocycle generating family
of the actual component/torso.

The exact audit target is:

```
CUBIC STAR PUNCTURE
    ->
NON-f REAL-SIDE SUPPORT <=3
    ->
ADD ONE ROOTED VIRTUAL 2/3-SUM INTERFACE
    ->
UNIFORM BOUNDED COCYCLE GENERATORS
    ->
BOUNDARY WITNESS / CONDITIONED-COST RECONSTRUCTION.
```

## G1 — internal anti-duplication

No prior Fundamentum artifact proves a bounded-support lift for the
**nondistinguished** real side plus a virtual 2/3-sum interface.

Do not reuse as if they settled this scope:

- NM-0012: distinguished real restriction, deletion-only;
- NM-0013: common-f anchored support-seven normalization;
- NM-0011: arbitrary minor universality, which may use contraction;
- PA-0005: generic two-row graph-lift;
- PA-0007: literal-placement invariant only.

## G2 — canonical source language

The exact external language is standard binary matroid/code decomposition:

- 2-sum from an exact 2-separation;
- ordinary 3-sum / Delta-sum across a common triangle;
- dual 3-sum / Y-sum across a common triad;
- puncturing vs shortening / deletion vs contraction;
- cycle/cocycle orthogonality across a binary separator.

These three sum types must not be conflated.

## G3 — source exhaustion

### S1 — 2-sum semantics are source-bound

Kashyap's code-decomposition exposition proves that an exact 2-separation can
be decomposed in polynomial time into two pieces equivalent to proper minors;
the parent can be reconstructed by 2-sum.

Thus the separator semantics and polynomial construction are known.

What is not supplied there is the JANUS-specific statement that a punctured
support-at-most-three parent cocycle generator has a bounded-support lift in the
component cocycle space.

Classification:
`2SUM_DECOMPOSITION_SEMANTICS_SOURCE_BOUND__BOUNDED_COCYCLE_LIFT_GAP_SURVIVES`.

### S2 — ordinary 3-sum / Delta-sum

Kashyap Definition 4.2 uses a common three-coordinate circuit.
The equivalent form states that the shared `111` word is a minimal codeword
and that the component restriction onto those three coordinates is all
`GF(2)^3`.

Theorem 4.11 states that if
`C=C1 plus_3 C2`, then the displayed partition is an exact 3-separation; if
the parent is 3-connected, `C1,C2` are equivalent to proper minors.

For cocycles, every trace on the shared triangle has even parity because every
binary circuit and cocycle intersect evenly.

This source-binds:

```
Delta-interface trace of a cocycle
in {000,110,101,011}.
```

It does **not** itself state the JANUS boundary-lifting theorem from the
punctured NM-0010 star generators.

Classification:
`DELTA3_INTERFACE_SEMANTICS_SOURCE_BOUND__EXACT_LIFT_GAP_SURVIVES`.

### S3 — dual 3-sum / Y-sum is a distinct operation

Kashyap explicitly notes that ordinary 3-sum is not closed under duality.
Definition 4.3 introduces the dual 3-sum, and Proposition 4.9 identifies
duality:

```
(C plus_3 C')^perp
=
C^perp barplus_3 C'^perp.
```

Truemper calls these Delta-sum and Y-sum.

Therefore an ordinary-triangle cocycle argument may not be silently reused on
a Y-interface.

Classification:
`Y3_DUAL_INTERFACE_SEMANTICS_SOURCE_BOUND__SEPARATE_PROOF_REQUIRED`.

### S4 — contraction support blow-up is source-bound

Jackson's Lemma 2.3 gives the exact cocycle-basis update:

- deletion removes the deleted coordinate from cocycles;
- contraction requires symmetric differences with a selected basis cocycle.

Therefore

```
component is a minor
NOT IMPLIES
parent small cocycles remain small in component.
```

This blocks the shortcut
`minor provenance -> bounded component cocycle support`.

Classification:
`DEL_CONTRACTION_COCYCLE_ASYMMETRY_SOURCE_BOUND_FIREWALL`.

### S5 — induced decompositions do not close the bounded-support question

Truemper's decomposition-conditions theory gives sufficient conditions under
which a decomposable minor induces a decomposition of a containing matroid and
supports decomposition algorithms.

It does not provide a uniform constant-support theorem for the cocycle lifts
created by virtual 2/3-sum elements.

Classification:
`INDUCED_DECOMPOSITION_SOURCE_BOUND__NO_BOUNDED_SUPPORT_COLLISION`.

## G4 — scoped decision

Known:

```
2/Delta3/Y3 decomposition semantics
=
SOURCE-BOUND

component/minor relations
=
SOURCE-BOUND

deletion/contraction cocycle behavior
=
SOURCE-BOUND

finite-interface decomposition machinery
=
SOURCE-BOUND
```

No exact collision located for:

```
punctured NM-0010 star support <=3
+
one rooted virtual interface
->
uniform bounded cocycle generating family
with exact boundary reconstruction.
```

Therefore:

```
PA-0009-CUBIC-ORIGIN-NONDISTINGUISHED-TORSO-VIRTUAL-INTERFACE-PROPAGATION
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E10A_NONDISTINGUISHED_TORSO_BOUNDARY_LIFTING_GATE_V1
```

## Mandatory proof split

Any positive theorem must prove separately:

1. 2-sum;
2. ordinary Delta 3-sum;
3. dual Y 3-sum;
4. restriction-map kernel/injectivity statement;
5. trace realizability/surjectivity statement;
6. witness and conditioned interface-state reconstruction.

Do not promote the heuristic bounds before these are proved.

## Firewalls

Do not:

- infer bounded support from "the component is a minor";
- use the ordinary triangle parity argument for Y-sums;
- assume restriction-map injectivity in Y-sums;
- reopen generic Bentert/PIT;
- claim a full cubic decomposition solver from one rooted-interface lemma;
- claim P=NP.

## Scientific ceiling

```
PA-0009
=
PASS_SCOPED_GAP_CONFIRMED

2SUM / DELTA3 / Y3 SOURCE SEMANTICS
=
BOUND

UNIFORM BOUNDARY-LIFTING CONSTANT
=
NOT YET PROVED IN THIS AUDIT

FULL DECOMPOSITION PROPAGATION
=
OPEN

P_VS_NP
=
OPEN
```
