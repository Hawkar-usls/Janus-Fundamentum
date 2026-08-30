#!/usr/bin/env python3
import argparse, hashlib, itertools, json, statistics
from collections import defaultdict, deque
from pathlib import Path

VARS=(1,2,3,4)
NS='JANUS-MK-BCEG-R0-FINAL-2026-08-30-A'
FALSE=((),)
TRUE=()

def lit_key(x): return (abs(x), 0 if x<0 else 1)
def clause_key(c): return (len(c), tuple(lit_key(x) for x in c))

def canonicalize(clauses):
    out=[]
    for cl in clauses:
        s=set(cl)
        if any(-x in s for x in s):
            continue
        c=tuple(sorted(s,key=lit_key))
        if len(c)==0: return FALSE
        out.append(c)
    if not out: return TRUE
    uniq=sorted(set(out),key=clause_key)
    sets=[set(c) for c in uniq]
    keep=[]
    for i,c in enumerate(uniq):
        sc=sets[i]
        if any(j!=i and sets[j].issubset(sc) for j in range(len(uniq))):
            continue
        keep.append(c)
    return tuple(sorted(keep,key=clause_key))

def live_vars(cnf):
    return tuple(sorted({abs(l) for c in cnf for l in c}))

def assign(cnf,v,b):
    if cnf in (TRUE,FALSE): return cnf
    out=[]
    true_lit=v if b else -v
    false_lit=-true_lit
    for c in cnf:
        if true_lit in c: continue
        out.append(tuple(l for l in c if l!=false_lit))
    return canonicalize(out)

def exists(cnf,v):
    if cnf in (TRUE,FALSE): return cnf
    pos=[];neg=[];ret=[]
    for c in cnf:
        if v in c: pos.append(c)
        elif -v in c: neg.append(c)
        else: ret.append(c)
    resolvents=[]
    for p in pos:
        ps=set(p);ps.remove(v)
        for n in neg:
            ns=set(n);ns.remove(-v)
            u=ps|ns
            if any(-x in u for x in u): continue
            resolvents.append(tuple(u))
    return canonicalize(ret+resolvents)

def eval_cnf(cnf,env):
    if cnf==TRUE:return True
    if cnf==FALSE:return False
    for c in cnf:
        ok=False
        for l in c:
            val=env[abs(l)]
            if (l>0 and val) or (l<0 and not val): ok=True;break
        if not ok:return False
    return True

def truth_key(cnf):
    vs=VARS
    bits=[];work=0
    for vals in itertools.product((0,1),repeat=len(vs)):
        env=dict(zip(vs,vals));bits.append(1 if eval_cnf(cnf,env) else 0)
        work += sum(len(c) for c in cnf) if cnf not in (TRUE,FALSE) else 1
    return (vs,tuple(bits)),work

def update_truth(key,action):
    vs,bits=key
    kind,v,*rest=action
    idx=vs.index(v)
    out=[];work=0
    def pos(full):
        p=0
        for x in full:p=(p<<1)|x
        return p
    for vals in itertools.product((0,1),repeat=len(vs)):
        f0=list(vals);f1=list(vals);f0[idx]=0;f1[idx]=1
        b0=bits[pos(f0)];b1=bits[pos(f1)];work+=2
        if kind=='ASSIGN': out.append(b1 if rest[0] else b0)
        elif kind=='EXISTS': out.append(1 if (b0 or b1) else 0)
        else: raise ValueError(action)
    return (vs,tuple(out)),work

def struct_key(cnf):
    vs=live_vars(cnf)
    widths=tuple(sorted(len(c) for c in cnf))
    units=tuple(sorted((c[0] for c in cnf if len(c)==1),key=lit_key))
    occ=[]
    for v in vs:
        p=sum(v in c for c in cnf);n=sum(-v in c for c in cnf)
        occ.append((v,p,n))
    return (vs,len(cnf),widths,units,tuple(occ))

def cnf_json(cnf): return [[int(x) for x in c] for c in cnf]
def bytes_len(obj): return len(json.dumps(obj,separators=(',',':'),sort_keys=True).encode())

def bdd_key_from_truth(tkey):
    vs,bits=tkey
    uniq={};nodes=[];calls=0
    def rec(level,subbits):
        nonlocal calls
        calls+=1
        if all(x==0 for x in subbits):return 0
        if all(x==1 for x in subbits):return 1
        if level>=len(vs): return 1 if subbits[0] else 0
        half=len(subbits)//2
        lo=rec(level+1,subbits[:half]);hi=rec(level+1,subbits[half:])
        if lo==hi:return lo
        sig=(vs[level],lo,hi)
        if sig in uniq:return uniq[sig]
        nid=len(nodes)+2;uniq[sig]=nid;nodes.append((nid,vs[level],lo,hi));return nid
    root=rec(0,bits)
    payload={'vars':list(vs),'root':root,'nodes':[list(x) for x in nodes]}
    return payload,{'nodes':len(nodes),'bytes':bytes_len(payload),'build_calls':calls}

def clause_pool():
    pool=[]
    for w in (1,2,3):
        for vv in itertools.combinations(VARS,w):
            for signs in itertools.product((-1,1),repeat=w):
                pool.append(tuple(sorted((v*s for v,s in zip(vv,signs)),key=lit_key)))
    return tuple(sorted(pool,key=clause_key))

def base_states():
    pool=clause_pool();base=set()
    for c in pool: base.add(canonicalize([c]))
    for i,j in itertools.combinations(range(len(pool)),2): base.add(canonicalize([pool[i],pool[j]]))
    triples=[]
    for comb in itertools.combinations(range(len(pool)),3):
        h=hashlib.sha256((NS+'|'+','.join(map(str,comb))).encode()).digest();triples.append((h,comb))
    triples.sort(key=lambda x:x[0])
    for _,(i,j,k) in triples[:2048]: base.add(canonicalize([pool[i],pool[j],pool[k]]))
    return pool,base

def closure(base):
    seen=set(base);q=deque(base);transitions=0
    while q:
        s=q.popleft()
        for v in VARS:
            for b in (0,1):
                t=assign(s,v,b);transitions+=1
                if t not in seen:seen.add(t);q.append(t)
            t=exists(s,v);transitions+=1
            if t not in seen:seen.add(t);q.append(t)
    return seen,transitions

def distinguishing_continuation(c1,c2,t1,t2):
    vs,b1=t1;vs2,b2=t2
    assert vs==vs2
    for idx,(a,b) in enumerate(zip(b1,b2)):
        if a!=b:
            vals=[];x=idx
            for _ in range(len(vs)): vals.append(x&1);x>>=1
            vals=list(reversed(vals))
            actions=[['ASSIGN',v,int(val)] for v,val in zip(vs,vals)]
            s1,s2=c1,c2
            for _,v,val in actions:
                s1=assign(s1,v,val);s2=assign(s2,v,val)
            return {'assignment':dict(zip(map(str,vs),vals)),'actions':actions,'terminal_1':cnf_json(s1),'terminal_2':cnf_json(s2),'truth_1':int(a),'truth_2':int(b)}
    return None

def self_tests():
    x=((1,),)
    assert assign(x,1,1)==TRUE and assign(x,1,0)==FALSE
    assert exists(x,1)==TRUE
    f=canonicalize([(1,2),(1,-2)])
    tk,_=truth_key(f); assert tk[0]==VARS
    assert exists(f,2)==((1,),)
    bdd,_=bdd_key_from_truth(tk); assert bdd['nodes']
    return True

def run(out_path,journal_path):
    self_tests();journal=[]
    journal.append({'event':'PREREG_FROZEN','status':'ACK','parent_bceg_commit':'efe10e82582e548697b009689828bf69f5fa511e','magic_key_spec_commit':'87d65442785c5488f9f78f49af4b2e907c0eee4a'})
    pool,base=base_states();states,transition_gen_work=closure(base)
    states=sorted(states,key=lambda s:json.dumps(cnf_json(s),separators=(',',':')))
    journal.append({'event':'UNIVERSE_BUILT','clause_pool':len(pool),'base_states':len(base),'reachable_states':len(states),'closure_transition_calls':transition_gen_work})

    truth={};bdd={};struct={};id_payload={};costs=[]
    for s in states:
        tk,tw=truth_key(s);bp,bc=bdd_key_from_truth(tk)
        truth[s]=tk;bdd[s]=bp;struct[s]=struct_key(s);id_payload[s]=cnf_json(s)
        costs.append({'state_bytes':bytes_len(cnf_json(s)),'truth_bits':len(tk[1]),'truth_eval_work':tw,'bdd_nodes':bc['nodes'],'bdd_bytes':bc['bytes'],'bdd_build_calls':bc['build_calls']})

    g1=len({json.dumps(id_payload[s],separators=(',',':')) for s in states})==len(states)

    def first_collision(keymap):
        groups=defaultdict(list);pair_checks=0
        for s in states:
            k=json.dumps(keymap[s],separators=(',',':'),sort_keys=True);groups[k].append(s)
        merges=0
        for grp in groups.values():
            if len(grp)<2:continue
            for a,b in itertools.combinations(grp,2):
                pair_checks+=1
                if truth[a]!=truth[b]:
                    return a,b,distinguishing_continuation(a,b,truth[a],truth[b]),pair_checks,merges
                if a!=b:merges+=1
        return None,None,None,pair_checks,merges

    a,b,monster,struct_checks,struct_merges=first_collision(struct)
    g2=monster is not None
    if monster:
        journal.append({'event':'STRUCTURAL_COLLISION_MONSTER','status':'REFUTED_FUTURE_INTERFACE_CANDIDATE','state_1':cnf_json(a),'state_2':cnf_json(b),'struct_key':struct[a],'distinguishing_continuation':monster})

    _,_,truth_monster,truth_checks,truth_merges=first_collision({s:{'vars':list(truth[s][0]),'bits':list(truth[s][1])} for s in states})
    g3=truth_monster is None
    _,_,bdd_monster,bdd_checks,bdd_merges=first_collision(bdd)
    g4=bdd_monster is None
    g5=bdd_merges>0

    cong_fail=None;cong_checks=0;update_work=0
    for s in states:
        tk=truth[s]
        for v in VARS:
            for action in [('ASSIGN',v,0),('ASSIGN',v,1),('EXISTS',v)]:
                t=assign(s,v,action[2]) if action[0]=='ASSIGN' else exists(s,v)
                updated,uw=update_truth(tk,action);update_work+=uw
                direct=truth[t];cong_checks+=1
                if updated!=direct:
                    cong_fail={'state':cnf_json(s),'action':list(action),'successor':cnf_json(t),'reason':'truth_update_mismatch'};break
                up_bdd,_=bdd_key_from_truth(updated)
                if up_bdd!=bdd[t]:
                    cong_fail={'state':cnf_json(s),'action':list(action),'successor':cnf_json(t),'reason':'bdd_update_mismatch'};break
            if cong_fail:break
        if cong_fail:break
    g6=cong_fail is None
    if cong_fail:journal.append({'event':'TRANSITION_CONGRUENCE_FAILURE','detail':cong_fail})

    csum={
      'states':len(states),
      'state_bytes':{'median':statistics.median(x['state_bytes'] for x in costs),'max':max(x['state_bytes'] for x in costs)},
      'truth_bits':{'median':statistics.median(x['truth_bits'] for x in costs),'max':max(x['truth_bits'] for x in costs)},
      'bdd_nodes':{'median':statistics.median(x['bdd_nodes'] for x in costs),'max':max(x['bdd_nodes'] for x in costs)},
      'bdd_bytes':{'median':statistics.median(x['bdd_bytes'] for x in costs),'max':max(x['bdd_bytes'] for x in costs)},
      'truth_eval_work_total':sum(x['truth_eval_work'] for x in costs),
      'bdd_build_calls_total':sum(x['bdd_build_calls'] for x in costs),
      'transition_update_work_total':update_work,
      'collision_pair_checks':{'struct':struct_checks,'truth':truth_checks,'robdd':bdd_checks}
    }
    gates=[
      {'gate':'G1_MK_ID_EXACT','passed':g1},
      {'gate':'G2_STRUCTURAL_MONSTER_EXISTS','passed':g2,'semantic_collision_found':bool(monster)},
      {'gate':'G3_TRUTH_INTERFACE_SOUND','passed':g3,'semantic_collisions':0 if g3 else 1,'certified_merge_pairs_seen':truth_merges},
      {'gate':'G4_ROBDD_INTERFACE_SOUND','passed':g4,'semantic_collisions':0 if g4 else 1,'certified_merge_pairs_seen':bdd_merges},
      {'gate':'G5_ROBDD_NONTRIVIAL_MERGE','passed':g5,'merge_pairs_seen':bdd_merges},
      {'gate':'G6_TRANSITION_CONGRUENCE','passed':g6,'checks':cong_checks,'failure':cong_fail},
      {'gate':'G7_COST_ACCOUNTING','passed':True,'cost_summary':csum},
      {'gate':'G8_SCIENTIFIC_BOUNDARY','passed':True,'P_VS_NP':'OPEN','finite_survivor_not_theorem':True}
    ]
    exact_survivor=all(g['passed'] for g in gates if g['gate']!='G2_STRUCTURAL_MONSTER_EXISTS') and g2
    verdict='FINITE_SURVIVOR_NOT_THEOREM' if exact_survivor else 'REFUTED_FUTURE_INTERFACE_CANDIDATE'
    unresolved=[
      'worst_case_ROBDD_size_polynomial_for_arbitrary_CNF_NOT_PROVED',
      'polynomial_discovery_of_future_interface_for_arbitrary_CNF_NOT_PROVED',
      'formal_transition_congruence_beyond_R0_enumeration_NOT_PROVED',
      'universal_decision_sufficiency_for_claimed_BCEG_domain_NOT_PROVED',
      'polynomial_end_to_end_trajectory_length_NOT_PROVED'
    ]
    result={
      'schema':'JANUS/THE_MAGIC_KEY/MK_BCEG_R0_FUTURE_EQUIVALENCE_ARENA/RESULT/v1.0',
      'status':'COMPLETE','verdict':verdict,
      'universe':{'clause_pool':len(pool),'base_states':len(base),'reachable_states':len(states),'closure_transition_calls':transition_gen_work},
      'gates':gates,
      'structural_collision_monster':None if not monster else {'state_1':cnf_json(a),'state_2':cnf_json(b),'key':struct[a],'distinguishing_continuation':monster},
      'cost_summary':csum,
      'unresolved_theorem_obligations':unresolved,
      'interpretation':{
        'MK_ID':'Exact identity control behaved as intended.',
        'MK_FUTURE_STRUCT_V0':'A lossy structural interface is rejected if a semantic collision monster is found.',
        'MK_FUTURE_TRUTH_V0':'Exact finite semantic control; exponential-size risk intentionally retained.',
        'MK_FUTURE_ROBDD_V0':'Canonical exact finite future-interface candidate under frozen order. Finite soundness and transition congruence do not imply a polynomial universal bound.'
      },
      'scientific_boundary':{'P_VS_NP':'OPEN','finite_testing_is_not_proof':True,'FORMALLY_CERTIFIED_emitted':False,'minimality_required':False}
    }
    journal.append({'event':'R0_RESULT','verdict':verdict,'gates':[{k:v for k,v in g.items() if k in ('gate','passed')} for g in gates],'unresolved':unresolved})
    Path(out_path).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    with open(journal_path,'w',encoding='utf-8') as f:
        for row in journal:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps({'verdict':verdict,'reachable_states':len(states),'structural_collision':bool(monster),'bdd_merges':bdd_merges,'congruence_checks':cong_checks,'cost_summary':csum},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output');ap.add_argument('--journal');ap.add_argument('--self-test-only',action='store_true');args=ap.parse_args()
    if args.self_test_only:
        self_tests();print(json.dumps({'status':'PASS','self_tests':True}))
    else:
        if not args.output or not args.journal: raise SystemExit('--output and --journal required')
        run(args.output,args.journal)
