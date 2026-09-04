#!/usr/bin/env python3
from collections import defaultdict
from itertools import combinations, product
import json


def lit_key(lit):
    return (abs(lit), 0 if lit > 0 else 1)


def canonical_clause(clause):
    s = {int(l) for l in clause if int(l) != 0}
    if any(-l in s for l in s):
        return None
    return tuple(sorted(s, key=lit_key))


def canonical_formula(clauses):
    out = set()
    for clause in clauses:
        c = canonical_clause(clause)
        if c is not None:
            out.add(c)
    return tuple(sorted(out, key=lambda c: (len(c), tuple(lit_key(l) for l in c))))


def variables(formula):
    return sorted({abs(l) for c in formula for l in c})


def exact_sat(formula):
    formula = canonical_formula(formula)
    if () in formula:
        return False
    vs = variables(formula)
    for bits in product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if all(any(a[abs(l)] if l > 0 else not a[abs(l)] for l in c) for c in formula):
            return True
    return False


class UnionFind:
    def __init__(self, elems):
        self.parent = {x: x for x in elems}

    def find(self, x):
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        lo, hi = sorted((ra, rb))
        self.parent[hi] = lo


def explicit_equality_classes(formula):
    formula = canonical_formula(formula)
    vs = variables(formula)
    uf = UnionFind(vs)
    binary = {frozenset(c) for c in formula if len(c) == 2}
    for c in list(binary):
        l1, l2 = tuple(c)
        if abs(l1) == abs(l2):
            continue
        # Only same-orientation variable equality is admitted:
        # (not u OR v) AND (u OR not v).  A same-sign pair would certify
        # anti-equivalence and MUST NOT be collapsed by this quotient.
        if l1 * l2 < 0 and frozenset((-l1, -l2)) in binary:
            uf.union(abs(l1), abs(l2))
    return {v: uf.find(v) for v in vs}


def dense_rename(formula):
    vs = variables(formula)
    ren = {v: i + 1 for i, v in enumerate(vs)}
    return canonical_formula(
        tuple((ren[abs(l)] if l > 0 else -ren[abs(l)]) for l in c)
        for c in formula
    )


def exact_congruence_quotient(formula):
    formula = canonical_formula(formula)
    cls = explicit_equality_classes(formula)
    substituted = []
    for c in formula:
        substituted.append(tuple(cls[abs(l)] if l > 0 else -cls[abs(l)] for l in c))
    quotient_pre_rename = canonical_formula(substituted)
    quotient = dense_rename(quotient_pre_rename)
    return quotient, cls


def quotient_signature(formula):
    q, _ = exact_congruence_quotient(formula)
    return q


def clause_pool(n=2):
    pool = []
    for width in range(1, min(3, n) + 1):
        for support in combinations(range(1, n + 1), width):
            for signs in product((-1, 1), repeat=width):
                pool.append(tuple(v * s for v, s in zip(support, signs)))
    return tuple(pool)


def base_formula_corpus():
    pool = clause_pool(2)
    corpus = [canonical_formula(())]
    for k in range(1, 4):
        for cs in combinations(pool, k):
            corpus.append(canonical_formula(cs))
    # 1 + C(8,1) + C(8,2) + C(8,3) = 93 canonical bases.
    assert len(corpus) == 93
    assert len(set(corpus)) == 93
    return corpus


def replace_var(formula, old, new, selector):
    out = []
    for ci, c in enumerate(formula):
        nc = []
        for li, l in enumerate(c):
            if abs(l) == old and selector(ci, li):
                nc.append(new if l > 0 else -new)
            else:
                nc.append(l)
        out.append(tuple(nc))
    return out


def equality_pair(u, v):
    return [(-u, v), (u, -v)]


def expand_with_certified_equalities(base, mode):
    base = canonical_formula(base)
    vs = variables(base)
    if not vs:
        return base
    n = max(vs)

    # Keep payload mutation separate from the equality certificates.  The
    # adversarial generator is not allowed to rewrite its own proof clauses.
    payload = list(base)
    equality_certificates = []
    for v in vs:
        c1 = n + v
        payload = replace_var(
            payload, v, c1,
            lambda ci, li, m=mode: ((ci + li + m) % 2 == 0),
        )
        equality_certificates.extend(equality_pair(v, c1))
        if mode >= 2:
            c2 = 2 * n + v
            payload = replace_var(
                payload, c1, c2,
                lambda ci, li, m=mode: ((2 * ci + li + m) % 3 == 0),
            )
            equality_certificates.extend(equality_pair(c1, c2))

    work = payload + equality_certificates
    if mode >= 2:
        work.extend(list(base))  # semantically redundant under the equalities.
        v0 = vs[0]
        work.append((v0, -v0))  # tautology; simplification must be inert.
    return canonical_formula(work)


def renamed(formula, shift):
    vs = variables(formula)
    mapping = {v: shift + 3 * i + 1 for i, v in enumerate(vs)}
    return canonical_formula(
        tuple(mapping[abs(l)] if l > 0 else -mapping[abs(l)] for l in c)
        for c in formula
    )


def equality_antiequality_contradiction(base):
    base = canonical_formula(base)
    vs = variables(base)
    if not vs:
        return base
    n = max(vs)
    v = vs[0]
    clone = n + v
    work = list(base)
    work.extend(equality_pair(v, clone))
    # Anti-equivalence pair is deliberately NOT unioned.  Once the certified
    # equality is substituted it becomes opposite units, preserving UNSAT.
    work.extend([(v, clone), (-v, -clone)])
    return canonical_formula(work)


def adversarial_corpus():
    out = []
    for i, base in enumerate(base_formula_corpus()):
        out.append(base)
        out.append(expand_with_certified_equalities(base, 1))
        out.append(expand_with_certified_equalities(base, 2))
        out.append(renamed(expand_with_certified_equalities(base, 2), 20 + 11 * i))
        if i % 9 == 0 and variables(base):
            out.append(equality_antiequality_contradiction(base))
    # Preserve distinct origins even when formulas coincide in a generated
    # lane; fiber grouping below is by decision representation, not origin id.
    return out


def audit():
    corpus = adversarial_corpus()
    fibers = defaultdict(list)
    preservation_mismatches = []

    for origin_id, f in enumerate(corpus):
        f = canonical_formula(f)
        q, classes = exact_congruence_quotient(f)
        sf = exact_sat(f)
        sq = exact_sat(q)
        if sf != sq:
            preservation_mismatches.append({
                'origin_id': origin_id,
                'formula': f,
                'quotient': q,
                'sat_formula': sf,
                'sat_quotient': sq,
                'classes': classes,
            })
        fibers[q].append((origin_id, f, sf))

    mixed = []
    nontrivial = 0
    max_fiber = 0
    for q, members in fibers.items():
        max_fiber = max(max_fiber, len(members))
        if len(members) > 1:
            nontrivial += 1
        vals = {m[2] for m in members}
        if len(vals) > 1:
            mixed.append({
                'quotient': q,
                'members': [
                    {'origin_id': oid, 'formula': f, 'sat': sat}
                    for oid, f, sat in members[:8]
                ],
            })

    assert not preservation_mismatches
    assert not mixed
    assert nontrivial > 0
    assert max_fiber >= 4

    return {
        'gate': 'R47AG_R44BW_CONGRUENCE_QUOTIENT_FIBER_AUTHORITY',
        'candidate': 'R44BW_EXPLICIT_BINARY_EQUALITY_CONGRUENCE_QUOTIENT',
        'target_predicate': 'SAT',
        'base_formulas': 93,
        'origins_checked': len(corpus),
        'unique_quotient_fibers': len(fibers),
        'nontrivial_fibers': nontrivial,
        'max_fiber_size': max_fiber,
        'semantic_preservation_mismatches': 0,
        'mixed_sat_unsat_fibers': 0,
        'finite_falsifier_result': 'NO_COUNTEREXAMPLE_FOUND',
        'universal_basis': 'TWO_DIRECTION_MODEL_PROJECTION_AND_LIFT_PROOF',
        'SAT_semantic_authority': 'THEOREM_AUTHORITY_GRANTED_FOR_EXACT_QUOTIENT',
        'generic_SAT_algorithmic_authority': 'NOT_GRANTED_NO_POLYNOMIAL_DECIDER_ON_ARBITRARY_QUOTIENT',
        'R44BW_scoped_transport_authority': 'UNCHANGED_EXISTING_FAMILY_SCOPE_ONLY',
        'decision_representation_is_not_lifting_provenance': True,
        'exact_explicit_equality_is_not_hidden_equivalence': True,
        'finite_no_collision_is_not_universal_proof': True,
        'UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE': 'OPEN',
        'O4_UNIVERSAL_COVERAGE': 'OPEN',
        'SAT_IN_P': 'NOT_PROVED',
        'P_EQ_NP': 'NOT_PROVED',
        'P_NE_NP': 'NOT_PROVED',
        'P_VS_NP': 'OPEN',
        'TRUMP_finished': False,
        'next_front': 'FIBER_GATE_A_LOSSIER_NONTRIVIAL_TRUMP_QUOTIENT_OR_INVARIANT_WITH_REAL_COLLISION_PRESSURE',
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
