#!/usr/bin/env python3
import argparse, hashlib, itertools, json


def span(vectors):
    s={0}
    for v in vectors:s|={x^v for x in tuple(s)}
    return frozenset(s)

def all_subspaces(n):
    nonzero=list(range(1,1<<n)); out={frozenset({0})}
    for mask in range(1<<len(nonzero)):out.add(span(nonzero[i] for i in range(len(nonzero)) if (mask>>i)&1))
    return tuple(sorted(out,key=lambda s:(len(s),tuple(sorted(s)))))
def d(A):return len(A).bit_length()-1
def ssum(A,B):return frozenset(a^b for a in A for b in B)
def path_formula(a,b,p,q,r):
    if a==1 and b==1:return r
    if a>=2 and b==1:return p
    if a==1 and b>=2:return q
    return max(p,q)
def patterns(a,b):
    N=a+b
    for Upos in itertools.combinations(range(N),a):
        x=['W']*N
        for i in Upos:x[i]='U'
        yield tuple(x)
def side(seq,U,W):
    if not seq:return frozenset({0})
    u='U' in seq; w='W' in seq
    if u and w:return ssum(U,W)
    return U if u else W
def actual_width(P,U,W):return max(d(side(P[:i],U,W)&side(P[i:],U,W)) for i in range(len(P)+1))
def mixed_both(P,a,b):
    u=w=0
    for x in P[:-1]:
        if x=='U':u+=1
        else:w+=1
        if 0<u<a and 0<w<b:return True
    return False
def fixed_formula(P,a,b,p,q,r):return p+q-r if mixed_both(P,a,b) else path_formula(a,b,p,q,r)

REQ_DERIV={
'cut_type_table':'internal side spans are U, W, or U+W; intersection dimensions are p,q,r,s',
'mixed_both_characterization':'mixed on both sides iff 0<u_i<a and 0<w_i<b; then width is s=p+q-r',
'U_lower_bound':'a>=2 => cut between first and last U has U on both sides => width>=p',
'W_lower_bound':'b>=2 => cut between first and last W has W on both sides => width>=q',
'grouped_upper_bound':'U^aW^b has no mixed|mixed cut and maximum equal to the piecewise pathwidth formula',
'grouped_order_characterization':'for a,b>=2, no mixed|mixed cut iff class pattern is U^aW^b or W^bU^a',
'inequality_used':'r<=p,q and s=p+q-r>=p,q'}

def verify(cert,max_n=4,max_mult=3):
    assert cert['schema']=='janus.fundamentum.a3.two_class_repeated_subspace_pathwidth_theorem_certificate.v1_1'
    assert cert['theorem_id']=='A3_TWO_CLASS_REPEATED_SUBSPACE_PATHWIDTH_V1' and cert['field']=='GF(2)'
    assert cert['pathwidth_formula']=={'a=1,b=1':'r','a>=2,b=1':'p','a=1,b>=2':'q','a>=2,b>=2':'max(p,q)'}
    assert cert['fixed_order_formula']=={'mixed_both_cut':'p+q-r','otherwise':'pathwidth_formula','predicate':'exists internal prefix with 0<u_i<a and 0<w_i<b'}
    assert cert['symbolic_derivation']==REQ_DERIV
    assert cert['target_layout_enumeration_used_as_symbolic_premise'] is False
    assert cert['literature_novelty']=='NOT_ESTABLISHED' and cert['world_novel_theorem_claim']=='FORBIDDEN_PENDING_AUDIT' and cert['p_vs_np']=='OPEN'
    stats={'subspace_pairs':0,'multiplicity_cases':0,'class_pattern_layouts':0,'cut_evaluations':0,'fixed_order_counterexamples':0,'pathwidth_counterexamples':0,'mixed_both_orders':0}
    for n in range(max_n+1):
        subs=all_subspaces(n)
        for U in subs:
            for W in subs:
                p,q,r=d(U),d(W),d(U&W); stats['subspace_pairs']+=1; assert r<=p and r<=q
                for a in range(1,max_mult+1):
                    for b in range(1,max_mult+1):
                        stats['multiplicity_cases']+=1; vals=[]
                        for P in patterns(a,b):
                            got=actual_width(P,U,W); exp=fixed_formula(P,a,b,p,q,r)
                            stats['class_pattern_layouts']+=1; stats['cut_evaluations']+=len(P)+1
                            if mixed_both(P,a,b):stats['mixed_both_orders']+=1
                            assert got==exp,(n,p,q,r,a,b,P,got,exp)
                            vals.append(got)
                        assert min(vals)==path_formula(a,b,p,q,r),(n,p,q,r,a,b,min(vals),path_formula(a,b,p,q,r))
    for k,v in stats.items():assert cert['exhaustive_controls'][k]==v,(k,cert['exhaustive_controls'][k],v)
    core={k:v for k,v in cert.items() if k not in {'raw_sha256','semantic_digest'}}
    assert cert['semantic_digest']==hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return stats

def repair(x):
    core={k:v for k,v in x.items() if k not in {'raw_sha256','semantic_digest'}}; x['semantic_digest']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest(); return x
def tamper(cert,max_n,max_mult):
    attacks=[]
    def add(f):
        x=json.loads(json.dumps(cert)); f(x); attacks.append(repair(x))
    add(lambda x:x['pathwidth_formula'].__setitem__('a=1,b=1','max(p,q)'))
    add(lambda x:x['pathwidth_formula'].__setitem__('a>=2,b=1','max(p,q)'))
    add(lambda x:x['pathwidth_formula'].__setitem__('a=1,b>=2','max(p,q)'))
    add(lambda x:x['pathwidth_formula'].__setitem__('a>=2,b>=2','r'))
    add(lambda x:x['fixed_order_formula'].__setitem__('mixed_both_cut','max(p,q)'))
    add(lambda x:x['fixed_order_formula'].__setitem__('predicate','always false'))
    add(lambda x:x.__setitem__('field','GF(3)'))
    add(lambda x:x.__setitem__('theorem_id','A0_P_VS_NP'))
    add(lambda x:x.__setitem__('target_layout_enumeration_used_as_symbolic_premise',True))
    add(lambda x:x.__setitem__('world_novel_theorem_claim','NEW_RESULT'))
    add(lambda x:x.__setitem__('p_vs_np','P_EQUALS_NP'))
    add(lambda x:x['exhaustive_controls'].__setitem__('fixed_order_counterexamples',1))
    add(lambda x:x['exhaustive_controls'].__setitem__('pathwidth_counterexamples',1))
    add(lambda x:x['exhaustive_controls'].__setitem__('class_pattern_layouts',x['exhaustive_controls']['class_pattern_layouts']+1))
    add(lambda x:x['symbolic_derivation'].__setitem__('U_lower_bound','deleted'))
    add(lambda x:x['symbolic_derivation'].__setitem__('W_lower_bound','deleted'))
    add(lambda x:x['symbolic_derivation'].__setitem__('mixed_both_characterization','deleted'))
    add(lambda x:x['symbolic_derivation'].__setitem__('grouped_order_characterization','deleted'))
    rejected=0
    for x in attacks:
        try:verify(x,max_n,max_mult)
        except Exception:rejected+=1
    assert rejected==len(attacks),(rejected,len(attacks)); return rejected,len(attacks)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--certificate',required=True); ap.add_argument('--max-n',type=int,default=4); ap.add_argument('--max-mult',type=int,default=3); ap.add_argument('--tamper-test',action='store_true'); a=ap.parse_args()
    cert=json.load(open(a.certificate)); st=verify(cert,a.max_n,a.max_mult)
    print('A3_TWO_CLASS_INDEPENDENT_REPLAY = PASS'); print('A3_TWO_CLASS_FIXED_ORDER_FORMULA = PASS')
    for k in ('subspace_pairs','multiplicity_cases','class_pattern_layouts','cut_evaluations','mixed_both_orders'):print(k.upper()+'_RECOMPUTED =',st[k])
    print('FIXED_ORDER_COUNTEREXAMPLES = 0'); print('PATHWIDTH_COUNTEREXAMPLES = 0')
    if a.tamper_test:
        r,t=tamper(cert,a.max_n,a.max_mult); print(f'DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}')
    print('WORLD_NOVEL_THEOREM_CLAIM = FORBIDDEN_PENDING_AUDIT'); print('P_VS_NP = OPEN')
if __name__=='__main__':main()
