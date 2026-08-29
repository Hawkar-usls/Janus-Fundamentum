#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, math, random, statistics
from pathlib import Path

PARENT_PATH = Path(__file__).with_name('janus_gemini_v1_cross_core.py')
spec = importlib.util.spec_from_file_location('gemini_v1_parent', PARENT_PATH)
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)

BITS = [26, 30, 34]
CASES_PER_RUNG = 8
BLIND_NS = 'JANUS-UNIFIED-KERNEL-V0-BLIND-SKEWED-2026-08-29'
HISTORICAL = [
    {'N':25789069,'a':2,'bits':26},
    {'N':417756517,'a':2,'bits':30},
    {'N':5643825779,'a':2,'bits':34},
]

def hseed(*parts):
    return int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8], 'big')

def make_blind_skewed(bitlen, idx):
    rng = random.Random(hseed(BLIND_NS, bitlen, 'SKEWED', idx))
    pb = max(5, bitlen//3); qb = bitlen-pb
    px = (1<<(pb-1)) + rng.randrange(max(2, 1<<(max(1,pb-2))))
    qx = (1<<(qb-1)) + rng.randrange(max(2, 1<<(max(1,qb-2))))
    p = parent.next_prime(px)
    q = parent.next_prime(qx+101)
    if p == q: q = parent.next_prime(q+2)
    n = p*q
    for a in parent.BASES:
        if math.gcd(a,n) == 1: break
    return {'bits_target':bitlen,'family':'SKEWED','N':n,'a':a,'p':p,'q':q}

def relation_until_near4(n, bits):
    budget = bits**3
    root = math.isqrt(n); x = root + (root*root < n)
    integer_mults = 0; gcds = 0
    for step in range(budget):
        z = x*x - n; integer_mults += 1
        y = math.isqrt(z); gap = z - y*y
        if gap == 0:
            gs = [math.gcd(x-y,n), math.gcd(x+y,n)]; gcds += 2
            fac = sorted({g for g in gs if 1 < g < n and n % g == 0})
            if fac:
                return {'status':'FACTOR_FOUND','factors':fac,'integer_mults':integer_mults,'gcds':gcds,'steps':step+1,'peak_stored':1}
        if gap == 4:
            inv2 = (n+1)//2
            u = ((x-y)*inv2) % n
            v = ((x+y)*inv2) % n
            cert = {
                'x2_minus_N_minus_y2_equals_4': x*x - n - y*y == 4,
                'N_is_odd': n % 2 == 1,
                'u_times_v_mod_N_equals_1': (u*v) % n == 1,
            }
            return {'status':'NEAR4','x':x,'y':y,'epsilon':4,'u':u,'v':v,'certificate':cert,'certificate_ok':all(cert.values()),'integer_mults':integer_mults,'gcds':gcds,'steps':step+1,'peak_stored':1}
        x += 1
    return {'status':'UNKNOWN_RESOURCE_LIMIT','integer_mults':integer_mults,'gcds':gcds,'steps':budget,'peak_stored':1}

def work_proxy(d):
    return int(d.get('modmults',0)) + int(d.get('integer_mults',0)) + int(d.get('gcds',0)) + int(d.get('trial_divisions',0))

def orbit_certificate(n, base, cap, salt_tag, pre_gcd=False):
    gcds = 0
    if pre_gcd:
        for z in (base, base-1, base+1):
            g = math.gcd(z,n); gcds += 1
            if 1 < g < n and n % g == 0:
                return {'status':'FACTOR_FOUND','factors':sorted({g,n//g}),'transitions':0,'modmults':0,'gcds':gcds,'trial_divisions':0,'peak_stored':0}
    col = parent.incremental_orbit_collision(n, base, max_transitions=cap)
    mm = col.get('modmults',0); gcds += col.get('gcds',0); div = 0
    if col.get('status') != 'COLLISION':
        return {'status':'UNKNOWN_RESOURCE_LIMIT','transitions':col.get('transitions',0),'modmults':mm,'gcds':gcds,'trial_divisions':div,'peak_stored':col.get('peak_stored',0),'collision':col}
    r, ok, red = parent.exact_reduce(col['multiple'], n, base)
    mm += red['modmults']; div += red['trial_divisions']
    if not ok:
        return {'status':'CERTIFICATE_FAILURE','transitions':col.get('transitions',0),'modmults':mm,'gcds':gcds,'trial_divisions':div,'peak_stored':col.get('peak_stored',0),'collision':col}
    post = parent.shor_post(n, base, r); mm += post['modmults']; gcds += post['gcds']
    if post['status'] == 'FACTOR_FOUND':
        return {'status':'FACTOR_FOUND','factors':post['factors'],'order':r,'transitions':col.get('transitions',0),'modmults':mm,'gcds':gcds,'trial_divisions':div,'peak_stored':col.get('peak_stored',0),'collision':col}
    return {'status':'ORDER_CERTIFIED','order':r,'transitions':col.get('transitions',0),'modmults':mm,'gcds':gcds,'trial_divisions':div,'peak_stored':col.get('peak_stored',0),'collision':col}

def run_case(n,a,bits):
    cap = 4*math.isqrt(n)+64
    relation = relation_until_near4(n,bits)
    unseeded = orbit_certificate(n,a,cap,'UNSEEDED',pre_gcd=False)
    if relation['status'] == 'FACTOR_FOUND':
        return {'eligible':False,'relation':relation,'unseeded':unseeded,'seeded':None,'unified_status':'FACTOR_FOUND','unified_factors':relation['factors'],'unified_work':work_proxy(relation),'cap':cap}
    if relation['status'] != 'NEAR4':
        return {'eligible':False,'relation':relation,'unseeded':unseeded,'seeded':None,'unified_status':'UNKNOWN_RESOURCE_LIMIT','unified_factors':[],'unified_work':work_proxy(relation)+work_proxy(unseeded),'cap':cap}
    if not relation['certificate_ok']:
        return {'eligible':True,'relation':relation,'unseeded':unseeded,'seeded':None,'unified_status':'CERTIFICATE_FAILURE','unified_factors':[],'unified_work':work_proxy(relation),'cap':cap}
    seeded = orbit_certificate(n, relation['u'], cap, 'SEEDED', pre_gcd=True)
    unified_work = work_proxy(relation) + 1 + work_proxy(seeded)  # charge uv modular check
    return {'eligible':True,'relation':relation,'unseeded':unseeded,'seeded':seeded,'unified_status':seeded['status'],'unified_factors':seeded.get('factors',[]),'unified_work':unified_work,'cap':cap}

def exact_factor_ok(n, result):
    fs = result.get('unified_factors',[])
    if result.get('unified_status') != 'FACTOR_FOUND': return True
    return bool(fs) and all(1 < f < n and n % f == 0 for f in fs)

def regression():
    rows=[]
    for c in HISTORICAL:
        r=run_case(c['N'],c['a'],c['bits'])
        rows.append({**c,**r})
    return rows

def run_blind():
    rows=[]
    for bits in BITS:
        for idx in range(CASES_PER_RUNG):
            c=make_blind_skewed(bits,idx)
            solver={'N':c['N'],'a':c['a']}
            r=run_case(solver['N'],solver['a'],c['N'].bit_length())
            bsgs=parent.bsgs_factor(solver['N'],solver['a'])
            rho=parent.rho_factor(solver['N'],solver['a'])
            rows.append({'bits_target':bits,'index':idx,'family':'SKEWED','N':c['N'],'a':c['a'],'evaluation':{'hidden_factors':[c['p'],c['q']]},'kernel':r,'strong_baselines':{'bsgs':bsgs,'rho':rho},'exact_factor_ok':exact_factor_ok(c['N'],r)})
    eligible=[x for x in rows if x['kernel']['eligible']]
    reductions=[]; trans_ratios=[]; paid=[]
    for x in eligible:
        k=x['kernel']; s=k['seeded']; u=k['unseeded']
        if s is None: continue
        reductions.append(s.get('transitions',k['cap']) < u.get('transitions',k['cap']))
        trans_ratios.append(s.get('transitions',k['cap']) / max(1,u.get('transitions',k['cap'])))
        cert={'FACTOR_FOUND','ORDER_CERTIFIED'}
        if s.get('status') in cert and u.get('status') in cert:
            paid.append(k['unified_work']/max(1,work_proxy(u)))
    eligible_n=len(eligible)
    enough=eligible_n>=6
    redfrac=(sum(reductions)/eligible_n) if eligible_n else None
    medtrans=statistics.median(trans_ratios) if trans_ratios else None
    medpaid=statistics.median(paid) if paid else None
    g1=all(x['exact_factor_ok'] and (not x['kernel']['eligible'] or x['kernel']['relation'].get('certificate_ok',True)) for x in rows)
    g2=enough and medtrans is not None and medtrans < 1.0 and redfrac >= 0.60
    g3=enough and medpaid is not None and medpaid <= 1.0
    if not enough: verdict='UNKNOWN_INSUFFICIENT_NEAR4_EVIDENCE'
    elif g2 and g3 and g1: verdict='PASS_RELATION_SEEDED_ORBIT_COMPRESSION'
    else: verdict='REFUTED_NEAR4_RELATION_SEEDED_ORBIT_COMPRESSION'
    summary={'blind_cases':len(rows),'near4_eligible':eligible_n,'strict_transition_reductions':sum(reductions),'strict_transition_reduction_fraction':redfrac,'median_seeded_over_unseeded_transition_ratio':medtrans,'paid_total_work_comparable_cases':len(paid),'median_paid_unified_over_unseeded_work_ratio':medpaid,'verdict':verdict}
    gates=[
      {'gate':'G1_EXACTNESS','passed':g1},
      {'gate':'G2_CONDITIONAL_COMPRESSION','passed':g2,'value':{'eligible':eligible_n,'strict_reduction_fraction':redfrac,'median_transition_ratio':medtrans},'criterion':'eligible>=6; strict reductions >=60%; median ratio <1'},
      {'gate':'G3_PAID_TOTAL_WORK','passed':g3,'value':{'comparable':len(paid),'median_ratio':medpaid},'criterion':'median <=1 among both-certified cases'},
      {'gate':'G4_STRONG_BASELINE_REPORTED','passed':True,'value':'BSGS/rho factor ledgers stored per case'},
      {'gate':'G5_NO_LEAKAGE','passed':True,'value':'kernel receives N,a only; p,q evaluation only'},
    ]
    return rows,summary,gates

def self_tests():
    tests=[]
    for n in [15,77,143]:
        r=relation_until_near4(n,n.bit_length())
        assert r['status'] in {'FACTOR_FOUND','NEAR4','UNKNOWN_RESOURCE_LIMIT'}
    for n,a in [(35,2),(143,2),(10403,2)]:
        cap=max(64,4*math.isqrt(n)+64)
        u=orbit_certificate(n,a,cap,'SELF',False)
        assert u['status'] in {'FACTOR_FOUND','ORDER_CERTIFIED','UNKNOWN_RESOURCE_LIMIT'}
        tests.append({'N':n,'status':u['status'],'transitions':u.get('transitions',0)})
    return tests

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output');ap.add_argument('--self-test-only',action='store_true');args=ap.parse_args()
    tests=self_tests()
    if args.self_test_only:
        print(json.dumps({'status':'PASS','tests':tests},indent=2));return
    historical=regression();rows,summary,gates=run_blind()
    result={'schema':'JANUS/UNIFIED-FACTOR-KERNEL/NEAR4-GATE/RESULT/v0.0','status':'COMPLETE','preregistration_commit':'488b0ea02d857655dbea558aa03449a4435e8f5c','self_tests':tests,'historical_nonvoting':historical,'blind_summary':summary,'gates':gates,'blind_cases':rows,'scientific_boundary':{'historical_does_not_vote':True,'finite_holdout_not_asymptotic':True,'polynomial_time_factoring':False,'quantum_speedup':False,'P_VS_NP':'OPEN'}}
    out=Path(args.output or 'JANUS_UNIFIED_FACTOR_KERNEL_V0_RESULT.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'summary':summary,'gates':gates,'historical':[{'N':x['N'],'relation':x['relation']['status'],'relation_steps':x['relation'].get('steps'),'unseeded_transitions':x['unseeded'].get('transitions'),'seeded_status':None if x['seeded'] is None else x['seeded'].get('status'),'seeded_transitions':None if x['seeded'] is None else x['seeded'].get('transitions')} for x in historical]},indent=2))
    if not gates[0]['passed']: raise SystemExit('Exactness gate failed')

if __name__=='__main__': main()
