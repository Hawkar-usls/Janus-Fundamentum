# C024 — Critical-Order Witness Candidate for GT Local-Resolution Robustness

**Status:** exploratory witness reconstruction / no asymptotic lower bound claimed.

## Motivation

C023 isolated the missing transfer theorem:

```text
historical graph-tautology lower bound for basic Formula Caching
+ Policy-0A one-pass local Resolution
---------------------------------------------------------------
? lower bound for JANUS-FC_local
```

It is invalid to assume that a polynomial local inference budget is harmless. A
single derived clause can remove exponentially many search states. C024 begins by
constructing and trying to destroy an explicit combinatorial witness measure.

## Critical total orders

For the smart graph-tautology CNF `GT_n`, each permutation of the vertices gives
a total-order assignment. Such an assignment:

- satisfies every transitivity clause;
- satisfies every non-minimality clause except the clause belonging to its
  minimum vertex.

Therefore there are `n!` critical assignments partitioned into `n` equal classes
of size `(n-1)!`, one class per violated minimum clause.

These assignments are a natural candidate witness family because they expose the
source of the contradiction while retaining a large symmetric space.

## Root damage function

For a clause `C`, define

```text
damage_n(C) = number of critical total orders that falsify C.
```

The executable audit enumerates every critical order for `n<=8`, independently
checks the one-failed-axiom property, replays Policy-0A's exact root local
Resolution pass, and records `damage_n(C)` for every accepted resolvent.

The first attack asks:

> Can one accepted low-support resolvent falsify almost all critical orders?

If yes, raw critical-order cardinality is too weak as a transfer invariant. If
no, the damage may admit a support-sensitive combinatorial bound.

## Required strengthening beyond the root

Even a good root bound is not enough. A lower-bound proof needs a residual-state
version that handles:

1. partial comparison assignments along the deterministic branch path;
2. unit consequences and the second propagation phase;
3. exact cache identification of residuals reached through different contexts;
4. multiple local resolvents within the addition budget;
5. repeated rediscovery of the same clause in many states;
6. normalization to the actual encoded CNF length.

A plausible state witness is the set of critical orders extending the current
comparison assignment and surviving a declared subset of residual clauses. This
proposal is not yet proved compatible with simplification or cache equality.

## Candidate bounded-damage lemma

Seek an explicit function `B(n,s,w)` such that for every accepted resolvent `C`
of width `w` involving `s` order vertices and every relevant residual state `F`,

```text
|Witness(F) \ Witness(F and C)| <= B(n,s,w),
```

and the sum of `B` over one Policy-0A pass remains too small to eliminate the
witness mass required by the Formula-Caching lower-bound induction.

A bound depending exponentially on `s` is insufficient unless the proof also
shows `s=O(log n)`; the C023 clause-shape census contains supports growing with
`n` even though most finite events have support four or five.

## Falsification conditions

The candidate measure is weakened or rejected if:

- one allowed root resolvent destroys a constant fraction approaching one;
- a residual restriction makes a small-support clause destroy all surviving
  witnesses;
- unit propagation collapses witness mass without a chargeable local event;
- exact cache equality identifies states carrying incompatible witness labels;
- the required witness representation or update cost is superpolynomial.

## Claim boundary

The critical-order audit is a finite diagnostic and may not coincide with the
historical Formula-Caching proof invariant. C024 does not yet transfer the
`GT_n` lower bound to Policy-0A, does not lower-bound clause learning, and does
not resolve P versus NP.
