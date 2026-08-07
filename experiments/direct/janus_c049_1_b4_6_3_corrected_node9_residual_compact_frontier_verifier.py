from __future__ import annotations
import argparse, ast, copy, hashlib, itertools, json
from collections import defaultdict
from pathlib import Path

SCHEMA='janus.c049_1.corrected_node9_residual_compact_frontier_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_node9_residual_compact_frontier_spec.v1'
SCALAR_SCHEMA='janus.c049_1.corrected_node9_scalar_symbolic_automaton_candidate.v1'
Q80_SCHEMA='C049.1-B4.6.3-CORRECTED-NODE9-QUOTIENT-SKELETON-STABILITY-ANALYSIS-v1'
SPEC_SHA='5e7141cfe628a2e0324bafec22febb1d9cec5776c2fb0dea516dfb2252b582c8'
PRODUCER_BLOB_SHA='bba8a73572a4f7e264ddd248ab2fff5d72e149ea'
SCALAR_SHA='b953c89f95f3deee18fe92080b0988846603a46c17e0f51bcfa2eef50d325aca'
SCALAR_SEM='cecafe9a26119c2b035db65d3d98f8f4f81cb033ce5616b8089c3e3207d7eae1'
Q80_SHA='fa21c129ad7c03cad0f46c5a5baeb3941d0c94baadea54718d8059652f3a3375'
Q80_SEM='1463974e2378c60ca6f2ebba961c5366a98c59f9efc65603851e87239229f4a1'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

class VError(AssertionError):
    def __init__(self,inv,msg): super().__init__(f'{inv}: {msg}'); self.inv=inv

def req(ok,inv,msg):
    if not ok: raise VError(inv,msg)
def cj(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cj(x)).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git_blob(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sem_ok(a): return a.get('semantic_digest_scope')=='proof_payload' and dg(a.get('proof_payload'))==a.get('semantic_digest')

def bind_inputs(spec_path,producer_source,scalar_path,q80_path):
    req(fh(spec_path)==SPEC_SHA,'INV01','spec sha')
    s=load(spec_path); req(s.get('schema')==SPEC_SCHEMA and s.get('status')=='SPEC_FROZEN','INV01','spec schema/status')
    e=s['expected_values_policy']; req(all(e[k] is None for k in ('expected_mixed_domain_count','expected_accepted_run_count','expected_global_compact_outcome_count','expected_per_domain_compact_outcome_count','expected_post_compact_generator_count')),'INV03','output oracle present')
    req(e['historical_or_local_values_may_seed_expected_values'] is False,'INV03','oracle policy')
    req(git_blob(producer_source)==PRODUCER_BLOB_SHA,'INV12','producer source git blob')
    text=Path(producer_source).read_text(encoding='utf-8'); tree=ast.parse(text)
    imported=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): imported.extend(a.name for a in node.names)
        elif isinstance(node,ast.ImportFrom): imported.append(node.module or '')
    req(not any('residual_compact_frontier_verifier' in name for name in imported),'INV12','producer imports verifier')
    scalar=load(scalar_path); req(fh(scalar_path)==SCALAR_SHA and scalar.get('schema')==SCALAR_SCHEMA and sem_ok(scalar) and scalar.get('semantic_digest')==SCALAR_SEM,'INV01','scalar binding')
    q80=load(q80_path); req(fh(q80_path)==Q80_SHA and q80.get('schema')==Q80_SCHEMA and sem_ok(q80) and q80.get('semantic_digest')==Q80_SEM,'INV02','q80 binding')
    return s,scalar,q80

def langs(r): return tuple(tuple(tuple(int(x) for x in w) for w in seg['words']) for seg in r['segment_languages'])
def dec(raw): return tuple((tuple(map(int,x['left'])),tuple(map(int,x['right'])),int(x['value'])) for x in raw)
def enc(seq): return [{'left':list(a),'right':list(b),'value':int(v)} for a,b,v in seq]
def seqdg(seq): return dg(enc(seq))

def interval_rule(s,i,j):
    if j-i<=1 or (s[i][0],s[i][1])!=(s[j][0],s[j][1]): return False
    a,b=s[i][2],s[j][2]; xs=[x[2] for x in s[i+1:j]]
    return (a<=b and all(a<=x<=b for x in xs)) or (a>=b and all(a>=x>=b for x in xs))

def compact_left(seq):
    s=list(seq); tr=[]
    while True:
        changed=False
        for i in range(1,len(s)):
            if s[i-1]==s[i]:
                rem=[s[i]]; before=len(s); del s[i]
                tr.append({'rule':'duplicate','start':i-1,'end':i,'before_length':before,'removed_entries':enc(rem),'after_length':len(s),'after_digest':seqdg(s)})
                changed=True; break
        if changed: continue
        for i in range(len(s)):
            for j in range(i+2,len(s)):
                if interval_rule(s,i,j):
                    rem=s[i+1:j]; before=len(s); del s[i+1:j]
                    tr.append({'rule':'interval','start':i,'end':j,'before_length':before,'removed_entries':enc(rem),'after_length':len(s),'after_digest':seqdg(s)})
                    changed=True; break
            if changed: break
        if not changed: return tuple(s),tr

def compact_alt(seq):
    s=list(seq)
    while True:
        hit=None
        for i in range(len(s)-1,-1,-1):
            for j in range(len(s)-1,i+1,-1):
                if interval_rule(s,i,j): hit=(i,j); break
            if hit: break
        if hit:
            i,j=hit; del s[i+1:j]; continue
        changed=False
        for i in range(len(s)-1,0,-1):
            if s[i-1]==s[i]: del s[i]; changed=True; break
        if not changed: return tuple(s)

def replay_trace(pre,trace):
    s=list(pre)
    for step in trace:
        before=len(s); req(step['before_length']==before,'INV05','trace before length')
        rule=step['rule']; i=int(step['start']); j=int(step['end'])
        if rule=='duplicate':
            req(j==i+1 and 0<=i<j<len(s) and s[i]==s[j],'INV05','duplicate trace rule')
            rem=[s[j]]; del s[j]
        elif rule=='interval':
            req(0<=i<j<len(s) and interval_rule(s,i,j),'INV05','interval trace rule')
            rem=s[i+1:j]; del s[i+1:j]
        else: raise VError('INV05','unknown trace rule')
        req(step['removed_entries']==enc(rem),'INV05','removed entries')
        req(step['after_length']==len(s) and step['after_digest']==seqdg(s),'INV05','trace after receipt')
    return tuple(s)

def contains(big,small): return (not small) or big==(1,)
def validate_compact(seq):
    req(bool(seq),'INV05','empty compact trajectory')
    req(seq[0][1]==seq[-1][0],'INV05','endpoint')
    for a,b in zip(seq,seq[1:]): req(contains(b[0],a[0]) and contains(a[1],b[1]),'INV05','trajectory monotonicity')
    req(compact_alt(seq)==tuple(seq),'INV05','not alt-priority compact')
    req(max(x[2] for x in seq)<=1,'INV05','width exceeds one')

def make_run(domain,left_profile,right_profile,steps,spath):
    q=[tuple(map(int,x)) for x in domain['quotient_path']]
    geom=[(tuple(map(int,g['left'])),tuple(map(int,g['right']))) for g in domain['projected_geometry']]
    corr=[int(a)+int(b) for a,b in zip(domain['join_correction_vector'],domain['shrink_correction_vector'])]
    pre=[]
    for qi,li,ri in spath:
        a,b=q[qi]; lam=left_profile[a][li]+right_profile[b][ri]+corr[qi]
        req(lam<=1,'INV04','accepted reference includes rejected state'); pre.append((geom[qi][0],geom[qi][1],lam))
    comp,tr=compact_left(pre); req(compact_alt(pre)==comp,'INV05','priority normal forms disagree'); validate_compact(comp)
    prov={'domain_id':domain['domain_id'],'left_profile':[list(w) for w in left_profile],'right_profile':[list(w) for w in right_profile],'fine_steps':list(steps),'fine_state_path':[{'quotient_cell_index':qi,'left_offset':li,'right_offset':ri} for qi,li,ri in spath]}
    rid='AR-'+dg(prov)[:24]; ce=enc(comp); tid='CT-'+dg(ce)[:24]
    rec={'run_id':rid,'domain_id':domain['domain_id'],'source_class_id':domain['source_class_id'],'provenance':prov,'precompact_trajectory':enc(pre),'precompact_trajectory_digest':seqdg(pre),'compact_trajectory_id':tid,'compact_trajectory':ce,'compact_trajectory_digest':dg(ce),'compactification_trace':tr,'compactification_trace_digest':dg(tr),'compact_width':max(x[2] for x in comp)}
    rec['run_record_digest']=dg(rec); return rec

def enumerate_fixed_profile_paths(domain,left_profile,right_profile):
    q=tuple(tuple(map(int,x)) for x in domain['quotient_path']); corr=tuple(int(a)+int(b) for a,b in zip(domain['join_correction_vector'],domain['shrink_correction_vector']))
    out=[]
    def valid(qi,li,ri):
        a,b=q[qi]; return left_profile[a][li]+right_profile[b][ri]+corr[qi]<=1
    def terminal(qi,li,ri):
        a,b=q[qi]; return qi==len(q)-1 and a==len(left_profile)-1 and b==len(right_profile)-1 and li==len(left_profile[a])-1 and ri==len(right_profile[b])-1
    def dfs(qi,li,ri,steps,spath):
        if not valid(qi,li,ri): return
        if terminal(qi,li,ri): out.append(make_run(domain,left_profile,right_profile,steps,spath)); return
        a,b=q[qi]; lp=left_profile[a]; rp=right_profile[b]
        if ri+1<len(rp): dfs(qi,li,ri+1,steps+('V_INTERNAL',),spath+((qi,li,ri+1),))
        elif qi+1<len(q) and q[qi+1]==(a,b+1): dfs(qi+1,li,0,steps+('V_CELL',),spath+((qi+1,li,0),))
        if li+1<len(lp): dfs(qi,li+1,ri,steps+('H_INTERNAL',),spath+((qi,li+1,ri),))
        elif qi+1<len(q) and q[qi+1]==(a+1,b): dfs(qi+1,0,ri,steps+('H_CELL',),spath+((qi+1,0,ri),))
    dfs(0,0,0,tuple(),((0,0,0),)); return out

def outcome(tid,traj,runs):
    ids=sorted(r['run_id'] for r in runs)
    return {'compact_trajectory_id':tid,'trajectory':traj,'trajectory_digest':dg(traj),'width':max(x['value'] for x in traj),'length':len(traj),'accepted_run_multiplicity':len(runs),'run_ids_digest':dg(ids)}

def derive_reference(scalar,q80):
    sp=scalar['proof_payload']; qp=q80['proof_payload']; qby={d['domain_id']:d for d in qp['quotient_domains']}; rby={r['source_class_id']:r for r in sp['scalar_factorization']['node8_source_class_receipts']}; R=langs(sp['scalar_factorization']['leaf5_receipt'])
    mixed=sorted((r for r in sp['domain_records'] if r['classification']=='MIXED'),key=lambda x:x['domain_id']); allruns=[]; domains=[]; projections=0
    for row in mixed:
        d=qby.get(row['domain_id']); req(d is not None,'INV02','missing q80 domain')
        for k in ('source_class_id','quotient_path','join_correction_vector','shrink_correction_vector'): req(row[k]==d[k],'INV02',row['domain_id']+' '+k)
        req(row['q80_fine_lift_domain_digest']==d['fine_lift_domain_digest'] and row['q80_fine_lift_multiplicity']==d['fine_lift_multiplicity'],'INV02','q80 multiplicity link')
        L=langs(rby[row['source_class_id']]); rr=[]
        for lp in itertools.product(*L):
            for rp in itertools.product(*R):
                projections+=1; rr.extend(enumerate_fixed_profile_paths(d,lp,rp))
        byid={r['run_id']:r for r in rr}; req(len(byid)==len(rr),'INV04','reference duplicate run')
        rr=[byid[k] for k in sorted(byid)]; req(len(rr)==row['width_filtered_automaton']['run_multiplicity'],'INV04','upstream accepted multiplicity mismatch')
        allruns.extend(rr); by=defaultdict(list)
        for r in rr: by[r['compact_trajectory_id']].append(r)
        outs=[outcome(t,by[t][0]['compact_trajectory'],by[t]) for t in sorted(by)]
        domains.append({'domain_id':row['domain_id'],'source_class_id':row['source_class_id'],'upstream_accepted_run_multiplicity':row['width_filtered_automaton']['run_multiplicity'],'materialized_accepted_run_count':len(rr),'accepted_run_ids_digest':dg(sorted(r['run_id'] for r in rr)),'distinct_compact_outcome_count':len(outs),'compact_outcomes':outs})
    allruns.sort(key=lambda r:r['run_id']); req(len({r['run_id'] for r in allruns})==len(allruns),'INV04','global duplicate run')
    gob=defaultdict(list)
    for r in allruns:gob[r['compact_trajectory_id']].append(r)
    gout=[]
    for t in sorted(gob):
        x=outcome(t,gob[t][0]['compact_trajectory'],gob[t]); x['source_domain_ids']=sorted({r['domain_id'] for r in gob[t]}); gout.append(x)
    total=sp['conservation_ledger']['derived_unrestricted_symbolic_run_total']; good=sp['conservation_ledger']['derived_width_le_1_run_total']; bad=sp['conservation_ledger']['derived_width_gt_1_run_total']
    req(len(allruns)==good and total==good+bad,'INV09','upstream conservation')
    return {'runs':allruns,'domains':domains,'outcomes':gout,'mixed_ids':[r['domain_id'] for r in mixed],'total':total,'good':good,'bad':bad,'profile_pair_domain_projections':projections}

def verify_run_record(r):
    base={k:v for k,v in r.items() if k!='run_record_digest'}; req(r['run_record_digest']==dg(base),'INV04','run digest')
    prov=r['provenance']; req(r['run_id']=='AR-'+dg(prov)[:24],'INV04','run id')
    pre=dec(r['precompact_trajectory']); comp=dec(r['compact_trajectory'])
    req(r['precompact_trajectory_digest']==seqdg(pre),'INV04','precompact digest')
    req(r['compact_trajectory_digest']==dg(r['compact_trajectory']) and r['compact_trajectory_id']=='CT-'+dg(r['compact_trajectory'])[:24],'INV05','compact digest/id')
    req(r['compactification_trace_digest']==dg(r['compactification_trace']),'INV05','trace digest')
    out=replay_trace(pre,r['compactification_trace']); req(out==comp,'INV05','trace output')
    req(compact_alt(pre)==comp,'INV05','alternative normal form')
    validate_compact(comp); req(r['compact_width']==max(x[2] for x in comp),'INV05','compact width receipt')

def verify_candidate(candidate,ref,spec):
    req(candidate.get('schema')==SCHEMA and sem_ok(candidate),'INV01','candidate schema/semantic digest'); p=candidate['proof_payload']
    req(p['candidate_phase']=='RESIDUAL_COMPACT_FRONTIER' and p['admitted'] is False,'INV12','candidate phase/admission')
    req(p['spec_binding']['spec_file_sha256']==SPEC_SHA and p['spec_binding']['upstream_admission_review_id']==spec['upstream_scalar_candidate_admission']['review_id'],'INV01','spec/admission binding')
    src=p['source_binding_receipt']; req(src=={'scalar_candidate_sha256':SCALAR_SHA,'scalar_candidate_semantic_digest':SCALAR_SEM,'q80_sha256':Q80_SHA,'q80_semantic_digest':Q80_SEM},'INV01','source binding receipt')
    sel=p['residual_domain_selection']; req(sel['selection_rule']=='classification == MIXED' and sel['selected_domain_ids']==ref['mixed_ids'] and sel['selected_domain_count']==len(ref['mixed_ids']) and sel['expected_count_used'] is False,'INV03','residual selection')
    runs=p['accepted_run_records']; req(runs==sorted(runs,key=lambda r:r['run_id']),'INV10','canonical run order'); req(len(runs)==len(ref['runs']),'INV04','run count')
    for r in runs: verify_run_record(r)
    req(runs==ref['runs'],'INV04','independent accepted run set mismatch')
    domains=p['domain_frontiers']; req(domains==sorted(domains,key=lambda r:r['domain_id']),'INV10','canonical domain order'); req(domains==ref['domains'],'INV06','per-domain frontier mismatch')
    gf=p['global_compact_frontier']; req(gf['outcomes']==ref['outcomes'] and gf['distinct_compact_trajectory_count']==len(ref['outcomes']) and gf['frontier_catalog_digest']==dg(ref['outcomes']) and gf['expected_count_used'] is False,'INV07','global frontier mismatch')
    led=p['conservation_ledger']; req(led['upstream_fine_refinements']==ref['total'] and led['upstream_width_le_1_multiplicity']==ref['good'] and led['upstream_width_gt_1_multiplicity']==ref['bad'],'INV09','upstream ledger')
    req(led['materialized_accepted_runs']==ref['good'] and led['materialized_failed_fine_paths']==0 and led['global_compact_outcome_multiplicity_sum']==ref['good'] and led['omitted_accepted_runs']==0 and led['duplicated_accepted_runs']==0 and led['fine_refinement_partition_preserved'] is True,'INV09','conservation')
    w=p['work_ledger']; req(w['accepted_runs_materialized']==ref['good'] and w['failed_fine_paths_materialized']==0 and w['compactification_traces_materialized']==ref['good'] and w['global_compact_outcomes_materialized']==len(ref['outcomes']),'INV08','work ledger')
    det=p['determinism']; req(det['required_order_modes']==['ORIGINAL','REVERSED','SEEDED_SHUFFLE'] and det['byte_identical_output_required'] is True and det['canonical_run_order'] is True and det['canonical_domain_order'] is True and det['canonical_frontier_order'] is True,'INV10','determinism contract')
    b=p['strict_boundary']; expected={'node9_scalar_automaton_candidate_complete':True,'node9_residual_compact_frontier_spec_frozen':True,'node9_residual_compact_frontier_producer_created':True,'node9_residual_compact_frontier_verifier_created':False,'node9_frontier_candidate_complete':False,'node9_parent_refinement_complete':False,'node9_parent_up_k_complete':False,'node9_integrated_into_bottom_up_executor':False,'repository_failed_domains':0,'repository_successful_domains':0,'root_reached':False,'found_layout':'FORBIDDEN','no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}
    req(b==expected,'INV12','strict boundary')
    return True

def repair_outer(x): x['semantic_digest']=dg(x['proof_payload']); return x

def repair_run(r):
    r['precompact_trajectory_digest']=dg(r['precompact_trajectory']); r['compact_trajectory_digest']=dg(r['compact_trajectory']); r['compact_trajectory_id']='CT-'+dg(r['compact_trajectory'])[:24]; r['compactification_trace_digest']=dg(r['compactification_trace']); r['run_id']='AR-'+dg(r['provenance'])[:24]; r['run_record_digest']=dg({k:v for k,v in r.items() if k!='run_record_digest'})

def tamper_suite(candidate,ref,spec):
    cases=[]
    def add(name,inv,mut):
        x=copy.deepcopy(candidate); mut(x); repair_outer(x)
        try: verify_candidate(x,ref,spec)
        except VError as e: cases.append((name,e.inv)); return
        raise AssertionError('tamper survived: '+name)
    add('T01_SCALAR_BINDING','INV01',lambda x:x['proof_payload']['source_binding_receipt'].__setitem__('scalar_candidate_sha256','0'*64))
    add('T02_Q80_BINDING','INV01',lambda x:x['proof_payload']['source_binding_receipt'].__setitem__('q80_sha256','1'*64))
    add('T03_DELETE_ACCEPTED_RUN','INV04',lambda x:x['proof_payload']['accepted_run_records'].pop())
    def t04(x):
        r=copy.deepcopy(x['proof_payload']['accepted_run_records'][0]); r['provenance']['fine_steps']=r['provenance']['fine_steps']+['H_INTERNAL']; repair_run(r); x['proof_payload']['accepted_run_records'].append(r); x['proof_payload']['accepted_run_records'].sort(key=lambda z:z['run_id'])
    add('T04_DUPLICATE_OR_EXTRA_RUN','INV04',t04)
    def t05(x):
        r=x['proof_payload']['accepted_run_records'][0]; r['provenance']['fine_steps'][0]='V_INTERNAL' if r['provenance']['fine_steps'][0]!='V_INTERNAL' else 'H_INTERNAL'; repair_run(r); x['proof_payload']['accepted_run_records'].sort(key=lambda z:z['run_id'])
    add('T05_FINE_PROVENANCE','INV04',t05)
    def t06(x):
        r=next(z for z in x['proof_payload']['accepted_run_records'] if z['compactification_trace']); r['compactification_trace'][0]['after_digest']='2'*64; repair_run(r); x['proof_payload']['accepted_run_records'].sort(key=lambda z:z['run_id'])
    add('T06_COMPACT_TRACE','INV05',t06)
    def t07(x):
        r=x['proof_payload']['accepted_run_records'][0]; r['compact_trajectory'][0]['value']=1-r['compact_trajectory'][0]['value']; repair_run(r); x['proof_payload']['accepted_run_records'].sort(key=lambda z:z['run_id'])
    add('T07_COMPACT_TRAJECTORY','INV05',t07)
    add('T08_DOMAIN_MULTIPLICITY','INV06',lambda x:x['proof_payload']['domain_frontiers'][0]['compact_outcomes'][0].__setitem__('accepted_run_multiplicity',x['proof_payload']['domain_frontiers'][0]['compact_outcomes'][0]['accepted_run_multiplicity']+1))
    def t09(x):
        r=x['proof_payload']['accepted_run_records'][0]; other=x['proof_payload']['global_compact_frontier']['outcomes'][-1]; r['compact_trajectory_id']=other['compact_trajectory_id']; r['run_record_digest']=dg({k:v for k,v in r.items() if k!='run_record_digest'})
    add('T09_RUN_OUTCOME_REMAP','INV04',t09)
    add('T10_CONSERVATION','INV09',lambda x:x['proof_payload']['conservation_ledger'].__setitem__('omitted_accepted_runs',1))
    add('T11_CANONICAL_ORDER','INV10',lambda x:x['proof_payload']['accepted_run_records'].reverse())
    add('T12_BOUNDARY_PROMOTION','INV12',lambda x:x['proof_payload']['strict_boundary'].__setitem__('next_gate','OPEN'))
    req(len(cases)==12,'INV11','tamper count'); return cases

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--producer-source',type=Path,required=True); ap.add_argument('--scalar-artifact',type=Path,required=True); ap.add_argument('--q80-artifact',type=Path,required=True); ap.add_argument('--candidate-original',type=Path,required=True); ap.add_argument('--candidate-reversed',type=Path,required=True); ap.add_argument('--candidate-seeded-shuffle',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); z=ap.parse_args()
    spec,scalar,q80=bind_inputs(z.spec,z.producer_source,z.scalar_artifact,z.q80_artifact)
    b0=z.candidate_original.read_bytes(); req(b0==z.candidate_reversed.read_bytes()==z.candidate_seeded_shuffle.read_bytes(),'INV10','three-mode byte identity')
    candidate=load(z.candidate_original); ref=derive_reference(scalar,q80); verify_candidate(candidate,ref,spec)
    tamp=tamper_suite(candidate,ref,spec) if z.tamper_suite else []
    print('JANUS_NODE9_RESIDUAL_COMPACT_FRONTIER_INDEPENDENT_VERIFIER = PASS')
    print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED')
    print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED')
    print('MATHEMATICAL_INDEPENDENCE = NOT_AUTOMATIC')
    print('SPECIFICATION_INDEPENDENCE = NOT_AUTOMATIC')
    print('INVARIANTS = 12/12')
    print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(tamp)}/12' if z.tamper_suite else 'NOT_RUN')
    print('MIXED_DOMAINS =',len(ref['mixed_ids']))
    print('PROFILE_PAIR_DOMAIN_PROJECTIONS =',ref['profile_pair_domain_projections'])
    print('ACCEPTED_RUNS =',ref['good'])
    print('GLOBAL_COMPACT_TRAJECTORIES =',len(ref['outcomes']))
    print('FAILED_FINE_PATHS_MATERIALIZED = 0')
    print('CANDIDATE_ARTIFACT_SHA256 =',fh(z.candidate_original))
    print('CANDIDATE_SEMANTIC_DIGEST =',candidate['semantic_digest'])
    print('NODE9_FRONTIER_CANDIDATE_COMPLETE = FALSE')
    print('NODE9_PARENT_REFINEMENT_COMPLETE = FALSE')
    print('FORMAL_ADMISSION = BLOCKED')
    print('NEXT_GATE = CLOSED')
    print('P_VS_NP = OPEN')
if __name__=='__main__': main()
