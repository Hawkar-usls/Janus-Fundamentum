# R5 — ExactSupport E129 Cover Tower: Real Memo-State Stress and an O(N)-Verifiable Arithmetic UNSAT Certificate

Date: 2026-10-11.
Repo: Hawkar-usls/Janus-Fundamentum; branch research/parity-isolation-trade-checkpoint-20261009; PR #515.
Baseline: `E129` rational-invertible q12 base, `ExactSupportResidualDAG` canonical labelled memo solver.

**Status**
- All-source E129 r-sheet-cover UNSAT theorem: existing, REUSED.
- NEW: explicitly constructed 12-integer linear combination certificate; it refutes EVERY r=2^k cover with a verifier running in O(N) integer operations WHEN an explicit correct 12-fibre map is provided. This is sound and proved independently of the search.
- NEW: three deterministic 2-lift towers, with exact measured ACTUALLY visited memo states and bounded UNKNOWN.
- Global polynomial ExactSupport: NOT CONSTRUCTED.
- Exponential actual AND/OR proof-size lower bound: NOT PROVED.
- P vs NP: OPEN.

## A. Short integer refutation of the entire E129 cover family

Let B be E129's explicit 12x12 binary square/cubic/linear incidence matrix,
with rows (i,P[i],Q[i]) and exact determinant det(B)=36. Every row has
three ones, so B*1=3*1.

Fix base variable j=0. Set

    u^T := 36*e_0^T*B^(-1).

The adjugate identity guarantees u is an INTEGER 12-vector. It satisfies

    u^T B = (36,0,...,0)
    sum_{i=0}^{11} u_i = 12,

where the latter follows by multiplying by 1 and using B*1=3*1.

Let A be ANY degree-r Levi incidence COVER of B. For each lifted check
copy (i,t), assign linear-combination coefficient u_i. Sum its exact
one right-hand side and coefficients across all 12r lifted check rows.
Because the covering map projects the r incidences for each original
base edge as a perfect matching, the linear combination is EXACTLY

    36 * y_0 = 12*r,

where y_0 counts how many of the r lifted copies of the base variable
0 are selected by an integer (a fortiori Boolean) solution.
This would imply 3*y_0=r, an impossibility if r is not divisible by 3.

The proof has an O(12)-word constant seed u, the r-cover map, and
the source 12x12 matrix. Given an explicit map with N=12r lifted
checks and N lifted variables, its verification scans each nonzero
incidence a constant number of times and checks

    lambda^T A = 36 * 1_{variable fibre 0},
    lambda^T 1 = 12r,
    3 does not divide r.

This takes O(N) integer operations of O(log r+constant) bits.
The Python checker derives u using exact Fraction elimination and then
performs the actual certificate validation using ONLY integers on
EVERY lifted source. It also independently audits the full fibre
cover map, not simply the numerical dimensions.

IMPORTANT: this **does not** constitute a short AND/OR residual-DAG
certificate under the frozen inference rules. It is a different,
strictly stronger arithmetic proof mechanism. Its existence
shows why using this particular tower to argue that ALL
algorithms must take exponential time would be wrong.
It does not prove universal polynomial recognition of arbitrary
SCL instances, nor polynomial discovery of an unknown fibre map.

## B. Finite ACTUAL visited DAG search on 2-lift towers

Run:
    python experiments/r5_universal_exact_support_e129_cover_tower_visited_attack.py

Seeds 129,132,9421, repeated 2-lift (n=12,24,48,96,192,384).
All instances are legal square/cubic/linear because a 2-lift
preserves the SCL incidence promise. They are all UNSAT by
the independent integer obstruction above. They may nevertheless
take many visited memo states if the solver does NOT use arithmetic
projection certificates.

Exact reproducible GitHub focused CI run #38142784983: SUCCESS.

       n        seed129   seed132   seed9421
      12            4         4          4
      24            8         5          8
      48           18         9         19
      96           69        22         39
     192          248       155        127
     384      UNKNOWN   UNKNOWN    UNKNOWN
              (1000)     (1000)     (1000)

The q384 counts are capped, not exact completed UNSAT proof sizes.
No polynomial or exponential asymptotic bound is inferred from the
table. The experiment has complete exact SAT/UNSAT/UNKNOWN semantics.

## C. Scientifically useful separation and next test

The family demonstrates a methodological separation:
- global rational/integer fibre invariants can prove UNSAT with
  small exact certificates, even for large coverings;
- the present purely combinatorial residual-DAG proof generator
  does not incorporate that arithmetic inference and can explore
  many more states before identifying UNSAT.

This is NOT evidence that the class is algorithmically hard for
all conceivable solvers. It strengthens the rationale for seeking
universal polynomially COMPUTABLE invariants, while forbidding
claims that a hard DAG instance alone disproves P=NP.

For a genuine exponential *frozen DAG* lower bound, one still
needs an infinite verified legal UNSAT family plus a proof of
superpolynomial minimum size in the **exact** AND/OR inference system
of `R5_UNIVERSAL_EXACT_SUPPORT_ANDOR_UNSAT_PROOF_SYSTEM_2026-10-11.md`.

For a genuine universal P=NP algorithm, one must instead show that
for ALL legal SCL matrices and pinned assignments, an exact
support/witness mechanism evaluates with n^C BIT complexity.

In particular, detecting an arbitrary projected INTEGER solution
obstruction by Smith/Hermite normal form is polynomial but only a
necessary test for Boolean exact-one; E123's semigroup-saturation
hole controls already prove integrality/relaxation constraints are
not equivalent to Boolean exact-one feasibility.

## Gate ledger

E129_INVERTIBLE_BASE_UNSAT_COVER_THEOREM = PREDECESSOR_PROVED.
E129_EXPLICIT_INTEGER_U_FIBRE_LINEAR_CERTIFICATE = PROVED.
E129_COVER_CERTIFICATE_CHECK_BIT_TIME_POLYNOMIAL = PROVED_WITH_GIVEN_MAP.
E129_R2K_3_SEEDS_18_FROZEN_FIXTURES = VERIFIED.
E129_N384 = UNKNOWN_SEARCH_RESOURCE_GUARD (MATHEMATICALLY UNSAT).
GENERAL_SCL_INTEGER_OBSTRUCTION_IMPLIES_BOOLEAN_UNSAT = SOUND_ONLY.
ALL_INPUT_UNSAT_ANDOR_PROOF_SIZE_POLY = OPEN.
ALL_INPUT_UNSAT_ANDOR_PROOF_SIZE_SUPERPOLY_LOWER_BOUND = OPEN.
UNIVERSAL_POLYNOMIAL_ExactSupport = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
