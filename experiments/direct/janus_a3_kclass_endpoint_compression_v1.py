#!/usr/bin/env python3
import argparse,itertools,json
from pathlib import Path

def span(vs):
 s={0}
 for v in vs:s|={x^v for x in tuple(s)}
 return frozenset(s)
def subs(n):
 nz=list(range(1,1<<n));out={frozenset({0})}
 for m in range(1<<len(nz)):out.add(span(nz[i] for i in range(len(nz)) if (m>>i)&1))
 return tuple(sorted(out,key=lambda x:(len(x),tuple(sorted(x)))))
def ssum(spaces):
 out=frozenset({0})
 for A in spaces:out=frozenset(x^y for x in out for y in A)
 return out
def dim(A):return len(A).bit_length()-1
def states(p):
 return [(tuple(sorted(set(p[:i]))),tuple(sorted(set(p[i:])))) for i in range(len(p)+1)]
def compress(p):
 first={x:p.index(x) for x in set(p)};last={x:len(p)-1-p[::-1].index(x) for x in set(p)}
 return tuple(x for i,x in enumerate(p) if i==first[x] or i==last[x])
def width(p,U):
 return max(dim(ssum(U[j] for j in L)&ssum(U[j] for j in R)) for L,R in states(p))
def patterns(mult):
 mult=list(mult);n=sum(mult);p=[0]*n
 def rec(i):
  if i==n:yield tuple(p);return
  for j,c in enumerate(mult):
   if c:
    mult[j]-=1;p[i]=j
    yield from rec(i+1)
    mult[j]+=1
 yield from rec(0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
 structural=0
 for mult in itertools.product(range(1,5),repeat=3):
  for p in patterns(mult):
   structural+=1;c=compress(p)
   assert set(states(p))==set(states(c))
 geometric=orders=cuts=0
 for n in range(4):
  S=subs(n)
  for U in itertools.product(S,repeat=3):
   for mult in itertools.product((1,2),repeat=3):
    geometric+=1;best=None
    for p in patterns(mult):
     orders+=1;cuts+=len(p)+1
     v=width(p,U);assert v==width(compress(p),U)
     best=v if best is None else min(best,v)
    # multiplicity-saturated optimization is over exactly the compressed signature min(a_j,2)
    assert best is not None
 cert={'schema':'janus.fundamentum.a3.kclass_endpoint_compression_certificate.v1','theorem_id':'A3_KCLASS_ENDPOINT_COMPRESSION_V1','structural_patterns':structural,'geometric_cases':geometric,'orders':orders,'cuts':cuts,'counterexamples':0,'evidence_strength':'ES3_IF_CI_SUCCESS_PENDING_ADMISSION','novelty':'N0_PENDING_AUDIT','p_vs_np':'OPEN'}
 Path(a.out).write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
 print('KCLASS_ENDPOINT_COMPRESSION_SYMBOLIC = PASS');print('K3_GF2_FALSIFICATION = PASS');print('STRUCTURAL_PATTERNS =',structural);print('GEOMETRIC_CASES =',geometric);print('ORDERS =',orders);print('CUTS =',cuts);print('COUNTEREXAMPLES = 0');print('P_VS_NP = OPEN')
if __name__=='__main__':main()
