# 2026-09-15 — Bicameral overwidth cut-support carrier v1.1 PASS

Authority: `SCOPED_HQ_JOURNAL__NO_GLOBAL_PROMOTION`

Verdict:

`PASS_SCOPED_BICAMERAL_OVERWIDTH_CUT_SUPPORT_INTERSECTION_CARRIER_V1_1`

Actions: run `34916790947`, job `104216055469`, conclusion `SUCCESS`.

## What changed

The parent canonical-mincut line already finds an overwidth cut in polynomial time and refuses raw conditioning when `2^k > L`. The frozen killer control has `k=20`, raw branch budget `1,048,576`, and zero parent branch enumerations.

This successor does not enumerate that cube. For the strict class in which deleting the canonical cut leaves one explicit relation per constraint-bearing component, it projects each relation's existing tuple rows onto the full cut and intersects those projected supports.

On the frozen overwidth control the two support sizes are the order-invariant multiset `{3,4}` and their exact intersection contains one cut state. The candidate reconstructs one original tuple from each relation and verifies the combined original witness. Raw `2^k` enumeration, Cartesian products, generic transfer calls, and SAT-solver invocations are all zero.

An empty-support control returns `EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION`. A multi-relation cut component remains `OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER`. Hint injection and provenance tampering are rejected.

## First-run failure preserved

Run `34916573617` remains an immutable `FAIL_OR_OPEN_BICAMERAL_CUT_SUPPORT_CARRIER`. It failed on two checker/control assumptions, not on the positive carrier:

1. ordered support-size expectation `[3,4]` versus canonicalized `[4,3]`;
2. a malformed `PARTIAL_CUT_VISIBILITY` control that did not isolate the intended reason.

v1.1 keeps the candidate bytes unchanged and requires the old v1 checker to continue failing.

## New structural lemma

`GLOBAL_MINCUT_SINGLETON_COMPONENT_FULL_CUT_VISIBILITY`

If `B` is globally minimum among variable-only cuts over all constraint-node pairs and deleting `B` leaves singleton relation components, then every singleton relation exposes every variable in `B`. Otherwise the variables it shares with the rest form a strict subset of `B` that itself separates that relation from another constraint, contradicting global minimality.

This means the discarded partial-visibility control was incompatible with the other frozen scope premises. Full-cut visibility is derived rather than separately trusted.

## Exact theorem shape

For component relations `R_i(B,U_i)` with pairwise-disjoint private variables, define

`P_i = projection_B(R_i)`

and

`H = intersection_i P_i`.

Then within the frozen scope:

`SAT(F) iff H is nonempty`.

Each `P_i` is built only from explicit input rows, so `|H| <= min_i |P_i| <= explicit tuple rows <= O(L)`. A common state reconstructs an original witness from one stored input row per component; empty intersection gives exact scoped UNSAT.

## What is now the real blocker

The blocker moves inward again. A singleton explicit relation can expose its cut support directly. A component containing two or more relations cannot, in general, obtain its exact boundary relation by simple row projection; naive join/project elimination may blow up.

The next admissible gate is therefore:

`TRUMP_BICAMERAL_COMPONENT_BOUNDARY_RELATION_OR_AFFINE_QUOTIENT_INDUCTION_FALSIFIER_GATE`

Priority order:

1. reuse the sealed affine-syndrome quotient when exact factor-through adequacy can be derived from the raw component semantics;
2. otherwise try a factorized/bounded join-project carrier with an original-input polynomial output bound;
3. otherwise another preregistered exact boundary quotient;
4. otherwise remain `OPEN`.

Do not repeat canonical mincut discovery, fixed-size separator enumeration, or singleton support intersection as the current blocker.

Firewalls unchanged:

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `ARBITRARY_UNSEEN_INVARIANT_DISCOVERY = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
