# R5 E123 — E64 Tutte-12 Rebind: Post-E18 / KLOC3-Clean UNSAT Benchmark

Date: 2026-10-10

Status:
EXISTING_E64_Q63_UNSAT_REBOUND_THROUGH_E18_AND_KLOC3__STRONG_FINITE_BENCHMARK

P_VS_NP = OPEN.

## 1. Anti-loop purpose

The post-E121/E122 benchmark search asked for a SAT-admissible connected
square+cubic+linear UNSAT carrier that survives:

* E18 zero/projective-coordinate compression; and
* arbitrary-coordinate KLOC1/KLOC2/KLOC3 tests.

A full repository audit shows that a substantially stronger finite carrier was
already frozen in E64:

    Tutte 12-cage / generalized hexagon GH(2,2)
    q = 63
    rank_Q = 49
    nullity_Q = 14
    Exact-One UNSAT.

E123 does not invent a new carrier. It replays the existing E64 carrier through
the later E18/KLOC filters and freezes the cross-frontier result.

## 2. Frozen E64 authority

E64 reconstructs the 126-vertex Tutte 12-cage from the standard LCF sequence,
extracts one 63-by-63 bipartite incidence matrix R, and independently verifies:

    square,
    row degree 3,
    column degree 3,
    linear/C4-free,
    Levi-connected,
    girth 12,
    rank_Q(R)=49,
    nullity_Q(R)=14.

Since

    63 = 0 mod 3,

this carrier is SAT-admissible with respect to the mandatory divisibility
precheck.

E64 exactly exhausts the 2^14 free rational-kernel assignments and finds

    ker_Q(R) intersect {-1,2}^63 = empty.

Therefore the carrier is Exact-One UNSAT.

## 3. E18 projective-clean replay

Construct a rational kernel basis from the exact RREF of R.

For every one of the 63 coordinates, take its coordinate functional row in the
14-dimensional kernel-parameter space.

The checker verifies:

    zero coordinate rows = 0,
    projectively proportional coordinate-row pairs = 0.

Hence E18 performs no zero-coordinate rejection and no equality/complement
quotient on this carrier.

The effective rational nullity after E18 remains

    d_eff = 14.

So the E64 q63 carrier is genuinely post-E18 clean.

## 4. Complete KLOC <=3 replay

For every coordinate subset S of sizes one, two and three, E123 tests exactly

    pi_S(ker_Q R) intersect {-1,2}^S != empty.

Counts:

    C(63,1) = 63,
    C(63,2) = 1953,
    C(63,3) = 39711.

All size-1 and size-2 projections have full local rank.

Among the 39711 coordinate triples, exactly

    63

have projection rank two rather than three.

Every one of those 63 dependent projected planes still contains at least one
corner of {-1,2}^3.

Therefore:

    KLOC1 = CLEAN,
    KLOC2 = CLEAN,
    KLOC3 = CLEAN.

## 5. Consequence

The E64 q63 carrier simultaneously satisfies:

    3 | n,
    connected square/cubic/linear,
    rational nullity 14,
    E18 projective-clean,
    arbitrary-coordinate KLOC3-clean,
    Exact-One UNSAT.

Thus E122 was not the first available strong finite post-E18/KLOC3 negative
control; it was only the first one produced on the new branch.

The repository already contained a better carrier, but the later filters had
not been cross-applied to it.

This is precisely why repository-wide anti-loop auditing is mandatory.

## 6. What this refutes

The following implications are false even on a highly symmetric, high-girth,
SAT-admissible direct quotient:

    E18-clean + KLOC3-clean => SAT;

and

    E18-clean + KLOC3-clean + moderately large finite rational nullity => SAT.

No solver may use those conditions as a terminal.

## 7. What this does NOT prove

This is one finite q=63 carrier.

Although

    d_eff = 14

is already much larger than the tiny-nullity controls and numerically exceeds
log_2(63), one finite point does NOT establish an asymptotic statement such as

    d_eff = omega(log n).

The E61 algorithm

    O(2^d poly(n))

still solves this specific fixture by finite exhaustive kernel replay.

Therefore E123 is a strong mandatory negative control, not an asymptotic lower
bound and not a universal-hardness theorem.

A scalable post-router hard family must additionally prove that its effective
nullity/other surviving parameter escapes every admitted polynomial terminal
as n grows.

## 8. Updated active target

The benchmark search no longer needs to ask whether post-E18/KLOC3-clean UNSAT
exists. It does.

The sharpened asymptotic benchmark target is:

    SCALABLE_POST_ROUTER_UNSAT

with:

    connected square/cubic/linear,
    3|n,
    E18 projective-clean,
    KLOC3-clean,
    no cube-root/rainbow-Z3 SAT certificate,
    effective rational nullity beyond O(log n),
    outside the admitted low normal-rank/component/branchwidth terminals,
    Exact-One UNSAT with an exact polynomially checkable or replayable
    certificate.

The theorem-level algorithmic target remains:

    GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION

for the one-check three-port support relation.

## Claim boundary

E64_TUTTE12_Q63_UNSAT = PRESERVED.
SAT_ADMISSIBLE = YES.
RATIONAL_NULLITY = 14.
E18_PROJECTIVE_CLEAN = YES.
E18_PROPORTIONAL_PAIRS = 0.
KLOC1_KLOC2_KLOC3 = CLEAN.
DEPENDENT_KLOC3_TRIPLES = 63, ALL ALPHABET_COMPATIBLE.
SCALABLE_POST_ROUTER_UNSAT_FAMILY = OPEN.
GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
