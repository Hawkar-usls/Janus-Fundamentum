#!/usr/bin/env python3
"""Faithful PhysarumNetwork (Tero-Nakagaki) extraction from user's PHYSARUM ENGINE.

Original user-provided source: physarum_engine(20261112-211012).py
SHA-256: e0e7a7d6f62acbae18a68141c4708f9d0006679d5e58bb95f36bc74c398dcf13
This port RETAINS original pressure network, Poiseuille flows, dD/dt
and original np.linalg.solve and uses exactly the same update equations.
The user's separate Jeff Jones PhysarumSwarm is intentionally NOT ported;
this is precisely the Tero-Nakagaki *network* variant, not full Physarum.
"""
from __future__ import annotations
import numpy as np

class PhysarumNetwork:
    """Original user's adaptive conductivity network, copied as mathematical core."""
    def __init__(self,nodes,decay=0.1,growth_factor=1.0):
        self.nodes=nodes
        self.n=len(nodes)
        self.decay=decay
        self.growth_factor=growth_factor
        self.D=np.zeros((self.n,self.n))
        self.L=np.zeros((self.n,self.n))
        for i in range(self.n):
            for j in range(i+1,self.n):
                dist=np.linalg.norm(np.array(nodes[i])-np.array(nodes[j]))
                self.L[i,j]=self.L[j,i]=max(dist,1e-6)
        self.D=0.01*np.ones((self.n,self.n))
        np.fill_diagonal(self.D,0)
    def set_source_sink(self,source_idx,sink_idx,inflow=1.0):
        self.source=source_idx
        self.sink=sink_idx
        self.inflow=inflow
    def compute_flow(self):
        A=np.zeros((self.n,self.n))
        for i in range(self.n):
            for j in range(self.n):
                if i!=j:
                    A[i,i]+=self.D[i,j]/self.L[i,j]
                    A[i,j]-=self.D[i,j]/self.L[i,j]
        b=np.zeros(self.n)
        b[self.source]=self.inflow
        b[self.sink]=-self.inflow
        A_reduced=np.delete(np.delete(A,self.sink,axis=0),self.sink,axis=1)
        b_reduced=np.delete(b,self.sink)
        try:
            p_reduced=np.linalg.solve(A_reduced,b_reduced)
        except np.linalg.LinAlgError:
            return np.zeros((self.n,self.n))
        p=np.zeros(self.n)
        p[:self.sink]=p_reduced[:self.sink]
        p[self.sink+1:]=p_reduced[self.sink:]
        Q=np.zeros((self.n,self.n))
        for i in range(self.n):
            for j in range(i+1,self.n):
                q=self.D[i,j]*(p[i]-p[j])/self.L[i,j]
                Q[i,j]=q
                Q[j,i]=-q
        return Q
    def update_conductivity(self,Q,dt=0.01):
        for i in range(self.n):
            for j in range(i+1,self.n):
                flow_abs=abs(Q[i,j])
                delta=self.growth_factor*flow_abs-self.decay*self.D[i,j]
                self.D[i,j]+=delta*dt
                self.D[j,i]=self.D[i,j]
                if self.D[i,j]<1e-6:
                    self.D[i,j]=1e-6
                    self.D[j,i]=1e-6
    def step(self,source_idx,sink_idx,dt=0.01):
        self.set_source_sink(source_idx,sink_idx)
        Q=self.compute_flow()
        self.update_conductivity(Q,dt)
        return Q

def pivot_class(f):
    """Map SOURCE-ONLY pivot geometry to one of 16 network food sinks."""
    pairs=f["pair_work"]
    band=0 if pairs<=2 else 1 if pairs<=6 else 2 if pairs<=16 else 3
    has_width4=int(any(len(c)==4 for _,c in f["pos"]+f["neg"]))
    balanced=int(abs(len(f["pos"])-len(f["neg"]))<=1)
    return band*4+has_width4*2+balanced

class SATPhysarum:
    """Adaptor only: the original Tero network receives verified reward sites."""
    def __init__(self):
        # one central source, 16 source-feature food locations, constant geometry
        nodes=[(0.0,0.0)]+[
            (float(i%4+1),float(i//4+1)) for i in range(16)]
        self.network=PhysarumNetwork(nodes)
        self.verified_hit_count=0
        self.verified_miss_count=0
    def source_score(self,f):
        node=pivot_class(f)+1
        # Conductivity through the original user's tube, normalized by cost;
        # this score never asserts an entailed SAT equation.
        return float(self.network.D[0,node]/self.network.L[0,node]) / (
            1.0+f["pair_work"])**0.5
    def observe_source_verified(self,f,positive):
        if positive:
            self.network.step(0,pivot_class(f)+1,dt=0.01)
            self.verified_hit_count+=1
        else:
            # Flow-free original Physarum decay, not reinforcement of failed path.
            self.network.update_conductivity(np.zeros_like(self.network.D),dt=0.01)
            self.verified_miss_count+=1
        if not np.isfinite(self.network.D).all():
            raise AssertionError("PHYSARUM_NONFINITE_CONDUCTIVITY")
    def state(self):
        return {"conductivity_q1000000":
                np.rint(self.network.D*1000000).astype(np.int64).tolist(),
                "positive_exact_source_proofs":self.verified_hit_count,
                "negative_exact_source_proofs":self.verified_miss_count,
                "original_user_equation":"dD/dt = |Q| - decay*D; Q = D*(p_i-p_j)/L",
                "source_file_sha256":"e0e7a7d6f62acbae18a68141c4708f9d0006679d5e58bb95f36bc74c398dcf13",
                "no_Jones_particle_swarm":True}
