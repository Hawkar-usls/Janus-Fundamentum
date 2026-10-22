# BABEL-27 — CONNECTED unique-SAT SCL family with unbounded Gram-indicator degree

**22 October 2026.** Research-only successor to BABEL-26 (#552), parent exact head \`f5b3b105234af918d94212513fcd7403b487e9dc\`. This note proves exact all-n structural and **restricted proof-representation** theorems. It is **NOT** a lower bound on all SAT algorithms, a refutation lower bound for UNSAT, or a P versus NP resolution. Main and frozen TRUMP v3.23 authority stay unchanged.

## 1. All-n row-deletion redundancy for square 3-regular Exact-One inputs

**Lemma.** In ANY square 3-uniform 3-regular Exact-One system F with n divisible by 3, every Boolean assignment satisfying n-1 of its rows necessarily satisfies the last row as well.

**Proof.** Every variable appears exactly three times; the sum of the true-bit counts across all n rows equals 3|x|. If all but one row are satisfied, those contribute n-1. Let w be the number of true variables in the remaining 3-variable row. Then

    3|x| = (n-1)+w.

Since n≡0 mod3, \`w≡1 mod3\`, and 0≤w≤3 forces w=1. QED.

This is a logical implication on ALL Boolean assignments, not just the parity kernel. The hypothesis n divisible by 3 is essential (otherwise every full SCL Exact-One instance is trivially UNSAT by total count anyway).

## 2. All-n uniqueness-preserving incidence-edge splice

Let L,R be vertex-disjoint, **connected legal square cubic/linear SCL** components, with n_L,n_R divisible by3 and each having EXACTLY ONE physical SAT model x_L,x_R. Choose row r of L and row s of R, and occurrences of variables a in r, b in s with \`x_L[a]=x_R[b]\`. Replace row incidences \`(r,a),(s,b)\` with \`(r,b),(s,a)\`. Nothing else changes.

**The splice output is legal connected square 3-regular 3-uniform linear and uniquely SAT.**

- Each row keeps size3; each variable retains exactly three occurrences; no new double intersection of two rows can occur: the two modified rows retain only two locals each and import one formerly disjoint variable. Distinct block rows originally intersect ≤1.
- The row-variable bipartite incidence graph of ANY connected k-regular bipartite graph with k≥2 has **no bridge**. If a single edge separated a vertex subset, balancing the degrees of its two color classes would give \`k(|L_S|-|R_S|)=±1\`, impossible. Thus deleting the two selected edges leaves both old incidence graphs connected, and the two new cross edges connect them.
- The original concatenated unique model still satisfies the new rows, because the swapped Boolean literals are equal.
- Conversely, in ANY SAT model of the new instance, every original row of L except r and every original row of R except s is still satisfied. By the row-deletion lemma applied separately to the OLD L,R systems, each deleted original row is necessarily also satisfied. Hence the restrictions to L,R must be their respective unique models. Therefore the concatenated model is the ONLY model.

All this is **all-n exact semantics**, including both SAT preservation and backward uniqueness; no randomness, average-case assumption, or exhaustive state enumeration is used.

## 3. Connected deterministic infinite unique-SAT SCL_t

Start from U, the certified connected 27-row, 27-variable unique-SAT SCL27 (BABEL-24 #550, frozen SHA256 \`9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed\`), with one-index set

    (2,3,7,9,13,17,19,23,24).

At step t, take the already connected unique-SAT component \`C_(t-1)\` and a fresh separate copy U. Deterministically choose a zero-valued literal from **row0 of C_(t-1)**, and a zero-valued literal from **row0 of the new U**, then perform one splice. At every step the new concatenated model remains the unchanged t-fold copy of U's unique model. The graph remains legal, connected and linear by the all-n splice theorem.

By induction, for **EVERY t≥1**:

    C_t is connected legal square/3-uniform/3-regular/linear SCL
    n=27t, #SAT(C_t)=1.

The construction is O(poly(t)) in explicit physical incidence size (one splice per component). The unique model is polynomially reconstructible **from the construction receipt**; no claim this class is computationally difficult.

## 4. All-n GF2 nullity lower bound

Let A_t be the binary incidence matrix. Initially, t disjoint copies U have GF2 rank 24t and nullity 3t. A single edge-splice between old row indices r,s and variables a,b changes the incidence matrix over GF2 by a rank-ONE outer product

    A' = A + (e_r+e_s)*(e_a+e_b)^T.

Consequently a single splice can increase rank by at most 1. After t-1 splices, the final connected incidence rank is at most 24t+(t-1), so

    d_t=dim_GF2 ker(A_t) >= 27t-25t+1 = 2t+1.

No claim of exact equality for all t without additional proof; the independent fixture checker computes actual exact d_t on selected sizes.

## 5. Exact fixed-degree Gram idempotence NO-GO for CONNECTED instances

A function which is the indicator of a SINGLE point in the d_t-dimensional K_t has exactly **2^d_t nonzero Fourier coefficients**, every one equal in magnitude to 2^(-d_t). The BABEL-25 all-n theorem proves that if the fixed degree-k Gram residual is idempotent, it must be this exact indicator.

But its sparse Fourier dictionary has at most

    S_k <= 1+4E_k,
    E_k <= n * sum_(j=0)^k binom(n,j),

because every legal degree-k row multiplier has at most four Fourier frequencies. At fixed k, this is polynomial in n=27t; while 2^d_t≥2^(2t+1) is exponential. Thus, for EVERY fixed k, sufficiently large CONNECTED \`C_t\` are SAT but make the BABEL-25 idempotence SAT gate **necessarily FAIL**. The sound UNSAT branch also cannot fire on a SAT instance. This closes the proposed fixed-degree two-terminal completion even under a connectedness promise.

**Stronger asymptotic degree lower bound:** since \`d_t >= (2/27)n+1\`, the binomial entropy bound \`sum_(j<=k)binom(n,j)<=2^(n H_2(k/n))\` for k<=n/2 shows that if \`k/n\` tends to zero, \`log2 S_k=o(n)\` but \`d_t=Omega(n)\`. Therefore any k admitting an exact degree-k Gram SAT indicator on this family must satisfy

    k = Omega(n)  as t -> infinity.

This is a real linear degree requirement for the **specific expanded Fourier-multiplier indicator representation on these SAT examples**. It is NOT an UNSAT proof degree lower bound and does NOT transfer to general SAT computational time. Notice that the unique SAT model is provided by our construction in linear-size metadata, so this family is purposely **algorithmically easy** despite its proof-system obstacle.

The all-n arbitrary-input BABEL-25 *soundness* and idempotence characterization remain intact. Only universal fixed-degree *completeness* is refuted.

## 6. Independent exact controls

\`experiments/babel27/connected_unique_sat_splice.py\`:
- reconstructs the certified U and its single model from every one of the eight local GF2 words, checks 27-by-27 incidence legality and connectivity;
- performs deterministic zero-valued incidence swaps for t=1,2,3,5,9,20,64; independently validates 3-uniform 3-regular linear connected incidence after every splice, and exactly computes GF2 rank;
- checks the concatenated model directly against ALL rows at every size; for small t it independently enumerates the full GF2 kernel and confirms the sole SAT solution;
- independently verifies every selected splice is a rank-one GF2 incidence update and the 2t+1 lower bound;
- computes the fixed-degree2 column support ceiling and shows it is strictly LESS than 2^d at the large connected examples, without enumerating that Fourier support or the parity cube.

The all-n proof is written above. Finite controls are regression evidence, not the source of an induction proof.

## 7. Permanent firewall and next mathematical obligation

- \`CONNECTED_UNIQUE_SAT_SPLICE_THEOREM = PROVED\`.
- \`CONNECTED_SCL_t_UNIQUE_SAT_FOR_ALL_t = PROVED\`.
- \`CONNECTED_KERNEL_NULLITY_d_t_GE_2t_PLUS_1 = PROVED\`.
- \`CONNECTED_SAT_INDICATOR_GRAM_FIXED_DEGREE_INCOMPLETENESS = PROVED\`.
- \`CONNECTED_SAT_INDICATOR_GRAM_NECESSARY_DEGREE_OMEGA_N = PROVED\`.
- \`UNSAT_FOURIER_M2_COMPLETENESS = OPEN\` (this family is SAT).
- \`POLYNOMIAL_COMPLETION_FOR_GENERAL_CONNECTED_SCL = OPEN\`.
- \`UNIVERSAL_SolveLinearCubicXSAT = NOT_PROVED\`.
- \`P_VS_NP = OPEN\`.

**Next step toward actual P=NP target:** Any future representation must decouple *proof discovery and witness recovery* from complete Fourier indicator expansion. Seek exact polynomial discovery of more general, possibly overlapping/connected factor circuits, with all-n polynomial composition and semantics-preserving SAT/UNSAT reconstruction. Neither connectedness, unique satisfiability nor growing kernel dimension by themselves prove any computational hardness.
