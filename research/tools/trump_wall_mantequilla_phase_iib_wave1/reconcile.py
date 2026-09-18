from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

IDS=("CHAL_001","CHAL_002","CHAL_003","CHAL_004")

def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def main():
    if len(sys.argv)!=5:
        raise SystemExit("usage: reconcile.py PUBLIC_DIR PRIVATE_GT RUNS_DIR OUTPUT")
    public_dir=Path(sys.argv[1])
    private=json.load(open(sys.argv[2],encoding="utf-8"))
    runs=Path(sys.argv[3])
    receipt=json.load(open(public_dir/"commitment.json",encoding="utf-8"))
    if sha(private)!=receipt["ground_truth_commitment_sha256"]:
        raise RuntimeError("GROUND_TRUTH_COMMITMENT_MISMATCH")
    gt=private["ground_truth"]
    rows=[]
    all_pass=True
    for sid in IDS:
        cand=json.load(open(runs/sid/"candidate.json",encoding="utf-8"))
        ind=json.load(open(runs/sid/"independent.json",encoding="utf-8"))
        expected=gt["specimens"][sid]
        truth=ind["checker_only_semantic_microscope"]["direct_local_existential_truth_table"]
        independent_ok=ind["verdict"]=="PASS_INDEPENDENT_PHASE_IIB_WAVE1_MANTEQUILLA_VERIFICATION" and all(ind["checks"].values())
        exact_truth=truth==expected["truth_table"]
        semantic_ok=cand["semantic_class"]==expected["expected_semantic_class"]==ind["semantic_class"]
        verdict_ok=cand["verdict"]==expected["expected_candidate_verdict"]==ind["scientific_verdict"]
        orcsp_ok=ind["checks"]["direct_truth_equals_orcsp"]
        robdd_ok=ind["checks"]["direct_truth_equals_robdd"]
        firewall_ok=(cand["accounting"]["constructor_boundary_cube_assignments_enumerated"]==0 and cand["accounting"]["sat_solver_invocations"]==0)
        mechanism_pass=all((independent_ok,exact_truth,semantic_ok,verdict_ok,orcsp_ok,robdd_ok,firewall_ok))
        all_pass &= mechanism_pass
        rows.append({
            "specimen_id":sid,
            "class_id":expected["class_id"],
            "truth_table":truth,
            "expected_correlated":expected["expected_correlated"],
            "semantic_class":cand["semantic_class"],
            "candidate_scientific_verdict":cand["verdict"],
            "mechanism_exact_handling_pass":mechanism_pass,
            "candidate_runtime_seconds":cand["candidate_runtime_seconds"],
            "independent_checker_runtime_seconds":ind["independent_checker_runtime_seconds"],
            "canonical_orcsp_symbol_count":cand["accounting"]["canonical_orcsp_symbol_count"],
            "raw_four_branch_residual_symbol_count":cand["accounting"]["raw_four_branch_residual_symbol_count"],
            "robdd_live_nonterminal_nodes":cand["accounting"]["robdd_live_nonterminal_nodes"],
            "robdd_total_operations":cand["accounting"]["robdd_total_operations"],
            "robdd_node_bound":cand["accounting"]["robdd_node_bound"],
            "robdd_operation_bound":cand["accounting"]["robdd_operation_bound"],
            "constructor_boundary_cube_assignments_enumerated":cand["accounting"]["constructor_boundary_cube_assignments_enumerated"],
            "sat_solver_invocations":cand["accounting"]["sat_solver_invocations"],
            "independent_verdict":ind["verdict"]
        })
    correlated=[r for r in rows if r["expected_correlated"]]
    factorized=[r for r in rows if not r["expected_correlated"]]
    result={
        "artifact_id":"JANUS-TRUMP-WALL-MANTEQUILLA-PHASE-IIB-WAVE1-CONTROLLED-WALL-CHALLENGE-RESULT-2026-09-18-v1.0",
        "date":"2026-09-18",
        "evidence_class":"CONTROLLED_MECHANISM_CHALLENGE_EVIDENCE",
        "scientific_outcome":"PASS_CONTROLLED_WAVE1_ALL_FOUR_EXACT" if all_pass else "FAIL_CONTROLLED_WAVE1_RECONCILIATION",
        "all_four_mechanism_exact_handling_pass":all_pass,
        "rows":rows,
        "summary":{
            "N_controlled_specimens":4,
            "N_factorized_nontrivial":len(factorized),
            "N_correlated":len(correlated),
            "N_exact_handling_pass":sum(r["mechanism_exact_handling_pass"] for r in rows),
            "N_exact_handling_fail":sum(not r["mechanism_exact_handling_pass"] for r in rows)
        },
        "commitment":{
            "ground_truth_commitment_sha256":receipt["ground_truth_commitment_sha256"],
            "public_bundle_payload_sha256":receipt["public_bundle_payload_sha256"],
            "commitment_verified":True
        },
        "ground_truth_reveal":gt,
        "interpretation":{
            "controlled_success_tests_wall_handling_not_wall_discovery":True,
            "factorized_candidate_FAIL_UNARY_FACTORIZATION_is_not_representation_failure_if_exact":True,
            "correlated_candidate_PASS_is_local_controlled_exact_interface_only":True,
            "natural_prevalence_inference_forbidden":True
        },
        "scientific_firewall":{
            "PHASE_I_NATURAL_EVIDENCE_UNCHANGED":True,
            "POLYNOMIAL_BRIDGE":"NOT_PROVED",
            "GENERAL_K_CLASS":"NOT_PROVED",
            "MULTI_INTERFACE_COMPOSITION":"NOT_PROVED",
            "GENERAL_SAT_IN_P":"NOT_PROVED",
            "P_VS_NP":"OPEN"
        }
    }
    result["result_semantic_digest_sha256"]=sha({
        "scientific_outcome":result["scientific_outcome"],
        "rows":[{
            "specimen_id":r["specimen_id"],
            "class_id":r["class_id"],
            "truth_table":r["truth_table"],
            "semantic_class":r["semantic_class"],
            "candidate_scientific_verdict":r["candidate_scientific_verdict"],
            "mechanism_exact_handling_pass":r["mechanism_exact_handling_pass"],
            "orcsp":r["canonical_orcsp_symbol_count"],
            "robdd_nodes":r["robdd_live_nonterminal_nodes"],
            "robdd_ops":r["robdd_total_operations"]
        } for r in rows]
    })
    Path(sys.argv[4]).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"scientific_outcome":result["scientific_outcome"],"summary":result["summary"],"digest":result["result_semantic_digest_sha256"]},sort_keys=True))
    if not all_pass:
        raise SystemExit(1)

if __name__=="__main__":
    main()
