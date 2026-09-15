from __future__ import annotations

import json

from research.tools.apma_component_join_carrier import component_join_carrier as v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-CANDIDATE-2026-09-15-v1.2"
AUTHORITY = "CANDIDATE_REPAIR_WRAPPER__NO_SCIENTIFIC_PROMOTION"
FROZEN_V1_CANDIDATE_BLOB = "89f5d591d4d553bb26489908a79f2c739f62b756"
ORIGINAL_JOIN_TREE = v1.deterministic_join_tree


def deterministic_join_tree_v1_2(relations: list[dict]) -> dict:
    if len(relations) != 1:
        return ORIGINAL_JOIN_TREE(relations)
    body = {
        "relation_count": 1,
        "edges": [],
        "running_intersection": True,
        "violations": [],
        "construction": "TRIVIAL_SINGLE_RELATION_TREE",
        "backtracking": False,
    }
    body["tree_sha256"] = v1.sha256_obj(body)
    return {"ok": True, "reason": "SINGLE_RELATION", **body}


def install_repair() -> None:
    v1.deterministic_join_tree = deterministic_join_tree_v1_2


def firewall() -> dict:
    return v1.firewall()


def explain_overwidth_component_join(raw: dict) -> dict:
    install_repair()
    return v1.explain_overwidth_component_join(raw)


def positive_multi_relation_k20() -> dict:
    return v1.positive_multi_relation_k20()


def empty_conditional_join_control() -> dict:
    return v1.empty_conditional_join_control()


def alpha_cycle_control() -> dict:
    return v1.alpha_cycle_control()


def no_anchor_unit_control() -> dict:
    install_repair()
    return v1.no_anchor_unit_control()


def injected_hint_control() -> dict:
    return v1.injected_hint_control()


def tampered_control() -> dict:
    install_repair()
    return v1.tampered_control()


def main() -> None:
    install_repair()
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "repair": "SINGLETON_JOIN_TREE_CANONICAL_RECEIPT_ONLY",
        "frozen_v1_candidate_blob": FROZEN_V1_CANDIDATE_BLOB,
        "positive": v1.explain_overwidth_component_join(v1.positive_multi_relation_k20()),
        "negative_empty": v1.explain_overwidth_component_join(v1.empty_conditional_join_control()),
        "negative_cycle": v1.explain_overwidth_component_join(v1.alpha_cycle_control()),
        "negative_no_anchor_unit": v1.no_anchor_unit_control(),
        "negative_hint": v1.explain_overwidth_component_join(v1.injected_hint_control()),
        "negative_tamper": v1.tampered_control(),
        "scientific_firewall": v1.firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
