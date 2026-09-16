from __future__ import annotations

import argparse,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_TRANSPOSITION_BREAK_SOURCE_PROVENANCE_PREREGISTRATION_2026-09-16.json'
SOURCE=ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'
SELECTED=set([2,4,8,29,38,40,49,57,61,72,74,75,79,81,84])

def parse(path):
 cs=[];buf=[];header=None
 for raw in path.read_text().splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();header=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3 and len({abs(x) for x in buf})==3;cs.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(cs)==91 and not buf;return cs

def rtype(c):return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))
def mrow(i,c):
 r=rtype(c);return {'ordinal':i,'source_literals':list(c),'normalized_literals':list(sorted(c,key=lambda x:abs(x))),'scope':sorted(abs(x) for x in c),'relation_type':r,'in_frozen_R000_R111_projection':i in SELECTED,'relation_in_core':r in {'000','111'}}
def expected_rows():
 pre=json.loads(PREREG.read_text());by=defaultdict(list)
 for i,c in enumerate(parse(SOURCE),1):by[tuple(sorted(abs(x) for x in c))].append(mrow(i,c))
 out=[]
 for spec in pre['pinned_scope_witnesses']:
  ms=by.get(tuple(spec['scope']),[]);cnt=defaultdict(int)
  for m in ms:cnt[m['relation_type']]+=1
  out.append({'scope':spec['scope'],'witness_role':spec['witness_role'],'source_match_count':len(ms),'matches':ms,'R111_match_count':cnt['111'],'R000_match_count':cnt['000'],'other_relation_type_matches':[m for m in ms if m['relation_type'] not in {'000','111'}],'scope_absent_from_source':len(ms)==0})
 return out

def main(candidate):
 rows=expected_rows();left=[r for r in rows if r['witness_role']=='BASE_LEFT_ONLY_R111'];right=[r for r in rows if r['witness_role']=='SWAPPED_RIGHT_ONLY_R111_IMAGE'];expected='LEFT_ONLY_WITNESS_NOT_FOUND_AS_R111_SOURCE_CLAUSE' if any(r['R111_match_count']==0 for r in left) else 'SWAP_IMAGE_R111_EXISTS_IN_SOURCE' if any(r['R111_match_count']>0 for r in right) else 'PASS_SOURCE_PROVENANCE_LOCALIZED';checks={'candidate_not_imported':True,'verdict':candidate.get('verdict')==expected,'source_clause_count':candidate.get('source_clause_count')==91,'pair':candidate.get('pinned_pair')==[4,20],'rows':candidate.get('rows')==rows};rr=candidate.get('resource_receipt',{});checks['resources']=rr.get('source_clauses_scanned')==91 and rr.get('pinned_scopes')==4 and rr.get('other_pairs_tested')==0 and rr.get('solver_invocations')==0 and rr.get('assignment_cube_enumerations')==0 and rr.get('new_signature_features')==0 and rr.get('new_invariants')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_adapters')==0 and rr.get('new_quotients')==0 and rr.get('budget_raise') is False;sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('NEW_INVARIANT_LICENSED') is False;return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-TRANSPOSITION-BREAK-SOURCE-PROVENANCE-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_rows':rows,'independent_expected_verdict':expected}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
