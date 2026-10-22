# BABEL-25 — exact sparse Fourier idempotence test equals full nonnegativity test for Gram residuals

**2026-10-22. Research-only exact theorem for ALL legal SCL at each FIXED Fourier multiplier degree.** Successor to BABEL-23 (#549) and the connected sparse-SAT l1 falsifier BABEL-24 (#550). No scientific authority/main promotion, no P=NP claim.

## ALL-N THEOREM: three conditions are mathematically EQUIVALENT

Let A be a legal square 3-uniform, 3-regular, linear Exact-One instance. Let K=ker_GF2(A) of dimension d, and let g_r(v)=1+chi_a(v)+chi_b(v)+chi_c(v) on K. Its values are exactly 0 (legal row) or 4 (forbidden all-zero v row). Let M_k contain ALL Fourier coefficient columns of products g_r * chi_u for characters represented by <=k original variable characters, **including u=0**. Let z solve Gram normal equations (M_k^T M_k)z=M_k^T e0 over Q, and h=e0-M_k z; denote by H(v)=sum_q h_q chi_q(v) the real Fourier function.

Then the following are **equivalent** for every input and every k:

1. \`H(v)>=0\` for EVERY v in K (pointwise nonnegativity);
2. \`H(v)^2=H(v)\` for EVERY v in K (pointwise idempotence);
3. \`H(v)=1\` if v is an Exact-One solution, and \`H(v)=0\` otherwise (the EXACT SAT indicator).

**Proof:**

- Because e0-M_k z is an exact representation, H(v)=1 at EVERY true SAT point, regardless of coefficient values or k.
- Because unshifted g_r columns are included, Gram orthogonality gives \`0=<H,g_r>=2^-d sum_(v in K) H(v)g_r(v)\` for EACH row.
- If H>=0, every summand H(v)g_r(v) is nonnegative; equality forces H(v)=0 whenever g_r(v)=4. Hence H=0 at any nonsolution, H=1 at every solution: condition (3).
- A Boolean-valued indicator is idempotent: (3) implies (2).
- Over Q/R, \`a^2=a\` implies a in {0,1}, so (2) implies (1).

**Crucial computational improvement:** Unlike arbitrary polynomial nonnegativity testing, exact idempotence of THIS special sparse Fourier Gram residual can be checked in deterministic **polynomial time for fixed k**, WITHOUT enumerating the 2^d states. Expand H^2 by XOR-convolution

    (h*h)_q = sum_(u xor v = q) h_u h_v,

compare all rational coefficients to h, and accept iff h*h=h. Each legal g_r chi_u column has <=4 frequencies, so h has S<=4E+1 with E<=n*sum_(j<=k)binom(n,j). The convolution has at most S^2 summands and coefficient bit sizes remain polynomial for any fixed k after exact Gram computation. The test requires NO external PIT oracle and NO unproven positivity relaxation.

### Constructive SAT recovery

If h0>0 and h*h=h, average(H)=h0>0. Thus H is a nonzero 0/1 indicator of real SAT solutions. In kernel coordinates v=sum_i alpha_i * basis_i, compute the exact conditional mean of H on a partial assignment of alpha_0,...,alpha_(i-1): retain only Fourier terms q with no unassigned coordinate bits; multiply their signs from the fixed prefix. Because H>=0 and the parent conditional mean is the average of two children, choosing any child with positive mean preserves positivity. After d choices, H(v)=1. Reconstruct x=1+v and independently replay every Exact-One row.

This is deterministic polynomial time for fixed k, using only exact rationals. A sound three-valued solver is now:

    h := exact_Gram_residual(F, degree=k)
    if h0==0 or 2^d*h0<1: return UNSAT
    if h0>0 and XOR_CONVOLUTION(h,h)==h:
        x := recover_by_positive_conditional_means(h, K_basis)
        assert verifies_exact_one(F,x)
        return SAT,x
    return UNKNOWN

This SAT gate is **strictly stronger** than BABEL-23's l1 dominance: l1 dominance implies H>=0, hence idempotence by the all-n theorem. The converse is false, proved by the frozen connected unique-SAT SCL27 (#550): h0=1/8, l1-tail=7/8, but h is the true point indicator and h*h=h. The new test correctly recovers its unique satisfying assignment, so it repairs that specific failure.

**No general completeness!** An UNSAT F may have h0>0 and an SAT F may have a sign-changing residual at fixed k. Unless one of the certified terminal criteria fires, result stays UNKNOWN; \`P_VS_NP = OPEN\`.

## Independent exact regression and provenance

\`experiments/babel25/idempotent_gram_sat_recovery.py\` uses Python stdlib fractions to:
- reconstruct the frozen BABEL24 connected SCL27 fixture and independently reproduce its GF2 rank and exact unique true assignment;
- prove it is the true degree1 Gram residual via exact 7x7 rational linear system for the spanning M1 columns and orthogonality against ALL full M1 generators;
- compute the complete XOR convolution h*h, prove exact equality, and recover a physically verified SAT model via positive conditional expectations; its BABEL-23 l1 test remains FALSE;
- replay affine SCL9 SAT indicator (h0=3/4, idempotent) and Fano7 degree0 signed residual (h0=9/16, NON-idempotent, so no false SAT).

All machine results are finite control replays supporting the symbolic all-n theorem above. No floating point, Monte Carlo, or modular-only conclusions.

## ALL-N NECESSARY SPARSITY BOUND: idempotence still has a fixed-degree barrier

The new idempotence test is complete for **nonnegative Gram residuals**, but it CANNOT be universally complete at fixed k across all (including disconnected) legal SCL instances. This follows from the uncertainty principle by a short direct calculation, requiring no external theorem.

**Theorem.** Suppose F has exactly s>0 satisfying K points among the 2^d parity states. Let E_k be the number of legal degree<=k row-multiplier columns. If the Gram residual is idempotent, it equals f=1_SAT. Write f's normalized Fourier coefficients \`h_q=2^-d sum_(v in SAT) chi_q(v)\`. Then

    |h_q| <= s / 2^d
    sum_q h_q^2 = s / 2^d

by triangle inequality and Parseval. If T is the number of NONZERO coefficients, then

    s / 2^d <= T * (s/2^d)^2  =>  T >= 2^d / s.

But by construction \`h=e0-M_k z\`, where each multiplier column has at most 4 Fourier frequencies, so \`T<=1+4E_k\`. Therefore

    IDEMPOTENCE POSSIBLE  ==>  s*(1+4E_k) >= 2^d.
    s*(1+4E_k) < 2^d  ==>  IDENTITY TEST MUST FAIL, even on SAT.

For fixed k, \`E_k<=n*sum_(j=0)^k binom(n,j)=O(n^(k+1))\`. Hence on a SAT family with \`d=Omega(n)\` and subexponentially many SAT assignments s, the fixed-degree Gram residual is necessarily non-idempotent for sufficiently large n. This is a **proof-system/certificate restriction**, NOT a generic SAT lower bound.

Concrete illustrative infinite family (NOT a connected hardness claim): take t disjoint copies of the certified BABEL24 connected SCL27 unique-SAT component. The disjoint union is a valid 3-uniform, 3-regular, linear square Exact-One instance with n=27t, d=3t and s=1. For any fixed k,

    1+4E_k <= 1+4*(27t)*sum_(j=0)^k binom(27t,j) = polynomial(t),

but \`2^d=8^t\` eventually exceeds it. Thus for sufficiently many components the new fixed-degree idempotence SAT gate necessarily returns UNKNOWN (while the UNSAT gate cannot fire on a satisfiable input). A solver that decomposes disjoint components can of course solve this family; **no connected-SCL or general-algorithm hardness conclusion follows**.

This result delineates the actual path to a universal proof: one must either show adaptive polynomial degree/size for the relevant connected adversarial family, or introduce a compact representation/positivity gate whose exact construction and verification do not require an exponentially supported Fourier indicator. Merely improving the idempotence checker cannot bypass this information-theoretic support condition.

## Further frontier

1. Find or prove a polynomial-size k (or alternate compressed representation) ensuring for EVERY SAT input either H is idempotent or another efficient SAT-witness mechanism works. The demonstrated idempotence is still a sufficient condition, not a universally complete method.
2. Separately attack **UNSAT** instances where degree2 M2 lacks e0; require exact full-M2 dual with h0>0 and independent UNSAT proof.
3. Preserve \`T_construct+T_solve+T_reconstruct+T_verify <= poly(|F|)\` INCLUDING bit length. Do not classify any finite successful test as generic P=NP.

\`\`\`
BABEL25_ALL_N_GRAM_NONNEGATIVITY_IFF_IDEMPOTENCE_IFF_SAT_INDICATOR = PROVED
BABEL25_FIXED_DEGREE_SPARSE_IDEMPOTENCE_TEST_IN_P = PROVED
BABEL25_CONDITIONAL_SAT_WITNESS_RECOVERY_IN_P = PROVED
BABEL25_CONNECTED_SCL27_L1_FALSIFIER_REPAIRED = PROVED
BABEL25_UNIVERSAL_COMPLETENESS = OPEN
GENERAL_SAT_IN_P = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
