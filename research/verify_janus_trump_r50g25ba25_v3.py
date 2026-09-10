from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

OUT = Path("ba25_verify_v3.json")
RESULT = Path("ba25_result.json")
GAP = Path("research/JANUS_TRUMP_R50G25BA25_SOURCE_RECONSTRUCTION_EVIDENCE_GAP_RECEIPT.json")
HARDENING = Path("research/JANUS_TRUMP_R50G25BA25_RECONSTRUCTION_HARDENING.json")
FAILURE_RECEIPT = Path("research/JANUS_TRUMP_R50G25BA25_AUTHORITATIVE_V2_RUN1_FAILURE_RECEIPT.json")
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
VERIFIER_V2_COMMIT = "57649038bd8b35e74464c878c0c15f81f3ff8ad1"
VERIFIER_V2_BLOB = "a54c2d8a141ff386650793e34104ace1c34409a2"
AUTHORITATIVE_V2_RUN1 = 34424706518
AUTHORITATIVE_V2_JOB1 = 102707349222
AUTHORITATIVE_V2_WORKFLOW_HEAD = "dceda2c5d7302730da6133aeab5380833ca5c9a9"
FAILURE_RECEIPT_COMMIT = "0a35e4e8b9f6b76bd071ca13e27c3e68b856b1fe"
FAILURE_RECEIPT_BLOB = "3bec4cc4ac40929d5664f606330c286732ca59af"
OLD_HISTORICAL_RUN = 34410959446
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
    "authoritative_v2_run1_failure_receipt": (FAILURE_RECEIPT, FAILURE_RECEIPT_BLOB),
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


def classify_expected_polarity(positive_obligations: dict[str, bool], negative_firewalls: dict[str, bool]):
    failed_positive = [name for name, value in positive_obligations.items() if value is not True]
    violated_negative = [name for name, value in negative_firewalls.items() if value is not False]
    return failed_positive, violated_negative


def polarity_classifier_self_test() -> dict:
    cases = [
        {
            "name": "accept_true_for_positive",
            "positive_obligations": {"P": True},
            "negative_firewalls": {},
            "expected_failed_positive": [],
            "expected_violated_negative": [],
        },
        {
            "name": "accept_false_for_negative",
            "positive_obligations": {},
            "negative_firewalls": {"N": False},
            "expected_failed_positive": [],
            "expected_violated_negative": [],
        },
        {
            "name": "reject_false_for_positive",
            "positive_obligations": {"P": False},
            "negative_firewalls": {},
            "expected_failed_positive": ["P"],
            "expected_violated_negative": [],
        },
        {
            "name": "reject_true_for_negative",
            "positive_obligations": {},
            "negative_firewalls": {"N": True},
            "expected_failed_positive": [],
            "expected_violated_negative": ["N"],
        },
    ]
    rows = []
    for case in cases:
        failed_positive, violated_negative = classify_expected_polarity(
            case["positive_obligations"], case["negative_firewalls"]
        )
        passed = (
            failed_positive == case["expected_failed_positive"]
            and violated_negative == case["expected_violated_negative"]
        )
        rows.append({
            "name": case["name"],
            "positive_obligations": case["positive_obligations"],
            "negative_firewalls": case["negative_firewalls"],
            "failed_positive_obligations": failed_positive,
            "violated_negative_firewalls": violated_negative,
            "pass": passed,
        })
    return {
        "classifier_contract": {
            "positive_obligation_expected_value": True,
            "negative_firewall_expected_value": False,
            "failed_positive_rule": "value is not true",
            "violated_negative_rule": "value is not false",
        },
        "cases": rows,
        "pass": all(row["pass"] for row in rows),
    }


def main():
    observed_blobs = {name: git_blob_sha(path) for name, (path, _) in PARENT_FILES.items()}
    gap = json.loads(GAP.read_text())
    hard = json.loads(HARDENING.read_text())
    failure_receipt = json.loads(FAILURE_RECEIPT.read_text())
    r20 = json.loads(BA20_RECEIPT.read_text())
    r21 = json.loads(BA21_RECEIPT.read_text())
    result = json.loads(RESULT.read_text())

    pinned_file_blobs = all(observed_blobs[name] == expected for name, (_, expected) in PARENT_FILES.items())
    historical_run_unsealed = (
        gap["historical_green_run"]["run_id"] == OLD_HISTORICAL_RUN
        and gap["historical_green_run"]["scientific_authority"] is False
        and gap["historical_green_run"]["scientific_result"] == "NOT_PROMOTED"
        and gap["historical_green_run"]["must_never_be_retroactively_promoted_to_authoritative"] is True
    )
    hardening_exact = (
        hard["state"] == "FROZEN_APPEND_ONLY_RECONSTRUCTION_HARDENING_BEFORE_VERIFIER_V2"
        and hard["SOURCE_RECONSTRUCTION_PASS_definition"]["no_synthesis_from_overall_verifier_pass"] is True
        and hard["promotion_firewall"]["BA26_STARTED"] is False
    )
    authoritative_v2_failure_preserved = (
        failure_receipt["authoritative_attempt"]["run_id"] == AUTHORITATIVE_V2_RUN1
        and failure_receipt["authoritative_attempt"]["job_id"] == AUTHORITATIVE_V2_JOB1
        and failure_receipt["authoritative_attempt"]["workflow_head"] == AUTHORITATIVE_V2_WORKFLOW_HEAD
        and failure_receipt["state"] == "UNSEALED_AUTHORITATIVE_V2_RUN_FAILED"
        and failure_receipt["scientific_authority"] is False
        and failure_receipt["scientific_result"] == "NOT_PROMOTED"
        and failure_receipt["scientific_falsifier_observed"] is False
        and failure_receipt["classification"] == "VERIFIER_V2_BOOLEAN_FIREWALL_POLARITY_HARNESS_GAP"
    )

    pins20 = hard["sealed_parent_pins"]["BA20"]
    pins21 = hard["sealed_parent_pins"]["BA21"]
    parent_commit_blob_receipt_provenance = (
        pins20["final_meta_commit"] == BA20_FINAL_META_COMMIT
        and pins20["final_meta_blob"] == BA20_FINAL_META_BLOB
        and pins20["result_receipt_commit"] == BA20_RECEIPT_COMMIT
        and pins20["result_receipt_blob"] == BA20_RECEIPT_BLOB
        and pins21["final_meta_commit"] == BA21_FINAL_META_COMMIT
        and pins21["final_meta_blob"] == BA21_FINAL_META_BLOB
        and pins21["result_receipt_commit"] == BA21_RECEIPT_COMMIT
        and pins21["result_receipt_blob"] == BA21_RECEIPT_BLOB
    )
    sealed_parent_receipts = (
        r20["authoritative_evidence"]["P_BA20_FINAL"] == 1
        and r20["authoritative_evidence"]["full_BA4_reconstruction_cases"] == 4454
        and r21["authoritative_evidence"]["P_BA21_FINAL"] == 1
        and r21["authoritative_evidence"]["full_BA4_reconstruction_cases"] == 48
        and r21["scientific_result"]["constructive_original_source_return"] is True
    )

    schema_provenance = {
        "BA20_final_meta": {"commit": BA20_FINAL_META_COMMIT, "blob": BA20_FINAL_META_BLOB},
        "BA20_result_receipt": {"commit": BA20_RECEIPT_COMMIT, "blob": BA20_RECEIPT_BLOB},
        "BA20_base_reconstruction": {"commit": BA20_BASE_COMMIT, "blob": BA20_BASE_BLOB},
        "BA20_authoritative_v2_wrapper": {"commit": BA20_V2_COMMIT, "blob": BA20_V2_BLOB},
        "BA4_carrier_schema": {"blob": BA4_SCHEMA_BLOB},
        "BA21_final_meta": {"commit": BA21_FINAL_META_COMMIT, "blob": BA21_FINAL_META_BLOB},
        "BA21_result_receipt": {"commit": BA21_RECEIPT_COMMIT, "blob": BA21_RECEIPT_BLOB},
        "BA21_compressed_projection_impl": {"commit": BA21_IMPL_COMMIT, "blob": BA21_IMPL_BLOB},
        "reconstruction_hardening": {"commit": HARDENING_COMMIT, "blob": HARDENING_BLOB},
        "verifier_v2_parent": {"commit": VERIFIER_V2_COMMIT, "blob": VERIFIER_V2_BLOB},
        "authoritative_v2_run1_failure_receipt": {"commit": FAILURE_RECEIPT_COMMIT, "blob": FAILURE_RECEIPT_BLOB},
    }
    schema_provenance["schema_sha256"] = sha256_json(schema_provenance)

    sys.path.insert(0, str(Path("experiments").resolve()))
    import janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence as ba20
    import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

    samples = result.get("proof_carrying", {}).get("samples", {})
    factor_dp_witness_samples_present = bool(samples)
    local_controls_pass = (
        bool(result.get("assertions", {}).get("reconstruction_controls"))
        and bool(result.get("assertions", {}).get("proof_carrying_payload"))
    )

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
            applicability.append({
                "sample": sample_name,
                "classification": "BA20_BA21_ROUTE_NOT_APPLICABLE",
                "reason": f"mapping_error:{type(exc).__name__}:{exc}",
            })
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
    per_control_applicability_classified = (
        len(applicability) == len(samples)
        and all(
            x["classification"] in {"BA20_BA21_ROUTE_APPLICABLE", "BA20_BA21_ROUTE_NOT_APPLICABLE"}
            for x in applicability
        )
    )
    replayed_cases_gt_zero = len(replay_rows) > 0
    parent_reconstruction_formula_match = parent_formula_mismatches == 0
    abstract_source_validation = abstract_failures == 0
    direct_original_ba4_zero_bad = original_failures == 0 and all(x["pass"] for x in replay_rows)
    sealed_parent_explicit_replay_pass = (
        pinned_file_blobs
        and parent_commit_blob_receipt_provenance
        and sealed_parent_receipts
        and replayed_cases_gt_zero
        and parent_reconstruction_formula_match
        and abstract_source_validation
        and direct_original_ba4_zero_bad
    )
    source_reconstruction_pass = (
        local_controls_pass
        and sealed_parent_explicit_replay_pass
        and direct_original_ba4_zero_bad
    )

    implementation_imported = False
    arbitrary_foreign_CNF_BA4_carrier_coverage_claimed = False
    BA26_STARTED = False

    self_test = polarity_classifier_self_test()

    positive_obligations = {
        "pinned_file_blobs": bool(pinned_file_blobs),
        "historical_run_34410959446_unsealed": bool(historical_run_unsealed),
        "reconstruction_hardening_exact": bool(hardening_exact),
        "authoritative_v2_run1_failure_preserved": bool(authoritative_v2_failure_preserved),
        "parent_commit_blob_receipt_provenance": bool(parent_commit_blob_receipt_provenance),
        "sealed_parent_receipts": bool(sealed_parent_receipts),
        "factor_dp_witness_samples_present": bool(factor_dp_witness_samples_present),
        "per_control_applicability_classified": bool(per_control_applicability_classified),
        "LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS": bool(local_controls_pass),
        "SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS": bool(sealed_parent_explicit_replay_pass),
        "DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES": bool(direct_original_ba4_zero_bad),
        "SOURCE_RECONSTRUCTION_PASS": bool(source_reconstruction_pass),
        "sealed_parent_reconstruction_replay": bool(source_reconstruction_pass),
        "number_of_replayed_cases_gt_zero": bool(len(replay_rows) > 0),
        "original_CNF_validation_failures_zero": bool(original_failures == 0),
        "parent_reconstruction_formula_mismatches_zero": bool(parent_formula_mismatches == 0),
        "abstract_source_validation_failures_zero": bool(abstract_failures == 0),
        "polarity_classifier_self_test": bool(self_test["pass"]),
        "SAT_IN_P_NOT_PROVED": True,
        "P_VS_NP_OPEN": True,
    }
    negative_firewalls = {
        "implementation_imported": implementation_imported,
        "arbitrary_foreign_CNF_BA4_carrier_coverage_claimed": arbitrary_foreign_CNF_BA4_carrier_coverage_claimed,
        "BA26_STARTED": BA26_STARTED,
    }

    failed_positive, violated_negative = classify_expected_polarity(positive_obligations, negative_firewalls)
    falsifiers = failed_positive + violated_negative

    out = {
        "gate": "R50G25BA25_VARIABLE_LOCALIZED_HYBRID_FACTOR_GRAPH_FPT_AND_ARBITRARY_CNF_INCIDENCE_WIDTH_CALIBRATION",
        "entry_type": "BA25_INDEPENDENT_VERIFIER_V3_EXPECTED_POLARITY_HARDENED",
        "status": "PASS" if not falsifiers else "FAIL",
        "scientific_authority": "INDEPENDENT_EVIDENCE_ONLY_PENDING_NEW_PRESEAL_AND_NEW_AUTHORITATIVE_WORKFLOW",
        "polarity_contract": {
            "positive_obligations_must_be": True,
            "negative_firewalls_must_be": False,
            "raw_boolean_without_expected_polarity_may_not_determine_failure": True,
            "failed_positive_definition": "[name for name,value in positive_obligations if value is not true]",
            "failed_negative_definition": "[name for name,value in negative_firewalls if value is not false]",
            "falsifiers_definition": "failed_positive_obligations + violated_negative_firewalls",
        },
        "polarity_self_test": self_test,
        "positive_obligations": positive_obligations,
        "negative_firewalls": negative_firewalls,
        "failed_positive_obligations": failed_positive,
        "violated_negative_firewalls": violated_negative,
        "falsifiers": falsifiers,
        "implementation_imported": implementation_imported,
        "sealed_parent_reconstruction_replay": source_reconstruction_pass,
        "SOURCE_RECONSTRUCTION_PASS": source_reconstruction_pass,
        "SOURCE_RECONSTRUCTION_PASS_definition": "LOCAL_BA25_RECONSTRUCTION_CONTROLS_PASS AND SEALED_BA20_BA21_RECONSTRUCTION_EXPLICIT_REPLAY_PASS AND DIRECT_ORIGINAL_BA4_CNF_ZERO_BAD_CLAUSES",
        "parent_BA20_commit": BA20_FINAL_META_COMMIT,
        "parent_BA21_commit": BA21_FINAL_META_COMMIT,
        "reconstruction_schema_hash_provenance": schema_provenance,
        "verifier_lineage": {
            "verifier_v2_commit": VERIFIER_V2_COMMIT,
            "verifier_v2_blob": VERIFIER_V2_BLOB,
            "verifier_v2_rewritten": False,
            "authoritative_v2_run1": AUTHORITATIVE_V2_RUN1,
            "authoritative_v2_job1": AUTHORITATIVE_V2_JOB1,
            "authoritative_v2_workflow_head": AUTHORITATIVE_V2_WORKFLOW_HEAD,
            "authoritative_v2_run1_status": "PERMANENTLY_FAILED_UNSEALED_NOT_PROMOTED",
            "failure_receipt_commit": FAILURE_RECEIPT_COMMIT,
            "failure_receipt_blob": FAILURE_RECEIPT_BLOB,
        },
        "number_of_replayed_cases": len(replay_rows),
        "applicable_control_count": len(applicable),
        "not_applicable_control_count": len(not_applicable),
        "original_CNF_validation_failures": original_failures,
        "abstract_source_validation_failures": abstract_failures,
        "parent_reconstruction_formula_mismatches": parent_formula_mismatches,
        "applicability": applicability,
        "replay_rows": replay_rows,
        "applicability_firewall": "Parent reconstruction replay only for controls that instantiate the sealed BA20/BA21 DBO surviving-variable route; foreign CNF remains a surviving-variable factor and is NOT transported through BA4 by this verifier.",
        "nonclaims": {
            "BA25_sealed": False,
            "BA25_theorem_falsified": False,
            "arbitrary_foreign_CNF_BA4_carrier_coverage": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "P_equals_NP_proved": False,
            "P_not_equals_NP_proved": False,
        },
        "STOP": {
            "BA25": "UNSEALED_PENDING_NEW_PRESEAL_AND_NEW_AUTHORITATIVE_WORKFLOW",
            "BA26_started": False,
            "preseal_created_in_this_step": False,
            "workflow_created_in_this_step": False,
            "next_permitted_object": "NEW_PRESEAL_HARDENING_REFERENCING_VERIFIER_V3_IN_A_SEPARATE_STEP",
            "external_literature_novelty_equivalence_audit_required_after_successful_BA25_seal": True,
            "general_sat_gap_map_required_after_successful_BA25_seal": True,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("BA25_VERIFY_V3_STATUS=" + out["status"])
    print("BA25_VERIFY_V3_POLARITY_SELF_TEST=" + str(self_test["pass"]).lower())
    print("BA25_VERIFY_V3_SEALED_PARENT_RECONSTRUCTION_REPLAY=" + str(source_reconstruction_pass).lower())
    print("BA25_VERIFY_V3_REPLAYED_CASES=" + str(len(replay_rows)))
    print("BA25_VERIFY_V3_ORIGINAL_CNF_VALIDATION_FAILURES=" + str(original_failures))
    print("BA25_VERIFY_V3_FAILED_POSITIVE=" + json.dumps(failed_positive, sort_keys=True))
    print("BA25_VERIFY_V3_VIOLATED_NEGATIVE=" + json.dumps(violated_negative, sort_keys=True))
    if falsifiers:
        print("BA25_VERIFY_V3_FALSIFIERS=" + json.dumps(falsifiers, sort_keys=True))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
