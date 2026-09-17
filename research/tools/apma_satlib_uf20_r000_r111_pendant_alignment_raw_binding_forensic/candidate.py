from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_ALIGNMENT_RAW_BINDING_FORENSIC_PREREGISTRATION_2026-09-17.json'
ALIGN = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_RESULT_2026-09-17.json'
EXPECTED = {
    PREREG: 'c0937e2b6115b3050250eebcd3f9505c9969884f',
    ALIGN: '9442fca30db3e623c56a33d8fda6c3a1e3c1f624',
}
SOURCES = {
    'UF20_02': (ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf', 'f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf', '8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf', '34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf', '3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}

def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()

def parse_clauses(path: Path):
    clauses=[]; buf=[]; header=None
    for raw in path.read_text(encoding='utf-8').splitlines():
        s=raw.strip()
        if not s or s.startswith('c') or s in {'%','0'}: continue
        if s.startswith('p '):
            p=s.split(); header=(int(p[2]),int(p[3])); continue
        for z in map(int,s.split()):
            if z==0:
                assert len(buf)==3 and len({abs(x) for x in buf})==3
                clauses.append(tuple(buf)); buf=[]
            else: buf.append(z)
    assert header==(20,91) and len(clauses)==91 and not buf
    return clauses

def is_core(clause):
    signs=[lit>0 for lit in clause]
    return all(signs) or not any(signs)

def scope_surface(source: str, clauses):
    out={}
    for ordinal,clause in enumerate(clauses,1):
        if not is_core(clause): continue
        cid=f'satlib_{source.lower()}_c{ordinal:03d}'
        out[cid]=sorted(abs(x) for x in clause)
    return out

def main():
    binding_guard={str(p.relative_to(ROOT)): blob(p)==h for p,h in EXPECTED.items()}
    source_guard={name: blob(path)==h for name,(path,h) in SOURCES.items()}
    assert all(binding_guard.values()) and all(source_guard.values())
    align=json.loads(ALIGN.read_text())
    rows=[]
    for sr in align['source_receipts']:
        source=sr['source']; path,_=SOURCES[source]
        surface=scope_surface(source,parse_clauses(path))
        scope_to_ids={}
        for cid,scope in surface.items(): scope_to_ids.setdefault(tuple(scope),[]).append(cid)
        for m in sr['mappings']:
            cid=m['constraint_id']; declared_scope=list(map(int,m['scope'])); leaf=int(m['singleton_variable']); gateway=sorted(map(int,m['gateway_pair']))
            exists=cid in surface; actual_scope=surface.get(cid)
            exact_ids=sorted(scope_to_ids.get(tuple(declared_scope),[]))
            declared_partition=(set(declared_scope)==set([leaf]+gateway) and len(declared_scope)==3)
            actual_partition=(actual_scope is not None and set(actual_scope)==set([leaf]+gateway) and len(actual_scope)==3)
            rows.append({
                'source':source,
                'declared_constraint_id':cid,
                'declared_scope':declared_scope,
                'declared_leaf':leaf,
                'declared_gateway_pair':gateway,
                'constraint_id_exists_in_frozen_projected_raw':exists,
                'actual_scope_for_declared_constraint_id':actual_scope,
                'declared_scope_equals_actual_scope':actual_scope==declared_scope,
                'declared_leaf_plus_gateway_equals_declared_scope_set':declared_partition,
                'declared_leaf_plus_gateway_equals_actual_scope_set':actual_partition,
                'constraint_ids_with_exact_declared_scope':exact_ids,
                'exact_declared_scope_match_count':len(exact_ids),
            })
    assert len(rows)==11
    exact=all(r['constraint_id_exists_in_frozen_projected_raw'] and r['declared_scope_equals_actual_scope'] and r['declared_leaf_plus_gateway_equals_declared_scope_set'] for r in rows)
    recoverable=all(r['declared_leaf_plus_gateway_equals_declared_scope_set'] and r['exact_declared_scope_match_count']==1 for r in rows)
    if exact:
        verdict='ALL_11_BINDINGS_EXACT'
    elif recoverable:
        verdict='ID_ONLY_MISMATCH_WITH_UNIQUE_SCOPE_RECOVERY'
    else:
        verdict='STRUCTURAL_BINDING_MISMATCH_NOT_RECOVERABLE_BY_SCOPE_ONLY'
    return {
        'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PENDANT-ALIGNMENT-RAW-BINDING-FORENSIC-CANDIDATE-2026-09-17-v1.0',
        'authority':'TECHNICAL_PROVENANCE_AND_COORDINATE_BINDING_FORENSIC_ONLY',
        'verdict':verdict,
        'rows':rows,
        'summary':{
            'row_count':len(rows),
            'exact_id_scope_binding_count':sum(r['declared_scope_equals_actual_scope'] for r in rows),
            'unique_scope_recovery_count':sum(r['exact_declared_scope_match_count']==1 for r in rows),
            'declared_partition_valid_count':sum(r['declared_leaf_plus_gateway_equals_declared_scope_set'] for r in rows),
        },
        'resource_receipt':{
            'target_sources':4,'target_mappings':11,'boundary_relation_enumerations':0,'boundary_assignment_enumerations':0,
            'allowed_table_value_reads':0,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'fresh_holdout_values_read':0
        },
        'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO'}
    }

if __name__=='__main__':
    print(json.dumps(main(),sort_keys=True,separators=(',',':')))
