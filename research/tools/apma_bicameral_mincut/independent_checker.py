from __future__ import annotations

import collections
import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_pair_separator.pair_separator_explainer import explain_with_pair_separator
from research.tools.apma_bicameral_mincut.mincut_logwidth_explainer import (
    ARTIFACT_ID,
    explain_with_mincut,
    positive_logwidth_cut3,
    negative_overwidth_cut,
    injected_hint_control,
    canonical_min_variable_cut,
    proposal_record,
    redteam_proposal,
)

CHECK_ARTIFACT = "JANUS-TRUMP-BICAMERAL-MINCUT-LOGWIDTH-EXPLANATION-INDEPENDENT-CHECK-2026-09-15-v1.0"
CANDIDATE_REL = Path("research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py")
CANDIDATE_GIT_BLOB_SHA1 = "c0c612676e39241b95026c15823e7af6b3da8f0d"
PREREG_REL = Path("research/TRUMP_BICAMERAL_MINCUT_LOGWIDTH_EXPLANATION_PREREGISTRATION_2026-09-15.json")
PREREG_GIT_BLOB_SHA1 = "e83bf98bca925e49e43b4045b2795cd5c6b66ca1"
PARENT_PAIR_REL = Path("research/tools/apma_bicameral_pair_separator/pair_separator_explainer.py")
PARENT_PAIR_GIT_BLOB_SHA1 = "b6dc5fde585affb167e74308bc8f10c64f7d2990"
COMPOSER_REL = Path("research/tools/apma_unseen_basis/compositional_basis.py")
COMPOSER_GIT_BLOB_SHA1 = "fdc83a3368a4ad362f00d3ee8aad958f06f8d264"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def independent_incidence(canonical: dict) -> dict[str, set[str]]:
    g: dict[str, set[str]] = {f"v:{v}": set() for v in canonical["variables"]}
    for i, row in enumerate(canonical["constraints"]):
        c = f"c:{i}"
        g[c] = set()
        for v in row["scope"]:
            vn = f"v:{v}"
            g[c].add(vn)
            g[vn].add(c)
    return g


class Dinic:
    def __init__(self) -> None:
        self.g: dict[str, list[list]] = {}

    def add(self, u: str, v: str, cap: int) -> None:
        self.g.setdefault(u, [])
        self.g.setdefault(v, [])
        a = [v, cap, None]
        b = [u, 0, a]
        a[2] = b
        self.g[u].append(a)
        self.g[v].append(b)

    def flow(self, s: str, t: str) -> tuple[int, set[str]]:
        total = 0
        while True:
            level = {s: 0}
            q = collections.deque([s])
            while q:
                u = q.popleft()
                for e in sorted(self.g.get(u, []), key=lambda x: x[0]):
                    if e[1] > 0 and e[0] not in level:
                        level[e[0]] = level[u] + 1
                        q.append(e[0])
            if t not in level:
                break
            it = {u: 0 for u in self.g}
            ordered = {u: sorted(self.g[u], key=lambda x: x[0]) for u in self.g}

            def dfs(u: str, pushed: int) -> int:
                if u == t:
                    return pushed
                arr = ordered[u]
                while it[u] < len(arr):
                    e = arr[it[u]]
                    if e[1] > 0 and level.get(e[0], -1) == level[u] + 1:
                        got = dfs(e[0], min(pushed, e[1]))
                        if got:
                            e[1] -= got
                            e[2][1] += got
                            return got
                    it[u] += 1
                return 0

            while True:
                got = dfs(s, 10**9)
                if not got:
                    break
                total += got

        reachable: set[str] = set()
        q = collections.deque([s])
        while q:
            u = q.popleft()
            if u in reachable:
                continue
            reachable.add(u)
            for e in self.g.get(u, []):
                if e[1] > 0 and e[0] not in reachable:
                    q.append(e[0])
        return total, reachable


def independent_st_cut(canonical: dict, s_idx: int, t_idx: int) -> dict:
    inc = independent_incidence(canonical)
    inf = len(canonical["variables"]) + 1
    d = Dinic()
    for node in sorted(inc):
        d.add(node + "|in", node + "|out", 1 if node.startswith("v:") else inf)
    seen = set()
    for u in sorted(inc):
        for v in sorted(inc[u]):
            pair = tuple(sorted((u, v)))
            if pair in seen:
                continue
            seen.add(pair)
            d.add(u + "|out", v + "|in", inf)
            d.add(v + "|out", u + "|in", inf)
    value, reachable = d.flow(f"c:{s_idx}|out", f"c:{t_idx}|in")
    cut = [v for v in canonical["variables"] if f"v:{v}|in" in reachable and f"v:{v}|out" not in reachable]
    return {"value": value, "cut": cut}


def independent_component_count(canonical: dict, removed_vars: set[int]) -> int:
    g = independent_incidence(canonical)
    removed = {f"v:{v}" for v in removed_vars}
    constraint_nodes = {n for n in g if n.startswith("c:")}
    seen: set[str] = set()
    count = 0
    for start in sorted(n for n in g if n not in removed):
        if start in seen:
            continue
        q = [start]
        has_constraint = False
        while q:
            u = q.pop()
            if u in seen or u in removed:
                continue
            seen.add(u)
            has_constraint |= u in constraint_nodes
            q.extend(v for v in g[u] if v not in seen and v not in removed)
        if has_constraint:
            count += 1
    return count


def independent_canonical_cut(canonical: dict) -> dict | None:
    records = []
    ccount = len(canonical["constraints"])
    for s in range(ccount):
        for t in range(s + 1, ccount):
            z = independent_st_cut(canonical, s, t)
            if len(z["cut"]) != z["value"]:
                continue
            if independent_component_count(canonical, set(z["cut"])) <= 1:
                continue
            records.append((len(z["cut"]), tuple(z["cut"]), s, t, z["value"]))
    if not records:
        return None
    records.sort()
    k, cut, s, t, value = records[0]
    return {"cut_size": k, "cut_variables": list(cut), "source_constraint_index": s, "target_constraint_index": t, "maxflow_value": value}


def independent_restrict(canonical: dict, cut: list[int], values: tuple[int, ...]) -> dict:
    assignment = dict(zip(cut, values))
    constraints = []
    unsat = False
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        positions = [(i, v) for i, v in enumerate(scope) if v in assignment]
        if not positions:
            constraints.append({"id": row["id"], "scope": scope, "allowed": [list(t) for t in row["allowed"]]})
            continue
        survivors = []
        for raw_t in row["allowed"]:
            t = tuple(int(x) for x in raw_t)
            if all(t[i] == assignment[v] for i, v in positions):
                survivors.append(t)
        if not survivors:
            unsat = True
            break
        keep = [i for i, v in enumerate(scope) if v not in assignment]
        new_scope = [scope[i] for i in keep]
        tuples = sorted({tuple(t[i] for i in keep) for t in survivors})
        if new_scope:
            constraints.append({"id": row["id"], "scope": new_scope, "allowed": [list(t) for t in tuples]})
    residual = {"variables": sorted({v for row in constraints for v in row["scope"]}), "constraints": constraints}
    return {"branch_unsat": unsat, "residual": residual if not unsat else None}


def independent_branch_admitted(r: dict) -> bool:
    if r["branch_unsat"]:
        return True
    residual = r["residual"]
    if not residual["constraints"]:
        return True
    return induce_compositional_basis(residual).get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO"


def permuted_positive() -> dict:
    raw = positive_logwidth_cut3()
    return {
        "variables": list(raw["variables"]),
        "constraints": [
            {"id": row["id"], "scope": list(row["scope"]), "allowed": list(reversed(row["allowed"]))}
            for row in reversed(raw["constraints"])
        ],
    }


def main() -> None:
    root = repo_root()
    prereg = json.loads((root / PREREG_REL).read_text(encoding="utf-8"))
    source_checks = {
        "candidate_blob": git_blob_sha1(root / CANDIDATE_REL) == CANDIDATE_GIT_BLOB_SHA1,
        "prereg_blob": git_blob_sha1(root / PREREG_REL) == PREREG_GIT_BLOB_SHA1,
        "prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "parent_pair_blob": git_blob_sha1(root / PARENT_PAIR_REL) == PARENT_PAIR_GIT_BLOB_SHA1,
        "sealed_composer_blob": git_blob_sha1(root / COMPOSER_REL) == COMPOSER_GIT_BLOB_SHA1,
    }

    pos_raw = positive_logwidth_cut3()
    pos_can = canonicalize_raw(pos_raw)
    pos_parent = explain_with_pair_separator(pos_raw)
    pos_global = induce_compositional_basis(pos_can)
    pos_ind_cut = independent_canonical_cut(pos_can)
    pos_candidate_cut = canonical_min_variable_cut(pos_can)
    pos = explain_with_mincut(pos_raw)
    pos_red = pos.get("redteam") or {}
    pos_branches = pos_red.get("branches") or []
    pos_L = len(canonical_bytes(pos_can))
    cut = pos_ind_cut["cut_variables"] if pos_ind_cut else []
    independent_restrictions = [independent_restrict(pos_can, cut, values) for values in itertools.product((0,1), repeat=len(cut))]
    independent_admitted = [independent_branch_admitted(r) for r in independent_restrictions]
    candidate_core_restrictions = [
        {"branch_unsat": b["restriction"]["branch_unsat"], "residual": b["restriction"]["residual"]}
        for b in pos_branches
    ]

    neg_raw = negative_overwidth_cut()
    neg_can = canonicalize_raw(neg_raw)
    neg_parent = explain_with_pair_separator(neg_raw)
    neg_global = induce_compositional_basis(neg_can)
    neg_ind_cut = independent_canonical_cut(neg_can)
    neg = explain_with_mincut(neg_raw)
    neg_red = neg.get("redteam") or {}
    neg_L = len(canonical_bytes(neg_can))

    hint = explain_with_mincut(injected_hint_control())
    perm = explain_with_mincut(permuted_positive())

    candidate_cut_for_tamper = canonical_min_variable_cut(pos_can)
    assert candidate_cut_for_tamper is not None
    proposal = proposal_record(pos_can, candidate_cut_for_tamper)
    proposal["separator_variables"] = [0,1,3]
    tampered = redteam_proposal(pos_can, candidate_cut_for_tamper, proposal)

    checks = {
        "P1_source_guard": all(source_checks.values()),
        "P2_positive_parent_pair_open": pos_parent.get("status") == "OPEN_NO_EXACT_PAIR_SEPARATOR_EXPLANATION",
        "P2_positive_global_basis_open": pos_global.get("status") == "OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS",
        "P2_negative_parent_pair_open": neg_parent.get("status") == "OPEN_NO_EXACT_PAIR_SEPARATOR_EXPLANATION",
        "P2_negative_global_basis_open": neg_global.get("status") == "OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS",
        "P3_independent_positive_cut_exists": pos_ind_cut is not None,
        "P3_positive_cut_exact_012": pos_ind_cut is not None and pos_ind_cut["cut_variables"] == [0,1,2] and pos_ind_cut["cut_size"] == 3,
        "P3_candidate_matches_independent_cut": pos_candidate_cut is not None and pos_ind_cut is not None and pos_candidate_cut["cut_variables"] == pos_ind_cut["cut_variables"] and pos_candidate_cut["cut_size"] == pos_ind_cut["cut_size"] and pos_candidate_cut["maxflow_value"] == pos_ind_cut["maxflow_value"],
        "P4_positive_cut_separates_constraints": independent_component_count(pos_can, {0,1,2}) > 1,
        "P5_positive_budget_passes": pos_ind_cut is not None and (1 << pos_ind_cut["cut_size"]) <= pos_L,
        "P6_positive_terminal_admits": pos.get("status") == "ADMIT_EXACT_LOGWIDTH_MINCUT_EXPLANATION",
        "P6_positive_exactly_8_branches": len(pos_branches) == 8,
        "P7_candidate_restrictions_match_independent": candidate_core_restrictions == independent_restrictions,
        "P8_all_independent_positive_branches_admit": all(independent_admitted),
        "P8_all_candidate_positive_branches_admit": len(pos_branches) == 8 and all(b["replay"]["admitted"] for b in pos_branches),
        "P9_independent_negative_cut_20": neg_ind_cut is not None and neg_ind_cut["cut_size"] == 20 and neg_ind_cut["cut_variables"] == list(range(20)),
        "P9_negative_budget_really_exceeds_L": neg_ind_cut is not None and (1 << neg_ind_cut["cut_size"]) > neg_L,
        "P10_negative_terminal_budget_open": neg.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P10_negative_zero_branch_enumeration": neg_red.get("branches") == [] and neg_red.get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P11_hint_rejected_before_cut_execution": hint.get("status") == "REJECT_RAW_INPUT",
        "P12_tampered_proposal_rejected": tampered.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "P13_permutation_preserves_terminal": perm.get("status") == "ADMIT_EXACT_LOGWIDTH_MINCUT_EXPLANATION",
        "P13_permutation_preserves_cut": (perm.get("cut") or {}).get("cut_variables") == [0,1,2],
        "P14_no_solver_execution": pos.get("metrics", {}).get("solver_invocations") == 0 and neg.get("metrics", {}).get("solver_invocations") == 0,
        "P14_no_generic_transfer": pos.get("metrics", {}).get("generic_transfer_calls") == 0 and neg.get("metrics", {}).get("generic_transfer_calls") == 0,
        "P14_no_full_variable_cube": pos.get("metrics", {}).get("full_variable_assignments_enumerated") == 0 and neg.get("metrics", {}).get("full_variable_assignments_enumerated") == 0,
        "P14_no_cartesian_products": pos.get("metrics", {}).get("cartesian_products_materialized") == 0 and neg.get("metrics", {}).get("cartesian_products_materialized") == 0,
        "P15_receipt_content_bound": bool(pos.get("provenance_receipt", {}).get("mincut_explanation_receipt_sha256")),
        "P16_firewall_p_vs_np_open": pos["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "P16_firewall_general_sat_not_proved": pos["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "P16_firewall_connected_mixed_not_solved": pos["scientific_firewall"]["CONNECTED_MIXED_CORE_SOLVED"] == "NO",
        "P16_firewall_arbitrary_unseen_not_proved": pos["scientific_firewall"]["ARBITRARY_UNSEEN_INVARIANT_DISCOVERY"] == "NOT_PROVED",
    }

    verdict = "PASS_SCOPED_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION" if all(checks.values()) else "FAIL_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION"
    out = {
        "artifact_id": CHECK_ARTIFACT,
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "candidate_artifact_id": ARTIFACT_ID,
        "checks": checks,
        "source_checks": source_checks,
        "controls": {
            "positive_parent_pair": pos_parent.get("status"),
            "positive_global_basis": pos_global.get("status"),
            "positive_independent_cut": pos_ind_cut,
            "positive_candidate_cut": pos_candidate_cut,
            "positive_L": pos_L,
            "positive_branch_budget": (1 << pos_ind_cut["cut_size"]) if pos_ind_cut else None,
            "positive_terminal": pos.get("status"),
            "positive_branch_count": len(pos_branches),
            "negative_parent_pair": neg_parent.get("status"),
            "negative_global_basis": neg_global.get("status"),
            "negative_independent_cut": neg_ind_cut,
            "negative_L": neg_L,
            "negative_branch_budget": (1 << neg_ind_cut["cut_size"]) if neg_ind_cut else None,
            "negative_terminal": neg.get("status"),
            "negative_branch_enumerations": neg_red.get("resource_receipt", {}).get("branch_enumerations"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tampered.get("status"),
            "permuted_terminal": perm.get("status"),
        },
        "complexity": {
            "cut_discovery": "O(C^2) polynomial max-flow calls; independent checker uses Dinic, candidate uses Edmonds-Karp",
            "branch_budget": "2^k <= L checked before enumeration; at most L exact branches",
            "subset_enumeration_for_discovery": False,
            "claim": "POLYNOMIAL_IN_CANONICAL_EXPLICIT_INPUT_LENGTH_FOR_FROZEN_MINCUT_LOGWIDTH_SCOPE",
            "finite_controls_are_not_asymptotic_evidence": True,
        },
        "scientific_firewall": pos["scientific_firewall"],
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
