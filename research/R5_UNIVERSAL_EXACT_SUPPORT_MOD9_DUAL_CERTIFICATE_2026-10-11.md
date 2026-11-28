# R5 — ExactSupport Polynomial MOD9 Dual-Certificate Gate (All Inputs and Pins)

Date: 2026-10-11
Repository: Hawkar-usls/Janus-Fundamentum
Branch: research/parity-isolation-trade-checkpoint-20261009, PR #515

## Scientific status and scope

**PROVED:** A deterministic polynomial-bit-time procedure decides
whether the integer linear exact-one equations, with arbitrary Boolean
pins, are consistent over the ring Z/9Z. On a contradiction it
constructs an independently verifiable left-annihilator vector
that soundly proves Boolean UNSAT. This procedure is now wired into
the callable pinned `ExactSupport` BEFORE its exponential fallback.

**NOT PROVED:** consistency modulo nine implies a Boolean exact-one
assignment, a uniformly polynomial support evaluator, or a
polynomial upper bound on the complete residual-DAG search.

Universal `SolveLinearCubicXSAT` n^{O(1)}: NOT CONSTRUCTED.
`P_VS_NP`: OPEN.

## I. Exact algebraic ring elimination and certificate

For an integer m-by-n system B x=b with m>=1 and n>=1,
reduce all entries mod 9. The executable algorithm chooses a
nonzero pivot of minimal 3-adic valuation in the remaining
submatrix, i.e. a UNIT of Z/9 or a nonzero multiple of 3.
Swap rows and columns to put it on the diagonal, multiply
the pivot row by a unit to normalize the pivot to 1 or 3,
and eliminate all other active entries in its column
by invertible row operations and its row by invertible
column operations.

The minimal-valuation selection guarantees the pivot
DIVIDES every entry of the active submatrix. Thus every
elimination multiplier is an integer modulo nine;
there is no illegal division by a non-unit or reliance
on field Gaussian elimination.

The process constructs invertible ring matrices U,V such
that

    D = U B V (mod 9)

is diagonal, with each diagonal entry in {1,3,0}.
The algorithm stores U as explicit transformed identity E,
but does not need to materialize V since only
inconsistency certificates are requested.

For the transformed RHS g=U b, the diagonal equation
D y=g is feasible exactly when:

    diagonal 1: no constraint on g_i;
    diagonal 3: g_i is divisible by 3;
    diagonal 0 (including all extra rows): g_i=0 mod 9.

If any condition fails, construct a vector lambda from
row i of U:

    if d_i=3 and g_i not divisible by 3,
        lambda = 3*U_i;
    if d_i=0 and g_i!=0,
        lambda = U_i.

Then lambda is guaranteed to satisfy

    lambda^T B = 0 (mod 9),
    lambda^T b != 0 (mod 9).

Indeed lambda^T B V is a zero row (because 3*3=9=0
or the diagonal row is zero), and V is invertible,
so lambda^T B=0. Its right-hand side is nonzero
by construction. Such lambda proves NO solution
even with unrestricted integer x. In particular
NO Boolean Exact-One solution exists.

The independent verifier checks those two equations
directly against the ORIGINAL input, not the transformed
matrix; no trusting the eliminator or floating-point
arithmetic is necessary.

The elimination requires O((m+n)^3) operations on ring
elements from {0,...,8}, including updating the m-by-m
row transform. Each ring operation has O(1) bit cost.
Space O((m+n)^2). For an SCL matrix with <=n pins,
m<=2n, giving O(n^3) fixed-ring bit time for this
particular negative gate.

## II. ExactSupport(A,pi) all-input integration

Given a valid square/cubic/linear n-by-n binary incidence
A and Boolean pinned assignments pi, build

    B = [ A ; e_j^T for j in dom(pi) ],
    b = [ 1_n ; pi(j) for j in dom(pi) ].

Every genuine Boolean Exact-One solution x must satisfy

    B x=b (mod 9).

Therefore when the ring system is inconsistent,
`ExactSupport` returns:

    status = UNSAT,
    reason = PINNED_MOD9_INTEGER_OBSTRUCTION,
    mod9_certificate = lambda,

where the certificate is independently verified.
This gate works with max_nodes=0 and costs polynomial
bit time, with no branching.

If the ring system is consistent, the test proves
NOTHING about Boolean satisfiability and `ExactSupport`
continues to the existing exact GF2/Gauss and exhaustive
search. Positive modular status is NEVER promoted to SAT.

The algorithm is complete as a modular linear-consistency
test, but it is only a sound UNSAT **filter** for Boolean
Exact-One support.

## III. Independent finite controls and limitation

Executable:

    python experiments/r5_universal_exact_support_mod9_dual_certificate.py

The checker independently enumerates 9^n candidate
ring assignments for 216 deterministic random SMALL
rectangular cases (m=1..4, n=1..3) and compares the
answer against the exact polynomial ring eliminator.

Frozen scientific matrices:

- E129 q12 rational-invertible base: MOD9-INCONSISTENT.
- E129 connected q24 2-lift: MOD9-INCONSISTENT.
- E129 q48 further 2-lift: MOD9-INCONSISTENT.
- E61 SAT12: MOD9-CONSISTENT, also with 0,1,4,12
  pinned coordinates from an actual Boolean SAT witness.
- E123 UNSAT63: MOD9-CONSISTENT.
- E118 UNSAT90: MOD9-CONSISTENT.
- E118 SAT90: MOD9-CONSISTENT.

The last two UNSAT controls are ESSENTIAL: they falsify any
claim that a modular-nine consistency test alone solves
the entire NP-complete SCL class. In particular the
E118 q90 negative control survives this relaxation.

The finite CI confirms the implementation; correctness for
ALL matrices follows from the ring-diagonalization proof,
not statistical extrapolation.

The predecessor E129 cover theorem already constructs a
constant-size dual vector for its special covered base.
This checkpoint **generalizes a NEGATIVE certificate finder
to arbitrary SCL matrices and arbitrary pins**; it does
NOT generalize UNSAT COMPLETENESS.

## IV. Proof complexity ceiling

The existence of a short arithmetic certificate for
E129 covers does not imply a small memoized AND/OR
refutation. Their inference rules differ.

Our MOD9 filter can be appended as an independent
polynomially checkable leaf rule to a stronger refutation
system, but lower bounds on the old purely combinatorial
AND/OR system are not automatically lower bounds on the
strengthened arithmetic system.

Conversely, adding this leaf rule to `ExactSupport`
cannot by itself achieve P=NP, because there exist
unresolved UNSAT instances on which all tested ring,
GF2 and quadratic-Gauss filters admit false-positive
relaxation solutions. The residual exact-cover search
can still be exponential.

## Claim ledger

MOD9_RING_SNF_ELIMINATION_ALL_INPUTS = PROVED.
MOD9_INCONSISTENCY_LEFT_ANNIHILATOR_EXISTS_AND_FOUND = PROVED.
MOD9_CERTIFICATE_INDEPENDENT_POLY_BIT_VERIFICATION = PROVED.
MOD9_PINNED_EXACTONE_UNSAT_FILTER_SOUND = PROVED.
MOD9_NEGATIVE_GATE_BIT_TIME_O(N^3) = PROVED.
MOD9_Q12_Q24_Q48_E129_CERTIFICATES = REPLAYED.
MOD9_RANDOM_RECTANGULAR_216_EXACT_BRUTE_FORCE = REPLAYED.
E123_AND_E118_NEGATIVE_MOD9_FALSE_POSITIVES = VERIFIED.
MOD9_BOOLEAN_EXACTONE_COMPLETENESS = FAILED.
GLOBAL_POLYNOMIAL_ExactSupport = OPEN.
MINIMUM_AND_OR_PROOF_SIZE_SUPERPOLY_BOUND = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
