# BABEL-26 — polynomial-composition theorem for tensor-factorized SAT indicators, and an exact linear Fourier-degree barrier

**2026-10-22. Research-only.** Parent BABEL-25 Draft PR #551, head \`d7c58f8c6d713875f1eba9433a23b616537f3f4a\`. This is an exact theorem for **independent input factors** and a counterexample to naïve Fourier expansion, NOT a universal SCL decision algorithm. The underlying tensor/Fourier identities are standard and historical novelty is NOT claimed. No TRUMP scientific-authority change, no modification to \`main\`.

## 0. Context recovery and anti-reentry classification

- Authority: \`START_HERE_TRUMP_CONTEXT.md\`; v3.23 \`registry/TRUMP_CURRENT_STATE_2026-09-16_v3.23.json\` blob \`70e8b78fedd05bedb2e2324846d83c6fceea434d\`, v3.23 overlay blob \`72af54233ebb2427894192c9904e179ece6f2708\`.
- Existing BABEL-25 all-n proof: fixed-degree Gram residual H is SAT indicator iff idempotent iff nonnegative, and sparse XOR convolution checks idempotence in P for fixed degree.
- This contribution is \`SUCCESSOR_REPAIR/DIAGNOSTIC_ONLY\`: it repairs the falsely pessimistic inference "exponential Fourier support means no polynomial representation" for independent products. It does not re-enter any exhausted TRUMP connected-mixed corpus or promote itself into a new authorized global SAT carrier.
- Existing universal P/NP firewall remains active.

## 1. Exact polynomial-composition theorem for independent SCL components

Suppose an SCL instance F decomposes as a vertex-disjoint union \`F=F_1 disjoint_union ... disjoint_union F_t\` (each component square cubic regular/linear). Its binary parity space decomposes exactly \`K=direct_sum_i K_i\`. For each i assume there is a polynomial-size, exactly verified Fourier polynomial

    H_i(alpha_i) = sum_(q in K_i*) a_{i,q} (-1)^(q·alpha_i)

with the **pointwise identity** \`H_i=1_SAT(F_i)\`. One way to certify that identity locally is BABEL-25's complete fixed-degree Gram orthogonality, \`h_i*h_i=h_i\`, and \`e0-h_i=M_i z_i\`, plus a stored exact polynomial-time replay. Other sound local certificates may be used provided they prove the same pointwise statement.

Then

    H_F(alpha_1,...,alpha_t) = product_(i=1)^t H_i(alpha_i)

is **exactly the SAT indicator** on K, is idempotent, and is represented by a product DAG with \`O(sum_i (support_i+1))\` arithmetic gates and polynomial-size coefficients (assuming local descriptions have polynomial bit sizes). **NEVER expand the product.** Certify exactness factor-by-factor and certify disjointness from the incidence graph; then no global 2^d Fourier enumeration or global S² convolution is necessary.

- Full-SAT existence: if each local indicator is nonzero (equivalently each \`a_{i,0}>0\`, since indicator is nonnegative), the product is nonzero and a model is recovered by applying positive-prefix conditional means on each local factor and concatenating the verified local models. Bit complexity is polynomial in the total input size and local proof lengths.
- Full-UNSAT: if any component has an independently verified UNSAT refutation, that same refutation (all variables and rows in the component) is also a sound global UNSAT refutation. No materialization of Cartesian products or global branching is required.
- Counting (conditional): if ALL factors carry indicator certificates, \`#SAT(F)=product_i 2^(d_i) a_{i,0}\` as exact integers. This is a theorem about those certificate-admitted factors, NOT a polynomial #SAT algorithm for general input.
- Exact runtime statement: \`T_total=O(poly(|F|+sum_i receipt_bytes_i))\` for certificate verification, local reconstruction and arithmetic composition. This is NOT a claim that all local certificates can be found in polynomial time.

The theorem can also apply to independent coordinate blocks in a fixed, explicitly provided GF2 kernel basis, if **every row's character support lies within a single block**, even when factorization is not initially obvious from syntax; a polynomial-time basis-coordinate locality checker is required. This is a conditional extension, not a discovered arbitrary invariant.

## 2. An exact LINEAR lower bound for expanded-degree Gram SAT-indicator recovery

Let U denote BABEL-24's frozen, connected 27-variable square cubic linear instance with **exactly one SAT model** and \`d_U=3\`, certified by an independent full 27-row replay and all eight kernel states in Draft PR #550. Let \`F_t\` be t disjoint copies of U. Then

    n=27t, d=3t, #SAT(F_t)=1.

Each local exact indicator \`H_U\` has all 8 Fourier coefficients nonzero (each ±1/8). Hence the global SAT indicator

    H_F = product_i H_U(alpha_i)

has **exactly 8^t nonzero Fourier coefficients**, each ±8^(-t), and admits a factorized DAG with t repeated eight-term factors (linear size). This is a strict exponential separation between the *expanded Fourier representation* and *factorized arithmetic circuit representation* for this family.

**Additional all-t degree theorem (stronger than a support-count estimate):** Let \`M_k(F_t)\` contain every allowed \`g_r chi_u\` column where \`u\` is a product of at most k **original variable characters**. Every original variable belongs to exactly one of the t blocks and its character has Fourier support in that one block. Thus any term in a single M_k column has a Fourier index whose nonzero coordinates occupy **at most k+1 distinct blocks** (at most k blocks from u and one from the row defect g_r).

But choose a character q with ONE nonzero coordinate in each of the t kernel blocks. The Fourier coefficient of \`1-H_F\` at that q is ±8^(-t) ≠0. Therefore \`1-H_F\` cannot lie in \`im M_k\` unless \`k+1>=t\`. Equivalently,

    [Gram_k residual is exact SAT indicator for F_t] ==> k >= t-1.

This is an **unconditional all-t lower bound for this PARTICULAR degree-limited Gram SAT-indicator representation**. At any \`k<t-1\`, even if F_t is SAT, its Gram residual cannot become idempotent (by BABEL-25's iff theorem). The BABEL-25 count-upper-bound UNSAT branch cannot fire on a genuinely satisfiable input either, so its three-way solver returns UNKNOWN.

It is NOT a lower bound on general SAT complexity, NOT a Nullstellensatz refutation-degree bound for UNSAT (F_t is SAT!), and does not rule out fast component decomposition. In fact the factorized certificate above solves every F_t efficiently, including t as large as desired.

## 3. Independent exact replay

\`experiments/babel26/factorized_tensor_composition.py\` re-derives the 27-row unique SAT component from frozen rows rather than relying on BABEL-25 producer imports. It:
- computes an exact GF2 parity basis and checks the eight full original assignments against all rows, establishing one model;
- computes all eight local rational Fourier coefficients, checks local XOR idempotence, local row-defect annihilation, and independent exact all-eight state replay;
- certifies the tensor-factor SAT product without expanding it for t=1,2,3,9,20,64, counting local proof gates and computing huge exact integer \`8^t\` only;
- for t=9, verifies \`n=243,d=27,#SAT=1\`, local-circuit vs support gap, exact sparse-support and block-degree lower bounds. Expands the full 8^3 Fourier coefficients only for t=3 as a finite control; t=20 and t=64 NEVER expand the Fourier product.
- verifies a second compositional case: add an independent Fano7 UNSAT component to U and show global UNSAT by an explicit all-Fano Boolean census (finite local fixture) without enumerating the product.

The local FFT/character checks use \`fractions.Fraction\` and integers, never floats/modular-only rank and never access remote state during execution.

## 4. Strict frontier: connected high-dimensional SCL

A disjoint direct product is easy to identify by ordinary graph connected components. The result **does not** prove there is a compact product/tree decomposition for arbitrary **connected** legal SCL. A general polynomial-time decomposition or low-rank quotient theorem needs: exact semantics, polynomial discovery, bounded accumulated representation states, local SAT/UNSAT proof obligations and constructive SAT witness. Research should seek connected examples with high d, high width, and no locally admitted carrier, rather than claim this trivial direct product is a universal method.

\`\`\`
BABEL26_POLYNOMIAL_TENSOR_COMPOSITION_ON_ADMITTED_FACTORS = PROVED
BABEL26_UNIQUE_SAT_INDICATOR_FULL_FOURIER_SUPPORT = 8^t
BABEL26_EXPANDED_GRAM_IDEMPOTENCE_DEGREE_NECESSITY = k>=t-1
BABEL26_GENERAL_CONNECTED_COMPOSITION = OPEN
UNIVERSAL_SolveLinearCubicXSAT = NOT_PROVED
P_VS_NP = OPEN
\`\`\`

Selected related literature background, *without asserting transfer of bounds to this quotient representation*:
- Buss, Grigoriev, Impagliazzo, Pitassi (JCSS 2001): https://www.sciencedirect.com/science/article/pii/S0022000000917264
- Dahiya, Mahajan, Mouli (SAT 2024), lower bounds for Polynomial Calculus over ±1 bases: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SAT.2024.10
