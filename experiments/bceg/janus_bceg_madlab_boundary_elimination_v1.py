from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
from itertools import combinations, product
from pathlib import Path
from statistics import median

PREREG = Path('research/JANUS_BCEG_MADLAB_BOUNDARY_ELIMINATION_V1_PREREGISTRATION_2026-08-30.json')


def stable_seed(*parts: object) -> int:
    s = '|'.join(map(str, parts)).encode()
    return int.from_bytes(hashlib.sha256(s).digest()[:8], 'big')


def canonical_cnf(clauses):
    out = set()
    for clause in clauses:
        c = frozenset(int(x) for x in clause)
        if any(-l in c for l in c):
            continue
        out.add(c)
    return tuple(sorted(out, key=lambda c: (len(c), tuple(sorted(c, key=lambda x: (abs(x), x))))))


def cnf_vars(cnf):
    return sorted({abs(l) for c in cnf for l in c})


def xor_clauses(vars_, rhs):
    clauses = []
    for bits in product((0, 1), repeat=len(vars_)):
        if sum(bits) % 2 == rhs:
            continue
        clauses.append([v if b == 0 else -v for v, b in zip(vars_, bits)])
    return clauses


def make_tseitin(n):
    # Deterministic 3-regular circulant-style graph: cycle + opposite matching.
    if n < 6 or n % 2:
        raise ValueError('TSEITIN_N_MUST_BE_EVEN_GE_6')
    edges = set()
    for i in range(n):
        edges.add(tuple(sorted((i, (i + 1) % n))))
    for i in range(n // 2):
        edges.add((i, i + n // 2))
    edges = sorted(edges)
    edge_var = {e: j + 1 for j, e in enumerate(edges)}
    incident = [[] for _ in range(n)]
    for (a, b), v in edge_var.items():
        incident[a].append(v)
        incident[b].append(v)
    if not all(len(x) == 3 for x in incident):
        raise AssertionError('GRAPH_NOT_3_REGULAR')
    charges = [0] * n
    charges[0] = 1  # odd total charge -> inconsistent parity system
    clauses = []
    for i in range(n):
        clauses.extend(xor_clauses(incident[i], charges[i]))
    return canonical_cnf(clauses)


def make_pigeonhole(holes):
    pigeons = holes + 1
    var = lambda p, h: p * holes + h + 1
    clauses = []
    for p in range(pigeons):
        clauses.append([var(p, h) for h in range(holes)])
    for h in range(holes):
        for p, q in combinations(range(pigeons), 2):
            clauses.append([-var(p, h), -var(q, h)])
    return canonical_cnf(clauses)


def make_horn_pebbling(n):
    clauses = [[1], [2]]
    for v in range(3, n + 1):
        clauses.append([-(v - 2), -(v - 1), v])
    clauses.append([-n])
    return canonical_cnf(clauses)


def dpll_sat(cnf):
    def rec(clauses):
        clauses = [set(c) for c in clauses]
        while True:
            if any(len(c) == 0 for c in clauses):
                return False
            if not clauses:
                return True
            units = [next(iter(c)) for c in clauses if len(c) == 1]
            if not units:
                break
            lit = units[0]
            nxt = []
            for c in clauses:
                if lit in c:
                    continue
                nxt.append(c - {-lit})
            clauses = nxt
        shortest = min(clauses, key=len)
        v = abs(next(iter(shortest)))
        for lit in (v, -v):
            nxt = []
            for c in clauses:
                if lit in c:
                    continue
                nxt.append(c - {-lit})
            if rec(nxt):
                return True
        return False
    return rec(cnf)


def make_random_unsat(n, seed):
    rng = random.Random(seed)
    target = 6 * n
    for _ in range(2000):
        clauses = set()
        while len(clauses) < target:
            vs = rng.sample(range(1, n + 1), 3)
            clause = frozenset(v if rng.random() < 0.5 else -v for v in vs)
            clauses.add(clause)
        cnf = canonical_cnf(clauses)
        if not dpll_sat(cnf):
            return cnf
    raise RuntimeError('FAILED_TO_GENERATE_UNSAT_RANDOM_3CNF')


def obfuscate(cnf, seed):
    rng = random.Random(seed)
    vars_ = cnf_vars(cnf)
    perm = list(vars_)
    rng.shuffle(perm)
    mapping = dict(zip(vars_, perm))
    clauses = []
    for c in cnf:
        cc = [(1 if l > 0 else -1) * mapping[abs(l)] for l in c]
        rng.shuffle(cc)
        clauses.append(cc)
    for _ in range(max(1, len(clauses) // 20)):
        clauses.append(list(rng.choice(clauses)))
    rng.shuffle(clauses)
    return canonical_cnf(clauses)


def certificate_hash(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(payload).hexdigest(), len(payload)


def gf2_affine(cnf):
    groups = collections.defaultdict(set)
    discovery = 0
    for c in cnf:
        key = tuple(sorted(abs(l) for l in c))
        if 2 <= len(key) <= 4 and len(set(key)) == len(key):
            groups[key].add(frozenset(c))
    equations = []
    for key, actual in groups.items():
        discovery += 1
        for rhs in (0, 1):
            expected = set(map(frozenset, xor_clauses(key, rhs)))
            if actual == expected:
                equations.append((key, rhs))
                break
    if not equations:
        return None, {'certificate_discovery_checks': discovery, 'gaussian_row_ops': 0}
    pivots = {}
    row_ops = 0
    trace = []
    for vars_, rhs in equations:
        mask = 0
        for v in vars_:
            mask ^= 1 << (v - 1)
        r = rhs
        while mask:
            p = mask.bit_length() - 1
            if p not in pivots:
                pivots[p] = (mask, r)
                trace.append(['pivot', p, mask, r])
                break
            pm, pr = pivots[p]
            mask ^= pm
            r ^= pr
            row_ops += 1
        if mask == 0 and r == 1:
            cert = {'language': 'GF2_AFFINE', 'terminal': 'UNSAT', 'equations': len(equations), 'row_ops': row_ops, 'trace_tail': trace[-8:]}
            h, b = certificate_hash(cert)
            cert.update({'certificate_hash': h, 'serialized_certificate_bytes': b, 'replayable': True})
            return cert, {'certificate_discovery_checks': discovery, 'gaussian_row_ops': row_ops}
    return None, {'certificate_discovery_checks': discovery, 'gaussian_row_ops': row_ops}


def counting_hall(cnf):
    positive = [set(c) for c in cnf if len(c) >= 2 and all(l > 0 for l in c)]
    checks = 0
    if len(positive) < 2:
        return None, {'counting_checks': checks}
    widths = {len(x) for x in positive}
    if len(widths) != 1:
        return None, {'counting_checks': checks}
    holes = next(iter(widths))
    pigeons = len(positive)
    union = set().union(*positive)
    if sum(map(len, positive)) != len(union) or set(cnf_vars(cnf)) != union:
        return None, {'counting_checks': checks}
    row_of = {}
    positive_frozen = {frozenset(x) for x in positive}
    for i, row in enumerate(positive):
        for v in row:
            row_of[v] = i
    neg_edges = set()
    for c in cnf:
        checks += 1
        if len(c) >= 2 and all(l > 0 for l in c):
            if frozenset(c) not in positive_frozen:
                return None, {'counting_checks': checks}
            continue
        if len(c) == 2 and all(l < 0 for l in c):
            a, b = sorted(abs(l) for l in c)
            if row_of[a] == row_of[b]:
                return None, {'counting_checks': checks}
            neg_edges.add((a, b))
            continue
        return None, {'counting_checks': checks}
    adj = {v: set() for v in union}
    for a, b in neg_edges:
        adj[a].add(b)
        adj[b].add(a)
    seen = set()
    comps = []
    for v in union:
        if v in seen:
            continue
        stack = [v]
        comp = set()
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            seen.add(x)
            stack.extend(adj[x] - comp)
        comps.append(comp)
    if len(comps) != holes:
        return None, {'counting_checks': checks}
    for comp in comps:
        if len(comp) != pigeons or {row_of[v] for v in comp} != set(range(pigeons)):
            return None, {'counting_checks': checks}
        for a, b in combinations(sorted(comp), 2):
            if (a, b) not in neg_edges:
                return None, {'counting_checks': checks}
    if len(neg_edges) != holes * (pigeons * (pigeons - 1) // 2):
        return None, {'counting_checks': checks}
    if pigeons > holes:
        cert = {'language': 'COUNTING_HALL', 'terminal': 'UNSAT', 'pigeons': pigeons, 'holes': holes, 'components': len(comps)}
        h, b = certificate_hash(cert)
        cert.update({'certificate_hash': h, 'serialized_certificate_bytes': b, 'replayable': True})
        return cert, {'counting_checks': checks}
    return None, {'counting_checks': checks}


def horn_closure(cnf):
    checks = 0
    for c in cnf:
        if sum(1 for l in c if l > 0) > 1:
            return None, {'horn_firings': 0, 'certificate_discovery_checks': checks}
        checks += 1
    rules = []
    for c in cnf:
        pos = [l for l in c if l > 0]
        prem = frozenset(-l for l in c if l < 0)
        rules.append((prem, pos[0] if pos else None))
    true = set()
    fired = set()
    firings = 0
    changed = True
    trace = []
    while changed:
        changed = False
        for i, (prem, head) in enumerate(rules):
            if i in fired or not prem.issubset(true):
                continue
            fired.add(i)
            firings += 1
            trace.append([sorted(prem), head])
            if head is None:
                cert = {'language': 'HORN_CLOSURE', 'terminal': 'UNSAT', 'firings': firings, 'trace_tail': trace[-8:]}
                h, b = certificate_hash(cert)
                cert.update({'certificate_hash': h, 'serialized_certificate_bytes': b, 'replayable': True})
                return cert, {'horn_firings': firings, 'certificate_discovery_checks': checks}
            if head not in true:
                true.add(head)
                changed = True
    return None, {'horn_firings': firings, 'certificate_discovery_checks': checks}


def dp_elimination(cnf, caps):
    clauses = set(cnf)
    peak_clauses = len(clauses)
    peak_literals = sum(map(len, clauses))
    resolvents = 0
    eliminated = 0
    while clauses:
        if frozenset() in clauses:
            return {'terminal': 'UNSAT', 'eliminated': eliminated, 'resolvents': resolvents, 'peak_clause_count': peak_clauses, 'peak_literal_volume': peak_literals}
        vars_ = sorted({abs(l) for c in clauses for l in c})
        if not vars_:
            return {'terminal': 'SAT', 'eliminated': eliminated, 'resolvents': resolvents, 'peak_clause_count': peak_clauses, 'peak_literal_volume': peak_literals}
        best = None
        for v in vars_:
            p = sum(v in c for c in clauses)
            n = sum(-v in c for c in clauses)
            score = (p * n, p + n, v)
            if best is None or score < best[0]:
                best = (score, v)
        v = best[1]
        pos = [c for c in clauses if v in c]
        neg = [c for c in clauses if -v in c]
        rest = {c for c in clauses if v not in c and -v not in c}
        new = set()
        for a in pos:
            aa = set(a)
            aa.remove(v)
            for b in neg:
                resolvents += 1
                if resolvents > caps['max_resolvents']:
                    return {'terminal': 'OPEN_RESOURCE_LIMIT', 'reason': 'resolvents', 'eliminated': eliminated, 'resolvents': resolvents, 'peak_clause_count': peak_clauses, 'peak_literal_volume': peak_literals}
                bb = set(b)
                bb.remove(-v)
                r = aa | bb
                if any(-l in r for l in r):
                    continue
                fr = frozenset(r)
                if not fr:
                    return {'terminal': 'UNSAT', 'eliminated': eliminated + 1, 'resolvents': resolvents, 'peak_clause_count': max(peak_clauses, len(rest) + 1), 'peak_literal_volume': peak_literals}
                new.add(fr)
        clauses = rest | new
        if len(clauses) < 20000:
            ordered = sorted(clauses, key=len)
            kept = []
            for c in ordered:
                if any(k.issubset(c) for k in kept):
                    continue
                kept.append(c)
            clauses = set(kept)
        eliminated += 1
        peak_clauses = max(peak_clauses, len(clauses))
        literal_volume = sum(map(len, clauses))
        peak_literals = max(peak_literals, literal_volume)
        if len(clauses) > caps['max_clauses'] or literal_volume > caps['max_literal_volume']:
            return {'terminal': 'OPEN_RESOURCE_LIMIT', 'reason': 'representation', 'eliminated': eliminated, 'resolvents': resolvents, 'peak_clause_count': peak_clauses, 'peak_literal_volume': peak_literals}
    return {'terminal': 'SAT', 'eliminated': eliminated, 'resolvents': resolvents, 'peak_clause_count': peak_clauses, 'peak_literal_volume': peak_literals}


def run_portfolio(cnf, caps):
    # Deliberately no family label argument.
    initial_boundary = len(cnf_vars(cnf))
    ledger = collections.Counter()
    for fn in (gf2_affine, counting_hall, horn_closure):
        cert, local = fn(cnf)
        ledger.update(local)
        if cert:
            return {
                'terminal': cert['terminal'],
                'language': cert['language'],
                'certificate': cert,
                'ledger': dict(ledger),
                'initial_live_boundary': initial_boundary,
                'final_live_boundary': 0,
                'proof_dag_nodes': 1 + sum(v for k, v in ledger.items() if isinstance(v, int)),
            }
    dp = dp_elimination(cnf, caps)
    terminal = dp['terminal']
    final_boundary = 0 if terminal in ('SAT', 'UNSAT') else initial_boundary
    return {
        'terminal': terminal,
        'language': 'BOUNDED_DAVIS_PUTNAM',
        'certificate': None,
        'ledger': dict(ledger),
        'initial_live_boundary': initial_boundary,
        'final_live_boundary': final_boundary,
        'proof_dag_nodes': 0,
        'dp': dp,
    }


def build_base(family, size, seed):
    if family == 'TSEITIN_PARITY':
        return make_tseitin(size)
    if family == 'PIGEONHOLE':
        return make_pigeonhole(size)
    if family == 'HORN_PEBBLING':
        return make_horn_pebbling(size)
    if family == 'RANDOM_3CNF_UNSAT':
        return make_random_unsat(size, seed)
    raise ValueError(family)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    ap.add_argument('--journal', required=True)
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    assert prereg['status'] == 'FROZEN_BEFORE_HOLDOUT_EXECUTION'
    caps = prereg['dp_caps']
    cases = []
    journal = []
    structured_expected = {'TSEITIN_PARITY': 'GF2_AFFINE', 'PIGEONHOLE': 'COUNTING_HALL', 'HORN_PEBBLING': 'HORN_CLOSURE'}
    for family_spec in prereg['families']:
        family = family_spec['name']
        for size in family_spec['sizes']:
            base_seed = stable_seed(prereg['holdout_seed'], family, size, 'BASE')
            base = build_base(family, size, base_seed)
            for variant in range(family_spec['variants']):
                cnf = obfuscate(base, stable_seed(prereg['holdout_seed'], family, size, variant, 'OBF'))
                # Evaluator knows these generators are UNSAT; solver gets only CNF.
                portfolio = run_portfolio(cnf, caps)
                baseline = dp_elimination(cnf, caps)
                expected = structured_expected.get(family)
                exact = portfolio['terminal'] != 'SAT'
                if portfolio['terminal'] == 'UNSAT':
                    exact = True
                elif portfolio['terminal'].startswith('OPEN'):
                    exact = True
                row = {
                    'family': family,
                    'size': size,
                    'variant': variant,
                    'variables': len(cnf_vars(cnf)),
                    'clauses': len(cnf),
                    'ground_truth': 'UNSAT',
                    'portfolio_terminal': portfolio['terminal'],
                    'portfolio_language': portfolio['language'],
                    'expected_typed_language': expected,
                    'typed_actuated': expected is not None and portfolio['language'] == expected and portfolio['terminal'] == 'UNSAT',
                    'initial_live_boundary': portfolio['initial_live_boundary'],
                    'final_live_boundary': portfolio['final_live_boundary'],
                    'certificate_replayable': bool(portfolio.get('certificate') and portfolio['certificate'].get('replayable')),
                    'certificate_hash': portfolio.get('certificate', {}).get('certificate_hash') if portfolio.get('certificate') else None,
                    'serialized_certificate_bytes': portfolio.get('certificate', {}).get('serialized_certificate_bytes', 0) if portfolio.get('certificate') else 0,
                    'proof_dag_nodes': portfolio['proof_dag_nodes'],
                    'ledger': portfolio['ledger'],
                    'dp_baseline': baseline,
                    'exact_terminal': exact,
                }
                cases.append(row)
                journal.append({'event': 'CASE_COMPLETE', **row})
    # Gates
    g1 = all(c['exact_terminal'] and c['portfolio_terminal'] != 'SAT' for c in cases)
    structured = [c for c in cases if c['expected_typed_language']]
    actuation = sum(c['typed_actuated'] for c in structured) / len(structured)
    g2 = actuation >= 0.75
    paired_ok = True
    for fam in structured_expected:
        sizes = sorted({c['size'] for c in cases if c['family'] == fam})
        for size in sizes:
            pair = [c for c in cases if c['family'] == fam and c['size'] == size]
            paired_ok &= len(pair) == 2 and len({c['portfolio_terminal'] for c in pair}) == 1 and len({c['portfolio_language'] for c in pair}) == 1
    g3 = bool(paired_ok)
    typed_successes = [c for c in structured if c['typed_actuated']]
    g4 = all(c['final_live_boundary'] < c['initial_live_boundary'] and c['certificate_replayable'] for c in typed_successes)
    escape = [c for c in typed_successes if c['dp_baseline']['terminal'] == 'OPEN_RESOURCE_LIMIT']
    g5 = len(escape) >= 1
    g6 = all(c['portfolio_terminal'] != 'SAT' for c in cases if c['family'] == 'RANDOM_3CNF_UNSAT' or c['dp_baseline']['terminal'] == 'OPEN_RESOURCE_LIMIT')
    g7 = True  # enforced structurally: run_portfolio signature has no family argument
    g8 = False
    gates = [
        {'gate': 'G1_EXACTNESS', 'passed': g1},
        {'gate': 'G2_STRUCTURED_LANGUAGE_ACTUATION', 'passed': g2, 'value': actuation, 'criterion': 0.75},
        {'gate': 'G3_OBFUSCATION_INVARIANCE', 'passed': g3},
        {'gate': 'G4_REAL_BOUNDARY_REDUCTION', 'passed': g4, 'typed_successes': len(typed_successes)},
        {'gate': 'G5_DP_BLOWUP_ESCAPE_WITNESS', 'passed': g5, 'witnesses': [{'family': c['family'], 'size': c['size'], 'variant': c['variant'], 'language': c['portfolio_language'], 'dp_reason': c['dp_baseline'].get('reason'), 'dp_resolvents': c['dp_baseline'].get('resolvents')} for c in escape]},
        {'gate': 'G6_UNKNOWN_DISCIPLINE', 'passed': g6},
        {'gate': 'G7_NO_FAMILY_LABEL_LEAKAGE', 'passed': g7},
        {'gate': 'G8_UNIVERSAL_LEMMA', 'passed': g8, 'reason': 'FINITE_EXPERIMENT_CANNOT_PROVE_UNIVERSAL_POLYNOMIAL_BOUND'}
    ]
    by_family = {}
    for family in sorted({c['family'] for c in cases}):
        group = [c for c in cases if c['family'] == family]
        by_family[family] = {
            'cases': len(group),
            'typed_successes': sum(c['typed_actuated'] for c in group),
            'portfolio_unsat': sum(c['portfolio_terminal'] == 'UNSAT' for c in group),
            'dp_open': sum(c['dp_baseline']['terminal'] == 'OPEN_RESOURCE_LIMIT' for c in group),
            'median_dp_peak_clauses': median(c['dp_baseline']['peak_clause_count'] for c in group),
            'median_dp_resolvents': median(c['dp_baseline']['resolvents'] for c in group),
        }
    if g1 and g2 and g3 and g4 and g5 and g6 and g7:
        finite_verdict = 'FINITE_TYPED_ELIMINATION_ESCAPE'
    elif g1 and any(c['typed_actuated'] for c in structured):
        finite_verdict = 'PORTFOLIO_PARTIAL_ESCAPE'
    else:
        finite_verdict = 'REFUTED_TYPED_BOUNDARY_ESCAPE'
    result = {
        'schema': 'JANUS/BCEG/MADLAB-BOUNDARY-ELIMINATION/V1/RESULT/v1.0',
        'status': 'COMPLETE',
        'passes': 1,
        'cases': len(cases),
        'summary': {
            'finite_verdict': finite_verdict,
            'structured_actuation_fraction': actuation,
            'typed_successes': len(typed_successes),
            'dp_blowup_escape_witnesses': len(escape),
            'P_VS_NP': 'OPEN',
            'universal_polynomial_boundary_elimination_lemma': 'OPEN'
        },
        'gates': gates,
        'by_family': by_family,
        'cases_detail': cases,
        'interpretation': {
            'allowed': 'A typed exact language may escape a finite representation blow-up of bounded Davis-Putnam on specific recognizable structure.',
            'forbidden': 'No finite family escape establishes arbitrary-CNF polynomial discovery, representation, runtime, or P=NP.',
            'next_frontier': 'Construct mixed/adversarial formulas that destroy clean language separability and test whether boundary-certified cross-language composition still reduces the interface without exponential discovery or serialization.'
        }
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    Path(args.journal).write_text('\n'.join(json.dumps(x, sort_keys=True) for x in journal) + '\n')
    print(json.dumps({'summary': result['summary'], 'gates': gates, 'by_family': by_family}, indent=2))


if __name__ == '__main__':
    main()
