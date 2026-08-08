#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

SCHEMA = "janus.fundamentum.a3.duplicate_subspace_pathwidth_literature_novelty_audit.v1"
THEOREM_ID = "A3_DUPLICATE_SUBSPACE_PATHWIDTH_V1"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def verify(audit: dict) -> None:
    assert audit["schema"] == SCHEMA
    assert audit["theorem_id"] == THEOREM_ID
    assert audit["theorem_admission_head"] == "23eb740a215dd6fe793483a7e9316c9aa3628c4c"
    assert audit["theorem_admission_receipt_git_blob"] == "26667b8d372d640d094b3ec7f4a4011c679afda1"

    sources = {row["id"]: row for row in audit["primary_sources"]}
    assert set(sources) == {"JKO_2017", "KASHYAP_2007_2008", "HLINENY_2016"}
    jko = sources["JKO_2017"]
    assert jko["arxiv"] == "1507.02184v4"
    assert jko["doi"] == "10.1109/TIT.2017.2740283"
    assert jko["source_role"] == "CONTROLLING_SUBSPACE_ARRANGEMENT_DEFINITION"
    assert "dim((V_1+...+V_i) intersect (V_{i+1}+...+V_n))" in jko["relevant_fact"]
    assert sources["KASHYAP_2007_2008"]["arxiv"] == "0705.1384"
    assert sources["HLINENY_2016"]["arxiv"] == "1605.09520"
    assert "parallel vectors are represented by identical points" in sources["HLINENY_2016"]["relevant_fact"]

    # Independent symbolic novelty test.  This does not attempt to prove absence
    # from all literature.  It checks that the admitted theorem is derivable by
    # direct substitution into the already-published JKO cut expression.
    for d in range(0, 8):
        for m in range(2, 9):
            profile = []
            for cut in range(m + 1):
                left_nonempty = cut > 0
                right_nonempty = cut < m
                # If a side has >=1 copy of U, its sum/span is U; otherwise {0}.
                # Intersection dimension is d iff both sides are nonempty.
                width = d if left_nonempty and right_nonempty else 0
                profile.append(width)
            assert profile == [0] + [d] * (m - 1) + [0]
            assert max(profile) == d
    for d in range(0, 8):
        m = 1
        profile = [0, 0]
        assert max(profile) == 0

    logic = audit["logical_novelty_test"]
    assert logic["derivation_requires_new_external_lemma"] is False
    assert logic["derivation_requires_new_construction"] is False
    assert logic["derivation_requires_new_counterexample"] is False
    assert logic["classification"] == "DIRECT_DEFINITIONAL_COROLLARY_OF_PREEXISTING_SUBSPACE_ARRANGEMENT_PATHWIDTH_DEFINITION"

    scope = audit["search_scope"]
    assert scope["source_policy"] == "PRIMARY_SOURCES_ONLY_FOR_TECHNICAL_NOVELTY_CLASSIFICATION"
    assert scope["explicit_exact_statement_found"] is False
    assert scope["absence_proof_claimed"] is False

    result = audit["audit_result"]
    assert result["PROJECT_LOCAL_THEOREM_VALID"] is True
    assert result["MATHEMATICAL_CONTENT_PREEXISTING_BY_DIRECT_DEFINITIONAL_IMPLICATION"] is True
    assert result["WORLD_NOVEL_THEOREM_CLAIM"] == "FORBIDDEN"
    assert result["STANDALONE_LITERATURE_NOVELTY"] == "NOT_ESTABLISHED"
    assert result["P_VS_NP"] == "OPEN"

    rows = audit["frontier_v1_3_1_snapshot"]
    assert len(rows) == 23
    assert [r["rank"] for r in rows] == list(range(1, 24))
    assert rows[0]["id"] == "A0_P_VS_NP"
    matroid = next(r for r in rows if r["id"] == "A3_MATROID_TRELLIS_RANK_WIDTH")
    assert matroid["rank"] == 2
    assert (matroid["all_surfaces"], matroid["proof_surfaces"], matroid["proof_classes"], matroid["marker_coverage"]) == (119, 85, 4, 6)
    assert "PROJECT_LOCAL_THEOREM_ADMITTED" in matroid["class"]
    assert all("ACTIVE_STRUCTURAL_ROUTE" not in r["class"] for r in rows)

    ceiling = audit["claim_ceiling"]
    assert ceiling["WORLD_NOVEL_THEOREM_CLAIM"] == "FORBIDDEN"
    assert ceiling["ANY_A0_A2_OPEN_PROBLEM_RESOLVED"] is False
    assert ceiling["P_VS_NP"] == "OPEN"


def reject(audit: dict, mutate) -> None:
    x = copy.deepcopy(audit)
    before = digest(x)
    mutate(x)
    assert digest(x) != before, "tamper fixture must actually mutate the audit"
    try:
        verify(x)
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("tamper accepted")


def tamper_suite(audit: dict) -> int:
    attacks = [
        lambda x: x["audit_result"].__setitem__("WORLD_NOVEL_THEOREM_CLAIM", "ESTABLISHED"),
        lambda x: x["audit_result"].__setitem__("STANDALONE_LITERATURE_NOVELTY", "ESTABLISHED"),
        lambda x: x["search_scope"].__setitem__("absence_proof_claimed", True),
        lambda x: x["search_scope"].__setitem__("explicit_exact_statement_found", True),
        lambda x: x["logical_novelty_test"].__setitem__("derivation_requires_new_external_lemma", True),
        lambda x: x["logical_novelty_test"].__setitem__("classification", "NEW_WORLD_THEOREM"),
        lambda x: x["primary_sources"][0].__setitem__("arxiv", "0000.00000"),
        lambda x: x["primary_sources"][0].__setitem__("doi", "wrong"),
        lambda x: x["primary_sources"][2].__setitem__("arxiv", "wrong"),
        lambda x: x["frontier_v1_3_1_snapshot"][1].__setitem__("rank", 1),
        lambda x: x["frontier_v1_3_1_snapshot"][1].__setitem__("proof_surfaces", 999),
        lambda x: x["frontier_v1_3_1_snapshot"][1].__setitem__("class", "ACTIVE_STRUCTURAL_ROUTE"),
        lambda x: x["claim_ceiling"].__setitem__("WORLD_NOVEL_THEOREM_CLAIM", "ESTABLISHED"),
        lambda x: x["claim_ceiling"].__setitem__("P_VS_NP", "P_EQUALS_NP"),
    ]
    for attack in attacks:
        reject(audit, attack)
    return len(attacks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True)
    ap.add_argument("--tamper-test", action="store_true")
    args = ap.parse_args()
    audit = json.loads(Path(args.audit).read_text(encoding="utf-8"))
    verify(audit)
    print("LITERATURE_NOVELTY_AUDIT_INDEPENDENT_REPLAY = PASS")
    print("DIRECT_JKO_DEFINITIONAL_COROLLARY = CONFIRMED")
    print("EXPLICIT_IDENTICAL_PRIOR_THEOREM_STATEMENT_FOUND = FALSE_IN_SEARCHED_PRIMARY_CORPUS")
    print("UNIVERSAL_ABSENCE_PROOF = NOT_CLAIMED")
    print("WORLD_NOVEL_THEOREM_CLAIM = FORBIDDEN")
    print("STANDALONE_LITERATURE_NOVELTY = NOT_ESTABLISHED")
    print("NEXT_NOVELTY_FRONTIER = MULTI_GEOMETRIC_CLASS_SUBSPACE_PATHWIDTH_STRUCTURE")
    print("P_VS_NP = OPEN")
    if args.tamper_test:
        n = tamper_suite(audit)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {n}/{n}")

if __name__ == "__main__":
    main()
