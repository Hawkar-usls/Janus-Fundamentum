# C049.1 Phase B1 — hardened compact B-trajectory normal form

```text
B1 = IMPLEMENTED / HARDENED / REVIEW_PENDING
B2 = PENDING
P_VS_NP = OPEN
```

This stacked draft implements only the compactification normal form `tau` from Jeong–Kim–Oum, `arXiv:1507.02184v4`, Section 3.1 and the length bounds in Lemmas 3.1–3.2.

A statistic is a triple `(L,R,lambda)` with `L,R <= B`. A valid `B`-trajectory has increasing `L`, decreasing `R`, and `R(first)=L(last)`. Compactification repeatedly:

1. removes one of two consecutive equal statistics;
2. removes the interior of a constant-`(L,R)` interval when every intermediate `lambda` lies between the endpoint values.

## Hardened certificate

The frozen artifact contains two complete transformed-basis proof cases at the minimum and maximum audited caps, each with the input trajectory, compact output, and every removal step. A separate digest-bound audit record is independently regenerated for all 120 deterministic cases. Each step binds:

```text
rule
start / end indices in the current sequence
before length
removed entries
after length
after-sequence digest
```

The outer artifact and every proof case have independent SHA-256 integrity fields.

## Independent verifier

The verifier does not import the producer or its core. It independently:

- canonicalizes every GF(2) subspace;
- rejects vectors outside `B` before RREF, including cancelling invalid rows;
- checks the trajectory endpoint and monotonicity conditions;
- replays every supplied removal step;
- computes the normal form again with reverse reduction priority;
- checks equality of replayed, alternative, and claimed outputs;
- checks `tau(tau(Gamma)) = tau(Gamma)`;
- checks exact width preservation;
- checks `length(tau(Gamma)) <= (2 dim(B)+1)(2k+1)`;
- exhaustively checks confluence on 6,684 scalar typical-sequence fixtures;
- independently rejects six malformed-trajectory controls.

## Frozen audit

```text
120 independently regenerated audit trajectories
2 full proof-carrying transformed-basis trajectories
17 replayed certified removal steps
741 total regenerated removal steps
48 transformed-basis flag trajectories
6 malformed controls
6,684 exhaustive scalar confluence checks
0 failures
```

Frozen integrity:

```text
1167133466834127dbaf4c4412450139bc8eabded3f31e6b4fda38f72a239dd6
```

The workflow additionally mutates one trace, recomputes both the case and outer digests, and requires the independent verifier to reject it. Thus rejection cannot rely only on the outer hash.

## Exact boundary

B1 closes only canonical compactification. It does not implement:

```text
extension preorder
domination
up_k
full sets
expand / join / shrink
iterative compression
FOUND_LAYOUT
complete NO_LAYOUT_AT_CAP
```

The next gate is:

```text
C049.1_PHASE_B2_EXTENSION_PREORDER_DOMINATION_AND_UP_K
```

Until B2–B4 and the full-set completeness theorem are implemented:

```text
OPEN_TRAJECTORY_ENGINE_INCOMPLETE
```

may not be promoted to `NO_LAYOUT_AT_CAP`.
