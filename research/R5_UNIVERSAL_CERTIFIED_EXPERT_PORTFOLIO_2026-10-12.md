# R5 — JANUS Certified Expert Portfolio: cooperative global SCL solver

Date: 2026-10-12 Europe/Kyiv. PR #516 stacked on #515, **not merged into main**.

## Precise goal
A deterministic universally polynomial-time `SolveLinearCubicXSAT` for
EVERY legal square/cubic/linear positive Exact-One system, returning
SAT+independently verified witness or UNSAT, complete, sound and with
worst-case n^{O(1)} bit complexity.

This *particular* milestone assembles a correct cooperative solver,
not that complexity theorem. `UNIVERSAL_POLY=NOT_CONSTRUCTED; P_VS_NP=OPEN`.

## Core insight: a proof-aware mixture of experts
Each module implements a **sound partial decision procedure**
`E_i(A,pins)` returning SAT with a witness, proven UNSAT, or UNKNOWN.
The top-level dispatch accepts SAT only after checking every ORIGINAL
row and pin. It accepts UNSAT only from a sound, proof-derived gate
and never treats resource limits or absent contradictions as UNSAT.

The current executable is:
`experiments/r5_universal_certified_expert_portfolio.py`,
with CI `.github/workflows/r5-certified-expert-portfolio.yml`.

Currently connected, reusing existing implementations:
1. strict source SCL validity and Boolean pin validator;
2. polynomial arithmetical contradiction `n%3!=0`;
3. zero-residual-node ExactSupportHybrid root checks:
   exact propagation, GF2 and modular/linear sound refuters;
4. optionally full GF2 Boolean degree-3 PC refutation on unpinned
   source n<=`pc3_max_n`, with INDEPENDENT GF2 recombination check;
5. bounded ExactSupportHybrid residual DAG with modular negative
   certificate checks and witness verification;
6. a COMPLETE exact AND/OR fallback that returns a SAT witness or
   an independently replayed exhaustive UNSAT proof DAG.

The system preserves `UNKNOWN` in polynomial-only mode. The
fallback proof checker is imported from the existing tested
`r5_universal_exact_support_unsat_andor_certificate.py`, rather
than implementing yet another incompatible verifier.

A few experts currently reuse submethods; this first router is a
cooperative scaffold, NOT a completed merger of literally every
Fundamentum experiment. The 3/4-cut graph interface, represented
delta-matroid lane, trade machinery, and specialized algebraic
certificates remain candidates for subsequent adapter plugins, only
where an actual all-input SOUND gate can be justified.

## Two distinct complexity/correctness theorems

**Theorem A (sound partial polynomial portfolio).**
Assume each registered partial expert is sound, deterministic and
bounded by p_i(n) bit operations, and the dispatcher runs k(n)
experts where sum_i p_i(n) is polynomial. The resulting dispatcher
also has polynomial worst-case runtime, and any SAT/UNSAT it
emits is correct. Its output alphabet may include UNKNOWN.

Current default registered polynomial set has a finite number of
passes with fixed `pc3_max_n=48` and `bounded_states=48`.
The degree-3 polynomial calculus performs O(n^3) bitset row
eliminations over O(n^3) monomial columns, with worst-case
bit time bounded conservatively by O(n^9). The fixed bounded
residual expansion retains polynomial cost; the full bounded
portfolio is a sound deterministic polynomial *partial solver*.

**Theorem B (complete portfolio conditional on coverage).**
If for EVERY legal A (and pinned self-reduction input, if allowed)
at least one *polynomially bounded* expert from A returns SAT
or UNSAT, then the finite portfolio is a sound, complete
polynomial-time solver. The condition is exactly:

  ALL_LEGAL_SCL = union_i COVERED_WITH_PROVED_POLY_TIME(E_i).

No such union-cover theorem has been proved. Empirical CI
coverage is irrelevant to that asymptotic universal claim.

**Theorem C (total exact portfolio).**
If the above bounded experts return UNKNOWN, call the existing
complete exact residual AND/OR construction, verify the resulting
original-input SAT witness or independently replay its UNSAT DAG.
This is sound and complete for all legal SCL inputs by induction
on decreasing residual clauses. However the number of distinct
residual states/proof nodes S can be exponential. Thus runtime is
  O(n^9 + S * poly(n))
with no universal n^O(1) bound on S.

The two operating modes are explicitly separate:
  `poly_only=True`  -> SAT, UNSAT, or UNKNOWN in polynomial time;
  `poly_only=False` -> SAT or UNSAT, exact total, possibly exponential.

No free-running guesses by a language-model router or probabilistic
confidence thresholds may be promoted into mathematical authority.
A transformer-style learned routing policy may optimize speed,
but cannot substitute for a proof that every input is handled
within a polynomial budget.

## Verified live independent CI replay

Workflow: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38187731590
Final status: SUCCESS. Code commit: 8aad1a60d5e493c3e36aa1d26c1eb27c09df56ac.

- E61 SAT12: polynomial budget 0 => UNKNOWN; exact mode => SAT witness.
- E61 UNSAT12: polynomial root algebra => UNSAT.
- K3,3 graph SCL27: polynomial budget 0 => UNKNOWN; exact mode => SAT.
- Petersen graph SCL45: PC3 => UNSAT, with independently
  checked GF2 coefficient-combination certificate.
- Prism5 SCL45: polynomial budget 0 => UNKNOWN; exact mode => SAT.
- Forced genuine complete SAT fallback (K3,3) => witnessed SAT.
- Pinned K3,3 SAT cases x0=0 and x0=1 both independently validated.
- Contradictory pins of two distinct 1s in one original Exact-One
  clause => UNSAT.
- Forced genuine complete UNSAT fallback (Petersen) =>
  an independent AND/OR proof of 40 states reconstructed/replayed.
- Exhausted bounded experts => UNKNOWN, **never inferred UNSAT**.

Prior failed CI #38187640483 reflected an incorrect ordering of
the prism test fixture `(rows,n)`, not a solver counterexample;
the fixed and extended run above passed. Always cite the green
run when claiming integration success.

## Path to the genuinely universal solver

1. Define a common soundness/authority contract for ALL admissible
   expert adapters: precondition, exact semantics, resource bound,
   original-instance lift of SAT witnesses, and UNSAT provenance.
2. Share verified pins, forced assignments, conflict clauses,
   proof objects and boundary signatures across experts, instead
   of serially repeating the same root work.
3. Attack hard unresolved inputs identified by this portfolio and
   find a polynomially computable discriminant/router or a new
   universally sound compression mechanism.
4. Prove a COVERAGE theorem for the union of all polynomial experts,
   or prove that their composition reduces an explicit strictly
   decreasing *global* potential in a polynomial number of steps.
5. Only after an all-input n^C bound and self-reduction proof may
   `UNIVERSAL_POLY_SOLVELINEARCUBICXSAT` be labeled CONSTRUCTED.

Scientific ledger:
  PORTFOLIO_CORRECTNESS_POLY_PARTIAL = PROVED_FROM_COMPONENTS.
  PORTFOLIO_COMPLETENESS_TOTAL_EXACT = PROVED_FROM_COMPONENTS.
  FULL_MODE_INDEPENDENT_UNSAT_ANDOR_REPLAY = VERIFIED_CI.
  PORTFOLIO_CERTIFIED_FINITE_CONTROLS = SUCCESS.
  POLYNOMIAL_EXPERTS_UNION_COVERAGE = OPEN.
  UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
  P_VS_NP = OPEN.
