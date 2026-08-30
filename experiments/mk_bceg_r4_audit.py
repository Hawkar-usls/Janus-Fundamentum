#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--cross-dir", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--journal", required=True)
    args = ap.parse_args()
    root = Path(args.root)
    cross = Path(args.cross_dir)
    prereg = load(args.prereg)
    hostile = load(root / "hostile_result.json")
    scaling = load(root / "scaling_result.json")
    storm = load(root / "storm" / "storm_result.json")
    old_reverify = load(root / "base" / "old_package_reverify.json")
    p0 = load(root / "base" / "package_0.json")
    p2 = load(root / "base" / "package_2.json")

    reports = []
    for p in sorted(cross.glob("cross_*.json")):
        reports.append(load(p))
    os_families = sorted(set(r.get("os") for r in reports))
    hash_vectors = [r.get("canonical_package_hashes") for r in reports]
    cross_hash_equal = len(hash_vectors) >= 2 and all(v == hash_vectors[0] for v in hash_vectors[1:])
    cross_pass = len(os_families) >= 2 and all(r.get("verdict") == "PASS" for r in reports) and cross_hash_equal

    r4a = cross_pass and all(r.get("producer_cache_available") is False and r.get("producer_code_imported") is False for r in reports)
    r4b = cross_pass
    r4c = hostile["gates"]["R4_C_RECEIPT_NECROMANCER"]
    r4d = (
        old_reverify.get("verdict") == "PASS"
        and p0["backend"]["release_version"] == "1.0"
        and p2["backend"]["release_version"] == "2.0"
        and old_reverify.get("accepted_backend_contract_digest") == p0["backend_contract_digest"]
    )
    r4e = hostile["gates"]["R4_E_LIABILITY_BOMB"]
    r4f = scaling["verdict"] == "BACKEND_VERIFICATION_COMPLEXITY_BARRIER"
    r4g = (
        storm["verdict"] == "FINITE_SWITCH_STORM_SURVIVOR_NOT_THEOREM"
        and storm["all_lineage_depths_exact"] is True
        and storm["all_switches_receipt_gated"] is True
    )
    r4h = hostile["gates"]["R4_H_CORRECT_REFUSAL"]
    gates = [
        {"gate":"R4_A_FRESH_PROCESS_AMNESIA","passed":r4a},
        {"gate":"R4_B_CROSS_MACHINE_CANONICAL_REPLAY","passed":r4b,"os_families":os_families,"canonical_hash_vectors_equal":cross_hash_equal},
        {"gate":"R4_C_RECEIPT_NECROMANCER","passed":r4c},
        {"gate":"R4_D_BACKEND_SHIP_OF_THESEUS","passed":r4d},
        {"gate":"R4_E_LIABILITY_BOMB","passed":r4e},
        {"gate":"R4_F_VERIFICATION_SCALING","passed":r4f,"classification":scaling["verdict"]},
        {"gate":"R4_G_SWITCH_STORM","passed":r4g},
        {"gate":"R4_H_CORRECT_REFUSAL","passed":r4h},
        {"gate":"SCIENTIFIC_BOUNDARY","passed":prereg["scientific_boundary"]["P_VS_NP"]=="OPEN" and prereg["scientific_boundary"]["SAT_in_P_proved"] is False},
    ]
    core_pass = all(g["passed"] for g in gates)
    auth_gap = hostile["receipt_authentication_diagnostic"]["malicious_recomputed_receipt_accepted"] is True
    if not core_pass:
        verdict = "REFUTED_HOSTILE_PROOF_STATE_PORTABILITY"
    elif auth_gap:
        verdict = "FINITE_HOSTILE_PORTABILITY_CORE_SURVIVOR__RECEIPT_SIGNER_AUTHENTICATION_GAP_OPEN"
    else:
        verdict = "FINITE_HOSTILE_PORTABILITY_SURVIVOR_NOT_THEOREM"

    scale_rows = scaling["rows"]
    result = {
        "schema":"JANUS/MK_BCEG/R4/RESULT/v1.0",
        "status":"COMPLETE_FROZEN_AUDIT",
        "verdict":verdict,
        "title":"R4 — HOSTILE PROOF-STATE PORTABILITY",
        "authority_law":"AUTHORITY_IS_TRANSITIVE_ONLY_THROUGH_VERIFIED_TRANSITIONS",
        "core_gates":gates,
        "cross_machine":{
            "os_families":os_families,
            "reports":reports,
            "canonical_package_hash_vectors_equal":cross_hash_equal,
        },
        "backend_ship_of_theseus":{
            "old_package_backend_version":p0["backend"]["release_version"],
            "later_package_backend_version":p2["backend"]["release_version"],
            "old_package_reverified_by_new_verifier":old_reverify.get("verdict")=="PASS",
            "old_package_hash":p0["package_hash"],
            "old_backend_contract_digest":p0["backend_contract_digest"],
        },
        "receipt_necromancer":hostile["receipt_necromancer"],
        "receipt_signer_authentication_gap":{
            "detected":auth_gap,
            "probe":hostile["receipt_authentication_diagnostic"],
            "consequence":"The R4 receipt chain is content-integrity and semantic-replay bound, but an unkeyed SHA-256 receipt hash alone cannot authenticate who ran the verifier. A malicious party able to author new receipt bytes can recompute the hash. Therefore release-grade TRUMP authority remains blocked pending a cryptographic signature/attestation trust root or mandatory fresh independent replay at consumption time.",
            "release_security_complete":False,
        },
        "liability_bomb":hostile["liability_bomb"],
        "verification_scaling":{
            "verdict":scaling["verdict"],
            "first_rung":scale_rows[0],
            "last_rung":scale_rows[-1],
            "backend_algorithm_fact":scaling["backend_algorithm_fact"],
        },
        "switch_storm":storm,
        "correct_refusal":hostile["correct_refusal"],
        "new_law":"AUTHORITY_IS_TRANSITIVE_ONLY_THROUGH_VERIFIED_TRANSITIONS, BUT PORTABLE RELEASE AUTHORITY ALSO REQUIRES AUTHENTICATED VERIFIER OR FRESH REPLAY; HASH BINDING ALONE IS NOT SIGNER AUTHENTICATION.",
        "theorem_candidate":"POLYNOMIAL_PORTABLE_CERTIFIED_LIFECYCLE_INTERFACE_LEMMA",
        "scientific_boundary":{
            "finite_R4_core_success_is_universal_theorem":False,
            "cryptographic_release_lineage_proved":False,
            "portable_polynomial_verification_proved":False,
            "SAT_in_P_proved":False,
            "P_VS_NP":"OPEN",
            "TRUMP_released":False,
        },
        "next_frontier":"R4_1_AUTHENTICATED_RECEIPT_LINEAGE: add a real verifier trust root (signature/attestation or mandatory fresh-replay authority), then repeat receipt necromancer and cross-machine portability without allowing hash-only forged receipts. After that, extend verification scaling beyond exhaustive semantic fallback with proof certificates whose verification cost is separately bounded.",
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    with open(args.journal, "w") as j:
        for g in gates:
            j.write(json.dumps({"event":"GATE","gate":g}, separators=(",", ":")) + "\n")
        j.write(json.dumps({"event":"RECEIPT_AUTHENTICATION_DIAGNOSTIC","detected_gap":auth_gap}, separators=(",", ":")) + "\n")
        j.write(json.dumps({"event":"FROZEN_VERDICT","verdict":verdict}, separators=(",", ":")) + "\n")
    print(json.dumps({"verdict":verdict,"gates":[(g["gate"],g["passed"]) for g in gates],"os_families":os_families,"receipt_authentication_gap":auth_gap}, indent=2))
    if not core_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
