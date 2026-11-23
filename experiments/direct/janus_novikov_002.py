#!/usr/bin/env python3
"""NOVIKOV-002: sound partial-assignment consistency before full-model search.

Conventional unit propagation (SAT), native Exact-One support propagation,
and OPTIONAL bounded failed-literal lookahead. No "future" information,
quantum effect, new NP-complete theorem or C023 replacement.

Only input-derived hints affect branch *order*, never prune. A speculative
lookahead prunes a literal only when assuming it yields an actual constraint
conflict. Both search arms remain reachable unless independently refuted.

Every state carries strict deterministic budgets for nodes and clause visits.
An exhausted budget reports UNKNOWN, never UNSAT. A SAT result is independently
checked. UNSAT for n>12 is explicitly search-only, not a portable proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from time import perf_counter
from typing import Iterable

from janus_ufr_001 import normalize, verify_model

UNSET = -1
MAX_VARIABLES = 240
MAX_ROWS = 4096
MAX_WIDTH = 24


class Exhausted(Exception):
    pass


class ProbeQuota(Exception):
    """Only speculative probing has hit its reserved quota, not the solver."""
    pass


@dataclass
class Meter:
    max_nodes: int
    max_visits: int
    deadline: float
    nodes: int = 0
    clause_visits: int = 0
    propagated: int = 0
    probes: int = 0
    conflict_probes: int = 0
    max_probe_visits: int = 0
    probe_clause_visits: int = 0
    probing: bool = False
    probing_disabled: bool = False

    def charge(self, count: int):
        self.clause_visits += count
        if self.clause_visits > self.max_visits or perf_counter() > self.deadline:
            raise Exhausted()
        if self.probing:
            self.probe_clause_visits += count
            if self.probe_clause_visits > self.max_probe_visits:
                self.probing_disabled = True
                raise ProbeQuota()

    def node(self):
        self.nodes += 1
        if self.nodes > self.max_nodes or perf_counter() > self.deadline:
            raise Exhausted()


@dataclass(frozen=True)
class Result:
    status: str
    model: int | None
    nodes: int
    clause_visits: int
    propagated_assignments: int
    failed_literal_probes: int
    rejected_probe_branches: int
    probe_clause_visits: int
    probe_quota_exhausted: bool
    model_independently_verified: bool
    unsat_independent_exhaustive_check: bool
    elapsed_seconds: float
    source_sha256: str
    certificate_status: str


def validated(rows: Iterable[Iterable[int]], n: int, kind: str):
    if type(n) is not int or not 1 <= n <= MAX_VARIABLES:
        raise ValueError("invalid variable bound")
    if kind not in ("SAT", "EXACT_ONE"):
        raise ValueError("kind must be SAT or EXACT_ONE")
    formula = normalize(rows)
    if len(formula) > MAX_ROWS:
        raise ValueError("too many constraints")
    for row in formula:
        if len(row) > MAX_WIDTH or any(
            type(lit) is not int or lit == 0 or abs(lit) > n for lit in row
        ):
            raise ValueError("invalid clause literal or width")
    return formula


def independently_model(formula, n: int, kind: str, bits: int) -> bool:
    return verify_model(formula, {
        i: bool((bits >> (i-1)) & 1) for i in range(1,n+1)
    }, kind)


def _exact_one_forces(row, values):
    """All exact-one contributions from repeated/complementary literals.

    Use bitset DP for precise reachable totals from other still-unset
    variables. This handles rows (x,x) and (x,-x) without unsound unit logic.
    """
    fixed = 0
    occurrence = {}
    for lit in row:
        v = abs(lit)-1
        if values[v] != UNSET:
            fixed += int(values[v] == int(lit > 0))
        else:
            pos, neg = occurrence.get(v, (0,0))
            occurrence[v] = (pos + int(lit > 0), neg + int(lit < 0))
    unknown = sorted(occurrence)
    reachable = 1 << fixed
    for v in unknown:
        pos, neg = occurrence[v]
        reachable = (reachable << pos) | (reachable << neg)
    if not (reachable & (1 << 1)):
        return None
    forced = []
    for v in unknown:
        # An alternative value is globally supported by this single row
        # iff other variables can supply exactly 1 - local contribution.
        others = 1 << fixed
        for u in unknown:
            if u != v:
                pos, neg = occurrence[u]
                others = (others << pos) | (others << neg)
        pos, neg = occurrence[v]
        permits_zero = neg <= 1 and bool(others & (1 << (1-neg)))
        permits_one = pos <= 1 and bool(others & (1 << (1-pos)))
        if not permits_zero and not permits_one:
            return None
        if permits_zero != permits_one:
            forced.append((v, int(permits_one)))
    return forced


def propagate(formula, values: list[int], kind: str, meter: Meter) -> bool:
    """Fixpoint of deterministic sound local reductions; False=conflict."""
    while True:
        changed = False
        for row in formula:
            meter.charge(1)
            if kind == "EXACT_ONE":
                effects = _exact_one_forces(row, values)
                if effects is None:
                    return False
            else:
                satisfied = False
                options = {}
                for lit in row:
                    v = abs(lit)-1
                    val = values[v]
                    if val != UNSET:
                        if val == int(lit > 0):
                            satisfied = True
                            break
                    else:
                        prior = options.get(v,0)
                        options[v] = prior | (2 if lit > 0 else 1)
                        if options[v] == 3:
                            satisfied = True  # x or not-x is tautological.
                            break
                if satisfied:
                    continue
                if not options:
                    return False
                effects = []
                if len(options) == 1:
                    v, signs = next(iter(options.items()))
                    # No mixed polarity when satisfied=False.
                    effects = [(v, int(signs == 2))]
            for v, val in effects:
                if values[v] == UNSET:
                    values[v] = val
                    meter.propagated += 1
                    changed = True
                elif values[v] != val:
                    return False
        if not changed:
            return True


def input_hint(formula, n: int) -> tuple[int,...]:
    score = [0]*n
    for row in formula:
        weight = max(1, 64//max(1,len(row)))
        for lit in row:
            score[abs(lit)-1] += weight*(1 if lit>0 else -1)
    return tuple(int(s>=0) for s in score)


def _bits(values):
    return sum(int(v==1)<<i for i,v in enumerate(values))


def search(rows: Iterable[Iterable[int]], n: int, kind: str = "SAT", *,
           policy: str = "unit", probe_width: int = 2,
           max_nodes: int = 1500, max_visits: int = 300000,
           seconds: float = 8.0, probe_share: float = 0.05) -> Result:
    """Exact bounded DPLL; optional failed-literal partial consistency.

    *Unit* vs *lookahead* have the SAME hint, variable ordering and clause
    propagation. Lookahead speculatively tests each of the two next literal
    values with this SAME propagation. Only a proven contradiction prunes.
    The extra work is paid and quantified. No full candidate is ever guessed.
    """
    started = perf_counter()
    if policy not in ("unit","lookahead","selective"):
        raise ValueError("invalid partial consistency policy")
    if (type(probe_width) is not int or not 0 <= probe_width <= 8
            or type(max_nodes) is not int or max_nodes<1
            or type(max_visits) is not int or max_visits<1
            or type(seconds) not in (float,int) or isinstance(seconds,bool)
            or not 0.01 <= seconds <= 60
            or type(probe_share) not in (float,int) or isinstance(probe_share,bool)
            or not 0 <= probe_share <= 0.25):
        raise ValueError("invalid bounded experiment budget")
    formula = validated(rows,n,kind)
    src = sha256(json.dumps({"n":n,"kind":kind,"rows":formula},
               sort_keys=True,separators=(",",":")).encode()).hexdigest()
    hint = input_hint(formula,n)
    incidence = [0]*n
    for row in formula:
        for var in {abs(lit)-1 for lit in row}:
            incidence[var] += 1
    meter = Meter(max_nodes,max_visits,perf_counter()+seconds,
                  max_probe_visits=(int(max_visits*probe_share)
                                    if policy=="selective" else 0))

    def choose(values):
        return sorted((i for i,v in enumerate(values) if v==UNSET),
                      key=lambda i:(-incidence[i],i))

    def dfs(source):
        meter.node()
        values = source[:]
        if not propagate(formula,values,kind,meter):
            return None
        if policy in ("lookahead","selective") and probe_width and not meter.probing_disabled:
            # A selective probe may run out of its 5% reserved work budget.
            # Discard that incomplete speculative branch and continue EXACT
            # unit DPLL. It must never turn timeout into a false conflict.
            while True:
                forced = False
                aborted = False
                for v in choose(values)[:probe_width]:
                    outcomes = []
                    for val in (0,1):
                        temporary = values[:]
                        temporary[v] = val
                        meter.probes += 1
                        meter.probing = policy=="selective"
                        try:
                            compatible = propagate(formula,temporary,kind,meter)
                        except ProbeQuota:
                            aborted = True
                            break
                        finally:
                            meter.probing = False
                        outcomes.append(compatible)
                        if not compatible:
                            meter.conflict_probes += 1
                    if aborted:
                        break
                    if not any(outcomes):
                        return None
                    if outcomes[0] != outcomes[1]:
                        values[v] = int(outcomes[1])
                        meter.propagated += 1
                        if not propagate(formula,values,kind,meter):
                            return None
                        forced = True
                        break
                if aborted or not forced:
                    break
        unbound = choose(values)
        if not unbound:
            bits = _bits(values)
            if not independently_model(formula,n,kind,bits):
                raise AssertionError("complete branch is not actual SAT model")
            return bits
        v = unbound[0]
        for val in (hint[v],1-hint[v]):
            assigned = values[:]
            assigned[v] = val
            result = dfs(assigned)
            if result is not None:
                return result
        return None

    answer = "UNKNOWN"
    found = None
    try:
        found = dfs([UNSET]*n)
        answer = "SAT" if found is not None else "UNSAT"
    except Exhausted:
        answer = "UNKNOWN"
    independent_unsat = False
    if answer=="UNSAT" and n<=12:
        independent_unsat = all(
            not independently_model(formula,n,kind,x) for x in range(1<<n))
        if not independent_unsat:
            raise AssertionError("claimed UNSAT contradicted exhaustive check")
    verified = (answer=="SAT" and independently_model(formula,n,kind,found))
    return Result(
        status=answer,model=found,nodes=meter.nodes,clause_visits=meter.clause_visits,
        propagated_assignments=meter.propagated,failed_literal_probes=meter.probes,
        rejected_probe_branches=meter.conflict_probes,
        probe_clause_visits=meter.probe_clause_visits,
        probe_quota_exhausted=meter.probing_disabled,
        model_independently_verified=verified,
        unsat_independent_exhaustive_check=independent_unsat,
        elapsed_seconds=perf_counter()-started,source_sha256=src,
        certificate_status=(
            "INDEPENDENT_SAT_MODEL" if answer=="SAT"
            else "INDEPENDENT_EXHAUSTIVE_UNSAT" if independent_unsat
            else "DPLL_UNSAT_NO_PORTABLE_PROOF" if answer=="UNSAT"
            else "UNKNOWN_RESOURCE_LIMIT"),
    )
