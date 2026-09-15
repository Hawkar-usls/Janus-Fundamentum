# TRUMP — Logarithmic Alien-Constraint Exact Transfer Theorem

Date: 2026-09-15

Authority: `SCOPED_THEOREM__NO_GLOBAL_PROMOTION`

## Scope

This theorem concerns two fixed Boolean mixed-language orientations:

1. base relation language `OR2 = {01,10,11}` with alien relation `EVEN_XOR3 = {000,011,101,110}`;
2. base relation language `EVEN_XOR3` with alien relation `OR2`.

The base language is solved by its native exact polynomial carrier after explicit variable pins are added.

Let `k` be the number of alien constraints and let `q` be the number of satisfying tuples of the fixed alien relation. Thus `q=4` for `EVEN_XOR3` aliens and `q=3` for `OR2` aliens.

Admission requires

`q^k <= L`,

where `L` is the frozen original encoded input-length parameter of the instance contract.

## Exactness

Write

`F = Base AND R_1 AND ... AND R_k`,

where every `R_i` is an alien constraint using the same fixed alien relation `R`.

Every satisfying assignment of `F` induces one satisfying tuple `t_i in R` for every alien constraint. Conversely, choose one satisfying tuple of every alien constraint. If the chosen tuples disagree on a shared variable, that tuple selection cannot extend to a global assignment and is rejected. Otherwise the tuple selection induces a consistent partial assignment `pi` to all variables touched by alien constraints.

Therefore

`SAT(F) <=> exists (t_1,...,t_k) in R^k such that the selections are overlap-consistent and SAT(Base | pi)`.

There are exactly `q^k` tuple selections before overlap rejection.

For an accepted branch, the exact native base solver is run under the pins `pi`. A native SAT witness combined with the pins is replayed against every original base and alien relation. Hence SAT reconstruction is exact.

For UNSAT, every one of the `q^k` tuple-selection branches must be accounted for as either overlap-inconsistent or exact native-base UNSAT. Therefore no missing alien tuple can hide a satisfying assignment.

## Polynomial lifecycle

By admission,

`q^k <= L`.

Each tuple-selection branch performs:

- overlap consistency over a polynomially encoded set of scoped variables;
- construction of explicit pins;
- one native polynomial base solve;
- polynomial witness reconstruction and original-relation replay;
- or a polynomial branch-rejection receipt.

Thus

`T_total <= q^k * poly(L) <= L * poly(L) = poly(L)`.

For global UNSAT, at most `q^k <= L` branch receipts are serialized, each of polynomial size, so certificate/replay bytes also remain polynomial.

The algorithm enumerates alien relation tuples only. It does not enumerate the full assignment cube of the instance variables.

## Why this is a strict extension rather than the unrestricted mixed case

The preceding Schaefer barrier established that unrestricted connected instances over the fixed pair `{OR2, EVEN_XOR3}` form an NP-complete Boolean constraint language. This theorem does not remove that barrier. It admits only instances whose alien tuple-selection count is polynomially bounded by the original input length.

The incidence graph may nevertheless be connected and contain multiple cycles. No small feedback-interface or disconnected-factorization assumption is needed for this gate.

## Relation to published few-alien-constraints theory

Jonsson, Lagerkvist and Osipov, *CSPs with Few Alien Constraints* (CP 2024), prove that when the Boolean base language is Schaefer, CSP with a parameterized number of arbitrary Boolean alien constraints is FPT in the number of alien constraints.

That published result motivates and cross-checks this scoped direction, but the polynomial-in-`L` claim here does not infer polynomiality from an unspecified FPT function. It follows directly from the explicit finite relation tuple counts and the frozen admission `q^k <= L`.

## Frozen lineage and execution

- Schaefer barrier journal parent: `85b7e1534e3d1068d85a37169d3105b3e45d9e3c`
- preregistration: `7d96bfe6a63035d31cb8a505e69c08198dfa3b23`
- candidate implementation: `d74c429f559bf51401c0385c5a43b972914f0d76`
- independent checker: `8f1fa4f1faa97415573894e010ce9d2599d32104`
- workflow/head at execution: `83076cbc7df5095efc315d612aa6139630350c7a`
- Actions run: `34911259582`
- Actions job: `104199035159`
- run conclusion: `success`

The checker independently verified exact SAT/UNSAT control truth, original witness replay, complete UNSAT branch accounting, overlap inconsistency handling, connected multi-cycle incidence controls, over-budget fail-closed behavior, absence of candidate full-variable-cube enumeration, and the scientific firewalls.

Regression checks remained green for the Schaefer mixed-carrier barrier, the factorized-feedback portfolio theorem, and the affine wide-interface quotient theorem.

## Verdict

`PASS_SCOPED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER`

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- unrestricted connected mixed-carrier NP-complete barrier remains unchanged
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
- finite control brute force in the independent checker is implementation cross-check only and is not used in the asymptotic proof
