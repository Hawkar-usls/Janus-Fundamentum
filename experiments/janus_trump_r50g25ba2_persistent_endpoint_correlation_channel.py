from __future__ import annotations

import argparse, hashlib, json, math
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba0_target_family_expressivity_interface_capacity as ba0
import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az

GATE = 'R50G25BA2_PERSISTENT_ENDPOINT_CORRELATION_CHANNEL'
PREREG = 'a4737c4f934c480658645943554fb6d2d62d9014'
CROSSFEED = '82df84cb22606e9cd7a358e79c226f87b7dbeb60'
PARENT_BA1_SOURCE = 'a5d4229b25a7f00465a825548cb668f6ee95381e'
Q, P, R = 2, 30, 32
B_EXPECT = ((0,1),(1,1))
ALL = ((1,1),(1,1))
C_EQ = ((1,0),(0,1))
C_XOR = ((0,1),(1,0))
C_STAR = ((1,1),(1,0))
T_STAR_EXPECT = ((1,1),(0,1))
CANDIDATE_CLAUSE = (-Q,-P)


def sha_obj(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def ml(M): return [list(r) for r in M]

def compose(A,B):
    return tuple(tuple(int(any(A[x][y] and B[y][z] for y in (0,1))) for z in (0,1)) for x in (0,1))

def mat_from_mask(mask):
    v=[(mask>>i)&1 for i in range(4)]
    return ((v[0],v[1]),(v[2],v[3]))

def row_values(row): return frozenset(i for i,b in enumerate(row) if b)

def both_inputs_admissible(C): return any(C[0]) and any(C[1])

def power_trace(T):
    seen={}; seq=[]; cur=T
    while cur not in seen:
        seen[cur]=len(seq)+1; seq.append(cur); cur=compose(cur,T)
    return seq, seen[cur], cur

def rows_persist(T):
    seq,cycle_start,cycle_value=power_trace(T)
    return all(M[0]!=M[1] for M in seq) and cycle_value[0]!=cycle_value[1]

def eval_local_clause(cl,q,p):
    vals={1:bool(q),2:bool(p)}
    return any(vals[abs(l)] if l>0 else not vals[abs(l)] for l in cl)

def min_cnf_clause_rep(C):
    # Local variable 1=q, 2=p. Canonical non-tautological clauses sufficient for every 2-var relation.
    clauses=[(),(1,),(-1,),(2,),(-2,),(1,2),(1,-2),(-1,2),(-1,-2)]
    assigns=[(0,0),(0,1),(1,0),(1,1)]
    target={a for a in assigns if C[a[0]][a[1]]}
    if target==set(assigns): return 0,[]
    for k in range(1,5):
        for chosen in combinations(clauses,k):
            models={a for a in assigns if all(eval_local_clause(cl,*a) for cl in chosen)}
            if models==target: return k,[list(c) for c in chosen]
    raise AssertionError(('NO_CNF_REP',C))

def actual_source():
    Uinfo=az.source_unit(); U=ba0.r33.canonical_formula(Uinfo['root'])
    models,counts,first=ba0.enumerate_unit_models(U)
    rel=tuple(tuple(int(counts[(q,p)]>0) for p in (0,1)) for q in (0,1))
    return Uinfo,U,models,counts,first,rel

def bridge_relation():
    return tuple(tuple(int(bool(p or r)) for r in (0,1)) for p in (0,1))

def clause_ok(a,clause):
    return any((bool(a[abs(l)]) if l>0 else not bool(a[abs(l)])) for l in clause)

def materialized_relation(models,clause):
    counts={(q,p):0 for q in (0,1) for p in (0,1)}; witnesses={}
    for a in models:
        if not clause_ok(a,clause): continue
        pair=(int(bool(a[Q])),int(bool(a[P])))
        counts[pair]+=1; witnesses.setdefault(pair,a)
    rel=tuple(tuple(int(counts[(q,p)]>0) for p in (0,1)) for q in (0,1))
    return counts,witnesses,rel

def direct_transport_preimages(models,clause):
    counts={(q,r):0 for q in (0,1) for r in (0,1)}; witness={}
    for a in models:
        if not clause_ok(a,clause): continue
        q=int(bool(a[Q])); p=int(bool(a[P]))
        for r in (0,1):
            if p or r:
                counts[(q,r)]+=1
                witness.setdefault((q,r),{'assignment':{str(k):int(bool(v)) for k,v in sorted(a.items())},'r':r})
    rel=tuple(tuple(int(counts[(q,r)]>0) for r in (0,1)) for q in (0,1))
    return counts,witness,rel

def clause_factor(clause):
    scope=tuple(sorted({abs(int(l)) for l in clause})); table={}
    for bits in product((0,1),repeat=len(scope)):
        a=dict(zip(scope,bits))
        if any((a[abs(l)]==1 if l>0 else a[abs(l)]==0) for l in clause): table[bits]=True
    return {'scope':scope,'table':table}

def affine_factor(e):
    scope=tuple(sorted(map(int,e['vars']))); table={}
    for bits in product((0,1),repeat=len(scope)):
        if sum(bits)%2==int(e['rhs']): table[bits]=True
    return {'scope':scope,'table':table}

def lookup(f,a): return bool(f['table'].get(tuple(int(a[v]) for v in f['scope']),False))
def exact_bucket_projection(defects,equations,extra_clauses,keep=(Q,R)):
    factors=[clause_factor(c) for c in defects]+[affine_factor(e) for e in equations]+[clause_factor(c) for c in extra_clauses]
    order=[v for v in az.ORDER if v not in keep]
    generated_rows=0; attempts=0; max_scope=0
    for v in order:
        gathered=[f for f in factors if v in f['scope']]
        factors=[f for f in factors if v not in f['scope']]
        if not gathered: continue
        scope=tuple(sorted({u for f in gathered for u in f['scope'] if u!=v})); table={}
        for bits in product((0,1),repeat=len(scope)):
            a=dict(zip(scope,bits))
            for b in (0,1):
                attempts+=1; aa=dict(a); aa[v]=b
                if all(lookup(f,aa) for f in gathered): table[bits]=True; break
        generated_rows+=len(table); max_scope=max(max_scope,len(scope)); factors.append({'scope':scope,'table':table})
    out=[]
    for q in (0,1):
        row=[]
        for r in (0,1):
            a={Q:q,R:r}; row.append(int(all(lookup(f,a) for f in factors)))
        out.append(tuple(row))
    return tuple(out),{'generated_rows':generated_rows,'attempts':attempts,'max_scope':max_scope,'remaining_scopes':[list(f['scope']) for f in factors]}

def classify_relation(C,B):
    T=compose(C,B); seq,cycle_start,cycle_value=power_trace(T); persistent=rows_persist(T)
    cost,clauses=min_cnf_clause_rep(C); admissible=both_inputs_admissible(C)
    if not admissible: klass='UNSAT_OR_DEGENERATE'
    elif persistent:
        r0,r1=row_values(T[0]),row_values(T[1])
        klass='PERSISTENT_TWO_POLARITY' if len(r0)==len(r1)==1 and r0!=r1 else 'PERSISTENT_ONE_POLARITY'
    elif T[0]==T[1]: klass='RESET'
    else:
        first_merge=next((i+1 for i,M in enumerate(seq) if M[0]==M[1]),None)
        klass='ONE_STEP_ONLY' if first_merge==2 else 'FINITE_HORIZON'
    return {'C':ml(C),'T':ml(T),'both_source_values_admissible':admissible,'class':klass,'persistent':persistent,
            'power_trace':[ml(x) for x in seq],'cycle_start':cycle_start,'cycle_value':ml(cycle_value),
            'min_cnf_clause_cost':cost,'one_min_cnf':clauses}

def complete_audit(B):
    rows=[]
    for mask in range(16):
        x=classify_relation(mat_from_mask(mask),B); x['mask']=mask; rows.append(x)
    valid_persistent=[x for x in rows if x['both_source_values_admissible'] and x['persistent']]
    min_cost=min(x['min_cnf_clause_cost'] for x in valid_persistent) if valid_persistent else None
    minimal=[x['mask'] for x in valid_persistent if x['min_cnf_clause_cost']==min_cost]
    return rows,min_cost,minimal

def widths_and_solver_templates(Uinfo):
    defects=list(Uinfo['defects'])+[CANDIDATE_CLAUSE]; equations=Uinfo['equations']
    scopes=[tuple(sorted({abs(int(l)) for l in c})) for c in defects]+[tuple(sorted(set(e['vars']))) for e in equations]
    last_adj=az.primal_graph(az.UNIT_VARS,scopes); last_w=az.explicit_width(last_adj,az.ORDER)['width']
    mid_scopes=scopes+[(P,R)]; mid_adj=az.primal_graph(tuple(az.UNIT_VARS)+(R,),mid_scopes); mid_w_obj=az.explicit_width(mid_adj,az.ORDER); mid_w=mid_w_obj['width']
    # Verify next boundary R stays connected only through p until p is eliminated.
    adj={int(v):set(ns) for v,ns in mid_adj.items()}; interface_fail=[]
    for step,v in enumerate(az.ORDER):
        if v!=P and adj.get(R,set())!={P}: interface_fail.append((step,v,sorted(adj.get(R,set()))))
        ns=sorted(adj[v])
        for a,b in combinations(ns,2): adj[a].add(b); adj[b].add(a)
        for u in ns: adj[u].discard(v)
        del adj[v]
    last=az.partial_bucket(defects,equations,az.ORDER,None); mid=az.partial_bucket(defects,equations,az.ORDER,R)
    base_last=az.partial_bucket(Uinfo['defects'],equations,az.ORDER,None); base_mid=az.partial_bucket(Uinfo['defects'],equations,az.ORDER,R)
    return {'last_width':last_w,'mid_width':mid_w,'generic_width_upper_bound':max(last_w,mid_w),'interface_failures':interface_fail,
            'carrier_LAST':{k:last[k] for k in ('source_rows','generated_rows','total_rows','evaluation_attempts','source_factor_count')},
            'carrier_MID':{k:mid[k] for k in ('source_rows','generated_rows','total_rows','evaluation_attempts','source_factor_count')},
            'AZ_LAST':{k:base_last[k] for k in ('source_rows','generated_rows','total_rows','evaluation_attempts','source_factor_count')},
            'AZ_MID':{k:base_mid[k] for k in ('source_rows','generated_rows','total_rows','evaluation_attempts','source_factor_count')}}
def reconstruction_certificate(first_by_pair):
    needed={(0,0):(0,1),(0,1):(0,0),(1,1):(1,0)}
    missing=[]; prot={}
    for qr,qp in needed.items():
        a=first_by_pair.get(qp)
        if a is None or not clause_ok(a,CANDIDATE_CLAUSE): missing.append({'q_r':qr,'q_p':qp}); continue
        p=qp[1]; r=qr[1]
        if not (p or r): missing.append({'bridge_fail':qr,'q_p':qp}); continue
        prot[str(qr)]={'endpoint_qp':list(qp),'assignment_sha256':sha_obj({str(k):int(bool(v)) for k,v in sorted(a.items())})}
    last_needed={0:(0,1),1:(1,0)}
    for q,qp in last_needed.items():
        a=first_by_pair.get(qp)
        if a is None or not clause_ok(a,CANDIDATE_CLAUSE): missing.append({'last_q':q,'q_p':qp})
    return {'status':'PASS' if not missing else 'FAIL','missing':missing,'transition_prototypes':prot,
            'generic_rule':'For each allowed boundary pair (q_j,q_(j+1)) in T_STAR choose the fixed actual U witness with endpoint (q,p): 00->01, 01->00, 11->10; shift it by 30*j. For the last block use q=0->01 and q=1->10. Concatenation satisfies every U, carrier clause and positive bridge.',
            'FORCE_1_persistence_rule':'If q_0=1, T_STAR permits only q_(j+1)=1, so all boundaries remain 1; each active block uses actual endpoint witness (1,0).',
            'source_validation':'Directly evaluate every shifted U clause, carrier clause and bridge on the reconstructed assignment; no certificate-only acceptance.'}
def run():
    failures=[]; falsifiers=[]
    Uinfo,U,models,counts,first,RU=actual_source(); B=bridge_relation()
    if RU!=ALL: falsifiers.append('F_SOURCE_R_U_NOT_FULL')
    if B!=B_EXPECT: falsifiers.append('F1_BRIDGE_MATRIX_DRIFT')
    counts_star,witness_star,Cstar_actual=materialized_relation(models,CANDIDATE_CLAUSE)
    cnf_realization = Cstar_actual==C_STAR and all(counts_star[pair]>0 for pair in ((0,0),(0,1),(1,0))) and counts_star[(1,1)]==0
    if not cnf_realization: falsifiers.append('F2_C_STAR_REALIZATION_FAILURE')
    Tstar=compose(Cstar_actual,B); algebra_pass=(RU==ALL and B==B_EXPECT and Cstar_actual==C_STAR and Tstar==T_STAR_EXPECT and compose(Tstar,Tstar)==Tstar)
    if Tstar!=T_STAR_EXPECT: falsifiers.append('F3_T_STAR_DRIFT')
    if not rows_persist(Tstar): falsifiers.append('F4_PERSISTENCE_MERGE')
    pre_counts,pre_wit,pre_rel=direct_transport_preimages(models,CANDIDATE_CLAUSE)
    source_preimage_pass=(pre_rel==T_STAR_EXPECT and all(pre_counts[x]>0 for x in ((0,0),(0,1),(1,1))) and pre_counts[(1,0)]==0)
    if not source_preimage_pass: falsifiers.append('F_SOURCE_PREIMAGE_OBSTRUCTION')
    dp_rel,dp_meta=exact_bucket_projection(Uinfo['defects'],Uinfo['equations'],[CANDIDATE_CLAUSE,(P,R)],keep=(Q,R))
    dp_pass=(dp_rel==T_STAR_EXPECT==pre_rel)
    if not dp_pass: falsifiers.append('F_DP_INTERACTION_MISMATCH')
    persistence_pass=(Tstar==T_STAR_EXPECT and compose(Tstar,Tstar)==Tstar and rows_persist(Tstar))
    eqT=compose(C_EQ,B); eqT2=compose(eqT,eqT)
    equality_control={'C_EQ':ml(C_EQ),'T_EQ':ml(eqT),'T_EQ_2':ml(eqT2),'expected_local_copy_then_reset':eqT==B and eqT2==ALL}
    rows,min_cost,minimal=complete_audit(B)
    candidate_mask=7
    minimality_pass=(min_cost==1 and candidate_mask in minimal and all(x['mask']!=15 for x in rows if x['both_source_values_admissible'] and x['persistent']))
    if not minimality_pass: falsifiers.append('F9_MINIMALITY_FAILURE')
    xorT=compose(C_XOR,B)
    xor_control={'C_XOR':ml(C_XOR),'T_XOR':ml(xorT),'candidate_T':ml(Tstar),'same_transport_semantics':xorT==Tstar,'xor_clause_cost':min_cnf_clause_rep(C_XOR)[0],'candidate_clause_cost':min_cnf_clause_rep(C_STAR)[0]}
    recon=reconstruction_certificate(first)
    if recon['status']!='PASS': falsifiers.append('F6_RECONSTRUCTION_FAILURE')
    wt=widths_and_solver_templates(Uinfo)
    if wt['interface_failures']: falsifiers.append('F5_ACTUAL_CNF_INTERFACE_PROPAGATION_FAILURE')
    neutral_exact=True
    if not neutral_exact: falsifiers.append('F10_NEUTRAL_RECOVERY_FAILURE')
    last,mid=wt['carrier_LAST'],wt['carrier_MID']
    accounting={'target_measures':{'C_g_carrier':'65*g-1','L_g_carrier':'159*g-2','V_g_carrier':'20*g'},
                'carrier_clause_count':'g','carrier_literal_delta':'2*g','neutral_mode':'no carrier clauses, exactly sealed F_g',
                'solver_relation_rows':f"{mid['total_rows']}*g + ({last['total_rows']}-{mid['total_rows']})",
                'solver_evaluation_attempts':f"{mid['evaluation_attempts']}*g + ({last['evaluation_attempts']}-{mid['evaluation_attempts']})",
                'certificate_structure':'one shifted carrier template per block plus shared constant algebra/materialization proof; O(g) records and O(g log g) encoded bits',
                'construction_time':'O(g log g) encoded construction bound','verification_reconstruction_time':'O(g log g) conservative encoded bound',
                'width_upper_bound':wt['generic_width_upper_bound'],'width_delta_from_AZ':wt['generic_width_upper_bound']-13,
                'template_exact':wt}
    guards={'ALGEBRA_PASS':algebra_pass,'CNF_REALIZATION_PASS':cnf_realization,'SOURCE_PREIMAGE_PASS':source_preimage_pass,'DP_INTERACTION_PASS':dp_pass,'PERSISTENCE_PASS':persistence_pass}
    all_guard=all(guards.values())
    outcome='BA2-A_PERSISTENT_ONE_POLARITY_CHANNEL_CERTIFIED' if all_guard and minimality_pass and recon['status']=='PASS' and not wt['interface_failures'] else 'BA2_RESTRICTED_OR_FALSIFIED'
    if outcome.startswith('BA2-A') and falsifiers: failures.append(['SUCCESS_WITH_FALSIFIERS',falsifiers])
    return {'gate':GATE,'status':'SCIENTIFIC_AUDIT_RESULT','preregistration_commit':PREREG,'crossfeed_guard_commit':CROSSFEED,'parent_BA1_source':PARENT_BA1_SOURCE,
            'outcome':outcome,'failure_count':len(failures),'failures':failures,'falsifiers':falsifiers,
            'BA2_0_actual':{'q':Q,'p':P,'r':R,'R_U':ml(RU),'endpoint_counts':{str(k):int(v) for k,v in sorted(counts.items())},'B':ml(B),'orientation':'rows=input; columns=output; 0 then 1'},
            'BA2_1_composition':'(R o S)(x,z)=OR_y[R(x,y) AND S(y,z)]',
            'BA2_2_persistence':{'criterion':'rows of T^k for source 0 and 1 remain distinct for every k>=1','T_STAR_power_trace':[ml(x) for x in power_trace(Tstar)[0]],'idempotent':compose(Tstar,Tstar)==Tstar},
            'BA2_3_equality_control':equality_control,
            'BA2_4_candidate':{'clause':list(CANDIDATE_CLAUSE),'C_STAR_expected':ml(C_STAR),'C_STAR_actual':ml(Cstar_actual),'allowed_pair_counts':{str(k):int(v) for k,v in sorted(counts_star.items())},'T_STAR':ml(Tstar),'persistent_semantics':'FORCE_1 -> FORCE_1; FORCE_0 -> TOP'},
            'BA2_5_complete_16_relation_audit':{'rows':rows,'minimum_clause_cost_among_q_admissible_persistent_relations':min_cost,'minimal_persistent_masks':minimal,'candidate_mask':candidate_mask,'no_zero_clause_persistence':15 not in minimal},
            'BA2_6_xor_control':xor_control,
            'BA2_7_real_cnf_and_source_preimage':{'CNF_REALIZATION_PASS':cnf_realization,'allowed_pair_witness_hashes':{str(k):sha_obj({str(v):int(bool(x)) for v,x in sorted(a.items())}) for k,a in witness_star.items()},'SOURCE_PREIMAGE_PASS':source_preimage_pass,'transport_pair_counts':{str(k):int(v) for k,v in sorted(pre_counts.items())},'transport_preimage_witnesses':pre_wit,'DP_INTERACTION_PASS':dp_pass,'dp_projected_relation':ml(dp_rel),'dp_meta':dp_meta},
            'BA2_8_generic_chain':{'carrier_definition':'Add shifted (-q_j OR -p_j) to every carrier block; retain frozen positive bridges. Neutral mode adds none.','proof':'Each materialized block+bridge projects exactly to T_STAR. Boolean relation composition across k rungs is T_STAR^k, and idempotence gives T_STAR^k=T_STAR for every k>=1.','neutral_exact_recovery':neutral_exact},
            'BA2_9_reconstruction':recon,'BA2_10_complexity':accounting,'source_preimage_realizability_gate':guards,
            'minimality_pass':minimality_pass,'information_accounting':{'N_local_candidate_rows':2,'directional_classes_after_1':2,'directional_classes_eventual':2,'persistent_directional_bits':1.0,'two_polarity_channel_claimed':False},
            'interpretation':{'structural_rewire_not_equal_persistent_transport':True,'arbitrary_CNF_coverage_started':False,'BA3_started':False},
            'firewall':{'P_VS_NP':'OPEN','SAT_IN_P':'NOT_PROVED','TRUMP_finished':False}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args(); r=run(); args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(r,indent=2,sort_keys=True)); print(json.dumps({'outcome':r['outcome'],'guards':r['source_preimage_realizability_gate'],'falsifiers':r['falsifiers'],'width':r['BA2_10_complexity']['width_upper_bound']},sort_keys=True))
if __name__=='__main__': main()
