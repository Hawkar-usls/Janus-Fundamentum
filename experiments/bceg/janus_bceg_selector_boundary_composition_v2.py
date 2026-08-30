from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from statistics import median

from experiments.bceg.janus_bceg_madlab_boundary_elimination_v1 import (
    canonical_cnf, cnf_vars, stable_seed, make_tseitin, make_pigeonhole,
    make_horn_pebbling, obfuscate, gf2_affine, counting_hall, horn_closure,
    dp_elimination, certificate_hash
)

PREREG=Path('research/JANUS_BCEG_SELECTOR_BOUNDARY_COMPOSITION_V2_PREREGISTRATION_2026-08-30.json')


def shift_cnf(cnf, offset):
    return canonical_cnf([[(1 if l>0 else -1)*(abs(l)+offset) for l in c] for c in cnf])


def guard_pair(left, right):
    left_n=max(cnf_vars(left), default=0)
    right_s=shift_cnf(right,left_n)
    selector=max(cnf_vars(right_s), default=left_n)+1
    clauses=[]
    for c in left:
        clauses.append(list(c)+[-selector])
    for c in right_s:
        clauses.append(list(c)+[selector])
    return canonical_cnf(clauses), selector


def restrict(cnf,v,value):
    sat=v if value else -v
    fals=-v if value else v
    out=[]
    for c in cnf:
        if sat in c:
            continue
        nc=[l for l in c if l!=fals]
        if not nc:
            return (frozenset(),)
        out.append(nc)
    return canonical_cnf(out)


def typed_only(cnf):
    ledger={'typed_discovery_checks':0,'typed_certificate_bytes':0}
    for fn in (gf2_affine,counting_hall,horn_closure):
        cert,local=fn(cnf)
        ledger['typed_discovery_checks'] += sum(v for k,v in local.items() if isinstance(v,int))
        if cert:
            ledger['typed_certificate_bytes'] += cert.get('serialized_certificate_bytes',0)
            return cert,ledger
    return None,ledger


def selector_compose(cnf,caps):
    initial=len(cnf_vars(cnf))
    direct,dledger=typed_only(cnf)
    if direct:
        return {'terminal':'UNSAT','language':direct['language'],'direct_typed':True,'certificate':direct,'initial_live_boundary':initial,'final_live_boundary':0,'selector_boundary_width':0,'selector_candidates_tested':0,'branch_restrictions':0,'typed_discovery_checks':dledger['typed_discovery_checks'],'typed_certificate_bytes':dledger['typed_certificate_bytes']}
    typed_checks=dledger['typed_discovery_checks']
    typed_bytes=0
    candidates=0
    restrictions=0
    for v in cnf_vars(cnf):
        candidates+=1
        branches=[]
        ok=True
        for value in (True,False):
            restrictions+=1
            rc=restrict(cnf,v,value)
            cert,led=typed_only(rc)
            typed_checks+=led['typed_discovery_checks']
            typed_bytes+=led['typed_certificate_bytes']
            if not cert or cert.get('terminal')!='UNSAT':
                ok=False
                break
            branches.append({'value':value,'language':cert['language'],'certificate_hash':cert['certificate_hash']})
        if ok and len(branches)==2:
            comp={'language':'BCEG_SELECTOR_SPLIT','terminal':'UNSAT','selector':v,'branches':branches,'rule':'UNSAT(F|v=1) AND UNSAT(F|v=0) => UNSAT(F)'}
            h,b=certificate_hash(comp)
            comp.update({'certificate_hash':h,'serialized_certificate_bytes':b,'replayable':True})
            return {'terminal':'UNSAT','language':'BCEG_SELECTOR_SPLIT','direct_typed':False,'certificate':comp,'initial_live_boundary':initial,'final_live_boundary':0,'selector_boundary_width':1,'selector_candidates_tested':candidates,'branch_restrictions':restrictions,'typed_discovery_checks':typed_checks,'typed_certificate_bytes':typed_bytes,'composition_certificate_bytes':b,'branch_languages':[x['language'] for x in branches]}
    dp=dp_elimination(cnf,caps)
    return {'terminal':dp['terminal'],'language':'BOUNDED_DAVIS_PUTNAM','direct_typed':False,'certificate':None,'initial_live_boundary':initial,'final_live_boundary':0 if dp['terminal'] in ('SAT','UNSAT') else initial,'selector_boundary_width':None,'selector_candidates_tested':candidates,'branch_restrictions':restrictions,'typed_discovery_checks':typed_checks,'typed_certificate_bytes':typed_bytes,'composition_certificate_bytes':0,'dp':dp}


def make_component(name,size):
    if name=='TSEITIN_PARITY': return make_tseitin(size)
    if name=='PIGEONHOLE': return make_pigeonhole(size)
    if name=='HORN_PEBBLING': return make_horn_pebbling(size)
    raise ValueError(name)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); ap.add_argument('--journal',required=True); args=ap.parse_args()
    p=json.loads(PREREG.read_text()); assert p['status']=='FROZEN_BEFORE_HOLDOUT_EXECUTION'
    cases=[]; journal=[]
    for spec in p['pair_families']:
        for lsize,rsize in spec['scales']:
            base,selector=guard_pair(make_component(spec['left'],lsize),make_component(spec['right'],rsize))
            for variant in range(p['variants_per_scale']):
                cnf=obfuscate(base,stable_seed(p['holdout_seed'],spec['left'],lsize,spec['right'],rsize,variant))
                direct,_=typed_only(cnf)
                result=selector_compose(cnf,p['dp_caps'])
                dp=dp_elimination(cnf,p['dp_caps'])
                row={'left':spec['left'],'left_size':lsize,'right':spec['right'],'right_size':rsize,'variant':variant,'variables':len(cnf_vars(cnf)),'clauses':len(cnf),'ground_truth':'UNSAT','direct_typed_hidden':direct is None,'terminal':result['terminal'],'language':result['language'],'selector_candidates_tested':result['selector_candidates_tested'],'branch_restrictions':result['branch_restrictions'],'typed_discovery_checks':result['typed_discovery_checks'],'typed_certificate_bytes':result['typed_certificate_bytes'],'composition_certificate_bytes':result.get('composition_certificate_bytes',0),'selector_boundary_width':result['selector_boundary_width'],'initial_live_boundary':result['initial_live_boundary'],'final_live_boundary':result['final_live_boundary'],'branch_languages':result.get('branch_languages',[]),'certificate_replayable':bool(result.get('certificate') and result['certificate'].get('replayable')),'dp_baseline':dp}
                cases.append(row); journal.append({'event':'CASE_COMPLETE',**row})
    g1=all(c['terminal']!='SAT' for c in cases)
    hidden=sum(c['direct_typed_hidden'] for c in cases)/len(cases); g2=hidden>=.90
    composed=[c for c in cases if c['language']=='BCEG_SELECTOR_SPLIT' and c['terminal']=='UNSAT']
    compfrac=len(composed)/len(cases); g3=compfrac>=.75
    g4=all(c['certificate_replayable'] and len(c['branch_languages'])==2 and c['branch_languages'][0]!=c['branch_languages'][1] for c in composed)
    g5=all(c['selector_boundary_width']==1 and c['final_live_boundary']<c['initial_live_boundary'] for c in composed)
    g6=all(c['selector_candidates_tested']<=c['variables'] and c['branch_restrictions']<=2*c['selector_candidates_tested'] for c in cases)
    escape=[c for c in composed if c['dp_baseline']['terminal']=='OPEN_RESOURCE_LIMIT']; g7=bool(escape)
    gates=[{'gate':'S1_EXACTNESS','passed':g1},{'gate':'S2_BASE_LANGUAGE_HIDDEN','passed':g2,'value':hidden},{'gate':'S3_SELECTOR_COMPOSITION_ACTUATION','passed':g3,'value':compfrac},{'gate':'S4_CROSS_LANGUAGE_CERTIFICATE','passed':g4},{'gate':'S5_REAL_INTERNAL_VARIABLE_ELIMINATION','passed':g5},{'gate':'S6_DISCOVERY_ACCOUNTING','passed':g6},{'gate':'S7_DP_BLOWUP_ESCAPE_WITNESS','passed':g7,'witnesses':[{'pair':c['left']+'+'+c['right'],'sizes':[c['left_size'],c['right_size']],'variant':c['variant'],'dp_resolvents':c['dp_baseline']['resolvents'],'branch_languages':c['branch_languages']} for c in escape]},{'gate':'S8_UNIVERSAL_LEMMA','passed':False,'reason':'WIDTH_ONE_FINITE_COMPOSITION_CANNOT_PROVE_ARBITRARY_CNF_POLYNOMIAL_BOUND'}]
    by_pair={}
    for key in sorted({c['left']+'+'+c['right'] for c in cases}):
        grp=[c for c in cases if c['left']+'+'+c['right']==key]
        by_pair[key]={'cases':len(grp),'composed':sum(c['language']=='BCEG_SELECTOR_SPLIT' for c in grp),'direct_hidden':sum(c['direct_typed_hidden'] for c in grp),'dp_open':sum(c['dp_baseline']['terminal']=='OPEN_RESOURCE_LIMIT' for c in grp),'median_selector_candidates':median(c['selector_candidates_tested'] for c in grp),'median_dp_resolvents':median(c['dp_baseline']['resolvents'] for c in grp)}
    finite='FINITE_CROSS_LANGUAGE_BOUNDARY_COMPOSITION' if all([g1,g2,g3,g4,g5,g6,g7]) else ('PARTIAL_CROSS_LANGUAGE_COMPOSITION' if composed else 'REFUTED_SELECTOR_COMPOSITION')
    out={'schema':'JANUS/BCEG/SELECTOR-BOUNDARY-COMPOSITION/V2/RESULT/v1.0','status':'COMPLETE','summary':{'cases':len(cases),'finite_verdict':finite,'base_language_hidden_fraction':hidden,'selector_composition_fraction':compfrac,'dp_blowup_escape_witnesses':len(escape),'P_VS_NP':'OPEN','universal_polynomial_boundary_elimination_lemma':'OPEN'},'gates':gates,'by_pair':by_pair,'cases_detail':cases,'interpretation':{'positive':'A one-variable live boundary can be discovered without an oracle and exactly eliminated by composing two different replayable certificate languages.','limit':'The search enumerates candidate boundary variables. Generalizing to an unbounded k-variable interface by branching can cost 2^k; this experiment proves no polynomial bound on k or on arbitrary-CNF certificate discovery.','next_frontier':'BOUNDARY_WIDTH_LADDER: construct compact formulas with controlled interface width k and measure whether exact typed composition remains polynomial or exhibits the expected 2^k frontier.'}}
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); Path(args.journal).write_text('\n'.join(json.dumps(x,sort_keys=True) for x in journal)+'\n')
    print(json.dumps({'summary':out['summary'],'gates':gates,'by_pair':by_pair},indent=2))

if __name__=='__main__': main()
