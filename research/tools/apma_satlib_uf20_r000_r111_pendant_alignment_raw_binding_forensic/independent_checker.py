from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ALIGN=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_RESULT_2026-09-17.json'
SOURCES={
 'UF20_02':ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf',
 'UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf',
 'UF20_04':ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf',
 'UF20_05':ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf',
}

def clauses(path):
 out=[]; cur=[]
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s.startswith('p ') or s in {'%','0'}: continue
  for z in map(int,s.split()):
   if z==0: out.append(tuple(cur));cur=[]
   else: cur.append(z)
 assert len(out)==91 and not cur
 return out

def frozen_surface(source,path):
 d={}
 for i,c in enumerate(clauses(path),1):
  pos=sum(x>0 for x in c)
  if pos not in {0,3}: continue
  d[f'satlib_{source.lower()}_c{i:03d}']=sorted(abs(x) for x in c)
 return d

def expected():
 a=json.loads(ALIGN.read_text()); rows=[]
 for sr in a['source_receipts']:
  source=sr['source']; surf=frozen_surface(source,SOURCES[source]); byscope={}
  for cid,scope in surf.items(): byscope.setdefault(tuple(scope),[]).append(cid)
  for m in sr['mappings']:
   cid=m['constraint_id']; ds=list(map(int,m['scope'])); leaf=int(m['singleton_variable']); gw=sorted(map(int,m['gateway_pair'])); actual=surf.get(cid); exact_ids=sorted(byscope.get(tuple(ds),[]))
   rows.append({'source':source,'declared_constraint_id':cid,'declared_scope':ds,'declared_leaf':leaf,'declared_gateway_pair':gw,'constraint_id_exists_in_frozen_projected_raw':cid in surf,'actual_scope_for_declared_constraint_id':actual,'declared_scope_equals_actual_scope':actual==ds,'declared_leaf_plus_gateway_equals_declared_scope_set':set(ds)==set([leaf]+gw) and len(ds)==3,'declared_leaf_plus_gateway_equals_actual_scope_set':actual is not None and set(actual)==set([leaf]+gw) and len(actual)==3,'constraint_ids_with_exact_declared_scope':exact_ids,'exact_declared_scope_match_count':len(exact_ids)})
 return rows

def main(path):
 c=json.loads(Path(path).read_text().strip().splitlines()[-1]); rows=expected(); assert c['rows']==rows
 exact=all(r['constraint_id_exists_in_frozen_projected_raw'] and r['declared_scope_equals_actual_scope'] and r['declared_leaf_plus_gateway_equals_declared_scope_set'] for r in rows)
 recover=all(r['declared_leaf_plus_gateway_equals_declared_scope_set'] and r['exact_declared_scope_match_count']==1 for r in rows)
 verdict='ALL_11_BINDINGS_EXACT' if exact else 'ID_ONLY_MISMATCH_WITH_UNIQUE_SCOPE_RECOVERY' if recover else 'STRUCTURAL_BINDING_MISMATCH_NOT_RECOVERABLE_BY_SCOPE_ONLY'
 assert c['verdict']==verdict
 rr=c['resource_receipt']; assert rr['boundary_relation_enumerations']==0 and rr['allowed_table_value_reads']==0 and rr['solver_invocations']==0 and rr['fresh_holdout_values_read']==0
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'rows':rows,'resource_receipt':rr}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--candidate-json',required=True);a=p.parse_args();print(json.dumps(main(a.candidate_json),sort_keys=True,separators=(',',':')))
