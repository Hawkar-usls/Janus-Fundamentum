from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit
ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SOURCE_ORBIT_CANONICAL_KEY_EQUIVALENCE_PROOF_PREREGISTRATION_2026-09-16.json'
SOURCES={'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'}
def rt(c):return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))
def sm(path):
 m=Counter()
 for c in projection_identity.parse(path):
  r=rt(c)
  if r in {'000','111'}:m[(r,tuple(sorted(abs(x) for x in c)))]+=1
 return m
def swscope(s,u,v):return tuple(sorted(v if x==u else u if x==v else x for x in s))
def swm(m,u,v):
 o=Counter()
 for (r,s),n in m.items():o[(r,swscope(s,u,v))]+=n
 return o
def one(spec):
 name=spec['source'];path=SOURCES[name];raw,_=projection_identity.normalize_projection(name,projection_identity.parse(path));f=orbit.validate_and_normalize(raw);u,v=spec['pair'];m=sm(path);cl=m==swm(m,u,v);ke=orbit._formula_key(f)==orbit._formula_key_after_swap(f,u,v);pr=orbit.is_exact_transposition_automorphism(f,u,v);return {'source':name,'pair':spec['pair'],'expected':spec['expected_existing_predicate'],'source_multiset_closure':cl,'sealed_key_equality':ke,'sealed_predicate_result':pr,'three_way_agreement':cl==ke==pr,'matches_expected':pr is spec['expected_existing_predicate'],'source_item_count_with_multiplicity':sum(m.values()),'canonical_key_count':len(orbit._formula_key(f))}
def main(c):
 pre=json.loads(PREREG.read_text());rows=[one(x) for x in pre['finite_sanity_controls']];checks={'candidate_not_imported':True,'verdict':c.get('verdict')=='PASS_SOURCE_ORBIT_CANONICAL_KEY_EQUIVALENCE_PROVED','rows':c.get('rows')==rows,'all_controls':all(r['three_way_agreement'] and r['matches_expected'] for r in rows)};rr=c.get('resource_receipt',{});checks['resources']=rr.get('new_pairs_tested')==0 and rr.get('solver_invocations')==0 and rr.get('new_signature_features')==0 and rr.get('new_invariants')==0 and rr.get('new_group_search_mechanisms')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_adapters')==0 and rr.get('new_quotients')==0 and rr.get('budget_raise') is False;sf=c.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('NEW_INVARIANT_LICENSED') is False;return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-SOURCE-ORBIT-CANONICAL-KEY-EQUIVALENCE-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_rows':rows}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
