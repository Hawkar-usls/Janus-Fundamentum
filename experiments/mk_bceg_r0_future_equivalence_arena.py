#!/usr/bin/env python3
import argparse, hashlib, json
from collections import defaultdict, deque
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

GLOBAL_VARS=(1,2,3,4)
PREREG_COMMIT='027f0455b8bf371253f3070f8a71466e97c6e5fc'
JOURNAL_SEED_COMMIT='482dcae82fedb46a588689a8dc94b18ab92eb2e6'

class Ledger:
    def __init__(self):
        self.canonicalize_calls=0; self.subsumption_checks=0; self.assign_clause_visits=0
        self.exists_clause_visits=0; self.resolution_pairs=0; self.truth_assignment_evals=0
        self.truth_clause_evals=0; self.bdd_build_calls=0; self.bdd_update_calls=0
        self.bdd_or_calls=0; self.key_comparisons=0; self.closure_transitions=0
    def d(self): return dict(self.__dict__)
L=Ledger()

def cjson(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def sha(x): return hashlib.sha256(cjson(x).encode()).hexdigest()
def lit_key(x): return (abs(x),0 if x>0 else 1)

def canon(clauses):
    L.canonicalize_calls+=1
    cs=set()
    for c in clauses:
        s=frozenset(int(x) for x in c)
        if any(-l in s for l in s): continue
        if len(s)==0: return ((),)
        cs.add(tuple(sorted(s,key=lit_key)))
    arr=sorted(cs,key=lambda c:(len(c),c)); keep=[]; keep_sets=[]
    for c in arr:
        sc=set(c); redundant=False
        for ks in keep_sets:
            L.subsumption_checks+=1
            if ks.issubset(sc): redundant=True; break
        if not redundant:
            keep.append(c); keep_sets.append(sc)
    return tuple(sorted(keep,key=lambda c:(len(c),c)))

def active_vars(F): return tuple(sorted({abs(l) for c in F for l in c}))
def state_json(F): return [list(c) for c in F]
def state_bytes(F): return len(cjson(state_json(F)).encode())
def terminal_verdict(F):
    if F==((),): return 'UNSAT'
    if F==(): return 'SAT'
    return 'NONTERMINAL'

def assign(F,v,b):
    if F==((),): return F
    out=[]; t=v if b else -v; f=-t
    for c in F:
        L.assign_clause_visits+=1
        if t in c: continue
        nc=tuple(x for x in c if x!=f)
        if not nc: return ((),)
        out.append(nc)
    return canon(out)

def exists(F,v):
    if F==((),): return F
    pos=[];neg=[];ret=[]
    for c in F:
        L.exists_clause_visits+=1
        if v in c: pos.append(c)
        elif -v in c: neg.append(c)
        else: ret.append(c)
    if not pos or not neg:
        return canon(ret)
    out=list(ret)
    for p in pos:
        for n in neg:
            L.resolution_pairs+=1
            r=set(p); r.discard(v); r|=set(n); r.discard(-v)
            if any(-l in r for l in r): continue
            out.append(tuple(r))
    return canon(out)

def sat_under(F,a):
    L.truth_assignment_evals+=1
    if F==((),): return False
    for c in F:
        L.truth_clause_evals+=1
        if not any(a[abs(l)]==(l>0) for l in c): return False
    return True

def truth_bits(F):
    bits=[]
    for vals in product((False,True), repeat=len(GLOBAL_VARS)):
        a=dict(zip(GLOBAL_VARS,vals)); bits.append(1 if sat_under(F,a) else 0)
    return tuple(bits)

def truth_key(F): return truth_bits(F)

def struct_key(F):
    av=active_vars(F); widths=tuple(sorted(len(c) for c in F)); deg=[]
    for v in av:
        p=sum(v in c for c in F); n=sum(-v in c for c in F)
        deg.append(tuple(sorted((p,n))))
    return (av,len(F),widths,tuple(sorted(deg)))

# Canonical ROBDD as immutable nested tuples: terminal 0/1 or (var,low,high).
def mk_node(v,lo,hi): return lo if lo==hi else (v,lo,hi)
def bdd_from_bits(bits):
    @lru_cache(None)
    def rec(bt,idx):
        L.bdd_build_calls+=1
        if all(x==bt[0] for x in bt): return int(bt[0])
        half=len(bt)//2; lo=rec(tuple(bt[:half]),idx+1); hi=rec(tuple(bt[half:]),idx+1)
        return mk_node(GLOBAL_VARS[idx],lo,hi)
    return rec(tuple(bits),0)
def bdd(F): return bdd_from_bits(truth_bits(F))
def bdd_top(n): return 99 if n in (0,1) else n[0]
def bdd_restrict(n,v,b):
    L.bdd_update_calls+=1
    if n in (0,1): return n
    x,lo,hi=n
    if x==v: return hi if b else lo
    if x>v: return n
    return mk_node(x,bdd_restrict(lo,v,b),bdd_restrict(hi,v,b))
def bdd_or(a,b):
    L.bdd_or_calls+=1
    if a==1 or b==1:return 1
    if a==0:return b
    if b==0:return a
    if a==b:return a
    v=min(bdd_top(a),bdd_top(b))
    def cof(n,bit):
        if n in (0,1):return n
        if n[0]==v:return n[2] if bit else n[1]
        return n
    lo=bdd_or(cof(a,0),cof(b,0)); hi=bdd_or(cof(a,1),cof(b,1))
    return mk_node(v,lo,hi)
def bdd_exists(n,v): return bdd_or(bdd_restrict(n,v,False),bdd_restrict(n,v,True))
def bdd_nodes(root):
    seen=set()
    def walk(n):
        if n in (0,1) or n in seen:return
        seen.add(n);walk(n[1]);walk(n[2])
    walk(root);return len(seen)
def bdd_bytes(root): return len(cjson(root).encode())

def build_universe():
    pool=[]
    for v in GLOBAL_VARS: pool.extend([(v,),(-v,)])
    for a,b in combinations(GLOBAL_VARS,2):
        for sa in (1,-1):
            for sb in (1,-1): pool.append((sa*a,sb*b))
    seeds=set(canon([c]) for c in pool)
    seeds.update(canon([a,b]) for a,b in combinations(pool,2))
    states=set(seeds); q=deque(sorted(seeds,key=repr))
    while q:
        F=q.popleft()
        for v in GLOBAL_VARS:
            for b in (False,True):
                L.closure_transitions+=1; G=assign(F,v,b)
                if G not in states: states.add(G);q.append(G)
            L.closure_transitions+=1; G=exists(F,v)
            if G not in states: states.add(G);q.append(G)
    return pool,seeds,states

def first_distinguishing_continuation(F1,F2):
    b1=truth_bits(F1);b2=truth_bits(F2)
    for idx,(x,y) in enumerate(zip(b1,b2)):
        if x==y: continue
        vals=list(product((False,True),repeat=4))[idx]
        A=F1;B=F2;pi=[]
        for v,val in zip(GLOBAL_VARS,vals):
            pi.append({'op':'ASSIGN','v':v,'value':bool(val)})
            A=assign(A,v,val);B=assign(B,v,val)
        va=terminal_verdict(A);vb=terminal_verdict(B)
        assert va in ('SAT','UNSAT') and vb in ('SAT','UNSAT') and va!=vb
        return {'continuation':pi,'terminal_S1':va,'terminal_S2':vb,'assignment':dict(zip(map(str,GLOBAL_VARS),vals))}
    return None

def analyze_key(name,states,keyfn,semantics):
    groups=defaultdict(list)
    for F in states: groups[keyfn(F)].append(F)
    equal_pairs=collision_pairs=certified_merge_pairs=0; replayed=0; first=None
    for key,gs in groups.items():
        if len(gs)<2: continue
        for i in range(len(gs)):
            for j in range(i+1,len(gs)):
                L.key_comparisons+=1; equal_pairs+=1
                s1,s2=gs[i],gs[j]
                if semantics[s1]!=semantics[s2]:
                    collision_pairs+=1
                    d=first_distinguishing_continuation(s1,s2)
                    if d is not None: replayed+=1
                    if first is None:
                        first={'key':cjson(key),'S1':state_json(s1),'S2':state_json(s2),'truth_S1':list(semantics[s1]),'truth_S2':list(semantics[s2]),**d}
                elif s1!=s2:
                    certified_merge_pairs+=1
    return {'language':name,'key_class_count':len(groups),'equal_key_pair_count':equal_pairs,'semantic_collision_pair_count':collision_pairs,'collision_replays':replayed,'certified_merge_pair_count':certified_merge_pairs,'first_collision_monster':first}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--journal',required=True);args=ap.parse_args()
    journal=[]
    def je(event,**kw): journal.append({'event_id':f'MK-R0-RUN-{len(journal)+1:04d}','event':event,**kw})
    je('EXECUTION_START',preregistration_commit=PREREG_COMMIT,journal_seed_commit=JOURNAL_SEED_COMMIT)
    pool,seeds,states=build_universe(); states=sorted(states,key=repr)
    je('SOURCE_UNIVERSE_RECEIPT',clause_pool=len(pool),seed_states=len(seeds),reachable_states=len(states),closure_transitions=L.closure_transitions)
    semantics={F:truth_bits(F) for F in states}; future_classes=defaultdict(list)
    for F,t in semantics.items(): future_classes[t].append(F)
    je('EXACT_FUTURE_ORACLE_BUILT',future_equivalence_classes=len(future_classes),distinct_states_in_nontrivial_classes=sum(len(g) for g in future_classes.values() if len(g)>1))

    struct=analyze_key('MK_STRUCT_V0',states,struct_key,semantics)
    je('STRUCTURAL_KEY_ATTACK',verdict='REFUTED_FUTURE_INTERFACE_CANDIDATE' if struct['semantic_collision_pair_count'] else 'FINITE_SURVIVOR_NOT_THEOREM',collisions=struct['semantic_collision_pair_count'],first_collision_monster=struct['first_collision_monster'])
    truth=analyze_key('MK_TRUTH_ORACLE',states,truth_key,semantics)
    je('TRUTH_ORACLE_CONTROL',verdict='CONTROL_EXACT_NOT_POLYNOMIAL_CLAIM',key_classes=truth['key_class_count'],collisions=truth['semantic_collision_pair_count'])
    bdds={F:bdd(F) for F in states}
    robdd=analyze_key('MK_ROBDD_FIXED_ORDER',states,lambda F:bdds[F],semantics)
    je('ROBDD_COLLISION_AUDIT',collisions=robdd['semantic_collision_pair_count'],certified_merge_pairs=robdd['certified_merge_pair_count'])

    congr_total=congr_pass=0; first_congr_fail=None
    for F in states:
        k=bdds[F]
        for v in GLOBAL_VARS:
            for val in (False,True):
                congr_total+=1
                lhs=bdd(assign(F,v,val)); rhs=bdd_restrict(k,v,val)
                if lhs==rhs:congr_pass+=1
                elif first_congr_fail is None:first_congr_fail={'state':state_json(F),'op':'ASSIGN','v':v,'value':val,'lhs':lhs,'rhs':rhs}
            congr_total+=1
            lhs=bdd(exists(F,v)); rhs=bdd_exists(k,v)
            if lhs==rhs:congr_pass+=1
            elif first_congr_fail is None:first_congr_fail={'state':state_json(F),'op':'EXISTS','v':v,'lhs':lhs,'rhs':rhs}
    je('ROBDD_TRANSITION_CONGRUENCE',passed=congr_pass==congr_total,checked=congr_total,passed_count=congr_pass,first_failure=first_congr_fail)

    decision_ok=all((any(semantics[F]))==(bdds[F]!=0) for F in states)
    mk_id_unique=len({cjson(state_json(F)) for F in states})==len(states)
    state_b=[state_bytes(F) for F in states]; bdd_n=[bdd_nodes(bdds[F]) for F in states]; bdd_b=[bdd_bytes(bdds[F]) for F in states]
    cost={'ledger':L.d(),'full_state_bytes':{'sum':sum(state_b),'max':max(state_b),'mean':sum(state_b)/len(state_b)},'robdd_nodes':{'sum':sum(bdd_n),'max':max(bdd_n),'mean':sum(bdd_n)/len(bdd_n)},'robdd_bytes':{'sum':sum(bdd_b),'max':max(bdd_b),'mean':sum(bdd_b)/len(bdd_b)}}
    je('COST_LEDGER',**cost)

    gates=[
      {'gate':'G1_COLLISION_DETECTOR','passed':struct['collision_replays']==struct['semantic_collision_pair_count'],'value':{'collisions':struct['semantic_collision_pair_count'],'replayed':struct['collision_replays']}},
      {'gate':'G2_ROBDD_SOUND_MERGE','passed':robdd['semantic_collision_pair_count']==0,'value':robdd['semantic_collision_pair_count']},
      {'gate':'G3_NONTRIVIAL_CERTIFIED_MERGE','passed':robdd['certified_merge_pair_count']>0,'value':robdd['certified_merge_pair_count']},
      {'gate':'G4_TRANSITION_CONGRUENCE','passed':congr_pass==congr_total,'value':{'passed':congr_pass,'total':congr_total}},
      {'gate':'G5_DECISION_SUFFICIENCY','passed':decision_ok},
      {'gate':'G6_REPLAY_LIFT','passed':struct['first_collision_monster'] is not None and struct['collision_replays']>0},
      {'gate':'G7_COST_ACCOUNTING','passed':all(v>0 for v in [L.canonicalize_calls,L.truth_assignment_evals,L.bdd_build_calls,L.bdd_update_calls,L.key_comparisons])},
      {'gate':'G8_NO_THEOREM_PROMOTION','passed':True}
    ]
    robdd_verdict='FINITE_SURVIVOR_NOT_THEOREM' if all(g['passed'] for g in gates) else 'REFUTED_FUTURE_INTERFACE_CANDIDATE'
    result={
      'schema':'JANUS/THE_MAGIC_KEY/MK_BCEG_R0_FUTURE_EQUIVALENCE_ARENA/RESULT/v1.0','status':'COMPLETE','date':'2026-08-30',
      'preregistration_commit':PREREG_COMMIT,'journal_seed_commit':JOURNAL_SEED_COMMIT,
      'universe':{'global_variables':list(GLOBAL_VARS),'clause_pool_size':len(pool),'seed_state_count':len(seeds),'reachable_state_count':len(states),'future_equivalence_class_count':len(future_classes),'nontrivial_future_merge_state_reduction':len(states)-len(future_classes),'mk_id_exact_unique':mk_id_unique},
      'keys':{
        'MK_STRUCT_V0':{**struct,'verdict':'REFUTED_FUTURE_INTERFACE_CANDIDATE' if struct['semantic_collision_pair_count'] else 'FINITE_SURVIVOR_NOT_THEOREM'},
        'MK_TRUTH_ORACLE':{**truth,'verdict':'CONTROL_EXACT_NOT_POLYNOMIAL_CLAIM','complexity_status':'NO_POLY_CLAIM'},
        'MK_ROBDD_FIXED_ORDER':{**robdd,'verdict':robdd_verdict,'equivalence_status':'FINITE_EXACTLY_VERIFIED' if robdd['semantic_collision_pair_count']==0 else 'NOT_CERTIFIED','complexity_status':'UNIVERSAL_POLY_BOUND_OPEN','transition_congruence':{'passed':congr_pass==congr_total,'checked':congr_total,'first_failure':first_congr_fail}}
      },
      'gates':gates,'cost_accounting':cost,
      'overall_verdict':'FINITE_SURVIVOR_NOT_THEOREM__STRUCTURAL_KEY_REFUTED' if robdd_verdict=='FINITE_SURVIVOR_NOT_THEOREM' else 'REFUTED_R0_EXACT_INTERFACE',
      'post_result_boundary':{'ROBDD_exact_future_factor_map_on_R0':robdd['semantic_collision_pair_count']==0 and congr_pass==congr_total,'universal_polynomial_ROBDD_size_or_discovery_proved':False,'arbitrary_CNF_future_interface_proved':False,'P_VS_NP':'OPEN'},
      'next_formal_obligation':'Find a representation/update algebra that preserves ROBDD-like future congruence while avoiding worst-case representation/discovery blow-up; R0 does not establish such a polynomial bound.'
    }
    je('FINAL_VERDICT',overall_verdict=result['overall_verdict'],robdd_verdict=robdd_verdict,P_VS_NP='OPEN')
    je('POST_RESULT_LEMMA',statement='Exact state identity is strictly finer than future-equivalence on the R0 universe.' if len(states)>len(future_classes) else 'No nontrivial future merges observed.')
    je('NEXT_ALLOWED_STEP',statement=result['next_formal_obligation'])
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    with open(args.journal,'w',encoding='utf-8') as f:
        for e in journal:f.write(json.dumps(e,ensure_ascii=False,sort_keys=True)+'\n')
    print(json.dumps({'overall_verdict':result['overall_verdict'],'reachable_states':len(states),'future_classes':len(future_classes),'struct_collisions':struct['semantic_collision_pair_count'],'robdd_collisions':robdd['semantic_collision_pair_count'],'robdd_certified_merge_pairs':robdd['certified_merge_pair_count'],'congruence':f'{congr_pass}/{congr_total}','gates':[(g['gate'],g['passed']) for g in gates],'P_VS_NP':'OPEN'},indent=2))
    if not all(g['passed'] for g in gates): raise SystemExit(2)

if __name__=='__main__': main()
