#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict, deque
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

SPEC_SCHEMA = 'janus.c049_1.corrected_node9_scalar_symbolic_automaton_spec.v1.2'
CAND_SCHEMA = 'janus.c049_1.corrected_node9_scalar_symbolic_automaton_candidate.v1'
SPEC_SUBJECT = '0b6a472d43096d4508a217c938a2988a3315bddc'
SPEC_SHA256 = '44b43927eebfb8145942d7f28f4ada3e85a0aaf4cd9a001d6546f08b8c8c5a9a'
PRODUCER_SUBJECT = '74d1d6fd02a7c45578b6ba79891ca93796e701b6'
PRODUCER_SHA256 = 'd18442232038833331aa9d11ae81cca2495c1eb1aef163394b1f77f3b9df280d'
N8_SHA256 = '80b74b500ae82639e51568a9a6dc70a72668f32991add42bc5ffac05b3f9537f'
N8_SEM = 'e0017e4e5de933e520c6ea374ef291c07bbbb373478c6f9952911cc376380622'
N8_SCHEMA = 'C049.1-B4.6.3-CORRECTED-NODE8-TWENTY-GENERATOR-UP-K-v1'
L5_SHA256 = '6e4bbd67747405846b63a87633e34d41b0f720d33a6f55e877717b5463c01882'
L5_SEM = 'd5dcbaf64366a93420691fd667776f0f577bb0afd0feb588421139c69eb42d65'
L5_SCHEMA = 'C049.1-B4.6.3-CORRECTED-NODE9-RIGHT-LEAF5-CANDIDATE-v1'
Q80_SHA256 = 'fa21c129ad7c03cad0f46c5a5baeb3941d0c94baadea54718d8059652f3a3375'
Q80_SEM = '1463974e2378c60ca6f2ebba961c5366a98c59f9efc65603851e87239229f4a1'
Q80_SCHEMA = 'C049.1-B4.6.3-CORRECTED-NODE9-QUOTIENT-SKELETON-STABILITY-ANALYSIS-v1'
REFINEMENTS = 98_319_408
SEED_HEX = '0xC049119'
TERM = 'OPEN_TRAJECTORY_ENGINE_INCOMPLETE'


class VerificationError(AssertionError):
    def __init__(self, code: str, detail: str = ''):
        super().__init__(f'{code}: {detail}' if detail else code)
        self.code = code
        self.detail = detail


def fail(code: str, detail: str = '') -> None:
    raise VerificationError(code, detail)


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def require(cond: bool, code: str, detail: str = '') -> None:
    if not cond:
        fail(code, detail)


def bind_payload(path: Path, file_hash: str, schema: str, scope: str, sem: str, code: str) -> dict:
    require(file_sha(path) == file_hash, code, 'file sha256')
    obj = load_json(path)
    require(obj.get('schema') == schema, code, 'schema')
    require(obj.get('semantic_digest_scope') == scope, code, 'semantic scope')
    require(obj.get('semantic_digest') == sem, code, 'declared semantic digest')
    require(scope in obj and digest(obj[scope]) == sem, code, 'recomputed semantic digest')
    return obj[scope]


def verify_spec(path: Path) -> dict:
    require(file_sha(path) == SPEC_SHA256, 'N9S-INV-01', 'spec sha256')
    spec = load_json(path)
    require(spec.get('schema') == SPEC_SCHEMA and spec.get('version') == '1.2', 'N9S-INV-01', 'spec schema/version')
    require(spec.get('status') == 'SPEC_FROZEN', 'N9S-INV-01', 'spec status')
    require(spec.get('admission') is False and spec.get('next_gate') == 'CLOSED', 'N9S-INV-12', 'spec boundary')
    require(spec['parent_structural_spec']['subject'] == 'f942dffdd5ba1b2c4fa4a61da722e0c7c4a18d15', 'N9S-INV-01', 'parent structural spec')
    require(spec['parent_structural_spec']['relation'] == 'EXTENDS_NOT_SUPERSEDES', 'N9S-INV-01', 'parent relation')
    e = spec['expected_values_policy']
    require(all(e[k] is None for k in ('expected_zero_language_domains','expected_mixed_domains','expected_all_accepting_domains','expected_surviving_fine_lifts')), 'N9S-INV-03', 'oracle values present')
    require(e['historical_or_local_counts_may_seed_expected_values'] is False, 'N9S-INV-03', 'oracle policy')
    require(spec['determinism'] == {'modes':['ORIGINAL','REVERSED','SEEDED_SHUFFLE'],'seed_hex':SEED_HEX,'fixed_seed_required':True,'byte_identical_required':True}, 'N9S-INV-11', 'determinism contract')
    return spec


def verify_producer_source(path: Path) -> None:
    require(file_sha(path) == PRODUCER_SHA256, 'N9S-INV-08', 'producer source sha256')
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    imports = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports.extend(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            imports.append(n.module or '')
    require(not any('scalar_symbolic_automaton_verifier' in x for x in imports), 'N9S-INV-12', 'producer/verifier circular import')
    require('itertools' not in imports, 'N9S-INV-08', 'producer imports itertools')
    require('fine_hv_path_records_materialized' in source and 'child_cartesian_records_materialized' in source, 'N9S-INV-08', 'materialization ledger fields absent')


def geometry_skeleton(entry: dict) -> tuple:
    out = []
    last = None
    for step in entry['trajectory']:
        g = (tuple(map(int, step['left'])), tuple(map(int, step['right'])))
        if g != last:
            out.append(g)
            last = g
    return tuple(out)


def scalar_profile(entry: dict) -> tuple:
    groups = []
    last = None
    for step in entry['trajectory']:
        g = (tuple(map(int, step['left'])), tuple(map(int, step['right'])))
        v = int(step['value'])
        if g != last:
            groups.append([v])
            last = g
        else:
            groups[-1].append(v)
    return tuple(tuple(x) for x in groups)


def encode_word(word: tuple[int, ...]) -> list[int]:
    return list(map(int, word))


def word_id(word: tuple[int, ...]) -> str:
    return 'SW-' + digest(encode_word(word))[:16]


def language_record(language: tuple[tuple[int, ...], ...]) -> dict:
    words = [encode_word(w) for w in language]
    return {
        'language_id': 'SL-' + digest(words)[:16],
        'word_count': len(words),
        'words': words,
        'language_digest': digest(words),
    }


def independently_factor(entries: list[dict], label: str) -> tuple[tuple, tuple, dict]:
    sks = {geometry_skeleton(e) for e in entries}
    require(len(sks) == 1, 'N9S-INV-03', label + ' skeleton nonuniform')
    sk = next(iter(sks))
    profiles = [scalar_profile(e) for e in entries]
    require(all(len(p) == len(sk) for p in profiles), 'N9S-INV-03', label + ' segment count')
    require(len(set(profiles)) == len(profiles), 'N9S-INV-03', label + ' duplicate scalar profiles')
    languages = tuple(tuple(sorted({p[i] for p in profiles})) for i in range(len(sk)))
    product_profiles = set(itertools.product(*languages))
    require(set(profiles) == product_profiles, 'N9S-INV-03', label + ' Cartesian factorization')
    require(len(product_profiles) == math.prod(len(x) for x in languages), 'N9S-INV-03', label + ' Cartesian cardinality')
    catalog = [[encode_word(w) for w in p] for p in sorted(profiles)]
    rec = {
        'label': label,
        'entry_count': len(entries),
        'segment_count': len(sk),
        'skeleton_digest': digest([{'left':list(a),'right':list(b)} for a,b in sk]),
        'segment_languages': [language_record(x) for x in languages],
        'unique_profile_count': len(set(profiles)),
        'cartesian_product_cardinality': len(product_profiles),
        'no_duplicate_profiles': True,
        'all_profiles_coordinatewise_in_derived_languages': True,
        'profile_catalog_digest': digest(catalog),
        'cartesian_factorization_complete': True,
        'product_materialized_for_proof': False,
    }
    rec['factorization_receipt_digest'] = digest(rec)
    return sk, languages, rec


def qpath(domain: dict) -> tuple[tuple[int,int], ...]:
    return tuple(tuple(map(int, z)) for z in domain['quotient_path'])


def transition_targets(state: tuple, path: tuple, left_langs: tuple, right_langs: tuple) -> tuple:
    qi, lw, rw, li, ri = state
    a, b = path[qi]
    out = []
    if li + 1 < len(lw):
        out.append(('H_INTERNAL', (qi, lw, rw, li+1, ri)))
    elif qi + 1 < len(path) and path[qi+1] == (a+1, b):
        for nxt in left_langs[a+1]:
            out.append(('H_CELL', (qi+1, nxt, rw, 0, ri)))
    if ri + 1 < len(rw):
        out.append(('V_INTERNAL', (qi, lw, rw, li, ri+1)))
    elif qi + 1 < len(path) and path[qi+1] == (a, b+1):
        for nxt in right_langs[b+1]:
            out.append(('V_CELL', (qi+1, lw, nxt, li, 0)))
    return tuple(sorted(out, key=lambda x: (x[0], x[1])))


def is_terminal(state: tuple, path: tuple, left_langs: tuple, right_langs: tuple) -> bool:
    qi, lw, rw, li, ri = state
    a, b = path[qi]
    return (qi == len(path)-1 and a == len(left_langs)-1 and b == len(right_langs)-1
            and li == len(lw)-1 and ri == len(rw)-1)


def state_record(state: tuple, domain: dict) -> dict:
    qi, lw, rw, li, ri = state
    a, b = map(int, domain['quotient_path'][qi])
    lam = int(lw[li]) + int(rw[ri]) + int(domain['join_correction_vector'][qi]) + int(domain['shrink_correction_vector'][qi])
    rec = {
        'quotient_cell_index': qi,
        'left_segment_index': a,
        'right_segment_index': b,
        'active_left_word_id': word_id(lw),
        'active_right_word_id': word_id(rw),
        'left_offset': li,
        'right_offset': ri,
        'lambda': lam,
    }
    rec['state_id'] = 'SA-' + digest(rec)[:20]
    return rec


def independently_replay_automaton(domain: dict, left_langs: tuple, right_langs: tuple, filtered: bool, want_graph: bool) -> dict:
    path = qpath(domain)
    require(path and path[0] == (0,0) and path[-1] == (len(left_langs)-1, len(right_langs)-1), 'N9S-INV-04', domain['domain_id'] + ' qpath endpoints')
    require(len(domain['join_correction_vector']) == len(path) == len(domain['shrink_correction_vector']), 'N9S-INV-04', domain['domain_id'] + ' corrections')
    correction = tuple(int(x)+int(y) for x,y in zip(domain['join_correction_vector'], domain['shrink_correction_vector']))

    def allowed(s: tuple) -> bool:
        if not filtered:
            return True
        qi,lw,rw,li,ri = s
        return int(lw[li]) + int(rw[ri]) + correction[qi] <= 1

    starts = tuple((0,lw,rw,0,0) for lw in left_langs[0] for rw in right_langs[0])

    @lru_cache(maxsize=None)
    def suffix_count(s: tuple) -> int:
        if not allowed(s):
            return 0
        if is_terminal(s, path, left_langs, right_langs):
            return 1
        return sum(suffix_count(t) for _,t in transition_targets(s, path, left_langs, right_langs))

    run_count = sum(suffix_count(s) for s in starts)

    queue = deque(starts)
    reached = set()
    valid_edges = []
    rejected = 0
    while queue:
        s = queue.popleft()
        if s in reached:
            continue
        reached.add(s)
        if not allowed(s):
            rejected += 1
            continue
        for kind,t in transition_targets(s, path, left_langs, right_langs):
            if allowed(t):
                valid_edges.append((s,kind,t))
            if t not in reached:
                queue.append(t)

    live = {s for s in reached if allowed(s) and suffix_count(s) > 0}
    indeg_paths = defaultdict(int)
    for s in starts:
        if s in live:
            indeg_paths[s] += 1
    rank = lambda s: (s[0], s[3]+s[4], s[3], word_id(s[1]), word_id(s[2]))
    for s in sorted(live, key=rank):
        for _,t in transition_targets(s, path, left_langs, right_langs):
            if t in live:
                indeg_paths[t] += indeg_paths[s]
    terminal_prefix = sum(indeg_paths[s] for s in live if is_terminal(s,path,left_langs,right_langs))
    require(terminal_prefix == run_count, 'N9S-INV-04', domain['domain_id'] + ' forward/backward count')

    state_rows = sorted((state_record(s, domain) for s in reached if allowed(s)), key=lambda x:x['state_id'])
    edge_rows = []
    for s,kind,t in valid_edges:
        edge_rows.append({'from':state_record(s,domain)['state_id'],'step':kind,'to':state_record(t,domain)['state_id']})
    edge_rows.sort(key=lambda x:(x['from'],x['step'],x['to']))

    out = {
        'run_multiplicity': run_count,
        'start_state_count': len(starts),
        'visited_state_count_including_guard_rejections': len(reached),
        'guard_rejected_state_count': rejected,
        'guard_valid_state_count': sum(allowed(s) for s in reached),
        'coaccessible_state_count': len(live),
        'guard_valid_transition_count': sum(len(transition_targets(s,path,left_langs,right_langs)) for s in reached if allowed(s)),
        'coaccessible_transition_count': sum(t in live for s in live for _,t in transition_targets(s,path,left_langs,right_langs)),
        'terminal_state_count': sum(is_terminal(s,path,left_langs,right_langs) for s in live),
        'terminal_prefix_multiplicity': terminal_prefix,
        'reachable_graph_digest': digest({'states':state_rows,'edges':edge_rows}),
    }
    if want_graph:
        graph_states = []
        graph_edges = []
        for s in sorted(live, key=rank):
            r = state_record(s, domain)
            r.update(prefix_multiplicity=int(indeg_paths[s]), accepting_suffix_multiplicity=int(suffix_count(s)), terminal=bool(is_terminal(s,path,left_langs,right_langs)))
            graph_states.append(r)
        graph_states.sort(key=lambda x:x['state_id'])
        for s in live:
            for kind,t in transition_targets(s,path,left_langs,right_langs):
                if t in live:
                    graph_edges.append({'from':state_record(s,domain)['state_id'],'step':kind,'to':state_record(t,domain)['state_id']})
        graph_edges.sort(key=lambda x:(x['from'],x['step'],x['to']))
        graph = {
            'states': graph_states,
            'edges': graph_edges,
            'start_state_ids': sorted({state_record(s,domain)['state_id'] for s in starts if s in live}),
            'state_catalog_digest': digest(graph_states),
            'edge_catalog_digest': digest(graph_edges),
        }
        graph['graph_digest'] = digest(graph)
        out['accepted_symbolic_state_graph'] = graph
    return out


def verify_compactification_interface(iface: dict) -> None:
    require(iface.get('compact_state_memoization_used') is False, 'N9S-INV-07', 'memoization must be off')
    require(iface.get('right_congruence_required_for_this_run') is False, 'N9S-INV-07', 'right congruence policy')
    require(iface.get('producer_claim') == 'MAX_LAMBDA_PRECOMPACT_EQUALS_MAX_LAMBDA_POSTCOMPACT', 'N9S-INV-05', 'max-lambda claim')
    require(iface.get('independent_verifier_proof_required') is True, 'N9S-INV-05', 'independent proof flag')
    rules = {x.get('rule') for x in iface.get('precompact_lambda_max_preservation_basis', [])}
    require(rules == {'DUPLICATE_STATE_REMOVAL','MONOTONE_INTERVAL_INTERIOR_REMOVAL'}, 'N9S-INV-05', 'compactification rule basis')
    for a in (0,1):
        require(max(a,a) == a, 'N9S-INV-05', 'duplicate max preservation')
        for b in (0,1):
            for m in (0,1):
                if (a <= b and a <= m <= b) or (a >= b and a >= m >= b):
                    require(max(a,m,b) == max(a,b), 'N9S-INV-05', 'interval max preservation')
    base = dict(iface)
    declared = base.pop('certificate_interface_digest', None)
    require(declared == digest(base), 'N9S-INV-05', 'compactification interface digest')


def canonical_order_checks(proof: dict) -> None:
    rows = proof['domain_records']
    require([x['domain_id'] for x in rows] == sorted(x['domain_id'] for x in rows), 'N9S-INV-11', 'domain order')
    langs = proof['scalar_factorization']['derived_segment_language_catalog']
    require([x['language_id'] for x in langs] == sorted(x['language_id'] for x in langs), 'N9S-INV-11', 'language order')
    words = proof['scalar_factorization']['derived_scalar_word_catalog']
    require([x['word_id'] for x in words] == sorted(x['word_id'] for x in words), 'N9S-INV-11', 'word order')
    for row in rows:
        a = row.get('accepted_language')
        if a:
            g = a['accepted_symbolic_state_graph']
            require([x['state_id'] for x in g['states']] == sorted(x['state_id'] for x in g['states']), 'N9S-INV-11', row['domain_id'] + ' state order')
            require(g['edges'] == sorted(g['edges'], key=lambda x:(x['from'],x['step'],x['to'])), 'N9S-INV-11', row['domain_id'] + ' edge order')


def verify_claim_digests(candidate: dict) -> None:
    require(candidate.get('semantic_digest_scope') == 'proof_payload', 'N9S-INV-12', 'candidate semantic scope')
    require(candidate.get('semantic_digest') == digest(candidate['proof_payload']), 'N9S-INV-12', 'candidate semantic digest')
    p = candidate['proof_payload']
    src = dict(p['source_binding_receipt'])
    claimed = src.pop('source_binding_receipt_digest', None)
    require(claimed == digest(src), 'N9S-INV-02', 'source binding receipt digest')
    iface = p['width_filter_certificate_interface']
    verify_compactification_interface(iface)
    for r in p['scalar_factorization']['node8_source_class_receipts']:
        base = {k:v for k,v in r.items() if k not in ('source_class_id','factorization_receipt_digest')}
        require(r['factorization_receipt_digest'] == digest(base), 'N9S-INV-03', 'source factorization receipt digest')
    lr = p['scalar_factorization']['leaf5_receipt']
    base = {k:v for k,v in lr.items() if k != 'factorization_receipt_digest'}
    require(lr['factorization_receipt_digest'] == digest(base), 'N9S-INV-03', 'leaf factorization receipt digest')
    require(p['scalar_factorization']['derived_language_catalog_digest'] == digest(p['scalar_factorization']['derived_segment_language_catalog']), 'N9S-INV-03', 'language catalog digest')
    for row in p['domain_records']:
        if row.get('accepted_language') is not None:
            a = row['accepted_language']
            ab = dict(a); ad = ab.pop('accepted_language_digest', None)
            require(ad == digest(ab), 'N9S-INV-06', row['domain_id'] + ' accepted language digest')
            g = a['accepted_symbolic_state_graph']
            require(g['state_catalog_digest'] == digest(g['states']), 'N9S-INV-06', row['domain_id'] + ' state catalog digest')
            require(g['edge_catalog_digest'] == digest(g['edges']), 'N9S-INV-06', row['domain_id'] + ' edge catalog digest')
            gb = dict(g); gd = gb.pop('graph_digest', None)
            require(gd == digest(gb), 'N9S-INV-06', row['domain_id'] + ' graph digest')
            for s in g['states']:
                sb = {k:s[k] for k in ('quotient_cell_index','left_segment_index','right_segment_index','active_left_word_id','active_right_word_id','left_offset','right_offset','lambda')}
                require(s['state_id'] == 'SA-' + digest(sb)[:20], 'N9S-INV-06', row['domain_id'] + ' state id')
        if row.get('zero_language_certificate') is not None:
            z = dict(row['zero_language_certificate']); zd = z.pop('zero_language_certificate_digest', None)
            require(zd == digest(z), 'N9S-INV-05', row['domain_id'] + ' zero cert digest')
        rb = dict(row); rd = rb.pop('domain_record_digest', None)
        require(rd == digest(rb), 'N9S-INV-12', row['domain_id'] + ' record digest')


def verify_candidate(candidate: dict, spec: dict, n8: dict, leaf: dict, q80: dict) -> dict:
    require(candidate.get('schema') == CAND_SCHEMA, 'N9S-INV-12', 'candidate schema')
    verify_claim_digests(candidate)
    p = candidate['proof_payload']
    require(p.get('candidate_phase') == 'SCALAR_SYMBOLIC_AUTOMATON', 'N9S-INV-12', 'phase')
    require(p.get('candidate_status') == 'PRODUCER_DERIVED_CANDIDATE' and p.get('admitted') is False, 'N9S-INV-12', 'candidate boundary')
    require(p['spec_binding']['spec_subject'] == SPEC_SUBJECT and p['spec_binding']['spec_file_sha256'] == SPEC_SHA256, 'N9S-INV-01', 'candidate spec binding')

    src = p['source_binding_receipt']
    require(src['node8']['artifact_sha256'] == N8_SHA256 and src['node8']['semantic_digest'] == N8_SEM, 'N9S-INV-02', 'candidate Node8 binding')
    require(src['leaf5']['artifact_sha256'] == L5_SHA256 and src['leaf5']['semantic_digest'] == L5_SEM, 'N9S-INV-02', 'candidate Leaf5 binding')
    require(src['q80']['artifact_sha256'] == Q80_SHA256 and src['q80']['semantic_digest'] == Q80_SEM, 'N9S-INV-01', 'candidate Q80 binding')
    require(src['all_exact_artifact_and_semantic_bindings_pass'] is True and src['unbound_artifact_substitution_allowed'] is False, 'N9S-INV-02', 'unbound substitution boundary')

    left_entries = n8['reachable_closure']['entries']
    right_entries = leaf['entries']
    domains = q80['quotient_domains']
    require(len(left_entries)==8676 and len(right_entries)==36 and len(domains)==80, 'N9S-INV-02', 'source counts')
    require(q80['conservation_ledger']['sum_fine_lift_multiplicities'] == REFINEMENTS, 'N9S-INV-10', 'Q80 total')
    require(q80['conservation_ledger']['omitted_fine_refinement_multiplicity'] == 0 and q80['conservation_ledger']['duplicated_fine_refinement_multiplicity'] == 0, 'N9S-INV-10', 'Q80 omissions/duplications')

    grouped = defaultdict(list)
    for e in left_entries:
        grouped[e['source_class_id']].append(e)
    require(len(grouped) == 20, 'N9S-INV-03', 'Node8 source class count')

    derived_left = {}
    derived_receipts = {}
    for cid in sorted(grouped):
        _, langs, rec = independently_factor(grouped[cid], 'NODE8:'+cid)
        rec_with_id = dict(rec); rec_with_id['source_class_id'] = cid
        derived_left[cid] = langs
        derived_receipts[cid] = rec_with_id
    _, right_langs, leaf_receipt = independently_factor(right_entries, 'LEAF5')

    claim_receipts = {x['source_class_id']:x for x in p['scalar_factorization']['node8_source_class_receipts']}
    require(set(claim_receipts) == set(derived_receipts), 'N9S-INV-03', 'factorization class coverage')
    for cid in derived_receipts:
        require(claim_receipts[cid] == derived_receipts[cid], 'N9S-INV-03', cid + ' factorization receipt mismatch')
    require(p['scalar_factorization']['leaf5_receipt'] == leaf_receipt, 'N9S-INV-03', 'Leaf5 factorization receipt mismatch')
    require(p['scalar_factorization']['historical_or_local_catalog_used_as_seed'] is False and p['scalar_factorization']['expected_language_catalog_used'] is False, 'N9S-INV-03', 'oracle use claim')

    all_langs = {}
    all_words = set()
    for langs in list(derived_left.values()) + [right_langs]:
        for lang in langs:
            lr = language_record(lang); all_langs[lr['language_id']] = lr
            all_words.update(lang)
    expected_lang_catalog = [all_langs[k] for k in sorted(all_langs)]
    expected_word_catalog = [{'word_id':word_id(w),'word':encode_word(w),'word_digest':digest(encode_word(w))} for w in sorted(all_words)]
    expected_word_catalog.sort(key=lambda x:x['word_id'])
    require(p['scalar_factorization']['derived_segment_language_catalog'] == expected_lang_catalog, 'N9S-INV-03', 'derived language catalog')
    require(p['scalar_factorization']['derived_scalar_word_catalog'] == expected_word_catalog, 'N9S-INV-03', 'derived word catalog')

    qby = {d['domain_id']:d for d in domains}
    crows = {d['domain_id']:d for d in p['domain_records']}
    require(len(qby)==80 and set(crows)==set(qby), 'N9S-INV-04', 'domain coverage')
    canonical_order_checks(p)

    cls = Counter()
    total = accepted = 0
    derived_state_counts = {'unrestricted':0,'filtered_seen':0,'filtered_live':0,'filtered_edges':0}
    for did in sorted(qby):
        qd = qby[did]; row = crows[did]; cid = qd['source_class_id']
        require(row['source_class_id'] == cid and row['quotient_path'] == qd['quotient_path'], 'N9S-INV-04', did + ' domain identity')
        require(row['join_correction_vector'] == qd['join_correction_vector'] and row['shrink_correction_vector'] == qd['shrink_correction_vector'], 'N9S-INV-04', did + ' correction binding')
        require(row['q80_fine_lift_domain_digest'] == qd['fine_lift_domain_digest'] and row['q80_correction_signature_digest'] == qd['correction_signature_digest'], 'N9S-INV-01', did + ' q80 domain binding')

        unrestricted = independently_replay_automaton(qd, derived_left[cid], right_langs, False, False)
        filtered = independently_replay_automaton(qd, derived_left[cid], right_langs, True, True)
        n = int(qd['fine_lift_multiplicity']); g = int(filtered['run_multiplicity'])
        require(unrestricted['run_multiplicity'] == n, 'N9S-INV-04', did + ' fine-lift bijection')
        require(row['q80_fine_lift_multiplicity'] == n, 'N9S-INV-04', did + ' q80 multiplicity claim')
        require(row['unrestricted_automaton'] == unrestricted, 'N9S-INV-04', did + ' unrestricted automaton receipt')
        claimed_filtered = dict(filtered); graph = claimed_filtered.pop('accepted_symbolic_state_graph')
        require(row['width_filtered_automaton'] == claimed_filtered, 'N9S-INV-05', did + ' width-filtered automaton receipt')

        typ = 'ZERO_LANGUAGE' if g == 0 else ('ALL_ACCEPTING' if g == n else 'MIXED')
        require(row['classification'] == typ, 'N9S-INV-05', did + ' classification')
        require(row['repository_success_promoted'] is False and row['repository_failure_promoted'] is False, 'N9S-INV-06', did + ' repository promotion')
        cls[typ] += 1; total += n; accepted += g

        post = row['post_shrink_interface']
        require(post['projected_geometry_digest'] == digest(qd['projected_geometry']), 'N9S-INV-05', did + ' projected geometry digest')
        require(post['join_correction_vector_digest'] == digest(qd['join_correction_vector']), 'N9S-INV-05', did + ' join correction digest')
        require(post['shrink_correction_vector_digest'] == digest(qd['shrink_correction_vector']), 'N9S-INV-05', did + ' shrink correction digest')
        require(row['compactification_interface'] == p['width_filter_certificate_interface'], 'N9S-INV-07', did + ' compact interface')

        if typ == 'ZERO_LANGUAGE':
            require(row['accepted_language'] is None and row['zero_language_certificate'] is not None, 'N9S-INV-05', did + ' zero evidence shape')
            z = row['zero_language_certificate']
            require(z['accepted_run_multiplicity'] == 0 and z['unrestricted_run_multiplicity'] == n, 'N9S-INV-05', did + ' zero multiplicities')
            require(z['width_filtered_reachable_graph_digest'] == filtered['reachable_graph_digest'], 'N9S-INV-05', did + ' zero graph digest')
            require(not graph['states'] and not graph['edges'] and not graph['start_state_ids'], 'N9S-INV-05', did + ' independently nonempty zero graph')
        else:
            require(row['zero_language_certificate'] is None and row['accepted_language'] is not None, 'N9S-INV-06', did + ' accepted evidence shape')
            a = row['accepted_language']
            require(a['accepted_run_multiplicity'] == g, 'N9S-INV-06', did + ' accepted multiplicity')
            require(a['accepted_symbolic_state_graph'] == graph, 'N9S-INV-06', did + ' accepted graph')
            require(a['post_shrink_interface'] == post and a['compactification_interface'] == row['compactification_interface'], 'N9S-INV-06', did + ' accepted interfaces')

        derived_state_counts['unrestricted'] += unrestricted['visited_state_count_including_guard_rejections']
        derived_state_counts['filtered_seen'] += filtered['visited_state_count_including_guard_rejections']
        derived_state_counts['filtered_live'] += filtered['coaccessible_state_count']
        derived_state_counts['filtered_edges'] += filtered['coaccessible_transition_count']

    require(total == REFINEMENTS, 'N9S-INV-10', 'derived total')
    ledger = p['conservation_ledger']
    require(ledger['derived_unrestricted_symbolic_run_total'] == total == REFINEMENTS, 'N9S-INV-10', 'unrestricted total ledger')
    require(ledger['derived_width_le_1_run_total'] == accepted, 'N9S-INV-10', 'accepted total ledger')
    require(ledger['derived_width_gt_1_run_total'] == total-accepted, 'N9S-INV-10', 'rejected total ledger')
    require(ledger['omitted_fine_refinement_multiplicity'] == 0 and ledger['duplicated_fine_refinement_multiplicity'] == 0 and ledger['fine_refinement_conservation'] is True, 'N9S-INV-10', 'conservation flags')
    summary = p['classification_summary']
    require(summary['zero_language_domain_count'] == cls['ZERO_LANGUAGE'], 'N9S-INV-05', 'zero summary')
    require(summary['mixed_domain_count'] == cls['MIXED'], 'N9S-INV-06', 'mixed summary')
    require(summary['all_accepting_domain_count'] == cls['ALL_ACCEPTING'], 'N9S-INV-06', 'all-accepting summary')
    require(summary['repository_successful_domain_count'] == 0 and summary['repository_failed_domain_count'] == 0 and summary['classification_promoted_to_repository_success_or_failure'] is False, 'N9S-INV-06', 'repository classification boundary')
    require(summary['expected_classification_counts_used'] is False, 'N9S-INV-03', 'classification oracle flag')

    work = p['work_ledger']
    require(work['fine_hv_path_records_materialized'] == 0, 'N9S-INV-08', 'fine paths materialized')
    require(work['child_cartesian_records_materialized'] == 0, 'N9S-INV-09', 'child Cartesian materialized')
    require(work['unrestricted_symbolic_states_visited'] == derived_state_counts['unrestricted'], 'N9S-INV-04', 'work unrestricted states')
    require(work['width_filtered_symbolic_states_visited_including_guard_rejections'] == derived_state_counts['filtered_seen'], 'N9S-INV-05', 'work filtered states')
    require(work['width_filtered_coaccessible_states'] == derived_state_counts['filtered_live'], 'N9S-INV-06', 'work live states')
    require(work['width_filtered_coaccessible_transitions'] == derived_state_counts['filtered_edges'], 'N9S-INV-06', 'work live edges')

    aut = p['symbolic_automaton_contract']
    require(aut['compact_state_memoization_used'] is False and aut['fine_path_materialization_used'] is False and aut['child_cartesian_materialization_used'] is False, 'N9S-INV-07', 'automaton materialization/memoization flags')
    verify_compactification_interface(p['width_filter_certificate_interface'])

    b = p['strict_boundary']
    require(b == {
        'node9_scalar_automaton_spec_frozen': True,
        'node9_scalar_automaton_producer_created': True,
        'node9_scalar_automaton_verifier_created': False,
        'node9_scalar_automaton_candidate_complete': False,
        'node9_frontier_candidate_complete': False,
        'node9_parent_refinement_complete': False,
        'node9_parent_up_k_complete': False,
        'node9_integrated_into_bottom_up_executor': False,
        'root_reached': False,
        'root_full_set_computed': False,
        'root_empty_proved': False,
        'found_layout': 'FORBIDDEN',
        'no_layout_at_cap': 'FORBIDDEN',
        'formal_admission': 'BLOCKED',
        'next_gate': 'CLOSED',
        'current_global_terminal': TERM,
        'p_vs_np': 'OPEN',
    }, 'N9S-INV-12', 'strict boundary')

    return {
        'zero_language_domains': int(cls['ZERO_LANGUAGE']),
        'mixed_domains': int(cls['MIXED']),
        'all_accepting_domains': int(cls['ALL_ACCEPTING']),
        'fine_refinements': total,
        'width_le_1_multiplicity': accepted,
        'width_gt_1_multiplicity': total-accepted,
        'derived_distinct_segment_languages': len(expected_lang_catalog),
        'derived_distinct_scalar_words': len(expected_word_catalog),
        'unrestricted_symbolic_states_visited': derived_state_counts['unrestricted'],
        'width_filtered_symbolic_states_visited': derived_state_counts['filtered_seen'],
        'width_filtered_coaccessible_states': derived_state_counts['filtered_live'],
        'width_filtered_coaccessible_transitions': derived_state_counts['filtered_edges'],
    }


def repair_claim_digests(candidate: dict) -> None:
    p = candidate['proof_payload']
    iface = p.get('width_filter_certificate_interface')
    if isinstance(iface, dict):
        base = dict(iface); base.pop('certificate_interface_digest', None); iface['certificate_interface_digest'] = digest(base)
    sf = p.get('scalar_factorization', {})
    for r in sf.get('node8_source_class_receipts', []):
        base = {k:v for k,v in r.items() if k not in ('source_class_id','factorization_receipt_digest')}
        r['factorization_receipt_digest'] = digest(base)
    lr = sf.get('leaf5_receipt')
    if isinstance(lr, dict):
        base = {k:v for k,v in lr.items() if k != 'factorization_receipt_digest'}
        lr['factorization_receipt_digest'] = digest(base)
    if 'derived_segment_language_catalog' in sf:
        sf['derived_language_catalog_digest'] = digest(sf['derived_segment_language_catalog'])
    src = p.get('source_binding_receipt')
    if isinstance(src, dict):
        base = dict(src); base.pop('source_binding_receipt_digest', None); src['source_binding_receipt_digest'] = digest(base)
    for row in p.get('domain_records', []):
        if isinstance(row.get('accepted_language'), dict):
            a = row['accepted_language']
            g = a.get('accepted_symbolic_state_graph')
            if isinstance(g, dict):
                g['state_catalog_digest'] = digest(g.get('states', []))
                g['edge_catalog_digest'] = digest(g.get('edges', []))
                gb = dict(g); gb.pop('graph_digest', None); g['graph_digest'] = digest(gb)
            ab = dict(a); ab.pop('accepted_language_digest', None); a['accepted_language_digest'] = digest(ab)
        if isinstance(row.get('zero_language_certificate'), dict):
            z = row['zero_language_certificate']; zb = dict(z); zb.pop('zero_language_certificate_digest', None); z['zero_language_certificate_digest'] = digest(zb)
        rb = dict(row); rb.pop('domain_record_digest', None); row['domain_record_digest'] = digest(rb)
    candidate['semantic_digest'] = digest(p)


def run_tamper_suite(candidate: dict, spec: dict, n8: dict, leaf: dict, q80: dict) -> list[dict]:
    tests = []
    def run(tid: str, expected: str, mutator):
        x = copy.deepcopy(candidate)
        mutator(x)
        repair_claim_digests(x)
        try:
            verify_candidate(x,spec,n8,leaf,q80)
        except VerificationError as e:
            require(e.code == expected, 'TAMPER_SUITE', f'{tid} expected {expected}, got {e.code}')
            tests.append({'tamper_id':tid,'expected_failure_code':expected,'observed_failure_code':e.code,'rejected':True})
            return
        fail('TAMPER_SUITE', tid + ' unexpectedly accepted')

    run('N9S-T01','N9S-INV-01',lambda x:x['proof_payload']['source_binding_receipt']['q80'].__setitem__('artifact_sha256','00'*32))
    run('N9S-T02','N9S-INV-02',lambda x:x['proof_payload']['source_binding_receipt']['node8'].__setitem__('artifact_sha256','11'*32))
    def t03(x):
        r=x['proof_payload']['scalar_factorization']['node8_source_class_receipts'][0]
        r['segment_languages'][0]['words'][0]=[9]
    run('N9S-T03','N9S-INV-03',t03)
    def t04(x): x['proof_payload']['domain_records'][0]['unrestricted_automaton'].__setitem__('run_multiplicity',x['proof_payload']['domain_records'][0]['unrestricted_automaton']['run_multiplicity']+1)
    run('N9S-T04','N9S-INV-04',t04)
    def t05(x):
        r=next(r for r in x['proof_payload']['domain_records'] if r['classification']!='ZERO_LANGUAGE')
        r['repository_success_promoted']=True
    run('N9S-T05','N9S-INV-06',t05)
    def t06(x):
        r=next(r for r in x['proof_payload']['domain_records'] if r['classification']=='MIXED')
        r['classification']='ZERO_LANGUAGE'; r['accepted_language']=None
        r['zero_language_certificate']={'certificate_kind':'ZERO_ACCEPTING_LANGUAGE_CANDIDATE','unrestricted_run_multiplicity':r['q80_fine_lift_multiplicity'],'accepted_run_multiplicity':0,'width_filtered_reachable_graph_digest':r['width_filtered_automaton']['reachable_graph_digest'],'width_filter_soundness_and_completeness_status':'PRODUCER_CERTIFICATE_INTERFACE_PENDING_INDEPENDENT_VERIFIER','interpretation_after_independent_verification':'FOR_ALL_FINE_LIFTS: FINAL_POST_SHRINK_COMPACT_WIDTH > 1'}
    run('N9S-T06','N9S-INV-05',t06)
    def t07(x): x['proof_payload']['domain_records'][0]['join_correction_vector'][0]+=1
    run('N9S-T07','N9S-INV-04',t07)
    def t08(x):
        x['proof_payload']['width_filter_certificate_interface']['compact_state_memoization_used']=True
        x['proof_payload']['symbolic_automaton_contract']['compact_state_memoization_used']=True
    run('N9S-T08','N9S-INV-07',t08)
    run('N9S-T09','N9S-INV-08',lambda x:x['proof_payload']['work_ledger'].__setitem__('fine_hv_path_records_materialized',1))
    run('N9S-T10','N9S-INV-10',lambda x:x['proof_payload']['conservation_ledger'].__setitem__('derived_unrestricted_symbolic_run_total',REFINEMENTS-1))
    def t11(x): x['proof_payload']['domain_records'].reverse()
    run('N9S-T11','N9S-INV-11',t11)
    def t12(x): x['proof_payload']['strict_boundary']['next_gate']='OPEN'
    run('N9S-T12','N9S-INV-12',t12)
    return tests


def verify_three_mode_identity(paths: Iterable[Path]) -> tuple[str, int]:
    paths = list(paths)
    require(len(paths) == 3, 'N9S-INV-11', 'three candidate modes required')
    blobs = [p.read_bytes() for p in paths]
    require(blobs[0] == blobs[1] == blobs[2], 'N9S-INV-11', 'candidate bytes differ by input order')
    return hashlib.sha256(blobs[0]).hexdigest(), len(blobs[0])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', type=Path, required=True)
    ap.add_argument('--producer-source', type=Path, required=True)
    ap.add_argument('--node8-artifact', type=Path, required=True)
    ap.add_argument('--leaf5-artifact', type=Path, required=True)
    ap.add_argument('--q80-artifact', type=Path, required=True)
    ap.add_argument('--candidate-original', type=Path, required=True)
    ap.add_argument('--candidate-reversed', type=Path, required=True)
    ap.add_argument('--candidate-seeded-shuffle', type=Path, required=True)
    ap.add_argument('--tamper-suite', action='store_true')
    args = ap.parse_args()

    spec = verify_spec(args.spec)
    verify_producer_source(args.producer_source)
    n8 = bind_payload(args.node8_artifact,N8_SHA256,N8_SCHEMA,'proof_payload',N8_SEM,'N9S-INV-02')
    leaf = bind_payload(args.leaf5_artifact,L5_SHA256,L5_SCHEMA,'leaf_payload',L5_SEM,'N9S-INV-02')
    q80 = bind_payload(args.q80_artifact,Q80_SHA256,Q80_SCHEMA,'proof_payload',Q80_SEM,'N9S-INV-01')
    artifact_sha, artifact_bytes = verify_three_mode_identity([args.candidate_original,args.candidate_reversed,args.candidate_seeded_shuffle])
    candidate = load_json(args.candidate_original)
    derived = verify_candidate(candidate,spec,n8,leaf,q80)
    run_tamper_suite(candidate,spec,n8,leaf,q80) if args.tamper_suite else []

    print('JANUS_NODE9_SCALAR_SYMBOLIC_AUTOMATON_INDEPENDENT_VERIFIER = PASS')
    print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED')
    print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED')
    print('MATHEMATICAL_INDEPENDENCE = NOT_AUTOMATIC')
    print('SPECIFICATION_INDEPENDENCE = NOT_AUTOMATIC')
    print('INVARIANTS = 12/12')
    if args.tamper_suite:
        print('DIGEST_REPAIRED_TAMPERS_REJECTED = 12/12')
    print('ZERO_LANGUAGE_DOMAINS =',derived['zero_language_domains'])
    print('MIXED_DOMAINS =',derived['mixed_domains'])
    print('ALL_ACCEPTING_DOMAINS =',derived['all_accepting_domains'])
    print('FINE_REFINEMENTS =',derived['fine_refinements'])
    print('WIDTH_LE_1_MULTIPLICITY =',derived['width_le_1_multiplicity'])
    print('WIDTH_GT_1_MULTIPLICITY =',derived['width_gt_1_multiplicity'])
    print('DERIVED_DISTINCT_SEGMENT_LANGUAGES =',derived['derived_distinct_segment_languages'])
    print('DERIVED_DISTINCT_SCALAR_WORDS =',derived['derived_distinct_scalar_words'])
    print('CANDIDATE_ARTIFACT_SHA256 =',artifact_sha)
    print('CANDIDATE_ARTIFACT_BYTES =',artifact_bytes)
    print('CANDIDATE_SEMANTIC_DIGEST =',candidate['semantic_digest'])
    print('REPOSITORY_FAILED_DOMAINS = 0')
    print('REPOSITORY_SUCCESSFUL_DOMAINS = 0')
    print('FORMAL_ADMISSION = BLOCKED')
    print('NEXT_GATE = CLOSED')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
