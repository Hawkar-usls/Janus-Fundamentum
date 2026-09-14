from __future__ import annotations
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'trump_apma_compositional_synthesis'
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(PREV))
import transfer_core as tc
import core as oldcore
import independent_checker as oldcheck

def canon(raw):
    out=set()
    for c in raw:
        s=set(int(x) for x in c)
        if any(-x in s for x in s): continue
        out.add(tuple(sorted(s,key=lambda z:(abs(z),z<0))))
    return [list(c) for c in sorted(out,key=lambda c:(len(c),tuple((abs(x),x<0) for x in c)))]

def replay(raw,a):
    return all(any((x>0 and bool(a.get(abs(x),a.get(str(abs(x)),False)))) or (x<0 and not bool(a.get(abs(x),a.get(str(abs(x)),False)))) for x in c) for c in raw)

def condition(raw,fixed):
    cnf=canon(raw); a={int(k):bool(v) for k,v in fixed.items()}
    while True:
        nxt=[]
        for c in cnf:
            sat=False; rem=[]
            for lit in c:
                v=abs(lit)
                if v in a:
                    if a[v]==(lit>0): sat=True; break
                else: rem.append(lit)
            if sat: continue
            if not rem: return {'status':'CONTRADICTION','assignment':a,'residual':[]}
            nxt.append(rem)
        cnf=canon(nxt); unit=next((c[0] for c in cnf if len(c)==1),None)
        if unit is None: return {'status':'OK','assignment':a,'residual':cnf}
        v=abs(unit); val=unit>0
        if v in a and a[v]!=val: return {'status':'CONTRADICTION','assignment':a,'residual':cnf}
        a[v]=val

def tuple_map(boundary,tup): return {int(v):bool(b) for v,b in zip(boundary,tup)}

def verify_relation_entry(leaf,boundary,entry,allowed):
    fixed=tuple_map(boundary,entry['tuple']); cert=entry.get('certificate') or {}
    if allowed:
        w={int(k):bool(v) for k,v in (entry.get('witness') or {}).items()}
        return all(w.get(v)==val for v,val in fixed.items()) and replay(leaf,w)
    cond=condition(leaf,fixed)
    if cert.get('kind')=='condition_contradiction': return cond['status']=='CONTRADICTION'
    if cert.get('kind')!='primitive_unsat' or cond['status']!='OK': return False
    slot=cert.get('primitive_slot')
    if not isinstance(slot,int) or not (0<=slot<4): return False
    z={'decision':'UNSAT','certificate':cert.get('residual_certificate')}
    return oldcheck.VER[slot](cond['residual'],z)

def verify_transfer(raw,z,rule):
    if not z.get('admitted') or z.get('decision') not in ('SAT','UNSAT'): return False,'NOT_ADMITTED'
    cert=z.get('certificate') or {}
    if cert.get('kind')!='rho_tree_transfer' or cert.get('rule_id')!=rule['id']: return False,'BAD_CERT_HEADER'
    leaves=cert.get('leaves') or []; relations=cert.get('relations') or []
    if len(leaves)!=len(relations) or not leaves: return False,'LEAF_RELATION_COUNT'
    rootset={tuple(c) for c in canon(raw)}; leafset=[]
    for leaf in leaves: leafset.extend(tuple(c) for c in canon(leaf))
    if len(leafset)!=len(set(leafset)) or set(leafset)!=rootset: return False,'CLAUSE_PARTITION'
    vsets=[{abs(x) for c in leaf for x in c} for leaf in leaves]; edges=[]; adj={i:[] for i in range(len(leaves))}
    for i in range(len(leaves)):
        for j in range(i+1,len(leaves)):
            s=sorted(vsets[i]&vsets[j])
            if s:
                if len(s)>int(rule['max_separator_width']): return False,'WIDTH'
                edges.append((i,j,s)); adj[i].append((j,s)); adj[j].append((i,s))
    seen={0}; q=[0]
    while q:
        u=q.pop()
        for v,_ in adj[u]:
            if v not in seen: seen.add(v); q.append(v)
    if len(seen)!=len(leaves) or len(edges)!=len(leaves)-1: return False,'NOT_TREE'
    boundaries=[]
    for i in range(len(leaves)):
        b=sorted(set().union(*(set(s) for _,s in adj[i])) if adj[i] else set())
        if len(b)>3: return False,'BOUNDARY_GT3'
        boundaries.append(b)
    for i,(leaf,rel,b) in enumerate(zip(leaves,relations,boundaries)):
        if list(rel.get('boundary',[]))!=b: return False,f'BOUNDARY_MISMATCH_{i}'
        allowed=rel.get('allowed') or []; forbidden=rel.get('forbidden') or []
        tuples=[tuple(x.get('tuple',[])) for x in allowed+forbidden]
        expected=set(product([0,1],repeat=len(b)))
        if len(tuples)!=len(set(tuples)) or set(tuples)!=expected: return False,f'TUPLE_COVER_{i}'
        if not all(verify_relation_entry(leaf,b,e,True) for e in allowed): return False,f'SAT_LOCAL_EVIDENCE_{i}'
        if not all(verify_relation_entry(leaf,b,e,False) for e in forbidden): return False,f'UNSAT_LOCAL_EVIDENCE_{i}'
    parent={0:None}; order=[0]
    for u in order:
        for v,_ in adj[u]:
            if v not in parent: parent[v]=u; order.append(v)
    children={u:[v for v,_ in adj[u] if parent.get(v)==u] for u in range(len(leaves))}; feasible={}
    for u in reversed(order):
        good=[]
        for e in relations[u]['allowed']:
            amap=tuple_map(boundaries[u],e['tuple']); ok=True
            for ch in children[u]:
                sep=next(s for v,s in adj[u] if v==ch); found=False
                for ce in feasible[ch]:
                    cmap=tuple_map(boundaries[ch],ce['tuple'])
                    if all(amap[x]==cmap[x] for x in sep): found=True; break
                if not found: ok=False; break
            if ok: good.append(e)
        feasible[u]=good
    independent_decision='SAT' if feasible[0] else 'UNSAT'
    if independent_decision!=z['decision']: return False,'GLOBAL_RELATION_DECISION'
    if z['decision']=='SAT' and not replay(raw,{int(k):bool(v) for k,v in (z.get('assignment') or {}).items()}): return False,'ROOT_REPLAY'
    return True,'OK'

def fingerprint_from_hidden(meta):
    return tuple(sorted(int(x) for x in meta['kinds']))

def local_and_prediction(cnf,rule):
    leaves,err=tc.discover_leaves(cnf,int(rule['max_separator_width']))
    if err: return None
    dec=[]
    for leaf in leaves:
        z=tc.solve_leaf(leaf,{})
        if not z.get('admitted'): return None
        dec.append(z['decision'])
    return 'UNSAT' if 'UNSAT' in dec else 'SAT'

def main():
    rho=json.loads((ROOT/'FROZEN_RHO.json').read_text(encoding='utf-8')); payload=dict(rho); bundle=payload.pop('bundle_sha256'); bundle_ok=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()==bundle
    rule=rho['selected_rule']; rule_hash_ok=tc.rule_hash(rule)==rho['selected_rule_hash']
    cal=json.loads((ROOT/'calibration.json').read_text(encoding='utf-8'))['cases']; adm=json.loads((ROOT/'sealed_admission.json').read_text(encoding='utf-8'))['cases']; hol=json.loads((ROOT/'sealed_holdout.json').read_text(encoding='utf-8'))['cases']; controls=json.loads((ROOT/'sealed_controls.json').read_text(encoding='utf-8'))['cases']; truth=json.loads((ROOT/'sealed_truth.json').read_text(encoding='utf-8'))
    core_src=(ROOT/'transfer_core.py').read_text(encoding='utf-8').lower(); synth_src=(ROOT/'synthesizer.py').read_text(encoding='utf-8').lower()
    forbidden=['g00','g11','g22','g33','run_program(','sealed_admission','sealed_holdout','sealed_truth','hidden_meta','matching_component','scc_component','propagation_component','linear_component']
    source_hits=[x for x in forbidden if x in core_src or x in synth_src]
    targets=[]; split_counts={'admission':0,'holdout':0}; failures=[]; timing=defaultdict(float); leaf_counts=[]
    for split,cases in [('admission',adm),('holdout',hol)]:
        for case in cases:
            gt=truth['targets'][case['id']]['truth']; z=tc.solve_formula(case['cnf'],rule); vok,vreason=verify_transfer(case['cnf'],z,rule) if z.get('admitted') else (False,z.get('reason','NOT_ADMITTED'))
            ok=z.get('admitted') and z.get('decision')==gt and vok
            if ok: split_counts[split]+=1
            else: failures.append([split,case['id'],gt,z.get('decision'),z.get('admitted'),vreason,z.get('reason')])
            for k,v in (z.get('timing') or {}).items(): timing[k]+=float(v)
            if z.get('leaf_count') is not None: leaf_counts.append(z['leaf_count'])
            targets.append({'id':case['id'],'split':split,'truth':gt,'decision':z.get('decision'),'admitted':bool(z.get('admitted')),'independent_verify':vok,'verify_reason':vreason,'leaf_count':z.get('leaf_count'),'timing':z.get('timing')})
    old_programs={p['id']:p for p in oldcore.grammar() if p['id'] in ('G00','G11','G22','G33')}; old_admissions=[]
    for case in adm+hol:
        for gid,p in old_programs.items():
            z=oldcore.run_program(case['cnf'],p)
            if z.get('admitted'): old_admissions.append([case['id'],gid,z.get('decision')])
    local_records=[]; local_misses_unsat=0
    for case in adm+hol:
        gt=truth['targets'][case['id']]['truth']; pred=local_and_prediction(case['cnf'],rule); local_records.append([case['id'],gt,pred]); local_misses_unsat+=int(gt=='UNSAT' and pred!='UNSAT')
    train=defaultdict(Counter)
    for case in cal:
        meta=truth['targets'][case['id']]['hidden_meta']; train[fingerprint_from_hidden(meta)][truth['targets'][case['id']]['truth']]+=1
    fp_records=[]; fp_correct=0
    for case in adm+hol:
        gt=truth['targets'][case['id']]['truth']; fp=fingerprint_from_hidden(truth['targets'][case['id']]['hidden_meta']); cnt=train.get(fp,Counter()); pred='SAT' if cnt['SAT']>=cnt['UNSAT'] else 'UNSAT'; fp_correct+=int(pred==gt); fp_records.append([case['id'],gt,pred,list(fp)])
    control_records=[]; control_fail=[]
    for case in controls:
        z=tc.solve_formula(case['cnf'],rule); rec={'id':case['id'],'control':case['control'],'admitted':bool(z.get('admitted')),'decision':z.get('decision'),'reason':z.get('reason')}; control_records.append(rec)
        if z.get('admitted'): control_fail.append(rec)
    hold_encoder_ok=all(c.get('encoder')=='hold_encoder_v6' for c in hol) and all(c.get('encoder')!='hold_encoder_v6' for c in cal)
    hold_ks=sorted({len(truth['targets'][c['id']]['hidden_meta']['kinds']) for c in hol}); admission_ks=sorted({len(truth['targets'][c['id']]['hidden_meta']['kinds']) for c in adm})
    pop=json.loads((ROOT/'POPULATION_AUDIT.json').read_text(encoding='utf-8')); pair_metrics_ok=bool(pop.get('all_pair_metrics_equal'))
    required_topologies={'long_path','balanced_binary_tree','irregular_degree_leq3','broom_star_like_degree_leq3'}; seen_topologies={x['topology'] for x in pop['pair_audit'] if str(x['pair_id']).startswith(('adm-','hold-','v12-adm-','v12-hold-'))}; topology_coverage=required_topologies.issubset(seen_topologies)
    if not bundle_ok or not rule_hash_ok or source_hits: verdict='FAIL_POLYNOMIAL_BUDGET'
    elif old_admissions: verdict='FAIL_OLD_CARRIER_COLLAPSE'
    elif local_misses_unsat==0: verdict='FAIL_LOCAL_AND_BASELINE'
    elif failures: verdict='FAIL_GLOBAL_EXACTNESS'
    elif not hold_encoder_ok: verdict='FAIL_ENCODER_TRANSFER'
    elif not topology_coverage: verdict='FAIL_TOPOLOGY_TRANSFER'
    elif control_fail: verdict='FAIL_SCOPE_REJECTION'
    else: verdict='PASS_SCOPED_NOVEL_COMPOSITE_SEMANTICS_TRANSFER'
    result={'artifact':'JANUS-TRUMP-APMA-NOVEL-COMPOSITE-SEMANTICS-TRANSFER-GATE-2026-09-14-v1.3','verdict':verdict,'rho':{'selected_rule':rule,'selected_rule_hash':rho['selected_rule_hash'],'bundle_integrity':bundle_ok,'rule_hash_integrity':rule_hash_ok},'source_firewall':{'forbidden_hits':source_hits,'synthesizer_reads_only_calibration':('calibration.json' in synth_src and 'sealed_' not in synth_src)},'target_exactness':{'counts':split_counts,'expected':{'admission':len(adm),'holdout':len(hol)},'failures':failures,'records':targets},'negative_baselines':{'OLD_CARRIER_WHOLE_INSTANCE_BASELINE':{'admissions':old_admissions,'pass':not old_admissions},'LOCAL_VERDICT_AND_BASELINE':{'interaction_only_unsat_misses':local_misses_unsat,'records':local_records,'required_to_fail':True,'pass':local_misses_unsat>0},'COMPONENT_MULTISET_FINGERPRINT_BASELINE':{'correct':fp_correct,'total':len(fp_records),'accuracy':fp_correct/len(fp_records) if fp_records else None,'records':fp_records,'note':'oracle-strength component inventory only; gluing omitted'}},'scope_controls':{'records':control_records,'failures':control_fail},'transfer_audit':{'admission_k':admission_ks,'holdout_k':hold_ks,'holdout_encoder_unseen':hold_encoder_ok,'pair_metrics_equal':pair_metrics_ok,'topologies_seen':sorted(seen_topologies),'topology_coverage':topology_coverage,'leaf_count_range':[min(leaf_counts),max(leaf_counts)] if leaf_counts else None},'timing_ms_sum':dict(timing),'complexity_ledger':{'normalize':'polynomial canonicalization','structure':'separator enumeration bounded at frozen w=1 for selected rho; O(n) candidate separators each with polynomial connectivity work','synthesis':'3 frozen candidate rules evaluated only on calibration; constant candidate count','component_relation':'boundary <=3, at most 8 tuples; each tuple uses lower-level polynomial exact primitive path','transfer':'tree DP over O(k) edges and <=8 tuples per local relation','certificate':'local SAT replay / lower-level UNSAT certificate plus relational elimination','reconstruction':'linear number of leaves plus root replay','timings_are_empirical_only':True},'scientific_firewall':{'COMPOSITE_TRANSFER':'PASS_SCOPED' if verdict.startswith('PASS_') else 'FAILED','NEW_LOCAL_INVARIANT_DISCOVERY':'NOT_CLAIMED','UNIVERSAL_DISCOVERY':'NOT_CLAIMED','SAT_IN_P':'NOT_PROVED','P_VS_NP':'OPEN','Pi_negative_evidence_weight':0,'UNSEEN_LOCAL_INVARIANT_INDUCTION':'LOCKED' if not verdict.startswith('PASS_') else 'ELIGIBLE_BUT_NOT_RUN'}}
    (ROOT/'checker_raw.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'verdict':verdict,'target_counts':split_counts,'failures':len(failures),'old_admissions':len(old_admissions),'local_unsat_misses':local_misses_unsat,'fingerprint_accuracy':result['negative_baselines']['COMPONENT_MULTISET_FINGERPRINT_BASELINE']['accuracy'],'control_failures':control_fail,'source_hits':source_hits,'rho':rule,'leaf_range':result['transfer_audit']['leaf_count_range']},sort_keys=True))
if __name__=='__main__': main()
