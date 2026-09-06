from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import janus_trump_r50g25a_bce_bve_joint_debt_hypergraph as r50g25a
import janus_trump_r50g25b_source_realizability_minimum_joint_debt as r50g25b
import janus_trump_r50g25i_all_1673_source_occurrence_witness_independence as r50g25i

GATE = "JANUS_TRUMP_R50G25J_STRUCTURAL_DP_PIVOT_FREE_EXTENSION_CONFLUENCE_AND_QUOTIENT"
PIVOT = 1
EXPECTED_SOURCES = 30
EXPECTED_OCCURRENCES = 1673
EXPECTED_TARGETS = 1212
EXPECTED_ACTUAL_QUOTIENT = 1074


def canon(formula):
    return r50g25b.canon(formula)


def sha(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def strict_subsumption_antichain(formula) -> bool:
    f = canon(formula)
    sets = [set(c) for c in f]
    return not any(i != j and sets[i] < sets[j] for i in range(len(f)) for j in range(len(f)))


def symbolic_lemma_certificate() -> dict:
    return {
        "name": "EXACT_DP_PIVOT_FREE_EXTENSION_CONFLUENCE",
        "status": "STRUCTURAL_LEMMA_PROVED_FROM_IMPLEMENTED_DEFINITIONS",
        "mechanization_status": "PAPER_PROOF_PLUS_EXECUTABLE_SIDE_CONDITION_AUDIT_NOT_PROOF_ASSISTANT_FORMALIZED",
        "statement": "For every finite canonical CNF F, pivot p occurring in both polarities, and finite extension K containing neither p nor -p: DP_p(F union K) = NF(DP_p(F) union K), where DP_p is exact_dp_record transformed output and NF is strict-subsumption minimization.",
        "definitions": {
            "DP": "DP_p(F)=NF(B_p(F) union R_p(F)); B removes all clauses containing +/-p; R is the set of all non-tautological p-resolvents.",
            "NF": "NF(X) is the inclusion-minimal clause antichain under strict set inclusion, after canonical duplicate removal.",
        },
        "proof_steps": [
            {
                "id": "L1_BASE_EXTENSION",
                "claim": "If K is pivot-free then B_p(F union K)=B_p(F) union K.",
                "reason": "Every clause of K survives the base filter and no pivot-containing source clause changes membership."
            },
            {
                "id": "L2_RESOLVENT_INVARIANCE",
                "claim": "If K is pivot-free then R_p(F union K)=R_p(F).",
                "reason": "K contributes to neither the positive nor negative parent set for pivot p, so the Cartesian parent-pair set is unchanged."
            },
            {
                "id": "L3_NF_ABSORPTION",
                "claim": "For finite clause families A,K: NF(NF(A) union K)=NF(A union K).",
                "reason": "NF(A) contains exactly the inclusion-minimal elements of A. Any nonminimal a in A has a finite descending chain to some m in NF(A) with m subset a, so removing nonminimal A-elements before adjoining K cannot create or destroy a minimal element of A union K. The reverse inclusion is immediate because NF(A) union K is a subset of A union K and every A-minimal element survives into NF(A)."
            },
            {
                "id": "L4_COMPOSE",
                "claim": "DP_p(F union K)=NF(DP_p(F) union K).",
                "reason": "By L1 and L2, DP_p(F union K)=NF(B_p(F) union R_p(F) union K). Apply L3 with A=B_p(F) union R_p(F), whose NF is DP_p(F)."
            },
        ],
        "scope_firewall": {
            "lemma_is_about_exact_DP_and_pivot_free_extensions_only": True,
            "lemma_does_not_prove_all_targets_have_a_useful_cover": True,
            "lemma_does_not_prove_micro_scheduler_terminal_on_arbitrary_CNF": True,
            "lemma_does_not_prove_universal_DIRECT5_coverage": True,
            "lemma_does_not_prove_SAT_in_P": True,
            "lemma_does_not_resolve_P_vs_NP": True,
        },
    }


def run():
    parent = r50g25i.run()
    if parent["next_gate"] != "R50G25J_FROZEN_PAIR_STATE_SOURCE_PREIMAGE_CONFLUENCE_LEMMA_AND_OUTER_COVERAGE_GATE":
        raise AssertionError(("R50G25J_PARENT_GATE_DRIFT", parent["next_gate"]))
    if parent["strong_witness_independent_target_group_count"] != EXPECTED_TARGETS:
        raise AssertionError(("R50G25J_PARENT_STRONG_COUNT_DRIFT", parent["strong_witness_independent_target_group_count"]))
    if parent["genuine_source_preimage_noncommutation_occurrence_count"] != 0:
        raise AssertionError("R50G25J_REQUIRES_ZERO_PARENT_NONCOMMUTATION")

    _parent_a, occurrences = r50g25a.enumerate_pair_post_dp_states()
    if len(occurrences) != EXPECTED_OCCURRENCES:
        raise AssertionError(("R50G25J_OCCURRENCE_COUNT_DRIFT", len(occurrences)))

    unique_targets = {}
    for row in occurrences:
        key = tuple(canon(row["forced_formula"]))
        unique_targets.setdefault(key, canon(row["forced_formula"]))
    if len(unique_targets) != EXPECTED_TARGETS:
        raise AssertionError(("R50G25J_TARGET_COUNT_DRIFT", len(unique_targets)))

    r50g23 = r50g25a.r50g24.r50g23
    r42 = r50g23.r47j.r45a.r42

    pivot_free_cover_violations = []
    nf_antichain_violations = []
    nf_absorption_violations = []
    quotient_groups = defaultdict(list)
    pre_nf_hashes = set()
    cover_size_hist = Counter()
    quotient_clause_count_hist = Counter()
    quotient_literal_count_hist = Counter()

    for target in unique_targets.values():
        cover = r50g25b.exact_minimum_cover(target)
        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]
        cover_size_hist[int(cover["minimum"])] += 1

        if any(PIVOT in clause or -PIVOT in clause for clause in lifted):
            if len(pivot_free_cover_violations) < 24:
                pivot_free_cover_violations.append({
                    "target_hash": r50g23.r50g4.fhash(target),
                    "cover": [list(c) for c in lifted],
                })

        pre_nf = canon(list(target) + list(lifted))
        post_nf = canon(r42.subsumption_minimize(pre_nf))
        pre_nf_hashes.add(sha([list(c) for c in pre_nf]))
        qhash = sha([list(c) for c in post_nf])
        thash = r50g23.r50g4.fhash(target)
        quotient_groups[qhash].append({
            "target_hash": thash,
            "cover_size": int(cover["minimum"]),
            "cover": [list(c) for c in lifted],
            "pre_nf_hash": sha([list(c) for c in pre_nf]),
        })

        if not strict_subsumption_antichain(post_nf):
            if len(nf_antichain_violations) < 24:
                nf_antichain_violations.append({"target_hash": thash, "quotient_hash": qhash})

        # Executable instance of the general NF absorption lemma. This is not
        # the proof; the proof is the finite-poset argument in the certificate.
        lhs = canon(r42.subsumption_minimize(list(r42.subsumption_minimize(target)) + list(lifted)))
        rhs = post_nf
        if lhs != rhs and len(nf_absorption_violations) < 24:
            nf_absorption_violations.append({"target_hash": thash})

        quotient_clause_count_hist[len(post_nf)] += 1
        quotient_literal_count_hist[sum(len(c) for c in post_nf)] += 1

    quotient_count = len(quotient_groups)
    fiber_hist = Counter(len(rows) for rows in quotient_groups.values())
    multi_fibers = [
        {
            "quotient_hash": qhash,
            "fiber_size": len(rows),
            "target_hashes": [r["target_hash"] for r in rows[:12]],
            "cover_sizes": sorted(set(r["cover_size"] for r in rows)),
            "pre_nf_hash_count": len(set(r["pre_nf_hash"] for r in rows)),
        }
        for qhash, rows in sorted(quotient_groups.items())
        if len(rows) > 1
    ]
    multi_fibers.sort(key=lambda x: (-x["fiber_size"], x["quotient_hash"]))

    all_side_conditions = (
        not pivot_free_cover_violations
        and not nf_antichain_violations
        and not nf_absorption_violations
        and quotient_count == EXPECTED_ACTUAL_QUOTIENT
    )

    if not all_side_conditions:
        next_gate = "R50G25K_STRUCTURAL_CONFLUENCE_SIDE_CONDITION_OR_QUOTIENT_DRIFT_FORENSICS"
    else:
        next_gate = "R50G25K_OUTER_COVERAGE_PREREGISTRATION_NO_FAMILY_EXPANSION"

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "symbolic_lemma": symbolic_lemma_certificate(),
        "coverage_contract": {
            "frozen_source_skeleton_count": EXPECTED_SOURCES,
            "new_source_skeletons_added": 0,
            "source_occurrence_count_in_parent": EXPECTED_OCCURRENCES,
            "unique_target_state_count": EXPECTED_TARGETS,
            "structural_lemma_scope_is_not_limited_to_the_1673_occurrences": True,
            "application_side_conditions_audited_on_all_frozen_targets": True,
        },
        "application_side_condition_audit": {
            "pivot_free_cover_violation_count": len(pivot_free_cover_violations),
            "pivot_free_cover_violation_examples": pivot_free_cover_violations,
            "NF_antichain_violation_count": len(nf_antichain_violations),
            "NF_antichain_violation_examples": nf_antichain_violations,
            "NF_absorption_instance_violation_count": len(nf_absorption_violations),
            "NF_absorption_instance_violation_examples": nf_absorption_violations,
            "all_frozen_target_side_conditions_pass": all_side_conditions,
        },
        "quotient_audit": {
            "operator": "Q(T)=NF(T union K(T)), with deterministic exact minimum binary incidence cover K(T)",
            "target_count": EXPECTED_TARGETS,
            "pre_NF_union_unique_count": len(pre_nf_hashes),
            "canonical_quotient_state_count": quotient_count,
            "compression_count": EXPECTED_TARGETS - quotient_count,
            "compression_ratio": (EXPECTED_TARGETS - quotient_count) / EXPECTED_TARGETS,
            "fiber_size_histogram": {str(k): int(v) for k, v in sorted(fiber_hist.items())},
            "multi_fiber_count": sum(1 for rows in quotient_groups.values() if len(rows) > 1),
            "largest_fibers": multi_fibers[:24],
            "cover_size_histogram": {str(k): int(v) for k, v in sorted(cover_size_hist.items())},
            "quotient_clause_count_histogram": {str(k): int(v) for k, v in sorted(quotient_clause_count_hist.items())},
            "quotient_literal_count_histogram": {str(k): int(v) for k, v in sorted(quotient_literal_count_hist.items())},
            "equivalence_relation": "T1 ~ T2 iff NF(T1 union K(T1)) = NF(T2 union K(T2))",
            "interpretation": "The 1212->1074 compression is the kernel quotient of deterministic cover augmentation followed by strict-subsumption normal form; source-preimage identity is absent from Q by the structural lemma.",
        },
        "next_gate": next_gate,
        "interpretation_contract": {
            "this_gate_replaces_source_preimage_replay_with_a_structural_exact_DP_extension_lemma": True,
            "the_lemma_is_mathematical_reasoning_over_the_implemented_set_operators_not_a_proof_assistant_artifact": True,
            "the_quotient_equivalence_is_structural_but_does_not_by_itself_prove_scheduler_termination_outside_the_frozen_domain": True,
            "no_outer_family_expansion_is_performed_here": True,
        },
        "firewall": {
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
