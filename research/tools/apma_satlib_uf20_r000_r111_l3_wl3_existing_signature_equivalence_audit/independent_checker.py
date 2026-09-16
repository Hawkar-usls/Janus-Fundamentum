from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_PREREGISTRATION_2026-09-17.json'
REVIEW = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_PREREGISTRATION_REVIEW_2026-09-17.json'
EXPECTED = {
    PREREG: 'cc3e3a4b8c8b0a5c00f8558471e7efa451bc0a25',
    REVIEW: '945dd3009dec8eb768d9224edfe413c80a1b1a43',
    ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_RESIDUAL_LOCAL_INVARIANT_FALSIFIER_RESULT_2026-09-16.json': '954893935bee1d46a77c5f635086e0e278b05fac',
    ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_RESULT_2026-09-16.json': 'b7ba5bd772c3092e0436dde8bd717dc28985983c',
    ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_signature_ablation/replay.py': '2edad57e6017cb34bf797313e4451c1ce014900b',
    ROOT / 'research/tools/apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier/candidate.py': '4ec02d6d42e6cad7d91f16b1acfdcbe51dbd65df',
    ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py': '2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
SOURCES = {
    'UF20_01': (ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
    'UF20_02': (ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}
LEVELS = ('S0','S1','S2','S3')
CUBE = tuple(itertools.product((0,1), repeat=3))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def relation_key_rows(rows) -> tuple[str, ...]:
    return tuple(sorted(''.join(str(int(b)) for b in row) for row in rows))


def full_surface_order() -> tuple[list[tuple[str, ...]], list[str]]:
    keys = []
    for forbidden in CUBE:
        allowed = [r for r in CUBE if r != forbidden]
        keys.append((relation_key_rows(allowed), ''.join(map(str, forbidden))))
    keys.sort(key=lambda x: x[0])
    return [k for k, _ in keys], [rid for _, rid in keys]


def projected_clauses(path: Path):
    return [c for c in projection_identity.parse(path) if projection_identity.rid(c) in {'000','111'}]


def existing_features(raw: dict[str, Any], clauses) -> dict[int, dict[str, Any]]:
    variables = raw['variables']
    adj = {v:set() for v in variables}
    for c in raw['constraints']:
        for u,v in itertools.combinations(c['scope'],2):
            adj[u].add(v); adj[v].add(u)
    degree = {v:len(adj[v]) for v in variables}
    pos = Counter(); neg = Counter()
    for clause in clauses:
        for lit in clause:
            (pos if lit > 0 else neg)[abs(lit)] += 1
    surface_keys, surface_rids = full_surface_order()
    assert surface_rids == ['111','110','101','100','011','010','001','000']
    index = {k:i for i,k in enumerate(surface_keys)}
    inc = {v:[0]*8 for v in variables}
    for c in raw['constraints']:
        i = index[relation_key_rows(c['allowed'])]
        for v in c['scope']:
            inc[v][i] += 1
    return {
        v:{
            'S0':(degree[v],),
            'S1':(degree[v],pos[v],neg[v]),
            'S2':(degree[v],pos[v],neg[v],tuple(inc[v])),
            'S3':(degree[v],pos[v],neg[v],tuple(inc[v]),tuple(sorted(degree[n] for n in adj[v]))),
        }
        for v in variables
    }


def partition_from_level(feats: dict[int, dict[str, Any]], level: str) -> list[list[int]]:
    groups = defaultdict(list)
    for v in sorted(feats):
        key = json.dumps(feats[v][level], separators=(',', ':'))
        groups[key].append(v)
    out = [sorted(xs) for xs in groups.values()]
    out.sort(key=lambda xs:(xs[0],len(xs),xs))
    return out


def l3_signature(V: list[int], edges: list[tuple[int,int,int]]) -> dict[int, Any]:
    nodes = [('v',v) for v in V] + [('c',i) for i in range(len(edges))]
    nbr = {n:[] for n in nodes}
    for i,e in enumerate(edges):
        c=('c',i)
        for v in e:
            x=('v',v)
            nbr[c].append(x); nbr[x].append(c)
    color = {n:(('VAR',) if n[0]=='v' else ('CORE_CONSTRAINT',)) for n in nodes}
    for _ in range(3):
        old = color
        color = {n:(old[n], tuple(sorted(old[m] for m in nbr[n]))) for n in nodes}
    return {v:color[('v',v)] for v in V}


def partition_from_signature(sig: dict[int, Any]) -> tuple[list[list[int]], str]:
    groups = defaultdict(list)
    canonical_map = []
    for v in sorted(sig):
        key = json.dumps(sig[v], sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        groups[key].append(v)
        canonical_map.append([v, sig[v]])
    out = [sorted(xs) for xs in groups.values()]
    out.sort(key=lambda xs:(xs[0],len(xs),xs))
    return out, canonical_sha(canonical_map)


def refines(p: list[list[int]], q: list[list[int]]) -> bool:
    qsets = [set(c) for c in q]
    return all(any(set(c) <= d for d in qsets) for c in p)


def compare(l3p: list[list[int]], skp: list[list[int]]) -> dict[str, Any]:
    a = refines(l3p, skp); b = refines(skp, l3p)
    if a and b: label='EQUAL'
    elif a: label='L3_STRICTLY_FINER_THAN_Sk'
    elif b: label='Sk_STRICTLY_FINER_THAN_L3'
    else: label='INCOMPARABLE'
    return {'l3_refines_sk':a,'sk_refines_l3':b,'relation':label}


def recompute_rows(expected_raw: dict[str,str]) -> list[dict[str,Any]]:
    rows=[]
    for name,(path,_) in SOURCES.items():
        clauses = projection_identity.parse(path)
        raw,_ = projection_identity.normalize_projection(name,clauses)
        raw_sha = canonical_sha(raw)
        assert raw_sha == expected_raw[name], (name,raw_sha,expected_raw[name])
        selected = projected_clauses(path)
        edges = [tuple(sorted(abs(x) for x in c)) for c in selected]
        V = sorted({v for e in edges for v in e})
        assert V == raw['variables'], (name,V,raw['variables'])
        feats = existing_features(raw,selected)
        sig = l3_signature(V,edges)
        l3p,l3map = partition_from_signature(sig)
        stages={}
        for level in LEVELS:
            skp = partition_from_level(feats,level)
            stages[level]={'sk_partition':skp,'sk_partition_sha256':canonical_sha(skp),**compare(l3p,skp)}
        rows.append({'source':name,'status':'AUDITED','raw_sha256':raw_sha,'variable_count':len(V),'l3_partition':l3p,'l3_partition_sha256':canonical_sha(l3p),'l3_signature_map_sha256':l3map,'stages':stages})
    return rows


def stage_summary(rows: list[dict[str,Any]]) -> tuple[dict[str,Any],list[str]]:
    summary={}; equiv=[]
    for level in LEVELS:
        rels={r['source']:r['stages'][level]['relation'] for r in rows}
        all_equal=all(x=='EQUAL' for x in rels.values())
        if all_equal: equiv.append(level)
        summary[level]={
            'relations_by_source':rels,
            'partition_equivalent_on_all_five_sources':all_equal,
            'l3_refines_stage_on_all_five_sources':all(r['stages'][level]['l3_refines_sk'] for r in rows),
            'stage_refines_l3_on_all_five_sources':all(r['stages'][level]['sk_refines_l3'] for r in rows),
            'strictly_finer_sources':[r['source'] for r in rows if r['stages'][level]['relation']=='L3_STRICTLY_FINER_THAN_Sk'],
            'strictly_coarser_sources':[r['source'] for r in rows if r['stages'][level]['relation']=='Sk_STRICTLY_FINER_THAN_L3'],
            'incomparable_sources':[r['source'] for r in rows if r['stages'][level]['relation']=='INCOMPARABLE'],
        }
    return summary,equiv


def main(candidate_path: Path) -> dict[str,Any]:
    bindings={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()}
    source_bindings={name:blob(path)==sha for name,(path,sha) in SOURCES.items()}
    assert all(bindings.values()) and all(source_bindings.values()), (bindings,source_bindings)
    pre=json.loads(PREREG.read_text())
    review=json.loads(REVIEW.read_text())
    assert pre['status']=='FROZEN_BEFORE_ANY_EQUIVALENCE_AUDIT_EXECUTION'
    assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
    candidate=json.loads(candidate_path.read_text().strip().splitlines()[-1])
    rows=recompute_rows(pre['frozen_projected_raw_sha256'])
    summary,equiv=stage_summary(rows)
    sanity={
        'UF20_01_L3_class_containing_7':next(c for c in rows[0]['l3_partition'] if 7 in c),
        'UF20_02_L3_all_singleton':all(len(c)==1 for c in rows[1]['l3_partition']),
        'UF20_03_L3_all_singleton':all(len(c)==1 for c in rows[2]['l3_partition']),
        'UF20_04_L3_all_singleton':all(len(c)==1 for c in rows[3]['l3_partition']),
        'UF20_05_L3_all_singleton':all(len(c)==1 for c in rows[4]['l3_partition']),
        'UF20_01_S3_non_singleton_classes':[c for c in rows[0]['stages']['S3']['sk_partition'] if len(c)>1],
        'UF20_03_S3_non_singleton_classes':[c for c in rows[2]['stages']['S3']['sk_partition'] if len(c)>1],
    }
    expected_sanity={k:v for k,v in pre['predeclared_sanity_receipts'].items() if k!='note'}
    assert sanity==expected_sanity,(sanity,expected_sanity)
    verdict='PASS_AUDIT_L3_PARTITION_EQUIVALENT_TO_EXISTING_STAGE__NOT_NOVEL' if equiv else 'PASS_SCOPED_PARTITION_NOVELTY_L3_NOT_EQUIVALENT_TO_ANY_EXISTING_STAGE'
    assert candidate['verdict']==verdict,(candidate['verdict'],verdict)
    assert candidate['rows']==rows
    assert candidate['stage_summary']==summary
    assert candidate['partition_equivalent_existing_stages']==equiv
    assert candidate['scoped_partition_novelty']==(not bool(equiv))
    assert candidate['sanity_receipts']==sanity
    rr=candidate['resource_receipt']
    assert rr['source_stage_partition_comparisons']==20 and rr['solver_invocations']==0 and rr['group_searches']==0
    assert rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0 and rr['budget_raise'] is False
    sf=candidate['scientific_firewall']
    assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO'
    return {'verified':True,'candidate_imported':False,'verdict':verdict,'partition_equivalent_existing_stages':equiv,'stage_summary':summary,'source_stage_partition_comparisons_verified':20}


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate-json',required=True)
    args=ap.parse_args()
    print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
