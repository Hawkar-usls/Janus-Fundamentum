from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import inspect,itertools,json,time
from research.tools.apma_ss_provenance.apma_ss_controller import encode_c023,run_apma_ss,direct_cardinality,checkpoint_hash


def eval_cnf(cnf,a):
    return all(any(bool(a[abs(l)])==(l>0) for l in c) for c in cnf)


def eval_image(image,a):
    n=image['n']; full={}
    for i in range(1,n+1):
        full[i]=bool(a[i]); full[n+i]=not bool(a[i])
    for c in image['horn']:
        if not any(bool(full[abs(l)])==(l>0) for l in c): return False
    for mask,rhs in image['affine']:
        s=0
        for v in range(1,2*n+1):
            if mask & (1<<(v-1)): s ^= int(full[v])
        if s != rhs: return False
    return True


def replay_small(source,n):
    image=encode_c023(source,n)
    for bits in itertools.product((False,True),repeat=n):
        a={i+1:bits[i] for i in range(n)}
        if eval_cnf(source,a) != eval_image(image,a): return False
    return True


def dense_positive(n): return tuple(tuple(c) for c in itertools.combinations(range(1,n+1),3))
def dense_negative(n): return tuple(tuple(-x for x in c) for c in itertools.combinations(range(1,n+1),3))


def main():
    t0=time.perf_counter(); checks={}
    # source/image semantic replay
    checks['replay_dense_positive']=[replay_small(dense_positive(n),n) for n in range(3,7)]
    checks['replay_dense_negative']=[replay_small(dense_negative(n),n) for n in range(3,7)]
    two=((1,2),(-1,3),(-2,-3)); checks['replay_2cnf']=replay_small(two,3)
    # tractable reverse escape
    pos=run_apma_ss(encode_c023(dense_positive(6),6)); neg=run_apma_ss(encode_c023(dense_negative(6),6)); t2=run_apma_ss(encode_c023(two,3))
    checks['positive_class']=pos['source_class']=='DUAL_HORN' and pos['status']=='CERTIFIED_SAT'
    checks['negative_class']=neg['source_class']=='HORN' and neg['status']=='CERTIFIED_SAT'
    checks['two_class']=t2['source_class']=='2CNF' and t2['status'] in {'CERTIFIED_SAT','CERTIFIED_UNSAT'}
    # general 3CNF remains open
    hard=((1,2,3),(-1,-2,-3)); h=run_apma_ss(encode_c023(hard,3)); checks['general_open']=h['status']=='OPEN_GENERAL_SOURCE_3CNF'
    # rollback killer: corrupt only reverse provenance schema
    img=encode_c023(dense_positive(7),7); direct=direct_cardinality(img); bad={**img,'provenance':dict(img['provenance'])}; bad['provenance']['schema']='CORRUPTED_SCHEMA'
    before=checkpoint_hash(bad); rb=run_apma_ss(bad)
    checks['rollback_hash_identity']=rb.get('rollback_hash')==before==rb.get('checkpoint_hash')
    checks['rollback_later_morph']=rb.get('terminal')=='CARDINALITY_CARRIER' and rb.get('carrier')==direct
    checks['failed_attempt_preserved']=rb['ledger'][0]['status']=='MORPH_FAIL_ROLLED_BACK' and len(rb['ledger'])==2
    # corrupt source hash must fail reverse and not forge tractable escape
    bad2=encode_c023(two,3); bad2={**bad2,'provenance':dict(bad2['provenance'])}; bad2['provenance']['source_cnf_sha256']='0'*64
    r2=run_apma_ss(bad2); checks['source_hash_corruption_not_promoted']=r2['ledger'][0]['status']=='MORPH_FAIL_ROLLED_BACK'
    # candidate guard
    import research.tools.apma_ss_provenance.apma_ss_controller as c
    text=inspect.getsource(c).lower(); forbidden=['random.','dpll','best_of','score_candidate','itertools.product']
    hits=[x for x in forbidden if x in text]; checks['captain_guard']=not hits
    ok=all(all(x) if isinstance(x,list) else bool(x) for x in checks.values())
    out={'schema':'JANUS_TRUMP_APMA_SS_PROVENANCE_ESCAPE_GATE_V1','verdict':'PASS_APMA_SS_PROVENANCE_ESCAPE_AND_ROLLBACK' if ok else 'FAIL_SEMANTIC_OR_ROLLBACK_MISMATCH','checks':checks,'captain_guard_hits':hits,'rollback_example':rb,'general_example':h,'runtime_ms':round((time.perf_counter()-t0)*1000,3),'scientific_status':{'SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0},'next':'apply APMA-SS to non-symmetric images and expand exact morph catalog only by preregistered child gates'}
    print(json.dumps(out,sort_keys=True))
    raise SystemExit(0 if ok else 1)

if __name__=='__main__': main()
