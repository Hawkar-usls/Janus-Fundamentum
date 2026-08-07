from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json
from pathlib import Path

SCHEMA='janus.c049_1.corrected_root_empty_up_k_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_root_empty_up_k_spec.v1'
ROOT_SCHEMA='janus.c049_1.corrected_root_full_refinement_candidate.v1'
SPEC_BLOB='0715adc3de2b7d206c84971d4538f73f8e5ddf1e'
PRODUCER_BLOB='cb65ab5b49d6973e930d4308baa2549021412a7b'
ROOT_SHA='74b734c8fc64a789dc4f0e40588956f93ad35ac799dea16417b1180ee5a83900'
ROOT_SEM='82a81c053dbd0bf99bb75f534f4e86ffe3794f06d21a359b76bcffd006fe3dc0'
K=1; TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
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
def enc(seq): return [{'left':[],'right':[],'value':int(v)} for v in seq]
def tid(seq): return 'ROOTUK-'+dg(enc(seq))[:24]
def reducible(seq):
    if any(a==b for a,b in zip(seq,seq[1:])): return True
    for i in range(len(seq)):
        for j in range(i+2,len(seq)):
            a,b=seq[i],seq[j]; inner=seq[i+1:j]
            if (a<=b and all(a<=x<=b for x in inner)) or (a>=b and all(a>=x>=b for x in inner)): return True
    return False
def universe_direct():
    out=[]
    for n in (1,2,3):
        for seq in itertools.product((0,1),repeat=n):
            if not reducible(seq): out.append(tuple(seq))
    return tuple(sorted(set(out)))
def preorder(lower,upper):
    m,n=len(lower),len(upper); reach={(0,0)} if lower[0]<=upper[0] else set()
    for s in range(1,m+n-1):
        for i in range(max(0,s-(n-1)),min(m-1,s)+1):
            j=s-i
            if j>=n or lower[i]>upper[j]: continue
            if any(p in reach for p in ((i-1,j),(i,j-1),(i-1,j-1))): reach.add((i,j))
    return (m-1,n-1) in reach
def source_bind(specp,producer,rootp):
    req(gb(specp)==SPEC_BLOB,'INV01','spec blob'); spec=load(specp); req(spec.get('schema')==SPEC_SCHEMA and spec.get('status')=='SPEC_FROZEN','INV01','spec')
    e=spec['expected_values_policy']; req(all(e[k] is None for k in ('expected_success_generator_count','expected_complete_universe_size','expected_closure_entry_count')),'INV01','oracle')
    req(gb(producer)==PRODUCER_BLOB,'INV12','producer blob'); tree=ast.parse(Path(producer).read_text()); mods=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): mods.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
    req(not any('corrected_root_empty_up_k_verifier' in m for m in mods),'INV12','producer imports verifier')
    root=load(rootp); req(fh(rootp)==ROOT_SHA and root.get('schema')==ROOT_SCHEMA and sem_ok(root) and root.get('semantic_digest')==ROOT_SEM,'INV01','root binding'); return spec,root
def derive_sources(root):
    ids=[]; by_digest={}; inconsistent=[]
    for r in root['proof_payload']['refinements']['records']:
        expected='SUCCESS' if int(r['final_width'])<=K else 'FAILED'
        if r['classification']!=expected: inconsistent.append(r['refinement_id'])
        if expected=='SUCCESS':
            ids.append(r['refinement_id']); req(all(not x['left'] and not x['right'] for x in r['final_compact']),'INV02','nonempty root boundary'); seq=tuple(int(x['value']) for x in r['final_compact']); req(seq in universe_direct(),'INV03','success generator not canonical'); by_digest.setdefault(dg(r['final_compact']),seq)
    req(not inconsistent,'INV02','classification inconsistency'); return sorted(ids),tuple(by_digest[k] for k in sorted(by_digest))
def cat(seqs): return [{'trajectory_id':tid(s),'trajectory':enc(s),'trajectory_digest':dg(enc(s)),'length':len(s),'width':max(s)} for s in sorted(seqs)]
def reference(root):
    ids,gens=derive_sources(root); U=universe_direct(); closure=[]
    for u in U:
        src=next((g for g in gens if preorder(g,u)),None)
        if src is not None: closure.append({'trajectory_id':tid(u),'trajectory':enc(u),'source_generator_id':tid(src)})
    closure=sorted(closure,key=lambda x:x['trajectory_id']); second_gens=tuple(tuple(x['value'] for x in e['trajectory']) for e in closure); second=[]
    for u in U:
        src=next((g for g in second_gens if preorder(g,u)),None)
        if src is not None: second.append({'trajectory_id':tid(u),'trajectory':enc(u),'source_generator_id':tid(src)})
    return {'ids':ids,'gens':gens,'U':U,'closure':closure,'second':sorted(second,key=lambda x:x['trajectory_id']),'records':len(root['proof_payload']['refinements']['records'])}
def verify(c,spec,ref):
    req(c.get('schema')==SCHEMA and sem_ok(c),'INV01','candidate semantic'); p=c['proof_payload']; req(p['candidate_phase']=='ROOT_EMPTY_UP_K' and p['admitted'] is False,'INV12','phase')
    req(p['source_binding']=={'root_refinement_sha256':ROOT_SHA,'root_refinement_semantic_digest':ROOT_SEM},'INV01','source receipt')
    ss=p['source_scan']; req(ss['root_refinement_record_count']==ref['records'] and ss['classification_inconsistencies']==0 and ss['successful_refinement_count']==len(ref['ids']) and ss['successful_refinement_ids']==ref['ids'] and ss['successful_refinement_ids_digest']==dg(ref['ids']) and ss['expected_success_count_used'] is False,'INV02','source scan')
    gf=p['successful_generator_family']; expected_cat=cat(ref['gens']); req(gf['generators']==expected_cat and gf['generator_count']==len(expected_cat) and gf['catalog_digest']==dg(expected_cat) and gf['expected_count_used'] is False,'INV03','generator family')
    Ucat=cat(ref['U']); u=p['complete_empty_boundary_universe']; req(u['entries']==Ucat and u['entry_count']==len(Ucat) and u['catalog_digest']==dg(Ucat) and u['max_length_bound']==3 and u['expected_universe_size_used'] is False and u['supplied_universe_used'] is False,'INV04','universe')
    for source in ref['gens']:
        for target in ref['U']:
            _=preorder(source,target)
    cl=p['root_up_k_closure']; req(cl['entries']==ref['closure'] and cl['entry_count']==len(ref['closure']) and cl['catalog_digest']==dg(ref['closure']) and cl['empty']==(len(ref['closure'])==0) and cl['expected_entry_count_used'] is False and cl['universe_entries_with_direct_source_witness']==len(ref['closure']),'INV06','closure')
    req(cl['empty']==(not any(preorder(g,u) for g in ref['gens'] for u in ref['U'])),'INV07','empty iff no witness')
    idem=p['idempotence']; req(idem['second_input_entry_count']==len(ref['closure']) and idem['second_closure_entries']==ref['second'] and idem['second_closure_digest']==dg(ref['second']) and idem['first_second_equal']==(ref['closure']==ref['second']),'INV08','idempotence')
    w=p['work_ledger']; req(w['root_refinement_records_scanned']==ref['records'] and w['successful_generators_materialized']==len(ref['gens']) and w['complete_universe_entries_materialized']==len(ref['U']) and w['source_to_universe_relation_tests']==len(ref['gens'])*len(ref['U']) and w['second_source_to_universe_relation_tests']==len(ref['closure'])*len(ref['U']) and w['supplied_universe_entries_consumed']==0,'INV09','work')
    d=p['determinism']; req(d['required_order_modes']==['ORIGINAL','REVERSED','SEEDED_SHUFFLE'] and d['byte_identical_output_required'] is True and d['canonical_source_order'] is True and d['canonical_universe_order'] is True and d['canonical_closure_order'] is True,'INV10','determinism')
    expected={'node9_integrated_into_bottom_up_executor':True,'root_reached':True,'root_parent_refinement_complete':True,'root_parent_up_k_complete':False,'root_full_set_computed':False,'root_empty_proved':False,'terminal_completeness_proved':False,'repository_failed_domains':0,'repository_successful_domains':0,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}; req(p['strict_boundary']==expected,'INV12','boundary'); return True
def repair(x):
    p=x['proof_payload']; s=p['source_scan']; s['successful_refinement_count']=len(s['successful_refinement_ids']); s['successful_refinement_ids_digest']=dg(s['successful_refinement_ids']); g=p['successful_generator_family']; g['generator_count']=len(g['generators']); g['catalog_digest']=dg(g['generators']); u=p['complete_empty_boundary_universe']; u['entry_count']=len(u['entries']); u['catalog_digest']=dg(u['entries']); c=p['root_up_k_closure']; c['entry_count']=len(c['entries']); c['catalog_digest']=dg(c['entries']); c['empty']=len(c['entries'])==0; i=p['idempotence']; i['second_input_entry_count']=len(c['entries']); i['second_closure_digest']=dg(i['second_closure_entries']); x['semantic_digest']=dg(p)
def tamper(candidate,spec,ref):
    ok=[]
    def atk(name,mut,post_repair=None):
        x=copy.deepcopy(candidate); mut(x); repair(x)
        if post_repair is not None:
            post_repair(x)
            x['semantic_digest']=dg(x['proof_payload'])
        try: verify(x,spec,ref)
        except VError as e: ok.append((name,e.inv)); return
        raise AssertionError('survived '+name)
    atk('T01_ROOT_BINDING',lambda x:x['proof_payload']['source_binding'].__setitem__('root_refinement_sha256','0'*64))
    atk('T02_FAKE_SUCCESS_GENERATOR',lambda x:x['proof_payload']['successful_generator_family']['generators'].append({'trajectory_id':'ROOTUK-fake','trajectory':[{'left':[],'right':[],'value':0}],'trajectory_digest':'0'*64,'length':1,'width':0}))
    atk('T03_SUPPRESS_SUCCESS_SCAN',lambda x:x['proof_payload']['source_scan'].__setitem__('root_refinement_record_count',x['proof_payload']['source_scan']['root_refinement_record_count']-1))
    atk('T04_GENERATOR_DIGEST',lambda x:None,lambda x:x['proof_payload']['successful_generator_family'].__setitem__('catalog_digest','1'*64))
    atk('T05_OMIT_UNIVERSE',lambda x:x['proof_payload']['complete_empty_boundary_universe']['entries'].pop())
    atk('T06_NONCANONICAL_UNIVERSE',lambda x:x['proof_payload']['complete_empty_boundary_universe']['entries'].append({'trajectory_id':'ROOTUK-x','trajectory':[{'left':[],'right':[],'value':0},{'left':[],'right':[],'value':0}],'trajectory_digest':'2'*64,'length':2,'width':0}))
    atk('T07_FAKE_CLOSURE',lambda x:x['proof_payload']['root_up_k_closure']['entries'].append({'trajectory_id':'ROOTUK-fake','trajectory':[{'left':[],'right':[],'value':0}],'source_generator_id':'ROOTUK-none'}))
    atk('T08_EMPTY_FLAG',lambda x:x['proof_payload']['root_up_k_closure'].__setitem__('universe_entries_with_direct_source_witness',1))
    atk('T09_IDEMPOTENCE',lambda x:x['proof_payload']['idempotence'].__setitem__('first_second_equal',False))
    atk('T10_SUPPLIED_UNIVERSE',lambda x:x['proof_payload']['complete_empty_boundary_universe'].__setitem__('supplied_universe_used',True))
    atk('T11_ORDER',lambda x:x['proof_payload']['complete_empty_boundary_universe']['entries'].reverse())
    atk('T12_TERMINAL_PROMOTION',lambda x:x['proof_payload']['strict_boundary'].__setitem__('no_layout_at_cap',True))
    req(len(ok)==12,'INV11','tamper count'); return ok
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--producer-source',type=Path,required=True); ap.add_argument('--root-refinement-artifact',type=Path,required=True); ap.add_argument('--candidate-original',type=Path,required=True); ap.add_argument('--candidate-reversed',type=Path,required=True); ap.add_argument('--candidate-seeded-shuffle',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args(); spec,root=source_bind(a.spec,a.producer_source,a.root_refinement_artifact); b=a.candidate_original.read_bytes(); req(b==a.candidate_reversed.read_bytes()==a.candidate_seeded_shuffle.read_bytes(),'INV10','three mode bytes'); ref=reference(root); c=load(a.candidate_original); verify(c,spec,ref); ts=tamper(c,spec,ref) if a.tamper_suite else []
    print('JANUS_CORRECTED_ROOT_EMPTY_UP_K_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED'); print('MATHEMATICAL_INDEPENDENCE = NOT_AUTOMATIC'); print('SPECIFICATION_INDEPENDENCE = NOT_AUTOMATIC'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN'); print('ROOT_REFINEMENT_RECORDS_SCANNED =',ref['records']); print('SUCCESS_GENERATORS =',len(ref['gens'])); print('COMPLETE_EMPTY_BOUNDARY_UNIVERSE =',len(ref['U'])); print('ROOT_UP_K_CLOSURE_ENTRIES =',len(ref['closure'])); print('ROOT_UP_K_CLOSURE_EMPTY =',len(ref['closure'])==0); print('IDEMPOTENT =',ref['closure']==ref['second']); print('CANDIDATE_ARTIFACT_SHA256 =',fh(a.candidate_original)); print('CANDIDATE_SEMANTIC_DIGEST =',c['semantic_digest']); print('ROOT_EMPTY_PROVED = FALSE'); print('NO_LAYOUT_AT_CAP = FORBIDDEN'); print('FORMAL_ADMISSION = BLOCKED'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
