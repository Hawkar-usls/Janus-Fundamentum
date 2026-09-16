from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXACT_TRANSPOSITION_WITNESS_LOCALIZATION_PREREGISTRATION_2026-09-16.json'
EXPECTED={
 PREREG:'b279a8f1134727e155e9abb0a73ec5e9f89a5093',
 ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_RESULT_2026-09-16.json':'b7ba5bd772c3092e0436dde8bd717dc28985983c',
 ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py':'a076cfc56d68aad0348415e313705da1f6b9cdcd',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f')}

def blob(path:Path)->str:
 d=path.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def key_bytes(key)->bytes:
 serial=[{'scope':list(scope),'allowed':[list(r) for r in rows]} for scope,rows in key]
 return json.dumps(serial,sort_keys=True,separators=(',',':')).encode()
def key_item(key,multiplicity:int)->dict[str,Any]:
 scope,rows=key
 return {'scope':list(scope),'allowed':[list(r) for r in rows],'multiplicity':multiplicity,'constraint_fingerprint':orbit._fingerprint_constraint(key)}
def diff_items(counter:Counter)->list[dict[str,Any]]:
 return [key_item(k,counter[k]) for k in sorted(counter)]
def one(source:str,pair:list[int],expected_raw:str,expected_predicate:bool):
 path=SOURCES[source][0];raw,_=projection_identity.normalize_projection(source,projection_identity.parse(path));raw_sha=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 if raw_sha!=expected_raw:return {'source':source,'pair':pair,'status':'PROJECTED_RAW_OR_SEALED_BINDING_GUARD_FAILURE','observed_raw_sha256':raw_sha}
 formula=orbit.validate_and_normalize(raw);u,v=pair;base=orbit._formula_key(formula);swapped=orbit._formula_key_after_swap(formula,u,v);predicate=orbit.is_exact_transposition_automorphism(formula,u,v);left=Counter(base)-Counter(swapped);right=Counter(swapped)-Counter(base);left_items=diff_items(left);right_items=diff_items(right)
 return {'source':source,'pair':pair,'status':'WITNESS_EXTRACTED','raw_sha256':raw_sha,'semantic_sha256':formula.semantic_sha256,'predicate_result':predicate,'expected_predicate_from_parent':expected_predicate,'predicate_matches_parent':predicate is expected_predicate,'base_key_sha256':hashlib.sha256(key_bytes(base)).hexdigest(),'swapped_key_sha256':hashlib.sha256(key_bytes(swapped)).hexdigest(),'base_key_equals_swapped_key':base==swapped,'constraint_multiset_size':len(base),'left_only_total_multiplicity':sum(left.values()),'right_only_total_multiplicity':sum(right.values()),'left_only_distinct_count':len(left),'right_only_distinct_count':len(right),'left_only':left_items,'right_only':right_items,'first_canonical_left_only':left_items[0] if left_items else None,'first_canonical_right_only':right_items[0] if right_items else None}
def main():
 binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={n:blob(p)==s for n,(p,s) in SOURCES.items()}
 if not all(binds.values()) or not all(sb.values()):return {'verdict':'PROJECTED_RAW_OR_SEALED_BINDING_GUARD_FAILURE','source_guard':{'ok':False,'bindings':binds,'source_bindings':sb}}
 pre=json.loads(PREREG.read_text());rows=[one(x['source'],x['pair'],x['projected_raw_sha256'],x['expected_predicate_from_parent']) for x in pre['pinned_pairs']]
 if any(r['status']!='WITNESS_EXTRACTED' for r in rows):verdict='PROJECTED_RAW_OR_SEALED_BINDING_GUARD_FAILURE'
 elif not all(r['predicate_matches_parent'] for r in rows):verdict='PINNED_PARENT_PREDICATE_OUTCOME_MISMATCH'
 else:
  a,b=rows
  if not a['base_key_equals_swapped_key'] or a['left_only_total_multiplicity'] or a['right_only_total_multiplicity']:verdict='PASSING_PAIR_KEY_MISMATCH'
  elif b['base_key_equals_swapped_key'] or (b['left_only_total_multiplicity']==0 and b['right_only_total_multiplicity']==0):verdict='FAILING_PAIR_HAS_NO_CANONICAL_DIFFERENCE'
  else:verdict='PASS_TRUE_PAIR_EQUALITY_AND_FALSE_PAIR_CANONICAL_MISMATCH_LOCALIZED'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-EXACT-TRANSPOSITION-WITNESS-LOCALIZATION-2026-09-16-v1.0','authority':'DIAGNOSTIC_EXISTING_PREDICATE_WITNESS_EXTRACTION_ONLY__NO_NEW_INVARIANT_GROUP_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT','verdict':verdict,'source_guard':{'ok':True,'bindings':binds,'source_bindings':sb},'rows':rows,'resource_receipt':{'pinned_pairs_tested':2,'other_pairs_tested':0,'solver_invocations':0,'assignment_cube_enumerations':0,'new_signature_features':0,'new_group_search_mechanisms':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','WITNESS_DIFFERENCE_IMPLIES_HARDNESS':False,'WITNESS_EQUALITY_IMPLIES_TRACTABILITY':False,'NEW_INVARIANT_LICENSED':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
