# BH-Q2 — Buzz/Physarum Proof-Carrying Residual Singularity

Status: **prospective finite calibration experiment**.  This is not a P-vs-NP theorem.

## Lineage

This experiment formally lifts an older JANUS architecture:

- Physarum/Slime: reinforce promising routes and let weak routes evaporate;
- black-hole layer: compress/attract search around capture rings and singularity routes;
- pre-collapse memory: preserve route state before a collapse boundary;
- HAWKING_ESCAPE / GRAVITY_SLINGSHOT / COOPER_DETACH: leave a bad or depleted region;
- Fundamentum: replace heuristic survival with an exact proof-carrying reuse gate.

Project-level names:

- **PHYSARUM** = inward candidate-route finder;
- **BUZZ** = outward witness/proof-return guard;
- **SINGULARITY** = one certified quotient representative.

The implementation names do not claim that historical code contained a `BuzzLightyear` class.  `Buzz` is the recovered project metaphor for the return-path scout.

## Frozen law

> **NO RETURN PATH => NO ABSORPTION.**

A cheap similarity, signature collision, embedding, heuristic score, or Physarum route can never authorize a cache merge.

## Q2 equivalence candidate

Q0 admits exact CNF equivalence under variable renaming.

BH-Q2 tests a strictly larger reversible transformation family:

```text
source variable x_i -> target variable x_j or NOT x_j
```

with a bijection on variables.  Equivalently, it tests exact equivalence under a **signed variable permutation**.

This transformation preserves SAT and gives an explicit reversible assignment map.  BH-Q2 still requires exact CNF equality after applying the map.

## Physarum inward path

A cheap signed-permutation-invariant profile is used only to choose a candidate capture ring:

- multiset of clause widths;
- for each variable, the unordered pair of its positive/negative occurrence-count vectors by width;
- multiset of those variable profiles.

A collision means only `EVENT_HORIZON_SEEK`.  It is not evidence of equivalence.

## Event-horizon canonicalization

BH-Q2 builds a signed literal/clause incidence structure:

- one node for each positive and negative literal;
- one complement edge between the two literals of each variable;
- literal-to-clause incidence edges;
- clause width as a clause-node type.

Deterministic color refinement is run on this structure.  BH-Q2 uses the signed quotient only when:

1. every variable pair has a unique unordered pair-color;
2. the two literal colors inside every variable pair are distinct, so orientation is canonical.

Otherwise it falls back to Q0.  If Q0 is also ambiguous it falls back to exact byte equality.

## Buzz return certificate

For every proposed absorption `F -> S` BH-Q2 constructs:

- the explicit signed variable map `F -> S`;
- its exact inverse `S -> F`;
- exact replay `map(F) == S`;
- exact reverse replay `inverse(S) == F`;
- literal round-trip checks for every `+x_i` and `-x_i`.

Only then may the Boolean cache result be reused.

Failure at any return check is `HAWKING_ESCAPE`: keep the residual explicit.

A dedicated self-test additionally transports a real satisfying assignment through a signed map and back.

## Calibration freeze

Only already-visible graph-tautology orders `GT_3..GT_9` are admitted in this run.

No new untouched holdout may be inspected.

Required comparison with Q1:

- same Boolean answer on every order;
- BH-Q2 residual states must not exceed Q1 residual states;
- all distinct absorptions require exact Buzz replay;
- all costs are reported;
- a zero-compression result is admissible and informative.

Tracked metrics include:

- residual states;
- singularity entries;
- absorption hits;
- bytewise-distinct absorptions;
- absorptions using at least one polarity flip;
- Physarum signature checks;
- event-horizon bucket collisions;
- Buzz return checks/passes;
- HAWKING_ESCAPE count;
- signed-refinement edge visits;
- Q0-fallback refinement edge visits;
- resolution attempts/additions.

## Claim boundary

Even a successful finite compression result establishes only that this signed quotient compresses these frozen calibration instances while preserving the tested exact replay contract.

It does **not** establish:

- a polynomial number of singularities for general SAT;
- polynomial total absorption/canonicalization cost;
- P = NP;
- P != NP.

`P_VS_NP = OPEN`.
