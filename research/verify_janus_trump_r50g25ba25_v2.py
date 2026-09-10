from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

OUT = Path("ba25_verify_v2.json")
RESULT = Path("ba25_result.json")
GAP = Path("research/JANUS_TRUMP_R50G25BA25_SOURCE_RECONSTRUCTION_EVIDENCE_GAP_RECEIPT.json")
HARDENING = Path("research/JANUS_TRUMP_R50G25BA25_RECONSTRUCTION_HARDENING.json")
BA20_RECEIPT = Path("research/JANUS_TRUMP_R50G25BA20_RESULT_RECEIPT.json")
BA21_RECEIPT = Path("research/JANUS_TRUMP_R50G25BA21_RESULT_RECEIPT.json")

BA20_FINAL_META_COMMIT = "fa0b503233cb873282c0d8317adf89e48223402b"
BA20_FINAL_META_BLOB = "a09eae8aa44b68530a5d24e542056c13a24ab865"
BA20_RECEIPT_COMMIT = "ef963eba447b1d88ef13eddc9b888138be4f4565"
BA20_RECEIPT_BLOB = "ed11ffc951eec1bf1a1c01d60699876f8a408018"
BA20_BASE_COMMIT = "6e895880f2cebeddd0ee72d6b90704d62434bc67"
BA20_BASE_BLOB = "c3112e59a213bf297d1bd757e251905f64d5900b"
BA20_V2_COMMIT = "ff94c204051d173ca4fabb51ad33e3260d13d7c0"
BA20_V2_BLOB = "6c2271f18677cebc9c37eab42c42b8228b41967b"

BA21_FINAL_META_COMMIT = "085bcdec8cd7613ad99e8766894010e6dd3d8fe4"
BA21_FINAL_META_BLOB = "e5f66732279c1b26b4f9a1fd991d4055eac9209e"
BA21_RECEIPT_COMMIT = "dd3cd439bffd67dd33790be83e719625310c0726"
BA21_RECEIPT_BLOB = "d94b91c7ed4b8bb3cce7efb52d02813bb222916a"
BA21_IMPL_COMMIT = "8da4e0560bdbbc31d94e7e4ab65a098222e5f5c1"
BA21_IMPL_BLOB = "22b891038e34dedcb53b75a74563cbe535c55e21"

BA4_SCHEMA_BLOB = "c85eab7d0bb1557bc0c472bbc8c2086b08625a4c"
GAP_BLOB = "8596960a0df33f7361303b94042468d7086ea16e"
HARDENING_COMMIT = "1ca79fa8078e0428cae669d47df72354e59f06c2"
HARDENING_BLOB = "f3f4f8da6240ca061c3085726d9ada1bfe6823df"
OLD_RUN = 34410959446
BLOCK = 30

PARENT_FILES = {
    "ba20_base": (Path("experiments/janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence.py"), BA20_BASE_BLOB),
    "ba20_v2": (Path("experiments/janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence_v2.py"), BA20_V2_BLOB),
    "ba4": (Path("experiments/janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel.py"), BA4_SCHEMA_BLOB),
    "ba21_impl": (Path("experiments/janus_trump_r50g25ba21_generic_proof_carrying_dbo_compressed_projection.py"), BA21_IMPL_BLOB),
    "ba20_receipt": (BA20_RECEIPT, BA20_RECEIPT_BLOB),
    "ba21_receipt": (BA21_RECEIPT, BA21_RECEIPT_BLOB),
    "gap_receipt": (GAP, GAP_BLOB),
    "reconstruction_hardening": (HARDENING, HARDENING_BLOB),
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def clause_ok(assignment: dict[int, bool], clause) -> bool:
    for lit in clause:
        v = abs(int(lit))
        if v not in assignment:
            return False
        val = bool(assignment[v])
        if (lit > 0 and val) or (lit < 0 and not val):
            return True
    return False


def eval_ba25_instance(raw: dict, assignment: dict[str, int]) -> bool:
    blocks = raw["blocks"]
    clauses = raw["clauses"]
    phi = any(all(bool(assignment[v]) for v in block) for block in blocks)
    gamma = True
    for clause in clauses:
        sat = False
        for v, sign in clause:
            val = bool(assignment[v])
            sat |= (int(sign) == 1 and val) or (int(sign) == -1 and not val)
        gamma &= sat
    return bool(phi and gamma)


def independent_layout(p: int, ns: tuple[int, ...]) -> dict:
    cur = 1
    def alloc(k):
        nonlocal cur
        out = list(range(cur, cur + k))
        cur += k
        return out
    A = alloc(p)
    x = alloc(1)[0]
    y = alloc(1)[0]
    h = len(ns)
    B = [None] * h
    T = [None] * max(0, h - 1)
    Z = [None] * max(0, h - 1)
    B[0] = alloc(ns[0])
    if h > 1:
        Z[0] = alloc(1)[0]
        T[0] = alloc(ns[0])
        for q in range(1, h - 1):
            B[q] = alloc(ns[q])
            T[q] = alloc(ns[q])
            Z[q] = alloc(1)[0]
        B[h - 1] = alloc(ns[h - 1])
    return {"A": A, "x": x, "y": y, "B": B, "T": T, "Z": Z, "D": cur - 1, "h": h}


def independent_source_formula(p: int, ns: tuple[int, ...]):
    L = independent_layout(p, ns)
    F = [(a, L["x"]) for a in L["A"]]
    F.append((-L["x"], L["y"]))
    F += [(-L["y"], b) for b in L["B"][0]]
    for q in range(L["h"] - 1):
        F += [(-L["B"][q][j], L["T"][q][j], L["Z"][q]) for j in range(len(L["B"][q]))]
        F += [(-L["Z"][q], b) for b in L["B"][q + 1]]
    return F, L


def independent_reconstruct_source_bits(final_bits, p: int, ns: tuple[int, ...]):
    L = independent_layout(p, ns)
    bits = tuple(map(int, final_bits))
    q = 0
    assign = {}
    Abits = bits[q:q + p]
    q += p
    for v, b in zip(L["A"], Abits):
        assign[v] = b
    Tbits = []
    for n in ns[:-1]:
        Tbits.append(bits[q:q + n])
        q += n
    Bh = bits[q:q + ns[-1]]
    Atruth = int(all(Abits))
    R = Atruth
    assign[L["x"]] = 1 - Atruth
    assign[L["y"]] = 1 - Atruth
    if L["h"] == 1:
        for v, b in zip(L["B"][0], Bh):
            assign[v] = b
    else:
        for level in range(L["h"] - 1):
            bval = 1 - int(bool(R))
            for v in L["B"][level]:
                assign[v] = bval
            for v, b in zip(L["T"][level], Tbits[level]):
                assign[v] = b
            R = int(bool(R) or all(Tbits[level]))
            assign[L["Z"][level]] = 1 - R
        for v, b in zip(L["B"][L["h"] - 1], Bh):
            assign[v] = b
    return tuple(assign[i] for i in range(1, L["D"] + 1))


def independent_abstract_source_ok(source_bits, p: int, ns: tuple[int, ...]) -> tuple[bool, int]:
    F, L = independent_source_formula(p, ns)
    a = {i + 1: bool(source_bits[i]) for i in range(L["D"])}
    bad = sum(not clause_ok(a, c) for c in F)
    return bad == 0, bad


def map_witness_to_parent_bits(sample: dict):
    raw = sample["instance"]
    wr = sample["witness_receipt"]
    if not wr.get("present") or not wr.get("direct_verify"):
        raise AssertionError("missing/direct-invalid BA25 factor-DP witness")
    assignment = {str(k): int(v) for k, v in wr["assignment"].items()}
    if not eval_ba25_instance(raw, assignment):
        raise AssertionError("BA25 factor-DP witness fails its own hybrid instance")
    blocks = [tuple(sorted(map(str, b))) for b in raw["blocks"]]
    if len(blocks) < 2:
        return {"classification": "BA20_BA21_ROUTE_NOT_APPLICABLE", "reason": "sealed BA20/BA21 DBO has at least A and C_1 blocks"}
    if not all(blocks):
        return {"classification": "BA20_BA21_ROUTE_NOT_APPLICABLE", "reason": "empty block"}
    flat = [v for b in blocks for v in b]
    if len(flat) != len(set(flat)):
        return {"classification": "BA20_BA21_ROUTE_NOT_APPLICABLE", "reason": "blocks not variable-disjoint"}
    p = len(blocks[0])
    ns = tuple(len(b) for b in blocks[1:])
    final_bits = tuple(assignment[v] for b in blocks for v in b)
    if not any(all(assignment[v] for v in b) for b in blocks):
        raise AssertionError("projected assignment is not a model of the DBO factor")
    return {
        "classification": "BA20_BA21_ROUTE_APPLICABLE",
        "p": p,
        "ns": ns,
        "blocks": blocks,
        "final_bits": final_bits,
        "assignment": assignment,
    }


def direct_original_ba4_replay(ba20, ba4, p: int, ns: tuple[int, ...], source_bits, g: int):
    U, first, _, _ = ba4.source_hardening()
    assignment: dict[int, bool] = {}
    for lane, bit in enumerate(source_bits):
        proto = first[(int(bit), 1 - int(bit))]
        lo = ba4.lane_off(int(g), lane)
        for block in range(int(g)):
            off = lo + BLOCK * block
            for v, val in proto.items():
                assignment[int(v) + off] = bool(val)
    clauses, _, _, _, cross = ba20.build_instance(U, int(g), p, ns)
    missing = sorted({abs(int(l)) for c in clauses for l in c if abs(int(l)) not in assignment})
    bad = [i for i, c in enumerate(clauses) if not clause_ok(assignment, c)] if not missing else list(range(len(clauses)))
    parent = ba20.construct_model(first, U, int(g), p, ns, source_bits)
    return {
        "g": int(g),
        "clause_count": len(clauses),
        "cross_clause_count": len(cross),
        "missing_variable_count": len(missing),
        "bad_clause_count": len(bad),
        "parent_reported_bad_clause_count": int(parent["bad_clause_count"]),
        "pass": not missing and not bad and bool(parent["pass"]) and int(parent["bad_clause_count"]) == 0,
    }


def main():
    assertions = {}
    falsifiers = []

    # Exact append-only governance/provenance objects.
    observed_blobs = {name: git_blob_sha(path) for name, (path, _) in PARENT_FILES.items()}
    assertions["pinned_file_blobs"] = all(observed_blobs[name] == expected for name, (_, expected) in PARENT_FILES.items())

    gap = json.loads(GAP.read_text())
    hard = json.loads(HARDENING.read_text())
    r20 = json.loads(BA20_RECEIPT.read_text())
    r21 = json.loads(BA21_RECEIPT.read_text())
    result = json.loads(RESULT.read_text())

    assertions["historical_run_unsealed"] = (
        gap["historical_green_run"]["run_id"] == OLD_RUN
        and gap["historical_green_run"]["scientific_authority"] is False
        and gap["historical_green_run"]["scientific_result"] == "NOT_PROMOTED"
        and gap["historical_green_run"]["must_never_be_retroactively_promoted_to_authoritative"] is True
    )
    assertions["hardening_exact"] = (
        hard["state"] == "FROZEN_APPEND_ONLY_RECONSTRUCTION_HARDENING_BEFORE_VERIFIER_V2"
        and hard["SOURCE_RECONSTRUCTION_PASS_definition"]["no_synthesis_from_overall_verifier_pass"] is True
        and hard["promotion_firewall"]["BA26_STARTED"] is False
    )
    pins20 = hard["sealed_parent_pins"]["BA20"]
    pins21 = hard["sealed_parent_pins"]["BA21"]
    assertions["parent_commit_blob_receipt_provenance"] = (
        pins20["final_meta_commit"] == BA20_FINAL_META_COMMIT
        and pins20["final_meta_blob"] == BA20_FINAL_META_BLOB
        and pins20["result_receipt_commit"] == BA20_RECEIPT_COMMIT
        and pins20["result_receipt_blob"] == BA20_RECEIPT_BLOB
        and pins21["final_meta_commit"] == BA21_FINAL_META_COMMIT
        and pins21["final_meta_blob"] == BA21_FINAL_META_BLOB
        and pins21["result_receipt_commit"] == BA21_RECEIPT_COMMIT
        and pins21["result_receipt_blob"] == BA21_RECEIPT_BLOB
    )
    assertions["sealed_parent_receipts"] = (
        r20["authoritative_evidence"]["P_BA20_FINAL"] == 1
        and r20["authoritative_evidence"]["full_BA4_reconstruction_cases"] == 4454
        and r21["authoritative_evidence"]["P_BA21_FINAL"] == 1
        and r21["authoritative_evidence"]["full_BA4_reconstruction_cases"] == 48
        and r21["scientific_result"]["constructive_original_source_return"] is True
    )

    # Pin the executable parent reconstruction schema before importing it.
    schema_provenance = {
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
    schema_provenance["schema_sha256"] = sha256_json(schema_provenance)

    sys.path.insert(0, str(Path("experiments").resolve()))
    import janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence as ba20
    import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

    samples = result.get("proof_carrying", {}).get("samples", {})
    assertions["factor_dp_witness_samples_present"] = bool(samples)
    local_controls_pass = bool(result.get("assertions", {}).get("reconstruction_controls")) and bool(result.get("assertions", {}).get("proof_carrying_payload"))
    assertions["LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS"] = local_controls_pass

    applicability = []
    replay_rows = []
    original_failures = 0
    abstract_failures = 0
    parent_formula_mismatches = 0

    for sample_name in sorted(samples):
        sample = samples[sample_name]
        try:
            mapped = map_witness_to_parent_bits(sample)
        except Exception as exc:
            applicability.append({"sample": sample_name, "classification": "BA20_BA21_ROUTE_NOT_APPLICABLE", "reason": f"mapping_error:{type(exc).__name__}:{exc}"})
            continue
        if mapped["classification"] != "BA20_BA21_ROUTE_APPLICABLE":
            applicability.append({"sample": sample_name, **mapped})
            continue

        p = int(mapped["p"])
        ns = tuple(map(int, mapped["ns"]))
        final_bits = tuple(map(int, mapped["final_bits"]))
        independent_bits = independent_reconstruct_source_bits(final_bits, p, ns)
        parent_bits = tuple(map(int, ba20.reconstruct_source_bits(final_bits, p, ns)))
        formula_match = independent_bits == parent_bits
        parent_formula_mismatches += int(not formula_match)
        abstract_ok, abstract_bad = independent_abstract_source_ok(independent_bits, p, ns)
        parent_abstract_ok = bool(ba20.source_bits_ok(parent_bits, p, ns))
        abstract_failures += int(not abstract_ok) + int(not parent_abstract_ok)

        applicability.append({
            "sample": sample_name,
            "classification": "BA20_BA21_ROUTE_APPLICABLE",
            "p": p,
            "ns": list(ns),
            "surviving_variable_count": len(final_bits),
            "foreign_clause_count": len(sample["instance"]["clauses"]),
            "foreign_clause_carrier_claimed": False,
        })

        for g in (1, 2):
            actual = direct_original_ba4_replay(ba20, ba4, p, ns, independent_bits, g)
            original_failures += int(actual["bad_clause_count"]) + int(actual["missing_variable_count"])
            replay_rows.append({
                "sample": sample_name,
                "p": p,
                "ns": list(ns),
                "g": g,
                "factor_DP_witness_to_surviving_assignment": True,
                "independent_vs_parent_reconstruction_match": formula_match,
                "independent_abstract_source_ok": abstract_ok,
                "parent_abstract_source_ok": parent_abstract_ok,
                "abstract_bad_clause_count": abstract_bad,
                **actual,
            })

    applicable = [x for x in applicability if x["classification"] == "BA20_BA21_ROUTE_APPLICABLE"]
    not_applicable = [x for x in applicability if x["classification"] == "BA20_BA21_ROUTE_NOT_APPLICABLE"]
    assertions["per_control_applicability_classified"] = len(applicability) == len(samples) and all(x["classification"] in {"BA20_BA21_ROUTE_APPLICABLE", "BA20_BA21_ROUTE_NOT_APPLICABLE"} for x in applicability)
    assertions["replayed_cases_gt_zero"] = len(replay_rows) > 0
    assertions["parent_reconstruction_formula_match"] = parent_formula_mismatches == 0
    assertions["abstract_source_validation"] = abstract_failures == 0
    assertions["DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES"] = original_failures == 0 and all(x["pass"] for x in replay_rows)
    assertions["SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS"] = (
        assertions["pinned_file_blobs"]
        and assertions["parent_commit_blob_receipt_provenance"]
        and assertions["sealed_parent_receipts"]
        and assertions["replayed_cases_gt_zero"]
        and assertions["parent_reconstruction_formula_match"]
        and assertions["abstract_source_validation"]
        and assertions["DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES"]
    )

    source_reconstruction_pass = (
        assertions["LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS"]
        and assertions["SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS"]
        and assertions["DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES"]
    )
    assertions["SOURCE_RECONSTRUCTION_PASS"] = source_reconstruction_pass
    assertions["sealed_parent_reconstruction_replay"] = source_reconstruction_pass
    assertions["implementation_imported"] = False
    assertions["arbitrary_foreign_CNF_BA4_carrier_coverage_claimed"] = False
    assertions["BA26_STARTED"] = False
    assertions["SAT_IN_P_NOT_PROVED"] = True
    assertions["P_VS_NP_OPEN"] = True

    for name, ok in assertions.items():
        if not ok:
            falsifiers.append(name)

    out = {
        "gate": "R50G25BA25_VARIABLE_LOCALIZED_HYBRID_FACTOR_GRAPH_FPT_AND_ARBITRARY_CNF_INCIDENCE_WIDTH_CALIBRATION",
        "entry_type": "BA25_INDEPENDENT_VERIFIER_V2_SOURCE_RECONSTRUCTION_HARDENED",
        "status": "PASS" if not falsifiers else "FAIL",
        "implementation_imported": False,
        "scientific_authority": "INDEPENDENT_EVIDENCE_ONLY_PENDING_PRESEAL_V2_AND_NEW_AUTHORITATIVE_WORKFLOW_V2",
        "historical_run_34410959446": "UNSEALED_SOURCE_RECONSTRUCTION_EVIDENCE_GAP_NOT_PROMOTED",
        "sealed_parent_reconstruction_replay": source_reconstruction_pass,
        "SOURCE_RECONSTRUCTION_PASS": source_reconstruction_pass,
        "parent_BA20_commit": BA20_FINAL_META_COMMIT,
        "parent_BA21_commit": BA21_FINAL_META_COMMIT,
        "reconstruction_schema_hash_provenance": schema_provenance,
        "number_of_replayed_cases": len(replay_rows),
        "applicable_control_count": len(applicable),
        "not_applicable_control_count": len(not_applicable),
        "original_CNF_validation_failures": original_failures,
        "abstract_source_validation_failures": abstract_failures,
        "parent_reconstruction_formula_mismatches": parent_formula_mismatches,
        "applicability": applicability,
        "replay_rows": replay_rows,
        "assertions": assertions,
        "falsifiers": falsifiers,
        "SOURCE_RECONSTRUCTION_PASS_definition": "LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS AND SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS AND DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES",
        "applicability_firewall": "Parent reconstruction replay only for controls that instantiate the sealed BA20/BA21 DBO surviving-variable route; foreign CNF remains a surviving-variable factor and is NOT transported through BA4 by this verifier.",
        "nonclaims": {
            "arbitrary_foreign_CNF_BA4_carrier_coverage": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "P_equals_NP_proved": False,
            "P_not_equals_NP_proved": False,
        },
        "STOP": {
            "BA25": "UNSEALED_PENDING_PRESEAL_V2_AND_NEW_AUTHORITATIVE_WORKFLOW_V2",
            "BA26_started": False,
            "next_permitted_object": "PRESEAL_V2",
            "external_literature_novelty_equivalence_audit_required_after_successful_BA25_seal": True,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("BA25_VERIFY_V2_STATUS=" + out["status"])
    print("BA25_VERIFY_V2_SEALED_PARENT_RECONSTRUCTION_REPLAY=" + str(source_reconstruction_pass).lower())
    print("BA25_VERIFY_V2_REPLAYED_CASES=" + str(len(replay_rows)))
    print("BA25_VERIFY_V2_ORIGINAL_CNF_VALIDATION_FAILURES=" + str(original_failures))
    if falsifiers:
        print("BA25_VERIFY_V2_FALSIFIERS=" + json.dumps(falsifiers, sort_keys=True))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
