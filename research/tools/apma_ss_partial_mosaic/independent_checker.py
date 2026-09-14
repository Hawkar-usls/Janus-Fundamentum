from pathlib import Path
import copy, inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_ss_partial_mosaic.partial_mosaic import (
    MORPH_SEQUENCE,
    commit_proposal,
    compile_image_mosaic,
    compile_source_mosaic,
    make_state,
    propose_extract,
    state_hash,
    verify_full_recomposition,
    verify_proposal,
)
from research.tools.apma_ss_provenance.apma_ss_controller import encode_c023


def eval_cnf(cnf, assignment):
    return all(any(bool(assignment[abs(lit)]) == (lit > 0) for lit in clause) for clause in cnf)


def brute_sat(cnf, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(cnf, a):
            return True
    return False


def signed_cube_3cnf():
    clauses = []
    for signs in itertools.product((-1, 1), repeat=3):
        clauses.append(tuple(signs[i] * (i + 1) for i in range(3)))
    return tuple(clauses)


def random_formula(rng, n):
    clauses = []
    for _ in range(rng.randint(1, 9)):
        width = rng.randint(1, min(3, n))
        vars_ = rng.sample(range(1, n + 1), width)
        clauses.append(tuple(v if rng.choice((False, True)) else -v for v in vars_))
    return tuple(clauses)


def carrier_counts(state):
    return {k: len(state['carriers'].get(k, ())) for k in MORPH_SEQUENCE}


def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}

    mixed_sat = ((1, 2), (1, -2, -3), (1, 2, -3))
    mixed = compile_source_mosaic(mixed_sat, 3)
    checks['mixed_recomposition'] = verify_full_recomposition(mixed['state']) and not mixed['state']['residual']
    checks['mixed_all_three_carriers'] = carrier_counts(mixed['state']) == {'2CNF': 1, 'HORN3': 1, 'DUAL_HORN3': 1}
    checks['mixed_shared_open'] = mixed['status'] == 'OPEN_CROSS_CARRIER_INTERACTION' and brute_sat(mixed_sat, 3)
    examples['MIXED_SAT'] = {'status': mixed['status'], 'counts': carrier_counts(mixed['state'])}

    cube = signed_cube_3cnf()
    cube_out = compile_source_mosaic(cube, 3)
    cube_counts = carrier_counts(cube_out['state'])
    checks['signed_cube_partition'] = cube_counts == {'2CNF': 0, 'HORN3': 4, 'DUAL_HORN3': 4}
    checks['signed_cube_each_carrier_sat'] = all(v['sat'] is True for v in cube_out['decision']['carrier_statuses'].values())
    checks['signed_cube_global_unsat'] = brute_sat(cube, 3) is False
    checks['signed_cube_not_false_sat'] = cube_out['status'] == 'OPEN_CROSS_CARRIER_INTERACTION'
    examples['SIGNED_CUBE'] = {'status': cube_out['status'], 'counts': cube_counts, 'actual_sat': False}

    local_unsat = ((1,), (-1,), (2, 3, -1))
    unsat_out = compile_source_mosaic(local_unsat, 3)
    checks['carrier_local_unsat_lifts'] = unsat_out['status'] == 'CERTIFIED_UNSAT_BY_CARRIER' and brute_sat(local_unsat, 3) is False

    disjoint = ((1, 2), (3, -4, -5), (6, 7, -8))
    disjoint_out = compile_source_mosaic(disjoint, 8)
    checks['disjoint_carriers_sat'] = disjoint_out['status'] == 'CERTIFIED_SAT_DISJOINT_CARRIERS' and brute_sat(disjoint, 8)

    state = make_state(mixed_sat)
    p2 = propose_extract(state, '2CNF')
    state = commit_proposal(state, p2)
    before = state_hash(state)
    ph = propose_extract(state, 'HORN3')
    corrupted = copy.deepcopy(ph)
    corrupted['selected'] = tuple()
    checks['corrupted_proposal_rejected'] = not verify_proposal(state, corrupted)
    checks['corrupted_proposal_rollback_identity'] = state_hash(state) == before
    state = commit_proposal(state, ph)
    checks['valid_after_failed_proposal'] = verify_full_recomposition(state)

    rng = random.Random(20260914)
    random_rows = []
    for n in range(3, 6):
        for _ in range(24):
            f = random_formula(rng, n)
            out = compile_source_mosaic(f, n)
            exact = verify_full_recomposition(out['state']) and not out['state']['residual']
            actual = brute_sat(f, n)
            promoted_ok = True
            if out['status'].startswith('CERTIFIED_SAT'):
                promoted_ok = actual is True
            if out['status'] == 'CERTIFIED_UNSAT_BY_CARRIER':
                promoted_ok = actual is False
            random_rows.append(exact and promoted_ok)
    checks['random_exactness_72_of_72'] = all(random_rows) and len(random_rows) == 72

    image = encode_c023(mixed_sat, 3)
    image_out = compile_image_mosaic(image)
    checks['image_reverse_to_same_mosaic'] = image_out['status'] == mixed['status'] and carrier_counts(image_out['state']) == carrier_counts(mixed['state'])

    import research.tools.apma_ss_partial_mosaic.partial_mosaic as candidate
    text = inspect.getsource(candidate).lower()
    forbidden = ['itertools.product', 'random.', 'dpll', 'best_of', 'score_candidate', 'brute_sat']
    hits = [x for x in forbidden if x in text]
    checks['captain_guard'] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = 'PASS_APMA_SS_PARTIAL_EXACT_MORPH_COMPOSITION__UNIVERSAL_3CNF_MOSAIC__SHARED_INTERACTION_OPEN' if ok else 'FAIL_PARTIAL_MORPH_OR_INTERACTION_FIREWALL'
    out = {
        'schema': 'JANUS_TRUMP_APMA_SS_PARTIAL_EXACT_MORPH_COMPOSITION_GATE_V1',
        'verdict': verdict,
        'checks': checks,
        'captain_guard_hits': hits,
        'examples': examples,
        'random_controls': {'seed': 20260914, 'count': len(random_rows)},
        'runtime_ms': round((time.perf_counter() - t0) * 1000, 3),
        'scientific_status': {'SAT_IN_P': 'NOT_PROVED', 'P_VS_NP': 'OPEN', 'Pi_negative_evidence_weight': 0},
        'next': 'exact shared-variable interaction message between simultaneously tractable carriers'
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
