# 2026-09-15 — Logarithmic alien-constraint exact transfer PASS

Authority: `SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION`

## Why this gate exists

The Schaefer mixed-carrier barrier showed that unrestricted connected composition of the individually tractable relations `OR2` and `EVEN_XOR3` is already an NP-complete fixed Boolean constraint language. Therefore the next positive gate had to add a genuine structural restriction instead of assuming a generic polynomial sum-of-languages glue.

The CP 2024 paper *CSPs with Few Alien Constraints* gives an external theoretical reason to examine the number of alien constraints: for a Boolean Schaefer base language, the alien-constraint problem is FPT in the number of alien constraints.

TRUMP did not convert that FPT statement into a polynomial-in-input claim. Instead it froze an explicit stronger admission rule with a direct polynomial bound.

## Exact scoped mechanism

For a fixed alien relation with `q` satisfying tuples and `k` alien constraints, enumerate exactly the `q^k` choices of one satisfying tuple per alien constraint.

Reject selections that disagree on a shared variable. Every surviving selection gives explicit variable pins. Solve the remaining base instance using its exact native polynomial carrier. Replay a reconstructed SAT witness against every original relation.

Global UNSAT requires complete accounting of every alien tuple branch.

The admitted orientations are:

- `OR2` base + `EVEN_XOR3` aliens: `q=4`, require `4^k <= L`;
- affine `EVEN_XOR3` base + `OR2` aliens: `q=3`, require `3^k <= L`.

Therefore at most `L` alien tuple branches are explored and

`T_total <= L * poly(L)`.

The algorithm does not enumerate the full variable-assignment cube.

## Frozen lineage

- Schaefer barrier journal parent: `85b7e1534e3d1068d85a37169d3105b3e45d9e3c`
- preregistration: `7d96bfe6a63035d31cb8a505e69c08198dfa3b23`
- candidate: `d74c429f559bf51401c0385c5a43b972914f0d76`
- independent checker: `8f1fa4f1faa97415573894e010ce9d2599d32104`
- workflow/head at execution: `83076cbc7df5095efc315d612aa6139630350c7a`
- theorem note: `bbfe6269eae871040410168d5e8a68f0482865b3`
- result seal: `39b7a0af2c0849dcac163aba62eccf9f18963800`
- Actions run: `34911259582`
- Actions job: `104199035159`

## Independent checker result

`PASS_SCOPED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER`

All independent checks passed.

Important controls:

- OR2-base / XOR-alien positive instance was incidence-connected with cycle rank `6`;
- reverse affine-base / OR2-alien positive instance was incidence-connected with cycle rank `2`;
- both SAT witnesses replayed the original relations;
- overlap-inconsistent alien tuple selections were exercised;
- the UNSAT control accounted for every one of its four alien tuple branches;
- a budget-exceeding instance returned `OPEN_ALIEN_TUPLE_BUDGET` before enumeration;
- a tampered witness was rejected;
- candidate source contained no full-variable-cube enumeration.

Regressions remained PASS for the Schaefer mixed-carrier barrier, factorized feedback-interface portfolio, and affine wide-interface quotient.

## Meaning

This gate handles connected, cyclic mixed-carrier instances that need not have a small feedback interface, provided the exact alien tuple budget is polynomially bounded.

It does **not** solve unrestricted connected mixed CSP. Once `q^k` becomes superpolynomial and no other sealed structure applies, the Schaefer NP-complete barrier remains.

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
- finite brute-force oracle in the checker is control verification only, not asymptotic evidence

## Next open surface

`CONNECTED_MIXED_CARRIER_WITH_SUPERLOGARITHMIC_ALIEN_TUPLE_BUDGET_AND_NO_OTHER_SEALED_STRUCTURE`

Before any new gate, run anti-loop harvest for exact ways to compress or factor the alien tuple-choice space (overlap rank, dependency width, quotient of tuple selections, or source-bound alien-constraint structure). Do not introduce a generic connected mixed-carrier glue that would contradict the already sealed Schaefer barrier unless explicitly attacking the P-vs-NP-scale implication.
