# Source Audit — Affine-Coset / Kernel / Signed-Trade Stack Governance Reconciliation

Date: 2026-09-27

Decision: `PASS_RETROSPECTIVE_SCOPED_RECONCILIATION`

Status:
`GOVERNANCE_RECONCILIATION_ONLY__NO_NEW_SCIENTIFIC_CLAIM__NO_NOVELTY_CLAIM`

## 1. Purpose

The pre-math validator identified a contiguous 2026-09-27 scientific stack that
was already committed to the active PR branch but was not covered by an
append-only pre-math supplement.  This audit reconciles that governance debt.
It does not alter, strengthen, promote, or re-label any theorem in the covered
files.

The covered stack consists of:

- the exact cubic Exact-One affine-coset/minimum-weight representation;
- local odd-parity LP blindness and circuit-augmentation controls;
- bounded-support affine-kernel descent barriers;
- R1/R5 semantic-oracle hardness controls;
- rational-kernel and rational-row-basis FPT routers;
- binary-kernel circuit contraction and local-swap classification;
- binary-kernel bipartite signed-trade lifting;
- polynomial-size boundary projection for an explicitly supplied connected
  signed trade.

Global scientific boundary remains:

```text
E8_D1 = EMPTY
P_VS_NP = OPEN
P_EQ_NP = NOT_PROVED
```

## 2. Internal anti-loop result

The current branch was searched before this reconciliation for the relevant
representations and donor languages.  The stack is not treated as a new route:
it is a continuation of the existing strict-equisatisfiable contraction route
and of the earlier cubic-kernel / coding-theory / WDR material.

In particular, the branch already knew before 2026-09-27 that the square cubic
Exact-One carrier can be expressed in all-ones-syndrome / coset-leader /
shortest-distinguished-circuit language.  The 2026-09-27 affine-coset files are
therefore authorized only as exact specializations, controls and routers, not as
novel coding-theory reductions.

## 3. External anti-loop: coding-theory layer

The following classical collision is binding.

Berlekamp, McEliece and van Tilborg, *On the Inherent Intractability of Certain
Coding Problems*, IEEE Transactions on Information Theory 24 (1978), 384-386,
DOI `10.1109/TIT.1978.1055873`, establishes NP-completeness of the classical
syndrome-decoding decision problem.  Standard coding references identify a
syndrome fibre with a coset of the code and minimum-syndrome decoding with a
nearest-codeword/coset-leader problem.

A contemporary source on regular syndrome decoding also records an NP-complete
regular-weight syndrome-decoding variant.  Therefore none of the following are
JANUS novelty claims:

```text
SYNDROME_DECODING
COSET_LEADER_SEARCH
LOW_WEIGHT_CODEWORD_SEARCH
EXACT_WEIGHT_IN_AFFINE_COSET
```

The JANUS files are restricted to the explicitly proved cubic-incidence
identities, parameterized routers, and structural donors they state.

## 4. External anti-loop: SAT semantic-equivalence layer

Full semantic literal equivalence is not a free preprocessing primitive.
Existing SAT literature distinguishes polynomial syntactic sufficient rules,
such as SCC-based equivalent-literal substitution in the binary implication
graph, from complete semantic equivalence.  The latter contains a coNP-hard
query; this agrees with the branch's explicit disjoint-union reduction in
`R5_E9_R1_R5_SEMANTIC_ORACLE_HARDNESS_BARRIER_2026-09-27_v1.0.md`.

Representative source binding:

- A. Biere, M. Järvisalo, B. Kiesl, *Preprocessing in SAT Solving*, Handbook of
  Satisfiability manuscript, 2021, for BIG/SCC equivalent-literal
  substitution;
- standard configuration/SAT complexity literature recording semantic literal
  equivalence as coNP-hard.

Thus the R1/R5 barrier is authorized only as a source-bound complexity firewall
and JANUS specialization, not as a new complexity-class result.

## 5. External anti-loop: cubic monotone Exact-One source class

Cubic Monotone 1-in-3 SAT is a known NP-complete source problem; the literature
states it as monotone 1-in-3 SAT with every variable occurring exactly three
times.  This source-class hardness is prior art and is not claimed by JANUS.

The 2026-09-27 files may use that source class only with their declared extra
promises and must not infer hardness for a narrower promise (for example
linearity, prescribed girth, a particular kernel dimension, or a particular
trade structure) unless separately proved.

## 6. External anti-loop: trades / bitrades

Combinatorial trades and bitrades, including Steiner trades, are established
objects.  Representative bindings already cited by the signed-trade files
include:

- N. J. Cavenagh, T. S. Griggs, *Subcubic trades in Steiner triple systems*,
  Discrete Mathematics 340(6), 2017, DOI `10.1016/j.disc.2016.10.021`;
- D. S. Krotov, I. Y. Mogilnykh, V. N. Potapov, *To the theory of q-ary
  Steiner and other-type trades*, Discrete Mathematics 339(3), 2016, DOI
  `10.1016/j.disc.2015.11.002`;
- J.-C. Picard, *Maximal Closure of a Graph and Applications to Combinatorial
  Problems*, Management Science 22(11), 1976, DOI `10.1287/mnsc.22.11.1268`.

Accordingly, `signed trade`, `bitrade`, `bipartite support`, and graph-closure
language are source-bound.  The authorized JANUS content is only the exact
incidence specialization proved in the covered theorem files, including the
explicit-support bipartite lifting criterion and the spanning-tree boundary
projection theorem.

## 7. Collision classification

```text
SYNDROME_DECODING / COSET_LEADER
= SOURCE_BOUND_PRIOR_ART

EXACT_WEIGHT / LOW_WEIGHT AFFINE-CODE SEARCH
= SOURCE_BOUND_PRIOR_ART LANGUAGE

CUBIC_MONOTONE_1_IN_3_NP_COMPLETENESS
= SOURCE_BOUND_PRIOR_ART

BIG_SCC_EQUIVALENT_LITERAL_SUBSTITUTION
= SOURCE_BOUND_PRIOR_ART

COMPLETE_SEMANTIC_LITERAL_EQUIVALENCE_HARDNESS
= SOURCE_BOUND_COMPLEXITY PHENOMENON + JANUS SPECIALIZATION

COMBINATORIAL_TRADES / BITRADES
= SOURCE_BOUND_PRIOR_ART

CUBIC_EXACT_ONE_DEFECT_IDENTITY
= JANUS_DERIVED_SPECIALIZATION__NO_NOVELTY_CLAIM

RATIONAL_KERNEL_INFORMATION_COORDINATE_ROUTER
= JANUS_DERIVED_PARAMETERIZED_ROUTER__NO_NOVELTY_CLAIM

ROW_BASIS_OVERLAP_EXCESS_ROUTER
= JANUS_DERIVED_PARAMETERIZED_ROUTER__NO_NOVELTY_CLAIM

BINARY_KERNEL_SUPPORT_BIPARTITE_IFF_UNIT_SIGNED_LIFT
= JANUS_DERIVED_SPECIALIZATION__NO_PRIORITY_CLAIM

EXPLICIT_CONNECTED_TRADE_SPANNING_TREE_BOUNDARY_PROJECTION
= JANUS_DERIVED_SPECIALIZATION__EXACT_FORMULATION_NOT_LOCATED_IN_CHECKED_SOURCES__NO_PRIORITY_CLAIM
```

## 8. Reconciled scientific artifacts

This audit authorizes pre-math coverage, without promotion, for exactly the
following already-existing scientific artifacts:

```text
experiments/r5_e9_affine_coset_circuit_augmentation.py
experiments/r5_e9_affine_coset_local_parity_lp_blindness.py
experiments/r5_e9_binary_kernel_bipartite_trade_donor.py
experiments/r5_e9_cubic_exact_one_affine_coset_minweight.py
experiments/r5_e9_cubic_kernel_circuit_contraction.py
experiments/r5_e9_local_swap_binary_coset_exactone_classification.py
experiments/r5_e9_r1_r5_semantic_oracle_hardness_controls.py
experiments/r5_e9_rational_kernel_nullity_fpt_router.py
experiments/r5_e9_rational_row_basis_overlap_excess_fpt_router.py
experiments/r5_e9_signed_trade_polysize_boundary_projection.py
research/R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md
research/R5_E9_AFFINE_COSET_LOCAL_ODD_PARITY_LP_BLINDNESS_2026-09-27_v1.0.md
research/R5_E9_BINARY_KERNEL_BIPARTITE_TRADE_DONOR_2026-09-27_v1.0.md
research/R5_E9_BOUNDED_SUPPORT_AFFINE_KERNEL_DESCENT_BARRIER_2026-09-27_v1.0.md
research/R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md
research/R5_E9_CUBIC_KERNEL_CIRCUIT_CONNECTED_CONTRACTION_2026-09-27_v1.0.md
research/R5_E9_LOCAL_SWAP_BINARY_COSET_EXACTONE_CLASSIFICATION_2026-09-27_v1.0.md
research/R5_E9_R1_R5_SEMANTIC_ORACLE_HARDNESS_BARRIER_2026-09-27_v1.0.md
research/R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md
research/R5_E9_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_2026-09-27_v1.0.md
research/R5_E9_SIGNED_TRADE_POLYSIZE_BOUNDARY_PROJECTION_THEOREM_2026-09-27_v1.0.md
```

No covered file is promoted from candidate/donor/barrier status by this audit.

## 9. Live frontier after reconciliation

The stack leaves the central algorithmic obligations open:

```text
POLYNOMIAL_SIGNED_TRADE_DISCOVERY
OR
POLYNOMIAL_MOVE_ON_TRADE_FREE_RESIDUE

+ MIXED_LINEAR/PB_CARRIER_GLOBAL_CLOSURE
+ ARBITRARY_INPUT_COVERAGE
+ POLYNOMIAL_TOTAL_CONSTRUCTION / RECONSTRUCTION
```

These are precisely the obligations that could carry genuine universal
P-vs-NP content.  They are not assumed by this governance repair.
