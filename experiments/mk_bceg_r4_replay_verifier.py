#!/usr/bin/env python3
import argparse
import hashlib
import json
import platform
from pathlib import Path

CANON_PROFILE = "JANUS_CANON_JSON_V1"


def canon_obj(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_obj(x):
    return hashlib.sha256(canon_obj(x)).hexdigest()


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def no_floats(x):
    if isinstance(x, float):
        return False
    if isinstance(x, dict):
        return all(no_floats(k) and no_floats(v) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return all(no_floats(v) for v in x)
    return True


def canon_cnf(cs):
    out = []
    for c in cs:
        s = set(int(x) for x in c)
        if any(-x in s for x in s):
            continue
        out.append(tuple(sorted(s, key=lambda z: (abs(z), z < 0))))
    out = sorted(set(out), key=lambda c: (len(c), c))
    if any(not c for c in out):
        return ((),)
    keep, seen = [], []
    for c in out:
        q = set(c)
        if any(x.issubset(q) for x in seen):
            continue
        keep.append(c)
        seen.append(q)
    return tuple(keep)


def restrict_cnf(f, var, value):
    f = canon_cnf(f)
    if f in ((), ((),)):
        return f
    lit = var if value else -var
    res = []
    for c in f:
        if lit in c:
            continue
        if -lit in c:
            d = tuple(x for x in c if x != -lit)
            if not d:
                return ((),)
            res.append(d)
        else:
            res.append(c)
    return canon_cnf(res)


def eval_cnf(f, assignment):
    f = canon_cnf(f)
    if f == ((),):
        return False
    if f == ():
        return True
    for clause in f:
        if not any((lit > 0 and bool(assignment[abs(lit)])) or (lit < 0 and not bool(assignment[abs(lit)])) for lit in clause):
            return False
    return True


def eval_obdd(K, assignment):
    nodes = K["nodes"]
    i = int(K["root"])
    seen = set()
    while i not in (0, 1):
        if i in seen:
            raise ValueError("ROBDD cycle detected")
        seen.add(i)
        v, lo, hi = nodes[str(i)]
        i = int(hi if assignment[int(v)] else lo)
    return i == 1


def eval_ddnnf(K, assignment):
    nodes = K["nodes"]
    memo = {}
    visiting = set()
    def rec(i):
        i = int(i)
        if i in memo:
            return memo[i]
        if i in visiting:
            raise ValueError("D_DNNF cycle detected")
        visiting.add(i)
        node = nodes[str(i)]
        t = node[0]
        if t == "CONST":
            out = bool(node[1])
        elif t == "LIT":
            v = bool(assignment[int(node[1])])
            out = v if bool(node[2]) else not v
        elif t == "AND":
            out = rec(node[1]) and rec(node[2])
        elif t == "OR":
            out = rec(node[1]) or rec(node[2])
        else:
            raise ValueError(f"Unknown D_DNNF node type: {t}")
        visiting.remove(i)
        memo[i] = out
        return out
    return rec(K["root"])


def enumerate_assignments(active_vars):
    active_vars = [int(v) for v in active_vars]
    for mask in range(1 << len(active_vars)):
        yield {v: bool((mask >> i) & 1) for i, v in enumerate(active_vars)}


def package_hash(pkg):
    body = dict(pkg)
    body.pop("package_hash", None)
    return sha_obj(body)


def receipt_hash(receipt):
    body = dict(receipt)
    body.pop("receipt_hash", None)
    return sha_obj(body)


def certificate_hash(cert):
    body = dict(cert)
    body.pop("certificate_hash", None)
    return sha_obj(body)


def representation_hash(pkg):
    return sha_obj({"language": pkg["language"], "theta": pkg["theta"], "K": pkg["K"]})


def semantic_hash(sem):
    return sha_obj({
        "cnf": sem["cnf"],
        "active_vars": sem["active_vars"],
        "frozen_assignments": sem.get("frozen_assignments", {}),
    })


def capability_digest(pkg):
    return sha_obj({"Gamma_L": pkg["Gamma_L"], "capability_map_sha256": pkg["capability_map_sha256"]})


def backend_contract_digest(pkg):
    return sha_obj(pkg["backend"])


def verifier_identity(release_version):
    return {
        "verifier_id": "MK_BCEG_R4_INDEPENDENT_PORTABILITY_VERIFIER",
        "verifier_schema_version": "1.0",
        "release_version": str(release_version),
        "python_version": platform.python_version(),
        "os": platform.system(),
        "machine": platform.machine(),
        "verifier_source_sha256": sha_file(__file__),
        "imports_producer_code": False,
        "hidden_mutable_state_required": False,
    }


def verify_package_data(pkg):
    failures = []
    work = 0
    required = [
        "schema", "canonicalization_profile", "step", "language", "theta", "K", "semantics_ref",
        "Gamma_L", "capability_map_sha256", "capability_digest", "backend", "backend_contract_digest",
        "paid_costs", "debt_ledger", "liability_potential", "provenance", "authority_lineage",
        "language_theorem_status", "backend_empirical_status", "representation_hash", "package_hash",
    ]
    for key in required:
        work += 1
        if key not in pkg:
            failures.append(f"missing:{key}")
    if failures:
        return failures, work, 0, 0
    work += 1
    if pkg["schema"] != "JANUS/MK_BCEG/R4/PROOF_STATE_PASSPORT/v1.0":
        failures.append("schema_mismatch")
    work += 1
    if pkg["canonicalization_profile"] != CANON_PROFILE:
        failures.append("canonicalization_profile_mismatch")
    work += 1
    if not no_floats(pkg):
        failures.append("floating_point_payload_forbidden")
    work += 1
    if pkg["package_hash"] != package_hash(pkg):
        failures.append("package_hash_mismatch")
    work += 1
    if pkg["representation_hash"] != representation_hash(pkg):
        failures.append("representation_hash_mismatch")
    work += 1
    if pkg["semantics_ref"]["semantic_hash"] != semantic_hash(pkg["semantics_ref"]):
        failures.append("semantic_hash_mismatch")
    work += 1
    if pkg["capability_digest"] != capability_digest(pkg):
        failures.append("capability_digest_mismatch")
    work += 1
    if pkg["backend_contract_digest"] != backend_contract_digest(pkg):
        failures.append("backend_contract_digest_mismatch")
    work += 1
    if pkg["status"] != "PENDING_INDEPENDENT_REPLAY":
        failures.append("unexpected_package_status")
    work += 1
    if pkg["provenance"].get("exact_fallback_embedded") is not True:
        failures.append("exact_fallback_not_embedded")
    work += 1
    if pkg["liability_potential"].get("Phi") != 1:
        failures.append("pending_package_phi_must_equal_1")
    work += 1
    if pkg["language_theorem_status"] == pkg["backend_empirical_status"]:
        failures.append("theorem_empirical_status_conflated")
    work += 1
    if pkg["authority_lineage"].get("law") != "AUTHORITY_IS_TRANSITIVE_ONLY_THROUGH_VERIFIED_TRANSITIONS":
        failures.append("authority_law_missing")
    sem = pkg["semantics_ref"]
    active = [int(v) for v in sem["active_vars"]]
    cnf = canon_cnf(sem["cnf"])
    checked = 0
    mismatches = 0
    for assignment in enumerate_assignments(active):
        checked += 1
        work += 1
        expected = eval_cnf(cnf, assignment)
        try:
            if pkg["language"] == "ROBDD_FIXED_ORDER":
                actual = eval_obdd(pkg["K"], assignment)
            elif pkg["language"] == "D_DNNF":
                actual = eval_ddnnf(pkg["K"], assignment)
            else:
                failures.append(f"unsupported_language:{pkg['language']}")
                break
        except Exception as exc:
            failures.append(f"representation_eval_error:{type(exc).__name__}:{exc}")
            break
        if actual != expected:
            mismatches += 1
            if mismatches <= 8:
                failures.append(f"semantic_mismatch:{assignment}:{expected}:{actual}")
    return failures, work, checked, mismatches


def verify_stored_receipt(pkg, receipt):
    failures = []
    if receipt.get("receipt_hash") != receipt_hash(receipt):
        failures.append("receipt_hash_mismatch")
    if receipt.get("verdict") != "PASS":
        failures.append("receipt_not_pass")
    if receipt.get("accepted_package_hash") != pkg.get("package_hash"):
        failures.append("receipt_package_binding_mismatch")
    if receipt.get("accepted_capability_digest") != pkg.get("capability_digest"):
        failures.append("receipt_capability_binding_mismatch")
    if receipt.get("accepted_backend_contract_digest") != pkg.get("backend_contract_digest"):
        failures.append("receipt_backend_binding_mismatch")
    if receipt.get("accepted_phi") != 0:
        failures.append("receipt_phi_not_zero")
    if int(pkg.get("step", 0)) > 0:
        b = receipt.get("transition_binding") or {}
        if b.get("successor_package_hash") != pkg.get("package_hash"):
            failures.append("receipt_successor_binding_mismatch")
        if b.get("capability_digest") != pkg.get("capability_digest"):
            failures.append("receipt_transition_capability_mismatch")
        if b.get("backend_contract_digest") != pkg.get("backend_contract_digest"):
            failures.append("receipt_transition_backend_mismatch")
    return failures


def verify_transition_data(src, parent_receipt, out, cert):
    failures = []
    work = 0
    prf = verify_stored_receipt(src, parent_receipt)
    failures.extend(f"parent:{x}" for x in prf)
    work += 6 + len(prf)
    work += 1
    if cert.get("certificate_hash") != certificate_hash(cert):
        failures.append("certificate_hash_mismatch")
    checks = [
        ("input_package_hash", src.get("package_hash")),
        ("input_representation_hash", src.get("representation_hash")),
        ("input_capability_digest", src.get("capability_digest")),
        ("input_backend_contract_digest", src.get("backend_contract_digest")),
        ("input_acceptance_receipt_hash", parent_receipt.get("receipt_hash")),
        ("output_package_hash", out.get("package_hash")),
        ("output_representation_hash", out.get("representation_hash")),
        ("output_capability_digest", out.get("capability_digest")),
        ("output_backend_contract_digest", out.get("backend_contract_digest")),
    ]
    for key, expected in checks:
        work += 1
        if cert.get(key) != expected:
            failures.append(f"certificate_{key}_mismatch")
    work += 1
    if out.get("provenance", {}).get("parent_package_hash") != src.get("package_hash"):
        failures.append("provenance_parent_mismatch")
    work += 1
    if out.get("provenance", {}).get("input_acceptance_receipt_hash") != parent_receipt.get("receipt_hash"):
        failures.append("provenance_receipt_mismatch")
    work += 1
    if out.get("authority_lineage", {}).get("parent_acceptance_receipt_hash") != parent_receipt.get("receipt_hash"):
        failures.append("lineage_receipt_mismatch")
    work += 1
    if out.get("authority_lineage", {}).get("parent_package_hash") != src.get("package_hash"):
        failures.append("lineage_parent_mismatch")
    work += 1
    if out.get("authority_lineage", {}).get("root_anchor_hash") != src.get("authority_lineage", {}).get("root_anchor_hash"):
        failures.append("lineage_root_changed")
    work += 1
    if out.get("authority_lineage", {}).get("lineage_depth") != src.get("authority_lineage", {}).get("lineage_depth") + 1:
        failures.append("lineage_depth_mismatch")
    work += 1
    if out.get("step") != src.get("step") + 1:
        failures.append("step_not_incremented")

    op = cert.get("operation")
    sin = src["semantics_ref"]
    sout = out["semantics_ref"]
    transition_checks = {"operation": op}
    if op == "ASSIGN":
        var = int(cert["operation_args"]["var"])
        value = bool(cert["operation_args"]["value"])
        expected_cnf = [list(c) for c in restrict_cnf(sin["cnf"], var, value)]
        expected_active = [int(v) for v in sin["active_vars"] if int(v) != var]
        expected_frozen = dict(sin.get("frozen_assignments", {}))
        expected_frozen[str(var)] = value
        work += 3
        if sout["cnf"] != expected_cnf:
            failures.append("assign_semantic_cnf_mismatch")
        if [int(v) for v in sout["active_vars"]] != expected_active:
            failures.append("assign_active_vars_mismatch")
        if sout.get("frozen_assignments", {}) != expected_frozen:
            failures.append("assign_frozen_assignment_mismatch")
        transition_checks.update({"var": var, "value": value, "semantic_restriction": "CHECKED_INDEPENDENTLY"})
    elif op == "ROBDD_TO_D_DNNF":
        work += 3
        if src["language"] != "ROBDD_FIXED_ORDER" or out["language"] != "D_DNNF":
            failures.append("translation_language_mismatch")
        if sout != sin:
            failures.append("translation_semantics_changed")
        if cert["operation_args"].get("producer_local_certificate_failures") != []:
            failures.append("producer_reported_local_certificate_failure")
        transition_checks["translation_semantics"] = "CHECKED_INDEPENDENTLY"
    elif op == "D_DNNF_TO_ROBDD_EXACT_RECOMPILE":
        work += 3
        if src["language"] != "D_DNNF" or out["language"] != "ROBDD_FIXED_ORDER":
            failures.append("recompile_language_mismatch")
        if sout != sin:
            failures.append("recompile_semantics_changed")
        if cert["operation_args"].get("direct_representation_translation") is not False:
            failures.append("fallback_recompile_kind_mismatch")
        transition_checks["fallback_recompile_semantics"] = "CHECKED_INDEPENDENTLY"
    else:
        failures.append(f"unknown_transition_operation:{op}")

    p_failures, p_work, checked, mismatches = verify_package_data(out)
    failures.extend(p_failures)
    work += p_work
    return failures, work, checked, mismatches, transition_checks


def make_receipt(pkg, failures, work, checked, mismatches, replay_kind, release_version,
                 parent_receipt=None, cert=None, transition_checks=None):
    verdict = "PASS" if not failures and mismatches == 0 else "FAIL"
    vid = verifier_identity(release_version)
    transition_binding = None
    if cert is not None:
        transition_binding = {
            "parent_package_hash": cert["input_package_hash"],
            "operation": cert["operation"],
            "parameters": cert["operation_args"],
            "successor_package_hash": cert["output_package_hash"],
            "capability_digest": pkg["capability_digest"],
            "backend_contract_digest": pkg["backend_contract_digest"],
            "certificate_hash": cert["certificate_hash"],
            "verifier_id": vid["verifier_id"],
            "verifier_schema_version": vid["verifier_schema_version"],
        }
    receipt = {
        "schema": "JANUS/MK_BCEG/R4/PORTABLE_REPLAY_RECEIPT/v1.0",
        "canonicalization_profile": CANON_PROFILE,
        "verdict": verdict,
        "replay_kind": replay_kind,
        "accepted_package_hash": pkg["package_hash"] if verdict == "PASS" else None,
        "accepted_capability_digest": pkg["capability_digest"] if verdict == "PASS" else None,
        "accepted_backend_contract_digest": pkg["backend_contract_digest"] if verdict == "PASS" else None,
        "accepted_phi": 0 if verdict == "PASS" else pkg["liability_potential"]["Phi"],
        "parent_acceptance_receipt_hash": parent_receipt.get("receipt_hash") if parent_receipt else None,
        "transition_binding": transition_binding,
        "verification_work_units": int(work),
        "semantic_assignments_checked": int(checked),
        "semantic_mismatches": int(mismatches),
        "transition_checks": transition_checks or {},
        "failures": failures,
        "backend_empirical_status_after_replay": "FINITE_REPLAY_PASS" if verdict == "PASS" else "FINITE_REPLAY_FAIL",
        "language_theorem_status_after_replay": pkg["language_theorem_status"],
        "liability_discharge": {"verification_liability": 1 if verdict == "PASS" else 0},
        "hidden_mutable_state_required": False,
        "replay_inputs": "serialized package plus certificate and parent receipt when applicable; no producer cache",
        "verifier": vid,
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    return receipt


def cmd_verify_package(args):
    pkg = read_json(args.package)
    failures, work, checked, mismatches = verify_package_data(pkg)
    receipt = make_receipt(pkg, failures, work, checked, mismatches, "PACKAGE_ACCEPTANCE", args.verifier_release)
    write_json(args.output, receipt)
    print(json.dumps({"verdict": receipt["verdict"], "work": work, "checked": checked, "mismatches": mismatches, "os": platform.system(), "canonical_package_hash": package_hash(pkg)}, indent=2))
    if receipt["verdict"] != "PASS":
        raise SystemExit(1)


def cmd_verify_transition(args):
    src = read_json(args.input)
    parent_receipt = read_json(args.parent_receipt)
    out = read_json(args.output_package)
    cert = read_json(args.certificate)
    failures, work, checked, mismatches, transition_checks = verify_transition_data(src, parent_receipt, out, cert)
    receipt = make_receipt(out, failures, work, checked, mismatches, "TRANSITION_ACCEPTANCE", args.verifier_release, parent_receipt=parent_receipt, cert=cert, transition_checks=transition_checks)
    write_json(args.receipt, receipt)
    print(json.dumps({"verdict": receipt["verdict"], "work": work, "checked": checked, "mismatches": mismatches, "operation": cert.get("operation"), "os": platform.system(), "canonical_package_hash": package_hash(out)}, indent=2))
    if receipt["verdict"] != "PASS":
        raise SystemExit(1)


def cmd_verify_chain(args):
    d = Path(args.dir)
    steps = int(args.steps)
    failures = []
    total_work = 0
    total_checked = 0
    hashes = []
    p0 = read_json(d / "package_0.json")
    r0 = read_json(d / "receipt_0.json")
    pf, pw, pc, pm = verify_package_data(p0)
    failures.extend(f"package_0:{x}" for x in pf)
    failures.extend(f"receipt_0:{x}" for x in verify_stored_receipt(p0, r0))
    total_work += pw
    total_checked += pc
    hashes.append(package_hash(p0))
    prev_pkg, prev_receipt = p0, r0
    for i in range(1, steps + 1):
        pkg = read_json(d / f"package_{i}.json")
        cert = read_json(d / f"cert_{i}.json")
        stored_receipt = read_json(d / f"receipt_{i}.json")
        tf, tw, tc, tm, _ = verify_transition_data(prev_pkg, prev_receipt, pkg, cert)
        failures.extend(f"transition_{i}:{x}" for x in tf)
        failures.extend(f"receipt_{i}:{x}" for x in verify_stored_receipt(pkg, stored_receipt))
        if stored_receipt.get("parent_acceptance_receipt_hash") != prev_receipt.get("receipt_hash"):
            failures.append(f"receipt_{i}:parent_receipt_chain_mismatch")
        b = stored_receipt.get("transition_binding") or {}
        expected = {
            "parent_package_hash": cert.get("input_package_hash"),
            "operation": cert.get("operation"),
            "parameters": cert.get("operation_args"),
            "successor_package_hash": cert.get("output_package_hash"),
            "capability_digest": pkg.get("capability_digest"),
            "backend_contract_digest": pkg.get("backend_contract_digest"),
            "certificate_hash": cert.get("certificate_hash"),
        }
        for k, v in expected.items():
            if b.get(k) != v:
                failures.append(f"receipt_{i}:transition_binding_{k}_mismatch")
        total_work += tw
        total_checked += tc
        hashes.append(package_hash(pkg))
        prev_pkg, prev_receipt = pkg, stored_receipt
    report = {
        "schema": "JANUS/MK_BCEG/R4/CROSS_MACHINE_CHAIN_REPLAY/v1.0",
        "verdict": "PASS" if not failures else "FAIL",
        "os": platform.system(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "verifier_release": args.verifier_release,
        "canonicalization_profile": CANON_PROFILE,
        "canonical_package_hashes": hashes,
        "steps": steps,
        "total_verification_work_units": total_work,
        "semantic_assignments_checked": total_checked,
        "failures": failures,
        "producer_cache_available": False,
        "producer_code_imported": False,
    }
    write_json(args.output, report)
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    vp = sub.add_parser("verify-package")
    vp.add_argument("--package", required=True)
    vp.add_argument("--output", required=True)
    vp.add_argument("--verifier-release", default="1.0")
    vp.set_defaults(fn=cmd_verify_package)
    vt = sub.add_parser("verify-transition")
    vt.add_argument("--input", required=True)
    vt.add_argument("--parent-receipt", required=True)
    vt.add_argument("--output-package", required=True)
    vt.add_argument("--certificate", required=True)
    vt.add_argument("--receipt", required=True)
    vt.add_argument("--verifier-release", default="1.0")
    vt.set_defaults(fn=cmd_verify_transition)
    vc = sub.add_parser("verify-chain")
    vc.add_argument("--dir", required=True)
    vc.add_argument("--steps", type=int, required=True)
    vc.add_argument("--output", required=True)
    vc.add_argument("--verifier-release", default="2.0")
    vc.set_defaults(fn=cmd_verify_chain)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
