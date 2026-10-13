# R5 — Attempt at the universal GF(3) polynomial-calculus degree theorem: symplectic-cover attack and exact proof-to-algorithm gate

Date: 2026-10-13, original source PR #516 DRAFT, branch `research/r5-cubic-flow-smith-pair-20261011`.
Research objective: one **unconditional uniform deterministic polynomial-bit-time sound-and-complete** `SolveLinearCubicXSAT` on EVERY legal square+cubic+linear Positive Exact-One original source, returning a SOURCE-valid SAT witness or correct UNSAT.

**THE CENTRAL THEOREM REMAINS UNPROVED.** No universal `LoopZeroTest`, no proved constant GF3 degree d, no P=NP; `P_VS_NP=OPEN`.

## 1. The exact universally sufficient theorem

For an original legal SCL on n Boolean variables, write for each original row C_i={a,b,c}

```
E_i=x_a+x_b+x_c-1 ∈ F3[x_0,...,x_(n-1)],
B_j=x_j²-x_j.
```

Because Boolean clause cardinality belongs to {0,1,2,3}, the congruence E_i=0 over F3 is EQUIVALENT to original Exact-One, without additional spurious Boolean roots.

For any d≥1 define (Boolean quotient with multilinear reduction)

```
V_d(F) = Span_F3{ E_i · x_M mod (B_0,...,B_(n-1))
                   : i∈source rows, M subset original variables,
                     |M|≤d−1}.
```

**Unconditional soundness:** if `1∈V_d(F)`, then original F is UNSAT. Source certificate is a linear combination of ORIGINAL source clause generators multiplied by squarefree monomials, with independent verifier checking constant polynomial1 modulo B_j.

**Unconditional dual completeness FOR FROZEN d:** if `1∉V_d(F)`, Gaussian elimination produces an exact F3-linear functional y on all multilinear monomials of degree≤d with
`y(1)=1`, `y(E_i*x_M)=0` for EVERY original i, |M|≤d−1. This is a VALID obstruction to a degree-d refutation, NOT evidence that F is SAT. Both primal and dual certificates are independently source-replayable by earlier R5 code.

**Conditional universal theorem:** IF there exists a FIXED CONSTANT d, independent of all input data, such that for EVERY legal original SCL F,

```
F UNSAT  ⇔  1∈V_d(F),
```

THEN a uniform deterministic polynomial-time source decision algorithm exists, because

```
N_d(m) = Σ_(j=0)^d binom(m,j) = O(m^d)   ambient monomials
G_d(m) = m Σ_(j=0)^(d-1) binom(m,j) = O(m^d)
                                                    generators
```

and dense exact F3 elimination tests 1∈span in O(G_d N_d²)=O(m^{3d}) F3 operations and polynomial memory. Each F3 element costs constant bits; all original clauses and coefficients have polynomial indexing bits. This is an EXPLICIT worst-case polynomial bit bound FOR FIXED d, not dependent on measured CI runtimes.

Prior authenticated G10/G11 source-preserving unary-pin compiler transforms any q<=n original Boolean pins into an ordinary UNPINNED legal square+cubic+linear source of size m=n+21q<=22n, preserving SAT iff SAT and multiplying counts by 2^q. Therefore querying the same unpinned degree-d test at most n+1 times recovers an independently checked original SAT witness, with overall F3 field-operation upper bound O(n (22n)^{3d})=O(n^{3d+1}), plus lower-degree source construction/audit. For d=3 specifically the CONDITIONAL gross bound is O(n^10).

**Thus proving a universal fixed d (e.g. d=3) would really imply P=NP.** No claim that the hypothesis holds follows from finitely many green workflows. Conversely, if P!=NP, such a constant cannot exist; this is a CONDITIONAL complexity statement, NOT a proof of P!=NP.

## 2. New actual source geometry: symplectic generalized quadrangle SCL15

Let points be the 15 nonzero vectors a∈F2^4, and let the alternating bilinear form be

```
〈a,b〉 = a_0 b_1 + a_1 b_0 + a_2 b_3 + a_3 b_2  (mod2).
```

For every independent a,b with 〈a,b〉=0, the three vectors {a,b,a XOR b} form a totally isotropic F2²-line. Their unique set gives exactly 15 original source clauses, one clause per line, with original variable set the 15 points.

Proof of SOURCE legality:
- for any nonzero a, the orthogonal hyperplane contains 8 vectors; excluding {0,a} leaves 6 b, paired as b↔b XOR a, so exactly 3 distinct lines contain a; every variable has degree3;
- each source clause contains exactly 3 distinct points and there are 15 clauses, so source square/cubic;
- any two distinct projective F2²-lines intersect in at most one point, so incidence C4-free/linear;
- the bipartite Tanner graph is connected and girth≥8 (the generalized quadrangle); finite source checker verifies connectivity and basic girth controls.

An independent exact original enumeration over 2^15 Boolean words gives EXACTLY SIX SAT assignments (certified finite, no general inference).

For s=2 or s=3, replacing each Tanner incidence by an independent cyclic permutation of the s sheets yields an ordinary legal original SCL of n=15s rows/variables, retaining source cubicity, C4-freeness, and connectedness (checked). Every original SAT assignment lifts by copying its bit to all sheets; hence the covers are SAT with at least six original witnesses, verified directly.

This is a useful ORIGINAL SOURCE testbed for polynomial degree, not a new algorithm.

## 3. New exact adversarial UNSAT tests SCL30 and SCL45

Take these original symplectic cyclic covers and perform deterministic random original Tanner 2-switches, accepting ONLY complete `validate_sparse` checks of original 3-regularity, all source row/column degrees, C4-free linearity and connectedness. Frozen seeds and trial procedure are in executable code.

At each trial an independent exponentially bounded ORIGINAL exact-cover DFS either returns a directly verified SAT witness or a complete original-source UNSAT DAG with every possible branch traced to a previously proven failed subset. UNKNOWN_RESOURCE_LIMIT never counts as UNSAT.

For the first UNSAT switch candidate in each tested case, a SEPARATE GF3 degree3 Gaussian DAG reconstructs an explicit sparse linear combination of ORIGINAL source row generators E_i*x_M, |M|≤2, equal to the constant polynomial1 in the Boolean quotient. An INDEPENDENT checker reconstructs the entire source identity; this is not just a Gaussian rank or an untrusted search result.

[#38329965724 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38329965724) on commit `4ef85322044e29989b7e5c7c8a4ddb80acf611f7`:

| Original legal input | Original truth | Independent exact check | Degree3 GF3 source certificate |
|---|---|---|---|
| symplectic SCL15 | SAT | exactly 6 source assignments | N/A |
| s=2 cyclic covered SCL30 | SAT | witness lifted and rechecked | N/A |
| s=3 cyclic covered SCL45 | SAT | witness lifted and rechecked | N/A |
| adversarial SCL30, trial3 | UNSAT | independently replayed original exact-cover DAG, 16 dead states | 201 nonzero original E_i*x_M terms, pivot rank4525 |
| adversarial SCL45, trial3 | UNSAT | independently replayed original exact-cover DAG, 39 dead states | 994 nonzero original E_i*x_M terms, pivot rank15226 |

Earlier independent source controls include Petersen SCL45: degree2 impossible (source-dual pseudomoment support454) and degree3 sufficient (explicit 1337-term source identity). Fano7, high-girth triple-Fano and E61 UNSAT12 admit degree2 source refutations. Sixteen source-certified SCL27 random UNSAT cases have V3 refutation CANDIDATES (not all separately source-unwound).

Additional exploratory local search, explicitly NOT GitHub-certified:
- hundreds of legal SCL15 adversarial 2-switch UNSAT inputs each had degree3 constant in the checked span;
- 100 legal SCL30 2-switch trials against a random cyclic 2-lift (88 UNSAT, 12 SAT) yielded no source with missing degree3 constant;
- 35 legal SCL45 2-switch trials (24 UNSAT, 11 SAT) yielded no source with missing degree3 constant;
- one source-checked 60-variable cyclic cover 2-switch UNSAT case also yielded degree3 constant in the exact rank test, but this individual exploratory case is NOT an independently source-unwound proof certificate.
All are finite observation only. Do NOT extrapolate to a universal V3 theorem, worst-case algebra runtime, or a uniform constant d.

Executable: `experiments/r5_universal_gf3_geometric_cover_degree3_stress.py`; workflow `.github/workflows/r5-gf3-geometric-cover-degree3-gate.yml`.

## 4. Strong proof-complexity literature and exact transfer barrier

- **Lauria–Nordström (CCC 2017),** *Graph Colouring is Hard for Algorithms Based on Hilbert's Nullstellensatz and Gröbner Bases*, DOI https://doi.org/10.4230/LIPIcs.CCC.2017.2, proves bounded-degree GRAPH VERTEX k-colouring sources requiring linear PC degree, based on degree-preserving reductions from functional pigeonhole principle.
- **Atserias–Ochremiak (2018)**, *Proof Complexity Meets Algebra*, https://arxiv.org/abs/1711.07320, proves standard CSP reductions preserve proof complexity for PC over ANY FIELD, among other systems. Their particularly strong bounded-width ↔ sublinear-degree GAP THEOREM is specifically stated for **PC over the REAL FIELD**, SOS and other systems; IT DOES NOT AUTOMATICALLY IMPLY the same gap over our characteristic-three F3 system.
- **Conneryd et al (FOCS 2023 / ECCC TR25-032),** *Graph Colouring Is Hard on Average for Polynomial Calculus and Nullstellensatz*, establishes linear proof degree for sparse random graph vertex 3-colouring over any field, https://eccc.weizmann.ac.il/report/2025/032/.

**Critical unproven transfer required to get a native SCL unbounded-degree theorem:** construct an EXPLICIT bounded-degree original-source-to-source translation of the hard vertex-colouring / FPHP / Tseitin polynomial system into square, 3-regular, C4-free, positive Exact-One SCL of size polynomial in original input, with a PC LOW-DEGREE BACK-SIMULATION theorem over the SAME F3 encoding:
If the reduced SCL has a degree-d source refutation, then the hard original system has an original-source refutation in degree O(d) (or O(d)+O(1)). This cannot be assumed from ordinary decision NP-completeness or the existence of a parsimonious reduction. The previous native Holyer cubic-edge-colouring bridge is SAT-semantic; no theorem yet verifies this STRONG GF3 degree-transfer property.

Without this source-legal degree-preserving transfer, the literature cannot be used to claim unbounded V_d degree for our special SCL promise, and no failure of degree3 has yet been certified.

Also, even if such a lower bound is established, it ONLY refutes fixed-degree polynomial calculus: it does not refute arbitrary polynomial solvers or prove P!=NP.

## 5. Honest proof frontier

There are now TWO rival possible routes:
(A) POSITIVE: prove a fixed d (e.g. 3) works on EVERY legal original SCL with a general theorem, not finite experiments; then original source-degree linear algebra plus authenticated native pin compiler yields a true uniform polynomial solver, implying P=NP.
(B) NEGATIVE to this PARTICULAR METHOD: build a source-certified UNSAT SCL plus a dual source-moment y annihilating all degree3 generators. Better: source-legal, degree-preserving transfer of existing unconditional PC lower-bound families into SCL gives unbounded-degree obstructions.

Current data does not establish A or B. Next effort should focus on the exact transfer lemma / dual-construction; spending more CI on routine easy UNSAT random sources should not be reported as universal progress.

GATES:
```
GQ_W32_ORIGINAL_SCL15_LEGAL = PROVED
GQ_W32_SCL15_EXACT_SAT_COUNT6 = FINITE_SOURCE_VERIFIED
CYCLIC_SCL30_SCL45_COVER_SAT_WITNESS_LIFT = PROVED_AND_CI
GQ_SCL30_SWITCH_UNSAT_GF3_DEGREE3_SOURCE_CERT = CI_SUCCESS_201_TERMS
GQ_SCL45_SWITCH_UNSAT_GF3_DEGREE3_SOURCE_CERT = CI_SUCCESS_994_TERMS
ALL_SCL_V3_REFUTATION_COMPLETENESS = NOT_PROVED
SCL_PRESERVING_PC_DEGREE_LOWER_BOUND_REDUCTION = NOT_CONSTRUCTED
GENERAL_UNIFORM_POLY_LOOP_ZERO_TEST = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
