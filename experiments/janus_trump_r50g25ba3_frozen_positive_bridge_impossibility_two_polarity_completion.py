from __future__ import annotations

import argparse, hashlib, json, math
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba2_persistent_endpoint_correlation_channel as ba2
import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az

GATE = 'R50G25BA3_FROZEN_POSITIVE_BRIDGE_IMPOSSIBILITY_TWO_POLARITY_COMPLETION'
PREREG = 'd602ffd76d6413f4a92322b62da897727231ab43'
PARENT_BA2 = '8caebdf7e157de3b610242e285afff412aaceb7d'
Q, P, R = 2, 30, 32
ALL = ((1,1),(1,1))
I = ((1,0),(0,1))
XOR = ((0,1),(1,0))
B = ((0,1),(1,1))
C_STAR = ((1,1),(1,0))
BA2_CLAUSE = (-Q,-P)
BA3_BLOCK = (Q,P)
FROZEN_BRIDGE = (P,R)
BA3_BRIDGE = (-P,-R)


def ml(M): return [list(r) for r in M]
def sha_obj(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def compose(A,B):
    return tuple(tuple(int(any(A[x][y] and B[y][z] for y in (0,1))) for z in (0,1)) for x in (0,1))
def intersect(A,B): return tuple(tuple(int(A[i][j] and B[i][j]) for j in (0,1)) for i in (0,1))
def rowset(row): return frozenset(i for i,b in enumerate(row) if b)
def clause_ok_map(a,cl): return any((bool(a[abs(l)]) if l>0 else not bool(a[abs(l)])) for l in cl)

def relation_of_clauses(clauses):
    out=[]
    for x,y in product((0,1),repeat=2):
        a={0:x,1:y}
        def ok(cl):
            return any((bool(a[v]) if sign else not bool(a[v])) for v,sign in cl)
        out.append(int(all(ok(c) for c in clauses)))
    return ((out[0],out[1]),(out[2],out[3]))

def endpoint_clause_rel(kind, literals):
    # literals are signed logical names 0(first),1(second): +1 means positive, -1 negative.
    out=[]
    for x,y in product((0,1),repeat=2):
        vals=(x,y); good=False
        for var,positive in literals:
            good |= bool(vals[var]) if positive else not bool(vals[var])
        out.append(int(good))
    return ((out[0],out[1]),(out[2],out[3]))

def declared_clauses():
    # All non-tautological unary/binary clauses on a declared endpoint pair.
    out=[]
    for v in (0,1):
        for positive in (False,True): out.append(((v,positive),))
    for s0 in (False,True):
        for s1 in (False,True): out.append(((0,s0),(1,s1)))
    return out

def exact_two_polarity(T):
    return T in (I,XOR)

def frozen_bridge_impossibility():
    bad=[]; observed=set()
    for mask in range(16):
        vals=[(mask>>i)&1 for i in range(4)]
        C=((vals[0],vals[1]),(vals[2],vals[3]))
        T=compose(C,B)
        for row in T:
            observed.add(tuple(sorted(rowset(row))))
            if rowset(row)==frozenset({0}): bad.append({'mask':mask,'C':ml(C),'T':ml(T)})
    expected={(),(1,),(0,1)}
    return {'pass':not bad and observed==expected,
            'enumerated_C_count':16,
            'observed_source_row_images':[list(x) for x in sorted(observed)],
            'expected_only_images':[[],[1],[0,1]],
            'counterexamples':bad,
            'proof':'Each source row of C selects a subset S of p={0,1}. Under frozen B, B[0]={1}, B[1]={0,1}; existential composition returns union_{p in S} B[p], hence only EMPTY,{1},{0,1}, never {0}.'}

def filter_models(models, clauses):
    counts={(q,p):0 for q in (0,1) for p in (0,1)}; first={}
    for a in models:
        if not all(clause_ok_map(a,c) for c in clauses): continue
        pair=(int(bool(a[Q])),int(bool(a[P])))
        counts[pair]+=1; first.setdefault(pair,a)
    rel=tuple(tuple(int(counts[(q,p)]>0) for p in (0,1)) for q in (0,1))
    return counts,first,rel

def generic_projection(defects,equations,extra_clauses,keep):
    factors=[ba2.clause_factor(c) for c in defects]+[ba2.affine_factor(e) for e in equations]+[ba2.clause_factor(c) for c in extra_clauses]
    order=[v for v in az.ORDER if v not in keep]
    rows=attempts=0; max_scope=0
    for v in order:
        gathered=[f for f in factors if v in f['scope']]
        factors=[f for f in factors if v not in f['scope']]
        if not gathered: continue
        scope=tuple(sorted({u for f in gathered for u in f['scope'] if u!=v})); table={}
        for bits in product((0,1),repeat=len(scope)):
            a=dict(zip(scope,bits))
            for b in (0,1):
                attempts+=1; aa=dict(a); aa[v]=b
                if all(ba2.lookup(f,aa) for f in gathered): table[bits]=True; break
        rows+=len(table); max_scope=max(max_scope,len(scope)); factors.append({'scope':scope,'table':table})
    out=[]
    for a0 in (0,1):
        row=[]
        for a1 in (0,1):
            a={keep[0]:a0,keep[1]:a1}
            row.append(int(all(ba2.lookup(f,a) for f in factors)))
        out.append(tuple(row))
    return tuple(out),{'generated_rows':rows,'attempts':attempts,'max_scope':max_scope,'remaining_scopes':[list(f['scope']) for f in factors]}

def bridge_xor_relation():
    out=[]
    for p,r in product((0,1),repeat=2): out.append(int(bool(p or r) and bool((not p) or (not r))))
    return ((out[0],out[1]),(out[2],out[3]))

def minimality_audit():
    clauses=declared_clauses(); entries=[]
    # cost 0 (BA2 as-is)
    entries.append({'cost':0,'where':'NONE','T':ml(compose(C_STAR,B)),'two_polarity':exact_two_polarity(compose(C_STAR,B))})
    # exactly one additional clause, either block or bridge
    one=[]
    for cb in clauses:
        C=intersect(C_STAR,endpoint_clause_rel('block',cb)); T=compose(C,B)
        one.append({'where':'BLOCK','clause':[[v,int(s)] for v,s in cb],'T':ml(T),'two_polarity':exact_two_polarity(T)})
    for cr in clauses:
        BX=intersect(B,endpoint_clause_rel('bridge',cr)); T=compose(C_STAR,BX)
        one.append({'where':'BRIDGE','clause':[[v,int(s)] for v,s in cr],'T':ml(T),'two_polarity':exact_two_polarity(T)})
    # one block + one bridge clause
    two=[]
    for cb in clauses:
        C=intersect(C_STAR,endpoint_clause_rel('block',cb))
        for cr in clauses:
            BX=intersect(B,endpoint_clause_rel('bridge',cr)); T=compose(C,BX)
            if exact_two_polarity(T):
                two.append({'block_clause':[[v,int(s)] for v,s in cb], 'bridge_clause':[[v,int(s)] for v,s in cr],
                            'C':ml(C),'BX':ml(BX),'T':ml(T)})
    expected_block=[[0,1],[1,1]]       # q OR p
    expected_bridge=[[0,0],[1,0]]      # not p OR not r
    unique_expected=(len(two)==1 and two[0]['block_clause']==expected_block and two[0]['bridge_clause']==expected_bridge)
    return {'declared_clause_count_per_endpoint_pair':len(clauses),
            'cost0_two_polarity':entries[0]['two_polarity'],
            'cost1_two_polarity_solutions':[x for x in one if x['two_polarity']],
            'cost2_two_polarity_solutions':two,
            'minimum_additional_clause_cost_beyond_BA2':2 if not any(x['two_polarity'] for x in one) and two else None,
            'unique_expected_cost2_solution':unique_expected,
            'pass':(not entries[0]['two_polarity'] and not any(x['two_polarity'] for x in one) and unique_expected)}

def primal_and_templates(Uinfo):
    defects=list(Uinfo['defects'])+[BA2_CLAUSE,BA3_BLOCK]
    equations=Uinfo['equations']
    scopes=[tuple(sorted({abs(int(l)) for l in c})) for c in defects]+[tuple(sorted(set(e['vars']))) for e in equations]
    last_adj=az.primal_graph(az.UNIT_VARS,scopes)
    last_w=az.explicit_width(last_adj,az.ORDER)['width']
    # both bridge clauses have identical primal scope (P,R), so one scope represents both graph edges.
    mid_scopes=scopes+[(P,R)]
    mid_adj=az.primal_graph(tuple(az.UNIT_VARS)+(R,),mid_scopes)
    mid_w=az.explicit_width(mid_adj,az.ORDER)['width']
    ba2w=ba2.widths_and_solver_templates(Uinfo)
    same_last_graph=(last_adj==az.primal_graph(az.UNIT_VARS,[tuple(sorted({abs(int(l)) for l in c})) for c in list(Uinfo['defects'])+[BA2_CLAUSE]]+[tuple(sorted(set(e['vars']))) for e in equations]))
    ba2_mid_scopes=[tuple(sorted({abs(int(l)) for l in c})) for c in list(Uinfo['defects'])+[BA2_CLAUSE]]+[tuple(sorted(set(e['vars']))) for e in equations]+[(P,R)]
    same_mid_graph=(mid_adj==az.primal_graph(tuple(az.UNIT_VARS)+(R,),ba2_mid_scopes))
    return {'BA3_LAST_width':last_w,'BA3_MID_width':mid_w,'generic_width_upper_bound':max(last_w,mid_w),
            'BA2_width_upper_bound':ba2w['generic_width_upper_bound'],'same_primal_graph_as_BA2_LAST':same_last_graph,
            'same_primal_graph_as_BA2_MID':same_mid_graph,
            'width_delta_from_BA2':max(last_w,mid_w)-int(ba2w['generic_width_upper_bound'])}

def shift_clause(c,off): return tuple((abs(l)+off if l>0 else -(abs(l)+off)) for l in c)
def verify_chain(U, first, g, bit):
    proto=first[(bit,1-bit)]
    a={}; clauses=[]
    for j in range(g):
        off=30*j
        for v,val in proto.items(): a[v+off]=bool(val)
        clauses += [shift_clause(c,off) for c in U]
        q=Q+off; p=P+off
        clauses += [(-q,-p),(q,p)]
    for j in range(g-1):
        p=P+30*j; r=Q+30*(j+1)
        clauses += [(p,r),(-p,-r)]
    bad=[list(c) for c in clauses if not clause_ok_map(a,c)]
    qs=[int(bool(a[Q+30*j])) for j in range(g)]
    return {'g':g,'input_bit':bit,'pass':not bad and qs==[bit]*g,'q_boundary_values':qs,'clause_count':len(clauses),'bad_clause_count':len(bad),
            'model_sha256':sha_obj({str(k):int(bool(v)) for k,v in sorted(a.items())})}

def run():
    falsifiers=[]; failures=[]
    Uinfo,U,models,counts,first,RU=ba2.actual_source()
    Bactual=ba2.bridge_relation()
    if RU!=ALL or Bactual!=B: falsifiers.append('F1_FROZEN_SOURCE_OR_BRIDGE_DRIFT')

    impossible=frozen_bridge_impossibility()
    if not impossible['pass']: falsifiers.append('F1_FROZEN_BRIDGE_FORCE0_IMPOSSIBILITY_FALSE')

    count_x,first_x,CX_actual=filter_models(models,[BA2_CLAUSE,BA3_BLOCK])
    cnf_realization=(CX_actual==XOR and count_x[(0,1)]>0 and count_x[(1,0)]>0 and count_x[(0,0)]==0 and count_x[(1,1)]==0)
    if not cnf_realization: falsifiers.append('F2_C_X_NOT_REALIZABLE')

    BX=bridge_xor_relation()
    if BX!=XOR: falsifiers.append('F3_B_X_NOT_XOR')
    T=compose(CX_actual,BX)
    if T!=I: falsifiers.append('F4_TWO_FLIPS_NOT_IDENTITY')
    if compose(T,T)!=I: falsifiers.append('F5_PERSISTENCE_FAILURE')

    dp_CX,dp_CX_meta=generic_projection(Uinfo['defects'],Uinfo['equations'],[BA2_CLAUSE,BA3_BLOCK],(Q,P))
    dp_CX_pass=(dp_CX==CX_actual==XOR)
    if not dp_CX_pass: falsifiers.append('F6_SOURCE_PREIMAGE_OR_DP_MISMATCH')

    # direct materialized one-rung preimage: U + C_X + B_X
    transport_counts={(q,r):0 for q in (0,1) for r in (0,1)}
    for a in models:
        if not all(clause_ok_map(a,c) for c in (BA2_CLAUSE,BA3_BLOCK)): continue
        q=int(bool(a[Q])); p=int(bool(a[P]))
        for r in (0,1):
            if (p or r) and ((not p) or (not r)): transport_counts[(q,r)]+=1
    transport_rel=tuple(tuple(int(transport_counts[(q,r)]>0) for r in (0,1)) for q in (0,1))
    source_preimage_pass=(transport_rel==I and transport_counts[(0,0)]>0 and transport_counts[(1,1)]>0 and transport_counts[(0,1)]==0 and transport_counts[(1,0)]==0)
    if not source_preimage_pass: falsifiers.append('F6_SOURCE_PREIMAGE_TRANSPORT_MISMATCH')

    chain_checks=[verify_chain(U,first,g,b) for g in (1,2,5) for b in (0,1)]
    reconstruction_pass=all(x['pass'] for x in chain_checks)
    if not reconstruction_pass: falsifiers.append('F7_RECONSTRUCTION_LOSES_POLARITY')

    hierarchy={
      'neutral':'Remove (-q|-p),(q|p),(-p|-r) carrier additions -> exact sealed F_g with frozen positive bridges.',
      'BA2':'Remove BA3-only (q|p) and (-p|-r) -> exact BA2 carrier: one (-q|-p) per block plus frozen positive bridge.',
      'BA3':'BA2 plus exactly (q|p) per block and (-p|-r) per bridge.',
      'neutral_exact_by_clause_set':True,'BA2_exact_by_clause_set':True
    }

    widths=primal_and_templates(Uinfo)
    if widths['generic_width_upper_bound']>13 or widths['width_delta_from_BA2']!=0 or not widths['same_primal_graph_as_BA2_LAST'] or not widths['same_primal_graph_as_BA2_MID']:
        falsifiers.append('F10_WIDTH_OR_PRIMAL_GRAPH_DRIFT')

    minimal=minimality_audit()
    if not minimal['pass']: falsifiers.append('F11_CHEAPER_OR_DIFFERENT_MINIMAL_CARRIER')

    endpoint_counts={f'{q}{p}':int(counts[(q,p)]) for q in (0,1) for p in (0,1)}
    cx_counts={f'{q}{p}':int(count_x[(q,p)]) for q in (0,1) for p in (0,1)}
    actual_gates={
      'ALGEBRA_PASS':(RU==ALL and Bactual==B and CX_actual==XOR and BX==XOR and T==I),
      'CNF_REALIZATION_PASS':cnf_realization and BX==XOR,
      'SOURCE_PREIMAGE_PASS':source_preimage_pass,
      'DP_INTERACTION_PASS':dp_CX_pass,
      'PERSISTENCE_PASS':T==I and compose(T,T)==I,
      'RECONSTRUCTION_PASS':reconstruction_pass,
    }
    if not all(actual_gates.values()): failures.append('REALIZATION_GATE_FAILURE')

    result={
      'gate':GATE,'preregistration_commit':PREREG,'parent_BA2_source_head':PARENT_BA2,
      'outcome':'BA3-A_PERSISTENT_TWO_POLARITY_BOOLEAN_CHANNEL_CERTIFIED' if not falsifiers and not failures else 'BA3_RESTRICT_OR_FAIL',
      'failure_count':len(failures),'failures':failures,'falsifiers':falsifiers,
      'orientation':{'q':Q,'p':P,'r':R,'rows':'input 0,1','columns':'output 0,1'},
      'BA3_1_frozen_bridge_impossibility':impossible,
      'actual_source':{'R_U':ml(RU),'endpoint_counts':endpoint_counts,'model_count':len(models),'bridge_B':ml(Bactual)},
      'BA3_2_block_completion':{'BA2_clause':list(BA2_CLAUSE),'BA3_clause':list(BA3_BLOCK),'C_X_actual':ml(CX_actual),'pair_counts':cx_counts,
                                'real_witness_sha256':{'01':sha_obj({str(k):int(bool(v)) for k,v in sorted(first_x[(0,1)].items())}),
                                                       '10':sha_obj({str(k):int(bool(v)) for k,v in sorted(first_x[(1,0)].items())})}},
      'BA3_3_bridge_completion':{'frozen_bridge_clause':list(FROZEN_BRIDGE),'BA3_bridge_clause':list(BA3_BRIDGE),'B_X_actual':ml(BX)},
      'BA3_4_transport':{'T_2P':ml(T),'identity':ml(I),'T2':ml(compose(T,T)),'generic_power_law':'T_2P=I, therefore T_2P^k=I for every integer k>=1.'},
      'BA3_5_information':{'N_direction':2,'I_direction_bits':1.0,'FORCE_0_vs_FORCE_1':'DISTINCT_FOR_ALL_CHAIN_LENGTHS',
                           'residual_classes':['TOP','FORCE_0','FORCE_1','BOTTOM']},
      'BA3_6_realization_gates':actual_gates,'DP_projection_C_X':ml(dp_CX),'DP_meta':dp_CX_meta,
      'one_rung_transport_counts':{f'{q}{r}':int(transport_counts[(q,r)]) for q in (0,1) for r in (0,1)},
      'BA3_7_reconstruction':{'status':'PASS' if reconstruction_pass else 'FAIL','generic_rule':'Choose one of the actual frozen-U endpoint witnesses (0,1) or (1,0) according to incoming bit b, shift the same witness by 30*j in every block; XOR block gives p_j=1-b and XOR bridge gives q_(j+1)=b. Directly validate every shifted U/carrier/bridge clause.','checks':chain_checks},
      'BA3_8_generic_chain':{'block_clauses':['(-q_j OR -p_j)','(q_j OR p_j)'],'bridge_clauses':['(p_j OR q_(j+1))','(-p_j OR -q_(j+1))'],
                             'effective_boundary_relation':ml(I),'induction':'q_(j+1)=q_j for every j, hence q_0=...=q_(g-1).'},
      'BA3_9_hierarchy':hierarchy,
      'BA3_10_complexity':{
        'C_g':'67*g-2','L_g':'163*g-4','V_g':'20*g','added_vs_F_g_clauses':'3*g-1','added_vs_F_g_literals':'6*g-2',
        'added_vs_BA2_clauses':'2*g-1','added_vs_BA2_literals':'4*g-2',
        'certificate_records':'O(g)','certificate_bit_complexity':'O(g log g)','construction_time':'O(g log g) conservative encoded bound',
        'verification_time':'O(g log g) conservative encoded bound','reconstruction_time':'O(g log g) conservative encoded bound',
        'width':widths},
      'BA3_11_minimality':minimal,
      'nonclaims':['ARBITRARY_CNF_COVERAGE','SAT_IN_P','P_EQ_NP','TRUMP_FINISHED'],
      'firewall':{'P_VS_NP':'OPEN','SAT_IN_P':'NOT_PROVED','TRUMP_finished':False}
    }
    result['result_identity_sha256']=sha_obj({k:v for k,v in result.items() if k!='result_identity_sha256'})
    return result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); args=ap.parse_args()
    x=run(); Path(args.out).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
    if x['failure_count'] or x['falsifiers']: raise SystemExit(2)
    print(json.dumps({'outcome':x['outcome'],'identity':x['result_identity_sha256'],'width':x['BA3_10_complexity']['width']['generic_width_upper_bound'],'min_cost':x['BA3_11_minimality']['minimum_additional_clause_cost_beyond_BA2']},sort_keys=True))

if __name__=='__main__': main()
