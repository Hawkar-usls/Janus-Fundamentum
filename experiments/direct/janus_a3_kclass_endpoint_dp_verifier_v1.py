#!/usr/bin/env python3
import argparse,itertools,json

BIG=10**9

def xor_rank(vs):
 piv={}
 for x in vs:
  y=x
  while y:
   p=y.bit_length()-1
   if p in piv:y^=piv[p]
   else:piv[p]=y;break
 return len(piv)

def span(vs):
 s={0}
 for v in vs:s|={x^v for x in tuple(s)}
 return frozenset(s)
def subspaces(n):
 nz=list(range(1,1<<n));out={frozenset({0})}
 for m in range(1<<len(nz)):
  out.add(span(nz[i] for i in range(len(nz)) if (m>>i)&1))
 return tuple(sorted(out,key=lambda A:(len(A),tuple(sorted(A)))))

def rho_table(U):
 k=len(U);r=[0]*(1<<k)
 for m in range(1<<k):
  vv=[]
  for j in range(k):
   if (m>>j)&1:vv.extend(U[j])
  r[m]=xor_rank(vv)
 return r

def width(P,S,r,k):
 K=(1<<k)-1
 return r[S]+r[K^P]-r[K]

def solve_dp(U,mult):
 k=len(U);K=(1<<k)-1;r=rho_table(U);best={(0,0):0}
 for score in range(2*k+1):
  layer=[st for st in tuple(best) if st[0].bit_count()+st[1].bit_count()==score]
  for P,S in layer:
   cur=best[(P,S)]
   for j,a in enumerate(mult):
    bit=1<<j
    nxt=None
    if not S&bit:
     nxt=(P|bit,S|bit) if a==1 else (P,S|bit)
    elif a>=2 and (S&bit) and not (P&bit):
     nxt=(P|bit,S)
    if nxt is not None:
     val=max(cur,width(nxt[0],nxt[1],r,k))
     if val<best.get(nxt,BIG):best[nxt]=val
 return best[(K,K)],len(best)

def brute_orders(U,mult):
 k=len(U);K=(1<<k)-1;r=rho_table(U);opt=BIG;leaves=0
 def walk(P,S,mx):
  nonlocal opt,leaves
  if P==K and S==K:
   leaves+=1;opt=min(opt,mx);return
  for j,a in enumerate(mult):
   bit=1<<j;nxt=None
   if not S&bit:nxt=(P|bit,S|bit) if a==1 else (P,S|bit)
   elif a>=2 and S&bit and not P&bit:nxt=(P|bit,S)
   if nxt is not None:walk(nxt[0],nxt[1],max(mx,width(nxt[0],nxt[1],r,k)))
 walk(0,0,0)
 return opt,leaves

def recompute():
 cases=orders=counter=0;max_states=0;max_k=0;k5=0
 for n in range(3):
  S=subspaces(n)
  for k in range(1,4):
   for U in itertools.product(S,repeat=k):
    for mult in itertools.product((1,2),repeat=k):
     d,ns=solve_dp(U,mult);b,c=brute_orders(U,mult);cases+=1;orders+=c;max_states=max(max_states,ns);max_k=max(max_k,k)
     counter += (d!=b)
 S=subspaces(3);families=[S[:4],(S[1],S[2],S[3],S[4]),(S[1],S[1],S[2],S[3])]
 for U in families:
  for mult in itertools.product((1,2),repeat=4):
   d,ns=solve_dp(U,mult);b,c=brute_orders(U,mult);cases+=1;orders+=c;max_states=max(max_states,ns);max_k=4;counter+=(d!=b)
 U=(S[1],S[2],S[3],S[4],S[5]);mult=(2,2,2,2,2)
 d,ns=solve_dp(U,mult);b,c=brute_orders(U,mult);cases+=1;orders+=c;k5=c;max_states=max(max_states,ns);max_k=5;counter+=(d!=b)
 return {'cases':cases,'bruteforce_event_orders':orders,'counterexamples':counter,'max_states_observed':max_states,'max_k':max_k,'k5_all_repeated_valid_orders':k5,'k5_state_bound':243}

def validate(c,ctl):
 assert c['schema']=='janus.fundamentum.a3.kclass_endpoint_dp_certificate.v1'
 assert c['theorem_id']=='A3_KCLASS_ENDPOINT_DP_THEOREM_V1'
 assert c['rank_identity']=='lambda(P,S)=rho(S)+rho(K\\P)-rho(K)'
 assert c['state_bound']=='3^k' and c['transition_bound']=='2k*3^k'
 assert c['dp_after_rank_precompute']=='O(k*3^k)' and c['subset_rank_entries']=='2^k'
 assert c['controls']==ctl and c['counterexamples']==0
 assert c['algorithmic_fpt']=='CANDIDATE_PENDING_SEMANTIC_ADMISSION'
 assert c['evidence_strength']=='ES3_IF_CI_SUCCESS_PENDING_SEMANTIC_ADMISSION'
 assert c['novelty']=='N0_PENDING_AUDIT' and c['p_vs_np']=='OPEN'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--certificate',required=True);ap.add_argument('--tamper-test',action='store_true');a=ap.parse_args();c=json.load(open(a.certificate));ctl=recompute();validate(c,ctl)
 print('KCLASS_ENDPOINT_DP_INDEPENDENT_REPLAY = PASS');print('BRUTEFORCE_CONTROLS_RECOMPUTED =',ctl['cases']);print('BRUTEFORCE_EVENT_ORDERS_RECOMPUTED =',ctl['bruteforce_event_orders']);print('K5_ALL_REPEATED_VALID_ORDERS_RECOMPUTED =',ctl['k5_all_repeated_valid_orders']);print('K5_DP_STATE_BOUND =',ctl['k5_state_bound']);print('COUNTEREXAMPLES =',ctl['counterexamples'])
 if a.tamper_test:
  mutations=[('theorem_id','X'),('rank_identity','X'),('state_bound','4^k'),('transition_bound','k!'),('dp_after_rank_precompute','O((2k)!)'),('subset_rank_entries','3^k'),('counterexamples',1),('algorithmic_fpt','ESTABLISHED'),('evidence_strength','ES7'),('novelty','N4'),('p_vs_np','P_EQUALS_NP')]
  rejected=0
  for key,val in mutations:
   x=json.loads(json.dumps(c));x[key]=val
   try:validate(x,ctl)
   except Exception:rejected+=1
  x=json.loads(json.dumps(c));x['controls']['k5_state_bound']=244
  try:validate(x,ctl)
  except Exception:rejected+=1
  assert rejected==12;print('TAMPERS_REJECTED = 12/12')
 print('P_VS_NP = OPEN')
if __name__=='__main__':main()
