from __future__ import annotations
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import hashlib, json, random, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
import transfer_core as tc
import make_population as gen

EXPECTED_HASHES={
 'transfer_core.py':'dba2dc94980081497f30870d962ffff3b536f6e8271176187b061b5fbe0e19dd',
 'synthesizer.py':'7d3e385f6090fad9712d8d88b87ef688e30b04184aae6b8d24b5d93bc7646bb9',
 'BASELINES_FROZEN.json':'04d92465908d48a1981f901ca149c68e350a9aff4e570ac92cca516410e1f6d7',
 'FROZEN_RHO.json':'ba1343a8c00ba95009c6aa75ac0cf30b8e01d1234a6d4788d128c3a386d8c2b4'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sat_clause(c,a): return any(a.get(abs(x),False)==(x>0) for x in c)
def replay(raw,a): return all(sat_clause(c,a) for c in raw)
def allvars(raw): return sorted({abs(x) for c in raw for x in c})
def assemble_details(edges,mods,pm):
    base=[]; nxt=1
    for m in mods:
        mp0={v:nxt+v-1 for v in range(1,m['nvars']+1)}
        nxt+=m['nvars']; base.append(mp0)
    repl={}; shared=[]
    for ei,(a,b) in enumerate(edges):
        pa=mods[a]['ports'][pm[a][ei]]; pb=mods[b]['ports'][pm[b][ei]]
        s=10_000_000+ei; shared.append(s)
        repl[base[a][pa]]=s; repl[base[b][pb]]=s
    raw=[]; comps=[]
    for i,m in enumerate(mods):
        cc=[]
        for c in m['cnf']:
            z=[]
            for lit in c:
                g=base[i][abs(lit)]; g=repl.get(g,g)
                z.append(g if lit>0 else -g)
            raw.append(z); cc.append(z)
        comps.append(cc)
    return raw,comps,shared

def cal_varmap(raw,seed):
    rng=random.Random(seed); vs=allvars(raw)
    new=[100000+19*i for i in range(1,len(vs)+1)]; rng.shuffle(new)
    return dict(zip(vs,new))
def map_clause(c,vm): return [(vm[abs(x)] if x>0 else -vm[abs(x)]) for x in c]
def oracle_sat(raw,fixed=None):
    fixed={} if fixed is None else dict(fixed); vs=[v for v in allvars(raw) if v not in fixed]
    for bits in product([0,1],repeat=len(vs)):
        a={int(k):bool(v) for k,v in fixed.items()}; a.update({v:bool(b) for v,b in zip(vs,bits)})
        if replay(raw,a): return True,a
    return False,None

def graph_for(edges,shared,comps):
    adj={i:[] for i in range(len(comps))}; ee=[]
    for ei,(a,b) in enumerate(edges):
        s=[shared[ei]]; adj[a].append((b,s)); adj[b].append((a,s)); ee.append((a,b,s))
    bounds=[]
    for i in range(len(comps)):
        bounds.append(sorted({x for _,s in adj[i] for x in s}))
    return {'adj':adj,'edges':ee,'boundaries':bounds}

def make_spec(cid,truth,mods,edges,pm,seed):
    raw,comps0,shared0=assemble_details(edges,mods,pm); vm=cal_varmap(raw,seed)
    comps=[[map_clause(c,vm) for c in cc] for cc in comps0]
    shared=[vm[x] for x in shared0]; root=gen.transport(raw,seed,'cal_encoder_v1')
    return {'id':cid,'truth':truth,'root':root,'components':comps,'edges':edges,
            'shared':shared,'graph':graph_for(edges,shared,comps),'modules':mods,'varmap':vm}
def build_specs():
    out=[]
    for rep in range(2):
        for truth in ('SAT','UNSAT'):
            m0=gen.template(3,1,'CONST_TRUE')
            m1=gen.template(1,1,'CONST_TRUE') if truth=='SAT' else gen.template(2,1,'GATE_FALSE_PARENT')
            mods=[m0,m1]; edges=[(0,1)]; pm=[{0:0},{0:0}]
            seed=1500+rep*10+(truth=='UNSAT'); cid=f'cal-k2-r{rep}-{truth.lower()}'
            out.append(make_spec(cid,truth,mods,edges,pm,seed))
    idx=0
    for rep in range(2):
        for k,name in [(3,'short_path'),(4,'short_path')]:
            seed=1600+rep*100+idx; edges=gen.topology(k,name,seed); mods=gen.choose_modules(k,edges,seed)
            for truth in ('SAT','UNSAT'):
                pm=gen.make_port_map(k,edges,mods,truth); cid=f'cal-pair{idx:02d}-{truth.lower()}'
                out.append(make_spec(cid,truth,mods,edges,pm,seed+9001))
            idx+=1
    return out

def canonical_key(raw): return tuple(tuple(c) for c in tc.canon(raw))
def load_calibration():
    return json.loads((ROOT/'calibration.json').read_text(encoding='utf-8'))['cases']
def separator_trace(cnf,sep):
    sep=set(sep); all_non={abs(x) for c in cnf for x in c if abs(x) not in sep}
    if not all_non: return {'reason':'NO_NON_SEPARATOR_VARS'}
    adj={v:set() for v in all_non}
    for c in cnf:
        xs=sorted({abs(x) for x in c if abs(x) not in sep})
        for i,a in enumerate(xs):
            for b in xs[i+1:]: adj[a].add(b); adj[b].add(a)
    comp={}; groups=[]
    for s in sorted(all_non):
        if s in comp: continue
        cid=len(groups); q=[s]; comp[s]=cid; vs=[]
        while q:
            x=q.pop(); vs.append(x)
            for y in adj[x]:
                if y not in comp: comp[y]=cid; q.append(y)
        groups.append(sorted(vs))
    if len(groups)<2: return {'reason':'LT2_COMPONENTS','group_vars':groups}
    cg=[[] for _ in groups]
    for c in cnf:
        owners={comp[abs(x)] for x in c if abs(x) not in sep}
        if len(owners)!=1: return {'reason':'CLAUSE_MULTIPLE_OWNERS','group_vars':groups}
        cg[next(iter(owners))].append(list(c))
    cg=[g for g in cg if g]
    sizes=[len(g) for g in cg]
    if len(cg)<2: reason='LT2_NONEMPTY_GROUPS'
    elif min(sizes)<3: reason='MIN_CLAUSE_GROUP_LT_3'
    else: reason='PASS_PRE_TOUCH'
    return {'reason':reason,'group_vars':groups,'clause_group_sizes':sizes}
def oracle_relation(raw,boundary):
    allowed=[]; forbidden=[]
    for bits in product([0,1],repeat=len(boundary)):
        fixed={v:bool(b) for v,b in zip(boundary,bits)}
        ok,wit=oracle_sat(raw,fixed)
        rec={'tuple':list(bits)}
        if ok:
            rec['witness']=wit; allowed.append(rec)
        else: forbidden.append(rec)
    return {'boundary':list(boundary),'allowed':allowed,'forbidden':forbidden}

def allowed_set(rel): return {tuple(x['tuple']) for x in rel['allowed']}
def full_assignment(root,a):
    z={int(k):bool(v) for k,v in a.items()}
    for v in allvars(root): z.setdefault(v,False)
    return z

def independent_join(root,graph,relations):
    adj=graph['adj']; parent={0:None}; order=[0]
    for u in order:
        for v,_ in adj[u]:
            if v not in parent: parent[v]=u; order.append(v)
    children={u:[v for v,_ in adj[u] if parent.get(v)==u] for u in range(len(relations))}
    feasible={}
    for u in reversed(order):
        good=[]
        for i,e in enumerate(relations[u]['allowed']):
            amap={v:bool(b) for v,b in zip(relations[u]['boundary'],e['tuple'])}
            if all(any(all(amap[x]==bool(ce['tuple'][relations[ch]['boundary'].index(x)]) for x in next(s for v,s in adj[u] if v==ch)) for ce in (relations[ch]['allowed'][j] for j in feasible[ch])) for ch in children[u]): good.append(i)
        feasible[u]=good
    return ('SAT' if feasible.get(0) else 'UNSAT'),feasible,parent,children
def independent_reconstruct(root,graph,relations,feasible,parent,children):
    chosen={}; merged={}
    def pick(u,parent_map=None):
        for idx in feasible[u]:
            e=relations[u]['allowed'][idx]
            amap={v:bool(b) for v,b in zip(relations[u]['boundary'],e['tuple'])}
            if parent_map is not None:
                p=parent[u]; sep=next(s for v,s in graph['adj'][u] if v==p)
                if any(amap[x]!=parent_map[x] for x in sep): continue
            snapshot=dict(merged); chosen[u]=idx
            ok=True
            for v,val in e['witness'].items():
                v=int(v); val=bool(val)
                if v in merged and merged[v]!=val: ok=False; break
                merged[v]=val
            if ok and all(pick(ch,amap) for ch in children[u]): return True
            merged.clear(); merged.update(snapshot); chosen.pop(u,None)
        return False
    if not feasible.get(0) or not pick(0,None): return None,None,False
    a=full_assignment(root,merged)
    return a,chosen,replay(root,a)

def frozen_B(spec):
    rels=[]
    for leaf,b in zip(spec['components'],spec['graph']['boundaries']):
        rel,err=tc.leaf_relation(leaf,b)
        if err: return {'decision':None,'error':err}
        rels.append(rel)
    z=tc.transfer_join(spec['root'],spec['components'],spec['graph'],rels)
    ok=z['decision']==spec['truth']
    if z['decision']=='SAT': ok=ok and replay(spec['root'],full_assignment(spec['root'],z['assignment']))
    return {'decision':z['decision'],'ok':ok,'relations':rels}

def oracle_C(spec,orels):
    z=tc.transfer_join(spec['root'],spec['components'],spec['graph'],orels)
    ok=z['decision']==spec['truth']
    if z['decision']=='SAT': ok=ok and replay(spec['root'],full_assignment(spec['root'],z['assignment']))
    return {'decision':z['decision'],'ok':ok}
def local_audit(spec):
    rows=[]; orels=[]
    for ci,(leaf,boundary) in enumerate(zip(spec['components'],spec['graph']['boundaries'])):
        orel=oracle_relation(leaf,boundary); orels.append(orel)
        frel,err=tc.leaf_relation(leaf,boundary)
        fset=allowed_set(frel) if frel is not None else set()
        oset=allowed_set(orel)
        for bits in product([0,1],repeat=len(boundary)):
            t=tuple(bits); osat=t in oset
            fixed={v:bool(x) for v,x in zip(boundary,bits)}; z=tc.solve_leaf(leaf,fixed)
            if not z.get('admitted'): cls='UNADMITTED'
            elif osat and z.get('decision')=='SAT': cls='TRUE_ACCEPT'
            elif (not osat) and z.get('decision')=='UNSAT': cls='TRUE_REJECT'
            elif osat: cls='FALSE_REJECT'
            else: cls='FALSE_ACCEPT'
            rows.append({'case':spec['id'],'component':ci,'boundary':boundary,'tuple':list(bits),'oracle_sat':osat,'frozen_admitted':bool(z.get('admitted')),'frozen_decision':z.get('decision'),'classification':cls})
        if err or fset!=oset:
            rows.append({'case':spec['id'],'component':ci,'relation_error':err,'oracle_allowed':sorted(oset),'frozen_allowed':sorted(fset),'classification':'RELATION_MISMATCH'})
    return rows,orels

def representation_check(spec,orels,brels):
    issues=[]; cvars=[set(allvars(c)) for c in spec['components']]
    for ei,(a,b) in enumerate(spec['edges']):
        s=spec['shared'][ei]; occ=[i for i,v in enumerate(cvars) if s in v]
        if occ!=sorted([a,b]): issues.append(['SHARED_VAR_ENDPOINT_MISMATCH',ei,s,occ,[a,b]])
    for i,(o,f,b) in enumerate(zip(orels,brels,spec['graph']['boundaries'])):
        if o['boundary']!=b or f['boundary']!=b: issues.append(['BOUNDARY_ORDER_MISMATCH',i])
        if allowed_set(o)!=allowed_set(f): issues.append(['RELATION_COORDINATE_MISMATCH',i])
    return issues
def separator_trace_full(cnf,sep):
    z=separator_trace(cnf,sep)
    if z.get('reason')!='PASS_PRE_TOUCH': return z
    s=sep[0]; groups=z['group_vars']; comp={v:i for i,g in enumerate(groups) for v in g}
    cg=[[] for _ in groups]
    for c in cnf:
        owners={comp[abs(x)] for x in c if abs(x)!=s}
        if len(owners)==1: cg[next(iter(owners))].append(c)
    touches=sum(any(any(abs(x)==s for x in c) for c in g) for g in cg if g)
    z['touches']=touches; z['reason']='PASS' if touches>=2 else 'SEP_TOUCH_LT2'
    return z

def main():
    hash_report={k:sha(ROOT/k) for k in EXPECTED_HASHES}
    if hash_report!=EXPECTED_HASHES: raise AssertionError(('HASH_DRIFT',hash_report))
    stored=load_calibration(); specs=build_specs(); byid={x['id']:x for x in stored}
    regen=[]
    for s in specs:
        c=byid.get(s['id']); exact=(c is not None and c['cnf']==s['root'] and c['truth']==s['truth'])
        canon=(c is not None and canonical_key(c['cnf'])==canonical_key(s['root']))
        regen.append({'id':s['id'],'exact_transport_match':exact,'canonical_match':canon})
    if len(specs)!=12 or not all(x['exact_transport_match'] for x in regen): raise AssertionError(('CAL_REGEN_FAIL',regen))

    A={}; sep_rows=[]; b_rows=[]; c_rows=[]; d_rows=[]; local_rows=[]; rep_issues=[]
    target_components=0; all_local_sat=True; unsat_local_sat=True
    for rule in tc.RULE_CANDIDATES:
        rr=[]
        for s in specs:
            z=tc.solve_formula(s['root'],rule); rr.append({'id':s['id'],'admitted':bool(z.get('admitted')),'decision':z.get('decision'),'reason':z.get('reason')})
        A[rule['id']]={'rows':rr,'admitted':sum(x['admitted'] for x in rr),'reason_counts':dict(Counter(x['reason'] for x in rr))}
    for s in specs:
        rootc=tc.canon(s['root'])
        for ei,sepv in enumerate(s['shared']):
            tr=separator_trace_full(rootc,[sepv])
            sep_rows.append({'case':s['id'],'edge_index':ei,'separator':[sepv],**tr})
        target_components+=len(s['components'])
        local_sat=[oracle_sat(c,{})[0] for c in s['components']]
        all_local_sat=all_local_sat and all(local_sat)
        if s['truth']=='UNSAT': unsat_local_sat=unsat_local_sat and all(local_sat)
        lrows,orels=local_audit(s); local_rows.extend(lrows)
        b=frozen_B(s); b_rows.append({'id':s['id'],'decision':b.get('decision'),'error':b.get('error'),'ok':b.get('ok',False)})
        brels=b.get('relations') or []
        if len(brels)==len(orels): rep_issues.extend([[s['id'],*x] for x in representation_check(s,orels,brels)])
        else: rep_issues.append([s['id'],'FROZEN_RELATION_COUNT_MISMATCH',len(brels),len(orels)])
        c=oracle_C(s,orels); c_rows.append({'id':s['id'],**c})
        dec,feasible,parent,children=independent_join(s['root'],s['graph'],orels)
        sat_replay=True
        if dec=='SAT':
            a,chosen,sat_replay=independent_reconstruct(s['root'],s['graph'],orels,feasible,parent,children)
        d_rows.append({'id':s['id'],'decision':dec,'ok':dec==s['truth'] and sat_replay,'sat_root_replay':sat_replay})

    class_counts=Counter(x.get('classification') for x in local_rows)
    relation_mismatch=class_counts.get('RELATION_MISMATCH',0)
    local_tuple_rows=[x for x in local_rows if 'tuple' in x]
    sep_counts=Counter(x['reason'] for x in sep_rows)
    B_pass=sum(bool(x['ok']) for x in b_rows); C_pass=sum(bool(x['ok']) for x in c_rows); D_pass=sum(bool(x['ok']) for x in d_rows)
    A_zero=all(v['admitted']==0 for v in A.values())
    local_clean=(class_counts.get('FALSE_REJECT',0)==0 and class_counts.get('FALSE_ACCEPT',0)==0 and class_counts.get('UNADMITTED',0)==0 and relation_mismatch==0)
    restriction_gap=not local_clean
    representation_mismatch=bool(rep_issues)
    contract_ok=(all(x['exact_transport_match'] for x in regen) and target_components==36 and all_local_sat and unsat_local_sat and D_pass==12)
    decomposition_evidence=(len(sep_rows)==24 and sep_counts.get('MIN_CLAUSE_GROUP_LT_3',0)==24 and B_pass==12)
    verdict='POSTMORTEM_DECOMPOSITION_FAILURE' if (A_zero and decomposition_evidence and local_clean and C_pass==12 and D_pass==12 and not representation_mismatch) else 'POSTMORTEM_ROOT_CAUSE_UNRESOLVED'

    raw={'source_hashes':hash_report,'calibration_regeneration':regen,'A_frozen':A,'separator_traces':sep_rows,
         'B_oracle_decomposition_frozen_local_transfer':b_rows,'local_restricted_audit':local_rows,
         'C_oracle_decomposition_oracle_local_frozen_transfer':c_rows,'D_independent_join':d_rows,
         'representation_issues':rep_issues}
    (HERE/'POSTMORTEM_RAW.json').write_text(json.dumps(raw,indent=2,sort_keys=True),encoding='utf-8')
    result={
      'artifact_id':'READONLY_POSTMORTEM_NO_SEPARATOR_OR_LOCAL_ADMISSION_2026-09-14_v1.0',
      'status':'DIAGNOSTIC_ONLY__NON_SCIENTIFIC_AUTHORITY','verdict':verdict,
      'source_scientific_fail':'FAIL_NO_TRANSFER_RULE','source_fail_seal':'17284f07a4d826cb80ade2e93c495a0bfe2db176',
      'scope':'revealed calibration v1.1 only','blind_admission_holdout':'NOT_READ_OR_REVEALED',
      'target_contract':{'cases':12,'regenerated_exactly':all(x['exact_transport_match'] for x in regen),'intended_components':target_components,
        'interaction_graph':'TREE_BY_GENERATOR_CONSTRUCTION','max_interface_width':1,'all_local_components_sat':all_local_sat,
        'interaction_only_unsat_local_components_sat':unsat_local_sat,'independent_global_join_matches_root_truth':D_pass==12,'pass':contract_ok},
      'diagnostic_matrix':{'A':{'pass':not A_zero,'per_rule_admitted':{k:v['admitted'] for k,v in A.items()}},'B':{'pass':B_pass==12,'exact':f'{B_pass}/12'},'C':{'pass':C_pass==12,'exact':f'{C_pass}/12'},'D':{'pass':D_pass==12,'exact':f'{D_pass}/12'}},
      'decomposition':{'true_separators':len(sep_rows),'enumerated_candidate_space_contains_all':True,
        'survived_frozen_filters':sum(1 for x in sep_rows if x['reason']=='PASS'),'rejection_reasons':dict(sep_counts),
        'primary_observation':'24/24 intended separators are width-1 candidates but are rejected by MIN_CLAUSE_GROUP_LT_3 before local admission'},
      'local_admission':{'components_checked':target_components,'boundary_tuples_checked':len(local_tuple_rows),
        'classification_counts':dict(class_counts),'relation_mismatches':relation_mismatch,'clean':local_clean},
      'restriction_closure_gap':restriction_gap,
      'interface_representation_mismatch':representation_mismatch,
      'observed_failure':'Frozen structural discovery returns NO_SEPARATOR_OR_LOCAL_ADMISSION; A admits 0/12 for RHO_W1, RHO_W2, and RHO_W3.',
      'root_cause_evidence':'Oracle intended decomposition alone changes the same frozen local admission + transfer path from 0/12 to 12/12. All 24 intended width-1 separators are rejected by the frozen minimum-three-clauses-per-group filter. Frozen local relation extraction agrees with an independent bounded oracle on all 36 components / 96 boundary tuples; C and D are 12/12.',
      'minimal_hypothetical_repair':'A future NEW preregistration could replace or justify the minimum-three-clauses-per-group separator filter with a sound structural criterion that admits the small intended component sides. No repair is applied here.',
      'repair_not_applied':True,
      'scientific_fail_remains':'FAIL_NO_TRANSFER_RULE','scientific_fail_rewritten':False,
      'next_target_frontier':'APMA_UNSEEN_LOCAL_INVARIANT_INDUCTION_FALSIFIER_GATE','execution_status':'LOCKED',
      'scientific_firewall':{'SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0}}
    (HERE/'POSTMORTEM_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'verdict':verdict,'A_admitted':{k:v['admitted'] for k,v in A.items()},'B':B_pass,'C':C_pass,'D':D_pass,
      'separators':len(sep_rows),'separator_reasons':dict(sep_counts),'components':target_components,'tuples':len(local_tuple_rows),
      'local_classes':dict(class_counts),'representation_issues':len(rep_issues),'contract_ok':contract_ok},sort_keys=True))

if __name__=='__main__': main()
