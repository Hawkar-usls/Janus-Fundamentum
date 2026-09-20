#!/usr/bin/env python3
import argparse,itertools,json,pathlib
from collections import Counter

def ek(a,b): return tuple(sorted((a,b)))
def eset(E): return {ek(a,b) for a,b in E}
def selected(mask,n=16): return [i for i in range(n) if (mask>>i)&1]

def precompute_seven_sets(V,baseE,ports):
    out=[]
    for S in itertools.combinations(V,7):
        pos={v:i for i,v in enumerate(S)}
        fixed=[]
        for a,b in baseE:
            if a in pos and b in pos:
                fixed.append((pos[a],pos[b]))
        local=[]
        localmask=0
        for i,(a,b) in enumerate(ports):
            if a in pos and b in pos:
                local.append((i,pos[a],pos[b])); localmask|=1<<i
        out.append((S,fixed,local,localmask))
    return out

def first_p7_direct(mask,seven_info):
    for S,fixed,local,localmask in seven_info:
        if len(fixed)+(mask & localmask).bit_count()!=6:
            continue
        deg=[0]*7; adj=[0]*7
        for i,j in fixed:
            deg[i]+=1;deg[j]+=1;adj[i]|=1<<j;adj[j]|=1<<i
        for edge_i,i,j in local:
            if (mask>>edge_i)&1:
                deg[i]+=1;deg[j]+=1;adj[i]|=1<<j;adj[j]|=1<<i
        if sorted(deg)!=[1,1,2,2,2,2,2]:
            continue
        seen=1; frontier=1
        while frontier:
            nbr=0
            f=frontier
            while f:
                lb=f & -f; i=lb.bit_length()-1; f-=lb
                nbr |= adj[i]
            frontier=nbr & ~seen; seen |= frontier
        if seen==0b1111111:
            return list(S)
    return None

def matching_metric(mask,ports,PA,PD):
    ids=selected(mask,len(ports))
    deg={v:0 for v in PA+PD}
    for i in ids:
        u,v=ports[i];deg[u]+=1;deg[v]+=1
    delta=max(deg.values()) if deg else 0
    best=[]
    for k in range(min(4,len(ids)),-1,-1):
        hit=None
        for comb in itertools.combinations(ids,k):
            L=set();R=set();ok=True
            for i in comb:
                u,v=ports[i]
                if u in L or v in R:ok=False;break
                L.add(u);R.add(v)
            if ok:hit=list(comb);break
        if hit is not None:
            best=hit;break
    return {
      "degree_sequence_left":[deg[v] for v in PA],
      "degree_sequence_right":[deg[v] for v in PD],
      "Delta_X":delta,
      "nu_X":len(best),
      "canonical_maximum_matching_edge_indices":best
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True)
    ap.add_argument("--freeze",required=True)
    ap.add_argument("--table",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    cand=json.load(open(a.candidate));fr=json.load(open(a.freeze));F=fr["frame"]
    V=F["vertices"];baseE=eset(F["base_non_port_edges"]);ports=[tuple(x) for x in F["port_edge_order"]]
    PA=F["left_ports"];PD=F["right_ports"];prov=F["frozen_provenance_coloring"]
    incompatible={i for i,(u,v) in enumerate(ports) if prov[u]==prov[v]}
    seven_info=precompute_seven_sets(V,baseE,ports)

    counts=Counter();maxdelta=-1;maxnu=-1;firstM2=None;firstC2=None
    table_ok=True;table_lines=0
    with open(a.table,encoding="utf-8") as fh:
        for mask in range(65536):
            line=fh.readline()
            if not line:
                table_ok=False;break
            table_lines+=1
            row=json.loads(line)
            ids=selected(mask)
            if row.get("mask")!=mask or row.get("selected_port_edge_indices")!=ids:
                table_ok=False;break
            conflicts=sorted(i for i in ids if i in incompatible)
            if conflicts:
                counts["PROVENANCE_IMPROPER_PORT_EDGE"]+=1
                if not(row.get("status")=="FRAME_INADMISSIBLE" and row.get("reason")=="PROVENANCE_IMPROPER_PORT_EDGE" and row.get("conflicting_edge_indices")==conflicts):
                    table_ok=False;break
                continue
            p7=first_p7_direct(mask,seven_info)
            if p7 is not None:
                counts["INDUCED_P7_PRESENT"]+=1
                if not(row.get("status")=="FRAME_INADMISSIBLE" and row.get("reason")=="INDUCED_P7_PRESENT" and row.get("p7_vertices")==p7):
                    table_ok=False;break
                continue
            met=matching_metric(mask,ports,PA,PD)
            counts["ADMISSIBLE"]+=1
            maxdelta=max(maxdelta,met["Delta_X"]);maxnu=max(maxnu,met["nu_X"])
            if met["Delta_X"]>=2 and firstM2 is None:firstM2=mask
            if met["nu_X"]==4 and firstC2 is None:firstC2=mask
            if row.get("status")!="FRAME_ADMISSIBLE" or row.get("reason")!="ADMISSIBLE":
                table_ok=False;break
            for k,v in met.items():
                if row.get(k)!=v:
                    table_ok=False;break
            if not table_ok:break
        if table_ok and fh.readline():
            table_ok=False

    M="M2_NONMATCHING_PORT_CHANNEL_WITNESS" if firstM2 is not None else "M1_PORT_CHANNEL_MATCHING_STRUCTURE_UNIVERSAL"
    C="C2_FOURTH_INDEPENDENT_DIRECT_CHANNEL_WITNESS" if firstC2 is not None else "C1_DIRECT_CHANNEL_MATCHING_NUMBER_LE3_UNIVERSAL"
    checks={
      "table_complete_and_exact":table_ok and table_lines==65536,
      "raw_accounting":sum(counts.values())==65536,
      "candidate_raw_accounting":cand["enumeration"]["raw_masks_accounted"]==65536,
      "reason_histogram":dict(sorted(counts.items()))==cand["enumeration"]["reason_histogram"],
      "admissible_count":counts["ADMISSIBLE"]==cand["enumeration"]["admissible_count"],
      "max_delta":maxdelta==cand["enumeration"]["max_Delta_over_admissible"],
      "max_nu":maxnu==cand["enumeration"]["max_nu_over_admissible"],
      "M_verdict":M==cand["M_axis"]["verdict"],
      "C_verdict":C==cand["C_axis"]["verdict"],
      "first_M2_mask":firstM2==(cand["M_axis"]["first_authoritative_witness"]["mask"] if cand["M_axis"]["first_authoritative_witness"] else None),
      "first_C2_mask":firstC2==(cand["C_axis"]["first_authoritative_witness"]["mask"] if cand["C_axis"]["first_authoritative_witness"] else None),
      "both_axes":cand["both_axes_completed"] is True and cand["early_stop_used"] is False,
      "current_control":cand["controls"]["current_Q2"]["pass"] is True,
      "synthetic_C2_control":cand["controls"]["synthetic_C2"]["pass"] is True,
      "synthetic_M2_control":cand["controls"]["synthetic_M2"]["pass"] is True,
      "no_forbidden":all(v is False for v in cand["oracle_use"].values()),
      "ceiling":cand["scientific_ceiling"]["UNIVERSAL_SEPARATOR4_COMPOSITION"]=="NOT_OPENED" and cand["scientific_ceiling"]["TW4"]=="NOT_OPENED" and cand["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and cand["scientific_ceiling"]["P_VS_NP"]=="OPEN",
      "stop":cand["stop"] is True
    }
    verdict="INDEPENDENT_BOTH_CHANNEL_AXES_EXHAUSTIVELY_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={
      "schema":"janus.trump.c11_two_octahedron_channel_structure.independent.v1",
      "verdict":verdict,
      "checks":checks,
      "independent_reason_histogram":dict(sorted(counts.items())),
      "independent_admissible_count":counts["ADMISSIBLE"],
      "independent_max_Delta":maxdelta,
      "independent_max_nu":maxnu,
      "independent_M_verdict":M,
      "independent_C_verdict":C,
      "first_M2_mask":firstM2,
      "first_C2_mask":firstC2,
      "scientific_ceiling":cand["scientific_ceiling"]
    }
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v],"M":M,"C":C,"counts":dict(counts),"maxDelta":maxdelta,"maxNu":maxnu},sort_keys=True))
    if verdict!="INDEPENDENT_BOTH_CHANNEL_AXES_EXHAUSTIVELY_VERIFIED":raise SystemExit(1)

if __name__=="__main__":main()
