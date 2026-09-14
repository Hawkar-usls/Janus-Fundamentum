# Prereg v0.3 candidate — line-by-line audit

This is a semantic materialization of the HQ contract. The pinned original draft bytes were not recovered, so no byte-identical claim is made.

All machine checks below PASS: `draft_not_blind, frontier_locked, frozen_leaf_relation, frozen_transfer_join, gyo_structural_only, historical_fail_immutable, no_backtracking, no_oracle_labels, p_vs_np_open, pairwise_tree_not_required, pinned_bytes_not_falsely_claimed, preserve_all_relations, rho_lte_3, root_replay_required, running_intersection, second_person_only, tuple_cap_8`.

| Line | Status | Audit note | Exact text |
|---:|---|---|---|
| 1 | PASS | JSON envelope, draft status, second-person authority | `{` |
| 2 | PASS | JSON envelope, draft status, second-person authority | `  "artifact": "JANUS-TRUMP-APMA-ALPHA-ACYCLIC-SEMANTIC-JOIN-TREE-TRANSFER-FREEZE-PREP-v0.3",` |
| 3 | PASS | JSON envelope, draft status, second-person authority | `  "status": "DRAFT_UNSEALED__DO_NOT_RUN_BLIND",` |
| 4 | PASS | JSON envelope, draft status, second-person authority | `  "authority": "SECOND_PERSON_EXECUTION_WORKER__FREEZE_PREPARATION_ONLY",` |
| 5 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `  "source_lineage": {` |
| 6 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `    "repository": "Hawkar-usls/Janus-Fundamentum",` |
| 7 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `    "historical_v1_1_fail": "17284f07a4d826cb80ade2e93c495a0bfe2db176",` |
| 8 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `    "readonly_postmortem": "6ec0ee28456601e3ebc89a99206b18b5322de987",` |
| 9 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `    "scientific_verdict_immutable": "FAIL_NO_TRANSFER_RULE",` |
| 10 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `    "pinned_draft_sha256": "0b6159614b11228b62a195bae9388612e024295debf9b22b99f41b96a0af6429",` |
| 11 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `    "pinned_draft_bytes_recovered": false,` |
| 12 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `    "materialization_class": "SEMANTIC_MATERIALIZATION_FROM_HQ_CONTRACT__NOT_BYTE_IDENTICAL_CLAIM"` |
| 13 | PASS | Historical v1.1/postmortem binding and unrecovered pinned-draft provenance | `  },` |
| 14 | PASS | Frozen local/transfer semantics; stop-before-semantic-change rule | `  "frozen_semantics": {` |
| 15 | PASS | Frozen local/transfer semantics; stop-before-semantic-change rule | `    "transfer_core_checkout_sha256": "dba2dc94980081497f30870d962ffff3b536f6e8271176187b061b5fbe0e19dd",` |
| 16 | PASS | Frozen local/transfer semantics; stop-before-semantic-change rule | `    "leaf_relation": "UNCHANGED",` |
| 17 | PASS | Frozen local/transfer semantics; stop-before-semantic-change rule | `    "transfer_join": "UNCHANGED",` |
| 18 | PASS | Frozen local/transfer semantics; stop-before-semantic-change rule | `    "semantic_change_policy": "STOP_BEFORE_IMPLEMENTATION_IF_REQUIRED"` |
| 19 | PASS | Frozen local/transfer semantics; stop-before-semantic-change rule | `  },` |
| 20 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `  "structural_contract": {` |
| 21 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "rho_max": 3,` |
| 22 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "min_clause_group_guard": "REMOVED",` |
| 23 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "separator_order": "WIDTH_ASC_THEN_FROZEN_SCORE_THEN_LEXICOGRAPHIC",` |
| 24 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "posthoc_separator_backtracking": false,` |
| 25 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "split_requires_two_nonempty_proper_children": true,` |
| 26 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "oracle_component_labels": false,` |
| 27 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "private_island_partition_enumeration": false,` |
| 28 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `    "historical_blind_data_access": false` |
| 29 | PASS | rho<=3 deterministic decomposition contract; no backtracking/oracle/private partition/blind access | `  },` |
| 30 | PASS | Complete boundary hypergraph; distinct duplicate/subset relation identities; width<=3 | `  "boundary_hypergraph": {` |
| 31 | PASS | Complete boundary hypergraph; distinct duplicate/subset relation identities; width<=3 | `    "relation_identity": "ONE_DISTINCT_ID_PER_DISCOVERED_LEAF",` |
| 32 | PASS | Complete boundary hypergraph; distinct duplicate/subset relation identities; width<=3 | `    "hyperedge": "COMPLETE_SHARED_VARIABLE_BOUNDARY_SCOPE",` |
| 33 | PASS | Complete boundary hypergraph; distinct duplicate/subset relation identities; width<=3 | `    "duplicate_scopes": "PRESERVE_DISTINCT_RELATIONS",` |
| 34 | PASS | Complete boundary hypergraph; distinct duplicate/subset relation identities; width<=3 | `    "subset_scopes": "PRESERVE_DISTINCT_RELATIONS",` |
| 35 | PASS | Complete boundary hypergraph; distinct duplicate/subset relation identities; width<=3 | `    "boundary_width_limit": 3` |
| 36 | PASS | Complete boundary hypergraph; distinct duplicate/subset relation identities; width<=3 | `  },` |
| 37 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `  "gyo_contract": {` |
| 38 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `    "algorithm": "DETERMINISTIC_GYO_ALPHA_ACYCLICITY",` |
| 39 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `    "vertex_tie_break": "ASCENDING_VARIABLE_ID",` |
| 40 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `    "subset_edge_tie_break": "REDUCED_SCOPE_SIZE_SCOPE_RELATION_ID_PARENT_KEY_ASC",` |
| 41 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `    "edge_removal_semantics": "STRUCTURAL_ONLY",` |
| 42 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `    "semantic_relation_deletion": false,` |
| 43 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `    "every_original_relation_in_join_tree": true,` |
| 44 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `    "join_edge_separator": "EXACT_INTERSECTION_OF_ORIGINAL_BOUNDARY_SCOPES"` |
| 45 | PASS | Deterministic GYO; structural-only reductions; all relation identities preserved | `  },` |
| 46 | PASS | Running-intersection requirement and explicit non-requirements | `  "running_intersection": {` |
| 47 | PASS | Running-intersection requirement and explicit non-requirements | `    "required": true,` |
| 48 | PASS | Running-intersection requirement and explicit non-requirements | `    "per_shared_variable": "ALL_RELATION_NODES_CONTAINING_X_INDUCE_CONNECTED_SUBTREE",` |
| 49 | PASS | Running-intersection requirement and explicit non-requirements | `    "pairwise_overlap_graph_tree_required": false,` |
| 50 | PASS | Running-intersection requirement and explicit non-requirements | `    "raw_incidence_graph_tree_required": false` |
| 51 | PASS | Running-intersection requirement and explicit non-requirements | `  },` |
| 52 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `  "normalization_and_replay": {` |
| 53 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `    "canonicalization": "FROZEN_PRIMITIVES_CANON",` |
| 54 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `    "duplicate_clauses": "AUDIT_SOURCE_TO_NORMALIZED_MULTIPLICITY__SEMANTICS_DEDUPED_BY_FROZEN_CANON",` |
| 55 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `    "tautologies": "AUDIT_AS_DROPPED_BY_FROZEN_CANON",` |
| 56 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `    "source_normalized_coverage": "EXACT_AUDIT_REQUIRED",` |
| 57 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `    "shared_variable_completeness": "EXACT_REQUIRED",` |
| 58 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `    "sat_source_root_replay": "REQUIRED"` |
| 59 | PASS | Frozen canonicalization, duplicate/tautology provenance, exact coverage and source replay | `  },` |
| 60 | PASS | Zero-boundary SAT/UNSAT semantics and <=8 tuple cap | `  "arity_controls": {` |
| 61 | PASS | Zero-boundary SAT/UNSAT semantics and <=8 tuple cap | `    "zero_boundary_sat": "PRESERVE_SINGLE_EMPTY_TUPLE_AND_WITNESS",` |
| 62 | PASS | Zero-boundary SAT/UNSAT semantics and <=8 tuple cap | `    "zero_boundary_unsat": "PRESERVE_EMPTY_ALLOWED_RELATION_AND_UNSAT_EFFECT",` |
| 63 | PASS | Zero-boundary SAT/UNSAT semantics and <=8 tuple cap | `    "leaf_relation_tuple_cap": 8` |
| 64 | PASS | Zero-boundary SAT/UNSAT semantics and <=8 tuple cap | `  },` |
| 65 | PASS | Forbidden search/data-access operations | `  "forbidden": [` |
| 66 | PASS | Forbidden search/data-access operations | `    "EXHAUSTIVE_GLOBAL_SHARED_VARIABLE_ASSIGNMENT_ENUMERATION",` |
| 67 | PASS | Forbidden search/data-access operations | `    "PRIVATE_ISLAND_PARTITION_ENUMERATION",` |
| 68 | PASS | Forbidden search/data-access operations | `    "UNBOUNDED_SEPARATOR_OR_DECOMPOSITION_BACKTRACKING",` |
| 69 | PASS | Forbidden search/data-access operations | `    "HIDDEN_ORACLE_OR_HINDSIGHT_WORK",` |
| 70 | PASS | Forbidden search/data-access operations | `    "BLIND_POPULATION_GENERATION_OR_REVEAL",` |
| 71 | PASS | Forbidden search/data-access operations | `    "READ_HISTORICAL_V1_1_ADMISSION_OR_HOLDOUT",` |
| 72 | PASS | Forbidden search/data-access operations | `    "LATE_V1_2_V1_3_TUNING"` |
| 73 | PASS | Forbidden search/data-access operations | `  ],` |
| 74 | PASS | Required MICRO/REVEALED positive and negative controls | `  "preblind_controls": {` |
| 75 | PASS | Required MICRO/REVEALED positive and negative controls | `    "positive": [` |
| 76 | PASS | Required MICRO/REVEALED positive and negative controls | `      "SINGLE_VARIABLE_SHARED_BY_AT_LEAST_3_LEAVES",` |
| 77 | PASS | Required MICRO/REVEALED positive and negative controls | `      "TWO_RELATIONS_SHARING_WIDTH_2_SCOPE",` |
| 78 | PASS | Required MICRO/REVEALED positive and negative controls | `      "FRAGMENTED_PORT_PATH_TREE",` |
| 79 | PASS | Required MICRO/REVEALED positive and negative controls | `      "ALPHA_ACYCLIC_MULTI_SEPARATOR_SCOPES"` |
| 80 | PASS | Required MICRO/REVEALED positive and negative controls | `    ],` |
| 81 | PASS | Required MICRO/REVEALED positive and negative controls | `    "negative": [` |
| 82 | PASS | Required MICRO/REVEALED positive and negative controls | `      "CYCLE_XY_YZ_ZX_REJECT",` |
| 83 | PASS | Required MICRO/REVEALED positive and negative controls | `      "BOUNDARY_WIDTH_4_REJECT",` |
| 84 | PASS | Required MICRO/REVEALED positive and negative controls | `      "RANKING_TRAP_NO_BACKTRACKING",` |
| 85 | PASS | Required MICRO/REVEALED positive and negative controls | `      "ZERO_ARITY_UNSAT",` |
| 86 | PASS | Required MICRO/REVEALED positive and negative controls | `      "DUPLICATE_SUBSET_RELATION_SEMANTICS",` |
| 87 | PASS | Required MICRO/REVEALED positive and negative controls | `      "SOURCE_ROOT_REPLAY_TAMPER"` |
| 88 | PASS | Required MICRO/REVEALED positive and negative controls | `    ]` |
| 89 | PASS | Required MICRO/REVEALED positive and negative controls | `  },` |
| 90 | PASS | Required symbolic complexity obligations | `  "complexity_obligations": [` |
| 91 | PASS | Required symbolic complexity obligations | `    "FIXED_RHO_SEPARATOR_CANDIDATES",` |
| 92 | PASS | Required symbolic complexity obligations | `    "TOTAL_RECURSIVE_DECOMPOSITION_NODES",` |
| 93 | PASS | Required symbolic complexity obligations | `    "SCOPE_HYPERGRAPH_CONSTRUCTION",` |
| 94 | PASS | Required symbolic complexity obligations | `    "GYO_AND_JOIN_TREE_RECONSTRUCTION",` |
| 95 | PASS | Required symbolic complexity obligations | `    "LEAF_RELATION_BYTES",` |
| 96 | PASS | Required symbolic complexity obligations | `    "JOIN_TREE_MESSAGE_WORK",` |
| 97 | PASS | Required symbolic complexity obligations | `    "WITNESS_RECONSTRUCTION",` |
| 98 | PASS | Required symbolic complexity obligations | `    "VERIFIER_WORK",` |
| 99 | PASS | Required symbolic complexity obligations | `    "CERTIFICATE_BYTES",` |
| 100 | PASS | Required symbolic complexity obligations | `    "TOTAL_T_CONSTRUCT_DISCOVER_RELATION_JOIN_RECONSTRUCT_VERIFY_IN_ORIGINAL_INPUT_LENGTH"` |
| 101 | PASS | Required symbolic complexity obligations | `  ],` |
| 102 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `  "promotion_firewall": {` |
| 103 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `    "diagnostic_or_micro_pass_is_theorem_evidence": false,` |
| 104 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `    "SAT_IN_P": "NOT_PROVED",` |
| 105 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `    "P_VS_NP": "OPEN",` |
| 106 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `    "NEXT_TARGET_FRONTIER": "UNCHANGED_BY_SECOND_PERSON",` |
| 107 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `    "APMA_UNSEEN_LOCAL_INVARIANT_INDUCTION_FALSIFIER_GATE": "LOCKED",` |
| 108 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `    "scientific_promotion_authority": "FIRST_PERSON_HQ_ONLY"` |
| 109 | PASS | Scientific-promotion firewall remains with HQ; frontier locked | `  },` |
| 110 | PASS | First-counterexample preservation/fail-open policy and JSON close | `  "failure_policy": "PRESERVE_FIRST_COUNTEREXAMPLE_AND_RETURN_FAIL_OPEN_WITHOUT_PATCHING_AFTER_RESULT"` |
| 111 | PASS | First-counterexample preservation/fail-open policy and JSON close | `}` |

## Audit conclusion

No line grants scientific promotion authority, no line unlocks the frontier, no line permits blind-data access, and no line permits semantic deletion of a relation during GYO reduction.
The only unresolved provenance item is the unavailable byte content of the separately pinned draft SHA-256; this candidate explicitly preserves that as a blocker rather than pretending equality.
