from __future__ import annotations
from pathlib import Path
from itertools import combinations
from collections import Counter
import hashlib, json

ROOT = Path(__file__).resolve().parent


def canon(raw):
    out = set()
    for clause in raw:
        s = {int(x) for x in clause}
        if any(-x in s for x in s):
            continue
        out.add(tuple(sorted(s, key=lambda z: (abs(z), z < 0))))
    return sorted(out, key=lambda c: (len(c), tuple((abs(x), x < 0) for x in c)))


def replay(raw, assignment):
    return all(any((x > 0 and bool(assignment.get(abs(x), False))) or
                   (x < 0 and not bool(assignment.get(abs(x), False))) for x in c)
               for c in raw)


def parse_graph(raw):
    cnf = canon(raw)
    pos = [c for c in cnf if c and all(x > 0 for x in c)]
    neg = [c for c in cnf if len(c) == 2 and all(x < 0 for x in c)]
    if not pos or len(pos) + len(neg) != len(cnf):
        return None
    owner = {}
    for u, c in enumerate(pos):
        for x in c:
            if x in owner:
                return None
            owner[x] = u
    if set(owner) != {abs(x) for c in cnf for x in c}:
        return None
    conflict = {x: set() for x in owner}
    pairs = set()
    for a, b in neg:
        x, y = -a, -b
        if x not in owner or y not in owner or owner[x] == owner[y]:
            return None
        pairs.add(tuple(sorted((x, y))))
        conflict[x].add(y); conflict[y].add(x)
    unseen = set(owner); comps = []
    while unseen:
        s = min(unseen); unseen.remove(s); stack = [s]; comp = {s}
        while stack:
            x = stack.pop()
            for y in conflict[x]:
                if y in unseen:
                    unseen.remove(y); comp.add(y); stack.append(y)
        comps.append(tuple(sorted(comp)))
    comps.sort(key=lambda c: (min(c), len(c)))
    comp_of = {}
    for rid, comp in enumerate(comps):
        seen_left = set()
        for x in comp:
            if owner[x] in seen_left:
                return None
            seen_left.add(owner[x]); comp_of[x] = rid
        for i, x in enumerate(comp):
            for y in comp[i + 1:]:
                if tuple(sorted((x, y))) not in pairs:
                    return None
    expected = set()
    for comp in comps:
        for i, x in enumerate(comp):
            for y in comp[i + 1:]:
                expected.add(tuple(sorted((x, y))))
    if expected != pairs:
        return None
    adj = {u: set() for u in range(len(pos))}
    edge_var = {}
    for x, u in owner.items():
        v = comp_of[x]
        if (u, v) in edge_var:
            return None
        adj[u].add(v); edge_var[(u, v)] = x
    return {'m': len(pos), 'n': len(comps), 'adj': adj, 'edge_var': edge_var}


def verify_sat(raw, g, cert):
    rows = cert.get('matching') if isinstance(cert, dict) else None
    if not isinstance(rows, list) or len(rows) != g['m']:
        return False
    seen_u = set(); seen_v = set(); assignment = {abs(x): False for c in raw for x in c}
    for row in rows:
        if not (isinstance(row, list) and len(row) == 3):
            return False
        u, v, var = map(int, row)
        if u in seen_u or v in seen_v or (u, v) not in g['edge_var']:
            return False
        if g['edge_var'][(u, v)] != var:
            return False
        seen_u.add(u); seen_v.add(v); assignment[var] = True
    return seen_u == set(range(g['m'])) and replay(raw, assignment)


def verify_unsat(g, cert):
    if not isinstance(cert, dict) or cert.get('kind') != 'HALL_DEFICIENT_SET':
        return False
    try:
        S = {int(x) for x in cert.get('S', [])}
        N = {int(x) for x in cert.get('N', [])}
    except Exception:
        return False
    if not S or not S.issubset(set(range(g['m']))):
        return False
    exact = set()
    for u in S:
        exact.update(g['adj'][u])
    return N == exact and len(N) < len(S)


def exact_expansion(g, r):
    checked = 0
    for k in range(1, r + 1):
        for S in combinations(range(g['m']), k):
            checked += 1
            counts = Counter()
            for u in S:
                counts.update(g['adj'][u])
            boundary = sum(1 for v in range(g['n']) if counts[v] == 1)
            if boundary < k:
                return False, checked, {'S': list(S), 'boundary': boundary, 'required': k}
    return True, checked, None


def payload_hash_without_hash(pop):
    q = dict(pop)
    q.pop('population_sha256', None)
    raw = json.dumps(q, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def main():
    pop = json.loads((ROOT / 'population.json').read_text(encoding='utf-8'))
    run = json.loads((ROOT / 'run_raw.json').read_text(encoding='utf-8'))
    by_id = {r['id']: r for r in run['cases']}
    failures = []
    lane_counts = {}
    hard_checks = []
    counting = {'hard_unsat': 0, 'hall_unknown': 0, 'sat_unknown': 0}
    if payload_hash_without_hash(pop) != pop.get('population_sha256'):
        failures.append(['POPULATION_HASH_DRIFT'])
    for case in pop['cases']:
        cid = case['id']; lane = case['lane']; truth = case['truth']
        rec = by_id.get(cid)
        if rec is None:
            failures.append([cid, 'MISSING_RUN_RECORD']); continue
        g = parse_graph(case['cnf'])
        ok = g is not None and rec.get('admitted') is True and rec.get('decision') == truth
        if g is None:
            failures.append([cid, 'INDEPENDENT_RECOGNIZER_REJECT'])
            continue
        if truth == 'SAT':
            ok = ok and rec.get('certificate', {}).get('kind') == 'SATURATING_MATCHING' and verify_sat(case['cnf'], g, rec.get('certificate', {}))
        else:
            ok = ok and verify_unsat(g, rec.get('certificate', {}))
        if not ok:
            failures.append([cid, 'EXACTNESS_OR_CERTIFICATE_FAIL', truth, rec.get('decision')])
        lane_counts.setdefault(lane, {'ok': 0, 'total': 0})
        lane_counts[lane]['total'] += 1
        lane_counts[lane]['ok'] += int(ok)

        base = rec.get('counting_baseline', {}).get('decision')
        if lane == 'HARD_UNSAT_EXPANDER' and base == 'UNSAT': counting['hard_unsat'] += 1
        if lane == 'HALL_UNSAT_CONTROL' and base == 'UNKNOWN': counting['hall_unknown'] += 1
        if lane == 'SAT_MATCHING_CONTROL' and base == 'UNKNOWN': counting['sat_unknown'] += 1

        if lane == 'HARD_UNSAT_EXPANDER':
            r = int(case['hardness']['r'])
            exp_ok, checked, witness = exact_expansion(g, r)
            width = max(len(c) for c in canon(case['cnf']))
            h_ok = exp_ok and g['m'] == g['n'] + 1 and width <= 5
            if not h_ok:
                failures.append([cid, 'HARDNESS_FIXTURE_FAIL', witness, g['m'], g['n'], width])
            hard_checks.append({
                'id': cid, 'expansion_ok': exp_ok, 'r': r, 'e': 1,
                'checked_subsets': checked, 'input_clause_width': width,
                'theorem_width_lower_bound': r / 2,
                'm': g['m'], 'n': g['n']
            })
    expected_per_lane = 4
    if any(v['ok'] != expected_per_lane or v['total'] != expected_per_lane for v in lane_counts.values()):
        failures.append(['LANE_COUNT_FAIL', lane_counts])
    if counting != {'hard_unsat': 4, 'hall_unknown': 4, 'sat_unknown': 4}:
        failures.append(['COUNTING_BASELINE_SEPARATION_FAIL', counting])

    pass_ok = not failures and len(lane_counts) == 3
    verdict = ('PASS_SCOPED_GRAPH_PHP_CARDINALITY_HALL_QUOTIENT_SEPARATION'
               if pass_ok else 'FAIL_GRAPH_PHP_CARDINALITY_HALL_QUOTIENT_SEPARATION')
    result = {
        'artifact': 'JANUS-TRUMP-GRAPH-PHP-CARDINALITY-HALL-MATCHING-QUOTIENT-VS-RESOLUTION-WIDTH-2026-09-14-v1.0',
        'verdict': verdict,
        'lane_counts': lane_counts,
        'counting_baseline': counting,
        'hardness_checks': hard_checks,
        'failures': failures,
        'theorem_authority': {
            'source': 'Ben-Sasson and Wigderson, Short Proofs Are Narrow—Resolution Made Simple',
            'theorem': 'Theorem 4.15',
            'statement_used': 'w(G-PHP |- 0) >= r*e/2 for (m,n,d,r,e)-expanders',
            'existence_used': 'for m=n+1, degree-5 expanders exist with r=Theta(n), e=1',
            'not_reproved_by_gate': True
        },
        'complexity_ledger': {
            'recognize_construct': 'polynomial canonicalization, conflict components, clique verification',
            'matching_hall': 'Hopcroft-Karp polynomial maximum matching plus alternating reachability Hall witness',
            'reconstruct_verify': 'linear assignment reconstruction plus original CNF replay',
            'post_admission_hidden_search': False,
            'population_expansion_audit_is_solver_runtime': False
        },
        'scientific_firewall': {
            'UNIVERSAL_SAT_SELECTOR': 'NOT_CLAIMED',
            'SAT_IN_P': 'NOT_PROVED',
            'P_VS_NP': 'OPEN',
            'Pi_negative_evidence_weight': 0
        }
    }
    (ROOT / 'checker_raw.json').write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps({'verdict': verdict, 'lane_counts': lane_counts, 'counting': counting,
                      'failures': failures}, sort_keys=True))


if __name__ == '__main__':
    main()
