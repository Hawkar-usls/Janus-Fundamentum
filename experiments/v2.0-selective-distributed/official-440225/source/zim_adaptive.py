from __future__ import annotations

import random
from collections import Counter, deque
from statistics import mean

from sat_core import SATInstance, SATState, touched_variables

class ZimAdaptiveLane:
    """Stepwise preservation of the v0.3 adaptive solver for scout control.

    This lane intentionally keeps the historical oscillation term. It is not the
    v2.0 active field; it is a quarantined reference/scout so the new Gladius
    cannot erase a previously successful strategy. Probe work is counted.
    """

    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random):
        self.inst=inst; self.rng=rng; self.st=SATState(inst,initial)
        self.m=len(inst.clauses); self.n=inst.n
        self.charge=[1.0]*self.m; self.momentum=[0.0]*self.n; self.tabu=[0]*self.n
        self.best=self.st.satisfied; self.best_assignment=self.st.a.copy(); self.stagn=0; self.cooldown=0
        self.escapes=self.attempts=self.improving=self.uphill=self.rejects=0
        self.depths=[]; self.signatures=deque(maxlen=max(18,self.n//2)); self.prev_unsat=None
        self.overlap_hist=deque(maxlen=max(10,self.n//4)); self.flip_hist=deque(maxlen=max(14,self.n//3)); self.progress_hist=deque(maxlen=12)
        self.ticks=0; self.committed_flips=0; self.probe_flips=0

    @property
    def solved(self): return not self.st.unsat

    def tick(self):
        if self.solved: return
        self.ticks += 1
        us=self.st.unsat.copy()
        for i in range(self.m):
            if i in us: self.charge[i]=min(48.0,self.charge[i]*1.085+0.18)
            else: self.charge[i]=max(1.0,self.charge[i]*0.978)
        for v in range(self.n):
            if self.tabu[v]>0: self.tabu[v]-=1
            self.momentum[v]*=0.89
        if self.cooldown>0: self.cooldown-=1
        signature=hash(tuple(sorted(us))); self.signatures.append(signature)
        recurrence=max(0.0,(Counter(self.signatures)[signature]-1)/max(1,len(self.signatures)-1))
        if self.prev_unsat is not None:
            union=len(us|self.prev_unsat); self.overlap_hist.append(len(us&self.prev_unsat)/union if union else 1.0)
        self.prev_unsat=us; overlap=mean(self.overlap_hist) if self.overlap_hist else 0.0
        repeat_signal=.60*recurrence+.40*overlap
        duplicate_ratio=0.0 if not self.flip_hist else 1.0-len(set(self.flip_hist))/len(self.flip_hist)
        top_q=sorted((self.charge[i] for i in us),reverse=True)[:max(1,min(len(us),self.n//12+1))]
        q_signal=min(2.0,(mean(top_q)-1.0)/14.0) if top_q else 0.0
        s_signal=min(2.5,self.stagn/max(14.0,.58*self.n))
        progress_signal=min(1.5,sum(max(0.0,x) for x in self.progress_hist)/max(1.0,len(self.progress_hist)*.35))
        depth=max(0.0,.95*s_signal+.72*repeat_signal+.46*q_signal+.58*duplicate_ratio-.80*progress_signal)
        self.depths.append(depth)
        ranked=[]
        for v in touched_variables(self.inst,us):
            pressure=sum(self.charge[i] for i,_ in self.inst.occurrences[v] if i in us)
            dw=self.st.delta(v,self.charge); dp=self.st.delta(v)
            score=pressure+1.72*dw+.38*self.momentum[v]-(2.4 if self.tabu[v] else 0.0)+self.rng.uniform(-.12,.12)
            ranked.append((score,dw,dp,v))
        ranked.sort(reverse=True); _,dw,_,v=ranked[0]
        if dw<0 and depth>.90:
            import math
            temp=min(2.8,.16+.72*(depth-.90))
            if self.rng.random()<math.exp(dw/max(.15,temp)): self.uphill+=1
            else:
                self.rejects+=1; nonneg=[row for row in ranked[1:] if row[1]>=0]
                if nonneg: v=nonneg[0][3]
                elif len(ranked)>1: v=ranked[1][3]
        old=self.st.satisfied; new=self.st.flip(v); self.committed_flips+=1; self.flip_hist.append(v)
        self.momentum[v]=.72*self.momentum[v]+new-old; self.tabu[v]=max(3,self.n//18)
        improvement=max(0,new-self.best); self.progress_hist.append(float(improvement))
        if new>self.best:
            self.best=new; self.best_assignment=self.st.a.copy(); self.stagn=0
            for i in us: self.charge[i]=max(1.0,self.charge[i]*.92)
        else: self.stagn+=1
        threshold=1.48+.22*(32.0/self.n)**.5; min_stagn=max(16,int(.38*self.n))
        if self.cooldown==0 and self.stagn>=min_stagn and depth>=threshold and self.st.unsat:
            self.attempts+=1
            if depth<threshold+.30: widths,samples=(2,),7
            elif depth<threshold+.75: widths,samples=(2,3,4),8
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
                    merit=(q-base_score)+.030*(base_hot-hot_left)-.035*width
                    for vv in reversed(packet): self.st.flip(vv); self.probe_flips+=1
                    if best_trial is None or merit>best_trial[0]: best_trial=(merit,q,hot_left,packet)
            permit=depth>=threshold+.95
            if best_trial is not None and (best_trial[0]>0.0 or (permit and best_trial[1]>=base_score-1)):
                _,q,_,packet=best_trial
                for vv in packet:
                    self.st.flip(vv); self.committed_flips+=1; self.tabu[vv]=max(self.tabu[vv],max(5,self.n//12)); self.flip_hist.append(vv)
                self.escapes+=1; self.improving+=int(q>base_score); self.best=max(self.best,self.st.satisfied); self.stagn=0; self.cooldown=max(10,self.n//5)
                for i in hottest: self.charge[i]=max(1.0,self.charge[i]*.58)
                self.progress_hist.clear()
            else: self.cooldown=max(5,self.n//12)
