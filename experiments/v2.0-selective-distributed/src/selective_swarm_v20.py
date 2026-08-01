from __future__ import annotations

import math
import random
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from statistics import mean

from sat_core import SATInstance, SATState, common_diag, touched_variables


@dataclass(frozen=True)
class SwarmV20Config:
    oscillation_weight: float = 0.16
    charge_growth: float = 1.082
    charge_add: float = 0.18
    charge_decay: float = 0.980
    charge_cap: float = 52.0
    avalanche_merit_min: float = 0.10
    single_lane_cutoff: int = 48
    anchor_activation_factor: float = 0.62
    anchor_activation_min: int = 28
    survive_stagn_factor: float = 0.62
    memory_gap: int = 1
    share_cooldown_factor: float = 0.20
    max_memory_injections: int = 4
    proof_scan: bool = True


def complete_sign_core_witness(inst: SATInstance):
    """Sound narrow UNSAT witness: all 2^k signs on the same variables."""
    groups: dict[tuple[int, ...], set[int]] = defaultdict(set)
    for clause in inst.clauses:
        vars_ = tuple(sorted(abs(lit) - 1 for lit in clause))
        if not vars_ or len(vars_) > 12:
            continue
        positive = {abs(lit) - 1: lit > 0 for lit in clause}
        mask = 0
        for j, v in enumerate(vars_):
            if positive[v]:
                mask |= 1 << j
        groups[vars_].add(mask)
    for vars_, masks in groups.items():
        if len(masks) == (1 << len(vars_)):
            return {"variables": list(vars_), "patterns": len(masks)}
    return None


class AgentBase:
    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random):
        self.inst = inst
        self.st = SATState(inst, initial)
        self.rng = rng
        self.n = inst.n
        self.m = len(inst.clauses)
        self.best = self.st.satisfied
        self.best_assignment = self.st.a.copy()
        self.stagn = 0
        self.flips = 0
        self.memory_injections = 0
        self.memory_flip_cost = 0
        self.last_improvement_round = 0

    def solved(self) -> bool:
        return not self.st.unsat

    def inject_memory(self, assignment: list[int], charge: list[float] | None = None) -> int:
        cost = 0
        for v, target in enumerate(assignment):
            if self.st.a[v] != target:
                self.st.flip(v)
                cost += 1
        self.flips += cost
        self.memory_flip_cost += cost
        self.memory_injections += int(cost > 0)
        self.stagn = 0
        if self.st.satisfied > self.best:
            self.best = self.st.satisfied
            self.best_assignment = self.st.a.copy()
        return cost


class AnchorStable(AgentBase):
    """Stateful form of the stable Junction Base lane."""
    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random):
        super().__init__(inst, initial, rng)
        self.charge = [1.0] * self.m
        self.momentum = [0.0] * self.n
        self.escapes = 0
        self.escape_attempts = 0

    def import_charge(self, source: list[float]) -> None:
        if len(source) == self.m:
            self.charge = [max(1.0, min(28.0, q)) for q in source]

    def step(self, round_id: int) -> None:
        if self.solved():
            return
        us = self.st.unsat.copy()
        for i in range(self.m):
            self.charge[i] = min(28.0, self.charge[i] * 1.105 + 0.15) if i in us else max(1.0, self.charge[i] * 0.986)
        for v in range(self.n):
            self.momentum[v] *= 0.90
        touched = touched_variables(self.inst, us)
        if not touched:
            return
        v = max(
            (
                sum(self.charge[i] for i, _ in self.inst.occurrences[vv] if i in us)
                + 1.78 * self.st.delta(vv, self.charge)
                + 0.34 * self.momentum[vv]
                + self.rng.uniform(-0.18, 0.18),
                vv,
            )
            for vv in touched
        )[1]
        old = self.st.satisfied
        new = self.st.flip(v)
        self.flips += 1
        self.momentum[v] = 0.75 * self.momentum[v] + new - old
        if new > self.best:
            self.best = new
            self.best_assignment = self.st.a.copy()
            self.stagn = 0
            self.last_improvement_round = round_id
        else:
            self.stagn += 1

        if self.stagn > max(24, int(0.62 * self.n)) and self.st.unsat:
            self.escape_attempts += 1
            hottest = sorted(self.st.unsat, key=lambda i: self.charge[i], reverse=True)[: max(2, self.n // 18)]
            pool = list({abs(lit) - 1 for ci in hottest for lit in self.inst.clauses[ci]})
            if pool:
                width = min(len(pool), max(1, self.n // 28))
                for vv in self.rng.sample(pool, width):
                    self.st.flip(vv)
                    self.flips += 1
                self.escapes += 1
                if self.st.satisfied > self.best:
                    self.best = self.st.satisfied
                    self.best_assignment = self.st.a.copy()
                    self.last_improvement_round = round_id
            self.stagn = 0


class GladiusSelective(AgentBase):
    """v0.4 Selective Field lane: weak oscillation, persistent charge, tested avalanche."""
    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random, cfg: SwarmV20Config):
        super().__init__(inst, initial, rng)
        self.cfg = cfg
        self.charge = [1.0] * self.m
        self.momentum = [0.0] * self.n
        self.tabu = [0] * self.n
        self.age = [0] * self.n
        self.signatures: deque[int] = deque(maxlen=max(18, self.n // 2))
        self.prev_unsat: set[int] | None = None
        self.overlap_hist: deque[float] = deque(maxlen=max(10, self.n // 4))
        self.flip_hist: deque[int] = deque(maxlen=max(14, self.n // 3))
        self.progress_hist: deque[float] = deque(maxlen=12)
        self.cooldown = 0
        self.uphill_episode = 0
        self.depth = 0.0
        self.max_depth = 0.0
        self.depth_sum = 0.0
        self.depth_samples = 0
        self.hunger = 0.0
        self.max_hunger = 0.0
        self.accepted_uphill = 0
        self.thermal_rejects = 0
        self.escape_attempts = 0
        self.escapes = 0
        self.improving_escapes = 0
        self.rejected_packets = 0
        self.probe_flips = 0

    def import_charge(self, source: list[float]) -> None:
        if len(source) == self.m:
            self.charge = [max(1.0, min(self.cfg.charge_cap, q)) for q in source]

    def _field(self) -> set[int]:
        us = self.st.unsat.copy()
        for i in range(self.m):
            if i in us:
                self.charge[i] = min(self.cfg.charge_cap, self.charge[i] * self.cfg.charge_growth + self.cfg.charge_add)
            else:
                self.charge[i] = max(1.0, self.charge[i] * self.cfg.charge_decay)
        for v in range(self.n):
            self.momentum[v] *= 0.89
            self.age[v] += 1
            if self.tabu[v] > 0:
                self.tabu[v] -= 1
        if self.cooldown > 0:
            self.cooldown -= 1

        sig = hash(tuple(sorted(us)))
        self.signatures.append(sig)
        recurrence = max(0.0, (Counter(self.signatures)[sig] - 1) / max(1, len(self.signatures) - 1))
        if self.prev_unsat is not None:
            union = len(us | self.prev_unsat)
            self.overlap_hist.append(len(us & self.prev_unsat) / union if union else 1.0)
        self.prev_unsat = us
        overlap = mean(self.overlap_hist) if self.overlap_hist else 0.0
        duplicate = 1.0 - len(set(self.flip_hist)) / len(self.flip_hist) if self.flip_hist else 0.0
        top_q = sorted((self.charge[i] for i in us), reverse=True)[: max(1, min(len(us), self.n // 12 + 1))]
        q_signal = min(2.0, (mean(top_q) - 1.0) / 14.0) if top_q else 0.0
        s_signal = min(2.5, self.stagn / max(14.0, 0.58 * self.n))
        progress = min(1.5, sum(max(0.0, x) for x in self.progress_hist) / max(1.0, len(self.progress_hist) * 0.35))
        self.depth = max(
            0.0,
            0.96 * s_signal
            + 0.70 * (0.60 * recurrence + 0.40 * overlap)
            + 0.48 * q_signal
            + self.cfg.oscillation_weight * duplicate
            - 0.82 * progress,
        )
        self.max_depth = max(self.max_depth, self.depth)
        self.depth_sum += self.depth
        self.depth_samples += 1
        self.hunger = max(0.0, 0.84 * self.hunger + 0.30 * s_signal + 0.18 * recurrence + 0.16 * q_signal - 0.52 * progress)
        self.max_hunger = max(self.max_hunger, self.hunger)
        return us

    def step(self, round_id: int) -> None:
        if self.solved():
            return
        us = self._field()
        ranked = []
        for v in touched_variables(self.inst, us):
            pressure = sum(self.charge[i] for i, _ in self.inst.occurrences[v] if i in us)
            dw = self.st.delta(v, self.charge)
            dp = self.st.delta(v)
            novelty = min(1.5, self.age[v] / max(4.0, self.n / 8.0))
            score = pressure + 1.70 * dw + 1.30 * dp + 0.34 * self.momentum[v] + 0.14 * novelty
            if self.tabu[v] and dp <= 0:
                score -= 2.0
            score += self.rng.uniform(-0.10, 0.10)
            ranked.append((score, dw, dp, v))
        ranked.sort(reverse=True)
        if not ranked:
            return
        chosen = ranked[0]
        if chosen[1] < 0:
            nonworse = [row for row in ranked if row[1] >= 0 or row[2] >= 0]
            threshold = 1.18 + 0.18 * math.sqrt(32.0 / self.n)
            allow = self.depth >= threshold and self.uphill_episode < 1 and chosen[2] >= -1
            if allow:
                self.uphill_episode += 1
                self.accepted_uphill += 1
            elif nonworse:
                chosen = nonworse[0]
                self.thermal_rejects += 1
            elif len(ranked) > 1:
                chosen = ranked[1]
                self.thermal_rejects += 1
        v = chosen[3]
        old = self.st.satisfied
        new = self.st.flip(v)
        self.flips += 1
        self.flip_hist.append(v)
        self.age[v] = 0
        self.tabu[v] = max(3, self.n // 18)
        self.momentum[v] = 0.72 * self.momentum[v] + new - old
        improvement = max(0, new - self.best)
        self.progress_hist.append(float(improvement))
        if new > self.best:
            self.best = new
            self.best_assignment = self.st.a.copy()
            self.stagn = 0
            self.hunger *= 0.25
            self.uphill_episode = 0
            self.last_improvement_round = round_id
            for ci, _ in self.inst.occurrences[v]:
                if ci not in self.st.unsat:
                    self.charge[ci] = max(1.0, self.charge[ci] * 0.88)
        else:
            self.stagn += 1

    def tested_avalanche(self, round_id: int) -> int:
        if self.solved() or self.cooldown > 0:
            return 0
        threshold = 1.50 + 0.20 * math.sqrt(32.0 / self.n)
        min_stagn = max(18, int(0.46 * self.n))
        if self.depth < threshold or self.stagn < min_stagn:
            return 0
        self.escape_attempts += 1
        us = self.st.unsat.copy()
        hottest = sorted(us, key=lambda i: self.charge[i], reverse=True)[: max(4, min(len(us), self.n // 10 + 2))]
        pool = list({abs(lit) - 1 for ci in hottest for lit in self.inst.clauses[ci]})
        if len(pool) < 2:
            self.rejected_packets += 1
            self.cooldown = max(6, self.n // 10)
            return 0
        ranked = sorted(
            (
                self.st.delta(v) + 0.38 * self.st.delta(v, self.charge) + 0.08 * min(2.0, self.age[v] / max(4.0, self.n / 8.0)),
                v,
            )
            for v in pool
        )
        ranked.reverse()
        max_width = min(5 if self.depth < threshold + 0.70 else 7, len(ranked))
        packets: list[list[int]] = []
        for width in range(2, max_width + 1):
            packets.append([v for _, v in ranked[:width]])
            for _ in range(3):
                packets.append(self.rng.sample(pool, width))
        base = self.st.satisfied
        base_hot = self.st.hot_unsat_charge(hottest, self.charge)
        best_trial = None
        for packet in packets:
            for v in packet:
                self.st.flip(v)
                self.probe_flips += 1
            score = self.st.satisfied
            hot_left = self.st.hot_unsat_charge(hottest, self.charge)
            gain = score - base
            merit = gain + 0.030 * (base_hot - hot_left) - 0.050 * len(packet)
            for v in reversed(packet):
                self.st.flip(v)
                self.probe_flips += 1
            if best_trial is None or merit > best_trial[0]:
                best_trial = (merit, gain, packet)
        if best_trial is None or best_trial[0] <= self.cfg.avalanche_merit_min or best_trial[1] < 0:
            self.rejected_packets += 1
            self.cooldown = max(8, self.n // 9)
            return 0
        _, _, packet = best_trial
        before = self.st.satisfied
        for v in packet:
            self.st.flip(v)
            self.flips += 1
            self.flip_hist.append(v)
            self.tabu[v] = max(self.tabu[v], max(5, self.n // 12))
        self.escapes += 1
        self.improving_escapes += int(self.st.satisfied > before)
        if self.st.satisfied > self.best:
            self.best = self.st.satisfied
            self.best_assignment = self.st.a.copy()
            self.last_improvement_round = round_id
        self.stagn = 0
        self.hunger *= 0.35
        self.uphill_episode = 0
        self.cooldown = max(10, self.n // 6)
        for ci in hottest:
            self.charge[ci] = max(1.0, self.charge[ci] * 0.86)
        return len(packet)


class LegacyAdaptiveV03(AgentBase):
    """Stateful exact control lane for v0.3; never modified by Holocron."""
    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random):
        super().__init__(inst, initial, rng)
        self.charge = [1.0] * self.m
        self.momentum = [0.0] * self.n
        self.tabu = [0] * self.n
        self.cooldown = 0
        self.signatures: deque[int] = deque(maxlen=max(18, self.n // 2))
        self.prev_unsat: set[int] | None = None
        self.overlap_hist: deque[float] = deque(maxlen=max(10, self.n // 4))
        self.flip_hist: deque[int] = deque(maxlen=max(14, self.n // 3))
        self.progress_hist: deque[float] = deque(maxlen=12)
        self.escapes = self.escape_attempts = self.improving_escapes = 0
        self.accepted_uphill = self.thermal_rejects = 0
        self.max_depth = self.depth_sum = 0.0
        self.depth_samples = 0
        self.probe_flips = 0

    def step(self, round_id: int) -> None:
        if self.solved():
            return
        us = self.st.unsat.copy()
        for i in range(self.m):
            if i in us:
                self.charge[i] = min(48.0, self.charge[i] * 1.085 + 0.18)
            else:
                self.charge[i] = max(1.0, self.charge[i] * 0.978)
        for v in range(self.n):
            if self.tabu[v] > 0:
                self.tabu[v] -= 1
            self.momentum[v] *= 0.89
        if self.cooldown > 0:
            self.cooldown -= 1

        signature = hash(tuple(sorted(us)))
        self.signatures.append(signature)
        recurrence = max(0.0, (Counter(self.signatures)[signature] - 1) / max(1, len(self.signatures) - 1))
        if self.prev_unsat is not None:
            union = len(us | self.prev_unsat)
            self.overlap_hist.append(len(us & self.prev_unsat) / union if union else 1.0)
        self.prev_unsat = us
        overlap = mean(self.overlap_hist) if self.overlap_hist else 0.0
        repeat_signal = 0.60 * recurrence + 0.40 * overlap
        duplicate_ratio = 1.0 - len(set(self.flip_hist)) / len(self.flip_hist) if self.flip_hist else 0.0
        top_q = sorted((self.charge[i] for i in us), reverse=True)[: max(1, min(len(us), self.n // 12 + 1))]
        q_signal = min(2.0, (mean(top_q) - 1.0) / 14.0) if top_q else 0.0
        s_signal = min(2.5, self.stagn / max(14.0, 0.58 * self.n))
        progress_signal = min(1.5, sum(max(0.0, x) for x in self.progress_hist) / max(1.0, len(self.progress_hist) * 0.35))
        depth = max(0.0, 0.95*s_signal + 0.72*repeat_signal + 0.46*q_signal + 0.58*duplicate_ratio - 0.80*progress_signal)
        self.max_depth = max(self.max_depth, depth)
        self.depth_sum += depth
        self.depth_samples += 1

        ranked=[]
        for v in touched_variables(self.inst, us):
            pressure=sum(self.charge[i] for i,_ in self.inst.occurrences[v] if i in us)
            dw=self.st.delta(v,self.charge); dp=self.st.delta(v)
            score=pressure+1.72*dw+0.38*self.momentum[v]-(2.4 if self.tabu[v] else 0.0)+self.rng.uniform(-0.12,0.12)
            ranked.append((score,dw,dp,v))
        ranked.sort(reverse=True)
        _,dw,_,v=ranked[0]
        if dw<0 and depth>0.90:
            temperature=min(2.8,0.16+0.72*(depth-0.90))
            if self.rng.random()<math.exp(dw/max(0.15,temperature)):
                self.accepted_uphill+=1
            else:
                self.thermal_rejects+=1
                nonnegative=[row for row in ranked[1:] if row[1]>=0]
                if nonnegative: v=nonnegative[0][3]
                elif len(ranked)>1: v=ranked[1][3]
        old=self.st.satisfied; new=self.st.flip(v); self.flips+=1
        self.flip_hist.append(v); self.momentum[v]=0.72*self.momentum[v]+new-old; self.tabu[v]=max(3,self.n//18)
        improvement=max(0,new-self.best); self.progress_hist.append(float(improvement))
        if new>self.best:
            self.best=new; self.best_assignment=self.st.a.copy(); self.stagn=0; self.last_improvement_round=round_id
            for i in us: self.charge[i]=max(1.0,self.charge[i]*0.92)
        else:
            self.stagn+=1

        threshold=1.48+0.22*math.sqrt(32.0/self.n); min_stagn=max(16,int(0.38*self.n))
        if self.cooldown==0 and self.stagn>=min_stagn and depth>=threshold:
            self.escape_attempts+=1
            if depth<threshold+0.30: widths,samples=(2,),7
            elif depth<threshold+0.75: widths,samples=(2,3,4),8
            else: widths,samples=tuple(range(3,min(8,max(4,self.n//12))+1)),10
            hottest=sorted(us,key=lambda i:self.charge[i],reverse=True)[:max(4,min(len(us),self.n//10+2))]
            pool=list({abs(lit)-1 for i in hottest for lit in self.inst.clauses[i]})
            base_score=self.st.satisfied; base_hot=self.st.hot_unsat_charge(hottest,self.charge); best_trial=None
            for width in widths:
                if len(pool)<width: continue
                for _ in range(samples):
                    packet=self.rng.sample(pool,width)
                    for vv in packet: self.st.flip(vv); self.probe_flips+=1
                    q=self.st.satisfied; hot_left=self.st.hot_unsat_charge(hottest,self.charge)
                    merit=(q-base_score)+0.030*(base_hot-hot_left)-0.035*width
                    for vv in reversed(packet): self.st.flip(vv); self.probe_flips+=1
                    if best_trial is None or merit>best_trial[0]: best_trial=(merit,q,packet)
            permit_crossing=depth>=threshold+0.95
            if best_trial is not None and (best_trial[0]>0.0 or (permit_crossing and best_trial[1]>=base_score-1)):
                _,q,packet=best_trial
                for vv in packet:
                    self.st.flip(vv); self.flips+=1; self.tabu[vv]=max(self.tabu[vv],max(5,self.n//12)); self.flip_hist.append(vv)
                self.escapes+=1; self.improving_escapes+=int(q>base_score); self.best=max(self.best,self.st.satisfied)
                if self.st.satisfied>=self.best: self.best_assignment=self.st.a.copy()
                self.stagn=0; self.cooldown=max(10,self.n//5)
                for i in hottest: self.charge[i]=max(1.0,self.charge[i]*0.58)
                self.progress_hist.clear()
            else:
                self.cooldown=max(5,self.n//12)


class WalkSatScout(AgentBase):
    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random, p_random: float = 0.58):
        super().__init__(inst, initial, rng)
        self.p_random = p_random

    def step(self, round_id: int) -> None:
        if self.solved():
            return
        ci = self.rng.choice(tuple(self.st.unsat))
        variables = [abs(lit) - 1 for lit in self.inst.clauses[ci]]
        if self.rng.random() < self.p_random:
            v = self.rng.choice(variables)
        else:
            v = max((self.st.delta(v), self.rng.random(), v) for v in variables)[2]
        new = self.st.flip(v)
        self.flips += 1
        if new > self.best:
            self.best = new
            self.best_assignment = self.st.a.copy()
            self.stagn = 0
            self.last_improvement_round = round_id
        else:
            self.stagn += 1


def _diag(agent: AgentBase) -> dict:
    if isinstance(agent, (GladiusSelective, LegacyAdaptiveV03)):
        return common_diag(
            escapes=agent.escapes,
            escape_attempts=agent.escape_attempts,
            immediate_improving_escapes=agent.improving_escapes,
            accepted_uphill=agent.accepted_uphill,
            max_depth=agent.max_depth,
            mean_depth=agent.depth_sum / agent.depth_samples if agent.depth_samples else 0.0,
            thermal_rejects=agent.thermal_rejects,
            probe_flips=agent.probe_flips,
            rejected_packets=getattr(agent, "rejected_packets", 0),
            max_hunger=getattr(agent, "max_hunger", 0.0),
        )
    if isinstance(agent, AnchorStable):
        return common_diag(escapes=agent.escapes, escape_attempts=agent.escape_attempts, probe_flips=0)
    return common_diag(probe_flips=0)


def selective_swarm_v20(
    inst: SATInstance, initial: list[int], budget: int, rng: random.Random,
    cfg: SwarmV20Config = SwarmV20Config(),
):
    """JANUS distributed v2.0: legacy control + selective field + stable Anchor."""
    witness=complete_sign_core_witness(inst) if cfg.proof_scan else None
    if witness is not None:
        return False,0,len(inst.clauses)-1,common_diag(
            no_recombination_state="PROVEN_NO_RECOMBINATION",no_recombination_witness=witness,
            latency_rounds=0,total_committed_flips=0,total_probe_flips=0,total_work=0,
            active_nodes_peak=0,anchor_activated=False,scout_activated=False,
            memory_injections=0,memory_flip_cost=0,packet_messages=0)

    legacy_rng=random.Random(); legacy_rng.setstate(rng.getstate())
    coord_rng=random.Random(rng.getrandbits(64))
    legacy=LegacyAdaptiveV03(inst,initial,legacy_rng)
    gladius=GladiusSelective(inst,initial,random.Random(coord_rng.getrandbits(64)),cfg)
    anchor=AnchorStable(inst,initial,random.Random(coord_rng.getrandbits(64)))
    scout=None
    k=len(inst.clauses[0]) if inst.clauses else 0
    anchor_first=k>=5
    anchor_active=anchor_first
    scout_active=False
    packet_messages=0; injections=0; max_active=1
    elite_score=max(legacy.best,gladius.best,anchor.best); elite_assignment=initial.copy(); elite_charge=gladius.charge.copy()
    activate_round=max(cfg.anchor_activation_min,int(cfg.anchor_activation_factor*inst.n))
    survive_stagn=max(20,int(cfg.survive_stagn_factor*inst.n))
    chaos_round=max(2*activate_round,int(1.45*inst.n))

    for round_id in range(1,budget+1):
        if anchor_first:
            anchor.step(round_id)
            agents=[anchor]
        else:
            legacy.step(round_id)
            gladius.step(round_id); gladius.tested_avalanche(round_id)
            if anchor_active: anchor.step(round_id)
            if scout_active and scout is not None: scout.step(round_id)
            agents=[legacy,gladius]+([anchor] if anchor_active else [])+([scout] if scout_active and scout is not None else [])
        max_active=max(max_active,len(agents))
        best_agent=max(agents,key=lambda a:a.best)
        if best_agent.best>elite_score:
            elite_score=best_agent.best; elite_assignment=best_agent.best_assignment.copy()
            if hasattr(best_agent,'charge'): elite_charge=best_agent.charge.copy()
        solved=[a for a in agents if a.solved()]
        if solved:
            winner=min(solved,key=lambda a:a.flips)
            all_agents=[legacy,gladius,anchor]+([scout] if scout is not None else [])
            total_probe=legacy.probe_flips+gladius.probe_flips
            total_committed=sum(a.flips for a in all_agents if a is not None)
            d=_diag(winner); d.update(
                no_recombination_state="RECOMBINATION_FOUND",no_recombination_witness=None,latency_rounds=round_id,
                winner_role=("ANCHOR" if winner is anchor else "GLADIUS_SELECTIVE" if winner is gladius else "LEGACY_V03" if winner is legacy else "SCOUT"),
                total_committed_flips=total_committed,total_probe_flips=total_probe,total_work=total_committed+total_probe,
                active_nodes_peak=max_active,anchor_activated=anchor_active,scout_activated=scout_active,
                memory_injections=injections,memory_flip_cost=anchor.memory_flip_cost,packet_messages=packet_messages,
                legacy_best=legacy.best,gladius_best=gladius.best,anchor_best=anchor.best,scout_best=scout.best if scout else None)
            return True,round_id,max(a.best for a in agents),d
        if anchor_first: continue

        if not anchor_active and inst.n>cfg.single_lane_cutoff and round_id>=activate_round:
            if min(legacy.stagn,gladius.stagn)>=max(14,inst.n//4) or max(getattr(gladius,'depth',0),0)>=1.15:
                anchor_active=True; packet_messages+=1; injections+=1
                anchor.inject_memory(elite_assignment); anchor.import_charge(elite_charge)

        if not scout_active and anchor_active and round_id>=chaos_round:
            if legacy.stagn>=survive_stagn and gladius.stagn>=survive_stagn and anchor.stagn>=survive_stagn:
                mutated=elite_assignment.copy()
                hot=sorted(range(len(elite_charge)),key=lambda i:elite_charge[i],reverse=True)[:max(3,min(8,inst.n//16))]
                pool=list({abs(lit)-1 for ci in hot for lit in inst.clauses[ci]})
                if pool:
                    width=min(len(pool),max(1,inst.n//96+1))
                    for v in coord_rng.sample(pool,width): mutated[v]^=1
                scout=WalkSatScout(inst,mutated,random.Random(coord_rng.getrandbits(64)),p_random=.60)
                scout_active=True; packet_messages+=1

    all_agents=[legacy,gladius,anchor]+([scout] if scout else [])
    best_agent=max(all_agents,key=lambda a:a.best); total_probe=legacy.probe_flips+gladius.probe_flips
    total_committed=sum(a.flips for a in all_agents if a is not None); d=_diag(best_agent)
    d.update(no_recombination_state="SEARCH_EXHAUSTED_NO_PROOF",no_recombination_witness=None,latency_rounds=budget,winner_role=None,
        total_committed_flips=total_committed,total_probe_flips=total_probe,total_work=total_committed+total_probe,
        active_nodes_peak=max_active,anchor_activated=anchor_active,scout_activated=scout_active,memory_injections=injections,
        memory_flip_cost=anchor.memory_flip_cost,packet_messages=packet_messages,legacy_best=legacy.best,gladius_best=gladius.best,
        anchor_best=anchor.best,scout_best=scout.best if scout else None)
    return False,budget,max(a.best for a in all_agents),d
