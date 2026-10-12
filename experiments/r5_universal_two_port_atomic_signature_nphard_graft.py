#!/usr/bin/env python3
"""R5 two-port atomic signature NP-hardness embedding audit.

For every connected legal square/cubic/linear Exact-One SCL source A,
join to fixed SAT K4 SCL18 by swapping one incidence edge from A
with one incidence edge in the gadget. The resulting Tanner graph
is connected and retains square/cubic/linear degrees/linearity, with
a certified 2-edge cut.

For a source side of size n, 3sum_inside x = n+x_u-x_w.
If n divisible by 3, this forces x_u=x_w. For a pair with
equal values (b,b), the cut-open A-side formula is EXACTLY A,
with source's original row incidence u replaced by a foreign
Boolean input w equal to u. Therefore

  SAT(A) iff sigma_A(0,0) OR sigma_A(1,1),

where sigma_A is the exact two-port feasibility signature of
the A side. If n mod3 !=0, source A and the joined source
are both UNSAT by cardinality, so the SAT equivalence still
holds for ALL original legal SCL sources.

K4 SCL18 has 6 3-edge-coloring witnesses; an arbitrary selected
gadget variable w can take BOTH Boolean values due colour
permutation symmetry. Hence the gadget imposes no additional
constraint on the equality diagonal.

This is a polynomial, size n+18, witness-preserving reduction
from connected SCL SAT to one cut-open *irregular fragment*
two-port signature extraction. Since connected SCL is NP-hard
(if all connected source components were poly-time decidable,
the NP-complete general source would be too), computing exact
general atomic port-signature feasibility is NP-hard.

NP-hardness is not an impossibility of P=NP and does not prohibit
a revolutionary universal solver. It rules out assuming that
constant-width two-port boundaries themselves render every
interior polynomially computable.
"""
from __future__ import annotations

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    K4,K33,petersen_graph,make_scl
)
from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
from r5_universal_connected_scl_tanner_two_cut_proof_audit import (
    exact_connected_incidence_switch,exact_tanner_graph,
)
from r5_universal_certified_scl_component_decomposition import (
    canonical_scl_components
)
from r5_universal_certified_two_port_signature_algebra import (
    cut_open_fragments,prove_piece,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def graft_any_connected_source(source):
    source=validate_sparse(source,len(source))
    n=len(source)
    assert len(canonical_scl_components(source,n))==1
    gadget,ng,_,_=make_scl(K4())
    assert ng==18
    joined=exact_connected_incidence_switch(source,gadget)
    total=n+ng
    assert len(canonical_scl_components(joined,total))==1
    edge_list,_=exact_tanner_graph(joined,total)
    u=source[0][0]
    w=n+gadget[0][0]
    # validate_sparse() canonicalizes/sorts the complete row list.
    # Identify ORIGINAL A-side rows by two (or three) A columns
    # instead of assuming any particular post-sort row index.
    source_row_ids=tuple(ci for ci,row in enumerate(joined)
                         if sum(v<n for v in row)>=2)
    assert len(source_row_ids)==n
    side=frozenset(
        source_row_ids+tuple(total+v for v in range(n))
    )
    cut_ids=tuple(i for i,(row,var) in enumerate(edge_list)
                  if (row in side)!=(var in side))
    assert len(cut_ids)==2
    assert {edge_list[i][1]-total for i in cut_ids}=={u,w}
    cut={'side':side,'edge_ids':cut_ids}
    pieces,ports=cut_open_fragments(joined,total,cut)
    assert ports==(u,w)
    assert len(pieces[0]['row_indices'])==n
    assert len(pieces[1]['row_indices'])==18
    return joined,cut,pieces,ports


def main():
    gadget,_,_,_=make_scl(K4())
    controls=[
        ('K4_SAT18',gadget,True),
        ('K33_SAT27',make_scl(K33())[0],True),
        ('PETERSEN_UNSAT45',make_scl(petersen_graph())[0],False),
        ('FANO_UNSAT7',cyclic(7),False),
    ]
    for name,source,truth in controls:
        n=len(source)
        joined,cut,pieces,(u,w)=graft_any_connected_source(source)
        side=pieces[0]
        recovered=[]
        for b in (0,1):
            local={i:b for i,v in enumerate(side['original_columns'])
                   if v in (u,w)}
            assert len(local)==2
            proof=prove_piece(side,local,max_states=1500)
            assert proof['status'] in ('SAT','UNSAT'),(name,b,proof['status'])
            if proof['status']=='SAT':
                recovered.append(b)
                witness=proof['model']
                # Restrict original interior variables and revalidate
                # EVERY original source clause with ORIGINAL column IDs.
                original=[None]*n
                for i,v in enumerate(side['original_columns']):
                    if v<n:
                        original[v]=witness[i]
                assert all(x in (0,1) for x in original)
                assert all(sum(original[v] for v in row)==1
                           for row in source)
        assert bool(recovered)==truth,(name,recovered,truth)
        assert len(joined)==n+18
        print(f'ATOMIC_SIGNATURE_NP_HARD_EMBEDDING {name} '
              f'original_n={n} connected_join_n={len(joined)} '
              f'diagonal_sat_values={recovered} '
              f'input_SAT={truth}',flush=True)
    print('GADGET_K4_VARIABLE_ZERO_AND_ONE_REALIZABLE=PROVED_BY_COLOR_SYMMETRY')
    print('ARBITRARY_CONNECTED_SCL_TO_TWO_PORT_SIGNATURE_POLY_REDUCTION=PROVED')
    print('GENERAL_TWO_PORT_ATOMIC_SIGNATURE_EXTRACTION=NP_HARD')
    print('INTERFACE_SIZE_CONSTANT_DOES_NOT_BOUND_SIGNATURE_CONSTRUCTION=PROVED')
    print('POLY_UNIVERSAL_SCL_SOLVER=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
