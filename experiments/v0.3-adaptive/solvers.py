from __future__ import annotations

import math
import random
from statistics import mean

from sat_core import SATInstance, SATState, common_diag, touched_variables

def walksat(inst: SATInstance, initial: list[int], budget: int, rng: random.Random, p_random: float = 0.55):
    st = SATState(inst, initial)
    best = st.satisfied
    for step in range(1, budget + 1):
        if not st.unsat:
            return True, step - 1, best, common_diag()
        ci = rng.choice(tuple(st.unsat))
        variables = [abs(lit) - 1 for lit in inst.clauses[ci]]
        if rng.random() < p_random:
            v = rng.choice(variables)
        else:
            v = max((st.delta(v), rng.random(), v) for v in variables)[2]
        best = max(best, st.flip(v))
    return not st.unsat, budget, best, common_diag()


def junction_base(inst: SATInstance, initial: list[int], budget: int, rng: random.Random):
    st = SATState(inst, initial)
    m, n = len(inst.clauses), inst.n
    charge = [1.0] * m
    momentum = [0.0] * n
    best = st.satisfied
    stagn = 0
    escapes = 0
    for step in range(1, budget + 1):
        if not st.unsat:
            return True, step - 1, best, common_diag(escapes=escapes, escape_attempts=escapes)
        us = st.unsat.copy()
        for i in range(m):
            charge[i] = min(24.0, charge[i] * 1.12 + 0.15) if i in us else max(1.0, charge[i] * 0.985)
        for j in range(n):
            momentum[j] *= 0.90
        touched = touched_variables(inst, us)
        v = max(
            (
                sum(charge[i] for i, _ in inst.occurrences[vv] if i in us)
                + 1.8 * st.delta(vv, charge)
                + 0.35 * momentum[vv]
                + rng.uniform(-0.2, 0.2),
                vv,
            )
            for vv in touched
        )[1]
        old = st.satisfied
        new = st.flip(v)
        momentum[v] = 0.75 * momentum[v] + new - old
        if new > best:
            best = new
            stagn = 0
        else:
            stagn += 1
        if stagn > max(20, n // 2):
            hottest = sorted(st.unsat, key=lambda i: charge[i], reverse=True)[: max(2, n // 16)]
            pool = list({abs(lit) - 1 for i in hottest for lit in inst.clauses[i]})
            if pool:
                for vv in rng.sample(pool, min(len(pool), max(1, n // 20))):
                    st.flip(vv)
                best = max(best, st.satisfied)
                escapes += 1
            stagn = 0
    return not st.unsat, budget, best, common_diag(escapes=escapes, escape_attempts=escapes)


def junction_tunnel_v02(inst: SATInstance, initial: list[int], budget: int, rng: random.Random):
    st = SATState(inst, initial)
    m, n = len(inst.clauses), inst.n
    charge = [1.0] * m
    momentum = [0.0] * n
    tabu = [0] * n
    best = st.satisfied
    stagn = 0
    barrier = 0.0
    escapes = uphill = attempts = improving = rejects = 0
    last_signature = None
    repeats = 0
    depths: list[float] = []
    for step in range(1, budget + 1):
        if not st.unsat:
            return True, step - 1, best, common_diag(
                escapes=escapes, escape_attempts=attempts, immediate_improving_escapes=improving,
                accepted_uphill=uphill, max_depth=max(depths, default=0.0), mean_depth=mean(depths) if depths else 0.0,
                thermal_rejects=rejects,
            )
        us = st.unsat.copy()
        for i in range(m):
            charge[i] = min(40.0, charge[i] * 1.10 + 0.20) if i in us else max(1.0, charge[i] * 0.975)
        for v in range(n):
            if tabu[v] > 0:
                tabu[v] -= 1
            momentum[v] *= 0.88
        signature = tuple(sorted(us))
        repeats = repeats + 1 if signature == last_signature else 0
        last_signature = signature
        barrier += 0.12 + 0.035 * len(us) + 0.08 * repeats
        temperature = min(3.5, 0.12 + barrier / (8.0 + n / 8.0))
        depths.append(barrier / max(1.0, n * 0.32))

        ranked = []
        for v in touched_variables(inst, us):
            pressure = sum(charge[i] for i, _ in inst.occurrences[v] if i in us)
            d = st.delta(v, charge)
            score = pressure + 1.75 * d + 0.40 * momentum[v] - (2.2 if tabu[v] else 0.0) + rng.uniform(-0.15, 0.15)
            ranked.append((score, d, v))
        ranked.sort(reverse=True)
        _, d, v = ranked[0]
        if d < 0 and rng.random() >= math.exp(d / max(0.15, temperature)):
            rejects += 1
            if len(ranked) > 1:
                v = ranked[1][2]
        elif d < 0:
            uphill += 1
        old = st.satisfied
        new = st.flip(v)
        momentum[v] = 0.7 * momentum[v] + new - old
        tabu[v] = max(3, n // 16)
        if new > best:
            best = new
            stagn = 0
            barrier *= 0.35
            repeats = 0
        else:
            stagn += 1

        if stagn >= max(12, n // 3) or barrier > max(8.0, n * 0.32):
            attempts += 1
            hottest = sorted(st.unsat, key=lambda i: charge[i], reverse=True)[: max(3, n // 12)]
            pool = list({abs(lit) - 1 for i in hottest for lit in inst.clauses[i]})
            base = st.satisfied
            best_trial = None
            for width in range(2, min(7, max(3, len(pool))) + 1):
                for _ in range(5):
                    if len(pool) < width:
                        continue
                    packet = rng.sample(pool, width)
                    for vv in packet:
                        st.flip(vv)
                    q = st.satisfied
                    hot_left = st.hot_unsat_charge(hottest, charge)
                    merit = q - 0.015 * hot_left + rng.uniform(-0.02, 0.02)
                    for vv in reversed(packet):
                        st.flip(vv)
                    if best_trial is None or merit > best_trial[0]:
                        best_trial = (merit, q, packet)
            if best_trial:
                _, q, packet = best_trial
                for vv in packet:
                    st.flip(vv)
                    tabu[vv] = max(tabu[vv], max(4, n // 12))
                escapes += 1
                improving += int(q > base)
                best = max(best, st.satisfied)
            barrier *= 0.18
            stagn = repeats = 0
            for i in hottest:
                charge[i] = max(1.0, charge[i] * 0.55)
    return not st.unsat, budget, best, common_diag(
        escapes=escapes, escape_attempts=attempts, immediate_improving_escapes=improving,
        accepted_uphill=uphill, max_depth=max(depths, default=0.0), mean_depth=mean(depths) if depths else 0.0,
        thermal_rejects=rejects,
    )
