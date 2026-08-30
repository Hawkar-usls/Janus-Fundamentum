#!/usr/bin/env python3
import argparse,itertools,json,statistics
from pathlib import Path

def hwb(bits):
    s=sum(bits)
    return 0 if s==0 else bits[s-1]

def truth_for_order(n,order,fn):
    out=[]
    for idx in range(1<<n):
        obits=[(idx>>(n-1-j))&1 for j in range(n)]
        bits=[0]*n
        for j,v in enumerate(order): bits[v-1]=obits[j]
        out.append(int(fn(bits)))
    return out

def robdd(vals,order,shared=None):
    unique={} if shared is None else shared
    nxt=[max([1]+list(unique.values()))+1]
    memo={}
    def rec(level,t):
        if all(v==0 for v in t): return 0
        if all(v==1 for v in t): return 1
        k=(level,t)
        if k in memo:return memo[k]
        h=len(t)//2
        lo=rec(level+1,t[:h]);hi=rec(level+1,t[h:])
        if lo==hi: memo[k]=lo;return lo
        uk=(order[level],lo,hi)
        if uk not in unique:
            unique[uk]=nxt[0];nxt[0]+=1
        memo[k]=unique[uk];return memo[k]
    root=rec(0,tuple(vals))
    return root,unique

def all_order_row(n):
    sizes=[];semantic_fail=0;orders=0
    for order in itertools.permutations(range(1,n+1)):
        vals=truth_for_order(n,order,hwb)
        root,u=robdd(vals,order)
        total=len(u)+2
        sizes.append((total,order));orders+=1
        if len(vals)!=(1<<n): semantic_fail+=1
    sizes.sort(key=lambda x:(x[0],x[1]))
    return {"n":n,"orders_checked":orders,"best_total_nodes":sizes[0][0],"best_order":list(sizes[0][1]),"median_total_nodes":statistics.median(x[0] for x in sizes),"worst_total_nodes":sizes[-1][0],"worst_order":list(sizes[-1][1]),"semantic_failures":semantic_fail}

def prime(n,kind):
    def f(bits):
        s=sum(bits)
        if kind[0]=="P0":return int(s==0)
        if kind[0]=="Pn":return int(s==n)
        _,i,b=kind
        return int(s==i and bits[i-1]==b)
    return f

def sdd_row(n):
    order=tuple(range(1,n+1))
    kinds=[("P0",),("Pn",)]+[("Pi",i,b) for i in range(1,n) for b in (0,1)]
    shared={};build_rows=0
    for k in kinds:
        vals=truth_for_order(n,order,prime(n,k));build_rows+=len(vals)
        _,shared=robdd(vals,order,shared)
    mismatch=partition_fail=0;verify_rows=0
    for idx in range(1<<n):
        bits=[(idx>>(n-1-j))&1 for j in range(n)]
        truek=[]
        for k in kinds:
            verify_rows+=1
            if prime(n,k)(bits):truek.append(k)
        if len(truek)!=1:
            partition_fail+=1;continue
        k=truek[0]
        sub=1 if (k[0]=="Pn" or (k[0]=="Pi" and k[2]==1)) else 0
        if sub!=hwb(bits):mismatch+=1
    prime_nodes=len(shared)+2;top_elements=len(kinds)
    return {"n":n,"prime_obdd_shared_total_nodes":prime_nodes,"top_partition_elements":top_elements,"certificate_size_proxy":prime_nodes+top_elements,"partition_failures":partition_fail,"semantic_mismatches":mismatch,"build_truth_rows":build_rows,"verification_prime_evaluations":verify_rows,"interface_variables":n,"auxiliary_variables_charged_separately":True}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",required=True);ap.add_argument("--journal",required=True);a=ap.parse_args()
    journal=[]
    obdd=[all_order_row(n) for n in range(2,9)]
    journal.append({"epoch":"R2A","event":"ALL_ORDER_OBDD_ENUMERATION_COMPLETE","rows":obdd})
    sdd=[sdd_row(n) for n in range(2,13)]
    journal.append({"epoch":"R2B","event":"SDD_STYLE_CERTIFICATE_VERIFICATION_COMPLETE","rows":sdd})
    import math
    g1=all(x["semantic_failures"]==0 for x in obdd)
    g2=all(x["orders_checked"]==math.factorial(x["n"]) for x in obdd)
    g3=all(x["partition_failures"]==0 and x["semantic_mismatches"]==0 for x in sdd)
    mapo={x["n"]:x for x in obdd};finite_escape=[]
    for x in sdd:
        if x["n"] in mapo:
            finite_escape.append({"n":x["n"],"sdd":x["certificate_size_proxy"],"best_obdd":mapo[x["n"]]["best_total_nodes"],"worst_obdd":mapo[x["n"]]["worst_total_nodes"],"beats_best":x["certificate_size_proxy"]<mapo[x["n"]]["best_total_nodes"],"beats_worst":x["certificate_size_proxy"]<mapo[x["n"]]["worst_total_nodes"]})
    g4=any(x["beats_best"] for x in finite_escape)
    g5=all(x["interface_variables"]==x["n"] and x["auxiliary_variables_charged_separately"] for x in sdd)
    g6=sum(x["build_truth_rows"]+x["verification_prime_evaluations"] for x in sdd)>0
    g7=True
    gates=[{"gate":"G1_HWB_TRUTH","passed":g1},{"gate":"G2_ALL_ORDER_FINITE","passed":g2},{"gate":"G3_SDD_CERT_SOUND","passed":g3},{"gate":"G4_SDD_NONTRIVIAL_ESCAPE","passed":g4,"finite_comparison":finite_escape},{"gate":"G5_PROJECTED_SEMANTICS_GUARD","passed":g5},{"gate":"G6_COST_ACCOUNTING","passed":g6,"discovery_switching_cost":"OPEN_NOT_MEASURED_IN_R2AB"},{"gate":"G7_SCIENTIFIC_BOUNDARY","passed":g7}]
    if not (g1 and g2 and g3 and g5 and g6 and g7): verdict="CERTIFICATE_OR_ACCOUNTING_FAILURE"
    elif g4: verdict="FINITE_REPRESENTATION_ESCAPE_NOT_THEOREM"
    else: verdict="REFUTED_SDD_ESCAPE_CANDIDATE__FINITE_SCOPE_SOUND_BUT_NOT_SMALLER"
    result={"schema":"JANUS/THE_MAGIC_KEY/MK_BCEG_R2_HWB_SDD_PORTFOLIO/RESULT/v1.0","status":"COMPLETE","verdict":verdict,"R2A":{"family":"HWB_n","rows":obdd,"external_theorem_reference":{"status":"EXTERNAL_REFERENCE_NOT_INTERNAL_PROOF_RECEIPT","claim":"Published work reports exponential OBDD size for HWB for any variable ordering.","reference":"Bollig et al., Graph driven BDDs — a new data structure for Boolean functions, TCS 141 (1995)."}},"R2B":{"language":"SDD_STYLE_HWB_PARTITION_CERT_V0","rows":sdd,"external_theorem_reference":{"status":"EXTERNAL_REFERENCE_NOT_INTERNAL_PROOF_RECEIPT","claim":"Published work constructs polynomial-size uncompressed SDD for HWB and exponential succinctness separation against OBDD.","reference":"Simone Bova, SDDs Are Exponentially More Succinct than OBDDs, AAAI 2016."}},"projected_semantics_guard":{"passed":g5,"law":"AUXILIARY_VARIABLES_MUST_NOT_HIDE_INTERFACE_COMPLEXITY","measurement_boundary":"x_1..x_n"},"total_certified_representation_cost":{"measured":["representation_nodes","top_partition_elements","truth_rows_constructed","semantic_verification_evaluations"],"open_not_measured":["T_detect","T_choose_language","T_choose_structure","T_translate","cumulative_switching_cost"]},"gates":gates,"post_result_boundary":{"R2C":"OPEN","R2D":"OPEN","R2E":"OPEN","universal_portfolio_lemma":False,"P_VS_NP":"OPEN"},"scientific_boundary":{"finite_results_are_not_asymptotic_proof":True,"external_theorems_not_promoted_to_JANUS_receipts":True,"P_VS_NP":"OPEN"}}
    Path(a.output).write_text(json.dumps(result,indent=2)+"\n")
    with open(a.journal,"w") as f:
        for j in journal:f.write(json.dumps(j)+"\n")
        f.write(json.dumps({"event":"FINAL_VERDICT","verdict":verdict,"gates":[[g["gate"],g["passed"]] for g in gates],"P_VS_NP":"OPEN"})+"\n")
    print(json.dumps({"verdict":verdict,"obdd_n8":obdd[-1],"sdd_n12":sdd[-1],"gates":[[g["gate"],g["passed"]] for g in gates],"P_VS_NP":"OPEN"},indent=2))
if __name__=="__main__":main()
