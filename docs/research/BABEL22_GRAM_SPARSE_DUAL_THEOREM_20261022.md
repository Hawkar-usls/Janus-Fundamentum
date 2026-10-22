# BABEL-22G — constructive sparse rational left dual for FULL degree-2 Fourier M2

Date: 2026-10-22. Scope: **all legal SCL inputs, fixed Fourier multiplier degree <=2**. This is an elementary exact linear-algebra consequence extending the existing BABEL-21G Gram rank theorem, not a claim of historical mathematical novelty.

## Theorem (all n; constructive polynomial-size full-M2 dual)

Let F be any legal square cubic/linear Exact-One instance on n variables. Compute its GF(2) kernel K of dimension d and variable character labels \lambda_j in the dual group K*. Let Q_2 consist of the distinct characters represented by a product of at most two variable characters. For every row r=(a,b,c) and q in Q_2 define the four-frequency Fourier column

    m_(r,q) = e_q + e_(q xor lambda_a) + e_(q xor lambda_b) + e_(q xor lambda_c).

Let M denote the matrix of ALL such legal columns, with target e_0, and E its number of columns. Then E <= n (1+n+choose(n,2)) = O(n^3). Define G=M^T M and c=M^T e_0. Both are computable from constant-size column-support intersections, in polynomial time and bit complexity, WITHOUT materializing K's 2^d Fourier rows. Every G_ij is an integer in [0,16], and every c_i in [0,4].

The system Gx=c is always solvable over Q. Choose any exact rational solution and define the formally sparse Fourier vector

    h = e_0 - Mx.                            (1)

By construction, M^T h = c-Gx=0 against EVERY legal column of M, not only transfer columns or a sampled subset. Also

    h_0 = 1-c^T x = h^T h >= 0.             (2)

The last equality uses M^T h=0 and e_0 = Mx+h. Thus there is an exact exhaustive dichotomy:

- h_0=0: h=0 and Mx=e_0. This is a rational UNSAT certificate within degree2, constructible and verifiable in polynomial time.
- h_0>0: H=h/h_0 satisfies H^T M=0 and H(e_0)=1, a **full degree-2 rational dual obstruction**, constructible and verifiable in polynomial time. This says degree2 certificates are absent. **It does not entail SAT:** a higher-degree UNSAT instance might also have this obstruction.

Crucially, from (1) the dual has at most 4E+1 Fourier frequencies in its explicit support (often fewer after cancellations). A rational left-kernel witness is not forced to use exponentially many Fourier entries even when the ambient Fourier space has 2^d rows.

Because G has polynomial order and bounded integer entries, standard exact fraction-free rational linear algebra (with Hadamard bounds on minors) ensures polynomial total bit complexity for computing x, h, and their checking receipts.

### Guardrails

This proves a polynomial-time full-degree2 **classification** and sparse proof-carrying dual construction. It DOES NOT prove that every UNSAT SCL admits a degree2 certificate. A full-M2 obstruction produced on a SAT input is expected and not a lower bound for general SAT. To falsify universal degree2 sufficiency, first independently prove some F UNSAT and then reconstruct a full-M2 h_0>0 witness on that SAME F. To prove the user's desired P=NP through this route, prove for EVERY legal UNSAT F that h_0=0; this remains OPEN.

## Implementation and exact controls

Script: \`experiments/babel22/gram_sparse_dual.py\`. It builds the full fixed-degree columns, their Gram and exact rational solution; reconstructs and replays all Fourier coefficients of the positive/negative output on small fixtures. It uses only Python's standard library; it never imports existing BABEL source or an independent purported verifier.

Previously tested exact Q fixtures (no novelty claim):
- Fano SCL7: degree0 h_0=9/16 >0, 8 Fourier frequencies in h; degree1 and degree2 h=0 (positive UNSAT identity).
- Affine SCL9: 3 Exact-One solutions; degree0, degree1 and degree2 h_0=3/4 >0 (correctly no UNSAT certificate).
- These tests check every legal column under each specified degree; not an approximate rank, modular-only hit or partial transfer space.

## Current scientific frontier

\`\`\`
ALL_N_FIXED_DEGREE2_SPARSE_DUAL_CONSTRUCTION = PROVED
POLYNOMIAL_TOTAL_BIT_COMPLEXITY_FIXED_DEGREE2 = PROVED
FULL_M2_LEFT_DUAL_SEARCH_MECHANISM = AVAILABLE
SCL_UNSAT_DEGREE2_UNIVERSAL_COMPLETENESS = OPEN
SCL_GENERAL_POLYNOMIAL_SOLVER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`

BABEL-21 proof-system bound vs problem bound vs general SAT bound firewall remains in force. No TRUMP authority or mainline change.
