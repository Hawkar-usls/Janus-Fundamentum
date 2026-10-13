# R5 — Joint Expert Global Coverage Strike After Complete Repository Audit

Date: 2026-10-12 (Europe/Kyiv). Research branch:
`research/r5-cubic-flow-smith-pair-20261011`, stacked DRAFT PR #516.
Main was not changed.

## I. Single scientific goal

Construct `SolveLinearCubicXSAT(A)`, a deterministic TOTAL
all-input algorithm for every legal square+cubic+linear positive
Exact-One SAT input, returning SAT+witness or UNSAT, both correct,
with a proved uniform n^O(1) worst-case BIT time including
all transforms, discovery, certificate production and verification.

**UNIVERSAL_POLY_SOLVER = NOT_CONSTRUCTED; P_VS_NP = OPEN.**

This checkpoint does NOT count finite coverage, an FPT terminal,
a bounded polynomial budget, or a local proof-state descent
as a P=NP algorithm.

## II. Source complete audit authority

The entire source-tracked repository was scanned (not a selective
tree search). Frozen 2026-10-12 CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189351705
SUCCESS. 1547 tracked source files, 126 folders, 427 Python
AST modules, 350 static imports, 97 workflows. The scan
produces `audits/r5_repository_inventory/source_manifest.json`
and `review_queue.tsv`. This is file-path and AST coverage,
not full independent mathematical review of every algorithm.
Review preconditions before raising source authority.
Method-by-method dispositions are in
`research/R5_UNIVERSAL_FULL_REPO_METHOD_AUDIT_AND_COVERAGE_ATTACK_2026-10-12.md`.

The main portfolio has sound all-source root checks, already
transitively connected independent MOD9/GAUSS, exact bounded
residual DAG, exact PC3 UNSAT checks for small n, checked
optional odd-order automorphism PC3 compression, checked
original-witness SAT and independently replayed exhaustive
UNSAT fallback. The exhaustive fallback is NOT polynomially bounded.

## III. Three attack routes on mathematical coverage

### 1. Budget ladder on eleven independent-source SCL controls

Experiment:
`experiments/r5_universal_certified_portfolio_poly_budget_ladder.py`.
CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189743948
**SUCCESS**, all original SAT/UNSAT truths cross-checked.

Bounded profile:
`pc3_max_n=48`, no supplied symmetry; `bounded_states=0,n,n²`.

| Source | Truth | 0 | n | n² |
| --- | --- | --- | --- | --- |
| E61 SAT12 | SAT | UNKNOWN | SAT | SAT |
| E61 UNSAT12 | UNSAT | UNSAT | UNSAT | UNSAT |
| E129 MOD9 UNSAT12 | UNSAT | UNSAT | UNSAT | UNSAT |
| K3,3 graph SCL27 | SAT | UNKNOWN | SAT | SAT |
| Petersen SCL45 | UNSAT | UNSAT | UNSAT | UNSAT |
| Prism5 SCL45 | SAT | UNKNOWN | SAT | SAT |
| Isaacs flower J5 SCL90 | UNSAT | UNKNOWN | UNKNOWN | UNSAT |
| E118 UNSAT90 | UNSAT | UNKNOWN | UNSAT | UNSAT |
| E118 SAT90 | SAT | UNKNOWN | SAT | SAT |
| Tutte12 E123 UNSAT63 | UNSAT | UNSAT | UNSAT | UNSAT |
| Fano SCL7 | UNSAT | UNSAT | UNSAT | UNSAT |

At `bounded_states=n²` all ELEVEN control inputs are
decided with original-source SAT witnesses or existing
sound negative gates. This is **FINITE EVIDENCE**, NOT the
universal polynomial-time theorem. The bound controls
expanded residual states; verifying worst-case bit time
also requires accounting per-state representation size.

The original `bounded_states=0` profile had six UNKNOWNs;
the stronger n² cap resolves them, without any mathematically
unproved promotion.

### 2. Strongest possible width-2 semantic closure cannot
generate SAT certificates from unit propagation alone

Experiment:
`experiments/r5_universal_semantic_width2_fixpoint_barrier.py`.
CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189776489
**SUCCESS**.

Construct the HOLYER direct SCL system of 3-edge coloring of
K3,3, a connected fully legal square+cubic+linear SCL n=27.
Independent enumeration of ALL 3^9 colored assignments
reveals exactly 12 valid edge colorings and thus 12 source
Boolean witnesses by the exact direct bijection.

Each of the 27 Boolean variables x_(edge,color) takes BOTH
values across these 12 witnesses: the automorphism relabeling
three colors maps any edge's distinguished color to another.
Hence no ORIGINAL SCL variable is forced.

Enumerate all 2n+4*C(n,2) unary/binary assignments and
classify against the COMPLETE model set. There are precisely
**81 semantically valid binary nogoods, zero unary nogoods**.
Unit propagation on Exact-One clauses plus even the complete
semantic list of all 81 forbidden pairs, from no pins, is
at a fixed point with zero fixed variables. It therefore
does not emit a witness, although 12 exist.

This proves a precise LIMITATION OF THE LOCAL KNOWLEDGE
CLOSURE + UNIT PROPAGATION ARCHITECTURE, not a SAT/UNSAT
lower bound for unrestricted experts. It excludes the
invalid inference

    strict O(n²) knowledge potential descent
       => eventually a SAT model/UNSAT proof.

A real additional global witness constructor or refuter
covering every remaining fixed point is necessary.

### 3. Actual growing hard-source stress after root algebra

A. Proven conflicting two-pin toroidal triangular SCL,
L=9,12,15, dimensions 81,144,225. The predecessor Fourier
theorem proves there are exactly three phase assignments,
and the frozen two pins choose different phases:
`UNSAT` on every checked input. Unlike the earlier pure
residual-DAG run, the current composite portfolio's
`HYBRID_ROOT` proves UNSAT before branching in all
six comparisons under n and bounded n² limits.
Experiment: `r5_universal_global_coverage_pinned_torus_poly_attack.py`.
CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189862821
SUCCESS.

B. Infinite known UNSAT Isaacs flower snark family J_k.
Actual complete root/residual states for k=5,7,9,11
under `n²` cap (without supplying symmetry annotation):

| k | SCL n=18k | n-state guard | n² guard | actual visited S |
| ---: | ---: | --- | --- | ---: |
| 5 | 90 | UNKNOWN | UNSAT | 286 |
| 7 | 126 | UNKNOWN | UNSAT | 574 |
| 9 | 162 | UNKNOWN | UNSAT | 862 |
| 11 | 198 | UNKNOWN | UNSAT | 1150 |

These four counts obey EXACTLY the **observed** affine law
`S(k)=144k-434=8n-434`. Do NOT turn this four-point
pattern into a theorem without symbolic inductive proof
of canonical residual transition and memoization behavior
for all odd k. This family has constant-width cyclic
structure and provides no general input-size bound.

CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38189943841
SUCCESS, four independent runner jobs.

C. Six genuinely legal random 2-lifts of source
Petersen SCL45 and Tutte/E123 SCL63,
each with deterministic seeds 9421, 11223, 334455.
Original parent UNSAT does not automatically license
calling a 2-cover UNSAT; the test asserts ONLY
sound target output and independent source legality.
Every lift returned real UNSAT with an n² guard.

Petersen 2-lifts n90: visited S = 87, 121, 94.
Tutte 2-lifts n126: visited S = 174, 214, 188.

A finite portfolio returning UNKNOWN would already be
a sound test of NON-coverage by that particular profile,
even without a ground-truth answer, but none of these
six produced UNKNOWN under n².

CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38190056218
SUCCESS in all six independent runner jobs.

## IV. Targeted contemporary literature check

- Jonas Conneryd, Susanna F. de Rezende, Jakob Nordström,
  Shuo Pang, Kilian Risse,
  *Graph Colouring Is Hard on Average for Polynomial Calculus
  and Nullstellensatz*, ECCC TR25-032 (2025);
  https://eccc.weizmann.ac.il/report/2025/032/
  Proves linear PC degree for 3-VERTEX-coloring of
  sparse random regular graphs over any field.
- Buss, Grigoriev, Impagliazzo, Pitassi, JCSS 62 (2001),
  DOI:10.1006/jcss.2000.1726: modular-PC proof degree
  lower bounds with characteristic-sensitive caveats.

These theorems are warning signals against asserting
fixed-degree proof-completeness, NOT automatically
applicable to JANUS's specific positive Exact-One
square+cubic+linear hypergraph encoding or Holyer
3-EDGE-coloring system. A sound reduction with precise
PC DEGREE overhead must be proved first.
In characteristic 2 the conventional XOR/Tseitin
contradiction itself may be easy; no direct fallacious
transfer is licensed.

## V. The actual missing universal theorem

Let `D_i(n)` denote the inputs decided correctly by
certified polynomial expert E_i within explicit total
polynomial bit budget b_i(n). To call
`SolveLinearCubicXSAT` CONSTRUCTED, prove:

  for EVERY n, EVERY legal SCL F on n variables,
     F belongs to UNION_i D_i(n)

and guarantee deterministic n^C total work summed over
expert discovery, preconditions, transforms,
certificate construction/size, reconstruction and
verification, with a single C independent of n.

This has NOT been proven. Neither a finite linear
visited-state pattern on Isaacs, complete knowledge
saturation, a broad repo inventory, nor 11/11 success
at n² establishes asymptotic universal coverage.

High-value next proof attack:
- Create an actual *source-aligned*, efficiently testable
  invariant of globally hard residual cores not reducible
  to bounded width/rank/symmetry.
- Find a legal infinite family on which proof-state
  closure and each fixed-degree polynomial expert have
  independently certified NON-refutation, or prove that
  a polynomial witness selector always exists.
- For possible PC-degree lower bounds, rigorously verify
  a degree-preserving source reduction (from known PC-hard
  vertex-coloring formulas into THIS SCL representation),
  distinguishing decision hardness from specific proof
  system hardness.
- Never claim UNKNOWN implies UNSAT.

## Checkpoint ledger

FULL_REPO_AUDIT = COMPLETE_STATIC_TREE / PARTIAL_SEMANTICS.
PROVENANCE_AWARE_PORTFOLIO = IMPLEMENTED.
BUDGET_11_CONTROLS_ALL_FINITE_DECIDED_AT_N2 = OBSERVED_CI.
EXACT_81_PAIR_K33_WIDTH2_FIXPOINT_BARRIER = PROVED_FINITE.
TORUS_L9_L12_L15_ROOT_UNSAT = VERIFIED_CI.
FLOWER_J5_J7_J9_J11_N2_UNSAT = VERIFIED_FINITE.
FLOWER_LINEAR_VISITED_COUNT_FORMULA = OBSERVED_4_POINTS_ONLY.
2LIFT_PETERSEN_TUTTE_SIX_N2_COMPLETIONS = VERIFIED_FINITE.
GLOBAL_POLY_EXPERT_COVERAGE = OPEN.
GLOBAL_POLY_WITNESS_CONSTRUCTION = OPEN.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
