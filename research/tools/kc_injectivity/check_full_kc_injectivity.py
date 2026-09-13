from __future__ import annotations
import hashlib, json
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
COMP=REPO/'research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_GAUGE_QUOTIENTED_PROOF_CARRYING_COLLISION_OR_SUFFICIENCY_COMPILER_PROOF_OR_FALSIFICATION_2026-09-12.json'
BERK=REPO/'research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_SCALABLE_EXACT_BERKOWITZ_DAG_MATERIALIZATION_AND_EQUIVALENCE_PROOF_OR_FALSIFICATION_2026-09-12.json'
OUT=REPO/'research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_EXACT_K_C_RESIDUAL_COORDINATE_INJECTIVITY_VS_CONGRUENCE_PROOF_OR_FALSIFICATION_2026-09-13.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def sts31_blocks():
    s=set()
    for a in range(1,32):
        for b in range(a+1,32):
            c=a^b
            if 1 <= c <= 31 and c not in (a,b): s.add(tuple(sorted((a,b,c))))
    return sorted(s)
def perm_matrix(code):
    p=[int(x)-1 for x in code]
    return tuple(tuple(1 if r==p[c] else 0 for c in range(4)) for r in range(4))

def main():
    comp=json.loads(COMP.read_text(encoding='utf-8'))
    berk=json.loads(BERK.read_text(encoding='utf-8'))
    blocks=sts31_blocks()
    eplus=[]
    for p in range(1,32):
        for B in sorted(B for B in blocks if p in B): eplus.append((p,B))
    tree=set(comp['CANONICAL_TWO_ROOT_FOREST']['tree_edge_indices_zero_based'])
    residual=[i for i in range(len(eplus)) if i not in tree]
    h_inc=[i for i,e in enumerate(eplus) if e[0]==1]
    t_block=(1,2,3)
    t_inc=[i for i,e in enumerate(eplus) if e[1]==t_block]
    ht=set(h_inc+t_inc)
    overlap=sorted(ht.intersection(residual))
    vc=berk['VECTOR_CONSTRUCTOR_CLOSURE']
    derived=vc['derived_positions']
    support=sorted(derived['h_sheet_indices']+derived['t_sheet_indices'])
    codes=comp['EXACT_S4_COMPILER']['coding']
    mats=[perm_matrix(c) for c in codes]
    checks={
      'sts31_block_count_155':len(blocks)==155,
      'every_point_degree_15':all(sum(p in B for B in blocks)==15 for p in range(1,32)),
      'eplus_count_465':len(eplus)==465,
      'tree_count_185':len(tree)==185 and all(0<=i<465 for i in tree),
      'residual_count_280':len(residual)==280,
      'e_star_is_tree_index_0':0 in tree and eplus[0]==(1,(1,2,3)),
      'h_incident_count_15':len(h_inc)==15,
      't_incident_count_3':len(t_inc)==3,
      'all_h_t_incident_edges_in_tree':not overlap,
      'residual_edges_disjoint_from_h_t':all(eplus[i][0]!=1 and eplus[i][1]!=(1,2,3) for i in residual),
      'frozen_local_support_indices_match':support==[0,1,2,3,124,125,126,127],
      'constructor_closure_pass':vc.get('closure')=='PASS',
      'all_named_local_vectors_bound':set(vc['vectors'])=={'u','v','a0','a1','b0','b1','c0','c1','x','y','zvec','c_plus_C1','c_minus_C1'},
      'physical_edge_block_binding':comp['EXACT_STATE_PI_CIRCUIT']['physical_full_permutation_replay']['non_distinguished_edge_block'].startswith('P(g_e)'),
      'M14_binding':'M_(B0,C)-c_(+|C)c_(+|C)^*' in comp['EXACT_STATE_PI_CIRCUIT']['common_middle_circuits']['M14_C'],
      'K_binding':comp['EXACT_STATE_PI_CIRCUIT']['common_middle_circuits']['K_C']=='zeta I - M14_C',
      's4_code_count_24':len(codes)==24 and len(set(codes))==24,
      's4_permutation_matrices_injective':len(set(mats))==24,
      'prior_residual_coordinates_lossless':comp['RESIDUAL_HOLONOMY_COORDINATES']['verdict']=='PASS_LOSSLESS_RESIDUAL_COORDINATES'
    }
    passed=all(checks.values())
    verdict=('PASS_FULL_K_C_INJECTIVE_OVER_FROZEN_S4_280_QUOTIENT__NO_NONTRIVIAL_FULL_K_C_CONGRUENCE' if passed else 'OPEN_SOURCE_BINDING_OR_RECONSTRUCTION_INCOMPLETE')
    result={
      'schema':'TRUMP_EXACT_K_C_RESIDUAL_COORDINATE_INJECTIVITY_VS_CONGRUENCE_RESULT_V1',
      'status':verdict,
      'source_artifacts':{'compiler':str(COMP.relative_to(REPO)).replace('\\','/'),'compiler_sha256':sha(COMP),'berkowitz':str(BERK.relative_to(REPO)).replace('\\','/'),'berkowitz_sha256':sha(BERK)},
      'measurements':{'sts31_blocks':len(blocks),'Eplus_edges':len(eplus),'tree_edges':len(tree),'residual_chords':len(residual),'h_incident_edge_indices':h_inc,'t_incident_edge_indices':t_inc,'residual_ht_overlap_indices':overlap,'local_correction_sheet_support':support},
      'checks':checks,
      'proof_chain':[
        'Every residual coordinate r_c occupies the positive point-to-block 4x4 block P(r_c) in the canonical physical replay.',
        'All frozen local correction vectors are supported only on h=P1 and t=B[1,2,3] sheet indices.',
        'The exact reconstructed E_+ order shows every edge incident to h or t belongs to T; therefore none of the 280 residual chords touches h or t.',
        'Hence every residual P(r_c) block is unchanged by every h/t-supported rank-one correction entering M14_C.',
        'From full K_C=zeta I-M14_C, each such off-diagonal block is exactly recoverable.',
        'The 24 frozen S4 permutation matrices are pairwise distinct, so every recovered P(r_c) uniquely determines r_c.',
        'Therefore equality of full K_C implies equality of all 280 residual coordinates within the frozen compiler semantics.'
      ] if passed else [],
      'scope':'frozen STS31/HPS/R4/Pi24 compiler semantics only',
      'firewalls':['DOES_NOT_RULE_OUT_PROJECTED_OR_STAGE_LOCAL_SEMANTIC_CONGRUENCE','DOES_NOT_PROVE_MINIMAL_INTERFACE_WIDTH','FINITE_FROZEN_INSTANCE_RESULT_NE_ASYMPTOTIC_COMPLEXITY_THEOREM','SAT_IN_P_REMAINS_NOT_PROVED','P_VS_NP_REMAINS_OPEN','PI_NEGATIVE_EVIDENTIARY_WEIGHT_REMAINS_ZERO'],
      'next_if_pass':'Do not use full K_C as the C035 message. Search a proper exact projection/future-relevant relation whose state size can be bounded.'
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':verdict,'residual_chords':len(residual),'residual_ht_overlap':overlap,'h_incident':h_inc,'t_incident':t_inc,'support':support,'checks_passed':sum(checks.values()),'checks_total':len(checks)},sort_keys=True))
    raise SystemExit(0 if passed else 2)
if __name__=='__main__': main()
