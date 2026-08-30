#!/usr/bin/env python3
import argparse
import hashlib
import json
import platform
from pathlib import Path


def canon_obj(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_obj(x):
    return hashlib.sha256(canon_obj(x)).hexdigest()


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


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
        ok = False
        for lit in clause:
            v = bool(assignment[abs(lit)])
            if (lit > 0 and v) or (lit < 0 and not v):
                ok = True
                break
        if not ok:
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


def verifier_identity():
    return {
        "verifier_id": "MK_BCEG_R3C_INDEPENDENT_REPLAY_VERIFIER",
        "verifier_schema_version": "1.0",
        "python_version": platform.python_version(),
        "verifier_source_sha256": sha_file(__file__),
        "imports_producer_code": False
    }


def recompute_package_hash(pkg):
    body = dict(pkg)
    body.pop("package_hash", None)
    return sha_obj(body)


def recompute_representation_hash(pkg):
    return sha_obj({"language": pkg["language"], "theta": pkg["theta"], "K": pkg["K"]})


def expected_semantic_hash(sem):
    return sha_obj({
        "cnf": sem["cnf"],
        "active_vars": sem["active_vars"],
        "frozen_assignments": sem.get("frozen_assignments", {})
    })


def enumerate_assignments(active_vars):
    active_vars = list(active_vars)
    for mask in range(1 << len(active_vars)):
        yield {v: bool((mask >> i) & 1) for i, v in enumerate(active_vars)}


def verify_package_data(pkg):
    failures = []
    work = 0
    required = [
        "schema", "language", "theta", "K", "semantics_ref", "Gamma_L", "paid_costs",
        "debt_ledger", "liability_potential", "provenance", "backend", "representation_hash",
        "package_hash", "language_theorem_status", "backend_empirical_status"
    ]
    for key in required:
        work += 1
        if key not in pkg:
            failures.append(f"missing:{key}")
    if failures:
        return failures, work, 0, 0

    work += 1
    if pkg["package_hash"] != recompute_package_hash(pkg):
        failures.append("package_hash_mismatch")
    work += 1
    if pkg["representation_hash"] != recompute_representation_hash(pkg):
        failures.append("representation_hash_mismatch")
    work += 1
    if pkg["semantics_ref"]["semantic_hash"] != expected_semantic_hash(pkg["semantics_ref"]):
        failures.append("semantic_hash_mismatch")
    work += 1
    if pkg["language_theorem_status"] == pkg["backend_empirical_status"]:
        failures.append("theorem_empirical_status_conflated")
    work += 1
    if pkg["liability_potential"].get("Phi") != 1:
        failures.append("pending_package_phi_must_equal_1")
    work += 1
    if pkg["liability_potential"].get("poly_claim_allowed") is not True:
        failures.append("finite_frozen_package_poly_flag_unexpected")
    work += 1
    if pkg.get("status") != "PENDING_INDEPENDENT_REPLAY":
        failures.append("unexpected_package_status")
    work += 1
    if pkg["provenance"].get("exact_fallback_embedded") is not True:
        failures.append("exact_fallback_not_embedded")

    sem = pkg["semantics_ref"]
    active = [int(v) for v in sem["active_vars"]]
    cnf = canon_cnf(sem["cnf"])
    mismatches = 0
    checked = 0
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


def make_receipt(pkg, failures, work, checked, mismatches, replay_kind, certificate_hash=None, transition_checks=None):
    verdict = "PASS" if not failures and mismatches == 0 else "FAIL"
    receipt = {
        "schema": "JANUS/MK_BCEG/R3C/INDEPENDENT_REPLAY_RECEIPT/v1.0",
        "verdict": verdict,
        "replay_kind": replay_kind,
        "accepted_package_hash": pkg["package_hash"] if verdict == "PASS" else None,
        "representation_hash": pkg["representation_hash"],
        "certificate_hash": certificate_hash,
        "verification_work_units": work,
        "semantic_assignments_checked": checked,
        "semantic_mismatches": mismatches,
        "transition_checks": transition_checks or {},
        "failures": failures,
        "liability_discharge": {"verification_liability": 1 if verdict == "PASS" else 0},
        "accepted_phi": 0 if verdict == "PASS" else pkg["liability_potential"]["Phi"],
        "backend_empirical_status_after_replay": "FINITE_REPLAY_PASS" if verdict == "PASS" else "FINITE_REPLAY_FAIL",
        "language_theorem_status_after_replay": pkg["language_theorem_status"],
        "hidden_mutable_state_required": False,
        "replay_inputs": "package JSON plus transition certificate JSON when applicable; no producer cache",
        "verifier": verifier_identity()
    }
    receipt["receipt_hash"] = sha_obj({k: v for k, v in receipt.items() if k != "receipt_hash"})
    return receipt


def verify_certificate_hash(cert):
    body = {k: v for k, v in cert.items() if k != "certificate_hash"}
    return cert.get("certificate_hash") == sha_obj(body)


def cmd_verify_package(args):
    pkg = read_json(args.package)
    failures, work, checked, mismatches = verify_package_data(pkg)
    receipt = make_receipt(pkg, failures, work, checked, mismatches, "PACKAGE")
    Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": receipt["verdict"], "work": work, "checked": checked, "mismatches": mismatches}, indent=2))
    if receipt["verdict"] != "PASS":
        raise SystemExit(1)


def cmd_verify_transition(args):
    src = read_json(args.input)
    out = read_json(args.output_package)
    cert = read_json(args.certificate)
    failures = []
    work = 0

    work += 1
    if not verify_certificate_hash(cert):
        failures.append("certificate_hash_mismatch")
    work += 1
    if cert.get("input_package_hash") != src.get("package_hash"):
        failures.append("certificate_input_hash_mismatch")
    work += 1
    if cert.get("output_package_hash") != out.get("package_hash"):
        failures.append("certificate_output_hash_mismatch")
    work += 1
    if out.get("provenance", {}).get("parent_package_hash") != src.get("package_hash"):
        failures.append("provenance_parent_mismatch")
    work += 1
    if out.get("step") != src.get("step") + 1:
        failures.append("step_not_incremented")

    op = cert.get("operation")
    transition_checks = {"operation": op}
    sin = src["semantics_ref"]
    sout = out["semantics_ref"]
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
    elif op == "TRANSLATE_ROBDD_TO_D_DNNF":
        work += 3
        if src["language"] != "ROBDD_FIXED_ORDER" or out["language"] != "D_DNNF":
            failures.append("translation_language_mismatch")
        if sout != sin:
            failures.append("translation_semantics_changed")
        if cert["operation_args"].get("producer_local_certificate_failures") != []:
            failures.append("producer_reported_local_certificate_failure")
        transition_checks["translation_semantics"] = "CHECKED_INDEPENDENTLY"
    else:
        failures.append(f"unknown_transition_operation:{op}")

    p_failures, p_work, checked, mismatches = verify_package_data(out)
    failures.extend(p_failures)
    work += p_work
    receipt = make_receipt(
        out,
        failures,
        work,
        checked,
        mismatches,
        "TRANSITION",
        certificate_hash=cert.get("certificate_hash"),
        transition_checks=transition_checks
    )
    Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": receipt["verdict"], "work": work, "checked": checked, "mismatches": mismatches, "operation": op}, indent=2))
    if receipt["verdict"] != "PASS":
        raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    vp = sub.add_parser("verify-package")
    vp.add_argument("--package", required=True)
    vp.add_argument("--output", required=True)
    vp.set_defaults(fn=cmd_verify_package)
    vt = sub.add_parser("verify-transition")
    vt.add_argument("--input", required=True)
    vt.add_argument("--output-package", required=True)
    vt.add_argument("--certificate", required=True)
    vt.add_argument("--receipt", required=True)
    vt.set_defaults(fn=cmd_verify_transition)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
