#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math
from pathlib import Path


def span(vectors):
    s={0}
    for v in vectors:
        s |= {x ^ v for x in tuple(s)}
    return frozenset(s)


def all_subspaces(n):
    nonzero=list(range(1,1<<n)); out={frozenset({0})}
    for mask in range(1<<len(nonzero)):
        out.add(span(nonzero[i] for i in range(len(nonzero)) if (mask>>i)&1))
    return tuple(sorted(out,key=lambda s:(len(s),tuple(sorted(s)))))


def d(A): return len(A).bit_length()-1

def ssum(A,B): return frozenset(a^b for a in A for b in B)

def expected(a,b,p,q,r):
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


def width(P,U,W):
    return max(d(side(P[:i],U,W)&side(P[i:],U,W)) for i in range(len(P)+1))


def verify_certificate(cert,max_n=4,max_mult=3):
    assert cert['schema']=='janus.fundamentum.a3.two_class_repeated_subspace_pathwidth_theorem_certificate.v1'
    assert cert['theorem_id']=='A3_TWO_CLASS_REPEATED_SUBSPACE_PATHWIDTH_V1'
    assert cert['field']=='GF(2)'
    assert cert['formula']=={'a=1,b=1':'r','a>=2,b=1':'p','a=1,b>=2':'q','a>=2,b>=2':'max(p,q)'}
    assert cert['target_layout_enumeration_used_as_symbolic_premise'] is False
    assert cert['world_novel_theorem_claim']=='FORBIDDEN_PENDING_AUDIT'
    assert cert['p_vs_np']=='OPEN'
    stats={'subspace_pairs':0,'multiplicity_cases':0,'class_pattern_layouts':0,'cut_evaluations':0,'counterexamples':0}
    for n in range(max_n+1):
        subs=all_subspaces(n)
        for U in subs:
            for W in subs:
                p,q,r=d(U),d(W),d(U&W); stats['subspace_pairs']+=1
                assert 0<=r<=min(p,q)
                for a in range(1,max_mult+1):
                    for b in range(1,max_mult+1):
                        stats['multiplicity_cases']+=1
                        best=None
                        for P in patterns(a,b):
                            got=width(P,U,W)
                            stats['class_pattern_layouts']+=1
                            stats['cut_evaluations']+=len(P)+1
                            best=got if best is None else min(best,got)
                        exp=expected(a,b,p,q,r)
                        if best!=exp:
                            stats['counterexamples']+=1
                            raise AssertionError((n,p,q,r,a,b,best,exp))
    cstats=cert['exhaustive_controls']
    for k in ('subspace_pairs','multiplicity_cases','class_pattern_layouts','cut_evaluations','counterexamples'):
        assert cstats[k]==stats[k],(k,cstats[k],stats[k])
    core={k:v for k,v in cert.items() if k not in {'raw_sha256','semantic_digest'}}
    dig=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert cert['semantic_digest']==dig
    return stats


def repaired(obj):
    x=json.loads(json.dumps(obj)); core={k:v for k,v in x.items() if k not in {'raw_sha256','semantic_digest'}}
    x['semantic_digest']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest(); return x


def tamper_suite(cert,max_n,max_mult):
    attacks=[]
    def add(fn):
        x=json.loads(json.dumps(cert)); fn(x); attacks.append(repaired(x))
    add(lambda x:x['formula'].__setitem__('a=1,b=1','max(p,q)'))
    add(lambda x:x['formula'].__setitem__('a>=2,b=1','max(p,q)'))
    add(lambda x:x['formula'].__setitem__('a=1,b>=2','max(p,q)'))
    add(lambda x:x['formula'].__setitem__('a>=2,b>=2','r'))
    add(lambda x:x.__setitem__('field','GF(3)'))
    add(lambda x:x.__setitem__('theorem_id','A0_P_VS_NP'))
    add(lambda x:x.__setitem__('target_layout_enumeration_used_as_symbolic_premise',True))
    add(lambda x:x.__setitem__('world_novel_theorem_claim','NEW_RESULT'))
    add(lambda x:x.__setitem__('p_vs_np','P_EQUALS_NP'))
    add(lambda x:x['exhaustive_controls'].__setitem__('counterexamples',1))
    add(lambda x:x['exhaustive_controls'].__setitem__('subspace_pairs',x['exhaustive_controls']['subspace_pairs']+1))
    add(lambda x:x['exhaustive_controls'].__setitem__('multiplicity_cases',x['exhaustive_controls']['multiplicity_cases']-1))
    add(lambda x:x['exhaustive_controls'].__setitem__('class_pattern_layouts',x['exhaustive_controls']['class_pattern_layouts']+3))
    add(lambda x:x['symbolic_derivation'].__setitem__('U_lower_bound','deleted'))
    add(lambda x:x['symbolic_derivation'].__setitem__('W_lower_bound','deleted'))
    add(lambda x:x['symbolic_derivation'].__setitem__('inequality_used','r>=max(p,q)'))
    rejected=0
    for x in attacks:
        try: verify_certificate(x,max_n,max_mult)
        except Exception: rejected+=1
    assert rejected==len(attacks)
    return rejected,len(attacks)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--certificate',required=True); ap.add_argument('--max-n',type=int,default=4); ap.add_argument('--max-mult',type=int,default=3); ap.add_argument('--tamper-test',action='store_true'); a=ap.parse_args()
    cert=json.load(open(a.certificate,encoding='utf-8'))
    stats=verify_certificate(cert,a.max_n,a.max_mult)
    print('A3_TWO_CLASS_INDEPENDENT_REPLAY = PASS')
    print('SUBSPACE_PAIRS_RECOMPUTED =',stats['subspace_pairs'])
    print('MULTIPLICITY_CASES_RECOMPUTED =',stats['multiplicity_cases'])
    print('CLASS_PATTERN_LAYOUTS_RECOMPUTED =',stats['class_pattern_layouts'])
    print('CUT_EVALUATIONS_RECOMPUTED =',stats['cut_evaluations'])
    print('COUNTEREXAMPLES = 0')
    if a.tamper_test:
        r,t=tamper_suite(cert,a.max_n,a.max_mult); print(f'DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}')
    print('WORLD_NOVEL_THEOREM_CLAIM = FORBIDDEN_PENDING_AUDIT')
    print('P_VS_NP = OPEN')
if __name__=='__main__':main()
