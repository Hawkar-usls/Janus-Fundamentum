from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as historical_source
from research.tools.apma_uf20_016_025_one_shot_class_coverage_wl_replication import candidate as panel

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_REVIEW_2026-09-17_v1.0.json'
PARENT = ROOT / 'research/TRUMP_UF20_016_025_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_RESULT_2026-09-17_v1.0.json'
HIST = ROOT / 'research/TRUMP_UF20_WL_POLYTIME_HISTORICAL_CLOSED_CONTROL_FALSIFIER_RESULT_2026-09-17_v1.0.json'
WL_CODE = ROOT / 'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
E3_CODE = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
RAW_BASIS = ROOT / 'research/tools/apma_unseen_basis/raw_relation_basis.py'
EXPECTED = {
    PREREG: '9daf44f5a94057fe1ec870776e47963cd0d30c8f',
    REVIEW: '812d950fd31d725a36641e5385e0cc75b21f781c',
    PARENT: '15aa1bbb6b8bcd1f9820b46dcda2c92f1eb96fd4',
    WL_CODE: '6b697fd8b3de4c83f8226b06399b6bad99953d4e',
    E3_CODE: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
    RAW_BASIS: '63490c05ef3e91a4f682f75da26ff2af811839a6',
}
MECH = 'EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT'


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def rank(signatures: dict[Any, Any]) -> dict[Any, int]:
    vals = sorted(set(signatures.values()), key=repr)
    idx = {v: i for i, v in enumerate(vals)}
    return {k: idx[v] for k, v in signatures.items()}


def relation_signature(c: dict[str, Any]) -> str:
    rows = sorted(''.join(str(int(b)) for b in row) for row in c['allowed'])
    return f"a{len(c['scope'])}:" + '/'.join(rows)


def incidence(raw: dict[str, Any]):
    nodes = []
    adj: dict[tuple[str, Any], set[tuple[str, Any]]] = defaultdict(set)
    labels = {}
    for v in sorted(int(x) for x in raw['variables']):
        n = ('v', v); nodes.append(n); adj[n]; labels[n] = 'V'
    for c in raw['constraints']:
        cn = ('c', str(c['id'])); nodes.append(cn); adj[cn]; labels[cn] = 'C:' + relation_signature(c)
        for v in sorted({int(x) for x in c['scope']}):
            vn = ('v', v); adj[cn].add(vn); adj[vn].add(cn)
    return sorted(nodes, key=lambda n: (n[0], str(n[1]))), adj, labels


def wl1(nodes, adj, labels):
    colors = rank({n: (labels[n],) for n in nodes})
    while True:
        sig = {n: (colors[n], tuple(sorted(colors[x] for x in adj[n]))) for n in nodes}
        new = rank(sig)
        if len(set(new.values())) == len(set(colors.values())):
            return new
        colors = new


def wl2(nodes, adj, labels):
    vc = rank({n: (labels[n],) for n in nodes})
    pairs = list(itertools.product(nodes, nodes))
    colors = rank({(u, v): (vc[u], vc[v], int(u == v), int(v in adj[u])) for u, v in pairs})
    while True:
        sig = {}
        for u, v in pairs:
            sig[(u, v)] = (colors[(u, v)], tuple(sorted((colors[(u, w)], colors[(w, v)]) for w in nodes)))
        new = rank(sig)
        if len(set(new.values())) == len(set(colors.values())):
            return new
        colors = new


def color_maps(raw: dict[str, Any]):
    nodes, adj, labels = incidence(raw)
    vars_nodes = [n for n in nodes if n[0] == 'v']
    c1 = wl1(nodes, adj, labels); c2 = wl2(nodes, adj, labels)
    return ({int(v[1]): int(c1[v]) for v in vars_nodes}, {int(v[1]): int(c2[(v, v)]) for v in vars_nodes})


def constraint_key(scope, rows):
    scope = list(scope)
    order = sorted(range(len(scope)), key=lambda i: scope[i])
    ss = tuple(scope[i] for i in order)
    rr = sorted({tuple(tuple(row)[i] for i in order) for row in rows})
    return ss, tuple(rr)


def formula_key(raw: dict[str, Any]):
    keys = [constraint_key(c['scope'], c['allowed']) for c in raw['constraints']]
    return tuple(sorted(keys))


def swapped_key(raw: dict[str, Any], u: int, v: int):
    keys = []
    for c in raw['constraints']:
        scope = [v if x == u else u if x == v else x for x in c['scope']]
        keys.append(constraint_key(scope, c['allowed']))
    return tuple(sorted(keys))


def exact_edges(raw: dict[str, Any]):
    base = formula_key(raw)
    vs = sorted(int(x) for x in raw['variables'])
    out = []
    for i, u in enumerate(vs):
        for v in vs[i + 1:]:
            if swapped_key(raw, u, v) == base:
                out.append((u, v))
    return out


def check_raw(raw: dict[str, Any]) -> dict[str, Any]:
    one, two = color_maps(raw)
    edges = exact_edges(raw)
    rows = [{'edge': [u, v], 'wl1_same': one[u] == one[v], 'wl2_same': two[u] == two[v]} for u, v in edges]
    c1 = Counter(one.values()); c2 = Counter(two.values())
    discrete1 = all(n == 1 for n in c1.values()); discrete2 = all(n == 1 for n in c2.values())
    negative_sound = not edges if (discrete1 or discrete2) else True
    return {
        'edges': [list(e) for e in edges],
        'edge_rows': rows,
        'all_edges_wl1_same': all(r['wl1_same'] for r in rows),
        'all_edges_wl2_same': all(r['wl2_same'] for r in rows),
        'wl1_discrete': discrete1,
        'wl2_diagonal_discrete': discrete2,
        'discrete_negative_certificate_sound_on_raw': negative_sound,
    }


def fresh_raw_024() -> tuple[dict[str, Any], dict[str, Any]]:
    parent = json.loads(PARENT.read_text())
    prow = next(r for r in parent['holdout_rows'] if r['source'] == 'UF20_024')
    source_freeze = json.loads(panel.SOURCE_FREEZE.read_text())
    meta = next(r for r in source_freeze['source_receipts'] if r['source'] == 'UF20_024')
    path = ROOT / meta['committed_copy_path']
    clauses, formula_hash = panel.frozen.parse_and_formula_hash(path)
    if formula_hash != meta['canonical_formula_sha256']:
        raise RuntimeError('UF20_024_FORMULA_HASH_MISMATCH')
    projected = panel.frozen.projection_identity.normalize_projection('UF20_024', clauses)[0]
    reduced, _, _ = panel.frozen.generic_round(projected)
    return reduced, prow


def empirical_panel() -> list[dict[str, Any]]:
    hist = json.loads(HIST.read_text())
    unique, source_guard = historical_source.reconstruct_unique_raws()
    if not source_guard.get('ok'):
        raise RuntimeError('HISTORICAL_SOURCE_GUARD_FAILURE')
    rows = []
    for r in hist['control_rows']:
        if r['closing_mechanism'] != MECH:
            continue
        raw = unique[r['raw_sha256']]['raw']
        rows.append({'kind': 'HISTORICAL_E3_CONTROL', 'id': r['raw_sha256'], **check_raw(raw)})
    raw, prow = fresh_raw_024()
    rows.append({'kind': 'FRESH_UF20_024', 'id': 'UF20_024', 'parent_edges': prow['existing_portfolio']['E3']['generator_edges'], **check_raw(raw)})
    return rows


def exhaustive_small_graph_equivariance() -> dict[str, Any]:
    checked_graphs = 0
    checked_automorphisms = 0
    failures = []
    for n in range(1, 5):
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for mask in range(1 << len(edges)):
            adj = {i: set() for i in range(n)}
            for bit, (u, v) in enumerate(edges):
                if (mask >> bit) & 1:
                    adj[u].add(v); adj[v].add(u)
            for labelmask in range(1 << n):
                labels = {i: ('A' if ((labelmask >> i) & 1) else 'B') for i in range(n)}
                nodes = list(range(n)); c1 = wl1(nodes, adj, labels); c2 = wl2(nodes, adj, labels)
                checked_graphs += 1
                for perm in itertools.permutations(nodes):
                    if any(labels[i] != labels[perm[i]] for i in nodes):
                        continue
                    ok = True
                    for i in nodes:
                        mapped = {perm[x] for x in adj[i]}
                        if mapped != adj[perm[i]]:
                            ok = False; break
                    if not ok:
                        continue
                    checked_automorphisms += 1
                    if any(c1[i] != c1[perm[i]] for i in nodes):
                        failures.append({'n': n, 'kind': 'WL1'}); return {'checked_graphs': checked_graphs, 'checked_automorphisms': checked_automorphisms, 'failures': failures}
                    if any(c2[(i, i)] != c2[(perm[i], perm[i])] for i in nodes):
                        failures.append({'n': n, 'kind': 'WL2_DIAGONAL'}); return {'checked_graphs': checked_graphs, 'checked_automorphisms': checked_automorphisms, 'failures': failures}
    return {'checked_graphs': checked_graphs, 'checked_automorphisms': checked_automorphisms, 'failures': failures}


def main(candidate_path: str) -> dict[str, Any]:
    cand = json.loads(Path(candidate_path).read_text())
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    review = json.loads(REVIEW.read_text())
    if not all(bindings.values()) or review.get('review_verdict') != 'PASS_CLEAN_WL_E3_NECESSITY_BRIDGE_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE':
        return {'verdict': 'FAIL_INDEPENDENT_AUTHORITY_BINDING', 'bindings': bindings}
    if cand.get('verdict') != 'PASS_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE':
        return {'verdict': 'FAIL_CANDIDATE_DID_NOT_PASS', 'candidate_verdict': cand.get('verdict')}
    small = exhaustive_small_graph_equivariance()
    rows = empirical_panel()
    empirical_ok = all(r['all_edges_wl1_same'] and r['all_edges_wl2_same'] and r['discrete_negative_certificate_sound_on_raw'] and len(r['edges']) > 0 for r in rows)
    fresh = next(r for r in rows if r['kind'] == 'FRESH_UF20_024')
    fresh_exact = fresh['edges'] == fresh['parent_edges']
    cert = cand.get('structural_certificate', {})
    cert_ok = set(cert) == {
        'C1_ENCODING_EQUIVARIANCE', 'C2_WL1_AUTOMORPHISM_INVARIANCE', 'C3_WL2_DIAGONAL_AUTOMORPHISM_INVARIANCE', 'C4_TRANSPOSITION_ENDPOINT_NECESSITY', 'C5_DISCRETE_NEGATIVE_CERTIFICATE'
    } and all(cert[k].get('proved') is True for k in cert)
    verdict = 'PASS_INDEPENDENT_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_VERIFICATION' if (not small['failures'] and empirical_ok and fresh_exact and cert_ok) else 'FAIL_INDEPENDENT_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_VERIFICATION'
    return {
        'verdict': verdict,
        'candidate_imported': False,
        'authority_bindings': bindings,
        'small_graph_equivariance': small,
        'empirical_rows': rows,
        'empirical_ok': empirical_ok,
        'fresh_parent_edges_exact': fresh_exact,
        'structural_certificate_shape_ok': cert_ok,
        'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED', 'WL_NONDISCRETE_SUFFICIENCY_FOR_E3': 'NOT_PROVED'},
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--candidate', required=True); args = ap.parse_args()
    print(json.dumps(main(args.candidate), sort_keys=True, separators=(',', ':')))
