# JANUS R5 — complete tree inventory and provisional solver-method routing

> Fully enumerated git-tracked source tree. Path/AST-level complete;
> mathematical semantic verification limited to explicitly reviewed entrypoints.
> Code is NOT assumed unused merely because it has no static importer.

Frozen source commit: `76184e5fd993479097b1c1ff877217c072ae118b`.
Tracked files scanned: **1547**.
Tracked folders represented: **126**.
Bytes scanned: **12213327**.
Python modules parsed: **427**.
Python parse errors: **0**.
Static local import edges: **350**.
Workflows: **97**.

## Every top-level subtree

| Subtree | Tracked files | Role |
|---|---:|---|
| `.github` | 100 | CI_GOVERNANCE |
| `.janus` | 4 | AGENT_POLICY |
| `CONTRIBUTING.md` | 1 | source/root metadata |
| `JANUS_AGENT_BEACON.json` | 1 | source/root metadata |
| `LICENSE` | 1 | source/root metadata |
| `README.md` | 1 | source/root metadata |
| `START_HERE_TRUMP_CONTEXT.md` | 1 | source/root metadata |
| `archive` | 1 | ARCHIVED_CONTROLS |
| `docs` | 92 | PUBLIC_SCIENTIFIC_DOCUMENTATION |
| `experiment_manifest.json` | 1 | source/root metadata |
| `experiments` | 393 | RUNNABLE_EXPERIMENTS_AND_FIXTURES |
| `proof_attempts` | 43 | LEGACY_PROOF_ATTEMPTS |
| `proposals` | 10 | PROPOSALS_UNADMITTED |
| `registry` | 224 | FROZEN_PROVENANCE_JSON |
| `research` | 653 | SCIENTIFIC_ARGUMENT_EVIDENCE |
| `reviews` | 2 | REVIEW_RECORDS |
| `tools` | 19 | GENERAL_TOOLING |

## Full role classification (discovery, NOT mathematical authority)

| Category | Files |
|---|---:|
| `ADAPTER_PRECONDITION` | 4 |
| `BENCHMARK_DATA` | 7 |
| `CI_WORKFLOW` | 100 |
| `CNF_FORMULA_CACHING_OR_PROOF_CONTROL` | 47 |
| `CODE_REVIEW_QUEUE` | 54 |
| `EVIDENCE_AUDIT` | 1 |
| `INTEGRATED` | 6 |
| `INTEGRATED_CONDITIONAL` | 1 |
| `INTEGRATED_TRANSITIVE` | 3 |
| `LEGACY_OR_HEURISTIC_CONTROL` | 19 |
| `NEGATIVE_CONTROL` | 4 |
| `OPTIONAL_SAT_SEARCH` | 2 |
| `OTHER_SOURCE` | 1 |
| `PROVENANCE_OR_DATA` | 664 |
| `R5_METHOD_REVIEW_QUEUE` | 159 |
| `REVIEW_CONDITIONAL` | 7 |
| `SCIENTIFIC_NOTE_OR_DOC` | 348 |
| `SEPARATE_APMA_TRACK_ADAPTER_NEEDED` | 103 |
| `TOOL_REVIEW_QUEUE` | 17 |

## High-value method audit (manually scoped first-pass)

| Method file | Proposed integration role | Current claim ceiling |
|---|---|---|
| `experiments/direct/janus_tear_policy0a_fc_proof_system.py` | REVIEW_CONDITIONAL | CNF_OTHER_INPUT — FC residual judgements, requires verified SCL/CNF adapter |
| `experiments/r5_e108_normal_span_quotient_solver.py` | REVIEW_CONDITIONAL | FPT_BY_RANK — 2^rank quotient; not all-input poly |
| `experiments/r5_e109_normal_matroid_component_decomposition.py` | REVIEW_CONDITIONAL | FPT_BY_COMPONENT — sum 2^component rank; not universal |
| `experiments/r5_e119_perfect_conflict_graph_global_terminal.py` | REVIEW_CONDITIONAL | PERFECT_GRAPH_PRECONDITION — MIS terminal only on certified perfect graph |
| `experiments/r5_e78_linear_delta_equality_gluing_meta_solver.py` | REVIEW_CONDITIONAL | REPRESENTABILITY_PRECONDITION — delta gluing; need poly construction and exact boundary signatures |
| `experiments/r5_parity_fixed_m_hall_tight_dm_trade.py` | REVIEW_CONDITIONAL | FIXED_MATCHING_PRECONDITION — Hall/Dulmage Mendelsohn trade feature |
| `experiments/r5_parity_fixed_m_trade_span_normal_form.py` | REVIEW_CONDITIONAL | FIXED_MATCHING_PRECONDITION — trade circuit evidence; non-TU firewall |
| `experiments/r5_universal_boolean_pc_degree3_global_attack.py` | INTEGRATED | POLY_SOUND_UNSAT — degree3 GF2 PC refuter, not complete |
| `experiments/r5_universal_certified_expert_portfolio.py` | INTEGRATED | CERTIFIED — main cooperative router |
| `experiments/r5_universal_certified_odd_symmetry_adapter.py` | INTEGRATED_CONDITIONAL | CERTIFIED_ODD_AUTOMORPHISM — row permutation validated before exact odd-group PC3 |
| `experiments/r5_universal_certified_portfolio_coverage_matrix.py` | EVIDENCE_AUDIT | FINITE_COVERAGE_FALSIFIER — 11 independent SCL fixture truths versus bounded portfolio |
| `experiments/r5_universal_certified_shared_proof_state.py` | INTEGRATED | CERTIFIED — shared no-good+GF2+ANDOR provenance ledger |
| `experiments/r5_universal_cubic_edgecolor_direct_scl_bridge.py` | ADAPTER_PRECONDITION | GADGET_MAP — graph-SCL witness preserving map |
| `experiments/r5_universal_cubic_four_cut_21_state_interface.py` | ADAPTER_PRECONDITION | CUBIC_GRAPH_ONLY — four-edge cut signature 21 states |
| `experiments/r5_universal_cubic_nondegenerate_threecut_recognizer.py` | ADAPTER_PRECONDITION | CUBIC_GRAPH_ONLY — polynomial 3-cut finder |
| `experiments/r5_universal_cubic_three_edge_cut_factorization.py` | ADAPTER_PRECONDITION | CUBIC_GRAPH_ONLY — 3-edge cut factor + witness gluing |
| `experiments/r5_universal_exact_support_exponential_reachable_residual_firewall.py` | NEGATIVE_CONTROL | EXACT_SUPPORT_EXPONENTIAL_STATE_FAMILY — forbid claim state count always polynomial |
| `experiments/r5_universal_exact_support_hybrid_algebraic_dag.py` | INTEGRATED | EXACT_GUARDED — root algebra + exact bounded DAG |
| `experiments/r5_universal_exact_support_mod9_dual_certificate.py` | INTEGRATED_TRANSITIVE | POLY_SOUND_UNSAT — called by ExactSupportHybrid; its negative certificate now lifted to main router and replayed |
| `experiments/r5_universal_exact_support_pinned_oracle_attack.py` | INTEGRATED_TRANSITIVE | EXACT_EXPONENTIAL — ExactSupportHybrid root calls this old pinned solver; do not duplicate |
| `experiments/r5_universal_exact_support_residual_dag_attack.py` | INTEGRATED | EXACT_GUARDED — source validation, pins, residual DAG |
| `experiments/r5_universal_exact_support_unsat_andor_certificate.py` | INTEGRATED | EXACT_PROOF — complete fallback/independent replay |
| `experiments/r5_universal_kettani_2025_toroidal_treewidth_counterexample.py` | NEGATIVE_CONTROL | REFUTED_TW_SHORTCUT — unbounded treewidth blocks naive bounded-width generality |
| `experiments/r5_universal_modular_flow_count_all_q_no_go.py` | NEGATIVE_CONTROL | REFUTED_FIXED_MODULAR_NONZERO — SAT false zero mod arbitrary fixed q |
| `experiments/r5_universal_pfaffian_cube_k33_cancellation.py` | NEGATIVE_CONTROL | REFUTED_NAIVE_PFAFFIAN — SAT false zero due sign cancellation |
| `experiments/r5_universal_quadratic_gauss_mod4_attack.py` | INTEGRATED_TRANSITIVE | POLY_SOUND_UNSAT — ExactSupport root imports modular Gauss filter; independently check boundary |
| `experiments/v2.0-selective-distributed/src/solvers.py` | OPTIONAL_SAT_SEARCH | HEURISTIC_SAT_ONLY — WalkSAT/Junction hints never UNSAT proof |
| `tools/OdontoForge_PNP_EXP.py` | OPTIONAL_SAT_SEARCH | EXACT_CNF_EXTERNAL_ADAPTER — exact CNF branch search, guard UNKNOWN; no general poly |

## Review and integration rules

1. **Keep:** original source validators, exact support, proof replay, PC3, mod9, and their independently checked SAT/UNSAT gates. Do not duplicate calls already integrated transitively; surface their proof objects in the common router.
2. **Adapter required:** representation-specific 3/4-cut, rank-FPT, perfect graph, matroid/delta, and formula-cache methods, only after exact bidirectional semantics and input preconditions are proved.
3. **Shadow only:** heuristic search, learned routing, old benchmark witnesses. They can suggest or find SAT assignments, but cannot certify UNSAT from timeout or silence.
4. **Negative firewall:** preserve counterexamples to Pfaffian cancellation, fixed modulus, bounded width and exponential-state shortcuts; NEVER import as positive solver passes.
5. **Do not delete:** automatically unreferenced does NOT mean scientifically unused; archived experiments/registry proofs remain provenance.
6. **Global requirement:** show ALL legal SCL inputs receive certified SAT witness or UNSAT within ONE n^O(1) bit bound; finite method coverage, imports, successful CI and polynomial knowledge vocabulary do not prove this.

## Next source-aligned global coverage gate

`UNION_POLY_EXPERTS_COVERS_ALL_LEGAL_SCL` = **NOT PROVED**.
`COMPLETE_DAG_FALLBACK_STATES_POLY_BOUNDED_AFTER_SHARED_CLOSURE` = **NOT PROVED**.
`UNIVERSAL_POLY_SolveLinearCubicXSAT` = **NOT CONSTRUCTED**.
`P_VS_NP` = **OPEN**.

Machine-readable exhaustive file+folder map:
`audits/r5_repository_inventory/source_manifest.json`.
Tabular row-by-row review queue:
`audits/r5_repository_inventory/review_queue.tsv`.

Generated files are omitted from the self-referential enumeration by design;
the scanner scans every other git-tracked file at the frozen source commit.
