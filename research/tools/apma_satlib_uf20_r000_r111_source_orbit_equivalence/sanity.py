from __future__ import annotations

import hashlib,json
from collections import Counter
from pathlib import Path

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SOURCE_ORBIT_CANONICAL_KEY_EQUIVALENCE_PROOF_PREREGISTRATION_2026-09-16.json'
PROOF=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SOURCE_ORBIT_CANONICAL_KEY_EQUIVALENCE_DIRECT_PROOF_2026-09-16.md'
EXPECTED={PREREG:'8bbf52bfd5dff47287e9ff22f1565739ce4756a5',PROOF:'d27e6d0919bd4e43ef4b395afc92bb5ae3cfdc6e',ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py':'a076cfc56d68aad0348415e313705da1f6b9cdcd'}
SOURCES={'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'}

def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def rtype(c):return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))
def source_multiset(path):
 m=Counter()
 for c in projection_identity.parse(path):
  r=rtype(c)
  if r in {'000','111'}:m[(r,tuple(sorted(abs(x) for x in c)))]+=1
 return m
def swap_scope(scope,u,v):return tuple(sorted(v if x==u else u if x==v else x for x in scope))
def swap_multiset(m,u,v):
 out=Counter()
 for (r,s),n in m.items():out[(r,swap_scope(s,u,v))]+=n
 return out
def row(source,pair,expected):
 path=SOURCES[source];raw,_=projection_identity.normalize_projection(source,projection_identity.parse(path));f=orbit.validate_and_normalize(raw);u,v=pair;m=source_multiset(path);sm=swap_multiset(m,u,v);base=orbit._formula_key(f);sw=orbit._formula_key_after_swap(f,u,v);closure=m==sm;keyeq=base==sw;pred=orbit.is_exact_transposition_automorphism(f,u,v);return {'source':source,'pair':pair,'expected':expected,'source_multiset_closure':closure,'sealed_key_equality':keyeq,'sealed_predicate_result':pred,'three_way_agreement':closure==keyeq==pred,'matches_expected':pred is expected,'source_item_count_with_multiplicity':sum(m.values()),'canonical_key_count':len(base)}
def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
 if not all(bindings.values()):return {'verdict':'BINDING_OR_CHECKER_FAILURE','bindings':bindings}
 pre=json.loads(PREREG.read_text());rows=[row(x['source'],x['pair'],x['expected_existing_predicate']) for x in pre['finite_sanity_controls']]
 verdict='PASS_SOURCE_ORBIT_CANONICAL_KEY_EQUIVALENCE_PROVED' if all(r['three_way_agreement'] and r['matches_expected'] for r in rows) else 'FINITE_SANITY_DISAGREES_WITH_PROOF'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-SOURCE-ORBIT-CANONICAL-KEY-EQUIVALENCE-SANITY-2026-09-16-v1.0','authority':'DIAGNOSTIC_DEFINITION_EQUIVALENCE_PROOF_SANITY_ONLY','verdict':verdict,'bindings':bindings,'direct_proof_blob':EXPECTED[PROOF],'rows':rows,'resource_receipt':{'new_pairs_tested':0,'solver_invocations':0,'new_signature_features':0,'new_invariants':0,'new_group_search_mechanisms':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','SOURCE_ORBIT_EQUIVALENCE_IMPLIES_TRACTABILITY':False,'SOURCE_ORBIT_DEFICIT_IMPLIES_HARDNESS':False,'NEW_INVARIANT_LICENSED':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
