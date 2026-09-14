from __future__ import annotations
from itertools import combinations
from pathlib import Path
from collections import Counter
import hashlib, json, random

ROOT = Path(__file__).resolve().parent
N_VALUES = [16, 20, 24, 32]
SEED_BASE = 9142026


def exact_boundary_expansion(adj, right_n, r):
    checked = 0
    left = range(len(adj))
    for k in range(1, r + 1):
        for S in combinations(left, k):
            checked += 1
            counts = Counter()
            for u in S:
                counts.update(adj[u])
            boundary = sum(1 for v in range(right_n) if counts[v] == 1)
            if boundary < k:
                return False, {'S': list(S), 'boundary': boundary, 'required': k}, checked
    return True, None, checked


def hard_expander(n):
    rng = random.Random(SEED_BASE + 1000 * n)
    m = n + 1
    r = n // 8
    for attempt in range(1, 20001):
        adj = [tuple(sorted(rng.sample(range(n), 5))) for _ in range(m)]
        used = {v for row in adj for v in row}
        if len(used) != n:
            continue
        ok, witness, checked = exact_boundary_expansion(adj, n, r)
        if ok:
            return adj, {'attempt': attempt, 'r': r, 'e': 1, 'checked_subsets': checked}
    raise RuntimeError(('NO_EXPANDER_FOUND', n, r))


def hall_unsat(n):
    adj = [(0, 1), (0, 1), (0, 1)]
    span = n - 2
    for j in range(n - 3):
        adj.append((2 + j, 2 + ((j + 1) % span)))
    return [tuple(sorted(set(row))) for row in adj]


def sat_cycle(n):
    return [tuple(sorted((u, (u + 1) % n))) for u in range(n)]


def graph_php_cnf(adj):
    edge_var = {}
    next_var = 1
    for u, row in enumerate(adj):
        for v in row:
            edge_var[(u, v)] = next_var
            next_var += 1
    cnf = []
    for u, row in enumerate(adj):
        cnf.append([edge_var[(u, v)] for v in row])
    right_to_vars = {}
    for (u, v), x in edge_var.items():
        right_to_vars.setdefault(v, []).append(x)
    for v in sorted(right_to_vars):
        xs = sorted(right_to_vars[v])
        for i, a in enumerate(xs):
            for b in xs[i + 1:]:
                cnf.append([-a, -b])
    return cnf


def transport(cnf, seed):
    rng = random.Random(seed)
    vars_ = sorted({abs(x) for c in cnf for x in c})
    labels = [2_000_000 + seed * 100 + 17 * i for i in range(1, len(vars_) + 1)]
    rng.shuffle(labels)
    mp = dict(zip(vars_, labels))
    out = []
    for clause in cnf:
        z = [mp[abs(x)] if x > 0 else -mp[abs(x)] for x in clause]
        rng.shuffle(z)
        out.append(z)
    rng.shuffle(out)
    return out


def max_clause_width(cnf):
    return max(len(c) for c in cnf)


def graph_degree_summary(adj, right_n):
    rd = [0] * right_n
    for row in adj:
        for v in row:
            rd[v] += 1
    return {
        'left_degree_max': max(len(row) for row in adj),
        'right_degree_min': min(rd),
        'right_degree_max': max(rd),
    }


def build_population():
    cases = []
    audit = {'seed_base': SEED_BASE, 'hard': []}
    for idx, n in enumerate(N_VALUES):
        adj, exp = hard_expander(n)
        cnf = transport(graph_php_cnf(adj), SEED_BASE + 10_000 + idx)
        hard_meta = {
            'literature_family': 'Ben-Sasson-Wigderson G-PHP bounded-degree boundary expander',
            'm': n + 1, 'n': n, 'left_degree': 5,
            'r': exp['r'], 'e': exp['e'],
            'resolution_width_lower_bound': exp['r'] / 2,
            'max_input_clause_width': max_clause_width(cnf),
            'expansion_checked_subsets': exp['checked_subsets'],
            'search_attempt': exp['attempt'],
            'degree_summary': graph_degree_summary(adj, n),
        }
        cases.append({
            'id': f'hard-n{n}', 'lane': 'HARD_UNSAT_EXPANDER', 'truth': 'UNSAT',
            'n_parameter': n, 'cnf': cnf, 'hardness': hard_meta
        })
        audit['hard'].append({'n': n, **hard_meta})

        h_adj = hall_unsat(n)
        h_cnf = transport(graph_php_cnf(h_adj), SEED_BASE + 20_000 + idx)
        cases.append({
            'id': f'hall-control-n{n}', 'lane': 'HALL_UNSAT_CONTROL', 'truth': 'UNSAT',
            'n_parameter': n, 'cnf': h_cnf,
            'planted_deficiency': {'S_size': 3, 'N_size': 2},
            'degree_summary': graph_degree_summary(h_adj, n)
        })

        s_adj = sat_cycle(n)
        s_cnf = transport(graph_php_cnf(s_adj), SEED_BASE + 30_000 + idx)
        cases.append({
            'id': f'sat-control-n{n}', 'lane': 'SAT_MATCHING_CONTROL', 'truth': 'SAT',
            'n_parameter': n, 'cnf': s_cnf,
            'planted_matching_exists': True,
            'degree_summary': graph_degree_summary(s_adj, n)
        })

    payload = {'artifact': 'GRAPH_PHP_HALL_QUOTIENT_POPULATION_V1', 'cases': cases}
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    payload['population_sha256'] = hashlib.sha256(raw).hexdigest()
    return payload, audit


if __name__ == '__main__':
    population, audit = build_population()
    (ROOT / 'population.json').write_text(json.dumps(population, indent=2, sort_keys=True), encoding='utf-8')
    (ROOT / 'population_audit.json').write_text(json.dumps(audit, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps({
        'cases': len(population['cases']),
        'population_sha256': population['population_sha256'],
        'hard_attempts': {str(x['n']): x['search_attempt'] for x in audit['hard']},
        'hard_width_lb': {str(x['n']): x['resolution_width_lower_bound'] for x in audit['hard']}
    }, sort_keys=True))

