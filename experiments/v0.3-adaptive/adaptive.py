from __future__ import annotations

import math
import random
from collections import Counter, deque
from dataclasses import dataclass
from statistics import mean

from sat_core import SATInstance, SATState, common_diag, touched_variables

@dataclass(frozen=True)
class AdaptiveFlags:
    repeat: bool = True
    oscillation: bool = True
    charge: bool = True
    avalanche: bool = True


def adaptive_v03(inst: SATInstance, initial: list[int], budget: int, rng: random.Random, flags: AdaptiveFlags = AdaptiveFlags()):
    """Adaptive depletion-depth detector, fixed before holdout seed 440223.

    Depth combines normalized stagnation, recurrence/overlap of unsatisfied maps,
    charged-clause pressure, flip oscillation, and recent positive progress.
    Escape strength is selected from depth and only applied after packet testing.
    """
    st = SATState(inst, initial)
    m, n = len(inst.clauses), inst.n
    charge = [1.0] * m
    momentum = [0.0] * n
    tabu = [0] * n
    best = st.satisfied
    stagn = 0
    cooldown = 0
    escapes = attempts = improving = uphill = rejects = 0
    depths: list[float] = []
    signatures: deque[int] = deque(maxlen=max(18, n // 2))
    prev_unsat: set[int] | None = None
    overlap_hist: deque[float] = deque(maxlen=max(10, n // 4))
    flip_hist: deque[int] = deque(maxlen=max(14, n // 3))
    progress_hist: deque[float] = deque(maxlen=12)

    for step in range(1, budget + 1):
        if not st.unsat:
            return True, step - 1, best, common_diag(
                escapes=escapes, escape_attempts=attempts, immediate_improving_escapes=improving,
                accepted_uphill=uphill, max_depth=max(depths, default=0.0), mean_depth=mean(depths) if depths else 0.0,
                thermal_rejects=rejects,
            )
        us = st.unsat.copy()
        for i in range(m):
            if i in us:
                charge[i] = min(48.0, charge[i] * 1.085 + 0.18)
            else:
                charge[i] = max(1.0, charge[i] * 0.978)
        for v in range(n):
            if tabu[v] > 0:
                tabu[v] -= 1
            momentum[v] *= 0.89
        if cooldown > 0:
            cooldown -= 1

        signature = hash(tuple(sorted(us)))
        signatures.append(signature)
        recurrence = max(0.0, (Counter(signatures)[signature] - 1) / max(1, len(signatures) - 1))
        if prev_unsat is not None:
            union = len(us | prev_unsat)
            overlap_hist.append(len(us & prev_unsat) / union if union else 1.0)
        prev_unsat = us
        overlap = mean(overlap_hist) if overlap_hist else 0.0
        repeat_signal = 0.60 * recurrence + 0.40 * overlap

        duplicate_ratio = 0.0
        if flip_hist:
            duplicate_ratio = 1.0 - len(set(flip_hist)) / len(flip_hist)
        top_q = sorted((charge[i] for i in us), reverse=True)[: max(1, min(len(us), n // 12 + 1))]
        q_signal = min(2.0, (mean(top_q) - 1.0) / 14.0) if top_q else 0.0
        s_signal = min(2.5, stagn / max(14.0, 0.58 * n))
        progress_signal = min(1.5, sum(max(0.0, x) for x in progress_hist) / max(1.0, len(progress_hist) * 0.35))
        depth = (
            0.95 * s_signal
            + (0.72 * repeat_signal if flags.repeat else 0.0)
            + (0.46 * q_signal if flags.charge else 0.0)
            + (0.58 * duplicate_ratio if flags.oscillation else 0.0)
            - 0.80 * progress_signal
        )
        depth = max(0.0, depth)
        depths.append(depth)

        ranked = []
        for v in touched_variables(inst, us):
            pressure = sum(charge[i] for i, _ in inst.occurrences[v] if i in us)
            d_weighted = st.delta(v, charge)
            d_plain = st.delta(v)
            score = pressure + 1.72 * d_weighted + 0.38 * momentum[v] - (2.4 if tabu[v] else 0.0) + rng.uniform(-0.12, 0.12)
            ranked.append((score, d_weighted, d_plain, v))
        ranked.sort(reverse=True)
        _, d_weighted, _, v = ranked[0]

        if d_weighted < 0 and depth > 0.90:
            temperature = min(2.8, 0.16 + 0.72 * (depth - 0.90))
            if rng.random() < math.exp(d_weighted / max(0.15, temperature)):
                uphill += 1
            else:
                rejects += 1
                nonnegative = [row for row in ranked[1:] if row[1] >= 0]
                if nonnegative:
                    v = nonnegative[0][3]
                elif len(ranked) > 1:
                    v = ranked[1][3]

        old = st.satisfied
        new = st.flip(v)
        flip_hist.append(v)
        momentum[v] = 0.72 * momentum[v] + new - old
        tabu[v] = max(3, n // 18)
        improvement = max(0, new - best)
        progress_hist.append(float(improvement))
        if new > best:
            best = new
            stagn = 0
            for i in us:
                charge[i] = max(1.0, charge[i] * 0.92)
        else:
            stagn += 1

        threshold = 1.48 + 0.22 * math.sqrt(32.0 / n)
        min_stagn = max(16, int(0.38 * n))
        if flags.avalanche and cooldown == 0 and stagn >= min_stagn and depth >= threshold:
            attempts += 1
            if depth < threshold + 0.30:
                widths, samples = (2,), 7
            elif depth < threshold + 0.75:
                widths, samples = (2, 3, 4), 8
            else:
                widths, samples = tuple(range(3, min(8, max(4, n // 12)) + 1)), 10

            hottest = sorted(us, key=lambda i: charge[i], reverse=True)[: max(4, min(len(us), n // 10 + 2))]
            pool = list({abs(lit) - 1 for i in hottest for lit in inst.clauses[i]})
            base_score = st.satisfied
            base_hot = st.hot_unsat_charge(hottest, charge)
            best_trial = None
            for width in widths:
                if len(pool) < width:
                    continue
                for _ in range(samples):
                    packet = rng.sample(pool, width)
                    for vv in packet:
                        st.flip(vv)
                    q = st.satisfied
                    hot_left = st.hot_unsat_charge(hottest, charge)
                    merit = (q - base_score) + 0.030 * (base_hot - hot_left) - 0.035 * width
                    for vv in reversed(packet):
                        st.flip(vv)
                    if best_trial is None or merit > best_trial[0]:
                        best_trial = (merit, q, hot_left, packet)

            permit_crossing = depth >= threshold + 0.95
            if best_trial is not None and (best_trial[0] > 0.0 or (permit_crossing and best_trial[1] >= base_score - 1)):
                _, q, _, packet = best_trial
                for vv in packet:
                    st.flip(vv)
                    tabu[vv] = max(tabu[vv], max(5, n // 12))
                    flip_hist.append(vv)
                escapes += 1
                improving += int(q > base_score)
                best = max(best, st.satisfied)
                stagn = 0
                cooldown = max(10, n // 5)
                for i in hottest:
                    charge[i] = max(1.0, charge[i] * 0.58)
                progress_hist.clear()
            else:
                cooldown = max(5, n // 12)

    return not st.unsat, budget, best, common_diag(
        escapes=escapes, escape_attempts=attempts, immediate_improving_escapes=improving,
        accepted_uphill=uphill, max_depth=max(depths, default=0.0), mean_depth=mean(depths) if depths else 0.0,
        thermal_rejects=rejects,
    )
