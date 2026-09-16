from __future__ import annotations

import base64
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

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

def blob_bytes(data:bytes)->str:return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
def blob(path:Path)->str:return blob_bytes(path.read_bytes())
def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def fetch_blob(repo:str,sha:str)->bytes:
 req=urllib.request.Request(f'https://api.github.com/repos/{repo}/git/blobs/{sha}',headers={'User-Agent':'Janus-Fundamentum-fresh-blind-source-freeze/1.0','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=30) as r:payload=json.loads(r.read().decode())
 assert payload['sha']==sha and payload['encoding']=='base64',payload
 data=base64.b64decode(payload['content']);assert blob_bytes(data)==sha,(repo,sha);return data
def parse_dimacs(data:bytes)->dict[str,Any]:
 nvars=nclauses=None;clauses=[]
 for raw in data.decode('utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   p=s.split();assert p[:2]==['p','cnf'] and len(p)==4;nvars,nclauses=int(p[2]),int(p[3]);continue
  vals=[int(x) for x in s.split()];assert vals[-1]==0;clause=vals[:-1];assert len(clause)==3 and len({abs(x) for x in clause})==3;clauses.append(clause)
 assert nvars==20 and nclauses==91 and len(clauses)==91
 canonical=''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')
 return {'variables':nvars,'clauses':clauses,'canonical_formula_sha256':sha256(canonical)}
def guard():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
 local={name:blob(spec[1])==spec[2] for name,spec in SOURCES.items()}
 checks={'authority_bindings':all(binds.values()),'reservation_status':pre.get('status')=='FROZEN_BEFORE_RESERVED_SOURCE_CONTENT_FETCH_OR_INSPECTION','review_authorized':review.get('verdict')=='PASS_FRESH_BLIND_RESERVATION_PREREGISTRATION_CLEAN__AUTHORIZED_TO_ACQUIRE_AND_FREEZE_SOURCES_ONLY','selection_exact':tuple(pre['neutral_selection_rule']['reserved_future_holdout'])==ORDER,'local_primary_blob_bindings':all(local.values())}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds,'local_primary_blob_bindings':local}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','SUCCESSOR_INVARIANT_EXISTS':'NOT_ESTABLISHED'}
def main():
 g=guard()
 if not g['ok']:return {'verdict':'HALT_RESERVED_SOURCE_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 rows=[]
 for name in ORDER:
  filename,local_path,local_blob,primary_repo,primary_blob,verify_repo,verify_blob=SOURCES[name]
  local=local_path.read_bytes();primary=fetch_blob(primary_repo,primary_blob);verify=fetch_blob(verify_repo,verify_blob)
  lp,pp,vp=parse_dimacs(local),parse_dimacs(primary),parse_dimacs(verify)
  ordered_equal=lp['clauses']==pp['clauses']==vp['clauses'];canonical_equal=lp['canonical_formula_sha256']==pp['canonical_formula_sha256']==vp['canonical_formula_sha256']
  row_ok=ordered_equal and canonical_equal and local==primary and blob_bytes(local)==local_blob
  rows.append({'source':name,'filename':filename,'status':'SOURCE_FROZEN' if row_ok else 'SOURCE_MISMATCH','variables':20,'clauses':91,'clause_arity':3,'ordered_clause_sequence_equal_across_primary_verification_and_committed_copy':ordered_equal,'canonical_formula_sha256_equal_across_all_three':canonical_equal,'primary_repo':primary_repo,'primary_git_blob':primary_blob,'primary_raw_sha256':sha256(primary),'verification_repo':verify_repo,'verification_git_blob':verify_blob,'verification_raw_sha256':sha256(verify),'committed_git_blob':local_blob,'committed_raw_sha256':sha256(local),'canonical_formula_sha256':pp['canonical_formula_sha256'],'raw_bytes_primary_equal_committed_copy':local==primary,'raw_bytes_primary_equal_verification_mirror':primary==verify})
 passed=all(r['status']=='SOURCE_FROZEN' for r in rows)
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-SUCCESSOR-FRESH-BLIND-SOURCE-ACQUISITION-CANDIDATE-2026-09-17-v1.0','authority':'SOURCE_ACQUISITION_AND_DUAL_MIRROR_HASH_FREEZE_ONLY__NO_SUCCESSOR_FEATURE_DEFINITION_NO_PARTITION_VALUE_COMPUTATION','verdict':'PASS_FRESH_BLIND_SOURCE_ACQUISITION_AND_DUAL_MIRROR_FORMULA_FREEZE' if passed else 'HALT_FRESH_BLIND_SOURCE_ACQUISITION_MISMATCH','source_guard':g,'rows':rows,'resource_receipt':{'sources':5,'remote_blob_fetches':10,'successor_feature_definitions':0,'successor_graph_statistics':0,'successor_candidate_values':0,'projected_partition_values':0,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
