#!/usr/bin/env python3
"""Exact finite replay for the PG15 bounded-fanout NOR 3-SAT source return.

This checker validates the general compiler's Boolean semantics, fanout accounting,
and explicit linear source-size bounds.  The source-level PG15 composition theorem is
proved in the parent artifact; this executable deliberately checks the independent
circuit-normalization layer rather than re-enumerating 15 variables per PG15 copy.
"""

from itertools import product


class Builder:
    def __init__(self):
        self.nodes = []
        self.uses = []
        self.source_copies = 0
        self.switches = 0
        self.pinned = None

    def _new(self, kind, **kw):
        idx = len(self.nodes)
        self.nodes.append({"kind": kind, **kw})
        self.uses.append(0)
        return idx

    def use(self, signal):
        self.uses[signal] += 1
        assert self.uses[signal] <= 2, ("fanout>2", signal, self.uses[signal])

    def free(self, var):
        self.source_copies += 1
        return self._new("FREE", var=var)

    def const0(self):
        # One target PG15 copy plus one fresh helper; one proved pin0 switch.
        self.source_copies += 2
        self.switches += 1
        return self._new("CONST0")

    def nor(self, a, b):
        self.use(a)
        self.use(b)
        self.source_copies += 1
        self.switches += 2
        return self._new("NOR", a=a, b=b)

    def buffer(self, x):
        # One-port identity: NOR(NOR(x,0),0)=x using one zero producer twice.
        z = self.const0()
        u = self.nor(x, z)
        return self.nor(u, z)

    def not_one_port(self, x):
        z = self.const0()
        return self.nor(x, z)

    def or2(self, a, b):
        t = self.nor(a, b)
        return self.nor(t, t)

    def and2_one_port(self, a, b):
        # AND(a,b)=NOR(NOR(a,0),NOR(b,0)); each logical input used once.
        z = self.const0()
        na = self.nor(a, z)
        nb = self.nor(b, z)
        return self.nor(na, nb)

    def pin1(self, x):
        # Parent pin1: tied-input inverter, then pin inverter output to zero.
        self.use(x)
        self.use(x)
        self.source_copies += 2
        self.switches += 3
        self.pinned = x

    def values(self, assignment):
        vals = []
        for i, node in enumerate(self.nodes):
            kind = node["kind"]
            if kind == "FREE":
                vals.append(int(bool(assignment[node["var"]])))
            elif kind == "CONST0":
                vals.append(0)
            elif kind == "NOR":
                assert node["a"] < i and node["b"] < i
                vals.append(int(not (vals[node["a"]] or vals[node["b"]])))
            else:
                raise AssertionError(kind)
        return vals

    def accepts(self, assignment):
        assert self.pinned is not None
        return self.values(assignment)[self.pinned] == 1


def compile_formula(clauses):
    """Compile nonempty clauses of arity 1..3 into the bounded-fanout NOR normal form.

    A literal is (variable_index, negated_bool).
    """
    assert clauses
    assert all(1 <= len(c) <= 3 for c in clauses)

    variables = sorted({v for clause in clauses for v, _ in clause})
    occurrences = {v: [] for v in variables}
    for ci, clause in enumerate(clauses):
        for li, (v, _neg) in enumerate(clause):
            occurrences[v].append((ci, li))

    b = Builder()
    roots = {v: b.free(v) for v in variables}
    signal_for_occurrence = {}
    buffer_count = 0

    # Exact k-use chain: k-2 one-port identity buffers for k>2.
    for v in variables:
        keys = occurrences[v]
        k = len(keys)
        cur = roots[v]
        signals = []
        if k == 1:
            signals = [cur]
        elif k == 2:
            signals = [cur, cur]
        else:
            for _ in range(k - 2):
                signals.append(cur)
                cur = b.buffer(cur)
                buffer_count += 1
            signals.extend([cur, cur])
        assert len(signals) == k
        for key, sig in zip(keys, signals):
            signal_for_occurrence[key] = sig

    negative_count = 0
    clause_outputs = []
    for ci, clause in enumerate(clauses):
        literal_signals = []
        for li, (_v, neg) in enumerate(clause):
            sig = signal_for_occurrence[(ci, li)]
            if neg:
                sig = b.not_one_port(sig)
                negative_count += 1
            literal_signals.append(sig)

        if len(literal_signals) == 1:
            out = literal_signals[0]
        elif len(literal_signals) == 2:
            out = b.or2(literal_signals[0], literal_signals[1])
        else:
            left = b.or2(literal_signals[0], literal_signals[1])
            out = b.or2(left, literal_signals[2])
        clause_outputs.append(out)

    acc = clause_outputs[0]
    for out in clause_outputs[1:]:
        acc = b.and2_one_port(acc, out)

    # Normalize the final signal to two unused output ports, then pin it to one.
    acc = b.buffer(acc)
    b.pin1(acc)

    stats = {
        "n": len(variables),
        "m": len(clauses),
        "L": sum(len(c) for c in clauses),
        "B": buffer_count,
        "Nminus": negative_count,
    }
    return b, stats


def formula_value(clauses, assignment):
    return all(
        any((not assignment[v]) if neg else assignment[v] for v, neg in clause)
        for clause in clauses
    )


def assert_bounds(builder, stats):
    n, m, L = stats["n"], stats["m"], stats["L"]
    B, Nminus = stats["B"], stats["Nminus"]
    assert B <= L
    assert Nminus <= L
    assert max(builder.uses, default=0) <= 2

    exact_copy_bound = n + 4 * B + 3 * Nminus + 9 * m + 1
    coarse_copy_bound = n + 7 * L + 9 * m + 1
    if L <= 3 * m:
        final_copy_bound = n + 30 * m + 1
    else:
        final_copy_bound = coarse_copy_bound
    assert builder.source_copies <= exact_copy_bound
    assert builder.source_copies <= coarse_copy_bound
    assert builder.source_copies <= final_copy_bound

    exact_switch_bound = 5 * B + 3 * Nminus + 15 * m + 1
    coarse_switch_bound = 8 * L + 15 * m + 1
    assert builder.switches <= exact_switch_bound
    assert builder.switches <= coarse_switch_bound
    if L <= 3 * m:
        assert builder.switches <= 39 * m + 1


def exact_three_variable_regression():
    # The 8 possible exact-3 clauses on x0,x1,x2, each variable used once.
    clause_types = [
        [(0, bool(s0)), (1, bool(s1)), (2, bool(s2))]
        for s0, s1, s2 in product((0, 1), repeat=3)
    ]

    formulas = 0
    assignments = 0
    max_copies = 0
    for mask in range(1, 1 << len(clause_types)):
        clauses = [clause_types[i] for i in range(8) if (mask >> i) & 1]
        builder, stats = compile_formula(clauses)
        assert_bounds(builder, stats)
        max_copies = max(max_copies, builder.source_copies)
        for bits in product((0, 1), repeat=3):
            assignment = {i: bool(bits[i]) for i in range(3)}
            assert builder.accepts(assignment) == formula_value(clauses, assignment)
            assignments += 1
        formulas += 1
    return formulas, assignments, max_copies


def short_clause_regression():
    # Exhaust every ordered single clause of arity 1,2,3 over two signed variables.
    literals = [(0, False), (0, True), (1, False), (1, True)]
    cases = 0
    assignments = 0
    for arity in (1, 2, 3):
        for clause in product(literals, repeat=arity):
            clauses = [list(clause)]
            builder, stats = compile_formula(clauses)
            assert_bounds(builder, stats)
            for bits in product((0, 1), repeat=2):
                assignment = {0: bool(bits[0]), 1: bool(bits[1])}
                assert builder.accepts(assignment) == formula_value(clauses, assignment)
                assignments += 1
            cases += 1
    return cases, assignments


def high_fanout_regression():
    clauses = [[(0, False), (1, False), (2, True)] for _ in range(100)]
    builder, stats = compile_formula(clauses)
    assert_bounds(builder, stats)
    assert stats == {"n": 3, "m": 100, "L": 300, "B": 294, "Nminus": 100}
    assert max(builder.uses) == 2
    assert builder.source_copies == 2380
    assert builder.switches == 3271
    for bits in product((0, 1), repeat=3):
        assignment = {i: bool(bits[i]) for i in range(3)}
        assert builder.accepts(assignment) == formula_value(clauses, assignment)
    return builder.source_copies, builder.switches


f, a, max_copies = exact_three_variable_regression()
s, sa = short_clause_regression()
hc, hs = high_fanout_regression()

assert f == 255
assert a == 255 * 8
assert s == 84
assert sa == 84 * 4

print("PASS_PG15_BOUNDED_FANOUT_NOR_3SAT_SOURCE_RETURN")
print(f"exact3_formulas={f} exact3_assignments={a} max_source_copies={max_copies}")
print(f"short_clause_cases={s} short_clause_assignments={sa}")
print(f"high_fanout_clauses=100 source_copies={hc} switches={hs} max_fanout=2")
print("construction_bound: G<=n+7L+9m+1<=n+30m+1 for L<=3m")
print("switch_bound: W<=8L+15m+1<=39m+1 for L<=3m")
print("LOCAL_AF3_COMPRESSION_AS_UNIVERSAL_SOLVER=CLOSED_BY_BOOLEAN_HARDNESS_RETURN")
print("GLOBAL_POLYNOMIAL_CONTRACTION=OPEN")
print("E8_D1=EMPTY P_VS_NP=OPEN")
