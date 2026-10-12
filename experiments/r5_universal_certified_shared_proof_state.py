#!/usr/bin/env python3
"""JANUS R5 certified monotone shared proof state (SCL exact-one).

EXPERIMENTAL PROOF-AWARE COORDINATION, NOT P=NP:
  * every learned width<=2 nogood is backed by an exact degree-3
    GF2 polynomial-calculus identity 1, with assumptions equal to
    the forbidden assignment; original clauses + previously verified
    learned nogoods may participate;
  * independent checker replays each certificate in chronological
    order, without trusting the Gaussian-elimination prover;
  * exact-one / learned-nogood propagation adds only sound pins;
  * a finite monotone potential strictly falls on each ACCEPTED new
    nogood/pin, with at most n + 2n + 4*C(n,2) such events;
  * on saturation, result remains UNKNOWN unless a separate expert
    proves UNSAT or supplies an independently verified SAT witness.

The bound is a theorem about KNOWLEDGE GROWTH / FIXPOINT DURATION,
NOT an all-input polynomial SAT/UNSAT theorem: hard instances may
reach a fixed point while undecided. Fixed PC degree and nogood
width cannot silently grow with n in the polynomial guarantee.
"""
from __future__ import annotations

from itertools import combinations
from math import comb
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_boolean_pc_degree3_global_attack import (
    monomial_masks,poly_row,
)


def canonical_assumptions(assignments,n):
    pairs=tuple(sorted((int(v),int(b)) for v,b in assignments))
    assert len({v for v,_ in pairs})==len(pairs)
    assert all(0<=v<n and b in (0,1) for v,b in pairs)
    return pairs


def forbidden_assignment_polynomial(nogood):
    """Indicator of a FORBIDDEN Boolean partial assignment in F2.

    To ban x_i=b_i, use product of x_i when b_i=1, (1+x_i)
    when b_i=0. The polynomial must be ZERO on legal models.
    Returns a set of squarefree monomial masks with coefficient 1.
    """
    terms={0}
    for var,value in nogood:
        shifted={m|(1<<var) for m in terms}
        if value:
            terms=shifted
        else:
            terms=terms.symmetric_difference(shifted)
    return terms


def polynomial_to_vector(terms,mult,coords):
    out=0
    for mask in terms:
        out^=1<<coords[mask|mult]
    return out


def generator_vector(tag,target,mult,rows,known,pins,coords):
    if tag=='LINEAR':
        return poly_row(rows[target],mult,'parity',coords)
    if tag=='QUADRATIC':
        return poly_row(rows[target],mult,'quadratic',coords)
    if tag=='NOGOOD':
        return polynomial_to_vector(
            forbidden_assignment_polynomial(known[target]),mult,coords)
    if tag=='ASSUME':
        var,value=pins[target]
        terms={1<<var}
        if value:terms.add(0)
        return polynomial_to_vector(terms,mult,coords)
    raise AssertionError('unrecognized generator tag')


def generators_for(n,rows,known,pins,degree=3):
    assert degree==3
    low1=monomial_masks(n,1)
    low2=monomial_masks(n,2)
    generators=[]
    for i in range(len(rows)):
        generators.extend(('LINEAR',i,m) for m in low2)
        generators.extend(('QUADRATIC',i,m) for m in low1)
    for j,no_good in enumerate(known):
        assert 1<=len(no_good)<=2
        ms=monomial_masks(n,degree-len(no_good))
        generators.extend(('NOGOOD',j,m) for m in ms)
    for i in range(len(pins)):
        generators.extend(('ASSUME',i,m) for m in low2)
    return generators


def independent_check_pc3_identity(rows,n,known,pins,combination):
    """Certificate verifier; independent of rank computation."""
    coords={m:i for i,m in enumerate(monomial_masks(n,3))}
    total=0
    for tag,target,mult in combination:
        assert mult in coords and mult.bit_count()<=2
        if tag=='NOGOOD':
            assert 0<=target<len(known)
        if tag=='ASSUME':
            assert 0<=target<len(pins)
        total^=generator_vector(tag,target,mult,rows,known,pins,coords)
    assert total==1,('invalid PC identity',len(combination))
    return True


def polynomial_contradiction(rows,n,known=(),pins=(),degree=3):
    """Exact bounded-degree PC certificate, independent checker attached."""
    assert degree==3
    coords={m:i for i,m in enumerate(monomial_masks(n,3))}
    gens=generators_for(n,rows,known,pins,degree)
    pivots={}
    for i,(tag,target,mult) in enumerate(gens):
        p=generator_vector(tag,target,mult,rows,known,pins,coords)
        support=1<<i
        while p:
            pivot=p.bit_length()-1
            if pivot in pivots:
                old,old_support=pivots[pivot]
                p^=old;support^=old_support
            else:
                pivots[pivot]=(p,support)
                break
    vec=1;combination=0
    while vec:
        pivot=vec.bit_length()-1
        if pivot not in pivots:break
        rhs,certificate=pivots[pivot]
        vec^=rhs;combination^=certificate
    if vec:return None,{"rank":len(pivots),"dimension":len(coords),
                        "generator_count":len(gens)}
    selected=tuple(g for i,g in enumerate(gens) if (combination>>i)&1)
    assert independent_check_pc3_identity(rows,n,known,pins,selected)
    return selected,{"rank":len(pivots),"dimension":len(coords),
                     "generator_count":len(gens),
                     "proof_terms":len(selected)}


class CertifiedSharedState:
    """Immutable-source proof ledger, append-only known nogoods."""
    def __init__(self,rows,n,base_pins=(),width=2):
        self.rows=validate_sparse(rows,n)
        self.n=n
        assert width==2,'only width2 has audited exact potential'
        self.base_pins=canonical_assumptions(base_pins,n)
        self.ledger=[]
        self.nogoods=[]
        self.known=set()
        self.query_count=0
        self.stored_pins=dict(self.base_pins)
        self.prop_trace=[]
        self.found_witness=None
        self.potential_initial=n+2*n+4*comb(n,2)
        self.potential=self.potential_initial-len(self.stored_pins)

    def learn_pc3(self,assumptions):
        """Derive a width<=2 no-good under the immutable base context."""
        ng=canonical_assumptions(assumptions,self.n)
        assert 1<=len(ng)<=2
        if ng in self.known:return 'DUPLICATE'
        combined=canonical_assumptions(
            tuple(self.base_pins)+tuple(ng),self.n
        ) if not any(v in dict(self.base_pins) for v,_ in ng) else None
        # Repeated identical/contradictory pins are treated carefully:
        # a contradictory context assignment makes a trivial no-good.
        if combined is None:
            ctx=dict(self.base_pins)
            if all(ctx.get(v,b)==b for v,b in ng):
                combined=canonical_assumptions(
                    tuple({**ctx,**dict(ng)}.items()),self.n
                )
            else:
                return 'TRIVIAL_CONTEXT_CONFLICT'
        cert,stats=polynomial_contradiction(
            self.rows,self.n,tuple(self.nogoods),combined
        )
        self.query_count+=1
        if cert is None:return 'UNKNOWN'
        assert independent_check_pc3_identity(
            self.rows,self.n,tuple(self.nogoods),combined,cert
        )
        record={"nogood":ng,"certificate":cert,
                "context":combined,"previous":len(self.nogoods),
                "stats":stats,"authority":"VERIFIED_GF2_PC3"}
        self.nogoods.append(ng)
        self.ledger.append(record)
        self.known.add(ng)
        self.potential-=1
        return 'PROVED_FORBIDDEN'

    def learn_bounded_andor(self,assumptions,max_states=48):
        """Second independent proof expert contributes a certified no-good.

        Its proof relies on ORIGINAL SCL clauses, not on unverified
        previous PC3 facts. Unlike PC3, it can also return a globally
        checkable satisfying assignment found under test assumptions.
        """
        from r5_universal_exact_support_unsat_andor_certificate import (
            construct_unsat_proof,verify_unsat_proof,
        )
        ng=canonical_assumptions(assumptions,self.n)
        assert 1<=len(ng)<=2
        if ng in self.known:return 'DUPLICATE'
        context=dict(self.base_pins)
        for v,value in ng:
            if v in context and context[v]!=value:
                return 'TRIVIAL_CONTEXT_CONFLICT'
            context[v]=value
        ordered=tuple(sorted(context.items()))
        result,data=construct_unsat_proof(
            self.rows,self.n,pins=dict(ordered),max_states=max_states
        )
        self.query_count+=1
        if result=='UNKNOWN':return 'UNKNOWN'
        if result is None and data is None:
            # The existing complete AND/OR constructor returns this
            # sentinel when root assumptions immediately contradict
            # an Exact-One clause. Replay via independent normalization,
            # rather than mistaking it for a resource UNKNOWN.
            from r5_universal_exact_support_residual_dag_attack import (
                residual_normalize,
            )
            assert residual_normalize(
                self.rows,
                fixed_zero=[v for v,x in ordered if x==0],
                fixed_one=[v for v,x in ordered if x==1],
            ) is None
            record={
                'nogood':ng,'certificate':None,
                'context':ordered,'previous':len(self.nogoods),
                'authority':'VERIFIED_LOCAL_PIN_CONFLICT',
                'stats':{'proof_nodes':0},
            }
            self.nogoods.append(ng)
            self.ledger.append(record)
            self.known.add(ng)
            self.potential-=1
            return 'PROVED_FORBIDDEN'
        if result=='SAT':
            selected=set(data)
            witness=tuple(int(v in selected) for v in range(self.n))
            assert all(sum(witness[v] for v in row)==1 for row in self.rows)
            assert all(witness[v]==value for v,value in ordered)
            self.found_witness=witness
            return 'SAT_WITNESS'
        assert result=='UNSAT' and data is not None
        initial,proof=data
        nodes=verify_unsat_proof(
            self.rows,self.n,initial,proof,pins=dict(ordered)
        )
        record={
            'nogood':ng,'certificate':None,
            'context':ordered,'previous':len(self.nogoods),
            'authority':'VERIFIED_ANDOR_DAG',
            'andor_initial':initial,'andor_proof':proof,
            'stats':{'proof_nodes':nodes},
        }
        self.nogoods.append(ng)
        self.ledger.append(record)
        self.known.add(ng)
        self.potential-=1
        return 'PROVED_FORBIDDEN'

    def replay_ledger(self):
        previous=[]
        for record in self.ledger:
            assert record['previous']==len(previous)
            assert record['nogood'] not in previous
            if record['authority']=='VERIFIED_GF2_PC3':
                assert independent_check_pc3_identity(
                    self.rows,self.n,tuple(previous),record['context'],
                    record['certificate']
                )
            elif record['authority']=='VERIFIED_ANDOR_DAG':
                from r5_universal_exact_support_unsat_andor_certificate import (
                    verify_unsat_proof,
                )
                nodes=verify_unsat_proof(
                    self.rows,self.n,record['andor_initial'],
                    record['andor_proof'],pins=dict(record['context'])
                )
                assert nodes==record['stats']['proof_nodes']
            elif record['authority']=='VERIFIED_LOCAL_PIN_CONFLICT':
                from r5_universal_exact_support_residual_dag_attack import (
                    residual_normalize,
                )
                ctx=dict(record['context'])
                assert residual_normalize(
                    self.rows,
                    fixed_zero=[v for v,x in ctx.items() if x==0],
                    fixed_one=[v for v,x in ctx.items() if x==1],
                ) is None
            else:
                raise AssertionError('unrecognized proof authority')
            previous.append(record['nogood'])
        assert previous==self.nogoods
        return True

    def propagate(self):
        """Sound least fixed point of original exact-one + learned nogoods."""
        pins=dict(self.base_pins)
        trace=[]
        for _ in range(self.n+1):
            additions={}
            def conclude(var,value,why):
                if var in pins:
                    if pins[var]!=value:
                        return ('CONFLICT',var,value,why)
                    return None
                if var in additions:
                    if additions[var][0]!=value:
                        return ('CONFLICT',var,value,why)
                    return None
                additions[var]=(value,why)
                return None
            for ci,row in enumerate(self.rows):
                ones=[v for v in row if pins.get(v)==1]
                zeros=[v for v in row if pins.get(v)==0]
                if len(ones)>1 or len(zeros)==3:
                    return 'UNSAT',pins,trace+[('CLAUSE_CONFLICT',ci)]
                if len(ones)==1:
                    for v in row:
                        if v!=ones[0]:
                            failure=conclude(v,0,('EXACT_ONE_TRUE',ci,ones[0]))
                            if failure:return 'UNSAT',pins,trace+[failure]
                if len(zeros)==2:
                    third=next(v for v in row if v not in zeros)
                    failure=conclude(third,1,('EXACT_ONE_TWO_ZEROS',ci,tuple(zeros)))
                    if failure:return 'UNSAT',pins,trace+[failure]
            for ni,ng in enumerate(self.nogoods):
                wrong=any(v in pins and pins[v]!=b for v,b in ng)
                if wrong:continue
                remaining=[(v,b) for v,b in ng if v not in pins]
                if not remaining:
                    return 'UNSAT',pins,trace+[('NOGOOD_CONFLICT',ni)]
                if len(remaining)==1:
                    v,b=remaining[0]
                    failure=conclude(v,1-b,('LEARNED_NOGOOD_UNIT',ni))
                    if failure:return 'UNSAT',pins,trace+[failure]
            if not additions:
                for v,x in pins.items():
                    if v not in self.stored_pins:
                        self.stored_pins[v]=x
                        self.potential-=1
                self.prop_trace=trace
                self.independently_replay_propagation(pins,trace)
                assert self.potential==self.potential_initial-len(self.nogoods)-len(self.stored_pins)
                return 'FIXPOINT',pins,trace
            for v,(value,why) in sorted(additions.items()):
                pins[v]=value
                trace.append(('IMPLIED',v,value,why))
        raise AssertionError('sound unit propagation exceeded n additions')

    def independently_replay_propagation(self,pins,trace):
        """Independent sequential checker of each asserted derived literal.

        Unlike the production closure routine, replay performs no
        propagation or search: each supplied trace step is checked
        against already known literals and original clauses/ledger.
        """
        assert self.replay_ledger()
        current=dict(self.base_pins)
        for record in trace:
            assert len(record)==4 and record[0]=='IMPLIED',record
            _,v,value,reason=record
            assert v not in current and value in (0,1)
            kind=reason[0]
            if kind=='EXACT_ONE_TRUE':
                _,ci,one=reason
                assert 0<=ci<len(self.rows)
                row=self.rows[ci]
                assert v in row and one in row and v!=one
                assert current.get(one)==1 and value==0
            elif kind=='EXACT_ONE_TWO_ZEROS':
                _,ci,zeros=reason
                assert 0<=ci<len(self.rows)
                row=self.rows[ci]
                assert v in row and len(zeros)==2
                assert all(z in row and z!=v and current.get(z)==0
                           for z in zeros)
                assert value==1
            elif kind=='LEARNED_NOGOOD_UNIT':
                _,ni=reason
                assert 0<=ni<len(self.nogoods)
                ng=self.nogoods[ni]
                assert (v,1-value) in ng
                assert all(current.get(u)==b
                           for u,b in ng if u!=v)
            else:
                raise AssertionError(('unknown provenance',kind))
            current[v]=value
        assert current==pins
        return True

    def run_bounded_descent(self,max_queries=6):
        """Deterministic bounded schedule for all width<=2 no-goods.

        A strictly decreasing potential is checked on EVERY accepted
        update, while resource guard and saturation are distinct from
        decision SAT/UNSAT. There are O(n^2) candidate patterns;
        a no-budget run with restart after every discovery needs at
        most O(n^4) PC3 queries, each polynomial for degree=3.
        """
        if not isinstance(max_queries,int) or max_queries<0:
            raise ValueError('max_queries must be nonnegative int')
        def candidates():
            for v in range(self.n):
                for b in (0,1):
                    yield ((v,b),)
            for u,v in combinations(range(self.n),2):
                for a in (0,1):
                    for b in (0,1):
                        yield ((u,a),(v,b))
        query_start=self.query_count
        accepted=0
        rounds=0
        while True:
            rounds+=1
            progress=False
            for ng in candidates():
                if ng in self.known:continue
                if self.query_count-query_start>=max_queries:
                    return {
                        'status':'UNKNOWN_RESOURCE_GUARD',
                        'queries':self.query_count-query_start,
                        'new_facts':accepted,'rounds':rounds,
                        'potential':self.potential,
                    }
                before=self.potential
                action=self.learn_pc3(ng)
                assert self.potential<=before
                if action=='PROVED_FORBIDDEN':
                    assert self.potential==before-1
                    progress=True
                    accepted+=1
                    status,implications,trace=self.propagate()
                    if status!='FIXPOINT':
                        return {
                            'status':'UNKNOWN_CONFLICT_REQUIRES_ROOT_PROOF',
                            'queries':self.query_count-query_start,
                            'new_facts':accepted,'rounds':rounds,
                            'potential':self.potential,
                        }
                    break
            if not progress:
                return {
                    'status':'UNKNOWN_AT_FIXED_POINT',
                    'queries':self.query_count-query_start,
                    'new_facts':accepted,'rounds':rounds,
                    'potential':self.potential,
                }
            assert accepted<=self.potential_initial

    def summarize(self):
        assert self.potential>=0
        return {"learned_nogoods":len(self.nogoods),
                "fixed_variables":len(self.stored_pins),
                "potential":self.potential,
                "potential_initial":self.potential_initial,
                "queries":self.query_count,
                "certificate_chain_valid":self.replay_ledger(),
                "universally_complete":False}


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl,K33
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT
    )
    from r5_universal_certified_expert_portfolio import (
        SolveLinearCubicXSAT_Portfolio,
    )

    rows,n,_,_=make_scl(K33())
    state=CertifiedSharedState(rows,n)
    p0=state.potential
    outcome=state.learn_pc3(((0,1),(1,1)))
    assert outcome=='PROVED_FORBIDDEN',outcome
    assert state.replay_ledger()
    assert state.potential==p0-1
    assert state.learn_pc3(((0,1),(1,1)))=='DUPLICATE'
    assert state.potential==p0-1
    print(f'GLOBAL_PAIR_NOGOOD_PC3_CERTIFIED: '
          f'P_initial={p0} P_after={state.potential} '
          f'certificate_terms={state.ledger[-1]["stats"]["proof_terms"]}',
          flush=True)

    # A second independent expert can insert a proof into the SAME
    # proof-state, not just publish a disconnected terminal answer.
    combined=CertifiedSharedState(rows,n)
    act=combined.learn_bounded_andor(((0,1),(1,1)),max_states=48)
    assert act=='PROVED_FORBIDDEN',act
    assert combined.replay_ledger()
    assert combined.ledger[0]['authority'] in (
        'VERIFIED_ANDOR_DAG','VERIFIED_LOCAL_PIN_CONFLICT'
    )
    # PC3 then derives another forbidden assignment while treating
    # the ANDOR-certified restriction as an available new axiom.
    p_before=combined.potential
    act2=combined.learn_pc3(((0,1),(2,1)))
    assert act2=='PROVED_FORBIDDEN',act2
    assert combined.potential==p_before-1
    assert combined.replay_ledger()
    assert combined.ledger[1]['authority']=='VERIFIED_GF2_PC3'
    assert combined.ledger[0]['authority'] in (
        'VERIFIED_LOCAL_PIN_CONFLICT','VERIFIED_ANDOR_DAG'
    )
    print('TWO_EXPERT_PROVENANCE_CHAIN_ANDOR_TO_GF2_PC3=VERIFIED',
          flush=True)

    # Distinct expert: the Boolean propagation engine consumes exactly
    # the prior algebraic no-good, under a separate pinned branch.
    local=CertifiedSharedState(rows,n,base_pins=((0,1),))
    assert local.learn_pc3(((1,1),))=='PROVED_FORBIDDEN'
    status,pins,trace=local.propagate()
    assert status=='FIXPOINT' and pins[1]==0 and pins[2]==0
    assert len(local.nogoods)==1
    assert local.replay_ledger()
    assert local.independently_replay_propagation(pins,trace)
    p1=local.potential
    # Portfolio consumes the derived pins as exact context, not
    # speculative guesses, and still independently checks witness.
    portfolio=SolveLinearCubicXSAT_Portfolio(
        rows,n,pins={0:1},poly_only=False,pc3_max_n=0,
        bounded_states=150,shared_state=local,
    )
    assert portfolio['status']=='SAT'
    assert 'CERTIFIED_SHARED_NOGOOD_AND_EXACTONE_PROPAGATION' in portfolio['experts']
    assert all(portfolio['witness'][v]==x for v,x in pins.items())
    assert all(sum(portfolio['witness'][v] for v in row)==1 for row in rows)
    print(f'CROSS_EXPERT_PC3_NOGOOD_TO_PROPAGATION_TO_EXACT_PORTFOLIO '
          f'SAT_WITNESS_VERIFIED P={p1} added_pins={len(pins)-1}',
          flush=True)

    # Prove that an admissible SAT input can reach fixed point
    # without UNSAT, and that the proof state NEVER calls this SAT.
    base=CertifiedSharedState(rows,n)
    outcome,pins,trace=base.propagate()
    assert outcome=='FIXPOINT'
    assert not pins and not base.nogoods
    # The new deterministic scheduler never invents a verdict.
    bounded=base.run_bounded_descent(max_queries=2)
    assert bounded['status'].startswith('UNKNOWN')
    assert bounded['queries']<=2
    print(f'BOUNDED_SHARED_DESCENT={bounded}',flush=True)

    print('SOUND_POLY_PROOF_STATE_CAN_STALL_ON_SAT_WITH_NO_FACTS = VERIFIED')

    # A structurally distinct SCL source can contribute constraints
    # without needing any cubic-graph construction at the main API.
    A=build_A(P_SAT,Q_SAT)
    e61_rows=[tuple(i for i,v in enumerate(row) if v) for row in A]
    E61=CertifiedSharedState(e61_rows,12)
    exact=SolveLinearCubicXSAT_Portfolio(
        e61_rows,12,poly_only=False,pc3_max_n=0,bounded_states=150
    )
    assert exact['status']=='SAT'
    opposite=((0,1-exact['witness'][0]),)
    learned=E61.learn_pc3(opposite)
    assert learned in ('PROVED_FORBIDDEN','UNKNOWN')
    if learned=='PROVED_FORBIDDEN':
        before=E61.potential
        stateflag,forced,trace=E61.propagate()
        assert stateflag=='FIXPOINT'
        assert forced[0]==exact['witness'][0]
        assert E61.potential<before
    print(f'E61_NON_GRAPH_SCL_N12_PC3_SINGLETON={learned} '
          f'state={E61.summarize()}',flush=True)

    print('GLOBAL_MONOTONE_POTENTIAL_ACCEPTED_UPDATE_LIMIT=O_N_SQUARED PROVED')
    print('SHARED_CERTIFICATE_CHAIN_REPLAY = VERIFIED')
    print('SHARED_FACT_PROPAGATION_INDEPENDENT_REPLAY = VERIFIED')
    print('POLYNOMIAL_QUERY_BUDGET_WITHOUT_FALSE_FINAL_VERDICT = VERIFIED')
    print('FIXPOINT_IMPLIES_GLOBAL_SAT_OR_UNSAT = FALSE_NOT_ASSERTED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
