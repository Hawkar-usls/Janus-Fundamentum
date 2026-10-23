# BABEL-34 — exact local-port forcing: BABEL-33's high-k/high-width expander SAT family is uniquely satisfiable

**2026-10-23. RESEARCH-ONLY, new audit of BABEL-33 [PR #559].** Stacked on BABEL-33 exact head \`d21ecdf9953e82a32a74e7cce17be65ff706cf40\`. This is a **scientific benchmark correction and scoped positive algorithmic theorem**, NOT a universal polynomial algorithm for arbitrary SCL, a P=NP proof, or a claim of novelty over established CSP motif-elimination techniques. \`main\` and TRUMP scientific-authority registry remain unchanged.

## 1. Frozen 27-variable U and complete 3-port punctured relation

Use the exact BABEL-24 unique-SAT U (27 original variables and 27 rows, SHA256 \`9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed\`), with BABEL-33's three *removed* incidences

    p0=(row0,variable0);
    p1=(row1,variable6);
    p2=(row2,variable5).

The three distinct rows and variables are modified exactly once, while the other 24 original Exact-One rows remain physically unchanged inside each macro block.

**Exact finite lemma for this fixed U** (verified by TWO genuinely different complete procedures):

1. Drop WHOLE rows 0,1,2. The remaining 24 rows constrain 26 of the 27 variables and leave variable0 absent; there is **exactly one** satisfying assignment on those 26 constrained variables.
2. Over all 27 original variables, the complete 24-row punctured system therefore has **EXACTLY TWO** Boolean assignments, with true-coordinate index sets

       X* = (2,3,7,9,13,17,19,23,24)
       X' = (0,2,3,7,9,13,17,19,23,24).

   They differ ONLY in x0; all other original bits, including exported port bits x6 and x5, are fixed ZERO.
3. Independently verify by (A) unit-propagating exhaustive Boolean Exact-One DPLL, and (B) exact rational echelon of the 24×27 {0,1} incidence matrix: its **Q-rank is 24**, leaving precisely THREE free original coordinates \`(0,25,26)\`. Exhaustively test ALL 2^3=8 Boolean projections, reconstruct all pivots with rational arithmetic and assert that the result is exactly \`{X*,X'}\`. Neither method trusts BABEL-33's planted model as an assumption.

Define for each punctured candidate its exported port bits \`a=(x0,x6,x5)\` and required incoming bits \`b=(1−sum_(j∈row_i\{portvar_i})x_j)_(i=0,1,2)\`. Each required incoming bit must lie in {0,1} for an external Boolean variable to satisfy the edited row.

The COMPLETE local boundary data is:

| Punctured physical assignment | Exported port bits a | Required imports b | Feasible with any Boolean imports? |
| --- | --- | --- | --- |
| X* | (0,0,0) | (0,0,0) | YES |
| X' | (1,0,0) | (0,-1,-1) | **NO** |

Indeed the second assignment has the two retained literal counts equal **2** in rows1 and2. Substituting any imported Boolean bit 0 or1 cannot make these rows Exact-One. Therefore after local feasibility filtering, the boundary relation is the SINGLE tuple

    R_U = { ((0,0,0),(0,0,0)) }.

This is an **exact constant-size model**, not an incomplete heuristic. It does not rely on rank over GF2, Fourier representation, macro width or macro adjacency.

## 2. ALL-n UNIQUE SAT theorem for the entire BABEL-33 macro-expander construction

Let H be ANY simple cubic connected macro graph. Form J(H) exactly as BABEL-33 specifies: replace each macro vertex by U and cross-swap the three ports according to the edge bijections.

**Theorem.** \`#SAT(J(H))=1\` for EVERY admissible H and EVERY choice of distinct port-to-incident-macro-edge bijections.

**Proof.** Given any satisfying physical assignment of J(H), restrict it to one macro block. Since the 24 unmodified rows of U are still locally present, that assignment must be either X* or X' by the finite lemma. X' is impossible irrespective of incoming data, because its edited rows1 and2 contain two local true variables. Thus each block is forced to X*; all its three outgoing ports and all its required incoming ports are 0. The concatenation of X* over all blocks is a satisfying assignment because each edited row receives the required zero bit from its neighbor, while untouched rows are already satisfied. No other global assignment exists. QED.

Unlike BABEL-33's earlier **planted SAT only** claim, this establishes a complete unique-model theorem. This family is **computationally EASY given its verified template decomposition**, despite its graph expansion and unbounded rational kernel. No polynomial way to recognize every legal SCL as a copy of this template is claimed.

## 3. More precise GF2 barrier and scoped full algorithmic composition

BABEL-33 derived \`dim_Q ker A(J(H))>=t/2\` from rational rank-one swaps. In fact the frozen U has binary rank24 (binary nullity3) as verified independently in BABEL-24. Each of the \`3t/2\` cross-incidence swaps is a rank-ONE update over GF2 as well. Consequently, starting from rank24t,

    dim_GF2 ker A(J(H)) >= 27t - (24t+3t/2) = 3t/2 = n/18.

With **EXACTLY ONE** global SAT point and d>=n/18, its SAT indicator has exactly \`2^d\` nonzero Fourier coefficients, whereas a degree-k Gram residual contains at most \`1+4n*sum_(j<=k) binom(n,j)\` supported characters. Therefore for every fixed k and even every \`k=o(n)\`, the BABEL-25 exact-idempotence SAT test necessarily fails on all sufficiently large macro constructions. In particular **degree k=Omega(n) is NECESSARY** for that particular expanded Fourier-indicator mechanism. The physical SAT problem is nonetheless trivial from the fixed local relation. This is a **specific proof-representation lower bound, NOT** evidence that SAT has superpolynomial complexity.

Given a certified partition of the input into the U motif blocks and a verified mapping of exactly three swapped port occurrences per block, one can check all incidences in O(n) graph operations, cache the **constant** exact local relation \`R_U\`, join its forced 0-valued ports and output the unique concatenated witness with O(n) construction/verification. Thus the **full** \`T_discover(on supplied certificate)+T_local+T_compose+T_reconstruct+T_verify\` is O(n), up to normal bit-model overhead, on this CERTIFIED template-admitted class. The certificate of block partition/port mapping is not assumed available for arbitrary inputs; finding an exact matching macro substitution in an unknown graph is a separate admission/discovery problem. No unrestricted claim is made.

## 4. Benchmarks and next honest universal frontier

This corrects the scientific interpretation of BABEL-33: high graph width AND large rational/binary kernels alone do **not** imply that a benchmark is hard. The expander-macro family has a SINGLE local relation with no global choice or long-range coordination. Do not count it as evidence of universally hard instances. The parameter-bound anti-dichotomy remains true, and the expanded Fourier degree requirement is now stronger, but both are **insufficient to prove SAT hardness**.

To challenge a universal compressed-carrier candidate, generate legal **connected** high-width/high-nullity instances whose **local port relations admit multiple consistent boundary assignments**, then independently test SAT/UNSAT under whole-system composition. An input with a planted unique local state is NOT an adversarial global-solvability benchmark even if every graph-theoretic separator is large.

## Independent reproducer

\`experiments/babel34/local_three_port_forcing.py\`: stdlib-only script reconstructs U, independently proves the two exact punctured models by Boolean DPLL AND rational Gauss elimination of all 32 Boolean projections, exhaustively computes the complete port relation including the invalid negative import requirements, independently constructs valid macro SCL at t8/12/16/24/40 without importing BABEL-33 producer code, tests every physical SAT row, reconstructs all splice incidences, checks exact GF2 rank nullity, and emits explicit all-n UNIQUE-SAT and composition receipt status. No enumeration of exponential full macro parity states is attempted.

\`\`\`
BABEL34_FIXED_U_PUNCTURED_Q_RANK = 24
BABEL34_FIXED_U_COMPLETE_PUNCTURED_MODELS = 2
BABEL34_FIXED_U_VALID_BOUNDARY_RELATION = SINGLE_000_TO_000
BABEL34_ALL_CUBIC_MACRO_EXPANDER_UNIQUE_SAT = PROVED
BABEL34_GFP2_KERNEL_LOWER_BOUND = 3t/2
BABEL34_EXPANDED_GRAM_INDICATOR_DEGREE_OMEGA_N = PROVED
BABEL34_THIS_MACRO_FAMILY_GLOBALLY_HARD = NOT_ESTABLISHED
BABEL34_CERTIFIED_MACRO_ADMITTED_COMPOSITION = POLYNOMIAL
BABEL34_UNIVERSAL_SCL_SOLVER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
