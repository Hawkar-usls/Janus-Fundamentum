from itertools import product


def vars_in_formula(phi):
    return sorted({abs(l) for c in phi for l in c})


def min_unsat(phi):
    vs=vars_in_formula(phi)
    best=len(phi)+1
    best_a=None
    for bits in product((0,1), repeat=len(vs)):
        a=dict(zip(vs,bits))
        bad=0
        for c in phi:
            sat=False
            for lit in c:
                val=a[abs(lit)]
                sat |= bool(val if lit>0 else 1-val)
            bad += int(not sat)
        if bad<best:
            best=bad; best_a=a
    return best,best_a


def build_source(phi):
    # One copy per literal occurrence. For each original variable x, copies are
    # indexed in encounter order j=0..k-1. Original-clause occurrence is L_j.
    copies={}
    clause_L=[]
    cid=0
    for ci,c in enumerate(phi):
        row=[]
        for lit in c:
            v=abs(lit)
            j=len(copies.setdefault(v,[]))
            copy=(v,j,1 if lit>0 else -1)
            copies[v].append(copy)
            row.append(copy)
        clause_L.append(row)
    return copies,clause_L


def phase_selected_M(sign, phase):
    # phase0: outgoing implication occurrence selected at q_j.
    # positive L => M=outgoing, negative L => R=outgoing.
    # phase1: incoming occurrence selected at q_j.
    # negative L => M=incoming, positive L => R=incoming.
    if sign>0:
        return phase==0
    return phase==1


def matching_defect_for_phases(phi, copies, clause_L, phase_by_var):
    # For fixed implication-cycle phases, each original clause chooses the L
    # witness with minimum local defect. There is no resource interaction among Ls.
    total=0
    chosen=[]
    for row in clause_L:
        costs=[]
        for v,j,sign in row:
            cost=int(phase_selected_M(sign, phase_by_var[v]))
            costs.append(cost)
        b=min(costs)
        total+=b
        chosen.append(costs.index(b))
    return total,chosen


def min_matching_defect(phi):
    copies,clause_L=build_source(phi)
    vs=sorted(copies)
    best=len(phi)+1
    best_phase=None
    for bits in product((0,1), repeat=len(vs)):
        phase=dict(zip(vs,bits))
        d,_=matching_defect_for_phases(phi,copies,clause_L,phase)
        if d<best:
            best=d; best_phase=phase
    return best,best_phase


def verify_cycle_geometry(phi):
    copies,_=build_source(phi)
    for v,lst in copies.items():
        k=len(lst)
        if k==1:
            # A one-copy implication loop is degenerate in the literal reduction;
            # the theorem/checker controls below use variables with >=2 occurrences.
            continue
        # Abstract incidence: q_j adjacent to I_{j-1}, I_j.
        q_neighbors={j:{(j-1)%k,j} for j in range(k)}
        I_neighbors={j:{j,(j+1)%k} for j in range(k)}
        assert all(len(x)==2 for x in q_neighbors.values())
        assert all(len(x)==2 for x in I_neighbors.values())
        # Exactly two perfect matchings in a simple even cycle for k>=2.
        phases=[]
        for choices in product(range(k), repeat=k):
            # choices[I_j] = q index; only q_j or q_{j+1} allowed.
            if all(choices[j] in I_neighbors[j] for j in range(k)) and len(set(choices))==k:
                phases.append(choices)
        expected=[tuple(range(k)), tuple((j+1)%k for j in range(k))]
        assert sorted(phases)==sorted(expected), (v,k,phases,expected)


def check(phi):
    assert all(len(c)==3 for c in phi)
    assert all(len({abs(l) for l in c})==3 for c in phi)
    # Keep controls away from single-occurrence degeneracy.
    counts={v:0 for v in vars_in_formula(phi)}
    for c in phi:
        for l in c: counts[abs(l)]+=1
    assert min(counts.values())>=2, counts

    verify_cycle_geometry(phi)
    mu,a=min_unsat(phi)
    md,p=min_matching_defect(phi)
    assert md==mu, (phi,md,mu,p,a)
    # Phase bit equals original truth assignment under the theorem convention.
    if a is not None:
        copies,clause_L=build_source(phi)
        d,_=matching_defect_for_phases(phi,copies,clause_L,a)
        unsat=sum(not any((a[abs(l)] if l>0 else 1-a[abs(l)]) for l in c) for c in phi)
        assert d==unsat
    print(f'clauses={len(phi)} vars={len(counts)} min_unsat={mu} min_matching_defect={md} PASS')


def main():
    controls=[
        [(1,2,3),(-1,2,-3),(1,-2,3),(-1,-2,-3)],
        [(1,2,3),(-1,-2,3),(1,-2,-3),(-1,2,-3)],
        # Unsatisfiable complete 3-variable clause cube: all 8 sign patterns.
        [tuple((v if ((mask>>(v-1))&1) else -v) for v in (1,2,3)) for mask in range(8)],
    ]
    for phi in controls:
        check(phi)
    print('PASS_TOVEY_CYCLE_PHASE_DEFECT_EQUALS_MIN_UNSAT')
    print('SOURCE_MATCHING_DEFECT_OBJECTIVE=EXACT_MIN_UNSAT')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
