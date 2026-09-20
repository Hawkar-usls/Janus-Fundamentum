#!/usr/bin/env python3
import itertools, json, pathlib, argparse

def ek(a,b): return tuple(sorted((a,b)))
def eset(E): return {ek(a,b) for a,b in E}
def adjacent(E,a,b): return ek(a,b) in E

def components(V,E,removed=()):
    V=set(V)-set(removed); out=[]
    while V:
        s=next(iter(V)); C=set(); st=[s]
        while st:
            v=st.pop()
            if v in C: continue
            C.add(v)
            for a,b in E:
                if a==v and b in V-C: st.append(b)
                elif b==v and a in V-C: st.append(a)
        V-=C; out.append(C)
    return out

def matching_number(mask,ports):
    ids=[i for i in range(len(ports)) if (mask>>i)&1]
    for k in range(4,-1,-1):
        for comb in itertools.combinations(ids,k):
            L=set();R=set();ok=True
            for i in comb:
                u,v=ports[i]
                if u in L or v in R: ok=False; break
                L.add(u);R.add(v)
            if ok: return k,list(comb)
    raise AssertionError

def global_kappa(V,E):
    for k in range(len(V)-1):
        for S in itertools.combinations(V,k):
            if len(components(V,E,S))>1:
                return k,list(S)
    return len(V)-1,[]

def local_cut(V,E,s,t):
    candidates=[v for v in V if v not in {s,t}]
    for k in range(len(candidates)+1):
        for S in itertools.combinations(candidates,k):
            comps=components(V,E,S)
            ci=next(i for i,C in enumerate(comps) if s in C)
            if t not in comps[ci]:
                return k,list(S)
    raise AssertionError

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--freeze",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    fr=json.load(open(a.freeze)); F=fr["frame"]
    V=F["expected_route34_component_vertices"]
    base=eset(F["base_non_port_edges"])
    ports=[tuple(x) for x in F["port_edge_order"]]
    prov=F["frozen_provenance_coloring"]
    compatible=[i for i,(u,v) in enumerate(ports) if prov[u]!=prov[v]]
    assert compatible==[2,3,6,7,8,9,12,13]
    dist={}; gap={}; failures=[]; rows=[]; canonical_common_cuts=None
    nu4_count=0
    for sub in range(1<<len(compatible)):
        mask=0
        for j,i in enumerate(compatible):
            if (sub>>j)&1: mask|=1<<i
        E=set(base)
        for i in range(16):
            if (mask>>i)&1: E.add(ek(*ports[i]))
        nu,match=matching_number(mask,ports)
        kap,kcut=global_kappa(V,E)
        lam,lcut=local_cut(V,E,"c0","f0")
        ok=(kap==1+nu and lam==1+nu and kap==lam)
        if not ok: failures.append({"mask":mask,"nu":nu,"kappa":kap,"lambda":lam})
        dist[str(nu)]=dist.get(str(nu),0)+1
        gap[str(lam-kap)]=gap.get(str(lam-kap),0)+1
        rows.append({"mask":mask,"nu":nu,"kappa":kap,"lambda":lam,"minimum_global_cut":kcut,"minimum_local_cut":lcut})
        if nu==4: nu4_count+=1
    expected={"0":1,"1":16,"2":78,"3":112,"4":49}
    assert dist==expected and nu4_count==49 and failures==[]
    result={
      "schema":"janus.trump.c11_frozen_frame_local_to_global_connectivity_replay.v1",
      "admissible_descendants":256,
      "compatible_port_edge_indices":compatible,
      "nu_distribution":dist,
      "global_kappa_distribution":{"1":1,"2":16,"3":78,"4":112,"5":49},
      "local_lambda_distribution":{"1":1,"2":16,"3":78,"4":112,"5":49},
      "lambda_minus_kappa_distribution":gap,
      "formula_failures":failures,
      "theorem_replay_pass":True,
      "rows":rows
    }
    pathlib.Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},sort_keys=True))

if __name__=="__main__": main()
