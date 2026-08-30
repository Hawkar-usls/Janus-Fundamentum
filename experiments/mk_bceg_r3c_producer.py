#!/usr/bin/env python3
import argparse
import hashlib
import json
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP_MAP_PATH = ROOT / "research/MK_BCEG_R3B_OPERATION_CAPABILITY_MAP_2026-08-30.json"


def canon_obj(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_obj(x):
    return hashlib.sha256(canon_obj(x)).hexdigest()


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def compile_obdd(f, order):
    memo, uniq, nodes = {}, {}, {}
    nxt = [2]
    work = [0]

    def rec(i, state):
        work[0] += 1
        if state == ():
            return 1
        if state == ((),):
            return 0
        key = (i, state)
        if key in memo:
            return memo[key]
        if i >= len(order):
            raise ValueError("OBDD variable order exhausted before formula resolved")
        v = order[i]
        lo = rec(i + 1, restrict_cnf(state, v, False))
        hi = rec(i + 1, restrict_cnf(state, v, True))
        if lo == hi:
            memo[key] = lo
            return lo
        node = (v, lo, hi)
        if node not in uniq:
            uniq[node] = nxt[0]
            nodes[nxt[0]] = node
            nxt[0] += 1
        memo[key] = uniq[node]
        return memo[key]

    root = rec(0, canon_cnf(f))
    return {"root": root, "nodes": nodes, "total_nodes": len(nodes) + 2}, work[0]


def support_obdd(comp, node, memo=None):
    memo = {} if memo is None else memo
    if node in (0, 1):
        return frozenset()
    if node in memo:
        return memo[node]
    v, lo, hi = comp["nodes"][node]
    s = frozenset({v}) | support_obdd(comp, lo, memo) | support_obdd(comp, hi, memo)
    memo[node] = s
    return s


def translate_obdd_to_ddnnf(comp):
    nodes = {0: ("CONST", False), 1: ("CONST", True)}
    uniq = {("CONST", False): 0, ("CONST", True): 1}
    nxt = [2]
    srcmap = {0: 0, 1: 1}
    litcache = {}
    cert_fail = []
    work = [0]
    smemo = {}

    def mk(k):
        work[0] += 1
        if k in uniq:
            return uniq[k]
        i = nxt[0]
        nxt[0] += 1
        uniq[k] = i
        nodes[i] = k
        return i

    def lit(v, pol):
        k = (v, pol)
        if k not in litcache:
            litcache[k] = mk(("LIT", v, pol))
        return litcache[k]

    def rec(i):
        if i in srcmap:
            return srcmap[i]
        v, lo, hi = comp["nodes"][i]
        sl = support_obdd(comp, lo, smemo)
        sh = support_obdd(comp, hi, smemo)
        if v in sl or v in sh:
            cert_fail.append({"source_node": i, "failure": "DECOMPOSABILITY_SUPPORT", "var": v})
        l = rec(lo)
        h = rec(hi)
        a0 = mk(("AND", lit(v, False), l))
        a1 = mk(("AND", lit(v, True), h))
        out = mk(("OR", a0, a1))
        srcmap[i] = out
        return out

    root = rec(comp["root"])
    return {
        "root": root,
        "nodes": nodes,
        "source_to_dest": srcmap,
        "local_cert_failures": cert_fail,
        "structural_nodes": len(nodes),
    }, work[0]


def condition_ddnnf(d, var, value):
    old = d["nodes"]
    memo = {}
    uniq = {("CONST", False): 0, ("CONST", True): 1}
    nodes = {0: ("CONST", False), 1: ("CONST", True)}
    nxt = [2]
    work = [0]

    def mk(k):
        work[0] += 1
        if k in uniq:
            return uniq[k]
        i = nxt[0]
        nxt[0] += 1
        uniq[k] = i
        nodes[i] = k
        return i

    def rec(i):
        if i in memo:
            return memo[i]
        k = old[i]
        t = k[0]
        if t == "CONST":
            out = 1 if k[1] else 0
        elif t == "LIT":
            if k[1] == var:
                out = 1 if (value if k[2] else not value) else 0
            else:
                out = mk(k)
        else:
            a, b = rec(k[1]), rec(k[2])
            if t == "AND":
                if a == 0 or b == 0:
                    out = 0
                elif a == 1:
                    out = b
                elif b == 1:
                    out = a
                elif a == b:
                    out = a
                else:
                    out = mk(("AND", a, b))
            elif t == "OR":
                if a == 1 or b == 1:
                    out = 1
                elif a == 0:
                    out = b
                elif b == 0:
                    out = a
                elif a == b:
                    out = a
                else:
                    out = mk(("OR", a, b))
            else:
                raise ValueError(f"Unknown D_DNNF node type: {t}")
        memo[i] = out
        return out

    root = rec(d["root"])
    return {"root": root, "nodes": nodes, "structural_nodes": len(nodes)}, work[0]


def json_ready_rep(rep):
    out = dict(rep)
    if "nodes" in out:
        out["nodes"] = {str(k): list(v) for k, v in out["nodes"].items()}
    if "source_to_dest" in out:
        out["source_to_dest"] = {str(k): v for k, v in out["source_to_dest"].items()}
    return out


def json_ready_cnf(f):
    return [list(c) for c in f]


def load_map():
    return json.loads(CAP_MAP_PATH.read_text()), sha_file(CAP_MAP_PATH)


def backend_identity():
    return {
        "producer_id": "MK_BCEG_R3C_PRODUCER",
        "producer_schema_version": "1.0",
        "python_version": platform.python_version(),
        "producer_source_sha256": sha_file(__file__),
    }


def package_hash(pkg):
    body = dict(pkg)
    body.pop("package_hash", None)
    return sha_obj(body)


def representation_hash(language, theta, K):
    return sha_obj({"language": language, "theta": theta, "K": K})


def read_json(path):
    return json.loads(Path(path).read_text())


def require_acceptance(pkg, receipt):
    if receipt.get("verdict") != "PASS":
        raise ValueError("Previous package has no PASS replay receipt")
    if receipt.get("accepted_package_hash") != pkg.get("package_hash"):
        raise ValueError("Replay receipt/package hash mismatch")
    if receipt.get("accepted_phi") != 0:
        raise ValueError("Accepted package must have zero outstanding certified liability potential")


def make_package(step, language, theta, K, semantics_ref, cumulative_paid, provenance, cap_map, cap_map_hash, producer_work, previous_acceptance=None):
    pkg = {
        "schema": "JANUS/MK_BCEG/R3C/PROOF_CARRYING_EXECUTABLE_LIFECYCLE_PACKAGE/v1.0",
        "status": "PENDING_INDEPENDENT_REPLAY",
        "step": step,
        "language": language,
        "theta": theta,
        "K": K,
        "semantics_ref": semantics_ref,
        "Gamma_L": cap_map["languages"][language],
        "paid_costs": {
            "cumulative_work_units_before_current_verification": cumulative_paid + producer_work,
            "current_producer_work_units": producer_work,
            "current_verification_work_units": None
        },
        "debt_ledger": [],
        "liability_potential": {
            "D_upper": 0,
            "V_liability": 1,
            "S_liability": 0,
            "Phi": 1,
            "poly_claim_allowed": True
        },
        "provenance": provenance,
        "backend": backend_identity(),
        "capability_map_sha256": cap_map_hash,
        "language_theorem_status": "EXTERNAL_MAP_ONLY_NOT_INTERNAL_RECEIPT",
        "backend_empirical_status": "PENDING_INDEPENDENT_REPLAY",
        "previous_acceptance_receipt_hash": sha_obj(previous_acceptance) if previous_acceptance else None,
        "representation_hash": representation_hash(language, theta, K)
    }
    pkg["package_hash"] = package_hash(pkg)
    return pkg


def seed_formula():
    f = []
    for a, b in ((1, 2), (3, 4), (5, 6), (7, 8)):
        f.extend([(-a, b), (a, -b)])
    return canon_cnf(f)


def cmd_seed(args):
    cap_map, cap_map_hash = load_map()
    f = seed_formula()
    order = list(range(1, 9))
    rep, work = compile_obdd(f, order)
    semantics = {
        "kind": "CNF",
        "cnf": json_ready_cnf(f),
        "active_vars": order,
        "all_vars": order,
        "frozen_assignments": {},
        "semantic_hash": sha_obj({"cnf": json_ready_cnf(f), "active_vars": order, "frozen_assignments": {}})
    }
    pkg = make_package(
        step=0,
        language="ROBDD_FIXED_ORDER",
        theta={"variable_order": order, "backend_operation": "COMPILE_FROM_EXACT_CNF"},
        K=json_ready_rep(rep),
        semantics_ref=semantics,
        cumulative_paid=0,
        provenance={"parent_package_hash": None, "operation": "SEED_COMPILE", "args": {}, "exact_fallback_embedded": True},
        cap_map=cap_map,
        cap_map_hash=cap_map_hash,
        producer_work=work
    )
    Path(args.output).write_text(json.dumps(pkg, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"package_hash": pkg["package_hash"], "producer_work": work, "phi": 1}, indent=2))


def cumulative_from_acceptance(pkg, receipt):
    return pkg["paid_costs"]["cumulative_work_units_before_current_verification"] + int(receipt["verification_work_units"])


def cmd_transition(args):
    cap_map, cap_map_hash = load_map()
    src = read_json(args.input)
    receipt = read_json(args.receipt)
    require_acceptance(src, receipt)
    cumulative = cumulative_from_acceptance(src, receipt)
    op = args.operation
    sem = src["semantics_ref"]
    f = canon_cnf(sem["cnf"])
    active = list(sem["active_vars"])
    frozen = dict(sem.get("frozen_assignments", {}))
    producer_work = 0
    cert_extra = {}

    if op == "ASSIGN":
        if args.var is None or args.value is None:
            raise ValueError("ASSIGN requires --var and --value")
        var = int(args.var)
        value = args.value.lower() in {"1", "true", "t", "yes"}
        if var not in active:
            raise ValueError("Assigned variable is not active")
        f2 = restrict_cnf(f, var, value)
        active2 = [v for v in active if v != var]
        frozen[str(var)] = value
        if src["language"] == "ROBDD_FIXED_ORDER":
            order = [v for v in src["theta"]["variable_order"] if v != var]
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
            raise ValueError("ASSIGN backend unsupported in R3C prototype")
        semantics = {
            "kind": "CNF",
            "cnf": json_ready_cnf(f2),
            "active_vars": active2,
            "all_vars": sem["all_vars"],
            "frozen_assignments": frozen,
            "semantic_hash": sha_obj({"cnf": json_ready_cnf(f2), "active_vars": active2, "frozen_assignments": frozen})
        }
        cert_extra = {"var": var, "value": value}

    elif op == "TRANSLATE_ROBDD_TO_D_DNNF":
        if src["language"] != "ROBDD_FIXED_ORDER":
            raise ValueError("Translation source must be ROBDD_FIXED_ORDER")
        rep_in = {"root": src["K"]["root"], "nodes": {int(k): tuple(v) for k, v in src["K"]["nodes"].items()}}
        rep, producer_work = translate_obdd_to_ddnnf(rep_in)
        if rep["local_cert_failures"]:
            raise ValueError("Producer local decomposability certificate failure")
        language = "D_DNNF"
        theta = {"backend_operation": "SHANNON_OBDD_TO_D_DNNF", "source_language": "ROBDD_FIXED_ORDER"}
        K = json_ready_rep(rep)
        semantics = sem
        cert_extra = {"translation_kind": "SHANNON_EXPANSION", "producer_local_certificate_failures": rep["local_cert_failures"]}

    else:
        raise ValueError(f"Unknown operation: {op}")

    provenance = {
        "parent_package_hash": src["package_hash"],
        "operation": op,
        "args": cert_extra,
        "exact_fallback_embedded": True,
        "input_acceptance_receipt_hash": sha_obj(receipt)
    }
    pkg = make_package(
        step=int(src["step"]) + 1,
        language=language,
        theta=theta,
        K=K,
        semantics_ref=semantics,
        cumulative_paid=cumulative,
        provenance=provenance,
        cap_map=cap_map,
        cap_map_hash=cap_map_hash,
        producer_work=producer_work,
        previous_acceptance=receipt
    )
    cert = {
        "schema": "JANUS/MK_BCEG/R3C/TRANSITION_CERTIFICATE/v1.0",
        "producer": backend_identity(),
        "input_package_hash": src["package_hash"],
        "input_representation_hash": src["representation_hash"],
        "output_package_hash": pkg["package_hash"],
        "output_representation_hash": pkg["representation_hash"],
        "operation": op,
        "operation_args": cert_extra,
        "producer_work_units": producer_work,
        "semantic_claim": "EXACT",
        "authority": "PRODUCER_CLAIM_REQUIRES_INDEPENDENT_REPLAY"
    }
    cert["certificate_hash"] = sha_obj({k: v for k, v in cert.items() if k != "certificate_hash"})
    Path(args.output).write_text(json.dumps(pkg, indent=2, sort_keys=True) + "\n")
    Path(args.certificate).write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"package_hash": pkg["package_hash"], "certificate_hash": cert["certificate_hash"], "producer_work": producer_work, "phi": 1}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    seed = sub.add_parser("seed")
    seed.add_argument("--output", required=True)
    seed.set_defaults(fn=cmd_seed)
    trans = sub.add_parser("transition")
    trans.add_argument("--input", required=True)
    trans.add_argument("--receipt", required=True)
    trans.add_argument("--operation", required=True)
    trans.add_argument("--var", type=int)
    trans.add_argument("--value")
    trans.add_argument("--output", required=True)
    trans.add_argument("--certificate", required=True)
    trans.set_defaults(fn=cmd_transition)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
