#!/usr/bin/env python3
"""TIME-SAT-004E12C1: source-sound wide XOR detection + bounded original RAW pilot.

Synthetic NEW generator/size/seed SHA, previous E12C0 cost audit as training.
A source certificate can be admitted only with ALL source full forbidden sign
masks of one parity. Every extra original clause survives intact. Fast raw
probe may finish SAT before XOR is attempted, counted in full cold wall.
Never infer UNSAT from timeouts; P=NP and external independent witness OPEN.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import itertools
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter,process_time
import janus_time_sat_004e12b_support_index as b
from janus_time_sat_004e8_model_first import planted_clause

ROOT=Path("experiments/time_sat_004_external")
PLAN=ROOT/"PREREGISTERED_004E12C1_COST_AWARE_BASELINE_20261102.json"
BLOB="e508a1b7a249325e64c470e1360206675b2554d3"
AUDIT=ROOT/"time_sat_004e12c0_evidence/DEVELOPMENT_SOURCE_COST_AUDIT.json"
AUDIT_BLOB="77f710fda77dbdde02fb3f7afb113d44a999b371"
IDS=("e12c1-knight-grid-g13","e12c1-knight-grid-g17",
     "e12c1-circulant-prime-n257","e12c1-circulant-prime-n331",
     "e12c1-random-hypergraph-w5-n180","e12c1-random-hypergraph-w6-n160",
     "e12c1-low-cover-w5-n180","e12c1-exactone-t30",
     "e12c1-mixed-xor3-n160","e12c1-planted-3sat-n200")
VARIANTS=("as_emitted","global_clause_literal_shuffle","round_robin_support_literal_shuffle")
ARMS=("e12c1_cost_aware","e12b_support_index","unaltered_e11_prefix",
      "native_width3_6","raw_cms","cadical195_original")
HOSTS=("ubuntu-22.04","ubuntu-24.04")
REPS=2;CPU=12;WALL=18;MEM=2147483648
PROBE_WALL=0.35
SAT=b.SAT
ALLOWED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}
SEED=202611022317
def sha(x):return sha256(x).hexdigest()

def frozen():
    g=subprocess.run(["git","hash-object",str(PLAN)],capture_output=True,text=True,check=True).stdout.strip()
    if g!=BLOB:raise AssertionError("E12C1 preregistered source/method protocol changed")
    h=subprocess.run(["git","hash-object",str(AUDIT)],capture_output=True,text=True,check=True).stdout.strip()
    if h!=AUDIT_BLOB:raise AssertionError("Development-only E12C0 auditor was modified")
    p=json.loads(PLAN.read_text())
    q=p["limits"];d=p["calibration"];c=p["new_original_source_configs"]
    if (tuple(x["id"] for x in c)!=IDS or tuple(p["variants"])!=VARIANTS
        or tuple(p["arms"])!=ARMS or tuple(q["OS"])!=HOSTS
        or (q["VMs"],q["max_parallel"],q["planned_cold_children"],q["repeats"])!=(20,8,720,2)
        or (q["CPU_soft_s"],q["WALL_s"],q["RLIMIT_AS_bytes"])!=(CPU,WALL,MEM)
        or d["raw_probe_wall_budget_s"]!=PROBE_WALL
        or d["eligible_widths_for_native_early_raw_race"]!=[5]
        or d["min_original_coverage"]!=0.70
        or d["min_equations_for_candidate"]!=4
        or p["science_gates"]["external_independent_custodians"]!=0):
        raise AssertionError("Frozen 004E12C1 unregistered sources, parameters or scientific gates")
    t=json.loads(AUDIT.read_text())
    if (t["source_E12B_run"]!="41479552023"
        or t["source_SAT_verified"]!=576
        or t["CPU_UNKNOWN"]!=24 or t["actual_completed_pairs"]!=456
        or t["E12C_candidate"]!="NOT_IMPLEMENTED"):
        raise AssertionError("Model calibration source is not the verified E12C0 DEVELOPMENT archive")
    return p

def source(case):
    if case not in IDS:raise AssertionError("Foreign E12C1 SAT source")
    q=frozen()["new_original_source_configs"][IDS.index(case)]
    family=q["family"];size=q["size"];rng=random.Random(q["seed"])
    if family=="exactone":
        # Explicit exact-one independent internal generation; neighbor constraints are
        # NOT added, so a complete planted assignment always exists.
        k=5;n=k*size
        pick=[rng.randrange(k) for _ in range(size)]
        model=[k*t+j+1 if pick[t]==j else -(k*t+j+1)
               for t in range(size) for j in range(k)]
        rows=[]
        for t in range(size):
            group=[k*t+j+1 for j in range(k)]
            rows.append(group)
            rows.extend([[-a,-d] for a,d in itertools.combinations(group,2)])
    elif family in ("mixedxor3","planted3sat"):
        n=size
        truth={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
        model=[i if truth[i] else -i for i in range(1,n+1)]
        rows=[];used=set()
        if family=="mixedxor3":
            for _ in range(size*2):
                support=tuple(sorted(rng.sample(range(1,n+1),3)))
                if support in used:continue
                used.add(support)
                rhs=sum(int(truth[v]) for v in support)%2
                for bits in itertools.product((0,1),repeat=3):
                    if sum(bits)%2!=rhs:
                        rows.append([v if not flag else -v for v,flag in zip(support,bits)])
        seen={tuple(sorted(r)) for r in rows};needed=size*4
        for attempt in range(needed*30):
            if needed<=0:break
            candidate=planted_clause(rng,n,truth)
            if candidate is None:continue
            key=tuple(sorted(candidate))
            if key in seen:continue
            rows.append(list(candidate));seen.add(key);needed-=1
        if needed:raise AssertionError("Planted CNF failed unique-clause budget")
    else:
        n=size if family in ("circulant5","randomhyper5","randomhyper6","lowcover5") else size*size
        truth={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
        model=[i if truth[i] else -i for i in range(1,n+1)]
        supports=[]
        if family=="knight5":
            for y in range(size):
                for x in range(size):
                    loc=[(y,x),(y,(x+2)%size),(y,(x-2)%size),
                         ((y+1)%size,(x+1)%size),((y-1)%size,(x-1)%size)]
                    supports.append(tuple(sorted(1+iy*size+ix for iy,ix in loc)))
        elif family=="circulant5":
            for base in range(n):
                supports.append(tuple(sorted(1+(base+off)%n for off in q["offsets"])))
        elif family.startswith("randomhyper") or family=="lowcover5":
            width=6 if family=="randomhyper6" else 5
            count=n if family!="lowcover5" else n//2
            seen=set()
            while len(seen)<count:
                seen.add(tuple(sorted(rng.sample(range(1,n+1),width))))
            supports=list(sorted(seen))
        else:raise AssertionError("Unknown new SAT generator family")
        if len(supports)!=len(set(supports)) or any(len(x)!=len(set(x)) for x in supports):
            raise AssertionError("Source hypergraph support duplicate/degenerate")
        blocks=[]
        for support in supports:
            rhs=sum(int(truth[v]) for v in support)%2
            clauses=[]
            for bits in itertools.product((0,1),repeat=len(support)):
                if sum(bits)%2==rhs:continue
                clauses.append([v if not bit else -v for v,bit in zip(support,bits)])
            rng.shuffle(clauses);blocks.append(clauses)
        rng.shuffle(blocks)
        rows=[row for block in blocks for row in block]
        if family=="lowcover5":
            seen={tuple(sorted(c)) for c in rows}
            left=n*10
            for _ in range(left*30):
                if not left:break
                clause=planted_clause(rng,n,truth)
                if clause is None or tuple(sorted(clause)) in seen:continue
                seen.add(tuple(sorted(clause)));rows.append(list(clause));left-=1
            if left:raise AssertionError("Unmet low-coverage source clauses")
    if not b.old.all_model_ok(rows,n,model):
        raise AssertionError("New planted original complete SAT model false")
    raw=b.old.original_cnf(n,rows)
    return {"id":case,"family":family,"n":n,"m":len(rows),"rows":rows,
        "model":model,"model_sha":sha(json.dumps(model).encode()),
        "bytes":raw,"sha":sha(raw),"origin":"JANUS_INTERNAL_NEW_SOURCE_NONSECRET"}

def variant(case,name):
    if name not in VARIANTS:raise AssertionError("Unregistered source presentation")
    s=source(case);rows=[list(r) for r in s["rows"]]
    if name!="as_emitted":
        spec=frozen()["new_original_source_configs"][IDS.index(case)]
        rng=random.Random(spec["seed"]+100003*VARIANTS.index(name))
        if name=="global_clause_literal_shuffle":
            for row in rows:rng.shuffle(row)
            rng.shuffle(rows)
        else:
            groups=defaultdict(list)
            for row in rows:groups[tuple(sorted(abs(x) for x in row))].append(row)
            supports=sorted(groups);rng.shuffle(supports)
            for key in supports:
                rng.shuffle(groups[key])
                for row in groups[key]:rng.shuffle(row)
            rows=[groups[sup][i] for i in range(max(map(len,groups.values())))
                 for sup in supports if i<len(groups[sup])]
    if Counter(tuple(sorted(r)) for r in rows)!=Counter(tuple(sorted(r)) for r in s["rows"]):
        raise AssertionError("SAT-equivalent source permutation changed original clause multiset")
    if not b.old.all_model_ok(rows,s["n"],s["model"]):
        raise AssertionError("Complete original source SAT model false under equivalent permutation")
    raw=s["bytes"] if name=="as_emitted" else b.old.original_cnf(s["n"],rows)
    return {**s,"rows":rows,"bytes":raw,"sha":sha(raw),"base_sha":s["sha"],"variant":name}

def source_index_all_widths(rows,n):
    """Sound source-only 3/4/5/6-bit XOR masks, unique indices; all leftover CNF."""
    if not 1<=n<=30000 or len(rows)>30000:raise AssertionError("Source cap")
    groups=defaultdict(dict);total_lits=0
    for i,row in enumerate(rows):
        total_lits+=len(row)
        if total_lits>140000:raise AssertionError("Literal cap")
        if any(type(v)!=int or v==0 or abs(v)>n for v in row):
            raise AssertionError("Illegal source literal")
        width=len(row)
        if width not in (3,4,5,6) or len({abs(v) for v in row})!=width:continue
        key=tuple(sorted(abs(v) for v in row))
        if key not in groups and len(groups)>=30000:raise AssertionError("Support cap")
        vals={abs(v):v<0 for v in row}
        mask=tuple(int(vals[v]) for v in key)
        groups[key].setdefault(mask,i)
    equations=[];used=set();counts=Counter()
    for key,masked in sorted(groups.items()):
        w=len(key)
        if len(masked)!=2**(w-1):continue
        parity={sum(mask)%2 for mask in masked}
        if len(parity)!=1:continue
        forbidden=next(iter(parity))
        expected={mask for mask in itertools.product((0,1),repeat=w)
                 if sum(mask)%2==forbidden}
        if set(masked)!=expected:raise AssertionError("Source parity certificate incomplete")
        indices=[masked[x] for x in sorted(masked)]
        if any(i in used for i in indices):raise AssertionError("Source clause double allocation")
        used.update(indices)
        equations.append({"variables":list(key),"rhs":1-forbidden,
            "original_clause_indices":indices,"certificate":"FULL_SOURCE_SIGN_MASKS",
            "width":w})
        counts[w]+=1
    return {"equations":equations,"used":used,"counts":dict(counts),
        "covered_source_fraction":len(used)/len(rows) if rows else 0.0,
        "covered_by_width":{str(w):sum(len(eq["original_clause_indices"])
                  for eq in equations if eq["width"]==w) for w in (3,4,5,6)},
        "scan_original_clauses":len(rows),"scan_original_literals":total_lits}

def index_or_raw(rows,n,mode):
    if mode not in ARMS:raise AssertionError("Unknown frozen arm")
    if mode=="raw_cms" or mode=="cadical195_original":
        return {"equations":[],"cnf_clauses":rows,"choice":"RAW_ORIGINAL",
                "decision":{"eligible":False,"reason":"NO_INDEX_BASELINE"}}
    if mode=="unaltered_e11_prefix":
        prior=b.old.policy(rows,n,"e11_prefix_certified",b.old.frozen_e9_model())
        return {**prior,"decision":{"eligible":prior["choice"]=="native_xor",
                    "reason":"E11_FROZEN_PREFIX"}}
    if mode=="e12b_support_index":
        previous=b.policy(rows,n,"e12b_support_index")
        return {**previous,"decision":{"eligible":previous["decision"]["choice"]=="XOR",
                    "reason":"E12B_FROZEN"}}
    try:index=source_index_all_widths(rows,n)
    except (AssertionError,MemoryError):
        return {"equations":[],"cnf_clauses":rows,"choice":"C1_FAIL_CLOSED_RAW",
                "decision":{"eligible":False,"reason":"SOURCE_CAP_OR_MALFORMED"}}
    count5=index["counts"].get(5,0)
    coverage5=index["covered_by_width"]["5"]/len(rows) if rows else 0
    eligible=count5>=4 and coverage5>=0.70
    if mode=="native_width3_6":
        selected=index["equations"]
        chosen="NATIVE_VERIFIED_3_6"
    else:
        selected=[x for x in index["equations"] if x["width"]==5] if eligible else []
        chosen="C1_ELIGIBLE_XOR_WITH_RAW_PROBE" if eligible else "C1_OOD_ABSTAIN_RAW"
    used=set(i for eq in selected for i in eq["original_clause_indices"])
    if any(i<0 or i>=len(rows) for i in used):
        raise AssertionError("Out of original source")
    return {"equations":selected,"cnf_clauses":[row for i,row in enumerate(rows) if i not in used],
        "choice":chosen,"decision":{"eligible":eligible,"width5_equations":count5,
            "width5_original_clause_coverage":coverage5,
            "full_source_width_distribution":index["counts"],
            "cost_model":"E12C0_DEVELOPMENT_FAST_RAW_PROBE_0_35S"}}

def lock_sources(out):
    frozen();locked={}
    for case in IDS:
        locked[case]={};decisions=set()
        for v in VARIANTS:
            src=variant(case,v)
            c=index_or_raw(src["rows"],src["n"],"e12c1_cost_aware")
            decisions.add(c["decision"]["eligible"])
            locked[case][v]={
                "original_source_SHA256":src["base_sha"],"original_variant_CNF_SHA256":src["sha"],
                "full_SAT_model_SHA256":src["model_sha"],"n":src["n"],"m":src["m"],
                "source_family_internal":src["family"],
                "candidate_source_XOR_eligible":c["decision"]["eligible"],
                "source_multiset_exact":True}
        if len(decisions)!=1:raise AssertionError("C1 source eligibility not reorder invariant before any worker")
    output={"schema":"JANUS-TIME-SAT-004E12C1-10-ORIGINAL-30-VARIANTS-FROZEN-BEFORE-WORKERS",
        "prereg_Git_blob":BLOB,"training_E12C0_Git_blob":AUDIT_BLOB,"source":locked,
        "original_groups":10,"source_variants":30,"independent_external_originals":0,
        "C023_main":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(output,indent=2,sort_keys=True)+"\n"
    (out/"SOURCE_LOCK.json").write_text(payload)
    (out/"SOURCE_LOCK.sha256").write_text(sha(payload.encode())+"  SOURCE_LOCK.json\n")
    print("E12C1_SOURCE_AND_COST_POLICY_FROZEN",json.dumps({
        "original_groups":10,"source_SHA_variants":30,
        "eligibility":{x:locked[x]["as_emitted"]["candidate_source_XOR_eligible"] for x in IDS},
        "lock_sha256":sha(payload.encode())},sort_keys=True))

def load_lock(path):
    payload=path.read_bytes()
    if path.with_name("SOURCE_LOCK.sha256").read_text().strip()!=sha(payload)+"  SOURCE_LOCK.json":
        raise AssertionError("Preworker CNF/model lock SHA drift")
    l=json.loads(payload)
    if l.get("schema")!="JANUS-TIME-SAT-004E12C1-10-ORIGINAL-30-VARIANTS-FROZEN-BEFORE-WORKERS" or (
        l.get("prereg_Git_blob"),l.get("training_E12C0_Git_blob"))!=(BLOB,AUDIT_BLOB) or (
        set(l.get("source",{}))!=set(IDS)):
        raise AssertionError("Unregistered preworker exact original SAT source/model lock")
    return l,sha(payload)

def run_solver(rows,n,picked,arm):
    if arm=="cadical195_original":
        from pysat.solvers import Solver
        with Solver(name="cadical195",bootstrap_with=rows) as slv:
            stamp=perf_counter();res=slv.solve();time_s=perf_counter()-stamp
            model=slv.get_model() if res is True else None
    else:
        import pycryptosat
        solver=pycryptosat.Solver(threads=1)
        for eq in picked["equations"]:solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
        for row in picked["cnf_clauses"]:solver.add_clause(row)
        stamp=perf_counter();res,ans=solver.solve();time_s=perf_counter()-stamp
        model=[i if bool(ans[i]) else -i for i in range(1,n+1)] if (
            res is True and ans is not None and len(ans)>n) else None
    if res is False:raise AssertionError("UNSAT on known SAT-source with complete original model")
    if res is True:
        if model is None or not b.old.original_model_replay(rows,n,model):
            raise AssertionError("Invalid SAT model on exact original CNF")
    return res,model,time_s

def child(case,v,arm,lockpath,expected):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    lock,locksha=load_lock(lockpath)
    src=variant(case,v);pin=lock["source"][case][v]
    if ((src["sha"],src["base_sha"],src["model_sha"],src["n"],src["m"])!=
        (pin["original_variant_CNF_SHA256"],pin["original_source_SHA256"],
         pin["full_SAT_model_SHA256"],pin["n"],pin["m"])
        or src["sha"]!=expected):raise AssertionError("Original source/model SHA mutated after lock")
    with TemporaryDirectory() as d:
        path=Path(d)/"source.cnf";path.write_bytes(src["bytes"])
        dims=b.old.scan_dimacs(path)
        if (dims["n_variables"],dims["n_clauses"],dims["n_literal_occurrences"])!=(
            src["n"],src["m"],sum(len(r) for r in src["rows"])):
            raise AssertionError("Strict original DIMACS shape corrupted")
        original=b.old.read_cnf(path,src["n"],src["m"],max_literals=200000)
    if original!=src["rows"] or not b.old.all_model_ok(original,src["n"],src["model"]):
        raise AssertionError("Original SAT-model-before-solver failed")
    index_start=perf_counter()
    picked=index_or_raw(original,src["n"],arm)
    analysis_s=perf_counter()-index_start
    if arm=="e12c1_cost_aware" and picked["decision"]["eligible"]!=pin["candidate_source_XOR_eligible"]:
        raise AssertionError("C1 eligibility differs from source-only frozen preworker decision")
    raw_probe_status="NOT_ELIGIBLE";probe_wall_s=0.;solver_wall=0.
    if arm=="e12c1_cost_aware" and picked["decision"]["eligible"]:
        raw_start=perf_counter()
        cmd=[sys.executable,str(Path(__file__).resolve()),"--raw-probe",
             "--case",case,"--variant",v,"--expected-sha",src["sha"]]
        try:
            sub=subprocess.run(cmd,capture_output=True,text=True,timeout=PROBE_WALL,check=False)
            if sub.returncode==0:
                info=json.loads(sub.stdout)
                if (info.get("original_variant_CNF_SHA256")==src["sha"]
                    and info.get("SAT") is True
                    and b.old.original_model_replay(original,src["n"],info["model"])):
                    raw_probe_status="VERIFIED_SAT_FAST_RAW"
                    res=True
                else:raise AssertionError("False fast RAW probe SAT source proof")
            else:raise AssertionError("Fast RAW probe executable failure, not allowed silent fallback")
        except subprocess.TimeoutExpired:
            raw_probe_status="BOUNDED_RAW_PROBE_TIMEOUT"
        probe_wall_s=perf_counter()-raw_start
        if raw_probe_status=="VERIFIED_SAT_FAST_RAW":
            model=info["model"];solver_wall=info["solve_s"]
        else:
            res,model,solver_wall=run_solver(original,src["n"],picked,arm)
    else:
        res,model,solver_wall=run_solver(original,src["n"],picked,arm)
    status=SAT if res is True else "UNKNOWN_SOLVER_NO_ANSWER"
    if status==SAT and not b.old.original_model_replay(original,src["n"],model):
        raise AssertionError("Final full original SAT replay failed")
    return {"status":status,"case":case,"variant":v,"arm":arm,
       "original_source_SHA256":src["base_sha"],
       "transformed_original_CNF_SHA256":src["sha"],
       "complete_planted_SAT_model_SHA256":src["model_sha"],
       "preworker_lock_SHA256":locksha,
       "predecision":picked["decision"],
       "raw_bounded_probe_status":raw_probe_status,"raw_probe_full_cold_wall_s":probe_wall_s,
       "source_index_analysis_s":analysis_s,"final_solver_wall_s":solver_wall,
       "selected_XOR":len(picked["equations"]),
       "complete_original_CNF_SAT_model_replay":"PASS" if status==SAT else "UNKNOWN",
       "inner_full_cold_wall_s":perf_counter()-started,
       "CPU_s":process_time(),"RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       "outside_custodian":False,"C023_main":"UNCHANGED"}

def probe(case,v,expected):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    src=variant(case,v)
    if src["sha"]!=expected:raise AssertionError("Fast RAW probe wrong source SHA")
    # Probe does not use planted model: only run the original raw CNF in CMS;
    # final model replay is performed independently in the parent.
    import pycryptosat
    solver=pycryptosat.Solver(threads=1)
    for row in src["rows"]:solver.add_clause(row)
    stamp=perf_counter();sat,ans=solver.solve();delta=perf_counter()-stamp
    if sat is not True:raise AssertionError("Fast RAW probe did not return verified SAT")
    model=[i if bool(ans[i]) else -i for i in range(1,src["n"]+1)]
    print(json.dumps({"SAT":True,"original_variant_CNF_SHA256":src["sha"],
        "model":model,"solve_s":delta},sort_keys=True))

def matrix(case,lockpath,out):
    frozen();lock,locksha=load_lock(lockpath)
    if case not in IDS:raise AssertionError("Foreign matrix case")
    records=[]
    for v in VARIANTS:
        src=variant(case,v)
        if src["sha"]!=lock["source"][case][v]["original_variant_CNF_SHA256"]:
            raise AssertionError("Source stale")
        for rep in range(REPS):
            arms=list(ARMS)
            random.Random(SEED+101*IDS.index(case)+79*VARIANTS.index(v)+rep).shuffle(arms)
            for arm in arms:
                started=perf_counter()
                cmd=[sys.executable,str(Path(__file__).resolve()),"--child",
                     "--case",case,"--variant",v,"--arm",arm,
                     "--source-lock",str(lockpath),"--expected-sha",src["sha"]]
                try:
                    r=subprocess.run(cmd,capture_output=True,text=True,timeout=WALL,check=False)
                    if r.returncode:
                        outcome=b.old.classify_nonzero_exit(r.returncode)
                        outcome["status"]=outcome.get("verdict","UNKNOWN_UNCLASSIFIED")
                        outcome["stderr_tail"]=r.stderr[-800:]
                    else:outcome=json.loads(r.stdout)
                except subprocess.TimeoutExpired:outcome={"status":"UNKNOWN_WALL_TIMEOUT"}
                records.append({"variant":v,"repeat":rep,"arm":arm,"order":arms,
                    "full_cold_child_wall_s":perf_counter()-started,"outcome":outcome})
                print("E12C1_CHILD",case,v,rep,arm,outcome["status"],
                      round(records[-1]["full_cold_child_wall_s"],4),flush=True)
    if len(records)!=36 or any(r["outcome"]["status"] not in ALLOWED for r in records):
        raise AssertionError("C1 unknown exit or missing trial")
    result={"schema":"JANUS-TIME-SAT-004E12C1-36-FROZEN-COLD-ORIGINAL-VM-V1",
        "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),"original_HEAD":os.getenv("GITHUB_SHA","LOCAL"),
        "original_runner":os.getenv("RUNNER_NAME","LOCAL"),"original_os":os.getenv("E12C1_OS","LOCAL"),
        "case":case,"family":source(case)["family"],
        "original_source_SHA256":source(case)["sha"],"full_model_SHA256":source(case)["model_sha"],
        "preworker_lock_SHA256":locksha,"prereg_Git_blob":BLOB,
        "repeats":2,"variants":3,"arms":6,"children":36,"CPU":CPU,"WALL":WALL,"MEM":MEM,
        "external_independent_sources":0,"C023_main":"UNCHANGED","records":records}
    out.mkdir(parents=True,exist_ok=True)
    (out/(case+"__"+os.getenv("E12C1_OS","LOCAL")+".json")).write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("E12C1_SOURCE_WORKER_PASS",case,len(records),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    ap.add_argument("--child",action="store_true")
    ap.add_argument("--raw-probe",action="store_true")
    ap.add_argument("--case",choices=IDS)
    ap.add_argument("--variant",choices=VARIANTS)
    ap.add_argument("--arm",choices=ARMS)
    ap.add_argument("--expected-sha",default="")
    ap.add_argument("--source-lock",type=Path)
    ap.add_argument("--out",type=Path)
    x=ap.parse_args()
    if x.raw_probe:probe(x.case,x.variant,x.expected_sha)
    elif x.preflight:lock_sources(x.out)
    elif x.child:print(json.dumps(child(x.case,x.variant,x.arm,x.source_lock,x.expected_sha),sort_keys=True))
    else:matrix(x.case,x.source_lock,x.out)
