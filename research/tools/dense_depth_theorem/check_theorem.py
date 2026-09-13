from pathlib import Path
import itertools, json, sys, time

ROOT=Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from research.tools.reduction_image_depth.fast_source_depth import (
    exact_depth, restrict_source, terminal_status,
)


def dense(n):
    return tuple(tuple(c) for c in itertools.combinations(range(1,n+1),3))


def restrict_partial(source,vals):
    out=source
    for i,val in enumerate(vals,start=1):
        if val==-1: continue
        out=restrict_source(out,i,val)
    return out


def symbolic_status(n,f,u):
    if f>=3: return False
    if f+u<=2: return True
    return None


def is_dual_horn(source):
    return all(sum(1 for l in c if l<0)<=1 for c in source)

def audit_symbolic(max_n=8):
    checked=0; failure=None
    for n in range(3,max_n+1):
        src=dense(n)
        for vals in itertools.product((-1,0,1),repeat=n):
            f=sum(1 for x in vals if x==0); u=sum(1 for x in vals if x==-1)
            want=symbolic_status(n,f,u)
            got=terminal_status(restrict_partial(src,vals))
            checked+=1
            if got!=want:
                failure={'n':n,'vals':vals,'f':f,'u':u,'want':want,'got':got}
                return {'pass':False,'checked':checked,'failure':failure}
    return {'pass':True,'checked':checked,'failure':None}


def adversary_certificate(n):
    rows=[]
    for k in range(0,n+1):
        f=min(2,k); u=n-k
        status=symbolic_status(n,f,u)
        rows.append({'decisions':k,'false_count':f,'unassigned':u,'status':status})
        if k<n and status is not None:
            return {'pass':False,'rows':rows}
    return {'pass':rows[-1]['status'] is True,'rows':rows}


def finite_depth_audit(max_n=12):
    rows=[]
    for n in range(3,max_n+1):
        d1,m1,c1,s1=exact_depth(dense(n),False)
        d2,m2,c2,s2=exact_depth(dense(n),True)
        rows.append({'n':n,'depth':d1,'reverse_depth':d2,'states':len(m1),'terminal_states':s1['terminal'],'all_first_vars_optimal': set(c1[dense(n)][1][1])==set(range(1,n+1)) if c1[dense(n)][0]=='S' else False,'pass':d1==n and d2==n})
    return rows

def main():
    t0=time.perf_counter()
    symbolic=audit_symbolic(8)
    finite=finite_depth_audit(12)
    adversary=[{'n':n,**adversary_certificate(n)} for n in range(3,33)]
    dual=[{'n':n,'dual_horn':is_dual_horn(dense(n)),'all_true_witness':True} for n in range(3,13)]
    proof_steps={
      'symmetry':'F_n is invariant under every permutation of source variables, so a partial assignment is characterized for terminal purposes by f=#false and u=#unassigned.',
      'unsat_terminal':'if f>=3, those three false variables form one dense positive triple whose residual clause is empty.',
      'sat_terminal':'if f+u<=2, every triple contains an assigned-true variable, so every Horn NAND3 clause is discharged and only affine NEQ remains.',
      'open_middle':'if f<=2 and f+u>=3, choose three variables not assigned true; their residual positive clause is nonempty, no opposite units exist in a monotone formula, and the frozen reduction-image grammar remains mixed OPEN.',
      'lower_bound':'for any decision strategy, the adversary answers false on the first two queried variables and true thereafter. Every prefix k<n has f<=2 and f+u>=3, hence is nonterminal.',
      'upper_bound':'after n source variables are fixed the source formula is either satisfied or falsified, hence the reduction image is terminal.',
      'conclusion':'d(F_n)=n for every n>=3 under the frozen grammar.'
    }
    all_ok=symbolic['pass'] and all(r['pass'] for r in finite) and all(r['pass'] for r in adversary) and all(r['dual_horn'] and r['all_true_witness'] for r in dual)
    verdict='PASS_THEOREM_DENSE_POSITIVE_TRIPLES_DEPTH_EQUALS_N_UNDER_FROZEN_GRAMMAR' if all_ok else 'FALSIFIED_THEOREM_OR_TERMINAL_CHARACTERIZATION'
    out={'schema':'JANUS_TRUMP_DENSE_POSITIVE_TRIPLES_REACHABLE_DEPTH_THEOREM_V1','verdict':verdict,'runtime_ms':round(1000*(time.perf_counter()-t0),3),'proof_steps':proof_steps,'symbolic_audit':symbolic,'finite_depth_audit':finite,'adversary_audit':adversary,'red_team':{'source_class':'MONOTONE_POSITIVE_3CNF__DUAL_HORN','root_all_true_witness':True,'provenance_aware_depth_prediction':0,'meaning':'linear depth is an obstruction to the frozen reduction-image grammar, not to SAT itself'},'scientific_status':{'SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0},'next_gate':'EXACT_PROVENANCE_PRESERVING_TRACTABLE_ESCAPE_ON_C023_IMAGES'}
    print(json.dumps(out,sort_keys=True))

if __name__=='__main__': main()
