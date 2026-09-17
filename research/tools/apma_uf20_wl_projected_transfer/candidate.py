from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_UF20_WL_PROJECTED_REPRESENTATION_TRANSFER_PREREGISTRATION_2026-09-17_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF20_WL_PROJECTED_REPRESENTATION_TRANSFER_REVIEW_2026-09-17_v1.0.json"
WL_RESULT = ROOT / "research/TRUMP_UF20_02_04_05_WL_POLYTIME_STRUCTURAL_INVARIANT_RESULT_2026-09-17_v1.0.json"
HIST_RESULT = ROOT / "research/TRUMP_UF20_WL_POLYTIME_HISTORICAL_CLOSED_CONTROL_FALSIFIER_RESULT_2026-09-17_v1.0.json"
PROJECTION = ROOT / "research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"
WL_REF = ROOT / "research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py"

EXPECTED_BLOBS = {
    PREREG: "971863e0ab4ea4f287b68513eb083c601f0c3d54",
    REVIEW: "8d93598fb15087094e25ae999f8780905bb884ec",
    WL_RESULT: "b2f84ed9e8e1bd97c42852e02f9abd2c88f74320",
    HIST_RESULT: "5bef066c04562594a6cb932300834b53d746189a",
    PROJECTION: "2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
    WL_REF: "6b697fd8b3de4c83f8226b06399b6bad99953d4e",
}

EXPECTED_PROJECTED_SHA = {
    "UF20_02": "cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6",
    "UF20_03": "30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d",
    "UF20_04": "db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3",
    "UF20_05": "fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6",
}
OPEN = {"UF20_02", "UF20_04", "UF20_05"}
CLOSED = "UF20_03"
FEATURES = [
    "WL1_MAX_VARIABLE_COLOR_CLASS_SIZE",
    "WL1_VARIABLE_PARTITION_IS_DISCRETE",
    "WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE",
    "WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE",
]
BLOCKER = {
    "WL1_MAX_VARIABLE_COLOR_CLASS_SIZE": 1,
    "WL1_VARIABLE_PARTITION_IS_DISCRETE": True,
    "WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE": 1,
    "WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE": True,
}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def relation_signature(c: dict[str, Any]) -> str:
    rows = sorted("".join(str(int(bit)) for bit in row) for row in c["allowed"])
    return f"a{len(c['scope'])}:" + "/".join(rows)


def canonical_rank(signatures: dict[Any, Any]) -> dict[Any, int]:
    unique = sorted(set(signatures.values()), key=repr)
    rank = {value: i for i, value in enumerate(unique)}
    return {key: rank[value] for key, value in signatures.items()}


def incidence(raw: dict[str, Any]):
    nodes = []
    adj = defaultdict(set)
    labels = {}
    for v in sorted(int(x) for x in raw["variables"]):
        n = ("v", v); nodes.append(n); adj[n]; labels[n] = "V"
    for c in raw["constraints"]:
        n = ("c", str(c["id"])); nodes.append(n); adj[n]; labels[n] = "C:" + relation_signature(c)
        for v in sorted({int(x) for x in c["scope"]}):
            vn = ("v", v); adj[n].add(vn); adj[vn].add(n)
    return sorted(nodes, key=lambda x: (x[0], str(x[1]))), adj, labels


def wl1(nodes, adj, labels):
    colors = canonical_rank({n: (labels[n],) for n in nodes}); rounds = 0
    while True:
        new = canonical_rank({n: (colors[n], tuple(sorted(colors[x] for x in adj[n]))) for n in nodes})
        rounds += 1
        if len(set(new.values())) == len(set(colors.values())): return new, rounds
        colors = new


def wl2(nodes, adj, labels):
    vc = canonical_rank({n: (labels[n],) for n in nodes}); pairs = list(itertools.product(nodes, nodes))
    colors = canonical_rank({(u,v):(vc[u],vc[v],int(u==v),int(v in adj[u])) for u,v in pairs}); rounds = 0
    while True:
        sig = {}
        for u,v in pairs:
            sig[(u,v)] = (colors[(u,v)], tuple(sorted((colors[(u,w)], colors[(w,v)]) for w in nodes)))
        new = canonical_rank(sig); rounds += 1
        if len(set(new.values())) == len(set(colors.values())): return new, rounds
        colors = new


def class_sizes(colors, keys):
    return sorted(Counter(colors[k] for k in keys).values())


def features(raw: dict[str, Any]) -> dict[str, Any]:
    nodes, adj, labels = incidence(raw); vars_ = [n for n in nodes if n[0] == "v"]
    c1,r1 = wl1(nodes,adj,labels); c2,r2 = wl2(nodes,adj,labels)
    s1 = class_sizes(c1, vars_); s2 = class_sizes(c2, [(v,v) for v in vars_])
    return {
        "WL1_MAX_VARIABLE_COLOR_CLASS_SIZE": max(s1),
        "WL1_VARIABLE_PARTITION_IS_DISCRETE": all(x == 1 for x in s1),
        "WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE": max(s2),
        "WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE": all(x == 1 for x in s2),
        "_receipt": {"variable_count":len(vars_),"constraint_count":sum(1 for n in nodes if n[0]=="c"),"incidence_vertex_count":len(nodes),"incidence_edge_count":sum(len(adj[n]) for n in nodes)//2,"wl1_rounds":r1,"wl2_rounds":r2},
    }


def build_projected(source: str):
    path, _ = projection_identity.SOURCES[source]
    raw, ordinals = projection_identity.normalize_projection(source, projection_identity.parse(path))
    sha = hashlib.sha256(canonical_bytes(raw)).hexdigest()
    return raw, ordinals, sha


def main():
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p,h in EXPECTED_BLOBS.items()}
    if not all(bindings.values()): return {"verdict":"HALT_PROJECTED_IDENTITY_OR_AUTHORITY_BINDING_FAILURE","authority_bindings":bindings}
    review = json.loads(REVIEW.read_text())
    if review.get("review_verdict") != "PASS_CLEAN_PROJECTED_TRANSFER_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE": return {"verdict":"HALT_PROJECTED_IDENTITY_OR_AUTHORITY_BINDING_FAILURE","reason":"review"}

    rows = {}
    identity_guards = {}
    for source in ["UF20_02","UF20_03","UF20_04","UF20_05"]:
        raw, ordinals, sha = build_projected(source)
        ok = sha == EXPECTED_PROJECTED_SHA[source]
        identity_guards[source] = {"projected_sha256":sha,"expected_projected_sha256":EXPECTED_PROJECTED_SHA[source],"ok":ok,"selected_clause_ordinals":ordinals}
        if not ok: return {"verdict":"HALT_PROJECTED_IDENTITY_OR_AUTHORITY_BINDING_FAILURE","identity_guards":identity_guards}
        rows[source] = features(raw)

    survivor = []
    per_feature = {}
    for f in FEATURES:
        open_match = {s: rows[s][f] == BLOCKER[f] for s in sorted(OPEN)}
        closed_diff = rows[CLOSED][f] != BLOCKER[f]
        survives = all(open_match.values()) and closed_diff
        per_feature[f] = {"blocker_value":BLOCKER[f],"open_matches":open_match,"closed_value":rows[CLOSED][f],"closed_differs":closed_diff,"survives":survives}
        if survives: survivor.append(f)
    if len(survivor) == 4: verdict = "PROJECTED_WL_TRANSFER_ALL_FOUR_SURVIVE__FRESH_HOLDOUT_PREREGISTRATION_MAY_FOLLOW"
    elif survivor: verdict = "PROJECTED_WL_TRANSFER_PARTIAL_SURVIVOR_SET__FREEZE_SURVIVORS_BEFORE_ANY_HOLDOUT_GATE"
    else: verdict = "PROJECTED_WL_TRANSFER_NO_SURVIVOR__DO_NOT_UNBLIND_FRESH_HOLDOUT_FOR_THIS_CANDIDATE"
    return {
        "artifact_id":"JANUS-TRUMP-UF20-WL-PROJECTED-REPRESENTATION-TRANSFER-CANDIDATE-2026-09-17-v1.0",
        "gate":"TRUMP_UF20_WL_PROJECTED_REPRESENTATION_TRANSFER_GATE",
        "verdict":verdict,
        "authority_bindings":bindings,
        "identity_guards":identity_guards,
        "feature_rows":rows,
        "per_feature_transfer":per_feature,
        "surviving_features":sorted(survivor),
        "falsified_features":sorted(set(FEATURES)-set(survivor)),
        "blindness_receipt":{"fresh_holdout_formula_reads":0,"fresh_holdout_projected_values":0,"fresh_holdout_wl_values":0,"posthoc_thresholds_or_combinations":0},
        "resource_receipt":{"solver_invocations":0,"automorphism_or_group_searches":0,"new_reduction_mechanisms":0,"new_solver_rules":0,"new_action_rules":0,"new_carrier_mechanisms":0},
        "scientific_firewall":{"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED","GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY":"NOT_PROVED"}
    }

if __name__ == "__main__": print(json.dumps(main(),sort_keys=True,separators=(",",":")))
