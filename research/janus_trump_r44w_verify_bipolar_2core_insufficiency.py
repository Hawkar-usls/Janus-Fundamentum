#!/usr/bin/env python3
import json

# Exact semantic witness: padding arbitrary 3CNF with satisfiable auxiliary clauses
# can enforce both polarities and repeated incidence without deciding the original formula.

def vars_of(cnf):
    return sorted({abs(l) for c in cnf for l in c})

def eval_clause(c,a):
    return any(a[abs(l)] == (l>0) for l in c)

def sat(cnf,a):
    return all(eval_clause(c,a) for c in cnf)

def pad(cnf):
    out=[list(c) for c in cnf]
    nextv=max(vars_of(cnf) or [0])+1
    aux={}
    for x in vars_of(cnf):
        a,b=nextv,nextv+1; nextv+=2
        aux[x]=(a,b)
        g1=[x,a,b]
        g2=[-x,a,b]
        # duplicate only to make the incidence point explicit; semantic witness does not rely on uniqueness.
        out.extend([g1,g2,list(g1),list(g2)])
    return out,aux

def occurrences(cnf,x):
    p=sum(1 for c in cnf for l in c if l==x)
    n=sum(1 for c in cnf for l in c if l==-x)
    return p,n

# Two arbitrary 3CNF seeds, one SAT and one explicit UNSAT complete cube on 3 variables.
sat_seed=[[1,2,3],[-1,2,3]]
unsat_seed=[]
for mask in range(8):
    c=[]
    for i,x in enumerate((1,2,3)):
        bit=(mask>>i)&1
        c.append(-x if bit else x)
    unsat_seed.append(c)

checks=[]
for name,F in [('SAT_SEED',sat_seed),('UNSAT_CUBE',unsat_seed)]:
    P,aux=pad(F)
    # Every original assignment extends to the padded formula by setting every a_x=True.
    # Therefore satisfiability of F iff satisfiability of padded(F).
    vs=vars_of(F)
    preserved=True
    for mask in range(1<<len(vs)):
        base={x:bool((mask>>i)&1) for i,x in enumerate(vs)}
        ext=dict(base)
        for x,(a,b) in aux.items():
            ext[a]=True; ext[b]=False
        if sat(F,base) != sat(P,ext):
            preserved=False; break
    assert preserved
    bipolar={x:occurrences(P,x) for x in vs}
    assert all(p>=2 and n>=2 for p,n in bipolar.values())
    checks.append({'id':name,'original_variables':vs,'bipolar_counts':bipolar,'extension_preserves_each_assignment_truth':True})

print(json.dumps({
  'gate_id':'R44W_BIPOLAR_2CORE_COMPRESSION_OR_EXPLICIT_COUNTEREXAMPLE',
  'verdict':'BIPOLAR_2CORE_ALONE_IS_INSUFFICIENT_FOR_U1',
  'checks':checks,
  'meaning':'An arbitrary 3CNF can be padded in polynomial time so every original variable has repeated positive and negative incidence while preserving satisfiability. Polarity/degree alone therefore cannot be the universal compression certificate.',
  'hardness_claim':False,
  'P_EQUALS_NP':'NOT_PROVED',
  'P_NE_NP':'NOT_PROVED',
  'P_VS_NP':'OPEN',
  'next_gate':'R44X_MINE_STRONGER_CORE_SIGNATURE_BEYOND_PURE_DEGREE_POLARITY'
},sort_keys=True))
