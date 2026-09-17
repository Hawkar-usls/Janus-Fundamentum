from __future__ import annotations

import argparse,hashlib,json,sys
from collections import defaultdict
from pathlib import Path

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
CANDIDATE=ROOT/'research/tools/apma_uf20_026_075_prospective_wl_orbit_bridge/candidate.py'
SOURCE_FREEZE=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_RESULT_2026-09-17_v1.0.json'
PREREG=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW=ROOT/'research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_REVIEW_2026-09-17_v1.0.json'
EXPECTED={CANDIDATE:'8e48ea5ee1060a182343787e7949cb74ee256948',SOURCE_FREEZE:'5be45a07e7455876c2e9ff643350a8eaaf265ef2',PREREG:'d06753061f4f1f06397ecb83188c6a580645ab52',REVIEW:'f3df81e17396d3fbba67346bf95e73df13e2be38'}
ORDER=tuple(f'UF20_{i:03d}' for i in range(26,76));CANDIDATE_MODULE='research.tools.apma_uf20_026_075_prospective_wl_orbit_bridge.candidate'
def blob(path):
    d=path.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def canonical_sha(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def classes(colors,keys,value_of):
    groups=defaultdict(list)
    for k in keys:groups[colors[k]].append(int(value_of(k)))
    out=[sorted(v) for v in groups.values() if len(v)>1];out.sort(key=lambda x:(len(x),x));return out
def prediction(reduced):
    nodes,adj,labels=wl_ref.incidence_structure(reduced);variables=[n for n in nodes if n[0]=='v'];c1,r1=wl_ref.wl1(nodes,adj,labels);c2,r2=wl_ref.wl2(nodes,adj,labels);cl1=classes(c1,variables,lambda n:n[1]);diag=[(v,v) for v in variables];cl2=classes(c2,diag,lambda p:p[0][1]);pair=None;exact=None;checks=0
    if len(cl1)==1 and len(cl1[0])==2 and len(cl2)==1 and cl2[0]==cl1[0]:
        pair=cl1[0];checks=1;exact=orbit.is_exact_transposition_automorphism(orbit.validate_and_normalize(reduced),pair[0],pair[1])
    return {'wl1_nontrivial_variable_classes':cl1,'wl2_nontrivial_diagonal_variable_classes':cl2,'wl_rounds':{'wl1':r1,'wl2':r2},'wl_derived_pair':pair,'direct_exact_transposition_automorphism':exact,'prediction_positive':bool(pair is not None and exact is True),'direct_checks':checks}
def recompute():
    bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
    if not all(bindings.values()):return {'verdict':'HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE','bindings':bindings}
    if CANDIDATE_MODULE in sys.modules:return {'verdict':'HALT_INDEPENDENT_CANDIDATE_IMPORT_VIOLATION'}
    ok,training=frozen.training_regression()
    if not ok:return {'verdict':'HALT_INDEPENDENT_TRAINING_REGRESSION_FAILURE'}
    sf=json.loads(SOURCE_FREEZE.read_text());metadata={r['source']:r for r in sf['source_receipts']};preds=[];prepared=[];direct=0
    for source in ORDER:
        meta=metadata[source];path=ROOT/meta['committed_copy_path'];clauses,fh=frozen.parse_and_formula_hash(path);assert frozen.blob(path)==meta['committed_git_blob'] and fh==meta['canonical_formula_sha256'];raw=frozen.projection_identity.normalize_projection(source,clauses)[0];reduced,D,T=frozen.generic_round(raw);p=prediction(reduced);direct+=p.pop('direct_checks');preds.append({'source':source,'source_git_blob':frozen.blob(path),'canonical_formula_sha256':fh,'projected_raw_sha256':frozen.csha(raw),'reduced_raw_sha256':frozen.csha(reduced),'degree1_variables':D,'target_constraints':T,**p});prepared.append((source,reduced))
    assert len(preds)==50;digest=canonical_sha(preds);pb={r['source']:r for r in preds};e3_closed=[];misses=[];open_fp=[];popen=[];pclosed=[]
    for source,reduced in prepared:
        route=frozen.route_row(reduced);p=pb[source];e3=route.get('E3',{});ep=bool(e3.get('solver_authority') is True and e3.get('status') in frozen.CLOSED_ORBIT);edges=[sorted(map(int,e)) for e in (e3.get('generator_edges') or [])];recovered=bool(ep and p['prediction_positive'] and p['wl_derived_pair'] in edges);is_open=route.get('label')=='PORTFOLIO_OPEN';fp=bool(is_open and p['prediction_positive'])
        if ep:e3_closed.append(source)
        if ep and not recovered:misses.append(source)
        if fp:open_fp.append(source)
        (popen if is_open else pclosed).append(source)
    if misses:outcome='FALSIFIED_AT_LEAST_ONE_E3_CLOSED_CASE_NOT_RECOVERED_BY_FROZEN_WL_PAIR_RULE'
    elif open_fp:outcome='FALSIFIED_AT_LEAST_ONE_PORTFOLIO_OPEN_CASE_HAS_A_WL_DERIVED_DIRECT_EXACT_TRANSPOSITION_FALSE_POSITIVE'
    elif len(e3_closed)<2:outcome='PARTIAL_COVERAGE_FEWER_THAN_TWO_E3_CLOSED_CASES'
    else:outcome='PASS_PROSPECTIVE_MULTI_CLOSED_WL_TO_E3_WITNESS_REPLICATION'
    return {'verdict':'PASS_INDEPENDENT_PROSPECTIVE_WL_ORBIT_RECOMPUTATION','scientific_outcome':outcome,'candidate_imported':False,'prediction_stage_sha256':digest,'prediction_positive_sources':[r['source'] for r in preds if r['prediction_positive']],'e3_closed_sources':e3_closed,'e3_closed_misses':misses,'portfolio_open_sources':popen,'portfolio_closed_sources':pclosed,'open_false_positives':open_fp,'direct_exact_checks':direct,'prediction_full_transposition_searches':0,'signed_route_invocations':0}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);args=ap.parse_args();c=json.loads(Path(args.candidate).read_text());k=recompute()
    if k.get('verdict')!='PASS_INDEPENDENT_PROSPECTIVE_WL_ORBIT_RECOMPUTATION':return k
    s=c.get('summary',{});checks={'candidate_not_imported':k['candidate_imported'] is False,'prediction_digest':c.get('prediction_stage_sha256')==k['prediction_stage_sha256'],'prediction_positive_sources':s.get('wl_prediction_positive_sources')==k['prediction_positive_sources'],'e3_closed_sources':s.get('e3_closed_sources')==k['e3_closed_sources'],'e3_closed_misses':s.get('e3_closed_misses')==k['e3_closed_misses'],'portfolio_open_sources':s.get('portfolio_open_sources')==k['portfolio_open_sources'],'portfolio_closed_sources':s.get('portfolio_closed_sources')==k['portfolio_closed_sources'],'open_false_positives':s.get('open_false_positives')==k['open_false_positives'],'scientific_outcome':c.get('verdict')==k['scientific_outcome'],'resource_no_prediction_search':c.get('resource_receipt',{}).get('prediction_full_transposition_searches')==0 and k['prediction_full_transposition_searches']==0,'signed_route_zero':c.get('resource_receipt',{}).get('signed_route_invocations')==0 and k['signed_route_invocations']==0,'direct_checks_equal':c.get('resource_receipt',{}).get('prediction_direct_exact_checks')==k['direct_exact_checks']}
    return {**k,'comparison_checks':checks,'candidate_verdict':c.get('verdict'),'verdict':'PASS_INDEPENDENT_PROSPECTIVE_WL_ORBIT_BRIDGE_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_PROSPECTIVE_WL_ORBIT_BRIDGE_MISMATCH'}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
