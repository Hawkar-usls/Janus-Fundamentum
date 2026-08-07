from __future__ import annotations
import argparse, ast, copy, hashlib, json
from collections import defaultdict
from pathlib import Path

SCHEMA='janus.c049_1.corrected_node9_residual_up_k_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_node9_residual_up_k_spec.v1'
RESIDUAL_SCHEMA='janus.c049_1.corrected_node9_residual_compact_frontier_candidate.v1'
SPEC_BLOB='f661107212acdca4019dc2d038610e2cdd3beb40'
PRODUCER_BLOB='f7082ee031074e6548a49e17227c5c4b410c891d'
RESIDUAL_SHA='4d81196e48b75d0f138e97fc2c72ef8984581cb0bb42ea0fd187dcb881a0b62f'
RESIDUAL_SEM='d70faf0fb15023671b4c0441a2d5191ff2e144b0a10151d4c4308355a61cd64e'
D=1; K=1; TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
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
def tid(g): return 'UKT-'+dg(enc(g))[:24]
def span(big,small): return (not small) or big==(1,)
def interval(g,i,j):
    if j-i<=1 or (g[i][0],g[i][1])!=(g[j][0],g[j][1]): return False
    a,b=g[i][2],g[j][2]; q=[x[2] for x in g[i+1:j]]
    return (a<=b and all(a<=x<=b for x in q)) or (a>=b and all(a>=x>=b for x in q))
def compact_b1(g):
    s=list(g)
    if not s: raise ValueError('empty')
    while True:
        changed=False
        for i in range(1,len(s)):
            if s[i-1]==s[i]:
                del s[i]; changed=True; break
        if changed: continue
        hit=None
        for i in range(len(s)):
            for j in range(i+2,len(s)):
                if interval(s,i,j): hit=(i,j); break
            if hit: break
        if hit:
            i,j=hit; del s[i+1:j]; continue
        return tuple(s)
def compact_alt(g):
    s=list(g)
    if not s: raise ValueError('empty')
    while True:
        hit=None
        for i in range(len(s)-1,-1,-1):
            for j in range(len(s)-1,i+1,-1):
                if interval(s,i,j): hit=(i,j); break
            if hit: break
        if hit:
            i,j=hit; del s[i+1:j]; continue
        for i in range(len(s)-1,0,-1):
            if s[i-1]==s[i]: del s[i]; break
        else:return tuple(s)
def valid_compact(g):
    if not g or g[0][1]!=g[-1][0]: return False
    if any(not span(b[0],a[0]) or not span(a[1],b[1]) for a,b in zip(g,g[1:])): return False
    return compact_b1(g)==tuple(g) and max(x[2] for x in g)<=K
def sleq(a,b): return a[0]==b[0] and a[1]==b[1] and a[2]<=b[2]
def relation_exists(lower,upper):
    reachable=set()
    for i in range(len(lower)):
        for j in range(len(upper)):
            if not sleq(lower[i],upper[j]): continue
            if (i,j)==(0,0): reachable.add((i,j)); continue
            if any(p in reachable for p in ((i-1,j-1),(i-1,j),(i,j-1))): reachable.add((i,j))
    return (len(lower)-1,len(upper)-1) in reachable
def verify_witness(lower,upper,w):
    path=w.get('path')
    if not isinstance(path,list) or not path or w.get('path_length')!=len(path): return False
    try: cells=[(int(x[0]),int(x[1])) for x in path if isinstance(x,list) and len(x)==2]
    except Exception:return False
    if len(cells)!=len(path) or cells[0]!=(0,0) or cells[-1]!=(len(lower)-1,len(upper)-1): return False
    for i,j in cells:
        if not (0<=i<len(lower) and 0<=j<len(upper)) or not sleq(lower[i],upper[j]): return False
    return all((b[0]-a[0],b[1]-a[1]) in ((1,0),(0,1),(1,1)) for a,b in zip(cells,cells[1:]))
def derive_inputs(residual):
    out=[]
    for row in residual['proof_payload']['global_compact_frontier']['outcomes']:
        g=dec(row['trajectory']); req(valid_compact(g),'INV02','bad residual frontier trajectory'); out.append(g)
    req(len(set(out))==len(out),'INV02','duplicate input generator'); return tuple(sorted(out))
def relation_set(gens): return {(tid(a),tid(b)) for a in gens for b in gens if relation_exists(a,b)}
def retained_set(gens,rel):
    gens=tuple(sorted(gens)); ids=[tid(g) for g in gens]; out=[]
    for j,g in enumerate(gens):
        strict=[i for i in range(len(gens)) if i!=j and (ids[i],ids[j]) in rel and (ids[j],ids[i]) not in rel]
        eq=[i for i in range(j) if (ids[i],ids[j]) in rel and (ids[j],ids[i]) in rel]
        if not strict and not eq: out.append(g)
    return tuple(out)
def universe_independent():
    subs=((),(1,)); states=tuple(reversed([(l,r,v) for l in subs for r in subs for v in range(K+1)])); maxlen=(2*D+1)*(2*K+1); emitted={}
    def dfs(seq,target):
        if seq[-1][0]==target: emitted[tuple(seq)]=tuple(seq)
        if len(seq)==maxlen:return
        last=seq[-1]
        for nxt in states:
            if not span(nxt[0],last[0]) or not span(last[1],nxt[1]) or not span(target,nxt[0]): continue
            cand=seq+(nxt,)
            if not valid_compact(cand): continue
            dfs(cand,target)
    for first in states:
        if span(first[1],first[0]): dfs((first,),first[1])
    return tuple(emitted[k] for k in sorted(emitted))
def reachable_set(gens,universe): return {tid(c) for c in universe if any(relation_exists(g,c) for g in gens)}
def check_spec_and_sources(specp,producer,residualp):
    req(gb(specp)==SPEC_BLOB,'INV01','spec blob'); s=load(specp); req(s.get('schema')==SPEC_SCHEMA and s.get('status')=='SPEC_FROZEN','INV01','spec')
    e=s['expected_values_policy']; req(all(e[k] is None for k in ('expected_input_generator_count','expected_ordered_relation_count','expected_retained_generator_count','expected_universe_size','expected_closure_entry_count')),'INV01','oracle')
    req(gb(producer)==PRODUCER_BLOB,'INV12','producer blob')
    tree=ast.parse(Path(producer).read_text()); mods=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): mods.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
    req(not any('residual_up_k_verifier' in m for m in mods),'INV12','producer imports verifier')
    r=load(residualp); req(fh(residualp)==RESIDUAL_SHA and r.get('schema')==RESIDUAL_SCHEMA and sem_ok(r) and r.get('semantic_digest')==RESIDUAL_SEM,'INV01','residual binding'); return s,r
def verify_candidate(cand,spec,residual):
    req(cand.get('schema')==SCHEMA and sem_ok(cand),'INV01','candidate semantic'); p=cand['proof_payload']; req(p['admitted'] is False and p['candidate_phase']=='RESIDUAL_UP_K','INV12','phase/admission')
    req(p['source_binding_receipt']['residual_sha256']==RESIDUAL_SHA and p['source_binding_receipt']['residual_semantic_digest']==RESIDUAL_SEM,'INV01','source receipt')
    inputs=derive_inputs(residual); icat=p['input_generators']; req(icat==sorted(icat,key=lambda x:dec(x['trajectory'])),'INV10','input order')
    got_inputs=tuple(sorted(dec(x['trajectory']) for x in icat)); req(got_inputs==inputs,'INV02','input catalog'); req(p['input_generator_catalog_digest']==dg(icat),'INV02','input digest'); req(p['expected_input_count_used'] is False,'INV02','input oracle')
    for x in icat: req(x['trajectory_id']==tid(dec(x['trajectory'])) and x['trajectory_digest']==dg(x['trajectory']) and valid_compact(dec(x['trajectory'])),'INV02','input receipt')
    rel=relation_set(inputs); edges=p['ordered_extension_relation']['edges']; req(edges==sorted(edges,key=lambda x:(x['lower_id'],x['upper_id'])),'INV10','edge order'); req(p['ordered_extension_relation']['edge_count']==len(edges) and p['ordered_extension_relation']['edge_catalog_digest']==dg(edges),'INV03','edge receipt')
    eset={(x['lower_id'],x['upper_id']) for x in edges}; req(eset==rel,'INV03','relation set')
    iby={tid(g):g for g in inputs}
    for e in edges: req(verify_witness(iby[e['lower_id']],iby[e['upper_id']],e['witness']),'INV03','relation witness')
    retained=retained_set(inputs,rel); rcat=p['minimization']['retained_generators']; req(tuple(sorted(dec(x['trajectory']) for x in rcat))==retained,'INV04','retained set'); req(p['minimization']['retained_catalog_digest']==dg(rcat),'INV04','retained digest')
    retby={tid(g):g for g in retained}; removed={tid(g) for g in inputs}-{tid(g) for g in retained}; recs=p['minimization']['removals']; req({x['removed_id'] for x in recs}==removed and p['minimization']['removal_catalog_digest']==dg(recs),'INV04','removal set')
    for x in recs:
        req(x['retained_id'] in retby and x['removed_id'] in iby,'INV04','removal ids'); req((x['retained_id'],x['removed_id']) in rel,'INV04','direct relation missing'); req(verify_witness(retby[x['retained_id']],iby[x['removed_id']],x['witness']),'INV04','removal witness')
    universe=universe_independent(); ucat=p['complete_universe']['entries']; req(ucat==sorted(ucat,key=lambda x:dec(x['trajectory'])),'INV10','universe order'); ugens=tuple(sorted(dec(x['trajectory']) for x in ucat)); req(ugens==universe,'INV05','universe catalog'); req(p['complete_universe']['entry_count']==len(universe) and p['complete_universe']['catalog_digest']==dg(ucat) and p['complete_universe']['supplied_universe_used'] is False,'INV05','universe receipt')
    uby={tid(g):g for g in universe}
    orig=reachable_set(inputs,universe); retcl=reachable_set(retained,universe); req(orig==retcl,'INV06','minimization changed closure')
    ce=p['closure']['retained_generator_entries']; req(ce==sorted(ce,key=lambda x:x['trajectory_id']),'INV10','closure order'); ids={x['trajectory_id'] for x in ce}; req(ids==retcl and p['closure']['entry_count']==len(ids),'INV06','closure set/count'); req(p['closure']['original_entry_catalog_digest']==dg(p['closure']['original_generator_entries']) and p['closure']['retained_entry_catalog_digest']==dg(ce) and p['closure']['closures_equal'] is True,'INV06','closure receipts')
    for x in ce:
        req(x['trajectory_id'] in uby and x['source_generator_id'] in retby,'INV07','closure ids'); req(x['trajectory']==enc(uby[x['trajectory_id']]),'INV07','closure trajectory'); req(relation_exists(retby[x['source_generator_id']],uby[x['trajectory_id']]),'INV07','source not below closure'); req(verify_witness(retby[x['source_generator_id']],uby[x['trajectory_id']],x['witness']),'INV07','closure witness')
    first=tuple(sorted(uby[x] for x in ids)); second_rel=relation_set(first); second_ret=retained_set(first,second_rel); second=reachable_set(second_ret,universe); req(second==ids,'INV08','fixed point mismatch')
    idem=p['idempotence']; req(idem['first_second_closure_equal'] is True and idem['second_closure_digest']==dg(idem['second_closure_entries']) and {x['trajectory_id'] for x in idem['second_closure_entries']}==ids,'INV08','idempotence receipt')
    w=p['work_ledger']; req(w['input_generators_materialized']==len(inputs) and w['ordered_generator_pairs_tested']==len(inputs)**2 and w['relation_edges_retained']==len(rel) and w['complete_universe_entries_materialized']==len(universe) and w['supplied_universe_entries_consumed']==0,'INV09','work ledger')
    d=p['determinism']; req(d['required_order_modes']==['ORIGINAL','REVERSED','SEEDED_SHUFFLE'] and d['byte_identical_output_required'] is True and d['canonical_input_order'] is True and d['canonical_relation_order'] is True and d['canonical_universe_order'] is True and d['canonical_closure_order'] is True,'INV10','determinism')
    expected={'node9_frontier_candidate_complete':True,'node9_parent_refinement_complete':True,'node9_residual_up_k_spec_frozen':True,'node9_residual_up_k_producer_created':True,'node9_residual_up_k_verifier_created':False,'node9_parent_up_k_complete':False,'node9_integrated_into_bottom_up_executor':False,'repository_failed_domains':0,'repository_successful_domains':0,'root_reached':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}
    req(p['strict_boundary']==expected,'INV12','strict boundary'); return {'inputs':inputs,'relation':rel,'retained':retained,'universe':universe,'closure':retcl}
def repair(x):
    p=x['proof_payload']; p['input_generator_catalog_digest']=dg(p['input_generators']); r=p['ordered_extension_relation']; r['edge_count']=len(r['edges']); r['edge_catalog_digest']=dg(r['edges']); m=p['minimization']; m['retained_catalog_digest']=dg(m['retained_generators']); m['removal_catalog_digest']=dg(m['removals']); u=p['complete_universe']; u['entry_count']=len(u['entries']); u['catalog_digest']=dg(u['entries']); c=p['closure']; c['original_entry_catalog_digest']=dg(c['original_generator_entries']); c['retained_entry_catalog_digest']=dg(c['retained_generator_entries']); c['entry_count']=len(c['retained_generator_entries']); i=p['idempotence']; i['second_closure_digest']=dg(i['second_closure_entries']); x['semantic_digest']=dg(p); return x
def tamper_suite(candidate,spec,residual):
    passed=[]
    def attack(name,mut):
        x=copy.deepcopy(candidate); mut(x); repair(x)
        try: verify_candidate(x,spec,residual)
        except VError as e: passed.append((name,e.inv)); return
        raise AssertionError('tamper survived '+name)
    attack('T01_RESIDUAL_BINDING',lambda x:x['proof_payload']['source_binding_receipt'].__setitem__('residual_sha256','0'*64))
    attack('T02_INPUT_GENERATOR',lambda x:x['proof_payload']['input_generators'][0]['trajectory'][0].__setitem__('value',1-x['proof_payload']['input_generators'][0]['trajectory'][0]['value']))
    attack('T03_RELATION_EDGE',lambda x:x['proof_payload']['ordered_extension_relation']['edges'].pop())
    attack('T04_REMOVAL_WITNESS',lambda x:x['proof_payload']['minimization']['removals'][0]['witness'].__setitem__('path',[[0,0]]))
    attack('T05_RETAINED',lambda x:x['proof_payload']['minimization']['retained_generators'].pop())
    attack('T06_UNIVERSE_OMISSION',lambda x:x['proof_payload']['complete_universe']['entries'].pop())
    attack('T07_CLOSURE_WITNESS',lambda x:x['proof_payload']['closure']['retained_generator_entries'][0]['witness'].__setitem__('path',[[0,0]]))
    attack('T08_CLOSURE_OMISSION',lambda x:x['proof_payload']['closure']['retained_generator_entries'].pop())
    def t09(x):
        used={e['trajectory_id'] for e in x['proof_payload']['closure']['retained_generator_entries']}; extra=next(e for e in x['proof_payload']['complete_universe']['entries'] if e['trajectory_id'] not in used); x['proof_payload']['closure']['retained_generator_entries'].append({'trajectory_id':extra['trajectory_id'],'trajectory':extra['trajectory'],'source_generator_id':x['proof_payload']['minimization']['retained_generators'][0]['trajectory_id'],'witness':{'path':[[0,0]],'path_length':1}}); x['proof_payload']['closure']['retained_generator_entries'].sort(key=lambda z:z['trajectory_id'])
    attack('T09_UNREACHABLE_CLOSURE_ENTRY',t09)
    attack('T10_IDEMPOTENCE',lambda x:x['proof_payload']['idempotence'].__setitem__('first_second_closure_equal',False))
    attack('T11_CANONICAL_ORDER',lambda x:x['proof_payload']['complete_universe']['entries'].reverse())
    attack('T12_BOUNDARY',lambda x:x['proof_payload']['strict_boundary'].__setitem__('next_gate','OPEN'))
    req(len(passed)==12,'INV11','tamper count'); return passed
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--producer-source',type=Path,required=True); ap.add_argument('--residual-artifact',type=Path,required=True); ap.add_argument('--candidate-original',type=Path,required=True); ap.add_argument('--candidate-reversed',type=Path,required=True); ap.add_argument('--candidate-seeded-shuffle',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args()
    spec,residual=check_spec_and_sources(a.spec,a.producer_source,a.residual_artifact); b=a.candidate_original.read_bytes(); req(b==a.candidate_reversed.read_bytes()==a.candidate_seeded_shuffle.read_bytes(),'INV10','three-mode bytes'); cand=load(a.candidate_original); ref=verify_candidate(cand,spec,residual); tamp=tamper_suite(cand,spec,residual) if a.tamper_suite else []
    print('JANUS_NODE9_RESIDUAL_UP_K_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED'); print('MATHEMATICAL_INDEPENDENCE = NOT_AUTOMATIC'); print('SPECIFICATION_INDEPENDENCE = NOT_AUTOMATIC'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(tamp)}/12' if a.tamper_suite else 'NOT_RUN'); print('INPUT_GENERATORS =',len(ref['inputs'])); print('ORDERED_EXTENSION_RELATIONS =',len(ref['relation'])); print('RETAINED_GENERATORS =',len(ref['retained'])); print('COMPLETE_UNIVERSE_SIZE =',len(ref['universe'])); print('UP_K_CLOSURE_ENTRIES =',len(ref['closure'])); print('IDEMPOTENT = TRUE'); print('CANDIDATE_ARTIFACT_SHA256 =',fh(a.candidate_original)); print('CANDIDATE_SEMANTIC_DIGEST =',cand['semantic_digest']); print('NODE9_PARENT_UP_K_COMPLETE = FALSE'); print('FORMAL_ADMISSION = BLOCKED'); print('NEXT_GATE = CLOSED'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
