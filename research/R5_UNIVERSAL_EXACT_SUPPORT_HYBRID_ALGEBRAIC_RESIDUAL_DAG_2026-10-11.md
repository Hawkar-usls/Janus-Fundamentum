# JANUS R5 — Constructive all-input ExactSupport Hybrid: algebraic refutation inside the residual DAG

Date: 2026-10-11.
Repository: Hawkar-usls/Janus-Fundamentum, PR #515,
branch research/parity-isolation-trade-checkpoint-20261009.

## Direct answer to the universal solver demand

The executable
`experiments/r5_universal_exact_support_hybrid_algebraic_dag.py`
now implements a sound and complete (when unguarded)
deterministic ExactSupport algorithm on EVERY square, cubic,
linear positive Exact-One instance and arbitrary Boolean pins.

**The universal polynomial-time SolveLinearCubicXSAT with
n^O(1) worst-case bit time is NOT CONSTRUCTED.** This is NOT
a proof of P=NP. The exact worst-case evaluation requires
O(S*n^3) bit operations where S is the number of actually
expanded canonical residual states, which can a priori be
exponential. Neither an S<=n^C theorem nor a symbolic
compression with bounded bit cost is supplied.

The new constructive capability is to attach a fresh,
independently checkable polynomial-time MOD9 UNSAT
certificate to EVERY residual hypergraph, including
irregular one/two-variable residual clauses, with shared
memoized outcomes and exact component factorization.

## I. The two-layer algorithm

Input: n rows of size 3, n columns each of degree 3,
pairwise column overlap <=1 per distinct row
(C4-free/linear); pins pi: coordinates -> 0 or 1.

Step 1, polynomial ROOT controls:
normalize pins and propagate selected ones. Run the
existing `ExactSupport(A, pi, max_nodes=0)`, which checks
square/cubic/cardinality promise, exact linear congruence
over Z/9, pinned affine GF2 feasibility, top-weight
capacity, and quadratic-Gauss MOD4 exclusions.
It cannot perform an exponential branch at budget 0.
A negative result is certified; an affirmative result
is a verifiable SAT Boolean witness; otherwise UNKNOWN
means the root survived the polynomial necessary tests.

Step 2, the exact canonical residual DAG:
Represent the current remaining clauses as sorted
tuples of sorted variable IDs. Cache each label-exact
residual state. At every NEW nonempty state, independently
build a rectangular 0/1 incidence matrix B_S from its
remaining clauses (size 1,2 or 3). The residual need NOT
be square, regular or connected.

Run the full algebraic linear-consistency algorithm over
Z/9 from the predecessor
`r5_universal_exact_support_mod9_dual_certificate.py`.
When inconsistent, the algorithm provides lambda with

    lambda^T B_S == 0 (mod 9),
    lambda^T 1   != 0 (mod 9).

Verify this certificate AGAINST B_S itself and cache
UNSAT(S) without further branching. Since every Boolean
satisfying assignment of S gives a ring solution, the
negative inference is sound for arbitrary reduced states.

Step 3, unchanged complete exact Boolean logic:
If no modular negative proof is found, split S into
variable-disjoint connected components. Support(S)
is their conjunction. If connected, choose the shortest
Exact-One clause C; test all choices of its unique
selected member v=1, deleting satisfied checks,
forbidding its neighbors and continuing. Cache either
an exact witness or a completed negative result.

A SAT witness is ALWAYS verified against every ORIGINAL
row and every Boolean pin, not merely against a relaxed
linear system.

Step 4, optional unique-state resource guard:
Return UNKNOWN, with no SAT/UNSAT claim, if a configured
number of new memo keys has been reached. Root polynomial
certificates are still allowed when max_states=0.

## II. All-input correctness proof

The root prefilters are sound by their predecessor
integer, GF2 and quadratic-Gauss derivations. Their
negative conclusions imply no Boolean completion.

For any residual S, every satisfying Boolean vector is
also a solution of B_S x=1 mod9. Thus the explicitly
verified left annihilator is a VALID UNSAT inference.

If modular consistency holds, the algorithm does NOT
assume satisfiability. It uses the original exact
AND/OR residual rules:
 - choosing v=1 is one of all mutually exclusive
   exhaustive placements of the unique one in C;
 - all co-occurring variables become zero;
 - completed clauses are deleted;
 - disjoint components combine by conjunction.

Each nonempty branch strictly decreases the number
of remaining clauses, so unguarded recursion terminates
for EVERY input. Induction on the number of clauses
proves soundness and completeness of the decision.

Any returned SAT model is explicitly checked, so
there is no false-positive SAT, even under a guard.
Any returned UNSAT is justified either by polynomial
certificate or complete exhaustion, so no false-negative.
The only possible incomplete response is UNKNOWN.

## III. Explicit bit runtime, not an unproved claim of P=NP

Let n denote the original number of columns, and S
the number of unique actually expanded residual states.
Each residual has <=n rows and <=n active columns.
A Z/9 Smith-style elimination with recorded left row
operations takes O(n^3) fixed-ring arithmetic operations.
Every ring value has 4 bits; active-variable compression,
state hashing, component decomposition and transitions
cost at most polynomial in n.

Consequently total exact runtime is

    O((S+1)*n^3) fixed-ring/bit operations
    plus polynomial validation and root GF2 work,

and space O(S*poly(n)) bits. This is an exact
resource-accounting result, NOT an all-input n^C bound,
because S can be as large as an exponential function
of n in the absence of a new theorem.

It is NOT enough to say "all algebraic subroutines are
polynomial" when they are called at exponentially many
different residual states. The universal polynomial
runtime gate stays LOCKED.

## IV. Independent focused CI observations

Focused R5 ExactSupport run #38148764131 = SUCCESS.

Frozen fixture                           baseline DAG   hybrid DAG
 E61 SAT12                                      8            8
 E61 UNSAT12                                    4            0
 E123 UNSAT63                                 164            0
 E118 UNSAT90                                  75           12
 E118 SAT90                                    37           37
 E129 UNSAT12 (MOD9 root)                         -           0
 E129 UNSAT24 (MOD9 root)                         -           0

On E118 UNSAT90, the new solver obtains exact UNSAT
while expanding only 12 residual states, compared
with 75 using the original cached pure-combinatorial
DAG; 3 of its local states are rejected by independent
MOD9 certificates. On E123 UNSAT63 the earlier exact
polynomial pinned quadratic-Gauss negative certificate
terminates before any residual state.

Pinned SAT12 subinstances are independently compared
against `ExactSupport(A,pi)`; SAT witnesses and all
original clause sums are checked.

These values are FINITE scientific controls, not
proofs of a polynomial asymptotic bound.

## V. Why stronger modular consistency is insufficient

The earlier semigroup saturation-hole checkpoint
establishes a legal SCL UNSAT63 incidence R for which
there is an integer vector z with one negative entry
satisfying Rz=1. Therefore for EVERY positive modulus M,
including every prime and prime power, z mod M solves
R x=1 mod M. No test based solely on feasibility of
any collection of such LINEAR modular systems can
decide Boolean exact-one satisfiability on this input.
This is true even if every modulus were checked at
once: all modular reductions inherit an integer
solution while Boolean support remains empty.

The hybrid's exact Boolean branching is therefore
not an implementation accident; the missing global
Boolean nonlinear mechanism is the central P-vs-NP
research obligation.

## VI. Next one-shot theorem that would meet the goal

Find an explicit uniform deterministic replacement
for the residual-state recursion, preserving exact
Boolean support and enabling SAT witness extraction,
with a proven bound O(n^C) on ALL input instances and
all pins. Possibilities would be an all-input symbolic
compressed residual evaluator, an oriented semigroup
membership algorithm with a polynomial bit bound, or
a genuine exact primitive-phase evaluator with all
intermediate sizes and arithmetic costs polynomial.
NO such construction is yet known/proved in Fundamentum.

A candidate whose compressed representation requires
exponential computation to construct or evaluate is
not a polynomial algorithm. Likewise a uniformly
polynomial gate on only E118/E123/E125 or invertible
cover instances is NOT sufficient.

## Gate ledger

HYBRID_SCL_SAT_UNSAT_SOUNDNESS = PROVED_ALL_INPUTS.
HYBRID_SCL_COMPLETENESS_UNGUARDED = PROVED_ALL_INPUTS.
HYBRID_RESIDUAL_MOD9_DUAL_NEGATIVE = PROVED_SOUND.
HYBRID_PINNED_SAT_WITNESS = VERIFIED.
HYBRID_RESOURCE_GUARD_UNKNOWN = PROVED.
HYBRID_BIT_TIME_O(S_N_CUBED) = PROVED.
HYBRID_E118_UNSAT90_75_TO_12_STATES = FINITE_REPLAY.
HYBRID_E123_UNSAT63_POLY_CERTIFICATE = PREDECESSOR_REPLAY.
GENERAL_MODULAR_BOOLEAN_EXACTONE_COMPLETENESS = FAILED_E123.
UNIVERSAL_POLYNOMIAL_ExactSupport = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
