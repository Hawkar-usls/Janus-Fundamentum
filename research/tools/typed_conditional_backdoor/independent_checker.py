import sys
from pathlib import Path as _P
_ROOT=_P(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path: sys.path.insert(0,str(_ROOT))
import itertools, json, math, random, time
from pathlib import Path
from research.tools.typed_conditional_backdoor.typed_backdoor import analyze, solve_forest


def hard_core(offset=0):
    horn=[]
    for signs in itertools.product((False,True), repeat=3):
        ids=[offset+(3+i if pos else i) for i,pos in enumerate(signs,start=1)]
        horn.append(tuple(-v for v in ids))
    affine=tuple(((1 << (offset+i-1)) | (1 << (offset+3+i-1)),1) for i in range(1,4))
    return tuple(horn),affine


def equality_neq():
    return ((-1,2),(1,-2)),((0b11,1),)


def easy_gadget(offset):
    s,y=offset+1,offset+2
    return ((-s,y),),(((1<<(s-1))|(1<<(y-1)),0),)


def combine(parts):
    h=[]; a=[]
    for x,y in parts: h.extend(x); a.extend(y)
    return tuple(h),tuple(a)


def eval_formula(horn, affine, bits, n):
    A={i+1:bool(bits[i]) for i in range(n)}
    for c in horn:
        if not any(A[abs(l)]==(l>0) for l in c): return False
    for mask,rhs in affine:
        p=0
        for v in range(1,n+1):
            if mask & (1<<(v-1)): p ^= int(A[v])
        if p!=rhs: return False
    return True


def brute_sat(horn, affine, n):
    return any(eval_formula(horn,affine,b,n) for b in itertools.product((0,1),repeat=n))


def covers(term,bits):
    return all(bool(bits[v-1])==bool(val) for v,val in term.items())


def hard_oracle(horn,affine):
    n=6; terminal=[]
    for vals in itertools.product((-1,0,1),repeat=n):
        q={i+1:bool(x) for i,x in enumerate(vals) if x!=-1}
        info=analyze(horn,affine,q)
        if info['terminal']:
            terminal.append({'term':q,'coverage':2**(n-len(q)),'sat':info['sat']})
    mx=max(x['coverage'] for x in terminal)
    return {'terminal_partial_assignments':len(terminal),'max_terminal_coverage':mx,'coverage_lower_bound_terms':math.ceil((2**n)/mx),'min_terminal_width':min(len(x['term']) for x in terminal)}


def captain_guard():
    text=Path(__file__).with_name('typed_backdoor.py').read_text(encoding='utf-8').lower()
    forbidden=['itertools.product','product(','brute_sat','dpll(','solve_all_assignments']
    hits=[x for x in forbidden if x in text]
    return {'pass':not hits,'hits':hits,'rule':'candidate may recursively split current mixed cores, but may not pre-enumerate the full cube or invoke a general SAT oracle'}


def random_controls(total=32,seed=20260913):
    rng=random.Random(seed); passed=0; fail=None
    for case in range(total):
        n=rng.randint(2,5); horn=[]; affine=[]
        for _ in range(rng.randint(1,7)):
            vs=rng.sample(range(1,n+1),rng.randint(1,min(3,n)))
            pos_used=False; c=[]
            for v in vs:
                pos=(not pos_used) and rng.random()<0.35
                if pos: pos_used=True
                c.append(v if pos else -v)
            horn.append(tuple(c))
        for _ in range(rng.randint(0,3)):
            vs=rng.sample(range(1,n+1),rng.randint(1,n)); mask=sum(1<<(v-1) for v in vs); affine.append((mask,rng.randint(0,1)))
        got=solve_forest(tuple(horn),tuple(affine))['sat']; want=brute_sat(tuple(horn),tuple(affine),n)
        if got==want: passed+=1
        elif fail is None: fail={'case':case,'horn':horn,'affine':affine,'got':got,'want':want}
    return {'passed':passed,'total':total,'seed':seed,'failure':fail}


def main():
    guard=captain_guard(); h,a=hard_core(); t0=time.perf_counter(); hard=solve_forest(h,a); hard_ms=1000*(time.perf_counter()-t0)
    terms=hard['generalized_terms'][0]; oracle=hard_oracle(h,a)
    taut=all(any(covers(t,b) for t in terms) for b in itertools.product((0,1),repeat=6))
    hard_exact=(hard['sat']==brute_sat(h,a,6) and not hard['sat'] and taut and all(analyze(h,a,t)['terminal'] for t in terms))
    eqh,eqa=equality_neq(); eq=solve_forest(eqh,eqa)
    easy=[]
    for k in (1,2,4,8,16):
        parts=[easy_gadget(2*i) for i in range(k)]; eh,ea=combine(parts); r=solve_forest(eh,ea)
        easy.append({'k':k,'explicit_joint_rows':2**k,'components':r['components'],'component_local_terms':r['metrics']['component_local_term_count'],'depth':r['metrics']['depth'],'visited_states':r['stats'].get('visited_states',0),'pass':r['components']==k and r['metrics']['component_local_term_count']<=2*k})
    disconnected=[]
    for k in (1,2,4,8):
        parts=[hard_core(6*i) for i in range(k)]; dh,da=combine(parts); r=solve_forest(dh,da)
        disconnected.append({'k':k,'naive_term_product':len(terms)**k,'components':r['components'],'stored_component_local_terms':r['metrics']['component_local_term_count'],'pass':r['components']==k and r['metrics']['component_local_term_count']==len(terms)*k})
    rnd=random_controls()
    lower=oracle['coverage_lower_bound_terms']; hard_terms=len(terms)
    all_ok=guard['pass'] and hard_exact and eq['sat'] is False and all(x['pass'] for x in easy+disconnected) and rnd['passed']==rnd['total']
    if not all_ok: verdict='FALSIFIED_EXACT_TERMINALITY'
    elif hard_terms < 8: verdict='PASS_SMALL_TYPED_BACKDOOR_DNF_ON_CONNECTED_MULTIROW_CORE'
    elif hard_terms==lower: verdict='PASS_SCOPED_COMPRESSION_BUT_HARD_CORE_REMAINS_EXPONENTIAL'
    else: verdict='NO_SMALL_TYPED_DNF_ON_FROZEN_CORE_WITHIN_FROZEN_POLICY'
    out={'schema':'JANUS_TRUMP_TYPED_CONDITIONAL_BACKDOOR_DNF_DEPTH_GATE_V1','verdict':verdict,'captain_obvious_guard':guard,'hard_core':{'sat':hard['sat'],'runtime_ms':round(hard_ms,3),'tree_metrics':hard['metrics'],'candidate_terms':[{str(k):int(v) for k,v in sorted(t.items())} for t in terms],'tautological_cover':taut,'oracle':oracle,'term_lower_bound_tight':hard_terms==lower},'equality_vs_disequality':{'sat':eq['sat'],'metrics':eq['metrics']},'synthetic_dnf_depth_family':easy,'disconnected_hard_core_family':disconnected,'random_exactness':rnd,'interpretation':'Backdoor DNF/depth can avoid cross-products across independent typed cores; the decisive question is whether the sealed connected multirow core admits a sub-exponential component-local conditional cover under the frozen typed terminal grammar.','scientific_status':{'SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0}}
    print(json.dumps(out,sort_keys=True))

if __name__=='__main__': main()
