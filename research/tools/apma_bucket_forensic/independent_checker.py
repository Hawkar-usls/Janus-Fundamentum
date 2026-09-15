from __future__ import annotations

import json
from math import prod

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_bucket_forensic import first_overbudget_bucket_forensic as profiler

ARTIFACT_ID = "JANUS-TRUMP-CAPTAIN-FIRST-OVERBUDGET-BUCKET-FORENSIC-INDEPENDENT-CHECK-2026-09-15-v1.0"
AUTHORITY = "INDEPENDENT_DIAGNOSTIC_CHECKER__NO_THEOREM_PROMOTION"


def factor_from_relation(rel: dict, index: int) -> dict:
    oscope = list(rel["scope"])
    scope = sorted(oscope)
    pos = {v: i for i, v in enumerate(oscope)}
    rows = sorted({tuple(int(row[pos[v]]) for v in scope) for row in rel["allowed"]})
    return {"id": f"orig:{index}", "scope": scope, "rows": rows}


def merge_assignments(a: dict[int, int], scope: list[int], row: tuple[int, ...]) -> dict[int, int] | None:
    out = dict(a)
    for v, bit in zip(scope, row):
        bit = int(bit)
        if v in out and out[v] != bit:
            return None
        out[v] = bit
    return out


def progressive_nested_loop(bucket: list[dict]) -> list[int]:
    states = [{v: int(bit) for v, bit in zip(bucket[0]["scope"], row)} for row in bucket[0]["rows"]]
    counts = [len(states)]
    for factor in bucket[1:]:
        next_states: dict[tuple[tuple[int, int], ...], dict[int, int]] = {}
        for state in states:
            for row in factor["rows"]:
                merged = merge_assignments(state, factor["scope"], row)
                if merged is None:
                    continue
                key = tuple(sorted(merged.items()))
                next_states.setdefault(key, merged)
        states = list(next_states.values())
        counts.append(len(states))
        if not states:
            break
    return counts


def pairwise_compatibility(a: dict, b: dict) -> int:
    total = 0
    for ar in a["rows"]:
        amap = {v: bit for v, bit in zip(a["scope"], ar)}
        for br in b["rows"]:
            ok = True
            for v, bit in zip(b["scope"], br):
                if v in amap and amap[v] != bit:
                    ok = False
                    break
            if ok:
                total += 1
    return total


def reconstruct_bucket() -> tuple[dict, list[dict], dict]:
    raw = guarded.overbudget_control()
    replay = guarded.explain(raw)
    assert replay["status"] == "OPEN_BUCKET_PRODUCT_BUDGET", replay["status"]
    failed = replay["carrier"]["failed_bucket"]
    assert int(failed["variable"]) == 20
    assert replay["carrier"]["resource_receipt"]["failed_bucket_combinations_enumerated"] == 0
    canonical = canonicalize_raw(raw)
    cut = list(replay["parent_cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    comp = next(c for c in components if any(20 in canonical["constraints"][gi]["scope"] for gi in c))
    factors = [factor_from_relation(canonical["constraints"][gi], gi) for gi in comp]
    bucket = [f for f in factors if 20 in f["scope"]]
    assert [f["id"] for f in bucket] == failed["bucket_factor_ids"]
    return replay, bucket, canonical


def run() -> dict:
    candidate = profiler.run()
    replay, bucket, canonical = reconstruct_bucket()
    counts = [len(f["rows"]) for f in bucket]
    raw_product = prod(counts)
    nested_counts = progressive_nested_loop(bucket)
    candidate_counts = [int(x["progressive_rows"]) for x in candidate["progressive_compatibility"]["steps"]]

    common = sorted(set.intersection(*(set(f["scope"]) for f in bucket)))
    candidate_common = candidate["factor_graph"]["common_shared_core"]

    pair_map = {}
    for i in range(len(bucket)):
        for j in range(i + 1, len(bucket)):
            pair_map[(bucket[i]["id"], bucket[j]["id"])] = pairwise_compatibility(bucket[i], bucket[j])
    candidate_pair_map = {(p["a"], p["b"]): int(p["compatible_row_pairs"]) for p in candidate["pairwise"]}

    checks = {
        "D1_profiler_source_guard": candidate.get("source_guard", {}).get("ok") is True,
        "D2_parent_open": replay["status"] == "OPEN_BUCKET_PRODUCT_BUDGET",
        "D2_failed_variable_20": int(replay["carrier"]["failed_bucket"]["variable"]) == 20,
        "D2_zero_failed_enumeration": replay["carrier"]["resource_receipt"]["failed_bucket_combinations_enumerated"] == 0,
        "D3_bucket_ids_match": [f["id"] for f in bucket] == candidate["target"]["failed_bucket_factor_ids"],
        "D4_raw_product_matches": raw_product == candidate["raw_product"]["exact"],
        "D4_raw_product_over_L2": raw_product > candidate["target"]["L2"],
        "D5_progressive_counts_match_separate_nested_loop": nested_counts == candidate_counts,
        "D6_pairwise_counts_match": pair_map == candidate_pair_map,
        "D7_common_shared_core_matches": common == candidate_common,
        "D9_no_promotion": candidate["interpretation"]["theorem_promotion"] is False,
        "D9_p_vs_np_open": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "D9_general_sat_not_proved": candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "D9_general_effective_compression_not_proved": candidate["scientific_firewall"]["GENERAL_EFFECTIVE_BUCKET_COMPRESSION"] == "NOT_PROVED",
    }
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "checks": checks,
        "controls": {
            "factor_count": len(bucket),
            "factor_row_counts": counts,
            "exact_raw_product": raw_product,
            "L2": candidate["target"]["L2"],
            "progressive_compatible_rows": nested_counts,
            "final_compatible_rows": nested_counts[-1],
            "common_shared_core": common,
            "common_shared_core_size": len(common),
        },
        "verdict": "PASS_DIAGNOSTIC_FIRST_OVERBUDGET_BUCKET_FORENSIC" if all(checks.values()) else "FAIL_DIAGNOSTIC_FIRST_OVERBUDGET_BUCKET_FORENSIC",
        "scientific_firewall": candidate["scientific_firewall"],
    }


def main() -> None:
    out = run()
    print(json.dumps(out, sort_keys=True))
    if not all(out["checks"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
