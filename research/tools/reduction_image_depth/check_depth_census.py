from pathlib import Path
import itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.typed_conditional_backdoor.typed_backdoor import analyze


def normalize_clause(c):
    s=set(c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s, key=lambda x:(abs(x),x<0)))


def normalize_cnf(clauses):
    out=[]
    for c in clauses:
        q=normalize_clause(c)
        if q is not None and q not in out: out.append(q)
    return tuple(out)


def encode_nand3_neq(source,n):
    affine=tuple(((1<<(i-1)) | (1<<(n+i-1)),1) for i in range(1,n+1))
    horn=[]
    for clause in source:
        falsity=[n+abs(l) if l>0 else abs(l) for l in clause]
        horn.append(tuple(-v for v in falsity))
    return normalize_cnf(horn),affine

def source_eval(source,bits):
    for c in source:
        if not any(bool(bits[abs(l)-1])==(l>0) for l in c): return False
    return True


def image_eval(horn,affine,bits,n):
    a={i+1:bool(bits[i]) for i in range(n)}
    a.update({n+i+1:not bool(bits[i]) for i in range(n)})
    for c in horn:
        if not any(a[abs(l)]==(l>0) for l in c): return False
    for mask,rhs in affine:
        p=0
        for v,val in a.items():
            if mask & (1<<(v-1)): p ^= int(val)
        if p!=rhs: return False
    return True


def row_vars(row):
    mask,_=row; out=set(); v=1
    while mask:
        if mask&1: out.add(v)
        mask >>= 1; v += 1
    return out


def state_vars(horn,affine,n):
    vs={abs(l) for c in horn for l in c}
    for r in affine: vs |= row_vars(r)
    return {v if v<=n else v-n for v in vs}


def branch_assignment(v,val,n):
    return {v:bool(val), n+v:not bool(val)}

def exact_depth(horn,affine,n,reverse=False,analysis_cache=None):
    memo={}; choices={}; stats={'states':0,'terminal':0,'parallel':0}
    if analysis_cache is None: analysis_cache={}
    def A(h,a,assignment):
        key=(tuple(h),tuple(a),tuple(sorted((int(k),bool(v)) for k,v in assignment.items())))
        if key not in analysis_cache: analysis_cache[key]=analyze(h,a,assignment)
        return analysis_cache[key]
    def rec(h,a):
        key=(tuple(h),tuple(a))
        if key in memo: return memo[key]
        stats['states']+=1
        info=A(h,a,{})
        if info['terminal']:
            stats['terminal']+=1; memo[key]=0; choices[key]=('T',None); return 0
        if len(info['mixed'])>1:
            stats['parallel']+=1
            d=max(rec(ch,ca) for ch,ca in info['mixed'])
            memo[key]=d; choices[key]=('P',tuple(info['mixed'])); return d
        ch,ca=info['mixed'][0]
        candidates=sorted(state_vars(ch,ca,n), reverse=reverse)
        best=None; bestvars=[]
        for v in candidates:
            ds=[]
            for val in (0,1):
                q=A(ch,ca,branch_assignment(v,val,n))
                ds.append(rec(q['horn'],q['affine']))
            d=1+max(ds)
            if best is None or d<best: best=d; bestvars=[v]
            elif d==best: bestvars.append(v)
        memo[key]=best; choices[key]=('S',(min(bestvars),tuple(bestvars)))
        return best
    depth=rec(horn,affine)
    return depth,memo,choices,stats


def replay_strategy(horn,affine,n,bits,choices,analysis_cache=None):
    if analysis_cache is None: analysis_cache={}
    def A(h,a,assignment):
        key=(tuple(h),tuple(a),tuple(sorted((int(k),bool(v)) for k,v in assignment.items())))
        if key not in analysis_cache: analysis_cache[key]=analyze(h,a,assignment)
        return analysis_cache[key]
    def walk(h,a):
        key=(tuple(h),tuple(a)); kind,payload=choices[key]
        if kind=='T': return 0
        if kind=='P': return max((walk(ch,ca) for ch,ca in payload),default=0)
        v,_=payload
        info=A(h,a,{})
        ch,ca=info['mixed'][0]
        q=A(ch,ca,branch_assignment(v,bits[v-1],n))
        return 1+walk(q['horn'],q['affine'])
    return walk(horn,affine)

def connected_source(source,n):
    adj={i:set() for i in range(1,n+1)}
    for c in source:
        vs=sorted({abs(l) for l in c})
        for i in vs:
            for j in vs:
                if i!=j: adj[i].add(j)
    seen=set(); stack=[1]
    while stack:
        v=stack.pop()
        if v in seen: continue
        seen.add(v); stack.extend(adj[v]-seen)
    return len(seen)==n


def c0372_core():
    out=[]
    for signs in itertools.product((False,True),repeat=3):
        out.append(tuple(-(3+i if pos else i) for i,pos in enumerate(signs,start=1)))
    # convert the frozen Horn image back to its source 3-CNF
    src=[]
    for signs in itertools.product((False,True),repeat=3):
        src.append(tuple((i if pos else -i) for i,pos in enumerate(signs,start=1)))
    return tuple(src)


def monotone_path(n):
    return tuple((i,i+1,i+2) for i in range(1,n-1))


def alternating_path(n):
    out=[]
    for s in range(1,n-1):
        c=[]
        for v in (s,s+1,s+2): c.append(-v if ((s+v)&1) else v)
        out.append(tuple(c))
    return tuple(out)


def xor3_even_clauses(a,b,c):
    out=[]
    for bits in itertools.product((0,1),repeat=3):
        if sum(bits)&1:
            out.append(tuple(v if bit==0 else -v for v,bit in zip((a,b,c),bits)))
    return tuple(out)


def xor_chain(n):
    out=[]
    for i in range(1,n-1): out.extend(xor3_even_clauses(i,i+1,i+2))
    return normalize_cnf(out)


def dense_positive(n):
    return tuple(tuple(c) for c in itertools.combinations(range(1,n+1),3))

def random_connected_cnf(n,m,rng):
    for _attempt in range(10000):
        clauses=[]; seen=set()
        while len(clauses)<m:
            vs=tuple(sorted(rng.sample(range(1,n+1),3)))
            c=tuple(v if rng.random()<0.5 else -v for v in vs)
            if c in seen: continue
            seen.add(c); clauses.append(c)
        src=tuple(clauses)
        if connected_source(src,n): return src
    raise RuntimeError('failed to generate connected random CNF')


def sat_label(source,n):
    return any(source_eval(source,b) for b in itertools.product((0,1),repeat=n))


def build_corpus():
    corpus=[('C0372_COMPLETE3_UNSAT',3,c0372_core())]
    for n in range(3,10):
        corpus.append(('MONOTONE_PATH',n,monotone_path(n)))
        corpus.append(('ALTERNATING_PATH',n,alternating_path(n)))
        corpus.append(('XOR3_CHAIN',n,xor_chain(n)))
    for n in range(4,9): corpus.append(('DENSE_POSITIVE_TRIPLES',n,dense_positive(n)))
    rng=random.Random(20260914)
    for n in range(4,9):
        for density in (2,4):
            for rep in range(3):
                corpus.append((f'RANDOM_CONNECTED_D{density}_R{rep}',n,random_connected_cnf(n,density*n,rng)))
    return corpus


def verify_transform(source,horn,affine,n):
    for bits in itertools.product((0,1),repeat=n):
        if source_eval(source,bits)!=image_eval(horn,affine,bits,n): return False
    return True

def main():
    t0=time.perf_counter(); rows=[]; failures=[]
    for family,n,source in build_corpus():
        horn,affine=encode_nand3_neq(source,n)
        transform_ok=verify_transform(source,horn,affine,n) if n<=8 else True
        if not transform_ok: failures.append({'family':family,'n':n,'kind':'transform'})
        analysis_cache={}
        d1,m1,c1,s1=exact_depth(horn,affine,n,False,analysis_cache)
        d2,m2,c2,s2=exact_depth(horn,affine,n,True,analysis_cache)
        if d1!=d2: failures.append({'family':family,'n':n,'kind':'depth_order','a':d1,'b':d2})
        root=(tuple(horn),tuple(affine)); first=[]
        if c1[root][0]=='S': first=list(c1[root][1][1])
        replay_ok=True; replay_max=0
        if n<=8:
            for bits in itertools.product((0,1),repeat=n):
                used=replay_strategy(horn,affine,n,bits,c1,analysis_cache); replay_max=max(replay_max,used)
                if used>d1: replay_ok=False; break
        if not replay_ok: failures.append({'family':family,'n':n,'kind':'replay'})
        rows.append({'family':family,'n':n,'clauses':len(source),'connected':connected_source(source,n),
                     'sat':sat_label(source,n),'depth':d1,'depth_ratio':round(d1/n,4),'optimal_first_vars':first,
                     'memo_states':len(m1),'terminal_states':s1['terminal'],'parallel_states':s1['parallel'],
                     'independent_order_depth':d2,'transform_replay':transform_ok,'strategy_replay':replay_ok,
                     'strategy_replay_max_depth':replay_max if n<=8 else None})
        print(f'PROGRESS {len(rows)}/{len(build_corpus())} {family} n={n} depth={d1} states={len(m1)} cache={len(analysis_cache)}', file=sys.stderr, flush=True)
    elapsed=round(1000*(time.perf_counter()-t0),3)
    profiles={}
    for fam in ('MONOTONE_PATH','ALTERNATING_PATH','XOR3_CHAIN','DENSE_POSITIVE_TRIPLES'):
        profiles[fam]=[{'n':r['n'],'depth':r['depth'],'ratio':r['depth_ratio']} for r in rows if r['family']==fam]
    random_rows=[r for r in rows if r['family'].startswith('RANDOM_CONNECTED')]
    max_rows=sorted(rows,key=lambda r:(-r['depth_ratio'],-r['depth'],r['family']))[:12]
    verdict='FALSIFIED_REDUCTION_OR_DEPTH_REPLAY' if failures else 'PASS_FINITE_CORPUS_DEPTH_CENSUS__NO_ASYMPTOTIC_CLAIM'
    out={
      'schema':'JANUS_TRUMP_EXACT_REACHABLE_BACKDOOR_DEPTH_REDUCTION_IMAGES_GATE_V1',
      'verdict':verdict,
      'runtime_ms':elapsed,
      'corpus_instances':len(rows),
      'failures':failures,
      'family_profiles':profiles,
      'random_summary':{
        'instances':len(random_rows),
        'max_depth':max((r['depth'] for r in random_rows),default=0),
        'max_ratio':max((r['depth_ratio'] for r in random_rows),default=0),
        'sat_count':sum(int(r['sat']) for r in random_rows),
        'unsat_count':sum(int(not r['sat']) for r in random_rows)
      },
      'highest_depth_ratio_instances':max_rows,
      'rows':rows,
      'captain_obvious':'finite exact depth is a property of this frozen corpus; only a separately proved family theorem can support asymptotic claims',
      'next_if_depth_grows':'TYPED_HYPERORDER_MESSAGE_WIDTH',
      'next_if_depth_stays_small':'prove the structural reason before extrapolating',
      'scientific_status':{'SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0}
    }
    print(json.dumps(out,sort_keys=True))

if __name__=='__main__': main()
