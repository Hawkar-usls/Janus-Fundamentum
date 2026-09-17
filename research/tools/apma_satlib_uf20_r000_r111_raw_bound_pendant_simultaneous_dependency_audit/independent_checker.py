from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BOUNDARY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17.json'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf',
 'UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf',
 'UF20_04':ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf',
 'UF20_05':ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf',
}

def parse(path:Path):
    clauses=[];buf=[];header=None
    for raw in path.read_text(encoding='utf-8').splitlines():
        s=raw.strip()
        if not s or s.startswith('c') or s in {'%','0'}: continue
        if s.startswith('p '):
            p=s.split();header=(int(p[2]),int(p[3]));continue
        for z in map(int,s.split()):
            if z==0:
                assert len(buf)==3 and len({abs(x) for x in buf})==3
                clauses.append(tuple(buf));buf=[]
            else: buf.append(z)
    assert header==(20,91) and len(clauses)==91 and not buf
    return clauses

def surface(source:str,path:Path):
    rows=[]
    for ordinal,c in enumerate(parse(path),1):
        positives=sum(x>0 for x in c)
        if positives in {0,3}:
            rows.append({'constraint_id':f'satlib_{source.lower()}_c{ordinal:03d}','scope':sorted(abs(x) for x in c)})
    return rows

def cyclic_kahn(nodes,edges):
    adj={n:[] for n in nodes};indeg={n:0 for n in nodes}
    for a,b in edges:
        adj[a].append(b);indeg[b]+=1
    q=deque(sorted(n for n in nodes if indeg[n]==0));seen=0
    while q:
        u=q.popleft();seen+=1
        for v in sorted(adj[u]):
            indeg[v]-=1
            if indeg[v]==0:q.append(v)
    return seen!=len(nodes)

def expected_rows():
    boundary=json.loads(BOUNDARY.read_text())
    attachments={r['source']:r['attachments'] for r in boundary['source_receipts']}
    rows=[]
    for source in ORDER:
        surf=surface(source,SOURCES[source]);byid={r['constraint_id']:r for r in surf};atts=attachments[source]
        ids=[a['constraint_id'] for a in atts];leaves=[int(a['leaf']) for a in atts];details=[]
        for a in atts:
            cid=a['constraint_id'];leaf=int(a['leaf']);assert cid in byid and byid[cid]['scope']==a['scope']
            occ=sorted(r['constraint_id'] for r in surf if leaf in r['scope']);nonown=[x for x in occ if x!=cid]
            details.append({'constraint_id':cid,'leaf':leaf,'scope':a['scope'],'gateway':a['gateway'],'frozen_leaf_occurrence':a['leaf_occurrence'],'scope_surface_occurrence_count':len(occ),'occurring_constraint_ids':occ,'nonown_occurring_constraint_ids':nonown})
        edges=[]
        for ai in atts:
            for aj in atts:
                if ai['constraint_id']==aj['constraint_id']:continue
                if int(ai['leaf']) in set(aj['scope']) or int(ai['leaf']) in set(aj['gateway']):edges.append([ai['constraint_id'],aj['constraint_id']])
        edges=sorted(edges);cyclic=cyclic_kahn(ids,[tuple(x) for x in edges]);distinct_ids=len(ids)==len(set(ids));distinct_leaves=len(leaves)==len(set(leaves));clean=all(x['frozen_leaf_occurrence']==1 and x['scope_surface_occurrence_count']==1 and not x['nonown_occurring_constraint_ids'] for x in details)
        label='ZERO_CROSS_ATTACHMENT_DEPENDENCY' if not edges and distinct_ids and distinct_leaves and clean else 'CYCLIC_DEPENDENCY' if cyclic else 'ACYCLIC_NONZERO_DEPENDENCY'
        rows.append({'source':source,'target_constraint_ids':ids,'target_leaves':leaves,'target_constraint_ids_distinct':distinct_ids,'target_leaves_distinct':distinct_leaves,'dependency_edges':edges,'dependency_edge_count':len(edges),'directed_cycle_present':cyclic,'leaf_occurrence_receipts':details,'all_leaf_occurrence_and_nonown_checks_clean':clean,'per_source_outcome':label})
    return rows

def main(path:Path):
    candidate=json.loads(path.read_text().strip().splitlines()[-1]);rows=expected_rows();assert candidate['rows']==rows,(candidate['rows'],rows)
    labels=[r['per_source_outcome'] for r in rows]
    verdict='ZERO_CROSS_ATTACHMENT_DEPENDENCY' if all(x=='ZERO_CROSS_ATTACHMENT_DEPENDENCY' for x in labels) else 'CYCLIC_DEPENDENCY' if any(x=='CYCLIC_DEPENDENCY' for x in labels) else 'ACYCLIC_NONZERO_DEPENDENCY'
    assert candidate['verdict']==verdict
    rr=candidate['resource_receipt'];assert rr['relation_table_value_reads']==0 and rr['boundary_relation_enumerations']==0 and rr['attachment_deletions']==0 and rr['projected_raw_modifications']==0 and rr['solver_invocations']==0 and rr['fresh_holdout_values_read']==0
    return {'verified':True,'candidate_imported':False,'verdict':verdict,'rows':rows,'resource_receipt':rr}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
