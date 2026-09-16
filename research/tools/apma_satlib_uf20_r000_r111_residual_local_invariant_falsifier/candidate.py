from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_RESIDUAL_LOCAL_INVARIANT_FALSIFIER_PREREGISTRATION_2026-09-16.json'
REVIEW = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_RESIDUAL_LOCAL_INVARIANT_FALSIFIER_PREREGISTRATION_REVIEW_2026-09-16.json'
PARENT = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_FOUR_UNADMITTED_EXISTING_EVIDENCE_RESIDUAL_MATRIX_RESULT_2026-09-16.json'
EXPECTED = {
    PREREG: '55c2a314900c5518bbd4fbeb41db74629e478911',
    REVIEW: 'dd6d08e7c519f3a39483f93d812f15484b11b390',
    PARENT: 'f6209a9b97c8f270ff915ba5c813922b5a8e3bb3',
    ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py': '2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
SOURCES = {
    'UF20_01': (ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
    'UF20_02': (ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}
CANDIDATES = (
    'L1_ROOT_PAIR_MULTIPLICITY_MULTISET',
    'L2_ROOT_INCIDENT_HYPEREDGE_NEIGHBOR_PROFILE',
    'L3_THREE_ROUND_INCIDENCE_WL_ROOT_COLOR',
    'L4_ROOT_SIMPLE_INCIDENCE_6CYCLE_PROFILE',
)


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_scope_projection(name: str, path: Path) -> tuple[list[int], list[tuple[int, int, int]], str]:
    clauses = projection_identity.parse(path)
    selected = [c for c in clauses if projection_identity.rid(c) in {'000','111'}]
    edges = [tuple(sorted(abs(x) for x in c)) for c in selected]
    variables = sorted({v for e in edges for v in e})
    raw, _ = projection_identity.normalize_projection(name, clauses)
    raw_sha = canonical_sha(raw)
    return variables, edges, raw_sha


def pair_multiplicity(edges: list[tuple[int, int, int]]) -> Counter[tuple[int, int]]:
    out: Counter[tuple[int, int]] = Counter()
    for e in edges:
        for a,b in itertools.combinations(e,2):
            out[tuple(sorted((a,b)))] += 1
    return out


def incident_degree(V: list[int], edges: list[tuple[int, int, int]]) -> Counter[int]:
    d: Counter[int] = Counter()
    for e in edges:
        for v in e:
            d[v] += 1
    for v in V:
        d[v] += 0
    return d


def l1(V: list[int], edges: list[tuple[int, int, int]]) -> dict[int, Any]:
    pm = pair_multiplicity(edges)
    d = incident_degree(V, edges)
    return {v:(d[v], tuple(sorted(pm[tuple(sorted((v,u)))] for u in V if u != v and pm[tuple(sorted((v,u)))] > 0))) for v in V}


def l2(V: list[int], edges: list[tuple[int, int, int]]) -> dict[int, Any]:
    pm = pair_multiplicity(edges)
    d = incident_degree(V, edges)
    inc: dict[int, list[tuple[int,int,int]]] = {v:[] for v in V}
    for e in edges:
        for v in e:
            others = [x for x in e if x != v]
            a,b = others
            va = pm[tuple(sorted((v,a)))]
            vb = pm[tuple(sorted((v,b)))]
            ab = pm[tuple(sorted((a,b)))]
            x,y = sorted((va,vb))
            inc[v].append((x,y,ab))
    return {v:(d[v], tuple(sorted(inc[v]))) for v in V}


def incidence_graph(V: list[int], edges: list[tuple[int, int, int]]) -> tuple[list[tuple[str,int]], dict[tuple[str,int], list[tuple[str,int]]]]:
    nodes: list[tuple[str,int]] = [('v',v) for v in V] + [('c',i) for i in range(len(edges))]
    nbr: dict[tuple[str,int], list[tuple[str,int]]] = {n:[] for n in nodes}
    for i,e in enumerate(edges):
        c=('c',i)
        for v in e:
            x=('v',v)
            nbr[c].append(x)
            nbr[x].append(c)
    return nodes,nbr


def l3(V: list[int], edges: list[tuple[int, int, int]]) -> dict[int, Any]:
    nodes,nbr = incidence_graph(V,edges)
    color: dict[tuple[str,int], Any] = {n:(('VAR',) if n[0]=='v' else ('CORE_CONSTRAINT',)) for n in nodes}
    for _ in range(3):
        old = color
        color = {n:(old[n], tuple(sorted(old[m] for m in nbr[n]))) for n in nodes}
    return {v:color[('v',v)] for v in V}


def l4(V: list[int], edges: list[tuple[int, int, int]]) -> dict[int, Any]:
    pair_edges: dict[tuple[int,int], list[int]] = defaultdict(list)
    for idx,e in enumerate(edges):
        for a,b in itertools.combinations(e,2):
            pair_edges[tuple(sorted((a,b)))].append(idx)
    total: Counter[int] = Counter()
    both: Counter[tuple[int,int]] = Counter()
    for a,b,c in itertools.combinations(V,3):
        ab = pair_edges.get((a,b),())
        bc = pair_edges.get((b,c),())
        ac = pair_edges.get((a,c),())
        for eab in ab:
            for ebc in bc:
                if ebc == eab:
                    continue
                for eac in ac:
                    if eac == eab or eac == ebc:
                        continue
                    total[a] += 1; total[b] += 1; total[c] += 1
                    both[(a,b)] += 1; both[(a,c)] += 1; both[(b,c)] += 1
    out = {}
    for v in V:
        per_u = []
        for u in V:
            if u == v:
                continue
            z = both[tuple(sorted((v,u)))]
            if z > 0:
                per_u.append(z)
        out[v] = (total[v], tuple(sorted(per_u)))
    return out


def partition(sig: dict[int, Any]) -> tuple[list[list[int]], str]:
    groups: dict[str, list[int]] = defaultdict(list)
    canonical_map = []
    for v in sorted(sig):
        key = json.dumps(sig[v], sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        groups[key].append(v)
        canonical_map.append([v, sig[v]])
    classes = [sorted(xs) for xs in groups.values()]
    classes.sort(key=lambda xs:(xs[0],len(xs),xs))
    return classes, canonical_sha(canonical_map)


def evaluate_candidate(cid: str, datasets: dict[str, tuple[list[int],list[tuple[int,int,int]],str]]) -> dict[str, Any]:
    fn = {
        CANDIDATES[0]: l1,
        CANDIDATES[1]: l2,
        CANDIDATES[2]: l3,
        CANDIDATES[3]: l4,
    }[cid]
    rows=[]
    by_source={}
    for name,(V,edges,raw_sha) in datasets.items():
        sig=fn(V,edges)
        classes,digest=partition(sig)
        nontriv=[c for c in classes if len(c)>1]
        row={'source':name,'raw_sha256':raw_sha,'variable_count':len(V),'constraint_count':len(edges),'classes':classes,'nontrivial_classes':nontriv,'max_class_size':max(map(len,classes)),'signature_map_sha256':digest}
        rows.append(row);by_source[name]=row
    control_class=next(c for c in by_source['UF20_01']['classes'] if 7 in c)
    control_ok=control_class==[7,10]
    panel_ok=all(all(len(c)==1 for c in by_source[name]['classes']) for name in ('UF20_02','UF20_03','UF20_04','UF20_05'))
    return {'candidate_id':cid,'survives':control_ok and panel_ok,'control_pair_class':control_class,'control_pair_exact':control_ok,'panel_all_singleton':panel_ok,'rows':rows}


def guard() -> dict[str, Any]:
    bindings={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()}
    source_bindings={name:blob(path)==sha for name,(path,sha) in SOURCES.items()}
    pre=json.loads(PREREG.read_text())
    review=json.loads(REVIEW.read_text())
    menu=[x['candidate_id'] for x in pre.get('candidate_menu',[])]
    checks={
        'bindings':all(bindings.values()),
        'source_bindings':all(source_bindings.values()),
        'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_CANDIDATE_VALUE_COMPUTATION',
        'menu_exact':menu==list(CANDIDATES),
        'review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
    }
    return {'ok':all(checks.values()),'checks':checks,'bindings':bindings,'source_bindings':source_bindings}


def main() -> dict[str, Any]:
    g=guard()
    if not g['ok']:
        return {'verdict':'HALT_BINDING_OR_CANONICALIZATION_FAILURE','source_guard':g,'scientific_firewall':firewall()}
    pre=json.loads(PREREG.read_text())
    expected_raw=pre['frozen_projected_raw_sha256']
    datasets={}
    for name,(path,_) in SOURCES.items():
        V,edges,raw_sha=source_scope_projection(name,path)
        if raw_sha != expected_raw[name]:
            return {'verdict':'HALT_BINDING_OR_CANONICALIZATION_FAILURE','source':name,'observed_raw_sha256':raw_sha,'expected_raw_sha256':expected_raw[name],'source_guard':g,'scientific_firewall':firewall()}
        datasets[name]=(V,edges,raw_sha)
    candidates=[evaluate_candidate(cid,datasets) for cid in CANDIDATES]
    survivors=[c['candidate_id'] for c in candidates if c['survives']]
    verdict='PASS_SCOPED_AT_LEAST_ONE_PREREGISTERED_LOCAL_CANDIDATE_SURVIVES_FALSIFIER' if survivors else 'FAIL_NO_PREREGISTERED_LOCAL_CANDIDATE_SURVIVES_FALSIFIER'
    return {
        'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-RESIDUAL-LOCAL-INVARIANT-FALSIFIER-CANDIDATE-2026-09-16-v1.0',
        'authority':'DIAGNOSTIC_FROZEN_FOUR_CANDIDATE_EVALUATION_ONLY__NO_SOLVER_CARRIER_ADAPTER_QUOTIENT_GROUP_SEARCH_OR_TRACTABILITY_CLAIM',
        'verdict':verdict,
        'source_guard':g,
        'surviving_candidates':survivors,
        'candidate_results':candidates,
        'resource_receipt':{
            'candidate_count':4,'candidate_value_families_computed':20,'full_assignment_cube_enumerations':0,'solver_invocations':0,'group_searches':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False,
        },
        'scientific_firewall':firewall(),
    }


def firewall() -> dict[str, Any]:
    return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','CANDIDATE_SURVIVAL_IMPLIES_HARDNESS':False,'CANDIDATE_SURVIVAL_IMPLIES_TRACTABILITY':False,'NEW_SOLVER_MECHANISM_LICENSED':False,'NEW_CARRIER_MECHANISM_LICENSED':False}


if __name__=='__main__':
    print(json.dumps(main(),sort_keys=True,separators=(',',':')))
