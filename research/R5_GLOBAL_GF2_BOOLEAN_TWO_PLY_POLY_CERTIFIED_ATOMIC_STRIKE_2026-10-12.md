# R5 — All-Source Polynomial Boolean Closure: Certified Two-Ply Proofs and Snark Frontier

Date: 2026-10-12, Europe/Kyiv.
Source branch: `research/r5-cubic-flow-smith-pair-20261011`,
stacked DRAFT PR #516. Main remains unchanged.

## Single scientific goal

Construct a deterministic TOTAL solver for EVERY legal square/cubic/linear
Positive Exact-One SAT source A, returning original SAT+witness or verified
UNSAT, with one UNIFORM worst-case n^C BIT-time bound. Special families,
finite passes, polynomially bounded-but-UNKNOWN partial experts, and an
exponential exact fallback do NOT meet this target.

**UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED. P_VS_NP = OPEN.**

## 1. Existing one-round fixed-point baseline was VERIFIED, not rewritten

Frozen predecessor `experiments/r5_universal_certified_gf2_boolean_fixedpoint_closure.py`
already proves a polynomial, source-replayed least fixed point for:
  (a) ALL GF2 affine unit equations forced by ORIGINAL Exact-One source
      clauses plus admitted pins, with explicit source-row XOR proofs;
  (b) every Boolean Exact-One clause unit consequence or conflict,
      with independent original source clause replay.

At most n new pins, hence polynomial rounds. It is NOT complete:
connected atomic Holyer K4 SAT18 and Petersen UNSAT45 have zero
unconditional forced literal; both return UNKNOWN with no pins.
Old CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38283160375
SUCCESS.

The original GF2 parity relaxation always accepts the all-one vector
on unpinned positive three-literal rows, so linear consistency alone
cannot decide general Boolean Exact-One satisfiability.

## 2. First polynomial improvement: explicit single-literal discharge

New `experiments/r5_universal_certified_failed_literal_boolean_closure.py`.
For any source variable x_i and bit b:
  run full predecessor polynomial GF2/Exact-One fixed point under
  TEMPORARY assumption x_i=b, with all independent source proof rows.

If the conditional source returns verified UNSAT, then the original
source implies x_i=1-b. Both verified branches UNSAT prove original
UNSAT because x_i has exactly two Boolean values; a verified SAT
witness in either branch proves original SAT. Otherwise UNKNOWN.

Repeat accepted forced pins until no more. This can perform
at most n accepted unconditional pins and at most 2n² conditional
fixed-point probes; every branch and assumption discharge has an
independent original-source certificate verifier. Conservative
polynomial worst-case total and checked-certificate cost O(n^8)
bit operations for this implementation (not an optimized bound).
Importantly this is NOT recursive arbitrary-depth backtracking.

Original independently certified 9-family CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38285447807
SUCCESS.

| SCL source | True decision | Single-ply status |
|---|---|---|
| K4 18 | SAT | UNKNOWN |
| K3,3 27 | SAT | UNKNOWN |
| prism3 27 | SAT | UNKNOWN |
| prism5 45 | SAT | UNKNOWN |
| Petersen45 | UNSAT | UNKNOWN |
| bridged Holyer45 | UNSAT | UNSAT, zero probes (GF2 root) |
| Fano7 | UNSAT | UNSAT, 4 probes, two passes |
| E61 SAT12 | SAT | SAT via certified root |
| E61 UNSAT12 | UNSAT | UNSAT via certified root |

Explicit forged nested GF2 XOR proof is rejected by the checker.
Main `SolveLinearCubicXSAT_Portfolio` includes the bounded,
proof-checked single-literal module after earlier exact root
experts, using source size guard `failed_literal_max_n=45`
(0 disables), and always retains UNKNOWN if inconclusive.
Focused integration + old portfolio regressions:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38285477526
SUCCESS.

## 3. NEW: polynomial two-ply proof closure REALLY DECIDES PETERSEN

Executable source:
`experiments/r5_universal_gf2_boolean_two_ply_lookahead_probe.py`.
For any currently unresolved source with first-ply UNKNOWN,
try each value b for one additional original Boolean variable,
and under EACH condition run the complete polynomial
single-literal source closure described above. No level
is allowed to grow as a function of input size; only TWO
nested conditional levels are used. SAT proof is always
a full original 0/1 witness; UNSAT uses 2 independently
source-replayed conditional UNSAT proof trees under
`x_i=0` and `x_i=1`. No modulo nonzero guessing,
no unproved exact support, no Complete_ANDOR fallback.

A conservative uniform total bound O(n^11) bit operations for
this FIXED-DEPTH code (it is loose, but a genuine fixed exponent)
is obtained by multiplying the polynomial number of variable
choices by the polynomial single-ply closure and independent
source certificate replay. When a refuted branch could derive
more facts but the optional diagnostic does not iterate them,
it may return UNKNOWN; this weakens coverage, not soundness.

Observed original source controls:

| Source | One-ply verdict | Two-ply | Outer calls |
|---|---|---|---:|
| K4 Holyer SCL18, true SAT | UNKNOWN | SAT + original witness | 3 |
| K3,3 Holyer SCL27, true SAT | UNKNOWN | SAT + original witness | 3 |
| Triangular prism SCL27, true SAT | UNKNOWN | SAT + original witness | 3 |
| Petersen Holyer SCL45, true UNSAT | UNKNOWN | UNSAT, both source conditional proof trees replayed | 3 |

CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38285739013
SUCCESS.

**IMPORTANT SAT/UNSAT scientific verdict:** Petersen's original graph is
bridgeless and its Holyer SCL Tanner graph has edge connectivity 3.
It is a genuine prior atom that neither the zero-budget hybrid root
nor unpinned GF2/Boolean fixedpoint resolved. Here, a FIXED 2-ply
original-source proof does refute it in polynomial work, with no
need for PC3, symmetry, imported graph identity or exponential DAG.

Real common Portfolio has opt-in/guarded polynomial
`two_ply_max_n=45` (default enabled for sources <=45, 0 disables)
and only calls it after prior cheaper bounded experts return UNKNOWN.
It independently replays each nested source proof before accepting
SAT or UNSAT and preserves an exact `two_ply_certificate` in its
result. It does NOT interfere with isolated MOD9/Tanner/ANDOR
historical provenance tests because those tests explicitly disable
the new lane where the old expert label is the tested property.

Exact zero-search ablation with PC3/Tanner/twoport/ANDOR disabled:
K4 and Petersen both return UNKNOWN with two_ply_max_n=0;
with two_ply_max_n=45 and identical other settings:
  K4 SAT original witness,
  Petersen UNSAT with both original nested conditional refutations.
The source code independently replays every accepted certificate
and tests a TAMPERED nested Petersen branch proof, which is rejected.
Integrated CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38286028103
SUCCESS.

## 4. Growing snark challenge remains UNRESOLVED

Independent adverse family control:
`experiments/r5_universal_two_ply_flower_first_branch_probe.py`.
Original source J5 SCL90 and J7 SCL126 are known UNSAT
Isaacs flower snarks. Each source was source-checked and a
single-ply root was independently verified UNKNOWN.

For FIRST original source variable x_0 ONLY, both branches
x_0=0 and x_0=1 produced UNKNOWN even after running
the full certified single-ply closure inside each branch:

  J5: first x0=0 branch UNKNOWN after 178 probes;
      first x0=1 branch UNKNOWN after 166 probes.
  J7: first x0=0 branch UNKNOWN after 250 probes;
      first x0=1 branch UNKNOWN after 238 probes.

https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38286461913
SUCCESS, two independent jobs.

**CRITICAL SCOPE:** This does NOT refute completeness of the
entire two-ply routine, because it tests only the first outer
variable. Other outer variables might produce a useful conditional
SAT witness or dual UNSAT proof. Calling this
`GLOBAL_TWO_PLY_COUNTEREXAMPLE` would be FALSE. To prove
such a counterexample one needs an exhaustive audited all-variable
run or a mathematically source-verified automorphism-equivariance
argument reducing all other variables to the tested representatives.

The finite Petersen/K4 successes likewise do NOT prove an
ALL-INPUT two-ply completeness theorem.

## 5. Actual missing global theorem

The family of algorithms at each FIXED lookahead depth k
has polynomial n^C_k worst-case for fixed k, but allowing k
to scale with source size can yield n^O(k) or exponentially
many branches. A successful UNIVERSAL algorithm must prove
a SINGLE C independent of n, even on all connected atomic
snarks and general Holyer images, not merely the existence of
some finite-depth proof for each finite instance.

Candidate next decisive tests:
- source-certified complete all-variable two-ply pass on
  J5/J7, with independent proof provenance; or
- derive a graph automorphism reducing the full source
  variable set to finitely many exact representatives,
  while proving the deterministic closure's verdict
  equivariant to original source row/column relabeling;
- discover a genuinely global polynomial Boolean-invariant
  or finite-depth uniform completeness theorem, which
  must apply beyond Petersen and bounded-width snarks.

Do NOT simply turn up assumption depth to n or relabel
that an n^O(1) algorithm.

## 6. Gate ledger

GF2_BOOLEAN_FIXED_POINT_ALL_SCL_POLY = PREDECESSOR_PROVED.
GF2_BOOLEAN_FIXED_POINT_ALL_SCL_COMPLETE = REFUTED_FINITE.
SINGLE_FAILED_LITERAL_CERTIFIED_SOURCE_DISCHARGE = PROVED.
SINGLE_FAILED_LITERAL_POLY_BOUND = PROVED.
SINGLE_FAILED_LITERAL_PETERSEN = UNKNOWN_CI.
FIXED_TWO_PLY_PROOF_REPLAY = PROVED.
FIXED_TWO_PLY_UNIFORM_POLYNOMIAL_RUNTIME = PROVED.
FIXED_TWO_PLY_K4_K33_PRISM3_SAT = VERIFIED_CI.
FIXED_TWO_PLY_PETERSEN_UNSAT = VERIFIED_CI.
TWO_PLY_IN_MAIN_CERTIFIED_PORTFOLIO = VERIFIED_CI.
FORGED_NESTED_UNSAT_SOURCE_PROOF_REJECTED = VERIFIED_CI.
J5_J7_FIRST_VARIABLE_TWO_PLY = UNKNOWN_CI_NOT_GLOBAL.
ALL_ATOMIC_TWO_PLY_COMPLETENESS = OPEN.
ALL_SCL_POLYNOMIAL_EXACT_BOOL_CLOSURE = OPEN.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
