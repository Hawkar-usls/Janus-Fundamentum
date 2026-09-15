from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bicameral_mincut.independent_checker import independent_canonical_cut, independent_incidence
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as candidate

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_BICAMERAL_CUT_SUPPORT_CARRIER_PREREGISTRATION_2026-09-15.json"
CANDIDATE = ROOT / "research/tools/apma_cut_support_carrier/cut_support_carrier.py"
PARENT_STATE = ROOT / "registry/TRUMP_CURRENT_STATE_2026-09-15_v2.7.json"
PARENT_MINCUT = ROOT / "research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py"
PARENT_MINCUT_CHECKER = ROOT / "research/tools/apma_bicameral_mincut/independent_checker.py"
OLD_QUOTIENT = ROOT / "research/tools/apma_interface_quotient/exact_quotient.py"
OLD_QUOTIENT_CHECKER = ROOT / "research/tools/apma_interface_quotient/independent_checker.py"
EXPECTED = {
    str(PREREG): "b4eaaf90fe45b2c45867114928e93726132ebaf5",
    str(CANDIDATE): "012aa1acf52fa12de26bb64df303b2208d396ea9",
    str(PARENT_STATE): "deb9b4b1d32b7dba24b945d80ef933f10044de2a",
    str(PARENT_MINCUT): "c0c612676e39241b95026c15823e7af6b3da8f0d",
    str(PARENT_MINCUT_CHECKER): "54e0a7b4117d59f3ad9a6e1d25c920dce8406319",
    str(OLD_QUOTIENT): "cc331245bd71b6c83ab6c43b86f961fe53ed31c8",
    str(OLD_QUOTIENT_CHECKER): "fb5fe1773bbc5cc91a78e13eb1129449b84d3820",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run_candidate_main() -> dict:
    cp = subprocess.run([sys.executable, "-m", "research.tools.apma_cut_support_carrier.cut_support_carrier"], cwd=ROOT, check=True, capture_output=True, text=True)
    return json.loads(cp.stdout.strip().splitlines()[-1])


def independent_components(canonical: dict, cut: list[int]) -> list[list[int]]:
    g = independent_incidence(canonical)
    removed = {f"v:{v}" for v in cut}
    seen: set[str] = set()
    out: list[list[int]] = []
    for i in range(len(canonical["constraints"])):
        start = f"c:{i}"
        if start in seen:
            continue
        stack = [start]
        cs: list[int] = []
        while stack:
            n = stack.pop()
            if n in seen or n in removed:
                continue
            seen.add(n)
            if n.startswith("c:"):
                cs.append(int(n.split(":",1)[1]))
            stack.extend(x for x in g[n] if x not in seen and x not in removed)
        if cs:
            out.append(sorted(cs))
    return sorted(out)


def independent_support(row: dict, cut: list[int]) -> dict[tuple[int,...], tuple[int,...]]:
    scope = list(row["scope"])
    if not set(cut).issubset(scope):
        raise ValueError("PARTIAL")
    pos = [scope.index(v) for v in cut]
    out: dict[tuple[int,...], tuple[int,...]] = {}
    for raw in row["allowed"]:
        t = tuple(int(x) for x in raw)
        key = tuple(t[i] for i in pos)
        out.setdefault(key, t)
    return out


def independent_carrier(raw: dict) -> dict:
    canonical = canonicalize_raw(raw)
    cut = independent_canonical_cut(canonical)
    if cut is None:
        return {"status":"NO_CUT"}
    B = list(cut["cut_variables"])
    comps = independent_components(canonical, B)
    if len(comps) < 2 or any(len(c)!=1 for c in comps):
        return {"status":"OPEN_COMPONENT_COUNT", "cut":cut, "components":comps}
    relations = [canonical["constraints"][c[0]] for c in comps]
    if any(not set(B).issubset(r["scope"]) for r in relations):
        return {"status":"OPEN_PARTIAL", "cut":cut, "components":comps}
    private = [set(r["scope"]) - set(B) for r in relations]
    if any(private[i] & private[j] for i in range(len(private)) for j in range(i+1,len(private))):
        return {"status":"OPEN_PRIVATE_OVERLAP", "cut":cut, "components":comps}
    supports = [independent_support(r,B) for r in relations]
    common = set.intersection(*(set(s) for s in supports))
    return {
        "status":"ADMIT" if common else "UNSAT",
        "cut":cut,
        "components":comps,
        "support_sizes":[len(s) for s in supports],
        "common":sorted(common),
        "rows":sum(len(r["allowed"]) for r in relations),
    }


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    source = {Path(p).name + "_blob": git_blob_sha1(Path(p)) == sha for p,sha in EXPECTED.items()}
    source["prereg_frozen"] = prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"
    source["prereg_gate"] = prereg.get("frozen_gate") == "TRUMP_BICAMERAL_MINCUT_EFFECTIVE_QUOTIENT_RANK_EXPLANATION_FALSIFIER_GATE__CUT_SUPPORT_INTERSECTION_FIRST"

    run = run_candidate_main()
    pos_raw = candidate.positive_overwidth()
    pos_parent = parent_mincut.explain_with_mincut(pos_raw)
    pos_ind = independent_carrier(pos_raw)
    pos = run["positive"]

    empty_raw = candidate.empty_intersection_control()
    empty_parent = parent_mincut.explain_with_mincut(empty_raw)
    empty_ind = independent_carrier(empty_raw)
    empty = run["negative_empty"]

    multi_raw = candidate.multi_relation_component_control()
    multi_parent = parent_mincut.explain_with_mincut(multi_raw)
    multi_ind = independent_carrier(multi_raw)
    multi = run["negative_multi_relation_component"]

    partial_raw = candidate.partial_cut_visibility_control()
    partial_parent = parent_mincut.explain_with_mincut(partial_raw)
    partial_ind = independent_carrier(partial_raw)
    partial = run["negative_partial_cut_visibility"]

    checks = {
        **{f"P1_{k}":v for k,v in source.items()},
        "P2_positive_parent_overwidth": pos_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_positive_parent_zero_branches": pos_parent.get("redteam",{}).get("resource_receipt",{}).get("branch_enumerations") == 0,
        "P3_positive_independent_cut20": pos_ind.get("cut",{}).get("cut_size") == 20 and pos_ind.get("cut",{}).get("cut_variables") == list(range(20)),
        "P3_candidate_cut_matches_independent": pos.get("parent_cut",{}).get("cut_variables") == pos_ind.get("cut",{}).get("cut_variables"),
        "P4_positive_two_single_relation_components": pos_ind.get("components") == [[0],[1]],
        "P5_positive_full_cut_visibility": pos_ind.get("status") == "ADMIT",
        "P7_positive_independent_support_sizes": pos_ind.get("support_sizes") == [3,4],
        "P8_positive_effective_support_one": len(pos_ind.get("common",[])) == 1 and pos.get("carrier",{}).get("effective_support_size") == 1,
        "P8_carrier_size_bounded_by_input_support": pos.get("carrier",{}).get("effective_support_size",999) <= pos.get("carrier",{}).get("support_size_bound",-1),
        "P9_positive_terminal": pos.get("status") == "ADMIT_EXACT_CUT_SUPPORT_INTERSECTION_CARRIER",
        "P10_positive_witness_verified": pos.get("carrier",{}).get("witness_verified") is True,
        "P12_positive_zero_raw_cube": pos.get("carrier",{}).get("resource_receipt",{}).get("raw_cut_assignments_enumerated") == 0,
        "P12_positive_zero_cartesian": pos.get("carrier",{}).get("resource_receipt",{}).get("cartesian_products_materialized") == 0,
        "P12_positive_zero_solver": pos.get("carrier",{}).get("resource_receipt",{}).get("solver_invocations") == 0,
        "P11_empty_parent_overwidth": empty_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P11_empty_independent_empty": empty_ind.get("status") == "UNSAT" and len(empty_ind.get("common",[])) == 0,
        "P11_empty_terminal_exact_unsat": empty.get("status") == "EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION",
        "P13_multi_parent_overwidth": multi_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P13_multi_independent_detects_multi": multi_ind.get("status") == "OPEN_COMPONENT_COUNT" and any(len(c)>1 for c in multi_ind.get("components",[])),
        "P13_multi_candidate_open": multi.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P13_partial_parent_overwidth": partial_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P13_partial_independent_detects_partial": partial_ind.get("status") == "OPEN_PARTIAL",
        "P13_partial_candidate_open": partial.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P14_hint_rejected": run["negative_hint"].get("status") == "REJECT_RAW_INPUT",
        "P14_tamper_rejected": run["negative_tamper"].get("status") == "REJECT_TAMPERED_PROVENANCE",
        "P15_rows_scanned_polynomial": pos.get("carrier",{}).get("total_input_rows_scanned") == pos_ind.get("rows"),
        "P15_effective_states_le_rows": pos.get("carrier",{}).get("effective_support_size",999) <= pos_ind.get("rows",-1),
        "FW_p_vs_np_open": run["scientific_firewall"].get("P_VS_NP") == "OPEN",
        "FW_general_sat_not_proved": run["scientific_firewall"].get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "FW_connected_mixed_not_solved": run["scientific_firewall"].get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
        "FW_arbitrary_unseen_not_proved": run["scientific_firewall"].get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
    }
    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_CUT_SUPPORT_INTERSECTION_CARRIER" if all(checks.values()) else "FAIL_OR_OPEN_BICAMERAL_CUT_SUPPORT_CARRIER"
    out = {
        "artifact_id":"JANUS-TRUMP-BICAMERAL-CUT-SUPPORT-CARRIER-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority":"INDEPENDENT_CHECKER__SCOPED_ONLY",
        "verdict":verdict,
        "checks":checks,
        "controls":{
            "positive_parent":pos_parent.get("status"),
            "positive_k":pos_ind.get("cut",{}).get("cut_size"),
            "positive_raw_branch_budget":pos_parent.get("redteam",{}).get("branch_budget"),
            "positive_parent_branch_enumerations":pos_parent.get("redteam",{}).get("resource_receipt",{}).get("branch_enumerations"),
            "positive_component_support_sizes":pos_ind.get("support_sizes"),
            "positive_effective_support": [list(x) for x in pos_ind.get("common",[])],
            "positive_terminal":pos.get("status"),
            "empty_terminal":empty.get("status"),
            "multi_terminal":multi.get("status"),
            "partial_terminal":partial.get("status"),
            "hint_terminal":run["negative_hint"].get("status"),
            "tamper_terminal":run["negative_tamper"].get("status"),
        },
        "complexity":{
            "cut_discovery":"frozen polynomial max-flow parent",
            "support_projection":"linear scan of explicit tuple cells",
            "support_intersection":"polynomial set intersection with no expansion",
            "carrier_size":"<= minimum projected support size <= input tuple rows",
            "raw_2_to_k_enumeration":0,
            "cartesian_products":0,
        },
        "scientific_firewall":candidate.firewall(),
    }
    print(json.dumps(out,sort_keys=True))
    if verdict.startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
