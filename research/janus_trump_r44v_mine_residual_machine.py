#!/usr/bin/env python3
import json
from collections import Counter, defaultdict, deque


def normalize(cnf):
    out=[]
    for clause in cnf:
        c=[]; seen=set(); taut=False
        for lit in clause:
            lit=int(lit)
            if -lit in seen:
                taut=True; break
            if lit not in seen:
                seen.add(lit); c.append(lit)
        if not taut:
            out.append(tuple(c))
    return out


def simplify(cnf, assignment):
    out=[]
    for c in cnf:
        sat=False; nc=[]
        for l in c:
            v=abs(l)
            if v in assignment:
                if assignment[v] == (l>0): sat=True; break
            else:
                nc.append(l)
        if not sat:
            out.append(tuple(nc))
    return out


def preprocess(cnf):
    cnf=normalize(cnf)
    assignment={}; receipt=[]
    while True:
        cnf=simplify(cnf, assignment)
        if any(len(c)==0 for c in cnf):
            return cnf, assignment, receipt, 'UNSAT_BY_EMPTY_CLAUSE'
        units=[c[0] for c in cnf if len(c)==1]
        if units:
            l=units[0]; v=abs(l); val=l>0
            if v in assignment and assignment[v]!=val:
                return [tuple()], assignment, receipt, 'UNSAT_BY_UNIT_CONFLICT'
            assignment[v]=val; receipt.append({'rule':'UNIT','var':v,'value':val}); continue
        pos=Counter(); neg=Counter(); occ=Counter()
        clause_ids=defaultdict(list)
        for i,c in enumerate(cnf):
            for l in c:
                v=abs(l); occ[v]+=1; clause_ids[v].append(i)
                if l>0: pos[v]+=1
                else: neg[v]+=1
        pure=next((v for v in occ if pos[v]==0 or neg[v]==0),None)
        if pure is not None:
            val=pos[pure]>0
            assignment[pure]=val; receipt.append({'rule':'PURE','var':pure,'value':val}); continue
        leaf=next((v for v,d in occ.items() if d==1),None)
        if leaf is not None:
            i=clause_ids[leaf][0]
            lit=next(l for l in cnf[i] if abs(l)==leaf)
            assignment[leaf]=lit>0
            receipt.append({'rule':'DEGREE_ONE','var':leaf,'value':lit>0,'clause_index':i}); continue
        break
    return cnf, assignment, receipt, 'FIXPOINT'


def signature(cnf):
    occ=Counter(); pos=Counter(); neg=Counter()
    var_to_clauses=defaultdict(list)
    for i,c in enumerate(cnf):
        for l in c:
            v=abs(l); occ[v]+=1; var_to_clauses[v].append(i)
            if l>0: pos[v]+=1
            else: neg[v]+=1
    vars_=sorted(occ)
    balanced=all(pos[v]>0 and neg[v]>0 for v in vars_)
    mindeg=min((occ[v] for v in vars_), default=0)
    no_units=all(len(c)>=2 for c in cnf)
    # incidence connected components over clauses via shared variables
    seen=set(); comps=[]
    for s in range(len(cnf)):
        if s in seen: continue
        q=[s]; seen.add(s); cc=[]
        while q:
            i=q.pop(); cc.append(i)
            for l in cnf[i]:
                for j in var_to_clauses[abs(l)]:
                    if j not in seen:
                        seen.add(j); q.append(j)
        comps.append(cc)
    return {
        'variables':len(vars_), 'clauses':len(cnf), 'min_variable_occurrence_degree':mindeg,
        'bipolar_all_variables':balanced, 'no_unit_clause':no_units,
        'incidence_components':len(comps),
        'candidate_machine': bool(cnf) and no_units and balanced and mindeg>=2
    }

FIXTURES={
 'R44F_BASE': [[1,2,3],[1,2,-3],[-1,-2,3]],
 'R44L_NAE3': [[1,2,3],[-1,-2,-3]],
 'R44D_FRESH': [[1,2,3],[1,-2,-3],[-1,2,-3],[-1,-2,3],[1,2,-4],[-1,3,4],[2,-3,4],[-2,3,-4],[1,-3,4],[-1,-2,-4]],
 'FRINGE_CONTROL': [[1],[1,2,3],[4,2,-3],[-2,-3,5]]
}

rows=[]
for name,cnf in FIXTURES.items():
    residual,assignment,receipt,status=preprocess(cnf)
    sig=signature(residual)
    rows.append({'id':name,'status':status,'residual':[list(c) for c in residual],
                 'elimination_receipt':receipt,'assignment_fragment':assignment,'signature':sig})

frozen=[r for r in rows if r['id']!='FRINGE_CONTROL']
all_match=all(r['signature']['candidate_machine'] for r in frozen)
print(json.dumps({
 'gate_id':'R44V_ARBITRARY_3CNF_RESIDUAL_MACHINE_MINING_WITH_FIXED_CORE',
 'candidate_machine':'BALANCED_BIPOLAR_INCIDENCE_2CORE_V1',
 'fixtures':rows,
 'all_frozen_residuals_match_candidate_machine':all_match,
 'universal_invariant_proved':False,
 'U1':'OPEN',
 'P_VS_NP':'OPEN',
 'next_gate':'R44W_BIPOLAR_2CORE_COMPRESSION_OR_EXPLICIT_COUNTEREXAMPLE'
},sort_keys=True))
