from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json, math
from pathlib import Path

SCHEMA='janus.c049_1.corrected_root_full_refinement_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_root_full_refinement_spec.v1'
UPK_SCHEMA='janus.c049_1.corrected_node9_residual_up_k_candidate.v1'
SPEC_BLOB='401c4856de261f6048d313ca62fa43598ea449e0'
PRODUCER_BLOB='e4378ee30743a43a0884237b3a51a6930542373a'
UPK_SHA='33aa00a538818b90ccaa0506071d579cf02ca49177b7875833c9625356ffc27f'
UPK_SEM='24de29ece76fe7aa2243c8227619ac74ff587f12ff8b199fb700cc6f29775c36'
PATTERNS=((0,),(0,1),(0,1,0),(1,),(1,0),(1,0,1)); K=1; TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
class VError(AssertionError):
    def __init__(self,inv,msg): super().__init__(f'{inv}: {msg}'); self.inv=inv
def req(ok,inv,msg):
    if not ok: raise VError(inv,msg)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sem_ok(a): return a.get('semantic_digest_scope')=='proof_payload' and dg(a.get('proof_payload'))==a.get('semantic_digest')
def enc(g): return [{'left':list(a),'right':list(b),'value':int(v)} for a,b,v in g]
def dec(raw): return tuple((tuple(map(int,x['left'])),tuple(map(int,x['right'])),int(x['value'])) for x in raw)
def trid(prefix,g): return prefix+'-'+dg(enc(g))[:24]
def plus(a,b): return (1,) if a or b else ()
def inter(a,b): return (1,) if a and b else ()
def dim(a): return len(a)
def contains(big,small): return not small or big==(1,)
def interval(g,i,j):
    if j-i<=1 or (g[i][0],g[i][1])!=(g[j][0],g[j][1]): return False
    a,b=g[i][2],g[j][2]; xs=[x[2] for x in g[i+1:j]]
    return (a<=b and all(a<=x<=b for x in xs)) or (a>=b and all(a>=x>=b for x in xs))
def compact(g):
    s=list(g); trace=[]
    while True:
        changed=False
        for i in range(1,len(s)):
            if s[i-1]==s[i]:
                before=len(s); rem=s[i]; del s[i]; trace.append({'rule':'duplicate','start':i-1,'end':i,'before_length':before,'after_length':len(s),'removed':enc((rem,))}); changed=True; break
        if changed: continue
        hit=None
        for i in range(len(s)):
            for j in range(i+2,len(s)):
                if interval(s,i,j): hit=(i,j); break
            if hit: break
        if hit:
            i,j=hit; before=len(s); rem=tuple(s[i+1:j]); del s[i+1:j]; trace.append({'rule':'interval','start':i,'end':j,'before_length':before,'after_length':len(s),'removed':enc(rem)}); continue
        return tuple(s),trace
def valid(g): return bool(g) and g[0][1]==g[-1][0] and all(contains(b[0],a[0]) and contains(a[1],b[1]) for a,b in zip(g,g[1:]))
def leaf_catalog():
    out=[]
    for p in PATTERNS:
        for q in PATTERNS:
            g=tuple([((),(1,),v) for v in p]+[((1,),(),v) for v in q]); req(valid(g) and compact(g)[0]==g,'INV02','leaf normal form')
            out.append({'leaf_id':trid('RL6',g),'source_patterns':[list(p),list(q)],'trajectory':enc(g),'trajectory_digest':dg(enc(g))})
    return sorted(out,key=lambda x:x['leaf_id'])
def combination_paths(m,n):
    h=m-1; v=n-1; total=h+v
    for hp in itertools.combinations(range(total),h):
        hs=set(hp); i=j=0; path=[(0,0)]; steps=[]
        for t in range(total):
            if t in hs: i+=1; steps.append('H')
            else: j+=1; steps.append('V')
            path.append((i,j))
        yield tuple(path),''.join(steps)
def join(g1,g2,path):
    init=inter(g1[0][1],g2[0][1]); raw=[]; corr=[]
    for i,j in path:
        a,b=g1[i],g2[j]; ar=plus(a[0],a[1]); br=plus(b[0],b[1]); c=dim(init)-dim(inter(ar,br)); req(c>=0,'INV04','negative correction'); raw.append((plus(a[0],b[0]),plus(a[1],b[1]),a[2]+b[2]+c)); corr.append(c)
    comp,tr=compact(tuple(raw)); req(valid(comp),'INV04','invalid compact join'); return tuple(raw),tuple(corr),comp,tr
def shrink(g):
    pre=[]; corr=[]
    for l,r,v in g:
        c=dim(inter(l,r)); pre.append(((),(),v+c)); corr.append(c)
    final,tr=compact(tuple(pre)); req(valid(final),'INV05','invalid shrink'); return tuple(pre),tuple(corr),final,tr
def reference(upk):
    left=[]
    for e in upk['proof_payload']['closure']['retained_generator_entries']:
        g=dec(e['trajectory']); req(valid(g) and compact(g)[0]==g and max(x[2] for x in g)<=K,'INV01','bad left full set entry'); left.append({'trajectory_id':e['trajectory_id'],'trajectory':e['trajectory'],'trajectory_digest':dg(e['trajectory'])})
    left=sorted(left,key=lambda x:x['trajectory_id']); right=leaf_catalog(); pairs=[]; refs=[]; suc=[]; fail=[]
    for lrow in left:
        g1=dec(lrow['trajectory'])
        for rrow in right:
            g2=dec(rrow['trajectory']); pid='PAIR-'+dg([lrow['trajectory_id'],rrow['leaf_id']])[:24]; ids=[]; count=0
            for path,steps in combination_paths(len(g1),len(g2)):
                count+=1; raw,jc,jcomp,jtr=join(g1,g2,path); pre,sc,final,strc=shrink(jcomp); w=max(x[2] for x in final); cls='SUCCESS' if w<=K else 'FAILED'; prov={'pair_id':pid,'left_trajectory_id':lrow['trajectory_id'],'right_leaf_id':rrow['leaf_id'],'path':[[i,j] for i,j in path],'steps':steps}; rid='REF-'+dg(prov)[:24]
                rec={'refinement_id':rid,'pair_id':pid,'left_trajectory_id':lrow['trajectory_id'],'right_leaf_id':rrow['leaf_id'],'ordinary_hv_path':[[i,j] for i,j in path],'ordinary_hv_steps':steps,'join_raw':enc(raw),'join_correction_vector':list(jc),'join_compact':enc(jcomp),'join_compactification_trace':jtr,'shrink_precompact':enc(pre),'shrink_correction_vector':list(sc),'final_compact':enc(final),'final_compact_digest':dg(enc(final)),'final_width':w,'classification':cls}; rec['record_digest']=dg(rec); refs.append(rec); ids.append(rid); (suc if cls=='SUCCESS' else fail).append(rid)
            req(count==math.comb(len(g1)+len(g2)-2,len(g1)-1),'INV03','H/V count formula')
            pairs.append({'pair_id':pid,'left_trajectory_id':lrow['trajectory_id'],'right_leaf_id':rrow['leaf_id'],'left_length':len(g1),'right_length':len(g2),'ordinary_hv_refinement_count':count,'refinement_ids_digest':dg(sorted(ids))})
    pairs.sort(key=lambda x:x['pair_id']); refs.sort(key=lambda x:x['refinement_id']); suc.sort(); fail.sort(); outs={}
    for r in refs:
        if r['classification']=='SUCCESS': outs.setdefault(r['final_compact_digest'],r['final_compact'])
    outputs=[{'trajectory_digest':k,'trajectory':outs[k]} for k in sorted(outs)]
    return {'left':left,'right':right,'pairs':pairs,'refs':refs,'suc':suc,'fail':fail,'outputs':outputs}
def source_bind(specp,producer,upkp):
    req(gb(specp)==SPEC_BLOB,'INV01','spec blob'); s=load(specp); req(s.get('schema')==SPEC_SCHEMA and s.get('status')=='SPEC_FROZEN','INV01','spec')
    e=s['expected_values_policy']; req(all(e[k] is None for k in ('expected_child_pairs','expected_ordinary_hv_refinements','expected_successful_refinements','expected_failed_refinements','expected_final_compact_outputs')),'INV01','oracle in spec')
    req(gb(producer)==PRODUCER_BLOB,'INV12','producer blob'); tree=ast.parse(Path(producer).read_text()); mods=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): mods.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
    req(not any('corrected_root_full_refinement_verifier' in m for m in mods),'INV12','producer imports verifier')
    u=load(upkp); req(fh(upkp)==UPK_SHA and u.get('schema')==UPK_SCHEMA and sem_ok(u) and u.get('semantic_digest')==UPK_SEM,'INV01','upk binding'); return s,u
def verify(c,spec,ref):
    req(c.get('schema')==SCHEMA and sem_ok(c),'INV01','candidate semantic'); p=c['proof_payload']; req(p['candidate_phase']=='CORRECTED_ROOT_FULL_REFINEMENT' and p['admitted'] is False,'INV12','phase/admit')
    req(p['source_binding']=={'up_k_sha256':UPK_SHA,'up_k_semantic_digest':UPK_SEM},'INV01','source receipt'); req(p['ordinary_join_domain']=={'steps':[[1,0],[0,1]],'diagonal_allowed':False},'INV09','ordinary domain')
    req(p['left_full_set']['entries']==ref['left'] and p['left_full_set']['entry_count']==len(ref['left']) and p['left_full_set']['catalog_digest']==dg(ref['left']) and p['left_full_set']['expected_count_used'] is False,'INV01','left set')
    req(p['right_leaf']['entries']==ref['right'] and p['right_leaf']['entry_count']==len(ref['right']) and p['right_leaf']['catalog_digest']==dg(ref['right']) and p['right_leaf']['expected_count_used'] is False,'INV02','right leaf')
    req(p['child_pairs']['records']==ref['pairs'] and p['child_pairs']['pair_count']==len(ref['pairs']) and p['child_pairs']['catalog_digest']==dg(ref['pairs']),'INV03','pair set')
    records=p['refinements']['records']; req(records==sorted(records,key=lambda x:x['refinement_id']),'INV10','refinement order'); req(records==ref['refs'],'INV07','complete refinement replay')
    for r in records:
        req(r['record_digest']==dg({k:v for k,v in r.items() if k!='record_digest'}),'INV07','record digest'); req(set(r['ordinary_hv_steps'])<=set('HV'),'INV09','diagonal')
    rr=p['refinements']; req(rr['ordinary_hv_refinement_count']==len(ref['refs']) and rr['successful_refinement_count']==len(ref['suc']) and rr['failed_refinement_count']==len(ref['fail']) and rr['successful_refinement_ids_digest']==dg(ref['suc']) and rr['failed_refinement_ids_digest']==dg(ref['fail']) and rr['catalog_digest']==dg(ref['refs']) and rr['expected_counts_used'] is False,'INV06','classification receipts')
    req(p['successful_generator_frontier']['outputs']==ref['outputs'] and p['successful_generator_frontier']['distinct_output_count']==len(ref['outputs']) and p['successful_generator_frontier']['catalog_digest']==dg(ref['outputs']) and p['successful_generator_frontier']['expected_count_used'] is False,'INV06','success frontier')
    l=p['conservation_ledger']; req(l['child_pairs']==len(ref['pairs']) and l['ordinary_hv_refinements']==len(ref['refs']) and l['analytic_hv_refinements']==len(ref['refs']) and l['successful_refinements']==len(ref['suc']) and l['failed_refinements']==len(ref['fail']) and l['omitted_child_pairs']==0 and l['duplicated_child_pairs']==0 and l['omitted_refinements']==0 and l['duplicated_refinements']==0 and l['ordinary_diagonal_steps']==0 and l['all_failed_records_materialized'] is True,'INV08','conservation')
    d=p['determinism']; req(d['required_order_modes']==['ORIGINAL','REVERSED','SEEDED_SHUFFLE'] and d['byte_identical_output_required'] is True and d['canonical_pair_order'] is True and d['canonical_refinement_order'] is True,'INV10','determinism')
    expected={'node9_parent_up_k_complete':True,'node9_integrated_into_bottom_up_executor':False,'root_reached':False,'root_parent_refinement_complete':False,'root_parent_up_k_complete':False,'root_full_set_computed':False,'root_empty_proved':False,'repository_failed_domains':0,'repository_successful_domains':0,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}; req(p['strict_boundary']==expected,'INV12','boundary'); return True
def repair(x):
    p=x['proof_payload']; p['left_full_set']['catalog_digest']=dg(p['left_full_set']['entries']); p['left_full_set']['entry_count']=len(p['left_full_set']['entries']); p['right_leaf']['catalog_digest']=dg(p['right_leaf']['entries']); p['right_leaf']['entry_count']=len(p['right_leaf']['entries']); p['child_pairs']['catalog_digest']=dg(p['child_pairs']['records']); p['child_pairs']['pair_count']=len(p['child_pairs']['records']); r=p['refinements']; r['catalog_digest']=dg(r['records']); r['ordinary_hv_refinement_count']=len(r['records']); r['successful_refinement_count']=sum(x['classification']=='SUCCESS' for x in r['records']); r['failed_refinement_count']=sum(x['classification']=='FAILED' for x in r['records']); r['successful_refinement_ids_digest']=dg(sorted(x['refinement_id'] for x in r['records'] if x['classification']=='SUCCESS')); r['failed_refinement_ids_digest']=dg(sorted(x['refinement_id'] for x in r['records'] if x['classification']=='FAILED')); p['successful_generator_frontier']['catalog_digest']=dg(p['successful_generator_frontier']['outputs']); p['successful_generator_frontier']['distinct_output_count']=len(p['successful_generator_frontier']['outputs']); x['semantic_digest']=dg(p)
def tampers(candidate,spec,ref):
    passed=[]
    def atk(name,mut):
        x=copy.deepcopy(candidate); mut(x); repair(x)
        try: verify(x,spec,ref)
        except VError as e: passed.append((name,e.inv)); return
        raise AssertionError('tamper survived '+name)
    atk('T01_UPK_BINDING',lambda x:x['proof_payload']['source_binding'].__setitem__('up_k_sha256','0'*64))
    atk('T02_RIGHT_LEAF',lambda x:x['proof_payload']['right_leaf']['entries'][0]['trajectory'][0].__setitem__('value',1-x['proof_payload']['right_leaf']['entries'][0]['trajectory'][0]['value']))
    atk('T03_DELETE_PAIR',lambda x:x['proof_payload']['child_pairs']['records'].pop())
    atk('T04_DELETE_REFINEMENT',lambda x:x['proof_payload']['refinements']['records'].pop())
    atk('T05_DIAGONAL',lambda x:x['proof_payload']['refinements']['records'][0].__setitem__('ordinary_hv_steps','D'+x['proof_payload']['refinements']['records'][0]['ordinary_hv_steps'][1:]))
    def t06(x):
        r=x['proof_payload']['refinements']['records'][0]; r['join_correction_vector'][0]+=1; r['record_digest']=dg({k:v for k,v in r.items() if k!='record_digest'})
    atk('T06_JOIN_CORRECTION',t06)
    def t07(x):
        r=x['proof_payload']['refinements']['records'][0]; r['shrink_correction_vector'][0]+=1; r['record_digest']=dg({k:v for k,v in r.items() if k!='record_digest'})
    atk('T07_SHRINK_CORRECTION',t07)
    def t08(x):
        r=x['proof_payload']['refinements']['records'][0]; r['final_width']+=1; r['record_digest']=dg({k:v for k,v in r.items() if k!='record_digest'})
    atk('T08_FINAL_WIDTH',t08)
    def t09(x):
        r=x['proof_payload']['refinements']['records'][0]; r['classification']='SUCCESS' if r['classification']=='FAILED' else 'FAILED'; r['record_digest']=dg({k:v for k,v in r.items() if k!='record_digest'})
    atk('T09_CLASSIFICATION',t09)
    atk('T10_CONSERVATION',lambda x:x['proof_payload']['conservation_ledger'].__setitem__('omitted_refinements',1))
    atk('T11_ORDER',lambda x:x['proof_payload']['refinements']['records'].reverse())
    atk('T12_BOUNDARY',lambda x:x['proof_payload']['strict_boundary'].__setitem__('root_empty_proved',True))
    req(len(passed)==12,'INV11','tamper count'); return passed
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--producer-source',type=Path,required=True); ap.add_argument('--up-k-artifact',type=Path,required=True); ap.add_argument('--candidate-original',type=Path,required=True); ap.add_argument('--candidate-reversed',type=Path,required=True); ap.add_argument('--candidate-seeded-shuffle',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args(); spec,upk=source_bind(a.spec,a.producer_source,a.up_k_artifact); b=a.candidate_original.read_bytes(); req(b==a.candidate_reversed.read_bytes()==a.candidate_seeded_shuffle.read_bytes(),'INV10','three mode bytes'); ref=reference(upk); c=load(a.candidate_original); verify(c,spec,ref); ts=tampers(c,spec,ref) if a.tamper_suite else []
    print('JANUS_CORRECTED_ROOT_FULL_REFINEMENT_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED'); print('MATHEMATICAL_INDEPENDENCE = NOT_AUTOMATIC'); print('SPECIFICATION_INDEPENDENCE = NOT_AUTOMATIC'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN'); print('LEFT_FULL_SET_ENTRIES =',len(ref['left'])); print('RIGHT_LEAF_ENTRIES =',len(ref['right'])); print('CHILD_PAIRS =',len(ref['pairs'])); print('ORDINARY_HV_REFINEMENTS =',len(ref['refs'])); print('SUCCESSFUL_REFINEMENTS =',len(ref['suc'])); print('FAILED_REFINEMENTS =',len(ref['fail'])); print('DISTINCT_SUCCESS_OUTPUTS =',len(ref['outputs'])); print('CANDIDATE_ARTIFACT_SHA256 =',fh(a.candidate_original)); print('CANDIDATE_SEMANTIC_DIGEST =',c['semantic_digest']); print('ROOT_PARENT_REFINEMENT_COMPLETE = FALSE'); print('ROOT_EMPTY_PROVED = FALSE'); print('FORMAL_ADMISSION = BLOCKED'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
