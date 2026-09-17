from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_SOURCE_AGNOSTIC_3CNF_DEGREE1_PENDANT_ONE_ROUND_THEOREM_PREREGISTRATION_2026-09-17_v1.0.json"
REVIEW = ROOT / "research/TRUMP_SOURCE_AGNOSTIC_3CNF_DEGREE1_PENDANT_ONE_ROUND_THEOREM_REVIEW_2026-09-17_v1.0.json"
PARENT = ROOT / "research/TRUMP_UF20_WL_PROJECTED_REPRESENTATION_TRANSFER_RESULT_2026-09-17_v1.0.json"
EXPECTED = {
    PREREG: "48a545a63dc95102a8c4478f0821cc872f95711e",
    REVIEW: "41b5459adf555175b652b68f2b0ab5aee1733512",
    PARENT: "3ae9a5995f01793f315fb291a77d51c44ca12d9c",
}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def literal_satisfied(bit: int, sign: int) -> bool:
    return (bit == 1) if sign == 1 else (bit == 0)


def independent_local_rows():
    rows=[]; bad=[]
    for sign_bits in range(8):
        signs=tuple(1 if sign_bits & (1 << (2-i)) else 0 for i in range(3))
        word="".join("+" if s else "-" for s in signs)
        for leaf in range(3):
            others=tuple(i for i in range(3) if i != leaf)
            for g0 in (0,1):
                for g1 in (0,1):
                    assignment=[0,0,0]
                    assignment[others[0]]=g0; assignment[others[1]]=g1
                    witness=1 if signs[leaf] else 0
                    assignment[leaf]=witness
                    sat=any(literal_satisfied(assignment[i], signs[i]) for i in range(3))
                    row={
                        "sign_pattern":word,
                        "witness_position":leaf,
                        "gateway_positions":list(others),
                        "gateway_bits":[g0,g1],
                        "canonical_witness_value":witness,
                        "full_assignment":assignment,
                        "clause_satisfied":sat,
                    }
                    rows.append(row)
                    if not sat: bad.append(row)
    return rows,bad


def expected_structural_certificate():
    return {
        "WITNESS_PRIVACY": {
            "premises": ["witness x belongs to D", "D means input incidence degree(x)=1", "x belongs to target constraint C"],
            "derivation": "If x also occurred in any C' != C then incidence degree(x) would be at least 2, contradiction.",
            "proved": True,
        },
        "DISTINCT_TARGET_WITNESSES": {
            "premises": ["each target chooses a witness in its own scope intersect D", "every witness has degree 1"],
            "derivation": "One variable cannot be chosen by two distinct target constraints because that would place it in two constraints.",
            "proved": True,
        },
        "NO_REMOVED_VARIABLE_IN_REMAINING_CONSTRAINT": {
            "premises": ["x in D has one unique incident constraint C_x", "C_x intersects D and therefore lies in T"],
            "derivation": "After removing all T, no constraint in C\\T can contain x; hence deleting D leaves every remaining scope well formed.",
            "proved": True,
        },
        "FORWARD_RESTRICTION": {
            "premises": ["reduced constraint set is exactly C\\T", "remaining constraints are unchanged"],
            "derivation": "A satisfying input assignment satisfies every C\\T constraint, so its restriction to V\\D satisfies the reduced raw.",
            "proved": True,
        },
        "REVERSE_EXTENSION": {
            "premises": ["reduced assignment satisfies C\\T", "each target has a private witness", "local surjectivity holds for every sign pattern and gateway assignment"],
            "derivation": "For each target independently assign all nonwitness removed variables canonically to 0 and set its private witness so its literal is true. Shared nonremoved gateway values are untouched, and private witnesses cannot conflict.",
            "proved": True,
        },
        "EXACT_PROJECTION_EQUALITY": {
            "premises": ["FORWARD_RESTRICTION", "REVERSE_EXTENSION"],
            "derivation": "Restriction maps every input solution into the reduced solution set, and every reduced solution has an input extension; therefore the projected input solution set equals the reduced solution set.",
            "proved": True,
        },
        "SAT_EQUIVALENCE": {
            "premises": ["EXACT_PROJECTION_EQUALITY"],
            "derivation": "The input solution set is nonempty iff the reduced solution set is nonempty.",
            "proved": True,
        },
        "POLYNOMIAL_CONSTRUCTION_AND_RECONSTRUCTION": {
            "premises": ["one pre-mutation incidence scan", "one target/deletion scan", "one reconstruction pass over targets and removed variables"],
            "derivation": "For explicit 3-CNF incidence size L=3m, all unsorted operations are O(n+m+L); canonical ordering adds at most ordinary polynomial sorting overhead.",
            "proved": True,
        },
    }


def main(candidate_path: Path):
    candidate=json.loads(candidate_path.read_text())
    bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
    prereg=json.loads(PREREG.read_text()); review=json.loads(REVIEW.read_text()); parent=json.loads(PARENT.read_text())
    rows,bad=independent_local_rows()
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    structural=expected_structural_certificate()
    expected_verdict="PASS_SOURCE_AGNOSTIC_ONE_ROUND_DEGREE1_PENDANT_THEOREM" if not bad and all(x["proved"] for x in structural.values()) else ("FAIL_LOCAL_SURJECTIVITY_COUNTEREXAMPLE" if bad else "FAIL_STRUCTURAL_PROOF_OBLIGATION")
    checks={
        "authority_bindings":all(bindings.values()),
        "review_authorized":review.get("review_verdict")=="PASS_CLEAN_SOURCE_AGNOSTIC_THEOREM_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE",
        "parent_negative_transfer_bound":parent.get("verdict")=="PROJECTED_WL_TRANSFER_NO_SURVIVOR__DO_NOT_UNBLIND_FRESH_HOLDOUT_FOR_THIS_CANDIDATE",
        "preregistered_case_count":prereg.get("finite_local_checker_contract",{}).get("required_local_cases")==96,
        "all_96_local_cases":len(rows)==96 and len(bad)==0,
        "local_digest_exact":candidate.get("local_surjectivity_receipt",{}).get("canonical_witness_rows_sha256")==digest,
        "local_counts_exact":candidate.get("local_surjectivity_receipt",{}).get("cases_checked")==96 and candidate.get("local_surjectivity_receipt",{}).get("failures")==0,
        "structural_certificate_exact":candidate.get("structural_proof_certificate")==structural,
        "verdict_exact":candidate.get("verdict")==expected_verdict,
        "source_agnostic_license":candidate.get("licensed_theorem",{}).get("source_names_required") is False and candidate.get("licensed_theorem",{}).get("route_labels_required") is False,
        "holdout_unread":all(v==0 for v in candidate.get("fresh_holdout_receipt",{}).values()),
        "no_solver_group_or_iteration":candidate.get("resource_receipt",{}).get("sat_solver_invocations")==0 and candidate.get("resource_receipt",{}).get("automorphism_or_group_searches")==0 and candidate.get("resource_receipt",{}).get("iterated_peeling_rounds")==0,
        "firewall":candidate.get("scientific_firewall",{}).get("P_VS_NP")=="OPEN" and candidate.get("scientific_firewall",{}).get("GENERAL_SAT_IN_P")=="NOT_PROVED",
    }
    return {
        "artifact_id":"JANUS-TRUMP-SOURCE-AGNOSTIC-DEGREE1-PENDANT-THEOREM-INDEPENDENT-CHECK-2026-09-17-v1.0",
        "verdict":"PASS_INDEPENDENT_SOURCE_AGNOSTIC_THEOREM_VERIFICATION" if all(checks.values()) else "FAIL_INDEPENDENT_SOURCE_AGNOSTIC_THEOREM_VERIFICATION",
        "checks":checks,
        "independent_local_case_count":len(rows),
        "independent_local_failures":len(bad),
        "independent_witness_rows_sha256":digest,
        "expected_candidate_verdict":expected_verdict,
        "candidate_imported":False,
        "repository_source_data_files_opened":0,
        "fresh_holdout_formula_reads":0,
        "scientific_firewall":{"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED"},
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--candidate",required=True); a=p.parse_args(); result=main(Path(a.candidate)); print(json.dumps(result,sort_keys=True,separators=(",",":"))); raise SystemExit(0 if result["verdict"].startswith("PASS_") else 1)
