from __future__ import annotations

import random
from collections import Counter, deque
from statistics import mean

from sat_core import SATInstance, SATState, common_diag, touched_variables
from config_anchor import V20Config, _restore_state


class GladiusSelectiveLane:
    """v2.0 active lane with retained charge and verified packet escape."""

    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random, cfg: V20Config):
        self.inst, self.rng, self.cfg = inst, rng, cfg
        self.st = SATState(inst, initial)
        self.n, self.m = inst.n, len(inst.clauses)
        self.charge = [1.0] * self.m
        self.momentum = [0.0] * self.n
        self.tabu = [0] * self.n
        self.age = [0] * self.n
        self.best = self.st.satisfied
        self.best_assignment = self.st.a.copy()
        self.stagn = self.cooldown = 0
        self.hunger = 0.0
        self.failed_survives = self.uphill_episode = 0
        self.ticks = self.committed_flips = self.probe_flips = 0
        self.memory_restore_flips = self.memory_injections = 0
        self.chaos_attempts = self.chaos_accepts = self.rejected_packets = 0
        self.accepted_uphill = self.neutral_crossings = 0
        self.mode_steps = Counter()
        self.depths, self.hungers = [], []
        self.signatures = deque(maxlen=max(18, self.n // 2))
        self.prev_unsat = None
        self.overlaps = deque(maxlen=max(10, self.n // 4))
        self.progress = deque(maxlen=12)

    @property
    def solved(self) -> bool:
        return not self.st.unsat

    def _update_field(self):
        us = self.st.unsat.copy()
        for ci in range(self.m):
            self.charge[ci] = min(self.cfg.charge_cap, self.charge[ci] * self.cfg.charge_growth + self.cfg.charge_add) if ci in us else max(1.0, self.charge[ci] * self.cfg.charge_decay)
        for v in range(self.n):
            self.age[v] += 1
            self.momentum[v] *= 0.90
            if self.tabu[v] > 0:
                self.tabu[v] -= 1
        if self.cooldown > 0:
            self.cooldown -= 1

        sig = tuple(sorted(us))
        self.signatures.append(sig)
        recurrence = max(0.0, (Counter(self.signatures)[sig] - 1) / max(1, len(self.signatures) - 1))
        if self.prev_unsat is not None:
            union = len(us | self.prev_unsat)
            self.overlaps.append(len(us & self.prev_unsat) / union if union else 1.0)
        self.prev_unsat = us
        overlap = mean(self.overlaps) if self.overlaps else 0.0
        hot_q = sorted((self.charge[i] for i in us), reverse=True)[:max(1, min(len(us), self.n // 12 + 1))]
        q_signal = min(2.2, (mean(hot_q) - 1.0) / 14.0) if hot_q else 0.0
        stagn_signal = min(2.8, self.stagn / max(14.0, 0.56 * self.n))
        positive_progress = sum(max(0, x) for x in self.progress) / max(1, len(self.progress))
        # The v0.3 oscillation term is deliberately absent.
        depth = max(0.0, 0.98 * stagn_signal + 0.62 * recurrence + 0.38 * overlap + 0.50 * q_signal - 0.78 * positive_progress)
        self.hunger = max(0.0, 0.82 * self.hunger + 0.36 * stagn_signal + 0.22 * recurrence + 0.16 * q_signal - 0.52 * positive_progress)
        self.depths.append(depth)
        self.hungers.append(self.hunger)
        return us, depth, recurrence

    def _commit(self, v: int, mode: str) -> None:
        before = self.st.satisfied
        after = self.st.flip(v)
        self.committed_flips += 1
        self.mode_steps[mode] += 1
        self.age[v] = 0
        self.momentum[v] = 0.72 * self.momentum[v] + after - before
        self.tabu[v] = max(self.tabu[v], max(2, self.n // 22))
        if after < before:
            self.accepted_uphill += 1
        self.progress.append(max(0, after - self.best))
        if after > self.best:
            self.best = after
            self.best_assignment = self.st.a.copy()
            self.stagn = 0
            self.hunger *= 0.25
            self.failed_survives = self.uphill_episode = 0
            for ci, _ in self.inst.occurrences[v]:
                if ci not in self.st.unsat:
                    self.charge[ci] = max(1.0, self.charge[ci] * 0.94)
        else:
            self.stagn += 1

    def _restore(self, target: list[int], source: str) -> None:
        used = _restore_state(self.st, target)
        self.committed_flips += used
        self.memory_restore_flips += used
        self.memory_injections += int(source == "ANCHOR" and used > 0)
        self.mode_steps["SURVIVE"] += used
        if self.st.satisfied > self.best:
            self.best, self.best_assignment = self.st.satisfied, self.st.a.copy()
        self.failed_survives += 1
        self.uphill_episode = 0
        if used > 0:
            self.stagn = 0
            self.hunger *= 0.30
            self.cooldown = max(self.cooldown, max(6, self.n // 14))
        else:
            # A no-op restore is evidence, not a successful rescue.
            self.hunger = max(self.hunger, 1.0)
            self.cooldown = max(self.cooldown, 2)

    def _tested_chaos(self, us: set[int], depth: float) -> bool:
        if self.cooldown > 0 or not us:
            return False
        threshold = 1.62 + 0.20 * (32.0 / self.n) ** 0.5
        min_stagn = max(20, int(self.cfg.chaos_stagn_factor * self.n))
        if depth < threshold or self.stagn < min_stagn or self.failed_survives < 1:
            return False
        self.chaos_attempts += 1
        hottest = sorted(us, key=lambda i: self.charge[i], reverse=True)[:max(4, min(len(us), self.n // 10 + 2))]
        pool = list({abs(lit) - 1 for ci in hottest for lit in self.inst.clauses[ci]})
        if len(pool) < 2:
            self.rejected_packets += 1
            self.cooldown = max(6, self.n // 12)
            return False

        ranked = sorted((self.st.delta(v) + 0.38 * self.st.delta(v, self.charge) + 0.08 * min(2.0, self.age[v] / max(4.0, self.n / 8.0)), v) for v in pool, reverse=True)
        packets = []
        for width in range(2, min(self.cfg.max_packet_width, len(ranked)) + 1):
            packets.append([v for _, v in ranked[:width]])
            for _ in range(self.cfg.packet_samples):
                packets.append(self.rng.sample(pool, width))

        base_score = self.st.satisfied
        base_hot = self.st.hot_unsat_charge(hottest, self.charge)
        best_trial = None
        for packet in packets:
            for v in packet:
                self.st.flip(v); self.probe_flips += 1
            score = self.st.satisfied
            hot_left = self.st.hot_unsat_charge(hottest, self.charge)
            plain_gain, hot_gain = score - base_score, base_hot - hot_left
            merit = plain_gain + 0.032 * hot_gain - 0.045 * len(packet)
            for v in reversed(packet):
                self.st.flip(v); self.probe_flips += 1
            if best_trial is None or merit > best_trial[0]:
                best_trial = (merit, plain_gain, hot_gain, packet)

        if best_trial is None:
            self.rejected_packets += 1
            self.cooldown = max(6, self.n // 12)
            return False
        merit, plain_gain, hot_gain, packet = best_trial
        useful = plain_gain > 0 or (plain_gain == 0 and hot_gain >= max(2.0, 0.04 * base_hot) and merit > 0.10)
        if not useful:
            self.rejected_packets += 1
            self.cooldown = max(7, self.n // 10)
            return False

        before = self.st.satisfied
        for v in packet:
            self._commit(v, "CHAOS")
        self.chaos_accepts += 1
        self.neutral_crossings += int(self.st.satisfied == before)
        self.stagn = self.failed_survives = 0
        self.hunger *= 0.30
        self.cooldown = max(12, self.n // 5)
        for ci in hottest:
            self.charge[ci] = max(1.0, self.charge[ci] * (0.90 if ci in self.st.unsat else 0.82))
        return True

    def tick(self, anchor_best: int, anchor_assignment: list[int]) -> None:
        if self.solved:
            return
        self.ticks += 1
        us, depth, recurrence = self._update_field()
        survive_threshold = max(18, int(self.cfg.survive_stagn_factor * self.n))
        drift = self.best - self.st.satisfied

        if self._tested_chaos(us, depth):
            return
        if self.cooldown == 0 and self.stagn >= survive_threshold and (drift >= self.cfg.memory_gap or recurrence >= 0.28):
            self._restore(anchor_assignment, "ANCHOR") if anchor_best >= self.best + 1 else self._restore(self.best_assignment, "SELF")
            return

        mode = "EXPLOIT" if self.hunger < 0.70 and depth < 0.75 else "HUNT"
        ranked = []
        for v in touched_variables(self.inst, us):
            pressure = sum(self.charge[i] for i, _ in self.inst.occurrences[v] if i in us)
            dp, dw = self.st.delta(v), self.st.delta(v, self.charge)
            novelty = min(1.5, self.age[v] / max(4.0, self.n / 8.0))
            score = pressure + 1.72 * dw + 0.38 * self.momentum[v] + 0.12 * novelty
            if self.tabu[v] and dw <= 0:
                score -= 2.1
            ranked.append((score + self.rng.uniform(-0.10, 0.10), dp, dw, v))
        ranked.sort(reverse=True)
        chosen = ranked[0]
        if chosen[2] < 0:
            nonworse = [row for row in ranked if row[2] >= 0]
            bounded = self.cfg.allow_single_uphill and depth >= 1.55 and self.uphill_episode < 1 and chosen[1] >= -1
            accepted = False
            if nonworse:
                chosen = nonworse[0]
            elif bounded:
                import math
                temperature = min(1.8, 0.16 + 0.55 * (depth - 1.55))
                accepted = self.rng.random() < math.exp(chosen[2] / max(0.15, temperature))
                self.uphill_episode += int(accepted)
            if not nonworse and not accepted:
                # Critical fix: HOLD instead of falling through to another negative move.
                self.mode_steps["HOLD"] += 1
                self.stagn += 1
                self.progress.append(0)
                return
        self._commit(chosen[3], mode)

    def diag(self) -> dict:
        return common_diag(
            escapes=self.chaos_accepts, escape_attempts=self.chaos_attempts,
            immediate_improving_escapes=0, accepted_uphill=self.accepted_uphill,
            max_depth=max(self.depths, default=0.0), mean_depth=mean(self.depths) if self.depths else 0.0,
            thermal_rejects=0, memory_injections=self.memory_injections,
            memory_restore_flips=self.memory_restore_flips, chaos_attempts=self.chaos_attempts,
            chaos_accepts=self.chaos_accepts, rejected_packets=self.rejected_packets,
            neutral_crossings=self.neutral_crossings, mode_exploit_steps=self.mode_steps["EXPLOIT"],
            mode_hunt_steps=self.mode_steps["HUNT"], mode_survive_steps=self.mode_steps["SURVIVE"],
            mode_chaos_steps=self.mode_steps["CHAOS"], mode_hold_steps=self.mode_steps["HOLD"],
            max_hunger=max(self.hungers, default=0.0), mean_hunger=mean(self.hungers) if self.hungers else 0.0,
        )
