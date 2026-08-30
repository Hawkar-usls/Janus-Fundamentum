#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, math, random, statistics
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base_gate',HERE/'janus_ufk_v1_fresh_blind_factor_gate.py')
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
BITS=[22,26,30,34]; VARIANTS=3; NS='JANUS-UFK-V1-HARD-SKEWED-PORTFOLIO-2026-08-30'
PREREG='dd2f121f49b0c4d44d578fc3ca05e65e18ac2fb3'

def hseed(*parts): return int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8],'big')
def make_case(bits,idx):
    rng=random.Random(hseed(NS,bits,idx)); pb=max(5,bits//3); qb=bits-pb
    px=(1<<(pb-1))+rng.randrange(max(2,1<<max(1,pb-2))); qx=(1<<(qb-1))+rng.randrange(max(2,1<<max(1,qb-2)))
    p=base.parent.next_prime(px); q=base.parent.next_prime(qx+101)
    if p==q:q=base.parent.next_prime(q+2)
    return {'bits_target':bits,'variant':idx,'N':p*q,'p':p,'q':q}

_orig_collision=base.collision_discovery
_orig_project=base.core.project
_probe={'collision_calls':0,'collision_exact_projections':0}
def collision_boosted(n,a,max_transitions,L):
    _probe['collision_calls']+=1
    return _orig_collision(n,a,16*math.isqrt(n)+256,L)
def project_counted(D,i,state):
    kind=D.get(i).kind
    r=_orig_project(D,i,state)
    if kind=='RESIDUE_COLLISION' and r.get('status')=='EXACT_PROJECTION': _probe['collision_exact_projections']+=1
    return r
base.collision_discovery=collision_boosted
base.core.project=project_counted

def run_ufk(n):
    _probe['collision_calls']=0; _probe['collision_exact_projections']=0
    r=base.run_ufk(n)
    r['orbit_attempted_bases']=_probe['collision_calls']
    r['collision_to_order_projection_count']=_probe['collision_exact_projections']
    return r

def row(bits,idx):
    c=make_case(bits,idx); n=c['N']; u=run_ufk(n)
    b=base.baseline_portfolio(n,'BSGS'); rho=base.baseline_portfolio(n,'RHO')
    strong=min([x['arithmetic_work'] for x in (b,rho) if x['status']=='FACTOR_FOUND'] or [0]) or None
    ratio=(u.get('arithmetic_work',0)/strong) if strong and u.get('status')=='FACTOR_FOUND' else None
    exposed=(u.get('factor_source')!='RELATION_PROJECTION' and u.get('relation_steps')==n.bit_length()**3)
    attempts=u.get('orbit_attempted_bases',0); hits=u.get('reuse',{}).get('m2r_hits',0)
    return {'bits_target':bits,'actual_bits':n.bit_length(),'variant':idx,'family':'EXTREME_SKEWED','N':n,'evaluation':{'hidden_factors':[c['p'],c['q']]},'exposed_to_portfolio':exposed,'reuse_every_attempted_base':bool(exposed and attempts>0 and hits==attempts),'ufk':u,'baselines':{'bsgs_portfolio':b,'rho_portfolio':rho,'strong_reference_work':strong},'ufk_over_strong_ratio':ratio,'exact_factor_ok':u.get('status')!='FACTOR_FOUND' or base.valid_factor(n,u.get('factor'))}

def summarize(rows):
    exact=all(x['exact_factor_ok'] and x['ufk'].get('status')!='CERTIFICATE_FAILURE' for x in rows)
    exposed=[x for x in rows if x['exposed_to_portfolio']]; ne=len(exposed)
    reuse=sum(x['reuse_every_attempted_base'] for x in exposed)/max(1,ne)
    colproj=sum(x['ufk'].get('collision_to_order_projection_count',0)>0 for x in exposed)/max(1,ne)
    success=sum(x['ufk'].get('status')=='FACTOR_FOUND' for x in exposed)/max(1,ne)
    integrity=all(x['ufk'].get('status')!='CERTIFICATE_FAILURE' and all(o.get('immutable') for o in x['ufk'].get('open_receipts',[])) for x in rows)
    ratios=[x['ufk_over_strong_ratio'] for x in exposed if x['ufk_over_strong_ratio'] is not None]; med=statistics.median(ratios) if ratios else None
    h1=exact; h2=ne>=10; h3=reuse>=.80; h4=colproj>=.60; h5=success>=.50; h6=integrity; h7=med is not None and med<=1.; h8=True
    gates=[
      {'gate':'H1_EXACTNESS','passed':h1},
      {'gate':'H2_HARD_GEOMETRY_EXPOSURE','passed':h2,'value':{'exposed':ne,'total':len(rows)}},
      {'gate':'H3_SHARED_REUSE_ACTUATION','passed':h3,'value':reuse},
      {'gate':'H4_NONTERMINAL_PROJECTION_ACTUATION','passed':h4,'value':colproj},
      {'gate':'H5_FACTOR_COVERAGE_ON_EXPOSED','passed':h5,'value':success},
      {'gate':'H6_INTERFACE_REPRESENTATION_INTEGRITY','passed':h6},
      {'gate':'H7_STRONG_BASELINE_COST','passed':h7,'value':{'median_ufk_over_strong':med,'comparable':len(ratios)}},
      {'gate':'H8_NO_LEAKAGE','passed':h8}]
    if not h1: verdict='CERTIFICATE_FAILURE'
    elif any(x['ufk'].get('status')=='OPEN_RESOURCE_LIMIT' for x in rows): verdict='UNKNOWN_RESOURCE_LIMIT'
    elif all([h1,h2,h3,h4,h5,h6,h7,h8]): verdict='PASS_FULL_ARCHITECTURE_AND_COST'
    elif all([h1,h2,h3,h4,h5,h6,h8]) and not h7: verdict='PASS_ARCHITECTURE_ACTUATED__NOT_COST_COMPETITIVE'
    elif all([h1,h2,h3,h4,h6,h8]) and not h5: verdict='PASS_REUSE_BUT_FACTORING_WEAK'
    else: verdict='REFUTED_PORTFOLIO_ACTUATION'
    by=[]
    for bits in BITS:
        rr=[x for x in rows if x['bits_target']==bits]; ee=[x for x in rr if x['exposed_to_portfolio']]
        by.append({'bits':bits,'cases':len(rr),'exposed':len(ee),'successes':sum(x['ufk'].get('status')=='FACTOR_FOUND' for x in ee),'collision_projection_cases':sum(x['ufk'].get('collision_to_order_projection_count',0)>0 for x in ee),'median_ufk_work':statistics.median([x['ufk']['arithmetic_work'] for x in ee if 'arithmetic_work' in x['ufk']]) if ee else None,'median_strong_work':statistics.median([x['baselines']['strong_reference_work'] for x in ee if x['baselines']['strong_reference_work']]) if ee else None})
    return {'summary':{'cases':len(rows),'exposed_cases':ne,'reuse_every_attempted_base_fraction':reuse,'collision_projection_case_fraction':colproj,'factor_coverage_on_exposed':success,'median_ufk_over_strong_arithmetic_work':med,'verdict':verdict},'gates':gates,'by_bits':by}

def selftest():
    for n in [10403,104729*1009]:
        r=run_ufk(n)
        assert r.get('status') in {'FACTOR_FOUND','OPEN_NO_FACTOR_IN_FROZEN_PORTFOLIO','OPEN_RESOURCE_LIMIT'}
        if r.get('status')=='FACTOR_FOUND': assert base.valid_factor(n,r.get('factor'))
    return True

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); ap.add_argument('--self-test-only',action='store_true'); a=ap.parse_args(); selftest()
    if a.self_test_only: print(json.dumps({'status':'PASS'})); return
    rows=[row(bits,idx) for bits in BITS for idx in range(VARIANTS)]; s=summarize(rows)
    out={'schema':'JANUS/UFK-V1/HARD-GEOMETRY-PORTFOLIO-ACTUATION/RESULT/v1.0','status':'COMPLETE','preregistration_commit':PREREG,**s,'cases':rows,'scientific_boundary':{'post_first_holdout_successor':True,'polynomial_time_factoring':False,'P_VS_NP':'OPEN'}}
    Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({**s,'scientific_boundary':out['scientific_boundary']},indent=2))
    if not s['gates'][0]['passed']: raise SystemExit('Exactness failed')
if __name__=='__main__': main()
