# BABEL-23 — two-sided, proof-carrying Fourier/Gram decision gates

**Research Draft, 2026-10-22.** Parent #548 BABEL-22G. All statements below are elementary exact finite-group Fourier/linear-algebra consequences, not a claimed world-priority result or a proof of P=NP. All calculations are rational; no probability, floating point, or modular inference is accepted as proof.

## All-n theorem: Gram residual bounds the NUMBER of satisfying assignments

Let F be any legal SCL input, A its n-by-n incidence, K=ker_GF2(A), d=dim K. Write v=1+x, so that any Exact-One solution x corresponds to v in K. Let chi_q be the characters of K, and g_r(v)=1+chi_a(v)+chi_b(v)+chi_c(v), where (a,b,c) is row r; g_r(v) is 4 on the forbidden all-zero v-pattern and 0 on the allowed 2-one v-pattern.

For a fixed multiplier degree k, let M_k include **all** columns (g_r chi_u)'s Fourier coefficient vectors with degree(u)<=k and let e0 be the constant Fourier vector. Form exact G=M_k^T M_k, c=M_k^T e0 and solve Gz=c over Q. Let h=e0-M_k z, written as its polynomially sparse Fourier dictionary; H(v)=sum_q h_q chi_q(v).

By normal equations and Parseval:

    M_k^T h=0
    h_0=||h||^2=2^-d sum_(v in K) H(v)^2 >=0.

At every genuine SAT assignment v, every g_r(v)=0, so H(v)=1. Consequently:

    0 <= #SAT(F) <= floor( 2^d * h_0 ).              (★)

The bound is **valid for every legal SCL, every fixed k**, regardless of whether the limited proof system is complete. A rational result 2^d*h0 < 1 is a sound unconditional **UNSAT certificate**, even if h0 is positive. h0=0 is the BABEL-22G certificate as a special case. A positive h0 otherwise is NOT evidence of SAT.

### All-n theorem: a CHECKABLE nonnegative residual provides a real SAT witness

If h0>0 and h0 >= sum_(q!=0)|h_q|, then H(v)>=0 for every v in K by the triangle inequality. Orthogonality with each constant-multiplier column gives

    0 = <h, g_r> = 2^-d sum_(v in K) H(v)*g_r(v).

Since both factors are nonnegative, every v with H(v)>0 must have g_r(v)=0 for **each** r. Since the average of H is h0>0, some such v exists. Moreover, it can be FOUND in deterministic polynomial time with exact rationals:

- express K by a GF2 basis and fix its d coordinate bits sequentially;
- the mean of H conditional on a fixed prefix of length i equals the sum of sparse coefficients h_q whose character q has no bit in positions i..d-1, multiplied by the already-fixed signs;
- at each step, choose a bit whose conditional mean remains strictly positive (one exists since the parent is the average of its two children);
- at length d, obtain H(v)>0, reconstruct x=1+v, and explicitly check all Exact-One rows.

The SAT model, plus the finite exact rational dominance check and full-M_k dual replay, are independently verifiable. This is a **two-sided polynomial-time PARTIAL solver**:

    if h0 == 0 or 2^d*h0 < 1: UNSAT
    elif h0 > 0 and h0 >= sum_(q != 0)|h_q|:
        reconstruct satisfying assignment by positive conditional means
        return SAT, witness
    else: UNKNOWN

Always re-verify the output model. This has polynomial total bit complexity for any FIXED k because E<=n sum_(j<=k) binom(n,j), each column support<=4, and the Gram equation system has polynomial dimension and bounded integer entries.

## Scope and critical gap

None of the preceding inequalities implies that all UNSAT instances satisfy 2^d h0<1, or that all SAT instances satisfy the l1 dominance condition. They may both fail: \`UNKNOWN\` is an ESSENTIAL result. The conditional means do not confer an efficient general-purpose nonnegativity test for arbitrary sparse Fourier polynomials; only the stated *sufficient* l1 bound is checked.

More general SOS/sum-of-nonnegative-circuits certificates are a possible candidate route, but their existence and **polynomial construction** remain completely OPEN.

For maximum multiplier degree >=d, all K-characters are available (the coordinate functions generate K*). Over the full Fourier algebra, M has range exactly all functions vanishing on SAT points, hence h0=#SAT/2^d. At bounded k, the hierarchy of h0 is non-increasing and upper-bounds this true SAT fraction, without guaranteeing convergence at fixed k.

## Exact independent regression fixtures

- Fano7, k=0: d=3, h0=9/16, tail l1=21/16, residual function H(0)=-3/4 and H(v)=3/4 at the other seven parity words; **no false SAT**, bound #SAT <= floor(8*9/16)=4 (true 0).
- Fano7, k=1: h0=0, exact UNSAT certificate and 0 upper bound.
- Affine9, k=0: d=2, h0=3/4, l1 tail=3/4, inverse Fourier H has values (0,1,1,1), **explicit SAT witness reconstructed by conditional means**, #SAT exact=3 and bound 4*(3/4)=3.

Verifier: \`experiments/babel23/gram_two_sided.py\`. Independent source-level all-n proofs above; tests are finite regressions only.

## Firewall

- Fixed-degree rational Gram **cannot** be assumed complete on all UNSAT SCL.
- Support compression, coefficient bounds and exact verification do **not** imply proof existence, nor SAT witness reconstruction in every case.
- The fact that #SAT upper-bounding by Gram residual is polynomially computable for k fixed does not mean counting is polynomially solvable.
- \`P_VS_NP=OPEN\`, \`GENERAL_SAT_IN_P=NOT_PROVED\`, and research branch only; never alter main.
