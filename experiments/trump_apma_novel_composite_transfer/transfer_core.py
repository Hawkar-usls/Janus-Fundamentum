from __future__ import annotations
from collections import defaultdict, deque
from itertools import combinations, product
from pathlib import Path
import hashlib, json, sys, time

ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'trump_apma_compositional_synthesis'
sys.path.insert(0,str(PREV))
import core as primitives

LOWER_PRIMITIVES=tuple(f'P{i}' for i in range(9))
RULE_CANDIDATES=[
 {'id':'RHO_W1','max_separator_width':1},
 {'id':'RHO_W2','max_separator_width':2},
 {'id':'RHO_W3','max_separator_width':3},
]
RULE_OPS=['normalize','generic_separator_search','restrict','extract','relation_filter','project','join','canonical_message','reconstruct','root_replay']

def canon(raw):
    return [list(c) for c in primitives.canon(raw)]

def vars_of(raw):
    return sorted({abs(int(x)) for c in raw for x in c})

def replay(raw,assignment):
    return primitives.replay(raw,assignment)

def condition(raw,fixed):
    cnf=canon(raw); a={int(k):bool(v) for k,v in fixed.items()}; trace=[]
    while True:
        nxt=[]
        for clause in cnf:
            sat=False; rem=[]
            for lit in clause:
                v=abs(lit)
                if v in a:
                    if a[v]==(lit>0): sat=True; break
                else: rem.append(lit)
            if sat: continue
            if not rem:
                return {'status':'CONTRADICTION','assignment':a,'trace':trace,'residual':[]}
            nxt.append(rem)
        cnf=canon(nxt)
        unit=None
        for c in cnf:
            if len(c)==1:
                unit=c[0]; break
        if unit is None: break
        v=abs(unit); val=unit>0
        if v in a and a[v]!=val:
            return {'status':'CONTRADICTION','assignment':a,'trace':trace+[unit],'residual':cnf}
        if v not in a:
            a[v]=val; trace.append(unit)
    return {'status':'OK','assignment':a,'trace':trace,'residual':cnf}

def solve_leaf(raw,fixed=None):
    fixed={} if fixed is None else fixed
    cond=condition(raw,fixed)
    if cond['status']=='CONTRADICTION':
        return {'admitted':True,'decision':'UNSAT','slot':'UNIT','assignment':None,'certificate':{'kind':'condition_contradiction','fixed':dict(fixed),'trace':cond['trace']}}
    residual=cond['residual']; forced=dict(cond['assignment'])
    allv=vars_of(raw)
    if not residual:
        full={v:forced.get(v,False) for v in allv}
        if replay(raw,full):
            return {'admitted':True,'decision':'SAT','slot':'TRIVIAL','assignment':full,'certificate':{'kind':'condition_satisfied','fixed':dict(fixed),'trace':cond['trace']}}
        return {'admitted':False,'reason':'TRIVIAL_REPLAY_FAIL'}
    for slot,(q,r) in enumerate(zip(primitives.QS,primitives.RS)):
        try: substrate=q(residual)
        except Exception: substrate=None
        if substrate is None: continue
        try: z=r(substrate)
        except Exception: z=None
        if not isinstance(z,dict) or z.get('decision') not in ('SAT','UNSAT'): continue
        if z['decision']=='SAT':
            full={v:forced.get(v,False) for v in allv}
            for k,val in (z.get('assignment') or {}).items(): full[int(k)]=bool(val)
            if not replay(raw,full): continue
            return {'admitted':True,'decision':'SAT','slot':slot,'assignment':full,'certificate':{'kind':'primitive_sat','primitive_slot':slot,'fixed':dict(fixed),'trace':cond['trace'],'residual_certificate':z.get('certificate')}}
        return {'admitted':True,'decision':'UNSAT','slot':slot,'assignment':None,'certificate':{'kind':'primitive_unsat','primitive_slot':slot,'fixed':dict(fixed),'trace':cond['trace'],'residual':residual,'residual_certificate':z.get('certificate')}}
    return {'admitted':False,'reason':'NO_LOWER_PRIMITIVE_ADMISSION'}

def _components_without_separator(cnf,sep):
    sep=set(sep); all_non={abs(x) for c in cnf for x in c if abs(x) not in sep}
    if not all_non: return None
    adj={v:set() for v in all_non}
    for c in cnf:
        xs=sorted({abs(x) for x in c if abs(x) not in sep})
        for i,a in enumerate(xs):
            for b in xs[i+1:]: adj[a].add(b); adj[b].add(a)
    comp={}; groups=[]
    for s in sorted(all_non):
        if s in comp: continue
        cid=len(groups); q=[s]; comp[s]=cid; vs=[]
        while q:
            x=q.pop(); vs.append(x)
            for y in adj[x]:
                if y not in comp: comp[y]=cid; q.append(y)
        groups.append(vs)
    if len(groups)<2: return None
    clause_groups=[[] for _ in groups]
    for c in cnf:
        owners={comp[abs(x)] for x in c if abs(x) not in sep}
        if len(owners)!=1: return None
        clause_groups[next(iter(owners))].append(list(c))
    clause_groups=[g for g in clause_groups if g]
    if len(clause_groups)<2 or min(map(len,clause_groups))<3: return None
    for s in sep:
        touches=sum(any(any(abs(x)==s for x in c) for c in g) for g in clause_groups)
        if touches<2: return None
    return clause_groups

def find_separator(cnf,max_w):
    vs=vars_of(cnf)
    for w in range(1,max_w+1):
        best=None; best_score=None
        for sep in combinations(vs,w):
            groups=_components_without_separator(cnf,sep)
            if groups is None: continue
            sizes=sorted(len(g) for g in groups)
            score=(sizes[0],-sizes[-1],-len(groups),tuple(-x for x in sep))
            if best is None or score>best_score:
                best=(sep,groups); best_score=score
        if best is not None: return best
    return None

def discover_leaves(raw,max_w,depth=0):
    cnf=canon(raw)
    if depth>128: return None,'DECOMPOSITION_DEPTH'
    z=solve_leaf(cnf,{})
    if z.get('admitted'): return [cnf],None
    hit=find_separator(cnf,max_w)
    if hit is None: return None,'NO_SEPARATOR_OR_LOCAL_ADMISSION'
    sep,groups=hit; leaves=[]
    for g in groups:
        sub,err=discover_leaves(g,max_w,depth+1)
        if err: return None,err
        leaves.extend(sub)
    return leaves,None

def build_interaction(leaves,max_w):
    vsets=[set(vars_of(x)) for x in leaves]; adj={i:[] for i in range(len(leaves))}; edges=[]
    for i in range(len(leaves)):
        for j in range(i+1,len(leaves)):
            inter=sorted(vsets[i]&vsets[j])
            if inter:
                if len(inter)>max_w: return None,'SEPARATOR_WIDTH_EXCEEDED'
                edges.append((i,j,inter)); adj[i].append((j,inter)); adj[j].append((i,inter))
    if not leaves: return None,'NO_LEAVES'
    seen={0}; q=[0]
    while q:
        u=q.pop()
        for v,_ in adj[u]:
            if v not in seen: seen.add(v); q.append(v)
    if len(seen)!=len(leaves) or len(edges)!=len(leaves)-1:
        return None,'INTERACTION_GRAPH_NOT_TREE'
    boundaries=[]
    for i in range(len(leaves)):
        b=sorted(set().union(*(set(s) for _,s in adj[i])) if adj[i] else set())
        if len(b)>3: return None,'COMPONENT_BOUNDARY_GT_3'
        boundaries.append(b)
    return {'adj':adj,'edges':edges,'boundaries':boundaries},None

def leaf_relation(raw,boundary):
    allowed=[]; forbidden=[]
    for bits in product([0,1],repeat=len(boundary)):
        fixed={v:bool(b) for v,b in zip(boundary,bits)}
        z=solve_leaf(raw,fixed)
        if not z.get('admitted'):
            return None,'LOCAL_RELATION_NOT_DERIVED'
        rec={'tuple':list(bits),'slot':z.get('slot'),'certificate':z.get('certificate')}
        if z['decision']=='SAT':
            rec['witness']=z['assignment']; allowed.append(rec)
        else: forbidden.append(rec)
    return {'boundary':list(boundary),'allowed':allowed,'forbidden':forbidden},None

def _entry_map(rel,entry):
    return {v:bool(b) for v,b in zip(rel['boundary'],entry['tuple'])}

def transfer_join(raw,leaves,graph,relations):
    adj=graph['adj']; parent={0:None}; order=[0]
    for u in order:
        for v,_ in adj[u]:
            if v not in parent: parent[v]=u; order.append(v)
    children={u:[v for v,_ in adj[u] if parent.get(v)==u] for u in range(len(leaves))}
    feasible={}; messages=[]
    for u in reversed(order):
        good=[]
        for idx,e in enumerate(relations[u]['allowed']):
            amap=_entry_map(relations[u],e); ok=True
            for ch in children[u]:
                sep=next(s for v,s in adj[u] if v==ch)
                found=False
                for j in feasible[ch]:
                    cmap=_entry_map(relations[ch],relations[ch]['allowed'][j])
                    if all(amap[x]==cmap[x] for x in sep): found=True; break
                if not found: ok=False; break
            if ok: good.append(idx)
        feasible[u]=good
        if parent[u] is not None:
            p=parent[u]; sep=next(s for v,s in adj[u] if v==p); vals=[]; seen=set()
            for idx in good:
                amap=_entry_map(relations[u],relations[u]['allowed'][idx]); t=tuple(int(amap[x]) for x in sep)
                if t not in seen: seen.add(t); vals.append(list(t))
            messages.append({'from':u,'to':p,'separator':list(sep),'tuples':vals})
    if not feasible[0]:
        return {'decision':'UNSAT','assignment':None,'certificate':{'kind':'tree_relational_elimination','messages':messages,'root_feasible':[],'feasible_entry_indices':feasible}}
    chosen={}; global_a={}
    def pick(u,parent_assignment=None):
        for idx in feasible[u]:
            e=relations[u]['allowed'][idx]; amap=_entry_map(relations[u],e)
            if parent_assignment is not None:
                p=parent[u]; sep=next(s for v,s in adj[u] if v==p)
                if any(amap[x]!=parent_assignment[x] for x in sep): continue
            chosen[u]=idx
            wit={int(k):bool(v) for k,v in e['witness'].items()}
            for v,val in wit.items():
                if v in global_a and global_a[v]!=val: return False
                global_a[v]=val
            for ch in children[u]:
                if not pick(ch,amap): return False
            return True
        return False
    if not pick(0,None): return {'decision':'INTERNAL_ERROR','assignment':None,'certificate':{'kind':'reconstruction_failed'}}
    for v in vars_of(raw): global_a.setdefault(v,False)
    if not replay(raw,global_a): return {'decision':'INTERNAL_ERROR','assignment':global_a,'certificate':{'kind':'root_replay_failed'}}
    return {'decision':'SAT','assignment':global_a,'certificate':{'kind':'tree_relational_elimination','messages':messages,'root_feasible':[chosen[0]],'chosen_entries':chosen}}

def solve_formula(raw,rule):
    t0=time.perf_counter(); cnf=canon(raw); t1=time.perf_counter()
    max_w=int(rule['max_separator_width'])
    leaves,err=discover_leaves(cnf,max_w); t2=time.perf_counter()
    if err: return {'admitted':False,'reason':err,'timing':{'normalize_ms':(t1-t0)*1000,'structure_ms':(t2-t1)*1000,'relation_ms':0.0,'transfer_ms':0.0,'reconstruct_ms':0.0}}
    graph,err=build_interaction(leaves,max_w)
    if err: return {'admitted':False,'reason':err,'leaf_count':len(leaves),'timing':{'normalize_ms':(t1-t0)*1000,'structure_ms':(time.perf_counter()-t1)*1000,'relation_ms':0.0,'transfer_ms':0.0,'reconstruct_ms':0.0}}
    relations=[]; tr0=time.perf_counter()
    for leaf,b in zip(leaves,graph['boundaries']):
        rel,e=leaf_relation(leaf,b)
        if e: return {'admitted':False,'reason':e,'leaf_count':len(leaves),'timing':{'normalize_ms':(t1-t0)*1000,'structure_ms':(tr0-t1)*1000,'relation_ms':(time.perf_counter()-tr0)*1000,'transfer_ms':0.0,'reconstruct_ms':0.0}}
        relations.append(rel)
    tr1=time.perf_counter(); z=transfer_join(cnf,leaves,graph,relations); tr2=time.perf_counter()
    if z['decision'] not in ('SAT','UNSAT'):
        return {'admitted':False,'reason':z['decision'],'leaf_count':len(leaves),'timing':{'normalize_ms':(t1-t0)*1000,'structure_ms':(tr0-t1)*1000,'relation_ms':(tr1-tr0)*1000,'transfer_ms':(tr2-tr1)*1000,'reconstruct_ms':0.0}}
    return {'admitted':True,'decision':z['decision'],'assignment':z.get('assignment'),'certificate':{'kind':'rho_tree_transfer','rule_id':rule['id'],'max_separator_width':max_w,'leaves':leaves,'edges':[[a,b,s] for a,b,s in graph['edges']],'boundaries':graph['boundaries'],'relations':relations,'transfer':z['certificate']},'leaf_count':len(leaves),'timing':{'normalize_ms':(t1-t0)*1000,'structure_ms':(tr0-t1)*1000,'relation_ms':(tr1-tr0)*1000,'transfer_ms':(tr2-tr1)*1000,'reconstruct_ms':0.0}}

def rule_hash(rule):
    payload={'rule':rule,'operations':RULE_OPS,'lower_primitives':LOWER_PRIMITIVES}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
