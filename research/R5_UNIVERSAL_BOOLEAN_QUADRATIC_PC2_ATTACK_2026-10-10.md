# Universal Solver Attack: Boolean Quadratic / Degree-2 Polynomial Calculus

Date: 2026-10-10
Repo: Hawkar-usls/Janus-Fundamentum
Parent before this experiment: PR #515 HEAD
`9a57a5c0cabbf9c07c4236e8bd6893f557e8afc3`.
Reference clean integrated predecessor: R5 run `38067538131` = SUCCESS;
registry run `38067538176` = SUCCESS.

**Sole objective:** deterministic, sound, complete worst-case
polynomial-time `SolveLinearCubicXSAT(F)` for *every* square + cubic +
linear Positive Exact-One instance, returning SAT+witness or UNSAT.

**Verdict:** candidate UNIVERSAL_FIXED_DEGREE_2_PC = REFUTED.
General polynomial-time solver NOT CONSTRUCTED. P vs NP OPEN.

This investigates the universal Boolean polynomial structure missing
from the prior rational/semigroup/LP/coefficient attacks; it does not
repeat those formulas, assert a new solved subclass, or claim P=NP.

## 1. Boolean quadratic identity for arbitrary incidence matrices

For any clause of three Boolean variables a,b,c, Exact-One is
**equivalent** to the two equations over GF(2), with Boolean
idempotence x^2=x:

    p(a,b,c)=1+a+b+c=0,
    q(a,b,c)=ab+ac+bc=0.

Reason: p=0 allows exactly one or all three bits to equal 1;
q=0 rules out the all-three case, since 1+1+1=1 in GF(2).
This equivalence is exact for all inputs and independent of
the regularity and C4-free promises.

These degree-2 constraints look attractive for a polynomial-time
linear-algebraic elimination theorem.

## 2. Concrete deterministic polynomial candidate

Work in the Boolean ring

    B = GF(2)[x_1,...,x_n] / <x_i^2-x_i : all i>.

Build the vector space with basis all squarefree monomials
of degree <= 2:

    {1} union {x_i} union {x_i x_j : i<j}.
    M = 1+n+n(n-1)/2 = O(n^2).

For each check c, generate all available degree<=2 products

    p_c, x_1 p_c, ..., x_n p_c, q_c.

Compute the GF(2) linear span using exact bit-packed Gaussian
elimination. If constant 1 is in the span, report UNSAT.
Otherwise report UNKNOWN (NOT SAT).

The test is SOUND on *every* formula: every Boolean Exact-One witness
annihilates each generator and hence annihilates any linear
combination, but evaluates constant 1 as 1.

There are n(n+2)=O(n^2) generators and O(n^2) columns.
Ordinary bit-Gaussian elimination uses polynomial total bit
operations, bounded conservatively by O(n^6) using
O(n^2)xO(n^2) matrix elimination; actual bitsets are faster.
Thus **the refutation test itself** is unconditionally
deterministic polynomial-time.

A universal solver would follow *only if* one could prove:

    for every UNSAT target F, 1 belongs to this degree-two span.

This proposed completeness implication is FALSE, as below.

## 3. Canonical q90 hard-to-PC2 counterexample from E118

Start from the 9-variable 3-occurrence cubic positive Exact-One source
with indices i in Z/9Z and one clause at each row i:

    C_i = {v_i, v_(i+1 mod 9), v_(i+6 mod 9)}.

Every variable occurs three times; all row triples have distinct
entries. Exhaustive examination of all 2^9 Boolean assignments
finds ZERO Exact-One witnesses.

There is also a short linear source-level proof:
the 9x9 binary incidence of these cyclic rows is invertible over
GF(2), since gcd(1+t+t^6, t^9-1)=1 in GF(2)[t].
The unique solution of the necessary parity equations
A x = 1 mod 2 is the all-ones vector (every row has weight three).
This vector fails Exact-One at every row. Hence source UNSAT.

Apply the **already canonical and independently validated E118**
occurrence splitter and EQUAL3 gadget (9 clauses / 7 internal
variables per source variable). The output contains

    n=90 variables and 90 checks,
    row degree = 3, column degree = 3,
    linear/C4-free, Levi connected,
    SAT(target) <=> SAT(source) = false.

The E118 gadget local projection is exactly ports 000 or 111,
with two internal extensions for false and one for true,
respectively. No extension can invent a satisfying assignment.

The independent exact PC2 row-span calculation on this q90
target reports:

    squarefree monomial columns:   4096
    degree<=2 generator rows:     8280
    GF(2) rank:                  3969
    constant 1 in row-span:       NO.

Thus we have a *connected, exact, target-class UNSAT* carrier
that survives the candidate's complete polynomial-time
degree-two test.

This is a decisive refutation of
`UNIVERSAL_FIXED_DEGREE_2_PC`; no assumption about P!=NP
or empirical SAT guess is needed.

## 4. Independent positive and negative controls

Use the identical q9->q90 E118 construction with cyclic shifts
(1,2) as the SAT control. The checker finds source witnesses,
constructs a full explicit 90-bit target witness from canonical
EQUAL3 gadget extensions, and verifies all 90 Exact-One checks.
Degree-two PC correctly refuses to report UNSAT:

    monomials = 4096; generators = 8280;
    rank = 3966; constant not in span.

For the existing canonical q63 E64/E123 Tutte-12 **UNSAT**
orientation, the same procedure reports:

    monomials = 2017; generators = 4095;
    rank = 1960; constant IN span.

For its E65 SAT transpose (36 true SAT solutions),
the rank is also 1960 but constant NOT IN span.

Thus the degree-two method really can extract nontrivial
global refutations (including E123), but that success cannot
be promoted to a universal solver.

## 5. Provenance, replay and invariant auditing

Executable: `experiments/r5_universal_boolean_quadratic_pc2_attack.py`

Reuses, *rather than redefines*, E118 gadget clauses/splitting and
the E64 Tutte-12 original matrix. Checks all source assignments,
all 90 target matrix structural promises, Levi connectivity,
both source->target SAT witness extension and one-to-one SAT
projection guaranteed by E118, and exact GF(2) rank/spanning
identities. No floating-point arithmetic.

The new code has a deliberately finite n=90 counterexample; do
not interpret it as an asymptotic runtime bound for solving SAT.
Its generic polynomial PC2 refutation algorithm has a proved
polynomial bound, but its completeness is disproved.

Prior R5 E67-E79/E102-E111 algebraic routes remain separate.
Known polynomial calculus degree lower bounds for other SAT
encodings (such as Tseitin expanders) make arbitrary bounded
degree a risky universal thesis; do **not** import their
lower bounds automatically to this square+cubic+linear class
without a formal E118 degree-preserving reduction.

Reference for general polynomial calculus lower bounds:
Buss, Grigoriev, Impagliazzo, Pitassi (JCSS 2001),
doi:10.1006/jcss.2000.1726.

## 6. Single unresolved *universal* step

The universal goal requires a polynomial-time algorithm able
to decide SAT vs UNSAT on the q90 target and *every* other
input. Degree-two PC is sound and computationally polynomial,
but the fixed-degree completeness theorem is false.

A correct successor cannot merely increase degree ad hoc:
unrestricted degree d entails n^{O(d)} monomials, and to keep
a deterministic global n^{O(1)} runtime needs a UNIVERSAL
constant-degree proof (refuted for d=2) or a genuinely
compressed representation with rigorous total polynomial
construction and extraction costs.

No universal bounded-degree theorem, polynomial compressed
high-degree certificate, or general polynomial search
procedure has been proved.

## Claim boundary

EXACT_ONE_PARITY_PLUS_QUADRATIC_ENCODING = PROVED.
DEGREE_2_PC_SOUND_POLYNOMIAL_UNSAT_TEST = PROVED.
E123_DEGREE_2_REFUTED = EXACT_REPLAY.
E65_TRANSPOSE_SAT_DEGREE_2_NOT_REFUTED = EXACT_REPLAY.
E118_Q90_SOURCE_UNSAT_TARGET_LINEAR_CUBIC = PROVED_AND_REPLAYED.
E118_Q90_DEGREE_2_INCONCLUSIVE = EXACT_REPLAY.
UNIVERSAL_FIXED_DEGREE_2_PC_COMPLETENESS = REFUTED.
UNIVERSAL_COMPRESSED_BOOLEAN_POLYNOMIAL_SOLVER = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
