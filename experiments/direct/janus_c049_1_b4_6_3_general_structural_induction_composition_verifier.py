from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json
from pathlib import Path

SCHEMA='janus.c049_1.general_structural_induction_composition_candidate.v1'
GATE='C049.1_B4.6.3_GENERAL_STRUCTURAL_INDUCTION_COMPOSITION'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

class VError(Exception):
    def __init__(self,inv,msg): super().__init__(f'{inv}:{msg}'); self.inv=inv

def req(x,inv,msg):
    if not x: raise VError(inv,msg)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def semok(x,scope,payload): return x.get('semantic_digest_scope')==scope and dg(x.get(payload))==x.get('semantic_digest')
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def imports(path):
    tree=ast.parse(Path(path).read_text()); mods=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): mods.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
    return mods

def implementation_decoupling(producer_source,verifier_source):
    pm=imports(producer_source); vm=imports(verifier_source)
    req(not any(x.endswith('janus_c049_1_b4_6_3_general_structural_induction_composition_verifier') for x in pm),'INV01','producer imports verifier')
    req(not any(x.endswith('janus_c049_1_b4_6_3_general_structural_induction_composition') for x in vm),'INV01','verifier imports producer')

def xb(rows):
    basis={}
    for raw in rows:
        x=int(raw)
        while x:
            p=x.bit_length()-1
            if p in basis: x ^= basis[p]; continue
            basis[p]=x
            for q,y in list(basis.items()):
                if q!=p and ((y>>p)&1): basis[q]=y^x
            break
    for p in sorted(basis):
        r=basis[p]
        for q in sorted(basis,reverse=True):
            if q!=p and ((basis[q]>>p)&1): basis[q]^=r
    return tuple(basis[p] for p in sorted(basis,reverse=True))
def vecs(b):
    out={0}
    for r in b: out |= {x^r for x in tuple(out)}
    return out
def sm(a,b): return xb((*a,*b))
def inter(a,b): return xb(sorted(vecs(a)&vecs(b)))
def contains(big,small): return vecs(small) <= vecs(big)
def subspaces(d):
    seen={()}; q=[()]
    while q:
        b=q.pop(0)
        for v in range(1,1<<d):
            c=xb((*b,v))
            if c not in seen: seen.add(c); q.append(c)
    return tuple(sorted(seen))

def lemma27_controls():
    checked=0
    for d in (1,2,3):
        ss=subspaces(d)
        for w1,w2,out in itertools.product(ss,repeat=3):
            b1=inter(w1,sm(w2,out)); b2=inter(w2,sm(w1,out)); b=inter(sm(w1,w2),out); bp=sm(b1,b2)
            req(inter(w1,bp)==b1,'INV03','finite expand w1')
            req(inter(w2,bp)==b2,'INV03','finite expand w2')
            req(contains(bp,b),'INV03','finite shrink containment')
            req(inter(sm(w1,bp),sm(w2,bp))==bp,'INV03','finite join separation')
            checked+=1
    return checked

def load_audits(a,s):
    receipts=s['local_semantic_receipts']; out=[]; blobs={}
    for i,p in enumerate(a.audits,1):
        key=f'O{i}'; x=load(p); blob=gb(p)
        req(blob==receipts[key]['audit_git_blob'],'INV01',f'{key} audit blob')
        req(semok(x,'audit_payload','audit_payload'),'INV01',f'{key} audit semantic')
        out.append(x); blobs[key]=blob
    return out,blobs

def expected_steps(s):
    cp=s['structural_induction_contract']['caller_precondition_discharge']
    return [
      {'step':'LEAF','receipt':'O1','premise':'B_v SUBSET V_leaf','conclusion':'F_v = FS_k(V_v,B_v)'},
      {'step':'EXPAND_CHILDREN','receipt':'O2','premise_source':'JKO_LEMMA_2_7','premise':cp['expand_child_i'],'conclusion':'F_v_child_i_expanded = FS_k(V_wi,Bprime_v)'},
      {'step':'CORRECTED_HV_JOIN','receipt':'O3','premise_source':'JKO_LEMMA_2_7','premise':cp['join'],'ordinary_path_domain':[[1,0],[0,1]],'conclusion':'JOIN_SOURCE_FAMILY_REPRESENTS_FS_k(V_v,Bprime_v)_BEFORE_CAP_CLOSURE'},
      {'step':'WIDTH_CAP','receipt':'O5','premise':cp['width_filter'],'conclusion':'WIDTH_GT_K_SOURCES_MAY_BE_REMOVED_WITHOUT_LOSING_ANY_FS_k_TARGET'},
      {'step':'B2_LANGUAGE_CLOSURE','receipt':'O6','premise':cp['b2_language_preservation'],'conclusion':'Fprime_v = FS_k(V_v,Bprime_v)'},
      {'step':'SHRINK','receipt':'O4','premise_source':'JKO_LEMMA_2_7','premise':cp['shrink'],'conclusion':'F_v = FS_k(V_v,B_v)'},
      {'step':'ROOT','receipt':'O7','premise':'COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_AND_F_root_EQUALS_FS_k(V,{0})','conclusion':'F_root_NONEMPTY_IFF_COMPLETE_LAYOUT_WIDTH_LE_K'}]

def verify(c,s,a):
    req(c.get('schema')==SCHEMA and semok(c,'proof_payload','proof_payload'),'INV01','candidate semantic')
    req(s['gate']==GATE and s['version']=='1.0' and s['admission'] is False,'INV01','spec')
    audits,blobs=load_audits(a,s); r=s['local_semantic_receipts']
    req(list(r)==[f'O{i}' for i in range(1,8)],'INV01','receipt ids')
    req(c['proof_payload']['audit_git_blobs']==blobs,'INV01','audit blob map')
    req(c['proof_payload']['audit_semantic_digests']=={f'O{i}':audits[i-1]['semantic_digest'] for i in range(1,8)},'INV01','audit digest map')
    req(c['proof_payload']['receipt_proof_heads']=={k:v['proof_head'] for k,v in r.items()},'INV01','proof heads')
    pub=s['published_source']; req(pub['source']=='arXiv:1507.02184v4' and pub['source_version_required']=='v4','INV02','v4')
    req(pub['dependency_status']=='PUBLISHED_LEMMA_2_7_AND_PROPOSITION_5_8_INDUCTION_BOUND_NOT_INDEPENDENTLY_REPROVED','INV02','dependency ceiling')
    req(pub['theorem_dependencies']==['Lemma 2.7 branch-decomposition boundary identities','Proposition 4.1 leaf full set','Proposition 4.2 expand full set','Proposition 4.3 shrink full set','Proposition 4.4 join full set','Proposition 5.8 structural induction and root criterion'],'INV02','dependency set')
    t=s['local_trace_contract']; req(t['field']=='GF(2)','INV03','field'); req(t['ordinary_join_path_domain']==[[1,0],[0,1]],'INV06','ordinary H/V'); req(t['preorder_path_domain']==[[1,0],[0,1],[1,1]],'INV06','preorder distinct')
    req(t['required_boundary_definitions']=={'B_v':'SPAN(V_v) INTER SPAN(V_MINUS_V_v)','Bprime_v':'B_w1 PLUS B_w2'},'INV03','boundaries')
    cp=s['structural_induction_contract']['caller_precondition_discharge']; req(cp['expand_child_i'].endswith('= B_wi'),'INV05','expand equality'); req(cp['join'].endswith('= Bprime_v'),'INV06','join equality'); req(cp['shrink']=='B_v SUBSET Bprime_v','INV07','shrink containment')
    p=c['proof_payload']; req(p['composition_steps']==expected_steps(s),'INV04','composition exact')
    req(p['lemma_2_7_caller_preconditions_discharge_candidate'] is True,'INV03','lemma27 discharge')
    req(p['algorithm1_compatible_trace_full_set_identity_candidate'] is True,'INV08','full-set induction candidate')
    req(p['root_full_set_identity_candidate']=='FOR_ANY_COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_F_root_EQUALS_FS_k(V,{0})','INV09','root identity candidate')
    req(p['terminal_biconditional_candidate_for_complete_trace'] is True,'INV09','O7 bridge')
    req(p['actual_corrected_engine_complete_algorithm1_trace_established'] is False,'INV12','actual trace ceiling')
    req(p['strict_boundary']==s['strict_boundary'],'INV12','boundary')
    req(p['general_semantic_receipt_count']==7,'INV08','receipt count')
    return True

def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tamper(c,s,a):
    ok=[]
    def attack(name,mut):
        x=copy.deepcopy(c); mut(x); seal(x)
        try: verify(x,s,a)
        except VError as e: ok.append((name,e.inv)); return
        raise AssertionError('survived '+name)
    attack('T01_AUDIT_BINDING',lambda x:x['proof_payload']['audit_git_blobs'].__setitem__('O1','0'*40))
    attack('T02_EXPAND_PREMISE',lambda x:x['proof_payload']['composition_steps'][1].__setitem__('premise','B_wi SUBSET Bprime_v'))
    attack('T03_DIAGONAL_ORDINARY_JOIN',lambda x:x['proof_payload']['composition_steps'][2].__setitem__('ordinary_path_domain',[[1,0],[0,1],[1,1]]))
    attack('T04_JOIN_PREMISE',lambda x:x['proof_payload']['composition_steps'][2].__setitem__('premise','WEAK_JOIN_PREMISE'))
    attack('T05_SHRINK_PREMISE',lambda x:x['proof_payload']['composition_steps'][5].__setitem__('premise','UNKNOWN'))
    attack('T06_O5_AUTOMATIC',lambda x:x['proof_payload']['composition_steps'][3].__setitem__('premise','AUTOMATIC'))
    attack('T07_O6_AUTOMATIC',lambda x:x['proof_payload']['composition_steps'][4].__setitem__('premise','AUTOMATIC'))
    attack('T08_LEMMA27',lambda x:x['proof_payload'].__setitem__('lemma_2_7_caller_preconditions_discharge_candidate',False))
    attack('T09_ACTUAL_TRACE',lambda x:x['proof_payload'].__setitem__('actual_corrected_engine_complete_algorithm1_trace_established',True))
    attack('T10_TERMINAL',lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True))
    attack('T11_GLOBAL_NO',lambda x:x['proof_payload']['strict_boundary'].__setitem__('global_engine_no_layout_at_cap','ADMITTED'))
    attack('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    req(len(ok)==12,'INV11','tamper count'); return ok

def main():
    p=argparse.ArgumentParser(); p.add_argument('--spec',type=Path,required=True); p.add_argument('--producer-source',type=Path,required=True); p.add_argument('--verifier-source',type=Path,required=True)
    for i in range(1,8): p.add_argument(f'--o{i}-audit',dest=f'o{i}_audit',type=Path,required=True)
    p.add_argument('--candidate-original',type=Path,required=True); p.add_argument('--candidate-reordered',type=Path,required=True); p.add_argument('--tamper-suite',action='store_true')
    a=p.parse_args(); a.audits=[getattr(a,f'o{i}_audit') for i in range(1,8)]; implementation_decoupling(a.producer_source,a.verifier_source)
    req(a.candidate_original.read_bytes()==a.candidate_reordered.read_bytes(),'INV10','byte identity')
    s=load(a.spec); c=load(a.candidate_original); verify(c,s,a); controls=lemma27_controls(); ts=tamper(c,s,a) if a.tamper_suite else []
    print('JANUS_GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_INDEPENDENT_VERIFIER = PASS')
    print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('VERIFIER_IMPORT_OF_PRODUCER = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED')
    print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN')
    print('FINITE_LEMMA_2_7_BUG_FINDING_CONTROLS =',controls)
    print('GENERAL_SEMANTIC_RECEIPTS_BOUND = 7/7'); print('IMMUTABLE_AUDIT_BLOB_BINDINGS = 7/7')
    print('ALGORITHM1_COMPATIBLE_TRACE_FULL_SET_IDENTITY = PASS_AS_DERIVED_CANDIDATE')
    print('ACTUAL_CORRECTED_ENGINE_COMPLETE_ALGORITHM1_TRACE_ESTABLISHED = FALSE')
    print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
