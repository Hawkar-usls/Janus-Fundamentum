#!/usr/bin/env python3
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
        if l1 * l2 < 0 and frozenset((-l1, -l2)) in binary:
            uf.union(abs(l1), abs(l2))
    return {v: uf.find(v) for v in vs}


def dense_rename(formula):
    vs = variables(formula)
    ren = {v: i + 1 for i, v in enumerate(vs)}
    return canonical_formula(
        tuple(ren[abs(l)] if l > 0 else -ren[abs(l)] for l in c)
        for c in formula
    )


def exact_congruence_quotient(formula):
    formula = canonical_formula(formula)
    cls = explicit_equality_classes(formula)
    substituted = []
    for c in formula:
        substituted.append(tuple(cls[abs(l)] if l > 0 else -cls[abs(l)] for l in c))
    return dense_rename(canonical_formula(substituted)), cls


def exact3_clause_pool(n):
    pool = []
    for support in combinations(range(1, n + 1), 3):
        for signs in product((-1, 1), repeat=3):
            pool.append(tuple(v * s for v, s in zip(support, signs)))
    return tuple(pool)


def exact3_corpus_n3_all():
    pool = exact3_clause_pool(3)
    out = []
    for mask in range(1 << len(pool)):
        out.append(canonical_formula(pool[i] for i in range(len(pool)) if mask & (1 << i)))
    return out


def exact3_corpus_n4_k_le3():
    pool = exact3_clause_pool(4)
    out = [canonical_formula(())]
    for k in range(1, 4):
        for cs in combinations(pool, k):
            out.append(canonical_formula(cs))
    return out


def is_exact3(formula):
    return all(len(c) == 3 and len({abs(l) for l in c}) == 3 for c in formula)


def is_singleton_classes(classes):
    return all(v == rep for v, rep in classes.items())


def structural_audit(corpus):
    failures = []
    for i, f in enumerate(corpus):
        f = canonical_formula(f)
        q, classes = exact_congruence_quotient(f)
        dense = dense_rename(f)
        if not is_exact3(f):
            failures.append({'index': i, 'kind': 'NOT_EXACT3', 'formula': f})
            continue
        if not is_singleton_classes(classes):
            failures.append({'index': i, 'kind': 'NON_SINGLETON_CLASS', 'formula': f, 'classes': classes})
        if q != dense:
            failures.append({'index': i, 'kind': 'QUOTIENT_NOT_DENSE_RENAME', 'formula': f, 'q': q, 'dense': dense})
        if sum(map(len, q)) != sum(map(len, dense)) or len(q) != len(dense):
            failures.append({'index': i, 'kind': 'SIZE_CHANGED_BEYOND_RENAME', 'formula': f, 'q': q})
    return failures


def audit():
    n3 = exact3_corpus_n3_all()
    n4 = exact3_corpus_n4_k_le3()
    corpus = n3 + n4
    failures = structural_audit(corpus)
    assert not failures

    # Exact SAT here is deliberately finite/exponential calibration only.
    n3_sat = sum(1 for f in n3 if exact_sat(f))
    n3_unsat = len(n3) - n3_sat
    assert n3_sat > 0 and n3_unsat > 0

    # Outside-slice positive control: certified equality really can compress.
    outside = canonical_formula([
        (-1, 2), (1, -2),
        (1, 3, 4), (-2, 3, 4),
    ])
    q_out, cls_out = exact_congruence_quotient(outside)
    assert not is_singleton_classes(cls_out)
    assert len(variables(q_out)) < len(variables(outside))

    return {
        'gate': 'R47AH_SINGLETON_SLICE_COMPRESS_OR_DECIDE',
        'parent_commit': 'd76bf034732c953ef35d0a9db16bd05e1d183d95',
        'candidate': 'R44BW_EXPLICIT_BINARY_EQUALITY_CONGRUENCE_QUOTIENT',
        'structural_theorem_target': 'EXACT_3CNF_IS_A_HARD_SUBSLICE_OF_THE_R44BW_SINGLETON_SLICE',
        'finite_structural_audit': {
            'n3_all_clause_subsets': len(n3),
            'n4_up_to_3_clauses': len(n4),
            'total_formulas_checked': len(corpus),
            'non_singleton_failures': 0,
            'quotient_not_dense_rename_failures': 0,
            'size_change_beyond_rename_failures': 0,
            'result': 'PASS'
        },
        'finite_semantic_calibration_n3': {
            'sat': n3_sat,
            'unsat': n3_unsat,
            'method': 'EXACT_ASSIGNMENT_ENUMERATION',
            'authority': 'CALIBRATION_ONLY_EXPONENTIAL_NOT_A_POLYNOMIAL_DECIDER'
        },
        'outside_slice_positive_control': {
            'certified_equality_classes_nontrivial': True,
            'variable_count_before': len(variables(outside)),
            'variable_count_after': len(variables(q_out)),
            'result': 'R44BW_CAN_COMPRESS_WHEN_EXPLICIT_EQUALITY_CERTIFICATES_EXIST'
        },
        'reduction_consequence': {
            'statement': 'IF_D_Q_DECIDES_EVERY_R44BW_QUOTIENT_IMAGE_IN_POLYNOMIAL_TIME_THEN_EXACT_3SAT_IS_DECIDABLE_IN_POLYNOMIAL_TIME',
            'reason': 'For exact-3-CNF F, Q_BW(F)=dense_rename(F), and dense renaming is polynomial and SAT preserving.',
            'status': 'CONDITIONAL_THEOREM_NOT_A_DECIDER'
        },
        'compression_lane': 'OPEN_NONTRIVIAL_SAT_SUFFICIENT_POLYNOMIAL_REPRESENTATION_NOT_SUPPLIED',
        'direct_decider_lane': 'OPEN_NO_TOTAL_POLYNOMIAL_DECIDER_ON_ARBITRARY_Q_SUPPLIED',
        'SAT_IN_P': 'NOT_PROVED',
        'P_EQ_NP': 'NOT_PROVED',
        'P_NE_NP': 'NOT_PROVED',
        'P_VS_NP': 'OPEN',
        'TRUMP_finished': False,
        'next_front': 'ATTACK_SINGLETON_SLICE_WITH_LOSSY_FIBER_GATED_COMPRESSION_OR_A_DIRECT_TOTAL_POLYNOMIAL_Q_DECIDER'
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
