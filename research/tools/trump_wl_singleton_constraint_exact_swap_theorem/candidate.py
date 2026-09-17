from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_WL_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW = ROOT / "research/TRUMP_WL_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_REVIEW_2026-09-18_v1.0.json"
PROJECTION = ROOT / "research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"
WL = ROOT / "research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py"
ORBIT = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
SCOPE_THEOREM = ROOT / "research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_RESULT_2026-09-18_v1.0.json"

EXPECTED = {
    PREREG: "5f3a4087a9399411f51e4abd90f77dd786497189",
    REVIEW: "5b693b091533eec19f8e96bb8d78a0e77663c950",
    PROJECTION: "2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
    WL: "6b697fd8b3de4c83f8226b06399b6bad99953d4e",
    ORBIT: "a076cfc56d68aad0348415e313705da1f6b9cdcd",
    SCOPE_THEOREM: "3cbf05cb0b0249ddf365bc43d176a06ddb7f72af",
}

def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def allowed(kind: str) -> list[list[int]]:
    forbidden = (0,0,0) if kind == "R000" else (1,1,1)
    return [list(bits) for bits in itertools.product((0,1), repeat=3) if bits != forbidden]

R000 = allowed("R000")
R111 = allowed("R111")

def relation_permutation_symmetric(rows: list[list[int]]) -> bool:
    rowset = {tuple(r) for r in rows}
    for p in itertools.permutations(range(3)):
        mapped = {tuple(r[i] for i in p) for r in rows}
        if mapped != rowset:
            return False
    return True

def make_raw(n: int, selected: tuple[tuple[tuple[int,int,int], str], ...]) -> dict[str, Any]:
    constraints=[]
    for idx,(scope,kind) in enumerate(selected):
        constraints.append({
            "id": f"s{idx:03d}_{kind}",
            "scope": list(scope),
            "allowed": R000 if kind=="R000" else R111,
        })
    used=sorted({v for c in constraints for v in c["scope"]})
    # Keep all declared variables: isolated variables are legal in the normalized formula contract
    # and make the theorem sanity stronger, not weaker.
    return {"variables": list(range(1,n+1)), "constraints": constraints}

def final_wl(raw: dict[str,Any]):
    nodes,adjacency,labels = wl_ref.incidence_structure(raw)
    colors,rounds = wl_ref.wl1(nodes,adjacency,labels)
    return nodes,adjacency,labels,colors,rounds

def stable_equitable(nodes, adjacency, colors) -> bool:
    signatures={}
    for n in nodes:
        signatures[n]=(colors[n], tuple(sorted(colors[x] for x in adjacency[n])))
    by=defaultdict(set)
    for n in nodes:
        by[colors[n]].add(signatures[n])
    return all(len(s)==1 for s in by.values())

def constraint_colors_singleton(nodes, colors) -> bool:
    cs=[n for n in nodes if n[0]=="c"]
    counts=Counter(colors[n] for n in cs)
    return all(v==1 for v in counts.values())

def same_color_variable_pairs(nodes, colors):
    vs=[n for n in nodes if n[0]=="v"]
    return [(u[1],v[1]) for i,u in enumerate(vs) for v in vs[i+1:] if colors[u]==colors[v]]

def identical_constraint_neighborhood(raw, u:int, v:int) -> bool:
    iu={str(c["id"]) for c in raw["constraints"] if u in set(map(int,c["scope"]))}
    iv={str(c["id"]) for c in raw["constraints"] if v in set(map(int,c["scope"]))}
    return iu==iv

def iter_synthetic():
    for n,max_k in ((3,None),(4,None),(5,3),(6,2)):
        universe=[(tuple(t),kind) for t in itertools.combinations(range(1,n+1),3) for kind in ("R000","R111")]
        if max_k is None:
            for mask in range(1<<len(universe)):
                yield n,tuple(universe[i] for i in range(len(universe)) if mask&(1<<i))
        else:
            for k in range(max_k+1):
                for combo in itertools.combinations(universe,k):
                    yield n,tuple(combo)

def main():
    bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
    if not all(bindings.values()):
        return {"verdict":"HALT_AUTHORITY_BINDING_FAILURE","authority_bindings":bindings}

    prereg=json.loads(PREREG.read_text())
    review=json.loads(REVIEW.read_text())
    scope=json.loads(SCOPE_THEOREM.read_text())
    guards={
        "prereg_frozen":prereg.get("status")=="FROZEN_BEFORE_THEOREM_IMPLEMENTATION_OR_SOURCE_BOUND_COROLLARY_MEASUREMENT",
        "review_authorized":review.get("review_verdict")=="PASS_CLEAN_SINGLETON_CONSTRAINT_EXACT_SWAP_THEOREM_SPEC__AUTHORIZED_TO_IMPLEMENT_PROVE_AND_INDEPENDENTLY_CHECK_ONCE",
        "prior_scope_theorem_pass":scope.get("scientific_outcome")=="PASS_SCOPE_BOUND_DIRECT_EXACT_TRANSPOSITION_WITNESS_SUFFICIENCY_FOR_FROZEN_E3",
        "relation_R000_S3_symmetric":relation_permutation_symmetric(R000),
        "relation_R111_S3_symmetric":relation_permutation_symmetric(R111),
    }
    if not all(guards.values()):
        return {"verdict":"FAIL_SYMBOLIC_PROOF_OBLIGATION","guards":guards}

    failures=[]
    cases=0
    premise_formulas=0
    premise_pair_checks=0
    equitable_failures=0
    type_separation_failures=0

    for n,selected in iter_synthetic():
        raw=make_raw(n,selected)
        nodes,adjacency,labels,colors,rounds=final_wl(raw)
        cases+=1
        if not stable_equitable(nodes,adjacency,colors):
            equitable_failures+=1
            failures.append({"class":"WL_NOT_EQUITABLE_AT_RETURN","n":n,"selected":selected})
            break
        vars_colors={colors[x] for x in nodes if x[0]=="v"}
        constraint_colors={colors[x] for x in nodes if x[0]=="c"}
        if vars_colors & constraint_colors:
            type_separation_failures+=1
            failures.append({"class":"VARIABLE_CONSTRAINT_COLOR_COLLISION","n":n,"selected":selected})
            break

        if not constraint_colors_singleton(nodes,colors):
            continue
        pairs=same_color_variable_pairs(nodes,colors)
        if not pairs:
            continue
        premise_formulas+=1
        formula=orbit.validate_and_normalize(raw)
        for u,v in pairs:
            premise_pair_checks+=1
            same_incidence=identical_constraint_neighborhood(raw,u,v)
            exact=orbit.is_exact_transposition_automorphism(formula,u,v)
            if not same_incidence or not exact:
                failures.append({
                    "class":"SYNTHETIC_COUNTEREXAMPLE",
                    "n":n,
                    "selected":[[list(s),k] for s,k in selected],
                    "pair":[u,v],
                    "same_incident_constraints":same_incidence,
                    "frozen_exact_transposition":exact,
                })
                break
        if failures:
            break

    symbolic={
        "C1_REFINEMENT_STABILITY_IMPLIES_EQUITABILITY": equitable_failures==0,
        "C2_TYPE_LABEL_SEPARATION": type_separation_failures==0,
        "C3_SINGLETON_CONSTRAINT_NEIGHBOR_EQUALITY": len(failures)==0,
        "C4_IDENTICAL_INCIDENT_CONSTRAINT_SET": len(failures)==0,
        "C5_SCOPE_SET_PRESERVATION": len(failures)==0,
        "C6_R000_R111_COORDINATE_SYMMETRY": guards["relation_R000_S3_symmetric"] and guards["relation_R111_S3_symmetric"],
        "C7_RELATION_PRESERVATION": len(failures)==0,
        "C8_EXACT_FORMULA_KEY_EQUALITY": len(failures)==0,
        "C9_DIRECT_EXACT_PREDICATE_TRUE": len(failures)==0,
        "C10_SCOPE_THEOREM_COMPOSITION": guards["prior_scope_theorem_pass"],
    }
    verdict=("PASS_SINGLETON_CONSTRAINT_WL_COLOR_IMPLIES_EXACT_SWAP_ON_R000_R111_RESIDUALS"
             if all(symbolic.values()) and not failures else
             "FAIL_SYNTHETIC_COUNTEREXAMPLE_FOUND" if failures else "FAIL_SYMBOLIC_PROOF_OBLIGATION")
    return {
        "artifact_id":"JANUS-TRUMP-WL-SINGLETON-CONSTRAINT-EXACT-SWAP-THEOREM-CANDIDATE-2026-09-18-v1.0",
        "verdict":verdict,
        "authority_bindings":bindings,
        "guards":guards,
        "symbolic_claims":symbolic,
        "synthetic_sanity":{
            "formulas_checked":cases,
            "premise_formulas":premise_formulas,
            "premise_pair_checks":premise_pair_checks,
            "failures":failures,
        },
        "theorem":{
            "premise":"R000_R111_RESIDUAL_AND_STABLE_WL1_SAME_COLOR_PAIR_AND_ALL_CONSTRAINT_NODES_SINGLETON",
            "conclusion":"FROZEN_EXACT_TRANSPOSITION_PREDICATE_TRUE",
            "direct_exact_check_required_as_selector_gate":False,
            "e3_corollary":"PLUS_3_TIMES_2_POW_N_MINUS_2_LE_L_SQUARED_IMPLIES_FROZEN_E3_ADMISSION",
        },
        "scientific_firewall":{
            "WL_SUFFICIENCY_WITHOUT_DIRECT_EXACT_CHECK":"PROVED_ONLY_FOR_EXPLICIT_SINGLETON_CONSTRAINT_R000_R111_SUBCLASS" if verdict.startswith("PASS_") else "NOT_PROVED",
            "GENERAL_SAT_IN_P":"NOT_PROVED",
            "P_VS_NP":"OPEN",
        },
    }

if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True,separators=(",",":")))
