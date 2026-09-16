from __future__ import annotations

import argparse,base64,hashlib,json,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_RESERVATION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_RESERVATION_PREREGISTRATION_REVIEW_2026-09-17.json'
TRANSFER=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_PARTITION_NOVELTY_TEN_SOURCE_TRANSFER_SYNTHESIS_RESULT_2026-09-17.json'
EXPECTED={PREREG:'7d4f61a66b4b90b95873597cd5e91ece11460f8c',REVIEW:'61c64e6a7f33cbed5e998c50eff187462f2e4af0',TRANSFER:'82d11ac4b8920f276b1966186abd2066a75c8171'}
ORDER=('UF20_011','UF20_012','UF20_013','UF20_014','UF20_015')
SOURCES={
 'UF20_011':('uf20-011.cnf',ROOT/'research/source_data/SATLIB_UF20_011_2026-09-17.cnf','d693e2c019a1ceb7abe1bf1c29ffd57d25cde01b','Jany26/tree-aut-lib','d693e2c019a1ceb7abe1bf1c29ffd57d25cde01b','dncarley/MolecularSimulation','ee07729fe8934188e1c1a4294710e16b756a562e'),
 'UF20_012':('uf20-012.cnf',ROOT/'research/source_data/SATLIB_UF20_012_2026-09-17.cnf','745e26942701ca6bcb3f9708e9306d7e6385ecdc','Jany26/tree-aut-lib','745e26942701ca6bcb3f9708e9306d7e6385ecdc','dncarley/MolecularSimulation','8d55531b37460cffd379d882c2ff268a59f78608'),
 'UF20_013':('uf20-013.cnf',ROOT/'research/source_data/SATLIB_UF20_013_2026-09-17.cnf','62349f4152b5ce1576e380242e7d62bbe2099907','Jany26/tree-aut-lib','62349f4152b5ce1576e380242e7d62bbe2099907','dncarley/MolecularSimulation','4f9c98d14718893f6ee6a356fb6e34a88006c0f3'),
 'UF20_014':('uf20-014.cnf',ROOT/'research/source_data/SATLIB_UF20_014_2026-09-17.cnf','9d2c03f1bd246ebcf0892722b522b82bbe07452f','Jany26/tree-aut-lib','9d2c03f1bd246ebcf0892722b522b82bbe07452f','dncarley/MolecularSimulation','026e56e97f8bbd8dce58aab991b2842f152546f4'),
 'UF20_015':('uf20-015.cnf',ROOT/'research/source_data/SATLIB_UF20_015_2026-09-17.cnf','09e4581c3281d62390731e553c2eab48c421166c','Jany26/tree-aut-lib','09e4581c3281d62390731e553c2eab48c421166c','dncarley/MolecularSimulation','bdf4f5bd0f5c409681939a1f3e2e671bb630fbba')}

def gblob(data:bytes)->str:return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
def blob(path:Path)->str:return gblob(path.read_bytes())
def h256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def remote(repo,sha):
 req=urllib.request.Request(f'https://api.github.com/repos/{repo}/git/blobs/{sha}',headers={'User-Agent':'Janus-Fundamentum-fresh-blind-source-freeze-independent/1.0','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=30) as r:p=json.loads(r.read().decode())
 assert p['sha']==sha and p['encoding']=='base64';data=base64.b64decode(p['content']);assert gblob(data)==sha;return data
def parse(data:bytes):
 n=m=None;clauses=[]
 for raw in data.decode().splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in ('%','0'):continue
  if s.startswith('p '):x=s.split();assert x[:2]==['p','cnf'] and len(x)==4;n,m=int(x[2]),int(x[3]);continue
  x=[int(z) for z in s.split()];assert len(x)==4 and x[-1]==0;c=x[:-1];assert len(set(map(abs,c)))==3;clauses.append(c)
 assert n==20 and m==91 and len(clauses)==91
 canon=''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')
 return clauses,h256(canon)
def expected_rows():
 assert all(blob(p)==sha for p,sha in EXPECTED.items())
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 assert tuple(pre['neutral_selection_rule']['reserved_future_holdout'])==ORDER
 assert review['verdict']=='PASS_FRESH_BLIND_RESERVATION_PREREGISTRATION_CLEAN__AUTHORIZED_TO_ACQUIRE_AND_FREEZE_SOURCES_ONLY'
 rows=[]
 for name in ORDER:
  filename,local_path,local_blob,pr,ps,vr,vs=SOURCES[name]
  local=local_path.read_bytes();assert gblob(local)==local_blob
  primary=remote(pr,ps);verify=remote(vr,vs)
  lc,lsha=parse(local);pc,psha=parse(primary);vc,vsha=parse(verify)
  ordered=lc==pc==vc;canonical= lsha==psha==vsha
  status='SOURCE_FROZEN' if ordered and canonical and local==primary else 'SOURCE_MISMATCH'
  rows.append({'source':name,'filename':filename,'status':status,'variables':20,'clauses':91,'clause_arity':3,'ordered_clause_sequence_equal_across_primary_verification_and_committed_copy':ordered,'canonical_formula_sha256_equal_across_all_three':canonical,'primary_repo':pr,'primary_git_blob':ps,'primary_raw_sha256':h256(primary),'verification_repo':vr,'verification_git_blob':vs,'verification_raw_sha256':h256(verify),'committed_git_blob':local_blob,'committed_raw_sha256':h256(local),'canonical_formula_sha256':psha,'raw_bytes_primary_equal_committed_copy':local==primary,'raw_bytes_primary_equal_verification_mirror':primary==verify})
 return rows
def main(candidate:Path):
 c=json.loads(candidate.read_text().strip().splitlines()[-1]);rows=expected_rows();assert c['rows']==rows,(c['rows'],rows)
 verdict='PASS_FRESH_BLIND_SOURCE_ACQUISITION_AND_DUAL_MIRROR_FORMULA_FREEZE' if all(r['status']=='SOURCE_FROZEN' for r in rows) else 'HALT_FRESH_BLIND_SOURCE_ACQUISITION_MISMATCH'
 assert c['verdict']==verdict
 rr=c['resource_receipt'];assert rr['sources']==5 and rr['remote_blob_fetches']==10 and rr['successor_feature_definitions']==0 and rr['successor_graph_statistics']==0 and rr['successor_candidate_values']==0 and rr['projected_partition_values']==0
 assert rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'sources_verified':5,'rows':rows,'successor_candidate_values':0,'projected_partition_values':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(Path(a.candidate_json)),sort_keys=True,separators=(',',':')))
