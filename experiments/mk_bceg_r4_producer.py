#!/usr/bin/env python3
import argparse
import hashlib
import json
import platform
from pathlib import Path

from mk_bceg_r3c_producer import (
    canon_cnf,
    restrict_cnf,
    compile_obdd,
    translate_obdd_to_ddnnf,
    condition_ddnnf,
    json_ready_rep,
    json_ready_cnf,
)

ROOT = Path(__file__).resolve().parent.parent
CAP_MAP_PATH = ROOT / "research/MK_BCEG_R3B_OPERATION_CAPABILITY_MAP_2026-08-30.json"
ENGINE_DEP = ROOT / "experiments/mk_bceg_r3c_producer.py"
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


def load_map():
    m = json.loads(CAP_MAP_PATH.read_text())
    return m, sha_file(CAP_MAP_PATH)


def backend_identity(release_version):
    return {
        "producer_id": "MK_BCEG_R4_PRODUCER",
        "producer_schema_version": "1.0",
        "release_version": str(release_version),
        "python_version": platform.python_version(),
        "producer_source_sha256": sha_file(__file__),
        "engine_dependency_sha256": sha_file(ENGINE_DEP),
    }


def capability_digest(gamma, cap_map_hash):
    return sha_obj({"Gamma_L": gamma, "capability_map_sha256": cap_map_hash})


def backend_contract_digest(backend):
    return sha_obj(backend)


def representation_hash(language, theta, K):
    return sha_obj({"language": language, "theta": theta, "K": K})


def semantic_hash(sem):
    return sha_obj({
        "cnf": sem["cnf"],
        "active_vars": sem["active_vars"],
        "frozen_assignments": sem.get("frozen_assignments", {}),
    })


def package_hash(pkg):
    body = dict(pkg)
    body.pop("package_hash", None)
    return sha_obj(body)


def receipt_hash(receipt):
    body = dict(receipt)
    body.pop("receipt_hash", None)
    return sha_obj(body)


def require_acceptance(pkg, receipt):
    if receipt.get("receipt_hash") != receipt_hash(receipt):
        raise ValueError("STALE_OR_REPLAYED_RECEIPT: receipt hash mismatch")
    if receipt.get("verdict") != "PASS":
        raise ValueError("STALE_OR_REPLAYED_RECEIPT: no PASS authority")
    if receipt.get("accepted_package_hash") != pkg.get("package_hash"):
        raise ValueError("STALE_OR_REPLAYED_RECEIPT: package binding mismatch")
    if receipt.get("accepted_capability_digest") != pkg.get("capability_digest"):
        raise ValueError("STALE_OR_REPLAYED_RECEIPT: capability binding mismatch")
    if receipt.get("accepted_backend_contract_digest") != pkg.get("backend_contract_digest"):
        raise ValueError("STALE_OR_REPLAYED_RECEIPT: backend binding mismatch")
    if receipt.get("accepted_phi") != 0:
        raise ValueError("STALE_OR_REPLAYED_RECEIPT: liability not discharged")
    if pkg.get("step", 0) > 0:
        b = receipt.get("transition_binding", {})
        if b.get("successor_package_hash") != pkg.get("package_hash"):
            raise ValueError("STALE_OR_REPLAYED_RECEIPT: successor binding mismatch")
        if b.get("capability_digest") != pkg.get("capability_digest"):
            raise ValueError("STALE_OR_REPLAYED_RECEIPT: transition capability mismatch")
        if b.get("backend_contract_digest") != pkg.get("backend_contract_digest"):
            raise ValueError("STALE_OR_REPLAYED_RECEIPT: transition backend mismatch")


def seed_formula(pairs):
    f = []
    for i in range(pairs):
        a, b = 2 * i + 1, 2 * i + 2
        f.extend([(-a, b), (a, -b)])
    return canon_cnf(f)


def make_package(step, language, theta, K, semantics_ref, cumulative_paid, provenance,
                 cap_map, cap_map_hash, producer_work, release_version, previous_receipt=None,
                 root_anchor_hash=None):
    backend = backend_identity(release_version)
    gamma = cap_map["languages"][language]
    cap_digest = capability_digest(gamma, cap_map_hash)
    back_digest = backend_contract_digest(backend)
    if previous_receipt is None:
        parent_receipt_hash = None
        lineage_depth = 0
    else:
        parent_receipt_hash = previous_receipt["receipt_hash"]
        lineage_depth = int(provenance.get("parent_lineage_depth", 0)) + 1
    pkg = {
        "schema": "JANUS/MK_BCEG/R4/PROOF_STATE_PASSPORT/v1.0",
        "status": "PENDING_INDEPENDENT_REPLAY",
        "canonicalization_profile": CANON_PROFILE,
        "step": int(step),
        "language": language,
        "theta": theta,
        "K": K,
        "semantics_ref": semantics_ref,
        "Gamma_L": gamma,
        "capability_map_sha256": cap_map_hash,
        "capability_digest": cap_digest,
        "backend": backend,
        "backend_contract_digest": back_digest,
        "paid_costs": {
            "cumulative_work_units_before_current_verification": int(cumulative_paid) + int(producer_work),
            "current_producer_work_units": int(producer_work),
            "current_verification_work_units": None,
        },
        "debt_ledger": [],
        "liability_potential": {
            "D_upper": 0,
            "V_liability": 1,
            "S_liability": 0,
            "Phi": 1,
            "upper_bounds_known": True,
            "poly_claim_allowed": True,
        },
        "provenance": provenance,
        "authority_lineage": {
            "law": "AUTHORITY_IS_TRANSITIVE_ONLY_THROUGH_VERIFIED_TRANSITIONS",
            "root_anchor_hash": root_anchor_hash,
            "parent_package_hash": provenance.get("parent_package_hash"),
            "parent_acceptance_receipt_hash": parent_receipt_hash,
            "lineage_depth": lineage_depth,
        },
        "language_theorem_status": "EXTERNAL_MAP_ONLY_NOT_INTERNAL_RECEIPT",
        "backend_empirical_status": "PENDING_INDEPENDENT_REPLAY",
        "representation_hash": representation_hash(language, theta, K),
    }
    if not no_floats(pkg):
        raise ValueError("R4 canonical payload forbids floating-point numbers")
    pkg["package_hash"] = package_hash(pkg)
    return pkg


def cumulative_from_acceptance(pkg, receipt):
    return int(pkg["paid_costs"]["cumulative_work_units_before_current_verification"]) + int(receipt["verification_work_units"])


def cmd_seed(args):
    cap_map, cap_map_hash = load_map()
    pairs = int(args.pairs)
    if pairs < 1 or pairs > 12:
        raise ValueError("R4 seed pairs must be 1..12")
    f = seed_formula(pairs)
    order = list(range(1, 2 * pairs + 1))
    rep, work = compile_obdd(f, order)
    semantics = {
        "kind": "CNF",
        "cnf": json_ready_cnf(f),
        "active_vars": order,
        "all_vars": order,
        "frozen_assignments": {},
    }
    semantics["semantic_hash"] = semantic_hash(semantics)
    root_anchor = sha_obj({
        "kind": "FROZEN_R4_SEED_SEMANTICS",
        "semantics_ref": semantics,
        "capability_map_sha256": cap_map_hash,
        "canonicalization_profile": CANON_PROFILE,
    })
    provenance = {
        "parent_package_hash": None,
        "parent_lineage_depth": -1,
        "operation": "SEED_COMPILE",
        "args": {"pairs": pairs},
        "exact_fallback_embedded": True,
        "input_acceptance_receipt_hash": None,
    }
    pkg = make_package(
        0, "ROBDD_FIXED_ORDER",
        {"variable_order": order, "backend_operation": "COMPILE_FROM_EXACT_CNF"},
        json_ready_rep(rep), semantics, 0, provenance, cap_map, cap_map_hash, work,
        args.backend_version, previous_receipt=None, root_anchor_hash=root_anchor,
    )
    write_json(args.output, pkg)
    print(json.dumps({
        "package_hash": pkg["package_hash"],
        "root_anchor_hash": root_anchor,
        "producer_work_units": work,
        "backend_version": args.backend_version,
        "Phi": 1,
    }, indent=2))


def cmd_transition(args):
    cap_map, cap_map_hash = load_map()
    src = read_json(args.input)
    receipt = read_json(args.receipt)
    require_acceptance(src, receipt)
    cumulative = cumulative_from_acceptance(src, receipt)
    sem = src["semantics_ref"]
    f = canon_cnf(sem["cnf"])
    active = [int(v) for v in sem["active_vars"]]
    frozen = dict(sem.get("frozen_assignments", {}))
    op = args.operation
    producer_work = 0
    cert_args = {}

    if op == "ASSIGN":
        if args.var is None or args.value is None:
            raise ValueError("ASSIGN requires --var and --value")
        var = int(args.var)
        value = str(args.value).lower() in {"1", "true", "t", "yes"}
        if var not in active:
            raise ValueError("Assigned variable is not active")
        f2 = restrict_cnf(f, var, value)
        active2 = [v for v in active if v != var]
        frozen[str(var)] = value
        if src["language"] == "ROBDD_FIXED_ORDER":
            order = [v for v in src["theta"]["variable_order"] if int(v) != var]
            rep, producer_work = compile_obdd(f2, order)
            language = "ROBDD_FIXED_ORDER"
            theta = {"variable_order": order, "backend_operation": "RESTRICT_CNF_THEN_RECOMPILE_ROBDD"}
            K = json_ready_rep(rep)
        elif src["language"] == "D_DNNF":
            rep_in = {"root": src["K"]["root"], "nodes": {int(k): tuple(v) for k, v in src["K"]["nodes"].items()}}
            rep, producer_work = condition_ddnnf(rep_in, var, value)
            language = "D_DNNF"
            theta = {"backend_operation": "CONDITION_D_DNNF"}
            K = json_ready_rep(rep)
        else:
            raise ValueError("ASSIGN unsupported in R4 prototype language")
        semantics = {
            "kind": "CNF",
            "cnf": json_ready_cnf(f2),
            "active_vars": active2,
            "all_vars": sem["all_vars"],
            "frozen_assignments": frozen,
        }
        semantics["semantic_hash"] = semantic_hash(semantics)
        cert_args = {"var": var, "value": value}

    elif op == "ROBDD_TO_D_DNNF":
        if src["language"] != "ROBDD_FIXED_ORDER":
            raise ValueError("ROBDD_TO_D_DNNF requires ROBDD_FIXED_ORDER")
        rep_in = {"root": src["K"]["root"], "nodes": {int(k): tuple(v) for k, v in src["K"]["nodes"].items()}}
        rep, producer_work = translate_obdd_to_ddnnf(rep_in)
        if rep["local_cert_failures"]:
            raise ValueError("Producer local decomposability certificate failure")
        language = "D_DNNF"
        theta = {"backend_operation": "SHANNON_OBDD_TO_D_DNNF", "source_language": "ROBDD_FIXED_ORDER"}
        K = json_ready_rep(rep)
        semantics = sem
        cert_args = {"translation_kind": "SHANNON_EXPANSION", "producer_local_certificate_failures": []}

    elif op == "D_DNNF_TO_ROBDD_EXACT_RECOMPILE":
        if src["language"] != "D_DNNF":
            raise ValueError("D_DNNF_TO_ROBDD_EXACT_RECOMPILE requires D_DNNF")
        order = list(active)
        rep, producer_work = compile_obdd(f, order)
        language = "ROBDD_FIXED_ORDER"
        theta = {
            "variable_order": order,
            "backend_operation": "RECOMPILE_ROBDD_FROM_EMBEDDED_EXACT_CNF",
            "source_language": "D_DNNF",
        }
        K = json_ready_rep(rep)
        semantics = sem
        cert_args = {"translation_kind": "EXACT_FALLBACK_RECOMPILE", "direct_representation_translation": False}

    else:
        raise ValueError(f"Unknown R4 operation: {op}")

    provenance = {
        "parent_package_hash": src["package_hash"],
        "parent_lineage_depth": src["authority_lineage"]["lineage_depth"],
        "operation": op,
        "args": cert_args,
        "exact_fallback_embedded": True,
        "input_acceptance_receipt_hash": receipt["receipt_hash"],
    }
    pkg = make_package(
        int(src["step"]) + 1, language, theta, K, semantics, cumulative, provenance,
        cap_map, cap_map_hash, producer_work, args.backend_version,
        previous_receipt=receipt,
        root_anchor_hash=src["authority_lineage"]["root_anchor_hash"],
    )
    cert = {
        "schema": "JANUS/MK_BCEG/R4/TRANSITION_CERTIFICATE/v1.0",
        "canonicalization_profile": CANON_PROFILE,
        "producer": backend_identity(args.backend_version),
        "input_package_hash": src["package_hash"],
        "input_representation_hash": src["representation_hash"],
        "input_capability_digest": src["capability_digest"],
        "input_backend_contract_digest": src["backend_contract_digest"],
        "input_acceptance_receipt_hash": receipt["receipt_hash"],
        "output_package_hash": pkg["package_hash"],
        "output_representation_hash": pkg["representation_hash"],
        "output_capability_digest": pkg["capability_digest"],
        "output_backend_contract_digest": pkg["backend_contract_digest"],
        "operation": op,
        "operation_args": cert_args,
        "producer_work_units": int(producer_work),
        "semantic_claim": "EXACT_REQUIRES_INDEPENDENT_REPLAY",
    }
    cert["certificate_hash"] = sha_obj({k: v for k, v in cert.items() if k != "certificate_hash"})
    write_json(args.output, pkg)
    write_json(args.certificate, cert)
    print(json.dumps({
        "package_hash": pkg["package_hash"],
        "certificate_hash": cert["certificate_hash"],
        "producer_work_units": producer_work,
        "backend_version": args.backend_version,
        "lineage_depth": pkg["authority_lineage"]["lineage_depth"],
        "Phi": 1,
    }, indent=2))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    seed = sub.add_parser("seed")
    seed.add_argument("--pairs", type=int, default=4)
    seed.add_argument("--backend-version", default="1.0")
    seed.add_argument("--output", required=True)
    seed.set_defaults(fn=cmd_seed)
    tr = sub.add_parser("transition")
    tr.add_argument("--input", required=True)
    tr.add_argument("--receipt", required=True)
    tr.add_argument("--operation", required=True, choices=["ASSIGN", "ROBDD_TO_D_DNNF", "D_DNNF_TO_ROBDD_EXACT_RECOMPILE"])
    tr.add_argument("--var", type=int)
    tr.add_argument("--value")
    tr.add_argument("--backend-version", default="1.0")
    tr.add_argument("--output", required=True)
    tr.add_argument("--certificate", required=True)
    tr.set_defaults(fn=cmd_transition)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
