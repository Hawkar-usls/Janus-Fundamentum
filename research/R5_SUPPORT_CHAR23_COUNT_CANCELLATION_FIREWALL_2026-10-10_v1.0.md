# R5 SC23 — Exact Three-Port Support Versus Modular Extension-Count Cancellation

Date: 2026-10-10

Status: FINITE_EXACT_SUPPORT_FIREWALL__NO_UNIVERSAL_SOLVER

P_VS_NP = OPEN.

## 0. Anti-loop: what is already known

E64 constructs the Tutte 12-cage / generalized hexagon incidence matrix
`R` (63 x 63). E65 **already** establishes that `R` is UNSAT and
`R^T` is SAT, with exactly 36 solutions on the transpose. E123 **already**
establishes E18-clean / KLOC1-3-clean for `R`.

SC23 does **not** claim to discover transpose asymmetry or a new family.
It audits the algorithmic target `SUPPORT_c`: exact per-port solution
multiplicities and their images in characteristics 2 and 3, and repeats
E18/KLOC3 filtering on `R^T`.

Primary executable authority:
`experiments/r5_e125_tutte12_three_port_count_firewall.py`.

## 1. Exact certificate principle

For any square-cubic matrix `A` of order `n` with `3|n`, put
`x = 1+k` over GF(2), with `k in ker_GF2(A)`.

Because every row has degree 3, `A1 = 1 mod 2`, so
`Ax = 1 mod 2`. Every integer row count `(Ax)_i` is therefore
either 1 or 3. If `t3` rows are triple-covered, then

    3 |x| = n + 2*t3.

Consequently,

    A x = 1 over integers
      iff
    x in 1 + ker_GF2(A) and |x| = n/3.

This gives a sound and complete **finite** verification for the frozen
nullity-14 fixtures by enumerating exactly 2^14 binary kernel words.
It is not a polynomial-time method for unbounded nullity.

## 2. Frozen pair and full one-check supports

`R` and `R^T` have:

* order 63, row/column degree 3, C4-free/linear and connected;
* Tutte-12 Levi girth 12;
* rank_Q = 49, rational nullity = 14;
* exactly the same uncoloured Levi graph / singular spectrum.

The exact binary top-shell enumeration returns:

| Carrier | Exact-One solutions | Each check's port counts | True SUPPORT_c |
|---|---:|---|---|
| `R` | 0 | (0,0,0) | 000 |
| `R^T` | 36 | (12,12,12) | 111 |

These statements concern **every one of the 63 checks**, not a
single chosen row. The `R^T` control also independently verifies each
enumerated binary vector against all integer Exact-One constraints.

On `R^T`, exact projected rational-kernel testing further gives:

    zero coordinate functionals = 0
    proportional E18 pairs = 0
    dependent coordinate triples = 63 of 39711
    all 63 dependent triples meet {-1,2}^3
    KLOC1/KLOC2/KLOC3 = CLEAN.

The existing E123 replay proves the corresponding E18/KLOC3 results
for `R`. Thus **both** orientation controls survive the same
low-arity rational-kernel tests, while their global masks disagree.

The classical finite-geometrical perspective on distance-2 ovoids
and the exact count 36 can be found in De Wispelaere and Van Maldeghem,
*Codes from generalized hexagons*, Designs, Codes and Cryptography
(2004), https://cage.ugent.be/geometry/preprints2.php?active_d=61
(see E65 for the older repository transpose result).

## 3. New precise firewall: characteristic 2/3 cancellations

For each check `c` and its three ports `j`, define the **integer**
extension multiplicity

    N_(c,j) = #{x in {0,1}^63 : R^T x=1 and x_j=1}.

SC23 establishes `N_(c,j)=12` for every `c,j`. Hence:

    Boolean support:     1[N_(c,j)>0] = 1
    count modulo 2:      N_(c,j) mod 2 = 0
    count modulo 3:      N_(c,j) mod 3 = 0.

Therefore a symbolic construction that declares a port extendible
**iff its ordinary solution-count coefficient is nonzero in GF(2)**
(or in GF(3)) gives a **false UNSAT signal** for every check of a
SAT square-cubic-linear instance.

Together, `R` and `R^T` have identically zero reduced
three-port count masks in these two characteristics, even though the
exact masks are respectively 000 and 111.

**This does not refute** algebraic algorithms with a justified
noncancellation mechanism, isolation, multiple moduli plus a
provably sufficient reconstruction bound, or an entirely different
symbolic invariant. It refutes only the above direct fixed-characteristic
nonzero-coefficient oracle.

## 3A. E127 dual-orientation affine-closure comparison

The independent E127 checkpoint had already computed the complete fixed-point
pin/unit/XOR/affine closure for every one-check state of the **UNSAT** orientation
`R`, reporting 189 surviving states and a uniform quotient profile.

SC23 now applies the **same E127 code** to all 189 pinned one-check states of
the **SAT** orientation `R^T`, including exact rational ranks of each
signed quotient. Every branch survives, and all 189 branches in *each*
orientation share the summary signature:

    originally unknown variables = 56
    XOR quotient components = 44
    size-2 components = 12
    size-1 components = 32
    surviving proper ternary constraints = 48
    signed quotient rank_Q = 34
    effective affine nullity = 10.

Yet the true global support mask remains `000` on `R` and `111`
on `R^T`.

**Precise obstruction:** a proposed `SUPPORT_c` procedure that uses only
these post-affine-closure **summary statistics** to decide the three ports
must fail. We do **not** claim the complete signed quotient matrices or
their full symbolic representations are isomorphic; a genuinely global
symbolic invariant of those matrices remains a possible approach.

This comparison reuses E127 rather than repeating its earlier UNSAT proof,
and still uses only finite controls, not an asymptotic theorem.

## 3B. E122/E123 adversarial fork for the exact SUPPORT_c algorithm

The primary request was to test actual polynomial support construction on
both E122 and E123, rather than only refine finite parameterized routers.

For the frozen E122 q36 UNSAT cyclic 3-lift, the same elementary E127
`propagate` and `quotient` procedures reject **every one-check pin**
before any global arithmetic solving:

    36 checks * 3 states = 108 states,
    90 rejected by Exact-One unit propagation,
    18 rejected by XOR-component parity inconsistency,
    0 surviving.

At the check level, 18 checks have (3 UP, 0 XOR) and 18 checks have
(2 UP, 1 XOR). Every check independently yields all three absent
`SUPPORT_c` bits. Thus a **deterministic polynomial** procedure with three
pins at any fixed check plus polynomial UP/XOR closure decides E122 UNSAT.
This is a stronger executable route for E122 than its previously cited
small rational nullity d=3, and no 2^d enumeration is required.

By contrast, E123 q63 UNSAT survives all 189 E127 pin/affine states.
Its SAT-transpose also survives all 189, with identical coarse closure
profiles, despite opposite exact support masks.

This does not solve an unrestricted input family. It sharpens the mandatory
benchmark: use E122 as a positive test of cheap UNSAT detection and E123
as the adversarial survivor of exactly the same preprocessing.

## 4. Consequence for the actual theorem target

A valid `GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION` must distinguish
**existential nonemptiness** from a field-dependent count that may
vanish by multiplicity. A 3-bit output and a rank-1 matroid interface
do not prevent cancellation of its inaccessible coefficients.

No new polynomial universal reduction, constructive representation,
completeness theorem, or runtime theorem is established here.

    E65_TRANSPOSE_ASYMMETRY = PRIOR_RESULT.
    E123_R_E18_KLOC3_CLEAN = PRIOR_RESULT.
    SC23_RT_E18_KLOC3_CLEAN = FINITE_REPLAY.
    SC23_PER_PORT_COUNTS = EXACT_FINITE_CERTIFICATE.
    SC23_MOD2_MOD3_COUNT_TO_SUPPORT = REFUTED.
    SC23_DUAL_AFFINE_SUMMARY_SUPPORT = REFUTED.
    SC23_E122_UP_XOR_BRANCH_EXHAUSTION = FINITE POLYNOMIAL CERTIFICATE.
    GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION = OPEN.
    SCALABLE_POST_ROUTER_UNSAT = OPEN.
    SolveLinearCubicXSAT = NOT_CONSTRUCTED.
    P_VS_NP = OPEN.

## 5. Reproducibility

    python experiments/r5_e125_tutte12_three_port_count_firewall.py

The executable reconstructs `R` using frozen E64 source,
reuses E65's exact GF(2) kernel RREF machinery and E123's exact
rational kernel-coordinate construction. Independent CI confirmation
is pending until an R5 run on this successor commit succeeds.
