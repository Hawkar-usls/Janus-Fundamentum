from __future__ import annotations

import hashlib
import json
from pathlib import Path

PRE = Path("research/JANUS_TRUMP_R50G25BA25_PREREGISTRATION.json")
RES = Path("ba25_result.json")
VER1 = Path("ba25_verify.json")
VER2 = Path("ba25_verify_v2.json")
GAP = Path("research/JANUS_TRUMP_R50G25BA25_SOURCE_RECONSTRUCTION_EVIDENCE_GAP_RECEIPT.json")
HARD = Path("research/JANUS_TRUMP_R50G25BA25_RECONSTRUCTION_HARDENING.json")
VERIFY_V2_FILE = Path("research/verify_janus_trump_r50g25ba25_v2.py")
OUT = Path("ba25_completion_v2.json")

PREREG_COMMIT = "466e839107f224cdf6ea7ec5294eef8bd9003cd6"
GAP_COMMIT = "a9eb4a65d0fa9c57fc70603ba63037f57ed479cf"
GAP_BLOB = "8596960a0df33f7361303b94042468d7086ea16e"
HARDENING_COMMIT = "1ca79fa8078e0428cae669d47df72354e59f06c2"
HARDENING_BLOB = "f3f4f8da6240ca061c3085726d9ada1bfe6823df"
VERIFY_V2_COMMIT = "57649038bd8b35e74464c878c0c15f81f3ff8ad1"
VERIFY_V2_BLOB = "a54c2d8a141ff386650793e34104ace1c34409a2"
OLD_RUN = 34410959446

BA20_FINAL_META_COMMIT = "fa0b503233cb873282c0d8317adf89e48223402b"
BA20_FINAL_META_BLOB = "a09eae8aa44b68530a5d24e542056c13a24ab865"
BA20_RECEIPT_COMMIT = "ef963eba447b1d88ef13eddc9b888138be4f4565"
BA20_RECEIPT_BLOB = "ed11ffc951eec1bf1a1c01d60699876f8a408018"
BA20_BASE_COMMIT = "6e895880f2cebeddd0ee72d6b90704d62434bc67"
BA20_BASE_BLOB = "c3112e59a213bf297d1bd757e251905f64d5900b"
BA20_V2_COMMIT = "ff94c204051d173ca4fabb51ad33e3260d13d7c0"
BA20_V2_BLOB = "6c2271f18677cebc9c37eab42c42b8228b41967b"
BA4_SCHEMA_BLOB = "c85eab7d0bb1557bc0c472bbc8c2086b08625a4c"

BA21_FINAL_META_COMMIT = "085bcdec8cd7613ad99e8766894010e6dd3d8fe4"
BA21_FINAL_META_BLOB = "e5f66732279c1b26b4f9a1fd991d4055eac9209e"
BA21_RECEIPT_COMMIT = "dd3cd439bffd67dd33790be83e719625310c0726"
BA21_RECEIPT_BLOB = "d94b91c7ed4b8bb3cce7efb52d02813bb222916a"
BA21_IMPL_COMMIT = "8da4e0560bdbbc31d94e7e4ab65a098222e5f5c1"
BA21_IMPL_BLOB = "22b891038e34dedcb53b75a74563cbe535c55e21"

SOURCE_DEF = (
    "LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS AND "
    "SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS AND "
    "DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES"
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main() -> None:
    pre = json.loads(PRE.read_text())
    res = json.loads(RES.read_text())
    ver1 = json.loads(VER1.read_text())
    ver2 = json.loads(VER2.read_text())
    gap = json.loads(GAP.read_text())
    hard = json.loads(HARD.read_text())
    names = pre["required_passes"]

    a2 = ver2.get("assertions", {})
    schema = ver2.get("reconstruction_schema_hash_provenance", {})

    local_ok = a2.get("LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS") is True
    sealed_ok = a2.get("SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS") is True
    direct_ok = a2.get("DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES") is True
    strict_source = bool(local_ok and sealed_ok and direct_ok)

    expected_schema = {
        "BA20_final_meta": {"commit": BA20_FINAL_META_COMMIT, "blob": BA20_FINAL_META_BLOB},
        "BA20_result_receipt": {"commit": BA20_RECEIPT_COMMIT, "blob": BA20_RECEIPT_BLOB},
        "BA20_base_reconstruction": {"commit": BA20_BASE_COMMIT, "blob": BA20_BASE_BLOB},
        "BA20_authoritative_v2_wrapper": {"commit": BA20_V2_COMMIT, "blob": BA20_V2_BLOB},
        "BA4_carrier_schema": {"blob": BA4_SCHEMA_BLOB},
        "BA21_final_meta": {"commit": BA21_FINAL_META_COMMIT, "blob": BA21_FINAL_META_BLOB},
        "BA21_result_receipt": {"commit": BA21_RECEIPT_COMMIT, "blob": BA21_RECEIPT_BLOB},
        "BA21_compressed_projection_impl": {"commit": BA21_IMPL_COMMIT, "blob": BA21_IMPL_BLOB},
        "hardening": {"commit": HARDENING_COMMIT, "blob": HARDENING_BLOB},
    }

    schema_core = {k: schema.get(k) for k in expected_schema}
    checks = {
        "prereg_frozen": pre.get("state") == "FROZEN_BEFORE_IMPLEMENTATION",
        "exact_34_names": len(names) == 34 and len(set(names)) == 34 and set(res.get("pass_map", {})) == set(names),
        "historical_run_never_promoted": (
            gap.get("historical_green_run", {}).get("run_id") == OLD_RUN
            and gap.get("historical_green_run", {}).get("scientific_authority") is False
            and gap.get("historical_green_run", {}).get("scientific_result") == "NOT_PROMOTED"
            and gap.get("historical_green_run", {}).get("must_never_be_retroactively_promoted_to_authoritative") is True
        ),
        "append_only_objects_pinned": (
            git_blob_sha(GAP) == GAP_BLOB
            and git_blob_sha(HARD) == HARDENING_BLOB
            and git_blob_sha(VERIFY_V2_FILE) == VERIFY_V2_BLOB
            and hard.get("state") == "FROZEN_APPEND_ONLY_RECONSTRUCTION_HARDENING_BEFORE_VERIFIER_V2"
        ),
        "builder_scope_except_hardened_source_and_final_two": (
            res.get("required") == 34
            and res.get("P_BA25_FINAL") == 0
            and res.get("falsifiers") == []
            and all(
                res["pass_map"][n]
                for n in names
                if n not in {"SOURCE_RECONSTRUCTION_PASS", "INDEPENDENT_REPLAY_PASS", "PRESEAL_COMPLETENESS_PASS"}
            )
            and res["pass_map"]["INDEPENDENT_REPLAY_PASS"] is False
            and res["pass_map"]["PRESEAL_COMPLETENESS_PASS"] is False
        ),
        "legacy_verifier_independent_pass": (
            ver1.get("status") == "PASS"
            and ver1.get("implementation_imported") is False
            and ver1.get("falsifiers") == []
        ),
        "verifier_v2_independent_pass": (
            ver2.get("status") == "PASS"
            and ver2.get("implementation_imported") is False
            and ver2.get("falsifiers") == []
        ),
        "runtime_sealed_parent_replay_true": ver2.get("sealed_parent_reconstruction_replay") is True,
        "runtime_replayed_cases_gt_zero": int(ver2.get("number_of_replayed_cases", 0)) > 0,
        "runtime_original_cnf_zero_failures": int(ver2.get("original_CNF_validation_failures", -1)) == 0,
        "runtime_parent_formula_zero_mismatches": int(ver2.get("parent_reconstruction_formula_mismatches", -1)) == 0,
        "runtime_abstract_source_zero_failures": int(ver2.get("abstract_source_validation_failures", -1)) == 0,
        "exact_parent_meta_commits": (
            ver2.get("parent_BA20_commit") == BA20_FINAL_META_COMMIT
            and ver2.get("parent_BA21_commit") == BA21_FINAL_META_COMMIT
        ),
        "exact_parent_commit_blob_receipt_schema": schema_core == expected_schema,
        "source_component_local": local_ok,
        "source_component_sealed_replay": sealed_ok,
        "source_component_direct_original_ba4": direct_ok,
        "source_reconstruction_exact_formula": (
            ver2.get("SOURCE_RECONSTRUCTION_PASS_definition") == SOURCE_DEF
            and ver2.get("SOURCE_RECONSTRUCTION_PASS") is strict_source
            and a2.get("SOURCE_RECONSTRUCTION_PASS") is strict_source
            and hard.get("SOURCE_RECONSTRUCTION_PASS_definition", {}).get("no_synthesis_from_overall_verifier_pass") is True
        ),
        "source_reconstruction_pass": strict_source,
        "applicability_firewall": (
            a2.get("arbitrary_foreign_CNF_BA4_carrier_coverage_claimed") is False
            and ver2.get("nonclaims", {}).get("arbitrary_foreign_CNF_BA4_carrier_coverage") is False
            and all(
                row.get("foreign_clause_carrier_claimed") is False
                for row in ver2.get("applicability", [])
                if row.get("classification") == "BA20_BA21_ROUTE_APPLICABLE"
            )
        ),
        "truth_firewall": (
            ver2.get("nonclaims", {}).get("SAT_IN_P") == "NOT_PROVED"
            and ver2.get("nonclaims", {}).get("P_VS_NP") == "OPEN"
            and res.get("theorem", {}).get("SAT_IN_P") == "NOT_PROVED"
            and res.get("theorem", {}).get("P_VS_NP") == "OPEN"
        ),
        "stop_before_ba26": (
            ver2.get("STOP", {}).get("BA26_started") is False
            and res.get("STOP", {}).get("BA26_started") is False
            and res.get("STOP", {}).get("next_theorem_gate_started") is False
            and res.get("STOP", {}).get("external_literature_novelty_equivalence_audit_required") is True
        ),
    }

    independent_pass = bool(checks["legacy_verifier_independent_pass"] and checks["verifier_v2_independent_pass"])

    # Rebuild the final pass map. The legacy builder's SOURCE_RECONSTRUCTION_PASS bit is deliberately ignored.
    pass_map = {}
    for name in names:
        if name == "SOURCE_RECONSTRUCTION_PASS":
            pass_map[name] = strict_source
        elif name == "INDEPENDENT_REPLAY_PASS":
            pass_map[name] = independent_pass
        elif name == "PRESEAL_COMPLETENESS_PASS":
            pass_map[name] = False
        else:
            pass_map[name] = bool(res["pass_map"][name])

    preseal_ready = all(checks.values()) and all(pass_map[n] for n in names if n != "PRESEAL_COMPLETENESS_PASS")
    pass_map["PRESEAL_COMPLETENESS_PASS"] = bool(preseal_ready)
    all_pass = bool(all(checks.values()) and all(pass_map.values()))

    if not all_pass:
        out = {
            "gate": pre.get("gate"),
            "entry_type": "BA25_PRESEAL_V2_SOURCE_RECONSTRUCTION_HARDENED",
            "status": "FAIL",
            "scientific_authority": False,
            "checks": checks,
            "required_passes": names,
            "pass_map": pass_map,
            "passes": sum(bool(x) for x in pass_map.values()),
            "required": 34,
            "P_BA25_FINAL": 0,
            "falsifiers": [k for k, v in checks.items() if not v] + [n for n, v in pass_map.items() if not v],
            "SOURCE_RECONSTRUCTION_PASS": strict_source,
            "STOP": {
                "BA25": "UNSEALED",
                "BA26_started": False,
                "next_permitted_object": "AUTHORITATIVE_WORKFLOW_V2_ONLY_AFTER_PRESEAL_V2_FIXED_OR_PASSED",
            },
        }
        OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps(out, indent=2, sort_keys=True))
        raise SystemExit(1)

    out = {
        "gate": pre["gate"],
        "entry_type": "BA25_PRESEAL_V2_SOURCE_RECONSTRUCTION_HARDENED",
        "status": "PRESEAL_V2_PASS_PENDING_NEW_AUTHORITATIVE_WORKFLOW_V2",
        "scientific_authority": False,
        "historical_run_34410959446": "UNSEALED_SOURCE_RECONSTRUCTION_EVIDENCE_GAP_NOT_PROMOTED",
        "checks": checks,
        "required_passes": names,
        "pass_map": pass_map,
        "passes": 34,
        "required": 34,
        "P_BA25_FINAL": 1,
        "P_BA25_FINAL_authority": "CANDIDATE_ONLY_UNTIL_NEW_AUTHORITATIVE_WORKFLOW_V2_RUN",
        "independent_replay": "PASS",
        "preseal_completeness": "PASS",
        "SOURCE_RECONSTRUCTION_PASS": True,
        "SOURCE_RECONSTRUCTION_PASS_definition": SOURCE_DEF,
        "sealed_parent_reconstruction_replay": True,
        "number_of_replayed_cases": int(ver2["number_of_replayed_cases"]),
        "original_CNF_validation_failures": 0,
        "parent_BA20_commit": BA20_FINAL_META_COMMIT,
        "parent_BA21_commit": BA21_FINAL_META_COMMIT,
        "reconstruction_schema_hash_provenance": schema,
        "falsifiers": [],
        "theorem": res["theorem"],
        "key_results": {
            "states_per_bag": "<=2^(tau+2)",
            "runtime": "poly(N,|T|)*2^O(tau)",
            "large_block_star": "tau=1 while BA24 kappa=lambda+1",
            "BA23_killer": "tau=2 and #SAT=3^m-2^m",
            "arbitrary_CNF_embedding": "SAT/#SAT exact",
            "incidence_treewidth": "tau_embedding=max(1,tw(H_F)) under frozen convention",
        },
        "nonclaims": {
            "arbitrary_foreign_CNF_BA4_carrier_coverage": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "P_equals_NP_proved": False,
            "P_not_equals_NP_proved": False,
        },
        "STOP": {
            "BA25": "UNSEALED_PENDING_NEW_AUTHORITATIVE_WORKFLOW_V2",
            "BA26_started": False,
            "next_permitted_object": "AUTHORITATIVE_WORKFLOW_V2",
            "external_literature_novelty_equivalence_audit_required_after_successful_BA25_seal": True,
            "general_sat_gap_map_required_after_external_audit": True,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
