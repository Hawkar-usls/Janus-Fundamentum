from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

PRE = Path("research/JANUS_TRUMP_R50G25BA25_PREREGISTRATION.json")
RES = Path("ba25_result.json")
VER1 = Path("ba25_verify.json")
VER3 = Path("ba25_verify_v3.json")
GAP = Path("research/JANUS_TRUMP_R50G25BA25_SOURCE_RECONSTRUCTION_EVIDENCE_GAP_RECEIPT.json")
HARD = Path("research/JANUS_TRUMP_R50G25BA25_RECONSTRUCTION_HARDENING.json")
FAILURE_RECEIPT = Path("research/JANUS_TRUMP_R50G25BA25_AUTHORITATIVE_V2_RUN1_FAILURE_RECEIPT.json")
VERIFY_V3_FILE = Path("research/verify_janus_trump_r50g25ba25_v3.py")
OUT = Path("ba25_completion_v3.json")

PREREG_COMMIT = "466e839107f224cdf6ea7ec5294eef8bd9003cd6"
V1_IMPLEMENTATION_COMMIT = "1b7f9be5dd94f346a6ba4102ab6900f541b5c14e"
V1_VERIFIER_COMMIT = "a7caa09fabab4cbfc1dcb9a7bdb5e260010cc2f5"
V1_PRESEAL_COMMIT = "d208790d54b897d79cc12de50a5ac91da9441cbf"
V1_WORKFLOW_COMMIT = "2060789ebd89dd0aa75f3901802d4c30a0d61a30"
GAP_COMMIT = "a9eb4a65d0fa9c57fc70603ba63037f57ed479cf"
GAP_BLOB = "8596960a0df33f7361303b94042468d7086ea16e"
HARDENING_COMMIT = "1ca79fa8078e0428cae669d47df72354e59f06c2"
HARDENING_BLOB = "f3f4f8da6240ca061c3085726d9ada1bfe6823df"
VERIFY_V2_COMMIT = "57649038bd8b35e74464c878c0c15f81f3ff8ad1"
VERIFY_V2_BLOB = "a54c2d8a141ff386650793e34104ace1c34409a2"
PRESEAL_V2_COMMIT = "bf5a2de761caf664a3eca8ba3059e382b1d011ba"
PRESEAL_V2_BLOB = "9bf212bf71aee5e868c866f111a825b85baa0064"
AUTHORITATIVE_V2_WORKFLOW_HEAD = "dceda2c5d7302730da6133aeab5380833ca5c9a9"
AUTHORITATIVE_V2_WORKFLOW_BLOB = "ea3869e88241630529b3dc37345324282fb4cb88"
AUTHORITATIVE_V2_RUN1 = 34424706518
AUTHORITATIVE_V2_JOB1 = 102707349222
FAILURE_RECEIPT_COMMIT = "0a35e4e8b9f6b76bd071ca13e27c3e68b856b1fe"
FAILURE_RECEIPT_BLOB = "3bec4cc4ac40929d5664f606330c286732ca59af"
VERIFY_V3_COMMIT = "2b5bbc47e75b8499ea684c96d1425af2121bb3b3"
VERIFY_V3_BLOB = "113e0c57a3137cbe3450984a0beb80f25d1ea3e6"
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

REQUIRED_NEGATIVE_FIREWALLS = {
    "implementation_imported",
    "arbitrary_foreign_CNF_BA4_carrier_coverage_claimed",
    "BA26_STARTED",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def is_ancestor(a: str, b: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", a, b],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def exact_lineage_chain() -> tuple[bool, list[str]]:
    chain = [
        PREREG_COMMIT,
        V1_IMPLEMENTATION_COMMIT,
        V1_VERIFIER_COMMIT,
        V1_PRESEAL_COMMIT,
        V1_WORKFLOW_COMMIT,
        GAP_COMMIT,
        HARDENING_COMMIT,
        VERIFY_V2_COMMIT,
        PRESEAL_V2_COMMIT,
        AUTHORITATIVE_V2_WORKFLOW_HEAD,
        FAILURE_RECEIPT_COMMIT,
        VERIFY_V3_COMMIT,
    ]
    return all(is_ancestor(a, b) for a, b in zip(chain, chain[1:])), chain


def main() -> None:
    pre = json.loads(PRE.read_text())
    res = json.loads(RES.read_text())
    ver1 = json.loads(VER1.read_text())
    ver3 = json.loads(VER3.read_text())
    gap = json.loads(GAP.read_text())
    hard = json.loads(HARD.read_text())
    failure_receipt = json.loads(FAILURE_RECEIPT.read_text())
    names = pre["required_passes"]

    positive = ver3.get("positive_obligations", {})
    negative = ver3.get("negative_firewalls", {})
    failed_positive = ver3.get("failed_positive_obligations", None)
    violated_negative = ver3.get("violated_negative_firewalls", None)
    self_test = ver3.get("polarity_self_test", {})
    schema = ver3.get("reconstruction_schema_hash_provenance", {})

    expected_schema = {
        "BA20_final_meta": {"commit": BA20_FINAL_META_COMMIT, "blob": BA20_FINAL_META_BLOB},
        "BA20_result_receipt": {"commit": BA20_RECEIPT_COMMIT, "blob": BA20_RECEIPT_BLOB},
        "BA20_base_reconstruction": {"commit": BA20_BASE_COMMIT, "blob": BA20_BASE_BLOB},
        "BA20_authoritative_v2_wrapper": {"commit": BA20_V2_COMMIT, "blob": BA20_V2_BLOB},
        "BA4_carrier_schema": {"blob": BA4_SCHEMA_BLOB},
        "BA21_final_meta": {"commit": BA21_FINAL_META_COMMIT, "blob": BA21_FINAL_META_BLOB},
        "BA21_result_receipt": {"commit": BA21_RECEIPT_COMMIT, "blob": BA21_RECEIPT_BLOB},
        "BA21_compressed_projection_impl": {"commit": BA21_IMPL_COMMIT, "blob": BA21_IMPL_BLOB},
        "reconstruction_hardening": {"commit": HARDENING_COMMIT, "blob": HARDENING_BLOB},
        "verifier_v2_parent": {"commit": VERIFY_V2_COMMIT, "blob": VERIFY_V2_BLOB},
        "authoritative_v2_run1_failure_receipt": {"commit": FAILURE_RECEIPT_COMMIT, "blob": FAILURE_RECEIPT_BLOB},
    }
    expected_schema_with_hash = dict(expected_schema)
    expected_schema_with_hash["schema_sha256"] = sha256_json(expected_schema)

    lineage_ok, lineage_chain = exact_lineage_chain()

    all_positive_true = bool(positive) and all(value is True for value in positive.values())
    all_negative_false = bool(negative) and all(value is False for value in negative.values())
    required_negative_present = REQUIRED_NEGATIVE_FIREWALLS.issubset(set(negative))

    local_ok = positive.get("LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS") is True
    sealed_ok = positive.get("SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS") is True
    direct_ok = positive.get("DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES") is True
    strict_source = bool(local_ok and sealed_ok and direct_ok)

    checks = {
        "prereg_frozen": pre.get("state") == "FROZEN_BEFORE_IMPLEMENTATION",
        "exact_34_names": (
            len(names) == 34
            and len(set(names)) == 34
            and set(res.get("pass_map", {})) == set(names)
        ),
        "append_only_lineage_exact_order": lineage_ok,
        "historical_run_34410959446_never_promoted": (
            gap.get("historical_green_run", {}).get("run_id") == OLD_RUN
            and gap.get("historical_green_run", {}).get("scientific_authority") is False
            and gap.get("historical_green_run", {}).get("scientific_result") == "NOT_PROMOTED"
            and gap.get("historical_green_run", {}).get("must_never_be_retroactively_promoted_to_authoritative") is True
        ),
        "authoritative_v2_failure_preserved": (
            failure_receipt.get("authoritative_attempt", {}).get("run_id") == AUTHORITATIVE_V2_RUN1
            and failure_receipt.get("authoritative_attempt", {}).get("job_id") == AUTHORITATIVE_V2_JOB1
            and failure_receipt.get("authoritative_attempt", {}).get("workflow_head") == AUTHORITATIVE_V2_WORKFLOW_HEAD
            and failure_receipt.get("authoritative_attempt", {}).get("workflow_blob") == AUTHORITATIVE_V2_WORKFLOW_BLOB
            and failure_receipt.get("classification") == "VERIFIER_V2_BOOLEAN_FIREWALL_POLARITY_HARNESS_GAP"
            and failure_receipt.get("scientific_authority") is False
            and failure_receipt.get("scientific_result") == "NOT_PROMOTED"
            and failure_receipt.get("scientific_falsifier_observed") is False
        ),
        "append_only_object_blobs": (
            git_blob_sha(GAP) == GAP_BLOB
            and git_blob_sha(HARD) == HARDENING_BLOB
            and git_blob_sha(FAILURE_RECEIPT) == FAILURE_RECEIPT_BLOB
            and git_blob_sha(VERIFY_V3_FILE) == VERIFY_V3_BLOB
        ),
        "verifier_v3_commit_blob_pinned": (
            ver3.get("verifier_lineage", {}).get("verifier_v2_commit") == VERIFY_V2_COMMIT
            and ver3.get("verifier_lineage", {}).get("verifier_v2_blob") == VERIFY_V2_BLOB
            and git_blob_sha(VERIFY_V3_FILE) == VERIFY_V3_BLOB
        ),
        "builder_scope_except_hardened_source_and_final_two": (
            res.get("required") == 34
            and res.get("falsifiers") == []
            and all(
                res["pass_map"][n]
                for n in names
                if n not in {"SOURCE_RECONSTRUCTION_PASS", "INDEPENDENT_REPLAY_PASS", "PRESEAL_COMPLETENESS_PASS"}
            )
            and res["pass_map"]["INDEPENDENT_REPLAY_PASS"] is False
            and res["pass_map"]["PRESEAL_COMPLETENESS_PASS"] is False
        ),
        "legacy_theorem_verifier_v1_pass": (
            ver1.get("status") == "PASS"
            and ver1.get("implementation_imported") is False
            and ver1.get("falsifiers") == []
        ),
        "reconstruction_verifier_v3_pass": ver3.get("status") == "PASS",
        "polarity_self_test_pass": self_test.get("pass") is True,
        "failed_positive_obligations_empty": failed_positive == [],
        "violated_negative_firewalls_empty": violated_negative == [],
        "all_positive_obligations_exact_true": all_positive_true,
        "all_negative_firewalls_exact_false": all_negative_false,
        "required_negative_firewalls_present": required_negative_present,
        "negative_implementation_imported_false": negative.get("implementation_imported") is False,
        "negative_arbitrary_foreign_cnf_ba4_carrier_false": negative.get("arbitrary_foreign_CNF_BA4_carrier_coverage_claimed") is False,
        "negative_ba26_started_false": negative.get("BA26_STARTED") is False,
        "runtime_sealed_parent_replay_true": ver3.get("sealed_parent_reconstruction_replay") is True,
        "runtime_source_reconstruction_pass_true": ver3.get("SOURCE_RECONSTRUCTION_PASS") is True,
        "runtime_replayed_cases_gt_zero": int(ver3.get("number_of_replayed_cases", 0)) > 0,
        "runtime_original_cnf_zero_failures": int(ver3.get("original_CNF_validation_failures", -1)) == 0,
        "runtime_parent_formula_zero_mismatches": int(ver3.get("parent_reconstruction_formula_mismatches", -1)) == 0,
        "runtime_abstract_source_zero_failures": int(ver3.get("abstract_source_validation_failures", -1)) == 0,
        "exact_parent_meta_commits": (
            ver3.get("parent_BA20_commit") == BA20_FINAL_META_COMMIT
            and ver3.get("parent_BA21_commit") == BA21_FINAL_META_COMMIT
        ),
        "exact_parent_commit_blob_receipt_schema": schema == expected_schema_with_hash,
        "source_component_local": local_ok,
        "source_component_sealed_replay": sealed_ok,
        "source_component_direct_original_ba4": direct_ok,
        "source_reconstruction_exact_formula": (
            ver3.get("SOURCE_RECONSTRUCTION_PASS_definition") == SOURCE_DEF
            and ver3.get("SOURCE_RECONSTRUCTION_PASS") is strict_source
            and positive.get("SOURCE_RECONSTRUCTION_PASS") is strict_source
            and hard.get("SOURCE_RECONSTRUCTION_PASS_definition", {}).get("no_synthesis_from_overall_verifier_pass") is True
        ),
        "source_reconstruction_pass": strict_source,
        "truth_firewall": (
            ver3.get("nonclaims", {}).get("SAT_IN_P") == "NOT_PROVED"
            and ver3.get("nonclaims", {}).get("P_VS_NP") == "OPEN"
            and res.get("theorem", {}).get("SAT_IN_P") == "NOT_PROVED"
            and res.get("theorem", {}).get("P_VS_NP") == "OPEN"
        ),
        "stop_before_ba26": (
            ver3.get("STOP", {}).get("BA26_started") is False
            and res.get("STOP", {}).get("BA26_started") is False
            and res.get("STOP", {}).get("next_theorem_gate_started") is False
            and res.get("STOP", {}).get("external_literature_novelty_equivalence_audit_required") is True
        ),
    }

    independent_pass = bool(
        checks["legacy_theorem_verifier_v1_pass"]
        and checks["reconstruction_verifier_v3_pass"]
        and checks["polarity_self_test_pass"]
        and checks["failed_positive_obligations_empty"]
        and checks["violated_negative_firewalls_empty"]
        and checks["all_positive_obligations_exact_true"]
        and checks["all_negative_firewalls_exact_false"]
    )

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

    preseal_ready = bool(
        all(checks.values())
        and all(pass_map[n] for n in names if n != "PRESEAL_COMPLETENESS_PASS")
    )
    pass_map["PRESEAL_COMPLETENESS_PASS"] = preseal_ready
    all_pass = bool(all(checks.values()) and all(pass_map.values()))

    common = {
        "gate": pre.get("gate"),
        "entry_type": "BA25_PRESEAL_V3_EXPECTED_POLARITY_AND_SOURCE_RECONSTRUCTION_HARDENED",
        "scientific_authority": False,
        "verifier_v3": {"commit": VERIFY_V3_COMMIT, "blob": VERIFY_V3_BLOB},
        "lineage": {
            "ordered_commits_through_verifier_v3": lineage_chain,
            "historical_v1_workflow": V1_WORKFLOW_COMMIT,
            "gap_receipt": GAP_COMMIT,
            "reconstruction_hardening": HARDENING_COMMIT,
            "verifier_v2": VERIFY_V2_COMMIT,
            "preseal_v2": PRESEAL_V2_COMMIT,
            "authoritative_v2_failed_workflow_head": AUTHORITATIVE_V2_WORKFLOW_HEAD,
            "authoritative_v2_failed_run": AUTHORITATIVE_V2_RUN1,
            "authoritative_v2_failed_job": AUTHORITATIVE_V2_JOB1,
            "failure_receipt": FAILURE_RECEIPT_COMMIT,
            "verifier_v3": VERIFY_V3_COMMIT,
        },
        "checks": checks,
        "required_passes": names,
        "pass_map": pass_map,
        "passes": sum(bool(x) for x in pass_map.values()),
        "required": 34,
        "SOURCE_RECONSTRUCTION_PASS": strict_source,
        "SOURCE_RECONSTRUCTION_PASS_definition": SOURCE_DEF,
        "sealed_parent_reconstruction_replay": ver3.get("sealed_parent_reconstruction_replay") is True,
        "number_of_replayed_cases": int(ver3.get("number_of_replayed_cases", 0)),
        "original_CNF_validation_failures": int(ver3.get("original_CNF_validation_failures", -1)),
        "parent_reconstruction_formula_mismatches": int(ver3.get("parent_reconstruction_formula_mismatches", -1)),
        "abstract_source_validation_failures": int(ver3.get("abstract_source_validation_failures", -1)),
        "positive_obligations": positive,
        "negative_firewalls": negative,
        "failed_positive_obligations": failed_positive,
        "violated_negative_firewalls": violated_negative,
        "polarity_self_test": self_test,
        "reconstruction_schema_hash_provenance": schema,
        "historical_run_34410959446": "HISTORICAL_UNSEALED_NOT_PROMOTED",
        "authoritative_v2_run_34424706518": "PERMANENTLY_FAILED_UNSEALED_NOT_PROMOTED",
        "nonclaims": {
            "arbitrary_foreign_CNF_BA4_carrier_coverage": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "P_equals_NP_proved": False,
            "P_not_equals_NP_proved": False,
        },
        "STOP": {
            "BA25": "UNSEALED",
            "BA26_started": False,
            "workflow_v3_created_in_this_step": False,
            "external_literature_novelty_equivalence_audit_required_after_successful_BA25_seal": True,
            "general_sat_gap_map_required_after_successful_BA25_seal": True,
        },
    }

    if not all_pass:
        out = dict(common)
        out.update({
            "status": "FAIL",
            "P_BA25_FINAL": 0,
            "P_BA25_FINAL_authority": "NONE",
            "falsifiers": [k for k, v in checks.items() if not v] + [n for n, v in pass_map.items() if not v],
            "STOP": {
                **common["STOP"],
                "next_permitted_object": "FIX_OR_HARDEN_ONLY_THE_EXACT_FAILED_PRESEAL_V3_OBLIGATION_BEFORE_ANY_WORKFLOW_V3",
            },
        })
        OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps(out, indent=2, sort_keys=True))
        raise SystemExit(1)

    out = dict(common)
    out.update({
        "status": "PRESEAL_V3_PASS_PENDING_NEW_AUTHORITATIVE_WORKFLOW_V3",
        "passes": 34,
        "required": 34,
        "P_BA25_FINAL": 1,
        "P_BA25_FINAL_authority": "CANDIDATE_ONLY_UNTIL_NEW_AUTHORITATIVE_WORKFLOW_V3_RUN",
        "independent_replay": "PASS",
        "preseal_completeness": "PASS",
        "falsifiers": [],
        "theorem": res.get("theorem", {}),
        "STOP": {
            **common["STOP"],
            "BA25": "UNSEALED_PENDING_NEW_AUTHORITATIVE_WORKFLOW_V3",
            "next_permitted_object": "AUTHORITATIVE_WORKFLOW_V3_IN_A_SEPARATE_STEP",
        },
    })
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
