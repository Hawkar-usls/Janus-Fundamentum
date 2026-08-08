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
def expected_graph_counts(mult):
 s=sum(a==1 for a in mult);rr=len(mult)-s
 states=(2**s)*(3**rr)
 atom=0 if s==0 else s*(2**(s-1))*(3**rr)
 rep=0 if rr==0 else 2*rr*(2**s)*(3**(rr-1))
 return states,atom+rep,s,rr

def solve_dp(U,mult):
 k=len(U);K=(1<<k)-1;r=rho_table(U);best={(0,0):0};edge_count=0
 for score in range(2*k+1):
  layer=[st for st in tuple(best) if st[0].bit_count()+st[1].bit_count()==score]
  for P,S in layer:
   cur=best[(P,S)]
   for j,a in enumerate(mult):
    bit=1<<j;nxt=None
    if not S&bit:nxt=(P|bit,S|bit) if a==1 else (P,S|bit)
    elif a>=2 and (S&bit) and not (P&bit):nxt=(P|bit,S)
    if nxt is not None:
     edge_count+=1;val=max(cur,width(nxt[0],nxt[1],r,k))
     if val<best.get(nxt,BIG):best[nxt]=val
 exp_states,exp_edges,_,_=expected_graph_counts(mult)
 assert len(best)==exp_states and edge_count==exp_edges
 return best[(K,K)],len(best),edge_count

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
 cases=orders=counter=0;max_states=max_edges=0;max_k=0;k5=0;checks=0
 for n in range(3):
  S=subspaces(n)
  for k in range(1,4):
   for U in itertools.product(S,repeat=k):
    for mult in itertools.product((1,2),repeat=k):
     d,ns,ne=solve_dp(U,mult);b,c=brute_orders(U,mult);cases+=1;orders+=c;checks+=1;max_states=max(max_states,ns);max_edges=max(max_edges,ne);max_k=max(max_k,k);counter+=(d!=b)
 S=subspaces(3);families=[S[:4],(S[1],S[2],S[3],S[4]),(S[1],S[1],S[2],S[3])]
 for U in families:
  for mult in itertools.product((1,2),repeat=4):
   d,ns,ne=solve_dp(U,mult);b,c=brute_orders(U,mult);cases+=1;orders+=c;checks+=1;max_states=max(max_states,ns);max_edges=max(max_edges,ne);max_k=4;counter+=(d!=b)
 U=(S[1],S[2],S[3],S[4],S[5]);mult=(2,2,2,2,2)
 d,ns,ne=solve_dp(U,mult);b,c=brute_orders(U,mult);cases+=1;orders+=c;checks+=1;k5=c;max_states=max(max_states,ns);max_edges=max(max_edges,ne);max_k=5;counter+=(d!=b)
 return {'cases':cases,'bruteforce_event_orders':orders,'counterexamples':counter,'graph_count_checks':checks,'max_states_observed':max_states,'max_edges_observed':max_edges,'max_k':max_k,'k5_all_repeated_valid_orders':k5,'k5_exact_states':ns,'k5_exact_transitions':ne,'k5_state_bound':3**5,'k5_transition_bound':5*3**5}
def validate(c,ctl):
 assert c['schema']=='janus.fundamentum.a3.kclass_endpoint_dp_certificate.v1_1'
 assert c['theorem_id']=='A3_KCLASS_ENDPOINT_DP_THEOREM_V1'
 assert c['rank_identity']=='lambda(P,S)=rho(S)+rho(K\\P)-rho(K)'
 assert c['exact_state_count']=='2^s*3^r' and c['state_bound']=='2^s*3^r<=3^k'
 assert c['exact_transition_count']=='s*2^(s-1)*3^r + 2r*2^s*3^(r-1)'
 assert c['transition_bound']=='k*2^s*3^r<=k*3^k'
 assert c['dp_after_rank_precompute']=='O(k*3^k)' and c['state_width_after_rank_precompute']=='O(1)' and c['subset_rank_entries']=='2^k'
 assert c['controls']==ctl and c['counterexamples']==0
 assert c['algorithmic_fpt']=='CANDIDATE_PENDING_SEMANTIC_ADMISSION'
 assert c['evidence_strength']=='ES3_IF_CI_SUCCESS_PENDING_SEMANTIC_ADMISSION'
 assert c['novelty']=='N0_PENDING_AUDIT' and c['p_vs_np']=='OPEN'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--certificate',required=True);ap.add_argument('--tamper-test',action='store_true');a=ap.parse_args();c=json.load(open(a.certificate));ctl=recompute();validate(c,ctl)
 print('KCLASS_ENDPOINT_DP_INDEPENDENT_REPLAY = PASS');print('EXACT_STATE_COUNT_REPLAY = PASS');print('EXACT_TRANSITION_COUNT_REPLAY = PASS');print('BRUTEFORCE_CONTROLS_RECOMPUTED =',ctl['cases']);print('BRUTEFORCE_EVENT_ORDERS_RECOMPUTED =',ctl['bruteforce_event_orders']);print('GRAPH_COUNT_CHECKS_RECOMPUTED =',ctl['graph_count_checks']);print('K5_ALL_REPEATED_VALID_ORDERS_RECOMPUTED =',ctl['k5_all_repeated_valid_orders']);print('K5_EXACT_STATES =',ctl['k5_exact_states']);print('K5_EXACT_TRANSITIONS =',ctl['k5_exact_transitions']);print('K5_STATE_BOUND =',ctl['k5_state_bound']);print('K5_TRANSITION_BOUND =',ctl['k5_transition_bound']);print('COUNTEREXAMPLES =',ctl['counterexamples'])
 if a.tamper_test:
  mutations=[('theorem_id','X'),('rank_identity','X'),('exact_state_count','3^k'),('state_bound','4^k'),('exact_transition_count','X'),('transition_bound','2k*3^k'),('dp_after_rank_precompute','O((2k)!)'),('state_width_after_rank_precompute','O(d^3)'),('subset_rank_entries','3^k'),('counterexamples',1),('algorithmic_fpt','ESTABLISHED'),('evidence_strength','ES7'),('novelty','N4'),('p_vs_np','P_EQUALS_NP')]
  rejected=0
  for key,val in mutations:
   x=json.loads(json.dumps(c));x[key]=val
   try:validate(x,ctl)
   except Exception:rejected+=1
  x=json.loads(json.dumps(c));x['controls']['k5_exact_transitions']+=1
  try:validate(x,ctl)
  except Exception:rejected+=1
  x=json.loads(json.dumps(c));x['controls']['graph_count_checks']-=1
  try:validate(x,ctl)
  except Exception:rejected+=1
  assert rejected==16;print('TAMPERS_REJECTED = 16/16')
 print('P_VS_NP = OPEN')
if __name__=='__main__':main()
