from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Sequence

import janus_c049_1_b4_2_3k_scaffold as b42
import janus_c049_1_b5_1_generic_corrected_runtime_trace_executor_verifier as b51v
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11 as b52av
import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier as b52bv
import janus_c049_1_b5_3_generic_empty_root_terminal_composition_verifier as b53v
import janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v11 as b54v
from janus_c049_1_b3_expand_join_shrink_core import subspace_intersection, xor_basis

SCHEMA = "janus.c049_1.b5.iterative_compression_orchestrator_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.iterative_compression_orchestrator_spec.v1"
BASE = Path("experiments/direct")

B51_SPEC = BASE / "C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_SPEC_V1.json"
B52A_AMENDMENT = BASE / "C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_AMENDMENT_V1_1.json"
B52B_SPEC = BASE / "C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_SPEC_V1.json"
B53_SPEC = BASE / "C049_1_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION_SPEC_V1.json"
B54_SPEC = BASE / "C049_1_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_SPEC_V1.json"

B5_CONTRACT_RECEIPT = BASE / "audits/C049_1_B5_GENERAL_RUNTIME_TERMINAL_CONTRACT_ADMISSION_CEBBCFF9.json"
B51_RECEIPT = BASE / "audits/C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_ADMISSION_DDA63620.json"
B52B_RECEIPT = BASE / "audits/C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_ADMISSION_F057B7AF.json"
B53_RECEIPT = BASE / "audits/C049_1_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION_ADMISSION_E9841522.json"
COMPOSITION_AUDIT = BASE / "audits/C049_1_B4_6_3_GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_INDEPENDENT_SOURCE_AUDIT_4F8F9424.json"
O7_AUDIT = BASE / "audits/C049_1_B4_6_3_GENERAL_EMPTY_ROOT_SPECIALIZATION_AUTHORITY_CLOSURE_AUDIT_7F9DF43C.json"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_bytes(value: Any | None) -> int:
    return 0 if value is None else len(cb(value)) + 1


def parse_raw(raw: dict) -> tuple[int, int, list[dict], list[str], dict, dict, int | None]:
    d, k = int(raw["ambient_dim"]), int(raw["k"])
    if d <= 0 or k < 0:
        raise AssertionError("d/k")
    factors = []
    seen = set()
    for item in raw.get("factors", []):
        fid = str(item["id"])
        if not fid or fid in seen:
            raise AssertionError("factor identity")
        seen.add(fid)
        factors.append({"id": fid, "normal_space": list(xor_basis(item.get("normal_space", []), d)), "affine_offset": item.get("affine_offset")})
    if not factors:
        raise AssertionError("empty factors")
    factors.sort(key=lambda x: x["id"])
    order = [str(x) for x in raw.get("input_order", [])]
    if len(order) != len(factors) or len(set(order)) != len(order) or sorted(order) != [f["id"] for f in factors]:
        raise AssertionError("input order")
    runtime_caps = dict(raw.get("runtime_caps", {}))
    phase_a_caps = dict(raw.get("phase_a_caps", {}))
    mr = raw.get("max_rounds")
    max_rounds = None if mr is None else int(mr)
    if max_rounds is not None and max_rounds < 0:
        raise AssertionError("round cap")
    return d, k, factors, order, runtime_caps, phase_a_caps, max_rounds


def fmap(factors: Sequence[dict]) -> dict[str, dict]:
    return {str(x["id"]): x for x in factors}


def left_deep(order_ids: Sequence[str], r: int) -> dict:
    leaves = [{"id": f"r{r:04d}:leaf:{i:04d}", "factor_id": str(fid)} for i, fid in enumerate(order_ids)]
    if not leaves:
        raise AssertionError("empty tree")
    if len(leaves) == 1:
        return {"root": leaves[0]["id"], "nodes": leaves}
    nodes = list(leaves)
    left = leaves[0]["id"]
    for i in range(1, len(leaves)):
        nid = f"r{r:04d}:join:{i:04d}"
        nodes.append({"id": nid, "left": left, "right": leaves[i]["id"]})
        left = nid
    return {"root": left, "nodes": nodes}


def tree_cert(tree: dict, factors: Sequence[dict], d: int, k: int) -> dict:
    by = fmap(factors)
    nodes = {str(n["id"]): n for n in tree["nodes"]}
    root = str(tree["root"])
    state, covers = {}, {}

    def visit(nid: str) -> tuple[str, ...]:
        if nid not in nodes or state.get(nid) == 1 or state.get(nid) == 2:
            raise AssertionError("tree cycle/multiparent")
        state[nid] = 1
        n = nodes[nid]
        if "factor_id" in n:
            fid = str(n["factor_id"])
            if fid not in by:
                raise AssertionError("unknown factor")
            c = (fid,)
        else:
            c = tuple(sorted((*visit(str(n["left"])), *visit(str(n["right"])))))
        state[nid] = 2
        covers[nid] = c
        return c

    root_cover = visit(root)
    if len(state) != len(nodes) or sorted(root_cover) != sorted(by) or len(root_cover) != len(set(root_cover)):
        raise AssertionError("tree coverage")
    edges, maximum = [], 0
    allids = set(by)
    for nid in sorted(nodes):
        if nid == root:
            continue
        covered = covers[nid]
        outside = tuple(sorted(allids - set(covered)))
        ls = xor_basis([v for fid in covered for v in by[fid]["normal_space"]], d)
        rs = xor_basis([v for fid in outside for v in by[fid]["normal_space"]], d)
        b = subspace_intersection(ls, rs, d)
        maximum = max(maximum, len(b))
        edges.append({"node_id": nid, "covered_factor_ids": list(covered), "outside_factor_ids": list(outside), "covered_span_rref": list(ls), "outside_span_rref": list(rs), "boundary_rref": list(b), "width": len(b)})
    return {"tree_digest": dg(tree), "edge_certificates": edges, "maximum_nonroot_edge_boundary_dimension": maximum, "three_k_cap": 3 * k, "all_nonroot_edges_width_le_3k": maximum <= 3 * k}


def round_raw(prefix: Sequence[dict], tree: dict, d: int, k: int, caps: dict) -> dict:
    value = {"ambient_dim": d, "k": k, "factors": [dict(x) for x in prefix], "tree": tree}
    if caps:
        value["caps"] = dict(caps)
    return value


def expected_monotonicity(prefix: Sequence[str], whole: Sequence[str], k: int) -> dict:
    p, w = [str(x) for x in prefix], [str(x) for x in whole]
    if not p or p == w or w[: len(p)] != p:
        raise AssertionError("monotonicity domain")
    omitted = w[len(p):]
    return {
        "lemma": "SUBARRANGEMENT_DELETION_MONOTONICITY",
        "prefix_factor_ids": p,
        "omitted_factor_ids": omitted,
        "full_factor_ids": w,
        "prefix_is_strict_schedule_prefix": True,
        "indexed_occurrence_partition": sorted(p + omitted) == sorted(w) and len(set(w)) == len(w),
        "hypothetical_full_layout_to_prefix_layout_map": "DELETE_ALL_NONPREFIX_OCCURRENCES_PRESERVING_RELATIVE_ORDER",
        "cut_map": "AFTER_r_PREFIX_OCCURRENCES_IN_THE_INDUCED_ORDER_USE_THE_FULL_LAYOUT_CUT_IMMEDIATELY_AFTER_THE_r_TH_PREFIX_OCCURRENCE",
        "left_span_inclusion": "PREFIX_LEFT_SPAN_LE_FULL_LEFT_SPAN",
        "right_span_inclusion": "PREFIX_RIGHT_SPAN_LE_FULL_RIGHT_SPAN",
        "intersection_inclusion": "PREFIX_LEFT_INTER_PREFIX_RIGHT_LE_FULL_LEFT_INTER_FULL_RIGHT",
        "width_conclusion": "INDUCED_PREFIX_LAYOUT_WIDTH_LE_FULL_LAYOUT_WIDTH",
        "contrapositive": "PREFIX_NO_LAYOUT_AT_WIDTH_LE_K_IMPLIES_FULL_NO_LAYOUT_AT_WIDTH_LE_K",
        "k": int(k),
        "affine_unsat_claimed": False,
    }


def verify_monotonicity(certificate: dict, prefix: Sequence[str], whole: Sequence[str], k: int) -> None:
    if certificate != expected_monotonicity(prefix, whole, k):
        raise AssertionError("deletion monotonicity certificate")
    # The mathematical direction is checked structurally: deleting occurrences
    # can only shrink both cut spans, hence their intersection is a subspace of
    # the corresponding full-layout cut intersection. The certificate may not
    # reverse this implication or mention affine satisfiability.
    if certificate["affine_unsat_claimed"] is not False:
        raise AssertionError("affine promotion")


def verify_scaffold(
    candidate_witness: dict,
    prefix: Sequence[dict],
    previous_layout: Sequence[str],
    d: int,
    k: int,
    expected_tree: dict,
    candidate_tree_cert: dict,
) -> None:
    schedule = [str(x["id"]) for x in prefix]
    local = {fid: i for i, fid in enumerate(schedule)}
    old = [local[str(fid)] for fid in previous_layout]
    blocks = [tuple(int(v) for v in x["normal_space"]) for x in prefix]
    betas = [x.get("affine_offset") for x in prefix]
    rebuilt = b42.scaffold(blocks, old, len(prefix) - 1, d, k, betas)
    if candidate_witness != rebuilt:
        raise AssertionError("B4.2 scaffold witness")
    if rebuilt.get("terminal") != "SCAFFOLD_3K_CERTIFIED":
        raise AssertionError("unexpected B4.2 local terminal")
    order_ids = [schedule[int(i)] for i in rebuilt["scaffold_order"]]
    if expected_tree != left_deep(order_ids, len(prefix)):
        raise AssertionError("left-deep scaffold tree")
    independent = tree_cert(expected_tree, prefix, d, k)
    if candidate_tree_cert != independent:
        raise AssertionError("tree boundary certificate")
    if not independent["all_nonroot_edges_width_le_3k"]:
        raise AssertionError("accepted scaffold exceeds 3k")
    candidate_edges = {tuple(schedule[int(i)] for i in e["left_leaf_ids"]): e for e in rebuilt["candidate_edges"]}
    covers = {tuple(e["covered_factor_ids"]): e for e in independent["edge_certificates"]}
    matched = 0
    for prefix_len in range(1, len(order_ids)):
        key_order = tuple(order_ids[:prefix_len])
        key_cover = tuple(sorted(key_order))
        if key_order not in candidate_edges or key_cover not in covers:
            raise AssertionError("scaffold prefix edge missing from binary tree")
        if int(candidate_edges[key_order]["width"]) != int(covers[key_cover]["width"]):
            raise AssertionError("scaffold/tree boundary disagreement")
        matched += 1
    if matched != len(rebuilt["candidate_edges"]):
        raise AssertionError("not all B4.2 candidate edges rebound")


def verify_round_bytes(record: dict) -> int:
    nested = {
        "scaffold_witness": record.get("scaffold_witness"),
        "b5_1": record.get("b5_1_artifact"),
        "b5_2a": record.get("b5_2a_artifact"),
        "b5_2b": record.get("b5_2b_artifact"),
        "b5_3": record.get("b5_3_artifact"),
    }
    if "b5_4_artifact" in record:
        nested["b5_4"] = record.get("b5_4_artifact")
    expected = {key: artifact_bytes(value) for key, value in nested.items()}
    if record["artifact_byte_counts"] != expected or int(record["round_certificate_bytes"]) != sum(expected.values()):
        raise AssertionError("round certificate byte ledger")
    return sum(expected.values())


def verify(candidate: dict, raw: dict, spec: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_IMPLEMENTATION_CANDIDATE_NOT_ADMITTED":
        raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or candidate.get("semantic_digest") != dg(candidate.get("proof_payload")):
        raise AssertionError("candidate digest")
    p = candidate["proof_payload"]
    d, k, factors, order, runtime_caps, phase_a_caps, max_rounds = parse_raw(raw)
    if p["ambient_dim"] != d or p["k"] != k or p["canonical_factor_catalog"] != factors or p["input_order"] != order:
        raise AssertionError("global input identity")
    if p["runtime_caps"] != runtime_caps or p["phase_a_caps"] != phase_a_caps or p["max_rounds"] != max_rounds:
        raise AssertionError("cap identity")
    if p["normal_space_role"] != spec["input_contract"]["normal_space_role"] or p["preprocessing_implemented"] is not False or p["local_2k_negative_certificate_implemented"] is not False:
        raise AssertionError("preprocessing/local 2k ceiling")
    if p["strict_boundary"] != spec["strict_boundary"]:
        raise AssertionError("strict boundary")
    policy = p["authority_policy"]
    if policy != {"b4_2_scaffold_is_construction_witness_only": True, "tree_boundaries_independently_recomputed": True, "b5_3_no_layout_used_as_c047_unsat_premise": False, "strict_prefix_negative_requires_deletion_monotonicity": True, "capability_open_never_promotes": True}:
        raise AssertionError("authority policy")

    by = fmap(factors)
    rounds = p["rounds"]
    completed_expected = 0
    previous_layout: list[str] | None = None
    previous_digest: str | None = None
    global_work: dict[str, int] = {}
    total_bytes = 0
    stopped = False
    terminal_expected: dict | None = None

    for r in range(1, len(order) + 1):
        if max_rounds is not None and completed_expected >= max_rounds:
            terminal_expected = {"terminal_class": "OPEN_ORCHESTRATOR_ROUND_CAP", "terminal_round_index": r, "open_reason": {"observed_next_round": r, "max_rounds": max_rounds}, "full_discovery_no_layout_at_cap": False, "c047_result": "NOT_ESTABLISHED"}
            stopped = True
            break
        if completed_expected >= len(rounds):
            # A pre-B5.1 local/scaffold OPEN has no committed round record in v1.
            prefix_ids = order[:r]
            new_id = prefix_ids[-1] if r > 1 else None
            if r > 1 and len(xor_basis(by[new_id]["normal_space"], d)) > 2 * k:
                terminal_expected = {"terminal_class": "OPEN_LOCAL_2K_CERTIFICATE_REQUIRED", "terminal_round_index": r, "open_reason": {"new_factor_id": new_id, "observed_discovery_dimension": len(xor_basis(by[new_id]["normal_space"], d)), "two_k_cap": 2 * k, "local_negative_certificate_implemented": False}, "full_discovery_no_layout_at_cap": False, "c047_result": "NOT_ESTABLISHED"}
                stopped = True
                break
            if r > 1 and previous_layout is not None:
                prefix = [dict(by[fid]) for fid in prefix_ids]
                schedule = [str(x["id"]) for x in prefix]
                local = {fid: i for i, fid in enumerate(schedule)}
                rebuilt = b42.scaffold([tuple(x["normal_space"]) for x in prefix], [local[fid] for fid in previous_layout], len(prefix)-1, d, k, [x.get("affine_offset") for x in prefix])
                order_ids = [schedule[int(i)] for i in rebuilt["scaffold_order"]]
                t = left_deep(order_ids, r)
                tc = tree_cert(t, prefix, d, k)
                if not tc["all_nonroot_edges_width_le_3k"]:
                    terminal_expected = {"terminal_class": "OPEN_3K_SCAFFOLD_OR_VERIFICATION", "terminal_round_index": r, "open_reason": {"maximum_nonroot_edge_boundary_dimension": tc["maximum_nonroot_edge_boundary_dimension"], "three_k_cap": 3*k, "scaffold_semantic_digest": rebuilt.get("semantic_digest")}, "full_discovery_no_layout_at_cap": False, "c047_result": "NOT_ESTABLISHED"}
                    stopped = True
                    break
            raise AssertionError("missing committed round record")

        rec = rounds[completed_expected]
        prefix_ids = order[:r]
        prefix = [dict(by[fid]) for fid in prefix_ids]
        if rec["round_index"] != r or rec["prefix_factor_ids"] != prefix_ids:
            raise AssertionError("round subject")
        if rec["previous_verified_layout_digest"] != previous_digest:
            raise AssertionError("previous layout digest")

        if r == 1:
            tree = left_deep(prefix_ids, r)
            tc = tree_cert(tree, prefix, d, k)
            if rec["scaffold_witness"] is not None or rec["tree"] != tree or rec["tree_boundary_certificate"] != tc:
                raise AssertionError("base round tree")
            if rec["new_factor_id_or_base"] != "BASE":
                raise AssertionError("base round marker")
        else:
            if previous_layout is None or sorted(previous_layout) != sorted(prefix_ids[:-1]):
                raise AssertionError("previous verified layout availability")
            new_id = prefix_ids[-1]
            if rec["new_factor_id_or_base"] != new_id:
                raise AssertionError("new factor identity")
            if len(xor_basis(by[new_id]["normal_space"], d)) > 2 * k:
                raise AssertionError("round committed after missing local 2k certificate")
            schedule = [str(x["id"]) for x in prefix]
            local = {fid: i for i, fid in enumerate(schedule)}
            rebuilt = b42.scaffold([tuple(x["normal_space"]) for x in prefix], [local[fid] for fid in previous_layout], len(prefix)-1, d, k, [x.get("affine_offset") for x in prefix])
            tree_order = [schedule[int(i)] for i in rebuilt["scaffold_order"]]
            tree = left_deep(tree_order, r)
            tc = tree_cert(tree, prefix, d, k)
            verify_scaffold(rec["scaffold_witness"], prefix, previous_layout, d, k, tree, rec["tree_boundary_certificate"])
            if rec["tree"] != tree or rec["tree_boundary_certificate"] != tc:
                raise AssertionError("scaffold tree")

        rr = round_raw(prefix, tree, d, k, runtime_caps)
        b51 = rec["b5_1_artifact"]
        closed = b51v.verify(b51, rr, load(B51_SPEC))
        for key, value in b51["proof_payload"].get("global_work_ledger", {}).items():
            if isinstance(value, int):
                global_work[key] = global_work.get(key, 0) + value

        if not closed:
            if rec["round_terminal_class"] != "OPEN_B5_1_RUNTIME_CAPABILITY" or rec["b5_2a_artifact"] is not None or rec["b5_2b_artifact"] is not None or rec["b5_3_artifact"] is not None:
                raise AssertionError("B5.1 OPEN round promotion")
            terminal_expected = {"terminal_class": "OPEN_B5_1_RUNTIME_CAPABILITY", "terminal_round_index": r, "open_reason": b51["proof_payload"]["open_reason"], "full_discovery_no_layout_at_cap": False, "c047_result": "NOT_ESTABLISHED"}
            total_bytes += verify_round_bytes(rec)
            completed_expected += 1
            stopped = True
            break

        root_count = int(b51["proof_payload"]["root_entry_count_if_closed"])
        if root_count == 0:
            if rec["b5_2a_artifact"] is not None or rec["b5_2b_artifact"] is not None or rec["b5_3_artifact"] is None:
                raise AssertionError("negative branch shape")
            neg = rec["b5_3_artifact"]
            b53v.verify(neg, load(B53_SPEC), b51, load(B5_CONTRACT_RECEIPT), load(B51_RECEIPT), load(COMPOSITION_AUDIT), load(O7_AUDIT), load(B52B_RECEIPT))
            if neg["proof_payload"]["candidate_no_layout_at_cap"] is not True:
                raise AssertionError("B5.3 negative result")
            if r < len(order):
                verify_monotonicity(rec.get("strict_prefix_deletion_monotonicity"), prefix_ids, order, k)
                tclass = "STRICT_PREFIX_NO_LAYOUT_AT_CAP_WITH_DELETION_MONOTONICITY"
                bridge = rec["strict_prefix_deletion_monotonicity"]
            else:
                if rec.get("strict_prefix_deletion_monotonicity") is not None:
                    raise AssertionError("full negative has strict-prefix bridge")
                tclass = "FULL_INPUT_NO_LAYOUT_AT_CAP"
                bridge = None
            if rec["round_terminal_class"] != tclass:
                raise AssertionError("negative terminal class")
            terminal_expected = {"terminal_class": tclass, "terminal_round_index": r, "b5_3_semantic_digest": neg["semantic_digest"], "strict_prefix_deletion_monotonicity": bridge, "full_discovery_no_layout_at_cap": True, "affine_instance_unsat": "NOT_ESTABLISHED", "c047_result": "NOT_ESTABLISHED"}
            total_bytes += verify_round_bytes(rec)
            completed_expected += 1
            stopped = True
            break

        carrier, layout = rec["b5_2a_artifact"], rec["b5_2b_artifact"]
        if carrier is None or layout is None or rec["b5_3_artifact"] is not None:
            raise AssertionError("positive branch shape")
        roots = b52av.verify_v11(carrier, rr, b51, load(B52A_AMENDMENT))
        if roots != root_count:
            raise AssertionError("carrier root count")
        expected_layout = b52bv.verify(layout, load(B52B_SPEC), rr, b51, carrier)
        if expected_layout["empty"]:
            raise AssertionError("positive branch reconstructed empty")
        next_order = [str(x) for x in expected_layout["order"]]
        if sorted(next_order) != sorted(prefix_ids) or len(set(next_order)) != len(next_order) or int(expected_layout["max_width"]) > k:
            raise AssertionError("next layout")
        vnext = rec["verified_next_layout"]
        if vnext != {"factor_order_ids": next_order, "maximum_cut_width": expected_layout["max_width"], "semantic_digest": layout["semantic_digest"]}:
            raise AssertionError("stored next layout")

        if r < len(order):
            if rec["round_terminal_class"] != "POSITIVE_PREFIX_LAYOUT" or "b5_4_artifact" in rec:
                raise AssertionError("prefix positive terminal")
            previous_layout, previous_digest = next_order, layout["semantic_digest"]
            total_bytes += verify_round_bytes(rec)
            completed_expected += 1
            continue

        if rec["round_terminal_class"].startswith("STRICT_PREFIX"):
            raise AssertionError("B5.4 on strict prefix")
        c047 = rec.get("b5_4_artifact")
        if c047 is None:
            raise AssertionError("full positive missing B5.4")
        b54_expected = b54v.verify(c047, load(B54_SPEC), rr, b51, carrier, layout, load(B52A_AMENDMENT), load(B52B_SPEC), load(B52B_RECEIPT), load(B53_RECEIPT), phase_a_caps)
        p54 = c047["proof_payload"]
        if b54_expected["c047_result"] != p54["c047_result"]:
            raise AssertionError("B5.4 verifier result")
        rebound, cres = str(p54["rebound_status"]), str(p54["c047_result"])
        tclass = "FULL_INPUT_C047_" + cres if rebound == "PHASE_A_C047_REPLAY_COMPLETED" and cres in {"SAT", "UNSAT"} else (rebound if rebound.startswith("OPEN_") else "OPEN_FINAL_B5_4_" + rebound)
        if rec["round_terminal_class"] != tclass:
            raise AssertionError("final positive terminal class")
        terminal_expected = {"terminal_class": tclass, "terminal_round_index": r, "b5_4_semantic_digest": c047["semantic_digest"], "verified_full_input_layout_digest": layout["semantic_digest"], "full_discovery_no_layout_at_cap": False, "c047_result": cres, "historical_phase_a_verifier_pass": p54.get("historical_phase_a_verifier_pass", False)}
        total_bytes += verify_round_bytes(rec)
        completed_expected += 1
        stopped = True
        break

    if not stopped or terminal_expected is None:
        raise AssertionError("no terminal")
    if completed_expected != len(rounds):
        raise AssertionError("extra/missing round records")
    if p["terminal"] != terminal_expected:
        raise AssertionError("terminal record")

    ledger = p["global_ledger"]
    expected_attempted = len(rounds) + (1 if terminal_expected["terminal_class"] in {"OPEN_LOCAL_2K_CERTIFICATE_REQUIRED", "OPEN_3K_SCAFFOLD_OR_VERIFICATION", "OPEN_ORCHESTRATOR_ROUND_CAP"} else 0)
    if ledger != {"attempted_round_count": expected_attempted, "completed_round_count": len(rounds), "round_indices": [r["round_index"] for r in rounds], "sum_b5_1_global_work_ledger": global_work, "sum_serialized_round_certificate_bytes": total_bytes, "failed_join_refinement_work_preserved_inside_b5_1_ledgers": True, "work_counter_reset_between_rounds": False}:
        raise AssertionError("global ledger")
    if p["terminal_promotion_policy"] != {"open_promoted": False, "b5_3_no_layout_used_as_c047_unsat_premise": False, "strict_prefix_negative_requires_deletion_monotonicity": True}:
        raise AssertionError("terminal promotion policy")
    return {"terminal_class": terminal_expected["terminal_class"], "round_count": len(rounds), "c047_result": terminal_expected.get("c047_result"), "full_discovery_no_layout_at_cap": terminal_expected.get("full_discovery_no_layout_at_cap", False)}


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite(subjects: dict[str, tuple[dict, dict]], spec: dict) -> tuple[int, int]:
    attacks: list[tuple[str, str, Callable[[dict], None]]] = []
    def add(name: str, subject: str, mutation: Callable[[dict], None]) -> None:
        attacks.append((name, subject, mutation))

    add("T01_INPUT_ORDER", "sat", lambda p: p["input_order"].__setitem__(0, p["input_order"][-1]))
    add("T02_DUP_FACTOR", "sat", lambda p: p["canonical_factor_catalog"].append(copy.deepcopy(p["canonical_factor_catalog"][0])))
    add("T03_GEOMETRIC_DEDUP", "dup", lambda p: p["canonical_factor_catalog"].pop())
    add("T04_PREVIOUS_LAYOUT", "sat", lambda p: p["rounds"][1].__setitem__("previous_verified_layout_digest", "0"*64))
    add("T05_PREVIOUS_WIDTH", "sat", lambda p: p["rounds"][1]["verified_next_layout"].__setitem__("maximum_cut_width", 999))
    add("T06_LOCAL_2K_PROMOTION", "local2k", lambda p: p["terminal"].update({"terminal_class":"FULL_INPUT_NO_LAYOUT_AT_CAP","full_discovery_no_layout_at_cap":True}))
    add("T07_SCAFFOLD_3K", "sat", lambda p: p["rounds"][1]["tree_boundary_certificate"].__setitem__("maximum_nonroot_edge_boundary_dimension", 999))
    add("T08_DROP_TREE_LEAF", "sat", lambda p: p["rounds"][1]["tree"]["nodes"].pop(0))
    add("T09_B51_OPEN_PROMOTION", "b5open", lambda p: p["terminal"].__setitem__("terminal_class", "FULL_INPUT_C047_SAT"))
    add("T10_B51_DIGEST", "sat", lambda p: p["rounds"][0]["b5_1_artifact"].__setitem__("semantic_digest", "0"*64))
    add("T11_CARRIER", "sat", lambda p: p["rounds"][1]["b5_2a_artifact"].__setitem__("semantic_digest", "0"*64))
    add("T12_LAYOUT", "sat", lambda p: p["rounds"][1]["b5_2b_artifact"]["proof_payload"]["factor_order_ids"].reverse())
    add("T13_UNVERIFIED_NEXT", "sat", lambda p: p["rounds"][1]["verified_next_layout"].__setitem__("semantic_digest", "0"*64))
    add("T14_DROP_MONOTONICITY", "prefixneg", lambda p: p["rounds"][-1].__setitem__("strict_prefix_deletion_monotonicity", None))
    add("T15_REVERSE_MONOTONICITY", "prefixneg", lambda p: p["rounds"][-1]["strict_prefix_deletion_monotonicity"].__setitem__("contrapositive", "FULL_NO_LAYOUT_IMPLIES_PREFIX_NO_LAYOUT"))
    add("T16_B53_TO_C047_UNSAT", "prefixneg", lambda p: p["terminal"].__setitem__("c047_result", "UNSAT"))
    add("T17_B54_OPEN_PROMOTION", "affineopen", lambda p: p["terminal"].update({"terminal_class":"FULL_INPUT_C047_SAT","c047_result":"SAT"}))
    add("T18_ROUND_CAP_PROMOTION", "roundcap", lambda p: p["terminal"].__setitem__("terminal_class", "FULL_INPUT_NO_LAYOUT_AT_CAP"))
    add("T19_DROP_COMPLETED_ON_OPEN", "roundcap", lambda p: p["rounds"].pop())
    add("T20_LEDGER_RESET", "sat", lambda p: p["global_ledger"].__setitem__("work_counter_reset_between_rounds", True))
    add("T21_CERT_BYTES", "sat", lambda p: p["global_ledger"].__setitem__("sum_serialized_round_certificate_bytes", 0))
    add("T22_B54_ON_PREFIX", "prefixneg", lambda p: p["rounds"][-1].__setitem__("b5_4_artifact", copy.deepcopy(subjects["sat"][0]["proof_payload"]["rounds"][-1]["b5_4_artifact"])))
    add("T23_AFFINE_IDENTITY", "sat", lambda p: p["canonical_factor_catalog"][0].__setitem__("affine_offset", {"tamper":True}))
    add("T24_TOTALITY", "sat", lambda p: p["strict_boundary"].__setitem__("all_input_termination", "ESTABLISHED"))
    add("T25_POLYTIME", "sat", lambda p: p["strict_boundary"].__setitem__("polynomial_runtime", "ESTABLISHED"))
    add("T26_B5_COMPLETE", "sat", lambda p: p["strict_boundary"].__setitem__("b5_complete", True))
    add("T27_P_VS_NP", "sat", lambda p: p["strict_boundary"].__setitem__("p_vs_np", "CLOSED"))

    rejected = 0
    for name, subject_name, mutate in attacks:
        original, raw = subjects[subject_name]
        c = copy.deepcopy(original)
        mutate(c["proof_payload"])
        repair(c)
        try:
            verify(c, raw, spec)
        except Exception:
            rejected += 1
            print(name + " = REJECTED")
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    args = ap.parse_args()
    spec, raw, candidate = load(args.spec), load(args.input), load(args.candidate)
    result = verify(candidate, raw, spec)
    print("JANUS_B5_ITERATIVE_COMPRESSION_ORCHESTRATOR_INDEPENDENT_VERIFIER = PASS")
    print("TERMINAL_CLASS =", result["terminal_class"])
    print("ROUND_COUNT =", result["round_count"])
    print("C047_RESULT =", result["c047_result"])
    print("FULL_DISCOVERY_NO_LAYOUT_AT_CAP =", str(result["full_discovery_no_layout_at_cap"]).upper())
    print("B5_3_NO_LAYOUT_USED_AS_C047_UNSAT_PREMISE = FALSE")
    print("OPEN_PROMOTION = FALSE")
    print("PREPROCESSING_IMPLEMENTED = FALSE")
    print("LOCAL_2K_NEGATIVE_CERTIFICATE_IMPLEMENTED = FALSE")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
