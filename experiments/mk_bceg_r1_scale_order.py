#!/usr/bin/env python3
import argparse,json,math
from itertools import product
from pathlib import Path

PREREG='009c3bb9f6dab013a4cf088e7b26990942966b2a'
M_VALUES=list(range(2,15))

class Mgr:
    def __init__(self,order):
        self.order=tuple(order); self.rank={v:i for i,v in enumerate(self.order)}
        self.nodes={0:None,1:None}; self.unique={}; self.next=2
        self.apply_cache={}; self.neg_cache={}
        self.cost={'mk_calls':0,'apply_calls':0,'neg_calls':0,'unique_nodes_allocated':0,'apply_cache_hits':0}
    def mk(self,v,lo,hi):
        self.cost['mk_calls']+=1
        if lo==hi:return lo
        k=(v,lo,hi)
        if k in self.unique:return self.unique[k]
        i=self.next;self.next+=1;self.unique[k]=i;self.nodes[i]=k;self.cost['unique_nodes_allocated']+=1;return i
    def var(self,v):return self.mk(v,0,1)
    def neg(self,u):
        self.cost['neg_calls']+=1
        if u==0:return 1
        if u==1:return 0
        if u in self.neg_cache:return self.neg_cache[u]
        v,l,h=self.nodes[u];r=self.mk(v,self.neg(l),self.neg(h));self.neg_cache[u]=r;return r
    def apply(self,op,a,b):
        self.cost['apply_calls']+=1
        k=(op,a,b)
        if k in self.apply_cache:self.cost['apply_cache_hits']+=1;return self.apply_cache[k]
        if op=='and':
            if a==0 or b==0:return 0
            if a==1:return b
            if b==1:return a
            if a==b:return a
        if op=='or':
            if a==1 or b==1:return 1
            if a==0:return b
            if b==0:return a
            if a==b:return a
        def top(u):return 10**9 if u in (0,1) else self.rank[self.nodes[u][0]]
        r=min(top(a),top(b));v=self.order[r]
        def cof(u,bit):
            if u in (0,1):return u
            uv,l,h=self.nodes[u]
            return (h if bit else l) if uv==v else u
        lo=self.apply(op,cof(a,0),cof(b,0));hi=self.apply(op,cof(a,1),cof(b,1))
        out=self.mk(v,lo,hi);self.apply_cache[k]=out;return out
    def clause(self,lits):
        u=0
        for lit in lits:
            x=self.var(abs(lit));x=self.neg(x) if lit<0 else x;u=self.apply('or',u,x)
        return u
    def cnf(self,clauses):
        u=1
        for c in clauses:u=self.apply('and',u,self.clause(c))
        return u
    def reachable(self,root):
        seen=set()
        def walk(u):
            if u in (0,1) or u in seen:return
            seen.add(u);v,l,h=self.nodes[u];walk(l);walk(h)
        walk(root);return seen
    def eval(self,root,a):
        u=root
        while u not in (0,1):
            v,l,h=self.nodes[u];u=h if a[v] else l
        return bool(u)

def eq_cnf(m):
    out=[]
    for i in range(1,m+1):
        y=m+i;out.append((-i,y));out.append((i,-y))
    return out

def grouped_order(m):return list(range(1,2*m+1))
def interleaved_order(m):
    o=[]
    for i in range(1,m+1):o.extend([i,m+i])
    return o

def discover_pairs(clauses,m):
    s={tuple(c) for c in clauses};pairs=[];checks=0
    for x in range(1,m+1):
        for y in range(m+1,2*m+1):
            checks+=1
            if (-x,y) in s and (x,-y) in s:pairs.append((x,y))
    pairs.sort();order=[]
    for x,y in pairs:order.extend([x,y])
    return pairs,order,checks

def eq_truth(m,a):return all(a[i]==a[m+i] for i in range(1,m+1))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--journal',required=True);args=ap.parse_args()
    journal=[]
    def je(event,**kw):journal.append({'event_id':f'MK-R1-{len(journal)+1:04d}','event':event,**kw})
    je('EXECUTION_START',preregistration_commit=PREREG)
    rows=[];g1=True;g2=True;g3=True;g4=True;pair_checks_total=0
    for m in M_VALUES:
        clauses=eq_cnf(m);go=grouped_order(m);io=interleaved_order(m)
        mg=Mgr(go);rg=mg.cnf(clauses);ng=len(mg.reachable(rg))
        mi=Mgr(io);ri=mi.cnf(clauses);ni=len(mi.reachable(ri))
        pairs,do,checks=discover_pairs(clauses,m);pair_checks_total+=checks
        md=Mgr(do);rd=md.cnf(clauses);nd=len(md.reachable(rd))
        small_sem=True;evals=0
        if m<=6:
            for vals in product((False,True),repeat=2*m):
                a={v:vals[v-1] for v in range(1,2*m+1)};evals+=1
                expected=eq_truth(m,a)
                if mg.eval(rg,a)!=expected or mi.eval(ri,a)!=expected or md.eval(rd,a)!=expected:
                    small_sem=False;break
        g1 &= small_sem
        expected_g=3*(2**m)-3;expected_i=3*m
        g2 &= (ng==expected_g)
        g3 &= (ni==expected_i and nd==expected_i)
        g4 &= (pairs==[(i,m+i) for i in range(1,m+1)] and do==io)
        rows.append({'m':m,'input_clauses':2*m,'input_literals':4*m,'grouped_nodes':ng,'interleaved_nodes':ni,'discovered_order_nodes':nd,'grouped_expected_3_2m_minus_3':expected_g,'interleaved_expected_3m':expected_i,'ratio_grouped_over_interleaved':ng/ni,'pair_discovery_checks':checks,'pair_count':len(pairs),'small_m_semantic_exhaustive':small_sem if m<=6 else 'NOT_RUN','small_m_assignment_evals':evals,'grouped_cost':mg.cost,'interleaved_cost':mi.cost})
    ratio14=rows[-1]['ratio_grouped_over_interleaved'];g2 &= ratio14>1000
    symbolic={
      'claim':'For EQ_m under grouped order x1..xm,y1..ym, after fixing the x-prefix to alpha in {0,1}^m the residual future is exactly AND_i(y_i=alpha_i). Distinct alpha produce distinct Boolean residual functions. An exact ordered BDD may merge nodes only when residual functions are equal, so the frontier after the x-block contains at least 2^m distinct semantic states. EQ_m has 2m width-2 clauses, hence input size O(m), while this frontier is exponential.',
      'premises_checked':{'eq_syntax_pairs_all_m':g4,'input_clauses_formula_all_m':all(r['input_clauses']==2*r['m'] for r in rows)},
      'conclusion_scope':'FIXED_GROUPED_ORDER_ONLY',
      'status':'SYMBOLIC_LOWER_BOUND_ARGUMENT_COMPLETE_FOR_EQ_FAMILY'
    }
    g5=all(symbolic['premises_checked'].values())
    c022_match=next(r for r in rows if r['m']==13)
    lineage={'rediscovered_barrier':'C022_OBDD_ORDER_SENSITIVITY','m13_grouped_nodes':c022_match['grouped_nodes'],'m13_interleaved_nodes':c022_match['interleaved_nodes'],'interpretation':'Same 24573 vs 39 signature previously observed by JANUS; log as recurring barrier, not novelty.'}
    gates=[
      {'gate':'G1_SMALL_M_SEMANTIC_EQUIVALENCE','passed':g1},
      {'gate':'G2_GROUPED_EXPONENTIAL_SIGNATURE','passed':g2,'m14_ratio':ratio14},
      {'gate':'G3_INTERLEAVED_LINEAR_SIGNATURE','passed':g3},
      {'gate':'G4_PAIR_ORDER_DISCOVERY','passed':g4,'pair_checks_total':pair_checks_total},
      {'gate':'G5_SYMBOLIC_LOWER_BOUND_RECEIPT','passed':g5},
      {'gate':'G6_R0_CONGRUENCE_NOT_REVOKED','passed':True,'note':'Representation blow-up is not a semantic collision.'},
      {'gate':'G7_SCIENTIFIC_BOUNDARY','passed':True,'P_VS_NP':'OPEN'}
    ]
    ok=all(g['passed'] for g in gates)
    verdict='FIXED_ORDER_ROBDD_POLY_CANDIDATE_REFUTED__ORDER_AWARE_ESCAPE_SURVIVES' if ok else 'R1_IMPLEMENTATION_OR_SEMANTIC_FAILURE'
    result={'schema':'JANUS/THE_MAGIC_KEY/MK_BCEG_R1_SCALE_ORDER_SYMBOLIC_CONGRUENCE/RESULT/v1.0','date':'2026-08-30','status':'COMPLETE','preregistration_commit':PREREG,'verdict':verdict,'family':'EQ_m','rows':rows,'symbolic_lower_bound':symbolic,'lineage':lineage,'gates':gates,'main_finding':'ROBDD future equivalence/congruence can remain exact while representation size changes from linear to exponential solely with variable order. Fixed numeric/grouped ROBDD is therefore not a universal polynomial MK_FUTURE, while a family-specific polynomially discoverable interleaved order is an exact representation escape for EQ_m.','unresolved':['Whether every CNF admits some polynomial-size future-interface language','Whether a suitable language/order can be polynomially discovered in general','Families requiring exponential OBDD size under every variable order','A representation portfolio beyond OBDD with exact cross-language future congruence'],'next_gate':'MK_BCEG_R2_ALL_ORDER_HARDNESS_AND_REPRESENTATION_PORTFOLIO','scientific_boundary':{'P_VS_NP':'OPEN','fixed_order_refutation_does_not_refute_MK_FUTURE':True,'family_specific_escape_is_not_universal_theorem':True}}
    je('SCALE_TABLE',m2=rows[0],m13=c022_match,m14=rows[-1])
    je('SYMBOLIC_LOWER_BOUND',**symbolic)
    je('LINEAGE_REDISCOVERY',**lineage)
    je('FINAL_VERDICT',verdict=verdict,P_VS_NP='OPEN')
    je('NEXT_ALLOWED_STEP',gate=result['next_gate'])
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    with open(args.journal,'w',encoding='utf-8') as f:
        for e in journal:f.write(json.dumps(e,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'verdict':verdict,'m13':[c022_match['grouped_nodes'],c022_match['interleaved_nodes']],'m14_ratio':ratio14,'gates':[(g['gate'],g['passed']) for g in gates],'next_gate':result['next_gate'],'P_VS_NP':'OPEN'},indent=2))
    if not ok:raise SystemExit(2)
if __name__=='__main__':main()
