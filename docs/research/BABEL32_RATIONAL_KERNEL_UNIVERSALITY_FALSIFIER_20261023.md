# BABEL-32 — universal-input rational-kernel gate and exact no-go to naïve polynomial completion

**2026-10-23, RESEARCH ONLY**. Stacked on BABEL-31 #557 at head \`c4d36d5c228810720706fac8183145e09e65df49\`; \`main\` and authority registry unmodified. Scope is all legal SCL inputs, but a **polynomial COMPLETE decider only when rational kernel dimension k=O(log n)**. This is elementary exact algebra, NOT a claim of historic novelty or an unconditional polynomial SAT algorithm.

## 1. All-input equivalence, exact certificate, complexity

For any square 3-uniform/3-regular/linear positive Exact-One SCL on n variables, let its rational n×n incidence A have A·1=3·1. Thus

    A x = 1   <=>   x = (1/3)·1 + y,   A y = 0.

Every satisfying Boolean x lies in this rational affine solution space, and conversely any x∈{0,1}^n satisfying A x=1 is exactly a valid physical SAT model (the original row equations are binary Exact-One).

Compute rational row-echelon form of A over Q, with rank n−k and k free **original variable coordinates** F. The linear projection x→(x_j)_(j∈F) is INJECTIVE on the entire affine space, as standard back-substitution uniquely reconstructs every pivot coordinate from free coordinates. Consequently:

- Each SAT assignment is uniquely determined by **k bits**, even if \`dim_GF2 ker A\` is much larger.
- There are at most 2^k SAT models, and the EXACT count and a full physical witness are recovered by testing each free Boolean bit vector, reconstructing the other rational x_j, requiring all x_j∈{0,1}, and replaying EVERY original row.
- A zero count is a complete UNSAT theorem on that input, because all binary projections were exhaustively tested; no heuristic success criterion or incomplete DPLL is involved.

Deterministic exact total time/bit complexity \`2^k poly(n)\`: rational Gaussian coefficients of a {0,1} matrix have polynomial-size bit lengths by determinants/Hadamard, and the n×n matrix is explicitly given. Hence if k≤c log₂ n for a fixed c the full decision/reconstruction/certificate verification is polynomial **regardless of graph cut width**.

An explicit production \`max_nullity\` admission threshold in the verifier returns \`UNKNOWN_Q_KERNEL_BUDGET\` if k exceeds the budget. It NEVER reports UNSAT merely because this rational dimension is large. Note that \`n%3≠0\` is unconditional UNSAT by \`3|x|=n\`, independent of this gate.

## 2. A new infinite CONNECTED 3-partite cubic-linear family with EXACT k=2 and SAT count3

Let m≥7 be odd, 1<h<m and gcd(m,h)=gcd(m,h−1)=1. Let variable groups \`A_i,B_i,C_i\` for i∈Z_m, total n=3m. Define exactly n rows indexed by \`(c,i)\`, c=0,1,2 and i∈Z_m:

    row(c,i) = { A_i, B_(i+c mod m), C_(i+c*h mod m) }.

All rows/variables have degree 3; no pair of variables co-occurs in two rows (the distinct shifts of A-B, A-C, B-C use invertible h and h−1, with m odd), and the bipartite incidence graph is connected (the c0 and c1 rows propagate shifts by1).

**All-n exact rational rank theorem:** Fourier-diagonalize the cyclic shifts i∈Z_m over complex mth roots z. The matrix acting on the three variable-group Fourier amplitudes at frequency z is

    V(z) = [ [1,1,1], [1,z,z^h], [1,z²,z^(2h)] ].

Its Vandermonde determinant is \`(z−1)(z^h−1)(z^h−z)\` (up to an irrelevant sign). For z^m=1 and z!=1 the gcd hypotheses ensure ALL three factors are nonzero. At z=1, rank(V)=1, with nullity 2. Therefore the whole rational incidence matrix has EXACT rank \`3m−2\` and \`k=2\` (rank invariant under extension Q→C).

Its affine rational Boolean solutions have values constant in each variable group, with \`x_A+x_B+x_C=1\`. Thus exactly THREE models exist: all A=1, all B=1, or all C=1. This is **all-n** and independent of any separator structure; no empirical rank extrapolation.

A convenient deterministic infinite subsequence is \`m=L²+L+1\`, \`h=L+1\`, for every integer L≥3. Both gcd conditions hold because \`gcd(L,m)=gcd(L+1,m)=1\`, and m is always odd. Finite Fraction controls use L=3,4,5,6, i.e. n=39,63,93,129. They must each reconstruct rank n−2 and three exact Boolean witnesses.

## 3. CONNECTED counterfamily to a global small-rational-nullity assumption

The BABEL-24 certified connected SCL27 unique-SAT input U has exact \`rank_Q(A_U)=25\`, hence k=2 (verified via explicit exact rational elimination). Let \`C_t\` be BABEL-27's deterministic t-block connected unique-SAT splice chain: start with t disjoint copies U (n=27t, exact rational rank25t), then perform t−1 cross-incidence swaps choosing equally valued literal occurrences. Each splice changes the incidence matrix over Q by a **rank-one update**

    ΔA=(e_r−e_s)(e_b−e_a)^T,

so \`rank_Q(A_Ct) ≤ 25t+(t−1)=26t−1\`, yielding

    k_Q(C_t) = nullity_Q(A_Ct) ≥ t+1 = n/27+1.

BABEL-27 already proves C_t is legal, connected and unique-SAT for ALL t. Thus no theorem \`every connected SAT SCL has k_Q=O(log n)\` is possible. This is a lower bound for the **specific rational-kernel Boolean-projection enumeration parameter**, NOT evidence that C_t needs exponential time by every algorithm: BABEL-30/31 solves the same connected chain via narrow separators.

## 4. Exact machine receipts and firewall

\`experiments/babel32/rational_kernel_gate.py\` is a standalone independent all-Fraction echelon implementation. Frozen controls include BABEL24 connected SCL27 SATcount1, BABEL29 connected double-cross SCL54 SATcount2, connected double-straight SCL54 SATcount1, and cyclic legal connected families with n39/63/93/129 SATcount3 and k=2. A seven-copy disjoint SCL27 instance with k=14 MUST return \`UNKNOWN_Q_KERNEL_BUDGET\` when cap12.

The all-n proofs are mathematical derivations above. CI may confirm finite tests but cannot promote \`k=O(log n)\` to a universal bound.

\`\`\`
BABEL32_ALL_INPUT_AFFINE_Q_KERNEL_REDUCTION = PROVED
BABEL32_BOOLEAN_PROJECTION_COMPLETE_COUNT = PROVED_WITH_2^k
BABEL32_P_TIME_WHEN_Q_NULLITY_O_LOG_N = PROVED
BABEL32_CYCLIC_3PARTITE_k_EQ_2_AND_SATCOUNT_3 = PROVED
BABEL32_CONNECTED_Q_NULLITY_LINEAR_COUNTERFAMILY = PROVED
BABEL32_ALL_CONNECTED_SCL_Q_NULLITY_LOG_BOUND = DISPROVED
BABEL32_GENERAL_POLYNOMIAL_SOLVER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`

**Required next actual P=NP frontier:** an all-input polynomial-time certificate construction/composition mechanism that simultaneously overcomes BOTH regimes: arbitrarily large graph frontier W,B and k_Q=Omega(n). A portfolio of individually parameterized methods does not establish universal polynomiality unless an ALL-n dichotomy plus polynomial total composition is independently proved.
