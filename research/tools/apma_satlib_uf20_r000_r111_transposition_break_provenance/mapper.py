from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_TRANSPOSITION_BREAK_SOURCE_PROVENANCE_PREREGISTRATION_2026-09-16.json'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXACT_TRANSPOSITION_WITNESS_LOCALIZATION_RESULT_2026-09-16.json'
SOURCE=ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'
EXPECTED={PREREG:'34e4f4cc8bc1a177c40d643759435a4d2e96bbce',PARENT:'ad05793643bca011d9ce9cd87fff9ae2a3e06181',SOURCE:'8f3d15154515457281f49201b843f2a7134dfa9f'}
SELECTED=set([2,4,8,29,38,40,49,57,61,72,74,75,79,81,84])

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()

def parse(path:Path):
 clauses=[];buf=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   x=s.split();assert len(x)==4 and x[1]=='cnf';header=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:
    assert len(buf)==3 and len({abs(x) for x in buf})==3
    clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(clauses)==91 and not buf
 return clauses

def relation_type(clause):
 ordered=sorted(clause,key=lambda x:abs(x))
 return ''.join('0' if lit>0 else '1' for lit in ordered)

def match_row(ordinal:int,clause):
 r=relation_type(clause)
 return {'ordinal':ordinal,'source_literals':list(clause),'normalized_literals':list(sorted(clause,key=lambda x:abs(x))),'scope':sorted(abs(x) for x in clause),'relation_type':r,'in_frozen_R000_R111_projection':ordinal in SELECTED,'relation_in_core':r in {'000','111'}}

def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
 if not all(bindings.values()):return {'verdict':'SOURCE_OR_PARENT_GUARD_FAILURE','source_guard':{'ok':False,'bindings':bindings}}
 pre=json.loads(PREREG.read_text());clauses=parse(SOURCE);by_scope=defaultdict(list)
 for i,c in enumerate(clauses,1):by_scope[tuple(sorted(abs(x) for x in c))].append(match_row(i,c))
 rows=[]
 for spec in pre['pinned_scope_witnesses']:
  scope=spec['scope'];matches=by_scope.get(tuple(scope),[]);counts=defaultdict(int)
  for m in matches:counts[m['relation_type']]+=1
  rows.append({'scope':scope,'witness_role':spec['witness_role'],'source_match_count':len(matches),'matches':matches,'R111_match_count':counts['111'],'R000_match_count':counts['000'],'other_relation_type_matches':[m for m in matches if m['relation_type'] not in {'000','111'}],'scope_absent_from_source':len(matches)==0})
 left=[r for r in rows if r['witness_role']=='BASE_LEFT_ONLY_R111'];right=[r for r in rows if r['witness_role']=='SWAPPED_RIGHT_ONLY_R111_IMAGE']
 if any(r['R111_match_count']==0 for r in left):verdict='LEFT_ONLY_WITNESS_NOT_FOUND_AS_R111_SOURCE_CLAUSE'
 elif any(r['R111_match_count']>0 for r in right):verdict='SWAP_IMAGE_R111_EXISTS_IN_SOURCE'
 else:verdict='PASS_SOURCE_PROVENANCE_LOCALIZED'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-TRANSPOSITION-BREAK-SOURCE-PROVENANCE-2026-09-16-v1.0','authority':'DIAGNOSTIC_SOURCE_PROVENANCE_MAPPING_ONLY__NO_NEW_INVARIANT_SOLVER_CARRIER_ADAPTER_QUOTIENT_OR_SEARCH','verdict':verdict,'source_guard':{'ok':True,'bindings':bindings},'source_clause_count':len(clauses),'pinned_pair':[4,20],'rows':rows,'resource_receipt':{'source_clauses_scanned':91,'pinned_scopes':4,'other_pairs_tested':0,'solver_invocations':0,'assignment_cube_enumerations':0,'new_signature_features':0,'new_invariants':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','SOURCE_PROVENANCE_PATTERN_IMPLIES_HARDNESS':False,'NEW_INVARIANT_LICENSED':False}}

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
