# R5 — Actual ExactSupport AND/OR Proof-Size Gate: Literature-Aligned Lower-Bound Route Audit

Date: 2026-10-11.
Repository: Hawkar-usls/Janus-Fundamentum.
PR: #515, research/parity-isolation-trade-checkpoint-20261009.

## Overall scientific verdict

A genuinely universal deterministic polynomial-time `ExactSupport`
and `SolveLinearCubicXSAT` has NOT been constructed. Neither a
uniform polynomial actual-DAG state bound nor a superpolynomial
minimum AND/OR certificate lower bound is proved.

This note deliberately distinguishes mathematically *verified*
theorems and exact finite experiments from a **candidate transfer
lemma that remains UNPROVED**.

## 1. Existing published exponential formula-caching lower bound — exact scope

Paul Beame, Russell Impagliazzo, Toniann Pitassi, Nathan Segerlind,
"Memoization and DPLL: Formula Caching Proof Systems",
Proceedings of the 18th IEEE Conference on Computational Complexity,
2003, publicly available:

    https://homes.cs.washington.edu/~beame/papers/caching.pdf

Their Theorem 4.6, on publication page 10 (PDF page index 9),
proves that every F_C^(WSR) formula-caching refutation of the
particular graph-tautology instance GT_m requires at least

    2^(m-2)

distinct nodes. Here WSR denotes their weakening, subsumption,
restriction enhancements. The hard GT_m is a specified Boolean
CNF family, **NOT** square+cubic+linear positive Exact-One.

This is a real unconditional exponential lower bound for THAT
proof system and THAT input family. It must NOT be cited as
already showing a lower bound on our frozen
`ExactSupportResidualDAG` or on E118's output.

The same paper gives polynomial simulations and strict
separations between different formula-caching rule systems;
in particular caching whole residual formulas is not
automatically equivalent to either tree-like or general
resolution. Our extra exact component-AND factoring and
ternary exact-one branching require careful treatment.

## 2. One precise theorem which would yield the desired lower bound

For every m, let GT_m be the *specific* hard graph-tautology
formula from the published theorem. The following TWO
statements together would suffice:

(A) Construct in polynomial time a **legal** N(m)xN(m)
square+cubic+C4-free positive Exact-One incidence matrix
T_m, with N(m) <= m^c for a fixed c, where T_m is UNSAT.

(B) Give a uniform explicit transformation that converts
EVERY valid AND/OR exact residual-DAG refutation of T_m
of size S (including arbitrary identical-state memoization,
ternary exact-one elimination, AND component decomposition)
into a valid F_C^(WSR) refutation of GT_m of size at most

    poly(m,S),

with ALL inference rules checked and explicit bit complexity.

If (A) and (B) were proved, the published exponential lower
bound would imply

    poly(m, S_min(T_m)) >= 2^(m-2),

hence

    S_min(T_m) >= 2^(Omega(m^epsilon))

for some epsilon>0 after accounting for polynomial
simulation overhead, and therefore
    S_min(T_m) >= 2^(Omega(N(m)^(epsilon/c))),

a superpolynomial lower bound on the MINIMUM proof size in
our specific AND/OR proof system. It would refute the claim
that THIS frozen algorithm is always polynomial-time, but
would NOT prove P!=NP or exclude other algorithms.

**CURRENT STATUS: (A) not carried through with the
required proof-complexity control; (B) is UNPROVED.**
E118's satisfiability-preserving reduction alone does
not imply (B). Indeed its EQUAL3 gadget has 2 internal
extensions when its ports are all zero, illustrating
additional local choices which must be tracked by any
proof-size preserving simulation.

Do NOT silently treat SAT-preserving reductions as
proof-size-preserving reductions.

## 3. Exact control: E129 coverings can be hard for AND/OR but easy for arithmetic

Predecessor E129 supplies the explicit q12 invertible
legal incidence matrix B with det(B)=36.
Its every r-sheet cover with 3 not dividing r is UNSAT.

New checker:
    experiments/r5_universal_exact_support_e129_cover_tower_visited_attack.py

Constructs exact dual integer vector in original base row order:

    u = (12,-6,12,0,-12,-6,6,-6,-12,18,6,0),

and independently verifies

    u^T B = 36 e_0^T,   sum_i u_i=12.

For EVERY degree-r covering A_r with its explicit fibre
projection, repeat coefficient u_i on all r lifted check
copies of base row i. Then

    lambda^T A_r = 36 * 1_{variable fibre 0},
    lambda^T 1 = 12r.

Any integer solution would force 36*y_0=12r, hence
3*y_0=r, impossible for 3 not dividing r. Modulo nine,
the contradiction becomes 0=3r (mod 9).

This certificate uses a constant-size seed and O(N)
integer operations with O(log N) bit length to verify
given the correctly provided fibre map. It is a
POLYNOMIAL arithmetic UNSAT proof of the complete cover
family, but is NOT an AND/OR proof under our frozen rules.
It warns us: strong *actual DAG search* numbers on this
family would only lower-bound a RESTRICTED algorithm.

Initial focused CI:
  #38142784983 SUCCESS for three deterministic 2-lift towers.
  #38143025842 FAILED due to checker row-index mismatch after
  canonical sorting, NOT because of a false arithmetic theorem.
  #38143104310 SUCCESS after repairing original base row mapping.

Actual visited state observations (all mathematically UNSAT):
   n     seed129   seed132   seed9421
   12       4         4          4
   24       8         5          8
   48      18         9         19
   96      69        22         39
   192    248       155        127
   384    >=1000    >=1000    >=1000
           UNKNOWN   UNKNOWN   UNKNOWN

These are finite measurements. There is no theorem about
asymptotic proof size.

## 4. Exact control: far-apart incompatible pins on a SAT torus

New checker:
    experiments/r5_universal_exact_support_pinned_torus_unsat_frontier.py

Use legal LxL triangular toroidal square/cubic/linear
incidence, L multiple of 3. The earlier Fourier proof
shows exactly three Boolean SAT models indexed by
    x_(i,j)=1 iff (i-j) mod3=t.

Pins x_(0,0)=1 and x_(floor(L/2),floor(L/2)+1)=1
choose distinct residues, so jointly produce mathematically
UNSAT formulas, even though either pin alone is SAT.
The pins are far in the toroidal conflict graph as L grows.

Focused CI #38143384337 SUCCESS:

    L      n    actual expanded states, UNSAT
     9     81         1
    12    144        15
    15    225        23
    18    324        40
    21    441        53
    24    576        77

This family also FAILS as a candidate to exhibit a
large actual search; the frozen solver detects the
pinned contradiction comparatively quickly. It is not
evidence of a worst-case polynomial bound elsewhere.

## 5. Why this passage is materially different from a new formulation

There are now three precisely and separately identified
objects of study:

(a) the exhaustive possible-reachable residual-state space,
    already PROVED exponential even for SAT toroids;
(b) the ACTUALLY EXPANDED frozen deterministic states,
    measured on explicit negative families but no proven
    general asymptotic bound;
(c) the MINIMUM number of nodes in the specified AND/OR
    refutation system (with exact verification), whose
    size can differ from the frozen solver trace.

The published GT_m formula-caching theorem supplies an
unconditional lower-bound TARGET, but the proof-system
transfer (A)+(B) is the essential missing lemma.
The E129 arithmetic dual certificate provides an
unconditional alternate fast mechanism for a special
UNSAT family, emphasizing that no restricted lower bound
would settle P vs NP.

## Gate ledger

PUBLISHED_GT_M_FCWSR_LOWER_BOUND_2^(M-2) = LITERATURE_PROVED.
GT_M_TO_LEGAL_SCL_PROOF_PRESERVING_REDUCTION = NOT_PROVED.
JANUS_ANDOR_TO_GT_M_FCWSR_POLYNOMIAL_SIMULATION = NOT_PROVED.
E129_COVER_ARITHMETIC_MOD9_SHORT_REFUTATION = PROVED.
PINNED_TOROIDAL_UNSAT_SHORT_ACTUAL_TRACE = FINITE_OBSERVATION.
SUPERPOLYNOMIAL_MINIMUM_JANUS_ANDOR_REFUTATION = OPEN.
ALL_INPUT_POLYNOMIAL_EXACT_SUPPORT = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
