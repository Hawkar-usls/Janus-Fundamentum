# BABEL-24 — certified CONNECTED SCL27 falsifier of the two-sided Gram SAT-dominance completion route

**2026-10-22. Research-only all-degree falsifier of the specific BABEL-23 l1 sufficient SAT gate.** Parent Draft #549 at \`088b15cd7f9df1c9af2503395048ea4ebd3ff50d\`. No main changes, no promotion to general SAT/P=NP authority.

## Key theorem: unique model + complete vanishing ideal implies l1 SAT gate NEVER fires

Let F be any legal SCL with GF(2) kernel K of dimension d>=2 and exactly one true Exact-One model, at kernel coordinate a. Let M_k be the complete Fourier multiplier degree-k matrix, and suppose im(M_k) equals the full rational space V of functions on K vanishing at the unique SAT point (equivalently dim V=2^d-1). The Gram residual H_k from e0 onto V^perp then necessarily equals the *point indicator* 1_{a}, because e0 represents the constant 1 function and the orthogonal decomposition of 1 into V and V^perp is 1=1_{a}+(1-1_{a}). Its Fourier coefficients are

    h_q=2^{-d} (-1)^{q·a}   for EVERY q in K*.

Hence

    h0=2^{-d},   sum_(q!=0)|h_q|=1-2^{-d} > 2^{-d}   (d>=2),
    2^d*h0=1.

Thus BABEL-23's **l1-dominance sufficient SAT gate fails**, and its #SAT upper-bound UNSAT gate fails, **at every k for which the full ideal is already spanned**. If the ideal is spanned at k=1, adding *any number* of higher-degree multipliers cannot change H_k; for EVERY k>=1 the exact two-sided method must output UNKNOWN on that SAT instance.

This is a *falsifier of the proposed completeness of these TWO SUFFICIENT GATES*, NOT a falsifier of the sound BABEL-22/23 theorems, nor of universal degree-2 UNSAT completeness, nor of P=NP. The input is SAT. Of course the SAT witness can be found by other algorithms; the failure is specific to the nonnegative residual certificate mechanism.

## One explicit CONNECTED 27-by-27 square cubic linear SAT instance

Frozen \`experiments/babel24/connected_unique_sat_falsifier.py\` has 27 rows and 27 columns, each row/column 3-regular, any two rows meet in <=1 column, and connected row-variable incidence. The 27 rows were obtained from three independent copies of the affine9 SCL by 8 reproducible cross-block single-literal swaps, \`random.Random(278)\`, selecting block endpoints (0,1), (1,2), (2,0), repeated. This origin is discovery provenance, NOT an independent preregistered blind search. The frozen row SHA256 is

    9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed

The independent exact GF2 rank is 24, so K has dimension 3 and **exactly eight** parity words. Exhaustive enumeration of all eight physical Boolean assignments gives exactly one true SAT model, with ONE-indices (the input Boolean x, not v):

    (2,3,7,9,13,17,19,23,24).

This is the actual verified assignment, not a candidate whose row satisfaction is assumed from weight alone.

## Complete **rational** rank certificate at degree ONE

Let labels lambda_j denote the independently verified K* character labels. For every row r=(a,b,c) and legal Fourier shift q drawn from \`Q1={0} union {lambda_j}\`, column m_(r,q) has counts at frequencies \`(q,q xor lambda_a,q xor lambda_b,q xor lambda_c)\`.

Seven legal degree<=1 full-M1 columns, in order:

    (row,shift) =
    (0,0), (0,4), (2,0), (3,0), (4,0), (14,0), (15,0).

Their integer Fourier coefficient submatrix restricted to the seven NONZERO frequency rows 1..7 is a **7x7 determinant exactly 8**. This proves rank_Q M1 >=7 without floating point, heuristic search, or reduction modulo a prime. Independently, EVERY legal generator must vanish as a function at the real SAT point, so its span is contained in the dimension-7 rational vanishing subspace. Thus

    rank_Q(M1)=7=dim(V), hence im(M1)=V.

Since M1 subset Mk subset V for every k>=1, ALL higher degrees have exactly the SAME im(Mk)=V. The Gram residual is forever exactly the unique SAT indicator with

    h0=1/8, sum_{q!=0}|h_q|=7/8, 2^d*h0=1.

The independent verifier checks **every** one of the 27*|Q1| legal columns vanishes at the model, cross-checks the 7x7 determinant by both Bareiss and a completely separate Leibniz permutation expansion, expands all eight exact Fourier coefficients of the indicator, and replays the physical SAT model row by row. No exponential enumeration outside this fixed 3D control, no floating point and no modular-only rank claim.

## Audited implementation detail

An exploratory external search script initially constructed a wrong GF2 null-basis by XORing a pivot **row** when a pivot **coordinate bit** needed to be flipped; this was corrected before any fixture was accepted, and the final fixture uses only exactly verified kernel vectors. The existing checked-in BABEL-22/23 scripts already flip the pivot COORDINATE bit and assert the kernel equations. The repository algorithms are not subject to the exploratory script defect. The discovery was correctly re-run from scratch after the fix.

## Scientific change / next target

- \`BABEL23_TWO_SUFFICIENT_GATES_COMPLETE_FOR_ALL_CONNECTED_SCL = DISPROVED\` (finite exact SAT counterexample, all Fourier degrees >=1).
- \`BABEL23_GRAM_COUNT_UPPER_BOUND = PROVED_AND_NOT_AFFECTED\`.
- \`BABEL23_L1_DOMINANCE_SAT_SUFFICIENCY = PROVED_AND_NOT_AFFECTED\`.
- \`BABEL24_M1_RATIONAL_FULL_IDEAL_RANK = 7_OF_8_CERTIFIED\`.
- \`BABEL24_GLOBAL_SCL_UNSAT_DEGREE2_SUFFICIENCY = OPEN\`.
- \`UNIVERSAL_POLYNOMIAL_SOLVER = NOT_PROVED\`.
- \`P_VS_NP = OPEN\`.

**Allowed successor:** replace the l1-only SAT sufficient gate with a strictly more expressive, provably polynomial witness-recovery method (e.g. special-case indicator recognition or structured positive function certificates), and separately seek a real UNSAT instance that falsifies fixed-degree2 Fourier completeness. Do not relabel this known SAT falsifier as a lower bound against all SCL algorithms. In particular, direct SAT witness search still works here: the point is ONLY that both fixed Gram sufficient gates alone return UNKNOWN forever.
