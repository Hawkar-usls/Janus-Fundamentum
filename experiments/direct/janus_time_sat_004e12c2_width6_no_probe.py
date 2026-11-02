#!/usr/bin/env python3
"""JANUS TIME-SAT-004E12C2: exact source-only width5/6 parity without 350ms RAW probe.

The candidate and its scientific cohort are immutable before the first worker.
All original inputs are JANUS-authored planted-SAT sources, NOT external tests.
A full complete model of each original CNF exists and is replayed before and
after every independent cold solver process. No production/main/C023 changes.
"""
from __future__ import annotations
import argparse,itertools,json,os,random,resource,subprocess,sys
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter,process_time
import janus_time_sat_004e12c1_cost_aware as c
import janus_time_sat_004e12b_support_index as b
from janus_time_sat_004e8_model_first import planted_clause

ROOT=Path("experiments/time_sat_004_external")
PLAN=ROOT/"PREREGISTERED_004E12C2_WIDTH6_NO_RAW_PROBE_20261102.json"
BLOB="417d3a81e6697b4cef9ffc6670b0a25f023993b1"
ARMS=("e12c2_certified_width5_6_no_probe","e12c1_frozen_raw_pilot",
      "e12b_frozen_width5","native_all_width3_6","raw_cms","cadical195_original")
VARIANTS=("as_emitted","global_clause_literal_shuffle",
          "round_robin_support_literal_shuffle")
HOSTS=("ubuntu-22.04","ubuntu-24.04")
IDS=("e12c2-ring6-n96","e12c2-ring6-n128","e12c2-hyper6-n110",
     "e12c2-hyper6-n140","e12c2-torus5-g12","e12c2-diagonal4-g12",
     "e12c2-exactone-t25","e12c2-mixed3-n130")
CPU=12;WALL=18;MEM=2147483648;REPS=2;PROBE=0.35
SAT=c.SAT
ALLOWED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}

def sha(x):return sha256(x).hexdigest()
def frozen():
    actual=subprocess.run(["git","hash-object",str(PLAN)],check=True,capture_output=True,text=True).stdout.strip()
    if actual!=BLOB:raise AssertionError("E12C2 original preregistered source/config changed")
    p=json.loads(PLAN.read_text())
    q=p["resources"];d=p["candidate"]
    if (tuple(x["id"] for x in p["source_cases"])!=IDS
        or tuple(p["methods"])!=ARMS or tuple(p["representations"])!=VARIANTS
        or tuple(q["OS"])!=HOSTS
        or (q["VMs"],q["max_parallel"],q["source_variants"],q["arms"],q["total_cold_children"])!=(16,6,3,6,576)
        or (q["CPU_soft_s"],q["WALL_s"],q["AS_bytes"])!=(CPU,WALL,MEM)
        or d["source_widths_allowed"]!=[5,6]
        or d["min_complete_source_certificates"]!=4
        or d["min_source_clause_fraction"]!=.70
        or d["raw_first_035_second_subprocess"] is not False
        or p["external_independent_custodian_count"]!=0
        or p["production_main_C023"]!="UNCHANGED"):
        raise AssertionError("E12C2 scientific protocol source/method/budget modified")
    return p

def original(case):
    p=frozen()
    if case not in IDS:raise AssertionError("Unregistered fresh original source")
    q=p["source_cases"][IDS.index(case)]
    family=q["family"]
    rng=random.Random(q["seed"])
    if family=="exactone":
        tasks=q["tasks"];k=5;n=tasks*k
        choices=[rng.randrange(k) for _ in range(tasks)]
        rows=[]
        for t in range(tasks):
            group=[k*t+j+1 for j in range(k)]
            rows.append(group)
            rows.extend([[-a,-z] for a,z in itertools.combinations(group,2)])
        model=[k*t+j+1 if choices[t]==j else -(k*t+j+1)
               for t in range(tasks) for j in range(k)]
    elif family=="mixed3":
        n=q["n"];truth={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
        model=[i if truth[i] else -i for i in range(1,n+1)]
        supports=set()
        while len(supports)<q["equations"]:
            supports.add(tuple(sorted(rng.sample(range(1,n+1),3))))
        rows=[];used=set()
        for support in sorted(supports):
            rhs=sum(truth[i] for i in support)%2
            for mask in itertools.product((0,1),repeat=3):
                if sum(mask)%2==rhs:continue
                clause=[v if not z else -v for v,z in zip(support,mask)]
                rows.append(clause);used.add(tuple(sorted(clause)))
        missing=q["guard_clauses"]
        for _ in range(missing*40):
            if not missing:break
            clause=planted_clause(rng,n,truth)
            if clause is None or tuple(sorted(clause)) in used:continue
            used.add(tuple(sorted(clause)));rows.append(list(clause));missing-=1
        if missing:raise AssertionError("Expected exact planted source 3CNF guards not attained")
    else:
        if family in ("ring6","hyper6"):n=q["n"]
        elif family in ("torus5","diagonal4"):n=q["size"]**2
        else:raise AssertionError("Foreign source family")
        truth={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
        model=[i if truth[i] else -i for i in range(1,n+1)]
        supports=set()
        if family=="ring6":
            offsets=q["offsets"]
            supports={tuple(sorted(1+(u+off)%n for off in offsets)) for u in range(n)}
        elif family=="hyper6":
            while len(supports)<q["equations"]:
                supports.add(tuple(sorted(rng.sample(range(1,n+1),6))))
        else:
            size=q["size"]
            for y in range(size):
                for x in range(size):
                    if family=="torus5":
                        cells=[(y,x),(y,(x+1)%size),(y,(x-1)%size),
                          ((y+1)%size,x),((y-1)%size,x)]
                    else:
                        cells=[(y,x),(y,(x+1)%size),
                          ((y+1)%size,x),((y+1)%size,(x+1)%size)]
                    supports.add(tuple(sorted(1+a*size+z for a,z in cells)))
        want=q.get("equations",n)
        if len(supports)!=want:raise AssertionError("Original graph source supports collapsed")
        blocks=[]
        for support in sorted(supports):
            width=len(support)
            if width not in (4,5,6):raise AssertionError("Wrong original support width")
            rhs=sum(truth[i] for i in support)%2
            block=[]
            for bits in itertools.product((0,1),repeat=width):
                if sum(bits)%2==rhs:continue
                block.append([v if not bit else -v for v,bit in zip(support,bits)])
            if len(block)!=2**(width-1):raise AssertionError("Not complete original parity masks")
            rng.shuffle(block);blocks.append(block)
        rng.shuffle(blocks)
        rows=[clause for block in blocks for clause in block]
    if len(rows)>30000 or sum(len(r) for r in rows)>140000:
        raise AssertionError("Original DIMACS exceeds frozen safe memory/scan limits")
    if not b.old.all_model_ok(rows,n,model):
        raise AssertionError("Original planted model invalid before any worker")
    payload=b.old.original_cnf(n,rows)
    return {"case":case,"family":family,"n":n,"m":len(rows),"rows":rows,
            "model":model,"model_sha":sha(json.dumps(model).encode()),
            "bytes":payload,"sha":sha(payload),"internal_source":True}

def signature(rows):return Counter(tuple(sorted(x)) for x in rows)

def variant(case,name):
    if name not in VARIANTS:raise AssertionError("Unsupported source permutation")
    src=original(case)
    seed=frozen()["source_cases"][IDS.index(case)]["seed"]
    rng=random.Random(seed+100003*VARIANTS.index(name))
    rows=[list(x) for x in src["rows"]]
    if name=="global_clause_literal_shuffle":
        for row in rows:rng.shuffle(row)
        rng.shuffle(rows)
    elif name=="round_robin_support_literal_shuffle":
        groups=defaultdict(list)
        for row in rows:groups[tuple(sorted(abs(x) for x in row))].append(row)
        supports=sorted(groups);rng.shuffle(supports)
        for key in supports:
            rng.shuffle(groups[key])
            for row in groups[key]:rng.shuffle(row)
        rows=[groups[key][j] for j in range(max(map(len,groups.values())))
              for key in supports if j<len(groups[key])]
    if (signature(rows)!=signature(src["rows"])
        or not b.old.all_model_ok(rows,src["n"],src["model"])):
        raise AssertionError("Permutation changes source semantics or planted model")
    data=src["bytes"] if name=="as_emitted" else b.old.original_cnf(src["n"],rows)
    return {**src,"rows":rows,"bytes":data,"sha":sha(data),
            "base_sha":src["sha"],"variant":name}

def policy(rows,n,arm):
    if arm not in ARMS:raise AssertionError("Never run an unregistered candidate")
    if arm=="raw_cms" or arm=="cadical195_original":
        return {"equations":[],"cnf_clauses":rows,"choice":"RAW_ORIGINAL",
                "decision":{"choice":"RAW","reason":"CONTROL"}}
    if arm=="e12b_frozen_width5":
        o=b.policy(rows,n,"e12b_support_index")
        return {**o,"decision":{"choice":o["decision"]["choice"],"reason":"PREVIOUS_E12B_FROZEN"}}
    if arm=="e12c1_frozen_raw_pilot":
        o=c.index_or_raw(rows,n,"e12c1_cost_aware")
        return {**o,"decision":{"choice":"XOR" if o["decision"].get("eligible") else "RAW",
                    "reason":"PREVIOUS_E12C1_FROZEN_WITH_350MS_PROBE",
                    "eligible":bool(o["decision"].get("eligible"))}}
    try:index=c.source_index_all_widths(rows,n)
    except (AssertionError,MemoryError):
        return {"equations":[],"cnf_clauses":rows,"choice":"C2_FAIL_CLOSED_RAW",
                "decision":{"choice":"RAW","reason":"SOURCE_SCAN_CAP_OR_INVALID"}}
    if arm=="native_all_width3_6":
        selected=index["equations"]
        tag="ALL_SOURCE_PROVED_WIDTH3_6"
    else:
        # The only NEW C2 selector change: exact 5/6 complete source masks.
        certified=[eq for eq in index["equations"] if eq["width"] in (5,6)]
        covered=sum(len(eq["original_clause_indices"]) for eq in certified)
        eligible=len(certified)>=4 and covered>=.70*len(rows)
        selected=certified if eligible else []
        tag="C2_CERTIFIED_XOR_5_6_NO_RAW_PROBE" if eligible else "C2_LOW_COVERAGE_RAW"
    used={j for eq in selected for j in eq["original_clause_indices"]}
    if sum(len(eq["original_clause_indices"]) for eq in selected)!=len(used):
        raise AssertionError("One source clause index used twice")
    residual=[row for i,row in enumerate(rows) if i not in used]
    return {"equations":selected,"cnf_clauses":residual,"choice":tag,
       "decision":{"choice":"XOR" if selected else "RAW",
            "certified_width_counts":index["counts"],
            "certified_selected_eq":len(selected),
            "certified_5_6_original_fraction":sum(len(x["original_clause_indices"]) for x in selected)/len(rows) if rows else 0,
            "probe_second_process_s":0.0,"source_only_no_generator_label":True}}

def preflight(out):
    frozen()
    lock={}
    used_original=set()
    for case in IDS:
        lock[case]={}
        decisions=set()
        original_src=original(case)
        if original_src["sha"] in used_original:raise AssertionError("Duplicate original SHA")
        used_original.add(original_src["sha"])
        for v in VARIANTS:
            s=variant(case,v)
            chosen=policy(s["rows"],s["n"],ARMS[0])
            decision=chosen["decision"]["choice"];decisions.add(decision)
            lock[case][v]={"original_SHA256":s["base_sha"],
               "original_variant_SHA256":s["sha"],
               "complete_original_model_SHA256":s["model_sha"],
               "n":s["n"],"m":s["m"],"family":s["family"],
               "frozen_candidate_choice":decision,
               "original_exact_clause_multiset_verified":True}
        if len(decisions)!=1:raise AssertionError("New C2 selector not order invariant")
    result={"schema":"JANUS-TIME-SAT-004E12C2-SOURCE-LOCK-BEFORE-16-VM",
         "prereg_protocol_git_blob":BLOB,
         "origins":lock,"original_sources":8,"variants":24,
         "external_independent_origin_count":0,"C023_main":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(result,sort_keys=True,indent=2)+"\n"
    (out/"SOURCE_LOCK.json").write_text(raw)
    (out/"SOURCE_LOCK.sha256").write_text(sha(raw.encode())+"  SOURCE_LOCK.json\n")
    print("E12C2_PREWORKER_SOURCE_LOCK_PASS",json.dumps({
        "originals":8,"transformed":24,
        "decisions":{case:lock[case]["as_emitted"]["frozen_candidate_choice"] for case in IDS},
        "lock_SHA":sha(raw.encode())},sort_keys=True))
    return result

def checked_lock(path):
    raw=path.read_bytes()
    if path.with_name("SOURCE_LOCK.sha256").read_text().strip()!=sha(raw)+"  SOURCE_LOCK.json":
        raise AssertionError("Source lock digest not valid")
    j=json.loads(raw)
    if (j.get("schema")!="JANUS-TIME-SAT-004E12C2-SOURCE-LOCK-BEFORE-16-VM"
        or j.get("prereg_protocol_git_blob")!=BLOB
        or set(j.get("origins",{}))!=set(IDS)
        or j.get("external_independent_origin_count")!=0):
        raise AssertionError("Foreign or altered presolve source manifest")
    return j,sha(raw)

def child(case,v,arm,lockpath,expected):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    lock,locksha=checked_lock(lockpath)
    s=variant(case,v);pin=lock["origins"][case][v]
    if (s["sha"],s["base_sha"],s["model_sha"],s["n"],s["m"])!=(
        pin["original_variant_SHA256"],pin["original_SHA256"],
        pin["complete_original_model_SHA256"],pin["n"],pin["m"]) or expected!=s["sha"]:
        raise AssertionError("Original/source model SHA mutated after preworker seal")
    with TemporaryDirectory() as d:
        f=Path(d)/"source-original.cnf"
        f.write_bytes(s["bytes"])
        q=b.old.scan_dimacs(f)
        if (q["n_variables"],q["n_clauses"],q["n_literal_occurrences"])!=(
           s["n"],s["m"],sum(map(len,s["rows"]))):
            raise AssertionError("Strict original DIMACS shape changed")
        rows=b.old.read_cnf(f,s["n"],s["m"],max_literals=200000)
    if rows!=s["rows"] or not b.old.all_model_ok(rows,s["n"],s["model"]):
        raise AssertionError("Full original SAT proof failed")
    begin=perf_counter();chosen=policy(rows,s["n"],arm)
    index_s=perf_counter()-begin
    if arm==ARMS[0] and chosen["decision"]["choice"]!=pin["frozen_candidate_choice"]:
        raise AssertionError("Frozen candidate source decision changed")
    raw_probe_status="NOT_RUN";probe_wall=0.
    if arm=="e12c1_frozen_raw_pilot" and chosen["decision"]["eligible"]:
        tick=perf_counter()
        command=[sys.executable,str(Path(__file__).resolve()),"--probe",
           "--case",case,"--variant",v,"--expected-sha",s["sha"]]
        try:
            r=subprocess.run(command,capture_output=True,text=True,timeout=PROBE,check=False)
            if r.returncode:
                raise AssertionError("RAW pilot child exited without valid SAT; not a timeout")
            original_result=json.loads(r.stdout)
            if (original_result.get("sha")!=s["sha"]
                or original_result.get("status")!="SAT"
                or not b.old.original_model_replay(rows,s["n"],original_result["model"])):
                raise AssertionError("RAW pilot returned untrusted source model")
            raw_probe_status="ORIGINAL_RAW_FAST_SAT_VERIFIED"
            solved=True;assignment=original_result["model"];solver_s=original_result["solver_s"]
        except subprocess.TimeoutExpired:
            raw_probe_status="ORIGINAL_RAW_PILOT_TIMEOUT"
        probe_wall=perf_counter()-tick
    if raw_probe_status!="ORIGINAL_RAW_FAST_SAT_VERIFIED":
        mapped="cadical195_original" if arm=="cadical195_original" else arm
        solved,assignment,solver_s=c.run_solver(rows,s["n"],chosen,mapped)
    status=SAT if solved is True else "UNKNOWN_SOLVER_NO_ANSWER"
    if status==SAT and not b.old.original_model_replay(rows,s["n"],assignment):
        raise AssertionError("Returned original SAT model wrong")
    return {"status":status,"case":case,"variant":v,"arm":arm,
       "original_source_SHA256":s["base_sha"],
       "transformed_source_SHA256":s["sha"],
       "original_complete_SAT_model_SHA256":s["model_sha"],
       "preworker_source_lock_SHA256":locksha,
       "frozen_decision":chosen["decision"]["choice"],
       "representation":chosen["choice"],
       "verified_native_XOR_equations":len(chosen["equations"]),
       "source_index_wall_s":index_s,"native_solver_wall_s":solver_s,
       "raw_probe_status":raw_probe_status,"raw_probe_wall_s":probe_wall,
       "full_cold_inner_wall_s":perf_counter()-started,
       "full_cold_CPU_s":process_time(),
       "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       "original_complete_CNF_model_replay":"PASS" if status==SAT else "UNKNOWN",
       "independent_external_source":False,"C023_main":"UNCHANGED"}

def pilot(case,v,expected):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    s=variant(case,v)
    if s["sha"]!=expected:raise AssertionError("Pilot source SHA incorrect")
    import pycryptosat
    q=pycryptosat.Solver(threads=1)
    for row in s["rows"]:q.add_clause(row)
    start=perf_counter();ok,ans=q.solve();elapsed=perf_counter()-start
    if ok is not True:raise AssertionError("Pilot was not SAT")
    model=[i if bool(ans[i]) else -i for i in range(1,s["n"]+1)]
    print(json.dumps({"status":"SAT","sha":s["sha"],"model":model,"solver_s":elapsed}))

def matrix(case,lockpath,out):
    frozen();lock,locksha=checked_lock(lockpath)
    receipts=[]
    for v in VARIANTS:
        ss=variant(case,v)
        if ss["sha"]!=lock["origins"][case][v]["original_variant_SHA256"]:
            raise AssertionError("Source variant preworker identity changed")
        for rep in range(2):
            arms=list(ARMS)
            random.Random(202611024300+101*IDS.index(case)+71*VARIANTS.index(v)+rep).shuffle(arms)
            for arm in arms:
                begin=perf_counter()
                cmd=[sys.executable,str(Path(__file__).resolve()),"--child",
                   "--case",case,"--variant",v,"--arm",arm,
                   "--source-lock",str(lockpath),"--expected-sha",ss["sha"]]
                try:
                    r=subprocess.run(cmd,text=True,capture_output=True,check=False,timeout=WALL)
                    if r.returncode:
                        status=b.old.classify_nonzero_exit(r.returncode)
                        status["status"]=status.get("verdict","UNSUPPORTED_FAIL")
                        status["returncode"]=r.returncode
                        status["stderr_tail"]=r.stderr[-600:]
                    else:status=json.loads(r.stdout)
                except subprocess.TimeoutExpired:
                    status={"status":"UNKNOWN_WALL_TIMEOUT"}
                receipts.append({"variant":v,"repeat":rep,"arm":arm,
                  "random_arm_order":arms,"full_cold_child_wall_s":perf_counter()-begin,
                  "outcome":status})
                print("E12C2_TRIAL",case,v,rep,arm,status["status"],round(receipts[-1]["full_cold_child_wall_s"],4),flush=True)
    if len(receipts)!=36 or any(x["outcome"].get("status") not in ALLOWED for x in receipts):
        raise AssertionError("Wrong source worker statuses or incomplete original 36 trials")
    out.mkdir(parents=True,exist_ok=True)
    d={"schema":"JANUS-TIME-SAT-004E12C2-36-COLD-ORIGINAL-VM-V1",
       "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
       "original_HEAD":os.getenv("GITHUB_SHA","LOCAL"),
       "original_runner_name":os.getenv("RUNNER_NAME","LOCAL"),
       "original_os":os.getenv("E12C2_OS","LOCAL"),
       "case":case,"family":ss["family"],"original_source_sha":original(case)["sha"],
       "source_model_sha":original(case)["model_sha"],
       "prereg_git_blob":BLOB,"source_lock_sha":locksha,
       "cold_children":36,"CPU":CPU,"WALL":WALL,"MEM":MEM,
       "outside_admin_sources":0,"C023_main":"UNCHANGED","records":receipts}
    (out/(case+"__"+os.getenv("E12C2_OS","LOCAL")+".json")).write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("E12C2_WORKER_ORIGINAL_36_PASS",case,flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight",action="store_true")
    parser.add_argument("--child",action="store_true")
    parser.add_argument("--probe",action="store_true")
    parser.add_argument("--case",choices=IDS)
    parser.add_argument("--variant",choices=VARIANTS)
    parser.add_argument("--arm",choices=ARMS)
    parser.add_argument("--expected-sha",default="")
    parser.add_argument("--source-lock",type=Path)
    parser.add_argument("--out",type=Path)
    x=parser.parse_args()
    if x.preflight:preflight(x.out)
    elif x.probe:pilot(x.case,x.variant,x.expected_sha)
    elif x.child:print(json.dumps(child(x.case,x.variant,x.arm,x.source_lock,x.expected_sha),sort_keys=True))
    else:matrix(x.case,x.source_lock,x.out)
