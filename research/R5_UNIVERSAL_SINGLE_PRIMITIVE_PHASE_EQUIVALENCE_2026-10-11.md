# The single primitive Fourier phase is already a complete Exact-One counting oracle

Date: 2026-10-11. Repo Hawkar-usls/Janus-Fundamentum, draft PR #515.
Predecessors: E61/E65 top-weight theorem, E118 cubic-to-linear
NP-hardness and count-amplification gadget, and the PR515
rank-aggregation / all-phases Fourier checkpoint.

**Status: exact all-input equivalence and finite reproducible tests.
NOT a polynomial phase evaluation method. P_VS_NP=OPEN.**

## Theorem 1: One primitive phase contains ALL half-weights verbatim

Given a legal n x n square, cubic, linear (C4-free) binary incidence
matrix A with n=3m, let K=ker_F2(A). For ANY affine Boolean pin
assignment pi on x=1+k, put

    H_{A,pi}(z) =
        sum_{k in K: x=1+k satisfies pi} z^(wt(k)/2).

Every word k in K has even weight at most 2n/3=2m
(E61/E65, by counting 0-or-2 incidences in every check).
Thus H is an integer polynomial of degree <=m, whose coefficient
a_m is EXACTLY the number Z(A,pi) of Boolean Exact-One extensions.

Let Q be the smallest power of 2 STRICTLY GREATER than 2m,
let D=Q/2 and zeta be a primitive Q-th root of unity. Then

    m < D <= 2m,    Q <= 4m = O(n).

The cyclotomic polynomial is Phi_Q(X)=X^D+1 and has degree D.
Hence 1,zeta,...,zeta^(D-1) are a Q-vector-space basis of
Q(zeta). Every algebraic integer has a unique integral coordinate
vector in this basis, since Z[zeta] is a free module with this
standard integral basis.

But H_{A,pi} has degree <=m<D. Therefore the EXACT canonical
coordinate vector of the ONE algebraic integer H_{A,pi}(zeta)
is precisely

    (a_0,a_1,...,a_m,0,...,0)  of length D,

and its coordinate at index m is Z(A,pi).

Each coordinate a_t counts a subset of the 2^d kernel words,
thus 0<=a_t<=2^d<=2^n and has O(n) bits. The complete exact
result has D*O(n)=O(n^2) bits, even on the worst legal input.

This is an encoding/injectivity theorem. The length of an exact
algebraic output is polynomial, but computing that output may
still require exponential time. An approximate complex-number
evaluation does NOT automatically give its integral coordinates.

## Theorem 2: A universal polynomial evaluator would imply P=NP

Assume an algorithm EVAL(A,pi) that, for every such A and arbitrary
partial Boolean pin pi, computes the exact standard D-coordinate
integral representation of H_{A,pi}(zeta_Q), where Q is chosen
as above, in deterministic polynomial BIT time.

1. Compute EVAL(A,empty), extract a_m=Z(A).
2. If a_m=0 return UNSAT.
3. If a_m>0, for each j set x_j=0 tentatively and query EVAL
   under the accumulated pins. If the extracted a_m>0,
   keep x_j=0; otherwise fix x_j=1.
4. By induction the pinned solution set stays nonempty.
   At the end verify A*x=1 and return the witness.

This is a SOUND, COMPLETE worst-case polynomial SAT+witness
algorithm under the EVAL premise. Indeed at most n+1 calls
are made with O(n)-bit pin vectors and O(n^2)-bit exact outputs.

The premise is NOT proved. E118 exhibits an explicit polynomial
SAT-preserving reduction from NP-complete cubic monotone
1-in-3-SAT to precisely this square/cubic/linear target.
In particular, for source n variables, target N=10n,
and every satisfying source assignment extends to

    2^(2n/3)

distinct target assignments. Therefore extracting a_m from
one target primitive phase decides the source instance, and
on counting versions recovers the exact source number via
division by this known factor. A generic primitive-phase
evaluator for ALL SCL targets is therefore NP-hard; its
polynomial-time existence would settle P=NP.

This does NOT prove such an evaluator impossible.
The gap from an exact field element's polynomial encoding
to its polynomial-time calculation is the central open problem.

All Q=O(n) phases from the prior note are not logically necessary:
one primitive phase with Q>2m already carries the full polynomial.
This sharpens the sufficient theorem target, not the established
algorithmic complexity bound.

## Theorem 3: The primitive phase includes higher-order interaction terms

Let b_1,...,b_d be the binary kernel basis and t in {0,1}^d.
For each nonempty S subseteq [d], let
w_S=wt(bitwise AND of the b_i for i in S).
The XOR inclusion-exclusion identity over INTEGERS gives

   wt(XOR_{i:t_i=1} b_i)/2
     = sum_i (wt(b_i)/2)t_i
       + sum_{r=2}^d (-1)^(r-1)*2^(r-2)
           sum_{S subseteq [d], |S|=r}
               w_S prod_{i in S}t_i.

For Q=2^s, reduction modulo Q deletes all terms of
degree r>=s+2. Hence each primitive phase summand is

    zeta_Q^[P_s(t)],

where P_s is a multilinear integer polynomial modulo Q of
degree <=min(d,s+1)=O(log n). All coefficients are explicitly
constructible, but naively expanding every such monomial
can require n^{Theta(log n)} operations, not n^{O(1)}.

More importantly, the degree-3 and higher terms do not vanish
for all legal carriers. With Q=64, the frozen q63 E123
UNSAT R has 246 nonzero degree-7 coefficients in its
canonical GF2 RREF basis (and SAT R^T has 104).
This is a finite, basis-dependent certificate that a direct
extension of purely quadratic Gauss pair elimination is not valid.

The known quadratic Gauss routine evaluates H(-1) in polynomial
time, but H(zeta_Q) is generally a much harder exact
high-order exponential sum. Literature on binary-code
weight enumerator complexity does not supply a missing
special all-input SCL phase algorithm.

## Reproducible exact finite controls

    python experiments/r5_universal_single_primitive_phase_hardness_attack.py

The test computes the full canonical phase coordinates by
exponential finite-fixture enumeration **only as a scientific
oracle for the identities**, and independently checks the source
SAT status where possible. Expected top coefficients:

    E61 SAT12   : m= 4, Q=16, a_m=1;
    E61 UNSAT12 : m= 4, Q=16, a_m=0;
    E123 UNSAT63: m=21, Q=64, a_m=0;
    E65 SAT63^T : m=21, Q=64, a_m=36;
    E118 UNSAT90: m=30, Q=64, a_m=0;
    E118 SAT90  : m=30, Q=64, a_m=192
                 = 64 * (three true source solutions).

Pins x_j=0/1 on q12 yield additive split of the exact
top coefficient, exercising the conditional witness protocol.

Correct scientific boundary:

    SINGLE_PRIMITIVE_PHASE_EXACT_COUNT_ENCODING = PROVED.
    SINGLE_PRIMITIVE_PHASE_OUTPUT_BITS = POLYNOMIAL.
    SINGLE_PRIMITIVE_PHASE_POLY_EVALUATOR = OPEN.
    SINGLE_PRIMITIVE_PHASE_ON_SCL = NP_HARD_TO_EXACTLY_EVALUATE.
    E118_COUNT_MULTIPLICITY = PREDECESSOR_E118.
    PHASE_ANF_DEGREE_O(LOG_N) = PROVED_AS_FORMULA_NOT_EVALUATOR.
    GENERIC_QUADRATIC_GAUSS_EXTENSION_TO_PRIMITIVE = NOT_PROVED.
    UNIVERSAL_SOLVER = NOT_CONSTRUCTED.
    P_VS_NP = OPEN.

External prior art: Vyalyi (2003), Hardness of approximating the
weight enumerator of a binary linear code, arXiv:cs/0304044;
Björklund and Kaski (SODA 2021), Fine-Grained Complexity of
Computing the Tutte Polynomial of a Linear Matroid, DOI
10.1137/1.9781611976465.139. Those results concern code/matroid
families in their respective statements; do not transplant
their fine-grained lower bounds to the SCL family without
an explicit preserving reduction.
