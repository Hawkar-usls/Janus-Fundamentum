from __future__ import annotations

import argparse, hashlib, json
from collections import Counter
from pathlib import Path

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXACT_TRANSPOSITION_WITNESS_LOCALIZATION_PREREGISTRATION_2026-09-16.json'
SOURCES={'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'}

def key_json(key):return [{'scope':list(s),'allowed':[list(r) for r in rows]} for s,rows in key]
def kb(key):return json.dumps(key_json(key),sort_keys=True,separators=(',',':')).encode()
def item(k,n):
 s,rows=k;return {'scope':list(s),'allowed':[list(r) for r in rows],'multiplicity':n,'constraint_fingerprint':orbit._fingerprint_constraint(k)}
def items(c):return [item(k,c[k]) for k in sorted(c)]
def row(spec):
 name=spec['source'];raw,_=projection_identity.normalize_projection(name,projection_identity.parse(SOURCES[name]));raw_sha=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();assert raw_sha==spec['projected_raw_sha256'];f=orbit.validate_and_normalize(raw);u,v=spec['pair'];base=orbit._formula_key(f);sw=orbit._formula_key_after_swap(f,u,v);pred=orbit.is_exact_transposition_automorphism(f,u,v);l=Counter(base)-Counter(sw);r=Counter(sw)-Counter(base);li=items(l);ri=items(r);return {'source':name,'pair':spec['pair'],'status':'WITNESS_EXTRACTED','raw_sha256':raw_sha,'semantic_sha256':f.semantic_sha256,'predicate_result':pred,'expected_predicate_from_parent':spec['expected_predicate_from_parent'],'predicate_matches_parent':pred is spec['expected_predicate_from_parent'],'base_key_sha256':hashlib.sha256(kb(base)).hexdigest(),'swapped_key_sha256':hashlib.sha256(kb(sw)).hexdigest(),'base_key_equals_swapped_key':base==sw,'constraint_multiset_size':len(base),'left_only_total_multiplicity':sum(l.values()),'right_only_total_multiplicity':sum(r.values()),'left_only_distinct_count':len(l),'right_only_distinct_count':len(r),'left_only':li,'right_only':ri,'first_canonical_left_only':li[0] if li else None,'first_canonical_right_only':ri[0] if ri else None}
def main(candidate):
 pre=json.loads(PREREG.read_text());rows=[row(s) for s in pre['pinned_pairs']];checks={'candidate_not_imported':True,'rows':candidate.get('rows')==rows,'verdict':candidate.get('verdict')=='PASS_TRUE_PAIR_EQUALITY_AND_FALSE_PAIR_CANONICAL_MISMATCH_LOCALIZED'};a,b=rows;checks['pass_pair']=a['predicate_result'] is True and a['base_key_equals_swapped_key'] and a['left_only_total_multiplicity']==0 and a['right_only_total_multiplicity']==0;checks['fail_pair']=b['predicate_result'] is False and not b['base_key_equals_swapped_key'] and b['left_only_total_multiplicity']>0 and b['right_only_total_multiplicity']>0;rr=candidate.get('resource_receipt',{});checks['resources']=rr.get('pinned_pairs_tested')==2 and rr.get('other_pairs_tested')==0 and rr.get('solver_invocations')==0 and rr.get('assignment_cube_enumerations')==0 and rr.get('new_signature_features')==0 and rr.get('new_group_search_mechanisms')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_adapters')==0 and rr.get('new_quotients')==0 and rr.get('budget_raise') is False;sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('NEW_INVARIANT_LICENSED') is False;return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-EXACT-TRANSPOSITION-WITNESS-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_rows':rows}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
