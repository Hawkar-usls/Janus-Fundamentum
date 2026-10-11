# Universal Solver Research: Exact Polynomial Quadratic Gauss / MOD4 Kernel Filter

Date: 2026-10-11
PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/515

Status: SOUND ALL-INPUT POLYNOMIAL MOD4 OBSTRUCTION,
NOT COMPLETE UNIVERSAL SOLVER; P_VS_NP=OPEN.

## 1. Mathematical theorem for EVERY square+cubic incidence matrix

Let A be n x n over {0,1}, each row and column with exactly
three ones. Let K=ker_F2(A), dim K=d; assume 3|n and m=n/3.
Every k in K has even Hamming weight:

    3|k| = 2 t,  0<=t<=n,

because each selected row has count 0 or 2 over the integers.
Thus |k| is even, |k|<=2n/3=2m, and

    A SAT iff exists k in K with |k|=2m  (E56/E65).

Consider the well-defined binary function

    q(k) = (|k|/2) mod 2.

For k,h in K, elementary Hamming arithmetic yields

    q(k+h) = q(k)+q(h)+(k dot h) (mod 2).

Thus q is a quadratic form on the F2-linear space K, and its
polar bilinear form is the standard F2 dot product restricted to K.

Given a basis b_1,...,b_d of K and k=sum t_i b_i,

    q(t) = sum_i (|b_i|/2 mod 2) t_i
           + sum_{i<j} ((b_i dot b_j) mod 2) t_i t_j.

The complete signed sum

    G(K)=sum_{t in F2^d} (-1)^q(t)

can be computed exactly in deterministic POLYNOMIAL time
without enumerating the 2^d vectors.

### Constructive quadratic Gauss elimination

Write a quadratic Boolean polynomial as

    q(u,v,r) = u*v + a(r)*u + b(r)*v + c(r),

where a,b are affine-linear Boolean polynomials in remaining
coordinates r, and c has degree<=2. Then

    sum_{u,v in F2} (-1)^q = 2*(-1)^[c(r)+a(r)b(r)].

Eliminate any quadratic edge uv, multiply scalar factor by 2,
and replace q with c+ab, still a quadratic Boolean polynomial.
If no quadratic edge remains, q is affine; its signed sum is 0
if a linear term is present and +/-2^(#remaining variables)
otherwise.

After at most floor(d/2) such pair eliminations the result
is exact. Dense Boolean polynomial updates touch O(d^2)
terms per elimination, giving a conservative O(d^3) GF2
arithmetic bound with polynomial bit operations. The Gaussian
result is an integer of magnitude at most 2^d and therefore
has O(d) bits.

No assumptions on girth, connectivity, nullity size or bounded
treewidth are used.

### Pinned/affine extension is also exact and polynomial

Partial assignments on Boolean x correspond to affine constraints
k_j=1-x_j within K. Gaussian elimination of the constraints
over F2 produces either no feasible affine word, or

    k=k0+sum_{i=1}^{d'} t_i c_i,

for independent even-weight codewords c_i in K.

Now

    q(k) = q(k0)
           +sum_i (q(c_i)+k0 dot c_i) t_i
           +sum_{i<j} (c_i dot c_j)t_i*t_j,

so the same polynomial Gauss algorithm returns

    G(pi)=sum_{k in K meeting pi} (-1)^q(k).

Let N=2^d' be the number of affine words. Counts in the two
possible Hamming residue classes are then EXACTLY

    #(|k|=0 mod 4) = (N+G(pi))/2,
    #(|k|=2 mod 4) = (N-G(pi))/2.

This gives a global POLYNOMIAL necessary decision for any pin:

    if (N+(-1)^m*G(pi))/2 == 0, then there is no
    Exact-One extension satisfying pi.

The implication is sound for EVERY square-cubic-linear input
(and square cubic inputs without linearity). If the count is
positive it does NOT imply any weight-2m vector exists;
therefore it is NOT a complete universal solver.

## 2. E123 UNSAT vs transpose SAT: a strong exact result

For the E64/E123 Tutte-12 incidence carrier R, n=63,m=21,d=14.
The independent integer/GF2 algorithm obtains

    R   : N0=16,384, N2=0,    G=16,384;
    R^T : N0=8,192, N2=8,192, G=0.

The source R's kernel is a doubly-even binary code, so all
kernel word weights are 0 mod 4. But Exact-One requires
weight 2m=42 = 2 mod 4, proving R UNSAT solely from a
POLYNOMIAL certificate, with NO enumeration of 2^14 vectors.

For **all 189 one-check pin choices**, the affine polynomial
Gauss algorithm returns N2=0 on R. The SAT transpose R^T
has strictly positive N2 for all 189 choices.

Thus this global orientation-sensitive quadratic invariant
separates the previously hard 189/189 LP-feasible pins and
the exact degree-2 SDP pseudo-moments. A second-moment SDP
over real-valued pseudo-variables does not automatically encode
the parity-weight quadratic invariant over the GF2 kernel.

This is a stronger algorithmic certificate for **E123** than
the prior finite kernel enumeration, not an all-input solution.
The known E67/E68 moment calculations and E65 frozen weight
enumerators already implied the R-side residue pattern;
the innovation in this checkpoint is an all-input constructive
polynomial computation of these residue counts including
arbitrary affine pins. Mathematical quadratic Gauss
elimination itself is classical; do NOT claim its discovery.

## 3. E118 hard reduction is mandatory anti-overclaim control

Run the same exact polynomial oracle on E118's 90-variable
connected square/cubic/linear target compiled from two q9
cubic sources (cyclic offsets (1,6) UNSAT and (1,2) SAT).

The resulting n=90 target weight is 2m=60, a 0-mod4 class.
The checker records both mod4 counts. Positive mod4 residue
count on an UNSAT target, if observed, is an explicit counterexample
to any assertion that the MOD4 oracle alone decides all SCL.

Even without such a finite example, NP-completeness of the
E118 full target class means no general completeness may be
assumed without proving a new theorem.

## 4. Relation to the rank-aggregation route

Earlier PR #515 notes show

    Z(A,pi) =
      sum_{k in K meeting pi} binom(|k|/2,m),

with the missing universal polynomial step being exact
high-degree rank moment aggregation.

The present quadratic Gauss method computes one special
weighted evaluation:

    H_pi(-1)=sum_{k in K meeting pi} (-1)^(|k|/2)

of the half-weight enumerator H_pi(z) =
sum_k z^(|k|/2), in polynomial time.

H_pi(1)=2^d' is also trivial. Computing H_pi(-1) at only these
two roots yields the residue pair but does not uniquely
determine its top coefficient [z^m]H_pi(z)=Z(A,pi).
A universal interpolation would need sufficiently many
independent evaluations or a proved special all-input
closed form; nothing here supplies them.

Special roots of unity can admit algebraic Gauss shortcuts,
but a cheap *single* evaluation is not a uniform polynomial
algorithm for an arbitrary coefficient. General weight
enumerator/Tutte polynomial calculations face known hardness
barriers; do NOT import hardness claims for an arbitrary
restricted carrier without an explicit reduction.

Related prior work: classical Arf invariants and GF2 quadratic
Gauss sums; see Agarwal and Jindal, "Deterministic NC Quadratic
Root Counting in Characteristic Two", arXiv:2609.12669 for
recent independent context, not a priority or originality claim.

## 5. Exact reproduction

    python experiments/r5_universal_quadratic_gauss_mod4_attack.py

The checker performs:
- independent exhaustive vs polynomial affine Gauss comparisons
  on five pin sets for E61 SAT12 and UNSAT12;
- q63 R and R^T exact integer arithmetic and 189 pinned checks;
- two E118 n=90 hard target comparisons (without enumerating
  a potentially large kernel);
- explicit all-input polynomial complexity boundary.

No theorem beyond the stated GF2 quadratic properties is inferred
from finite positive or negative controls.

## Gate

GAUSS_QUADRATIC_MOD4_ALL_INPUT_POLYNOMIAL = PROVED.
AFFINE_PINNED_QUADRATIC_GAUSS_ALL_INPUT_POLYNOMIAL = PROVED.
E123_SOURCE_Q63_MOD4_UNSAT = POLYNOMIAL_CERTIFICATE.
E123_ALL_189_PIN_MOD4_EXCLUSION = EXACT_REPLAY.
TRANSPOSE_R_T_SAT_SUPPORT_RETAINS_MOD4 = EXACT_REPLAY.
MOD4_RESIDUE_POSITIVE_IMPLIES_EXACTONE_SAT = NOT_PROVED.
RANK_AGGREGATION_FOR_TOP_COEFFICIENT = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
