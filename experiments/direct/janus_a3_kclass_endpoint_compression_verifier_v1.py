#!/usr/bin/env python3
import argparse,itertools,json

def span(vs):
 s={0}
 for v in vs:s|={x^v for x in tuple(s)}
 return frozenset(s)
def subs(n):
 nz=list(range(1,1<<n));out={frozenset({0})}
 for m in range(1<<len(nz)):out.add(span(nz[i] for i in range(len(nz)) if (m>>i)&1))
 return tuple(sorted(out,key=lambda x:(len(x),tuple(sorted(x)))))
def plus(spaces):
 s=frozenset({0})
 for A in spaces:s=frozenset(x^y for x in s for y in A)
 return s
def d(A):return len(A).bit_length()-1
def pats(mult):
 mult=list(mult);n=sum(mult);p=[0]*n
 def rec(i):
  if i==n:yield tuple(p);return
  for j,c in enumerate(mult):
   if c:
    mult[j]-=1;p[i]=j
    yield from rec(i+1)
    mult[j]+=1
 yield from rec(0)
def st(p):return [(frozenset(p[:i]),frozenset(p[i:])) for i in range(len(p)+1)]
def cp(p):
 f={x:p.index(x) for x in set(p)};l={x:len(p)-1-p[::-1].index(x) for x in set(p)}
 return tuple(x for i,x in enumerate(p) if i in (f[x],l[x]))
def wd(p,U):return max(d(plus(U[j] for j in L)&plus(U[j] for j in R)) for L,R in st(p))
def recompute():
 structural=0
 for mult in itertools.product(range(1,5),repeat=3):
  for p in pats(mult):
   structural+=1;assert set(st(p))==set(st(cp(p)))
 geometric=orders=cuts=0
 for n in range(4):
  S=subs(n)
  for U in itertools.product(S,repeat=3):
   for mult in itertools.product((1,2),repeat=3):
    geometric+=1
    for p in pats(mult):
     orders+=1;cuts+=len(p)+1;assert wd(p,U)==wd(cp(p),U)
 return structural,geometric,orders,cuts
def validate(c,got):
 assert c['schema']=='janus.fundamentum.a3.kclass_endpoint_compression_certificate.v1'
 assert c['theorem_id']=='A3_KCLASS_ENDPOINT_COMPRESSION_V1'
 assert c['counterexamples']==0 and c['p_vs_np']=='OPEN'
 assert c['novelty']=='N0_PENDING_AUDIT'
 exp=(c['structural_patterns'],c['geometric_cases'],c['orders'],c['cuts']);assert got==exp
 return True
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--certificate',required=True);ap.add_argument('--tamper-test',action='store_true');a=ap.parse_args();c=json.load(open(a.certificate));got=recompute();validate(c,got)
 print('KCLASS_ENDPOINT_COMPRESSION_INDEPENDENT_REPLAY = PASS');print('STRUCTURAL_PATTERNS_RECOMPUTED =',got[0]);print('GEOMETRIC_CASES_RECOMPUTED =',got[1]);print('ORDERS_RECOMPUTED =',got[2]);print('CUTS_RECOMPUTED =',got[3]);print('COUNTEREXAMPLES = 0')
 if a.tamper_test:
  attacks=[]
  for k,v in [('counterexamples',1),('p_vs_np','P_EQUALS_NP'),('novelty','N4'),('theorem_id','X'),('orders',c['orders']+1),('cuts',c['cuts']-1),('geometric_cases',c['geometric_cases']+1),('structural_patterns',c['structural_patterns']-1)]:
   x=json.loads(json.dumps(c));x[k]=v;attacks.append(x)
  r=0
  for x in attacks:
   try:validate(x,got)
   except Exception:r+=1
  assert r==len(attacks);print(f'TAMPERS_REJECTED = {r}/{len(attacks)}')
 print('P_VS_NP = OPEN')
if __name__=='__main__':main()
