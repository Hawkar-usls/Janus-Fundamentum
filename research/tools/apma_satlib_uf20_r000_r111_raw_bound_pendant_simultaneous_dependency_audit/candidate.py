from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_SIMULTANEOUS_DEPENDENCY_AUDIT_PREREGISTRATION_2026-09-17.json';REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_SIMULTANEOUS_DEPENDENCY_AUDIT_PREREGISTRATION_REVIEW_2026-09-17.json';BOUNDARY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17.json';RECON=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_D2_D3_WITNESS_RECONSTRUCTION_RESULT_2026-09-17.json'
EXPECTED={PREREG:'81c985cd3be76cee1286eff4fa91728e55a8adb9',REVIEW:'f40af28892a6e8762d9dc98a9438f710515e4348',BOUNDARY:'3a9d46cb888489e769bab1e7d292e4eff459f786',RECON:'d91e82fa2e558bb2926cc42b5f4368af51ae9c10'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05');SOURCES={'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def parse(path):
 out=[];buf=[]
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s.startswith('p ') or s in {'%','0'}:continue
  for z in map(int,s.split()):
   if z==0:out.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert len(out)==91 and not buf;return out
def surface(source,path):
 rows=[]
 for i,c in enumerate(parse(path),1):
  if sum(x>0 for x in c) in {0,3}:rows.append({'constraint_id':f'satlib_{source.lower()}_c{i:03d}','scope':sorted(abs(x) for x in c)})
 return rows
def has_cycle(nodes,edges):
 adj={n:[] for n in nodes}
 for a,b in edges:adj[a].append(b)
 seen=set();active=set()
 def dfs(u):
  seen.add(u);active.add(u)
  for v in adj[u]:
   if v not in seen and dfs(v):return True
   if v in active:return True
  active.remove(u);return False
 return any(n not in seen and dfs(n) for n in nodes)
def main():
 binds={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()};sb={n:blob(p)==h for n,(p,h) in SOURCES.items()};pre=json.loads(PREREG.read_text());rev=json.loads(REVIEW.read_text());b=json.loads(BOUNDARY.read_text());recon=json.loads(RECON.read_text());checks={'bindings':all(binds.values()),'sources':all(sb.values()),'boundary_all_universal':b['verdict']=='ALL_ELEVEN_UNIVERSAL','reconstruction_exact':recon['verdict']=='COMMON_FOUR_EXACT_RAW_BOUND_ALIGNMENT','review_authorized':rev['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'};guard={'ok':all(checks.values()),'checks':checks}
 if not guard['ok']:return {'verdict':'HALT_BINDING_FAILURE','source_guard':guard}
 br={r['source']:r['attachments'] for r in b['source_receipts']};rows=[]
 for source in ORDER:
  surf=surface(source,SOURCES[source][0]);byid={r['constraint_id']:r for r in surf};atts=br[source];ids=[a['constraint_id'] for a in atts];leaves=[int(a['leaf']) for a in atts];detail=[];edges=[]
  for a in atts:
   cid=a['constraint_id'];leaf=int(a['leaf']);assert cid in byid and byid[cid]['scope']==a['scope'];occ=[r['constraint_id'] for r in surf if leaf in r['scope']];nonown=[x for x in occ if x!=cid];detail.append({'constraint_id':cid,'leaf':leaf,'scope':a['scope'],'gateway':a['gateway'],'frozen_leaf_occurrence':a['leaf_occurrence'],'scope_surface_occurrence_count':len(occ),'occurring_constraint_ids':occ,'nonown_occurring_constraint_ids':nonown})
  for ai in atts:
   for aj in atts:
    if ai['constraint_id']==aj['constraint_id']:continue
    if int(ai['leaf']) in set(aj['scope']) or int(ai['leaf']) in set(aj['gateway']):edges.append([ai['constraint_id'],aj['constraint_id']])
  edges=sorted(edges);cyclic=has_cycle(ids,[tuple(x) for x in edges]);distinct_ids=len(ids)==len(set(ids));distinct_leaves=len(leaves)==len(set(leaves));all_occ=all(x['frozen_leaf_occurrence']==1 and x['scope_surface_occurrence_count']==1 and not x['nonown_occurring_constraint_ids'] for x in detail)
  label='ZERO_CROSS_ATTACHMENT_DEPENDENCY' if not edges and distinct_ids and distinct_leaves and all_occ else 'CYCLIC_DEPENDENCY' if cyclic else 'ACYCLIC_NONZERO_DEPENDENCY'
  rows.append({'source':source,'target_constraint_ids':ids,'target_leaves':leaves,'target_constraint_ids_distinct':distinct_ids,'target_leaves_distinct':distinct_leaves,'dependency_edges':edges,'dependency_edge_count':len(edges),'directed_cycle_present':cyclic,'leaf_occurrence_receipts':detail,'all_leaf_occurrence_and_nonown_checks_clean':all_occ,'per_source_outcome':label})
 labels=[r['per_source_outcome'] for r in rows];overall='ZERO_CROSS_ATTACHMENT_DEPENDENCY' if all(x=='ZERO_CROSS_ATTACHMENT_DEPENDENCY' for x in labels) else 'CYCLIC_DEPENDENCY' if any(x=='CYCLIC_DEPENDENCY' for x in labels) else 'ACYCLIC_NONZERO_DEPENDENCY'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-RAW-BOUND-PENDANT-SIMULTANEOUS-DEPENDENCY-AUDIT-CANDIDATE-2026-09-17-v1.0','authority':'READ_ONLY_CROSS_ATTACHMENT_DEPENDENCY_SYNTHESIS_FROM_FROZEN_RECEIPTS','verdict':overall,'source_guard':guard,'rows':rows,'resource_receipt':{'relation_table_value_reads':0,'boundary_relation_enumerations':0,'attachment_deletions':0,'projected_raw_modifications':0,'solver_invocations':0,'fresh_holdout_values_read':0},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO'}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
