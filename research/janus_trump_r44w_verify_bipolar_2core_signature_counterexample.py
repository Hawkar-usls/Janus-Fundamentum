#!/usr/bin/env python3
import itertools, json

UNSAT=[[-1,-2,-4],[-1,-2,4],[-1,2,-4],[-1,2,4],[1,-3,-4],[1,-3,4],[1,-2,3],[1,2,3]]
SAT=[[-1,-2,-3],[-1,2,-4],[-1,2,-3],[-1,3,-4],[1,-2,-4],[1,-2,4],[1,2,4],[1,3,4]]


def vars_of(cnf):
    return sorted({abs(l) for c in cnf for l in c})


def signature(cnf):
    vs=vars_of(cnf)
    return tuple((sum(v in c for c in cnf),sum(-v in c for c in cnf)) for v in vs)


def decision(cnf):
    vs=vars_of(cnf)
    rejected=[]
    for bits in itertools.product([False,True],repeat=len(vs)):
        a=dict(zip(vs,bits))
        ok=all(any(a[abs(l)]==(l>0) for l in c) for c in cnf)
        if ok:
            return 'SAT',a,rejected
        rejected.append(bits)
    return 'UNSAT',None,rejected


def main():
    su=signature(UNSAT); ss=signature(SAT)
    assert su==ss==((4,4),(3,3),(2,2),(3,3))
    assert all(p>=1 and n>=1 and p+n>=2 for p,n in su)
    du,wu,ru=decision(UNSAT)
    ds,ws,rs=decision(SAT)
    assert du=='UNSAT' and len(ru)==16
    assert ds=='SAT' and ws is not None
    out={
      'gate_id':'R44W_BIPOLAR_2CORE_COMPRESSION_OR_EXPLICIT_COUNTEREXAMPLE',
      'shared_signature':[list(x) for x in su],
      'unsat_status':du,
      'unsat_assignments_rejected':len(ru),
      'sat_status':ds,
      'sat_witness':ws,
      'coarse_signature_exact_decision_sufficient':False,
      'stronger_polynomial_compression_ruled_out':False,
      'P_VS_NP':'OPEN',
      'next_gate':'R44X_INTERACTION_SIGNATURE_COMPRESSION_OR_STRONGER_COUNTEREXAMPLE'
    }
    print(json.dumps(out,sort_keys=True))

if __name__=='__main__': main()
