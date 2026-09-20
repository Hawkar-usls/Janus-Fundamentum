#!/usr/bin/env python3
import argparse,itertools,json,pathlib,hashlib
from collections import Counter

COLORS={1,2,3,4}
def ek(a,b):return tuple(sorted((a,b)))
def eset(E):return {ek(a,b) for a,b in E}
def adjacent(E,a,b):return ek(a,b) in E

def connected(V,E):
    V=set(V)
    if not V:return True
    seen=set();stack=[next(iter(V))]
    while stack:
        v=stack.pop()
        if v in seen:continue
        seen.add(v)
        for a,b in E:
            if a==v and b in V-seen:stack.append(b)
            elif b==v and a in V-seen:stack.append(a)
    return seen==V

def is_induced_p7(S,E):
    SS=set(S)
    sub=[x for x in E if x[0] in SS and x[1] in SS]
    if len(sub)!=6:return False
    deg={v:0 for v in S}
    for a,b in sub:deg[a]+=1;deg[b]+=1
    return sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,set(sub))

def first_p7_direct(V,E):
    for S in itertools.combinations(V,7):
        if is_induced_p7(S,E):return list(S)
    return None

def selected(mask,n=16):return [i for i in range(n) if (mask>>i)&1]

def matching_metric(mask,ports,PA,PD):
    ids=selected(mask,len(ports))
    deg={v:0 for v in PA+PD}
    for i in ids:
        u,v=ports[i];deg[u]+=1;deg[v]+=1
    delta=max(deg.values()) if deg else 0
    best=[]
    for k in range(4,-1,-1):
        for comb in itertools.combinations(ids,k):
            L=[];R=[];ok=True
            for i in comb:
                u,v=ports[i]
                if u in L or v in R:ok=False;break
                L.append(u);R.append(v)
            if ok:
                best=list(comb);break
        if best or k==0:break
    return delta,len(best),best,[deg[v] for v in PA],[deg[v] for v in PD]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    cand=json.load(open(a.candidate));fr=json.load(open(a.freeze));F=fr["frame"]
    V=F["vertices"];base=eset(F["base_non_port_edges"]);ports=[tuple(x) for x in F["port_edge_order"]]
    PA=F["left_ports"];PD=F["right_ports"];prov=F["frozen_provenance_coloring"]
    incompatible={i for i,(u,v) in enumerate(ports) if prov[u]==prov[v]}

    counts=Counter();maxdelta=-1;maxnu=-1;firstM2=None;firstC2=None
    digest=hashlib.sha256()
    rows=[]
    # Independent method: direct induced-P7 enumeration only on provenance-compatible masks.
    for mask in range(65536):
        ids=selected(mask)
        conflicts=sorted(i for i in ids if i in incompatible)
        if conflicts:
            status=("FRAME_INADMISSIBLE","PROVENANCE_IMPROPER_PORT_EDGE")
            counts[status[1]]+=1
            class_token=f"{mask}:P:{','.join(map(str,conflicts))}\n"
        else:
            E=set(base)
            for i in ids:E.add(ek(*ports[i]))
            p7=first_p7_direct(V,E)
            if p7:
                status=("FRAME_INADMISSIBLE","INDUCED_P7_PRESENT")
                counts[status[1]]+=1
                class_token=f"{mask}:7:{','.join(p7)}\n"
            else:
                status=("FRAME_ADMISSIBLE","ADMISSIBLE")
                counts["ADMISSIBLE"]+=1
                delta,nu,match,dl,dr=matching_metric(mask,ports,PA,PD)
                maxdelta=max(maxdelta,delta);maxnu=max(maxnu,nu)
                if delta>=2 and firstM2 is None:firstM2=(mask,ids,delta,nu,match,dl,dr)
                if nu==4 and firstC2 is None:firstC2=(mask,ids,delta,nu,match,dl,dr)
                class_token=f"{mask}:A:{delta}:{nu}:{','.join(map(str,match))}\n"
        digest.update(class_token.encode())

    M="M2_NONMATCHING_PORT_CHANNEL_WITNESS" if firstM2 else "M1_PORT_CHANNEL_MATCHING_STRUCTURE_UNIVERSAL"
    C="C2_FOURTH_INDEPENDENT_DIRECT_CHANNEL_WITNESS" if firstC2 else "C1_DIRECT_CHANNEL_MATCHING_NUMBER_LE3_UNIVERSAL"

    checks={}
    checks["raw_accounting"]=sum(counts.values())==65536
    checks["candidate_raw_accounting"]=cand["enumeration"]["raw_masks_accounted"]==65536
    checks["reason_histogram"]=dict(sorted(counts.items()))==cand["enumeration"]["reason_histogram"]
    checks["admissible_count"]=counts["ADMISSIBLE"]==cand["enumeration"]["admissible_count"]
    checks["max_delta"]=maxdelta==cand["enumeration"]["max_Delta_over_admissible"]
    checks["max_nu"]=maxnu==cand["enumeration"]["max_nu_over_admissible"]
    checks["M_verdict"]=M==cand["M_axis"]["verdict"]
    checks["C_verdict"]=C==cand["C_axis"]["verdict"]
    checks["both_axes"]=cand["both_axes_completed"] is True and cand["early_stop_used"] is False
    checks["current_control"]=cand["controls"]["current_Q2"]["pass"] is True
    checks["synthetic_C2_control"]=cand["controls"]["synthetic_C2"]["pass"] is True
    checks["synthetic_M2_control"]=cand["controls"]["synthetic_M2"]["pass"] is True
    checks["no_forbidden"]=all(v is False for v in cand["oracle_use"].values())
    checks["ceiling"]=cand["scientific_ceiling"]["UNIVERSAL_SEPARATOR4_COMPOSITION"]=="NOT_OPENED" and cand["scientific_ceiling"]["TW4"]=="NOT_OPENED" and cand["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and cand["scientific_ceiling"]["P_VS_NP"]=="OPEN"
    checks["stop"]=cand["stop"] is True

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
      "independent_classification_digest":digest.hexdigest(),
      "first_M2_mask":firstM2[0] if firstM2 else None,
      "first_C2_mask":firstC2[0] if firstC2 else None,
      "scientific_ceiling":cand["scientific_ceiling"]
    }
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v],"M":M,"C":C,"counts":dict(counts),"maxDelta":maxdelta,"maxNu":maxnu},sort_keys=True))
    if verdict!="INDEPENDENT_BOTH_CHANNEL_AXES_EXHAUSTIVELY_VERIFIED":raise SystemExit(1)

if __name__=="__main__":main()
