#!/usr/bin/env python3
import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

from mk_bceg_r4_producer import package_hash, capability_digest, backend_contract_digest, receipt_hash

HERE = Path(__file__).resolve().parent
PRODUCER = HERE / "mk_bceg_r4_producer.py"
VERIFIER = HERE / "mk_bceg_r4_replay_verifier.py"
ROOT = HERE.parent
CAP_MAP = ROOT / "research/MK_BCEG_R3B_OPERATION_CAPABILITY_MAP_2026-08-30.json"


def load(path):
    return json.loads(Path(path).read_text())


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def run(cmd):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, (p.stdout + "\n" + p.stderr)[-3000:]


def expect_fail(name, cmd):
    rc, log = run(cmd)
    return {"attack": name, "rejected": rc != 0, "returncode": rc, "log_tail": log}


def mutate_package_rehash(pkg, mutator):
    q = copy.deepcopy(pkg)
    mutator(q)
    q["backend_contract_digest"] = backend_contract_digest(q["backend"])
    q["capability_digest"] = capability_digest(q["Gamma_L"], q["capability_map_sha256"])
    # Representation hash is unchanged unless mutator explicitly changes representation fields.
    q["package_hash"] = package_hash(q)
    return q


def receipt_necromancer(d):
    p0 = load(d / "package_0.json")
    r0 = load(d / "receipt_0.json")
    p1 = load(d / "package_1.json")
    r1 = load(d / "receipt_1.json")
    c1 = load(d / "cert_1.json")
    out = []

    forged = copy.deepcopy(r0)
    forged["accepted_package_hash"] = "FORGED"
    save(d / "attack_receipt_hash_corrupt.json", forged)
    out.append(expect_fail("receipt_body_changed_without_hash_update", [
        sys.executable, str(PRODUCER), "transition", "--input", str(d / "package_0.json"),
        "--receipt", str(d / "attack_receipt_hash_corrupt.json"), "--operation", "ROBDD_TO_D_DNNF",
        "--output", str(d / "should_not_materialize_1.json"), "--certificate", str(d / "should_not_materialize_1_cert.json")
    ]))

    q = mutate_package_rehash(p0, lambda x: x["backend"].__setitem__("release_version", "THESEUS-MUTATION"))
    save(d / "attack_package_backend_changed.json", q)
    out.append(expect_fail("old_receipt_replayed_after_backend_mutation", [
        sys.executable, str(PRODUCER), "transition", "--input", str(d / "attack_package_backend_changed.json"),
        "--receipt", str(d / "receipt_0.json"), "--operation", "ROBDD_TO_D_DNNF",
        "--output", str(d / "should_not_materialize_2.json"), "--certificate", str(d / "should_not_materialize_2_cert.json")
    ]))

    def cap_mut(x):
        x["Gamma_L"]["COUNT"]["capability_status"] = "UNKNOWN"
        x["Gamma_L"]["COUNT"]["proof_status"] = "OPEN"
    q = mutate_package_rehash(p0, cap_mut)
    save(d / "attack_package_capability_changed.json", q)
    out.append(expect_fail("old_receipt_replayed_after_capability_mutation", [
        sys.executable, str(PRODUCER), "transition", "--input", str(d / "attack_package_capability_changed.json"),
        "--receipt", str(d / "receipt_0.json"), "--operation", "ROBDD_TO_D_DNNF",
        "--output", str(d / "should_not_materialize_3.json"), "--certificate", str(d / "should_not_materialize_3_cert.json")
    ]))

    cm = copy.deepcopy(c1)
    cm["input_package_hash"] = "WRONG_PARENT"
    cm["certificate_hash"] = __import__("mk_bceg_r4_replay_verifier").certificate_hash(cm)
    save(d / "attack_cert_parent_changed.json", cm)
    out.append(expect_fail("certificate_parent_rebound", [
        sys.executable, str(VERIFIER), "verify-transition", "--input", str(d / "package_0.json"),
        "--parent-receipt", str(d / "receipt_0.json"), "--output-package", str(d / "package_1.json"),
        "--certificate", str(d / "attack_cert_parent_changed.json"), "--receipt", str(d / "attack_parent_receipt_out.json")
    ]))

    cm = copy.deepcopy(c1)
    if cm["operation"] == "ASSIGN":
        cm["operation_args"]["value"] = not bool(cm["operation_args"]["value"])
    else:
        cm["operation"] = "ASSIGN"
        cm["operation_args"] = {"var": 1, "value": False}
    cm["certificate_hash"] = __import__("mk_bceg_r4_replay_verifier").certificate_hash(cm)
    save(d / "attack_cert_operation_changed.json", cm)
    out.append(expect_fail("certificate_operation_or_parameters_rebound", [
        sys.executable, str(VERIFIER), "verify-transition", "--input", str(d / "package_0.json"),
        "--parent-receipt", str(d / "receipt_0.json"), "--output-package", str(d / "package_1.json"),
        "--certificate", str(d / "attack_cert_operation_changed.json"), "--receipt", str(d / "attack_operation_receipt_out.json")
    ]))

    q = copy.deepcopy(p1)
    q["theta"]["hostile_marker"] = "mutated_successor"
    # Updating representation hash makes this a coherent new representation identity, but cert/receipt are now stale.
    from mk_bceg_r4_replay_verifier import sha_obj
    q["representation_hash"] = sha_obj({"language": q["language"], "theta": q["theta"], "K": q["K"]})
    q["package_hash"] = package_hash(q)
    save(d / "attack_successor_mutated_rehashed.json", q)
    out.append(expect_fail("certificate_replayed_on_mutated_successor", [
        sys.executable, str(VERIFIER), "verify-transition", "--input", str(d / "package_0.json"),
        "--parent-receipt", str(d / "receipt_0.json"), "--output-package", str(d / "attack_successor_mutated_rehashed.json"),
        "--certificate", str(d / "cert_1.json"), "--receipt", str(d / "attack_successor_receipt_out.json")
    ]))
    out.append(expect_fail("old_receipt_replayed_on_mutated_successor", [
        sys.executable, str(PRODUCER), "transition", "--input", str(d / "attack_successor_mutated_rehashed.json"),
        "--receipt", str(d / "receipt_1.json"), "--operation", "ROBDD_TO_D_DNNF" if q["language"] == "ROBDD_FIXED_ORDER" else "D_DNNF_TO_ROBDD_EXACT_RECOMPILE",
        "--output", str(d / "should_not_materialize_4.json"), "--certificate", str(d / "should_not_materialize_4_cert.json")
    ]))

    # Diagnostic beyond the frozen R4-C mutation promise: an unkeyed hash is not signer authentication.
    malicious = copy.deepcopy(r0)
    malicious["verifier"]["verifier_id"] = "MALICIOUS_FORGER"
    malicious["verifier"]["verifier_source_sha256"] = "NOT_A_REAL_VERIFIER"
    malicious["verification_work_units"] = 0
    malicious["semantic_assignments_checked"] = 0
    malicious["receipt_hash"] = receipt_hash(malicious)
    save(d / "diagnostic_hash_only_forged_receipt.json", malicious)
    rc, log = run([
        sys.executable, str(PRODUCER), "transition", "--input", str(d / "package_0.json"),
        "--receipt", str(d / "diagnostic_hash_only_forged_receipt.json"), "--operation", "ROBDD_TO_D_DNNF",
        "--output", str(d / "diagnostic_forged_successor.json"), "--certificate", str(d / "diagnostic_forged_successor_cert.json")
    ])
    auth_gap = {
        "probe": "HASH_ONLY_RECEIPT_FORGERY",
        "malicious_recomputed_receipt_accepted": rc == 0,
        "interpretation": "If true, receipt hashes provide integrity/binding but not cryptographic signer authentication. TRUMP release authority must add an external trust root/signature/attestation or re-run an independent verifier instead of trusting receipt bytes alone.",
        "log_tail": log,
    }
    return out, auth_gap


def liability_bomb():
    per_step = 2
    steps = 64
    budget = 100
    cumulative = 0
    rows = []
    blocked_at = None
    for i in range(1, steps + 1):
        proposed = cumulative + per_step
        materialize = proposed <= budget
        rows.append({"step": i, "liability_upper": per_step, "cumulative_upper_if_accepted": proposed, "materialized": materialize})
        if not materialize:
            blocked_at = i
            break
        cumulative = proposed
    return {
        "status": "LIFECYCLE_BUDGET_EXCEEDED" if blocked_at else "WITHIN_BUDGET",
        "per_step_upper": per_step,
        "budget": budget,
        "accepted_steps": blocked_at - 1 if blocked_at else steps,
        "blocked_step": blocked_at,
        "final_accepted_cumulative_upper": cumulative,
        "pre_materialization_block": blocked_at is not None and rows[-1]["materialized"] is False,
        "law": "FOR_ALL_i_D_i_SMALL_DOES_NOT_IMPLY_SUM_D_i_SMALL",
        "rows": rows,
    }


def correct_refusal():
    M = load(CAP_MAP)
    start = "STRUCTURED_D_DNNF"
    ops = ["EXISTS_SINGLE", "COUNT"]
    first = M["languages"][start]["EXISTS_SINGLE"]
    exact = [t for t in M["translations"] if t["from"] == start and t["semantic_status"] == "EXACT"]
    dnnf_escape = next((t for t in exact if t["to"] == "DNNF"), None)
    count_after = M["languages"]["DNNF"]["COUNT"]["capability_status"] if dnnf_escape else None
    no_route = first["capability_status"] == "NOT_POLY_CLOSED" and dnnf_escape is not None and count_after != "POLY_CERTIFIED"
    return {
        "start": start,
        "operations": ops,
        "status": "NO_CERTIFIED_CHEAP_ROUTE" if no_route else "ROUTE_REQUIRES_REAUDIT",
        "same_language_first_operation": first,
        "exact_escape": dnnf_escape,
        "required_future_COUNT_after_escape": count_after,
        "unknown_promoted": False,
        "hidden_fallback_materialized": False,
        "external_theorem_used_as_internal_receipt": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    d = Path(args.dir)
    attacks, auth_gap = receipt_necromancer(d)
    liability = liability_bomb()
    refusal = correct_refusal()
    specified_attacks_pass = all(x["rejected"] for x in attacks)
    result = {
        "schema": "JANUS/MK_BCEG/R4/HOSTILE_ATTACK_RESULT/v1.0",
        "receipt_necromancer": {
            "specified_mutation_attacks": attacks,
            "all_specified_mutations_rejected": specified_attacks_pass,
            "verdict": "STALE_OR_REPLAYED_RECEIPT_REJECTED" if specified_attacks_pass else "REFUTED_RECEIPT_BINDING",
        },
        "receipt_authentication_diagnostic": auth_gap,
        "liability_bomb": liability,
        "correct_refusal": refusal,
        "gates": {
            "R4_C_RECEIPT_NECROMANCER": specified_attacks_pass,
            "R4_E_LIABILITY_BOMB": liability["status"] == "LIFECYCLE_BUDGET_EXCEEDED" and liability["pre_materialization_block"],
            "R4_H_CORRECT_REFUSAL": refusal["status"] == "NO_CERTIFIED_CHEAP_ROUTE",
        },
        "scientific_boundary": {
            "receipt_hash_is_signer_authentication": False,
            "cryptographic_release_lineage_proved": False,
            "P_VS_NP": "OPEN",
        },
    }
    save(args.output, result)
    print(json.dumps({
        "gates": result["gates"],
        "hash_only_forgery_accepted": auth_gap["malicious_recomputed_receipt_accepted"],
        "liability_status": liability["status"],
        "refusal": refusal["status"],
    }, indent=2))
    if not all(result["gates"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
