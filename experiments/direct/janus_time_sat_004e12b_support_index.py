#!/usr/bin/env python3
"""E12B: one-pass source-support-indexed exact XOR certificates, order invariant.

The original E11/E12A corpus is DISCLOSED DEVELOPMENT, never fresh holdout.
Frozen new seeds and sizes, all synthetic and internally generated. Original
complete SAT models and exact CNF SHA are locked BEFORE any worker starts.
There is no hidden-source or general winner claim, and no production change.
"""
from __future__ import annotations
import argparse
from collections import defaultdict,Counter
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
import janus_time_sat_004e11_parity_probe as old
import janus_time_sat_004e12a_clause_order as prior
from janus_time_sat_004e8_model_first import synth as planted_mixed
from janus_time_sat_004e6_semantic_selector import normalized_selector

ROOT=Path("experiments/time_sat_004_external")
PREREG=ROOT/"PREREGISTERED_004E12B_SUPPORT_INDEX_NEW_SIZES_20261102.json"
PREREG_BLOB="04c79834b227b2b814aa305bcea0a9813e23ed26"
MODEL_SHA=old.OLD_MODEL_SHA
VARIANTS=("as_emitted","global_clause_literal_shuffle",
          "round_robin_support_literal_shuffle")
ARMS=("e12b_support_index","unaltered_e11_prefix",
      "native_all","raw_cms","cadical195_original")
HOSTS=("ubuntu-22.04","ubuntu-24.04")
IDS=("e12b-torus-g14","e12b-torus-g18",
     "e12b-circulant-n288","e12b-circulant-n352",
     "e12b-diagonal-g16","e12b-diagonal-g22",
     "e12b-exactone-t24","e12b-exactone-t36",
     "e12b-mixedxor-n128","e12b-mixedxor-n192")
REPS=2
CPU=12
WALL=16
MEM=2147483648
SAT=old.SAT
ALLOWED=old.ALLOWED
BASE_SEED=202611022100
WIDTH=5
MIN_EQUATIONS=4
MIN_COVER=0.70
MAX_CLAUSES=30000
MAX_LITERALS=140000
MAX_SUPPORTS=30000

def digest(raw):return sha256(raw).hexdigest()

def frozen():
    blob=subprocess.run(["git","hash-object",str(PREREG)],check=True,
        capture_output=True,text=True).stdout.strip()
    if blob!=PREREG_BLOB:raise AssertionError("E12B pre-registered immutable protocol SHA drift")
    p=json.loads(PREREG.read_text())
    b=p["original_cross_family_tests"];c=p["candidate"]
    if (tuple(x["id"] for x in p["original_source_configs"])!=IDS
        or tuple(p["variants"])!=VARIANTS or tuple(p["arms"])!=ARMS
        or tuple(b["OS"])!=HOSTS
        or (b["VM_jobs"],b["parallel_limit"],b["planned_cold_subprocesses"],
            b["per_variant_arm_repeats"])!=(20,8,600,REPS)
        or (b["CPU_soft_s"],b["WALL_s"],b["RLIMIT_AS_bytes"])!=(CPU,WALL,MEM)
        or (c["support_width"],c["min_certified_original_clause_fraction"],
            c["min_certified_XOR_equations"])!=(WIDTH,MIN_COVER,MIN_EQUATIONS)
        or (c["max_source_clauses"],c["max_source_literal_occurrences"],
            c["max_distinct_supports"])!=(MAX_CLAUSES,MAX_LITERALS,MAX_SUPPORTS)
        or b["true_new_independent_external_sources"]!=0
        or p["gates"]["004F"]!="NOT_READY"):
        raise AssertionError("Original frozen E12B sources, thresholds or workload disagree")
    return p

def source(case):
    if case not in IDS:raise AssertionError("Unknown source")
    item=frozen()["original_source_configs"][IDS.index(case)]
    size=item["size"];family=item["family"]
    rng=random.Random(item["seed"])
    if family=="mixedxor":
        rows,n,model=planted_mixed({"n":size,"seed":item["seed"],
          "xor3_equations":item["xor3_equations"],"added_3cnf":item["added_3cnf"],
          "expected_m":item["expected_m"]})
    elif family=="exactone":
        tasks=size;k=5;n=tasks*k
        slots=[rng.randrange(k) for _ in range(tasks)]
        for i in range(1,tasks):
            if slots[i]==slots[i-1]:
                slots[i]=(slots[i]+1+rng.randrange(k-1))%k
        rows=[]
        for task in range(tasks):
            vs=[k*task+j+1 for j in range(k)]
            rows.append(vs)
            for a,b in itertools.combinations(vs,2):
                rows.append([-a,-b])
        for task in range(tasks-1):
            for j in range(k):
                rows.append([-(k*task+j+1),-(k*(task+1)+j+1)])
        model=[(k*task+j+1) if slots[task]==j else -(k*task+j+1)
               for task in range(tasks) for j in range(k)]
    else:
        n=size if family=="circulant" else size*size
        values={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
        model=[i if values[i] else -i for i in range(1,n+1)]
        supports=[]
        if family=="circulant":
            offsets=item["offsets"]
            for b in range(n):
                supports.append(tuple(sorted(1+(b+d)%n for d in offsets)))
        else:
            for r in range(size):
                for c in range(size):
                    if family=="torus":
                        loc=[(r,c),(r,(c+1)%size),(r,(c-1)%size),
                             ((r+1)%size,c),((r-1)%size,c)]
                    elif family=="diagonal":
                        loc=[(r,c),(r,(c+1)%size),((r+1)%size,c),
                             ((r+1)%size,(c+1)%size)]
                    else:raise AssertionError("Unknown generator family")
                    supports.append(tuple(sorted(1+x*size+y for x,y in loc)))
        if len(supports)!=n or len(set(supports))!=n:
            raise AssertionError("Original source parity graph supports collapsed")
        blocks=[]
        for support in supports:
            if len(support) not in (4,5) or len(set(support))!=len(support):
                raise AssertionError("Original source parity width invalid")
            rhs=sum(int(values[v]) for v in support)%2
            block=[]
            for bits in itertools.product((0,1),repeat=len(support)):
                if sum(bits)%2==rhs:continue
                block.append([v if bit==0 else -v
                   for v,bit in zip(support,bits)])
            if len(block)!=2**(len(support)-1):
                raise AssertionError("Source XOR mask set incomplete")
            rng.shuffle(block);blocks.append(block)
        rng.shuffle(blocks)
        rows=[clause for block in blocks for clause in block]
    if not old.all_model_ok(rows,n,model):
        raise AssertionError("Generated E12B original complete planted SAT model invalid")
    data=old.original_cnf(n,rows)
    return {"case":case,"family":family,"n":n,"m":len(rows),"rows":rows,
        "model":model,"model_sha":digest(json.dumps(model).encode()),
        "bytes":data,"sha":digest(data),"source_kind":"INTERNAL_NEW_SEED_NOT_EXTERNAL"}

def signature(rows):
    return Counter(tuple(sorted(row)) for row in rows)

def variant(case,variant_name):
    if variant_name not in VARIANTS:raise AssertionError("Unregistered source permutation")
    base=source(case)
    rng=random.Random(frozen()["original_source_configs"][IDS.index(case)]["seed"]
                      +100003*VARIANTS.index(variant_name))
    rows=[list(row) for row in base["rows"]]
    if variant_name=="global_clause_literal_shuffle":
        for row in rows:rng.shuffle(row)
        rng.shuffle(rows)
    elif variant_name=="round_robin_support_literal_shuffle":
        groups=defaultdict(list)
        for row in rows:groups[tuple(sorted(abs(v) for v in row))].append(row)
        supports=sorted(groups)
        rng.shuffle(supports)
        for support in supports:
            rng.shuffle(groups[support])
            for row in groups[support]:rng.shuffle(row)
        rows=[groups[key][layer]
              for layer in range(max(len(group) for group in groups.values()))
              for key in supports if layer<len(groups[key])]
    if signature(rows)!=signature(base["rows"]):
        raise AssertionError("Permutation changed exact original CNF clause multiset")
    if not old.all_model_ok(rows,base["n"],base["model"]):
        raise AssertionError("Complete SAT original model changed under source permutation")
    content=base["bytes"] if variant_name=="as_emitted" else old.original_cnf(base["n"],rows)
    return {**base,"rows":rows,"bytes":content,"sha":digest(content),
        "base_sha":base["sha"],"variant":variant_name}

def certified_support_index(rows,n):
    """Order-invariant complete parity from exact original masks; no guessed XOR.

    Scan all original clauses exactly once; use only fully source-matched 5-var
    supports with all 16 distinct forbidden masks of ONE parity. Each original
    index allocated at most once; duplicates/noncertified rows remain CNF.
    """
    if type(n)!=int or n<1 or len(rows)>MAX_CLAUSES:
        raise AssertionError("Source dimension or clause cap exceeded")
    groups=defaultdict(dict)
    literal_total=0
    for index,row in enumerate(rows):
        if not isinstance(row,(tuple,list)):raise AssertionError("Non-source clause")
        literal_total+=len(row)
        if literal_total>MAX_LITERALS:raise AssertionError("Source literal cap exceeded")
        if any(type(v)!=int or v==0 or abs(v)>n for v in row):
            raise AssertionError("Source contains illegal literal")
        if len(row)!=WIDTH or len({abs(v) for v in row})!=WIDTH:
            continue # must keep malformed/repeated-mask original in residual CNF
        key=tuple(sorted(abs(v) for v in row))
        if key not in groups and len(groups)>=MAX_SUPPORTS:
            raise AssertionError("Too many absolute variable supports")
        ordered={abs(v):v<0 for v in row}
        mask=tuple(int(ordered[v]) for v in key)
        # Exact duplicate signed OR clauses remain as original residual.
        groups[key].setdefault(mask,index)
    selected=[];used=set()
    for key,masked in sorted(groups.items()):
        if len(masked)!=1<<(WIDTH-1):continue
        parities={sum(mask)%2 for mask in masked}
        if len(parities)!=1:continue
        forbidden_parity=next(iter(parities))
        canonical={tuple(bits) for bits in itertools.product((0,1),repeat=WIDTH)
                 if sum(bits)%2==forbidden_parity}
        if set(masked)!=canonical:
            raise AssertionError("Mask completeness counterexample: never remove original clauses")
        rhs=1-forbidden_parity
        source_indices=[masked[mask] for mask in sorted(masked)]
        if any(i in used for i in source_indices):
            raise AssertionError("Original clause reused for different parity certificate")
        used.update(source_indices)
        selected.append({"variables":list(key),"rhs":rhs,
           "original_clause_indices":source_indices,
           "certificate":"FULL_EXACT_SIGN_MASKS_ONE_PARITY_REPLAYED",
           "forbidden_masks_count":len(source_indices)})
    return {"equations":selected,"source_clause_indices":used,
        "source_complete_equation_count":len(selected),
        "original_clause_coverage":len(used)/len(rows) if rows else 0.,
        "scan_original_rows":len(rows),"scanned_literals":literal_total}

def policy(rows,n,arm):
    if arm not in ARMS:raise AssertionError("Unknown unregistered candidate")
    if arm=="e12b_support_index":
        try:scan=certified_support_index(rows,n)
        except (AssertionError,MemoryError) as ex:
            return {"equations":[],"cnf_clauses":rows,"choice":"E12B_FAIL_CLOSED_RAW",
                    "decision":{"choice":"RAW","reason":"SOURCE_SCAN_BOUND_OR_MALFORMED","detail":str(ex)}}
        allow=(scan["source_complete_equation_count"]>=MIN_EQUATIONS
               and scan["original_clause_coverage"]>=MIN_COVER)
        if allow:
            used=scan["source_clause_indices"]
            clauses=[row for i,row in enumerate(rows) if i not in used]
            if len(clauses)+16*len(scan["equations"])!=len(rows):
                raise AssertionError("Source partition accounting inconsistent")
            return {"equations":scan["equations"],"cnf_clauses":clauses,
                "choice":"E12B_CERTIFIED_NATIVE","decision":{"choice":"XOR",
                   "proved_XOR_equations":len(scan["equations"]),
                   "source_coverage":scan["original_clause_coverage"]}}
        return {"equations":[],"cnf_clauses":rows,"choice":"E12B_INDEXED_RAW",
            "decision":{"choice":"RAW","proved_XOR_equations":len(scan["equations"]),
                "source_coverage":scan["original_clause_coverage"]}}
    if arm=="unaltered_e11_prefix":
        o=old.policy(rows,n,"e11_prefix_certified",old.frozen_e9_model())
        return {**o,"decision":{"choice":"XOR" if o["choice"]=="native_xor" else "RAW"}}
    if arm=="native_all":return normalized_selector(rows,n,"native_all")
    if arm=="raw_cms":return normalized_selector(rows,n,"raw_cms")
    return {"equations":[],"cnf_clauses":rows,"choice":"cadical195_original"}

def preflight(folder):
    p=frozen();old.frozen_e9_model()
    locked={}
    for case in IDS:
        locked[case]={}
        choices=set()
        for name in VARIANTS:
            s=variant(case,name)
            decision=policy(s["rows"],s["n"],"e12b_support_index")
            choice=decision["decision"]["choice"]
            choices.add(choice)
            locked[case][name]={
                "original_source_SHA256":s["base_sha"],
                "transformed_original_CNF_SHA256":s["sha"],
                "complete_original_SAT_model_SHA256":s["model_sha"],
                "n":s["n"],"m":s["m"],"family":s["family"],
                "frozen_candidate_decision":choice,
                "original_clause_multiset_exact":True}
        if len(choices)!=1:
            raise AssertionError("NEW 004E12B source-order invariant candidate failed before workers")
    result={"schema":"JANUS-TIME-SAT-004E12B-PREWORKER-10-CNF-30-VARIANT-SHA-LOCK-V1",
      "frozen_prereg_Git_blob":PREREG_BLOB,
      "original_E9_model_SHA256":MODEL_SHA,
      "sources":locked,"original_CNF_count":len(IDS),"variant_originals":len(IDS)*3,
      "no_independent_external_source":True,
      "no_production":True}
    folder.mkdir(parents=True,exist_ok=True)
    data=json.dumps(result,sort_keys=True,indent=2)+"\n"
    (folder/"SOURCE_LOCK.json").write_text(data)
    (folder/"SOURCE_LOCK.sha256").write_text(digest(data.encode())+"  SOURCE_LOCK.json\n")
    print("E12B_FROZEN_SOURCE_ORDER_INVARIANCE_PASS",json.dumps({
        "original_sources":len(IDS),"variant_originals":len(IDS)*3,
        "choices":{case:locked[case]["as_emitted"]["frozen_candidate_decision"] for case in IDS},
        "lock_SHA256":digest(data.encode())},sort_keys=True))
    return result

def checked_lock(path):
    data=path.read_bytes();hashline=path.with_name("SOURCE_LOCK.sha256").read_text().strip()
    if hashline!=digest(data)+"  SOURCE_LOCK.json":
        raise AssertionError("E12B pre-worker source/model lock tampered")
    lock=json.loads(data)
    if (lock.get("schema")!="JANUS-TIME-SAT-004E12B-PREWORKER-10-CNF-30-VARIANT-SHA-LOCK-V1"
        or lock.get("frozen_prereg_Git_blob")!=PREREG_BLOB
        or lock.get("original_E9_model_SHA256")!=MODEL_SHA
        or set(lock.get("sources",{}))!=set(IDS)
        or lock.get("no_independent_external_source") is not True):
        raise AssertionError("Not original frozen E12B source lock")
    return lock,digest(data)

def child(case,variant_name,arm,lock_path,expect):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    began=perf_counter()
    lock,locksha=checked_lock(lock_path)
    src=variant(case,variant_name)
    pre=lock["sources"][case][variant_name]
    if ((src["sha"],src["base_sha"],src["model_sha"],src["n"],src["m"])!=
        (pre["transformed_original_CNF_SHA256"],pre["original_source_SHA256"],
         pre["complete_original_SAT_model_SHA256"],pre["n"],pre["m"])
        or expect!=src["sha"]):
        raise AssertionError("Frozen original source/model SHA changed after preflight")
    with TemporaryDirectory() as t:
        path=Path(t)/"original_transformed.cnf"
        path.write_bytes(src["bytes"])
        scanned=old.scan_dimacs(path)
        if (scanned["n_variables"],scanned["n_clauses"],
             scanned["n_literal_occurrences"])!=(
             src["n"],src["m"],sum(map(len,src["rows"]))):
            raise AssertionError("Original transformed DIMACS shape/source mismatch")
        rows=old.read_cnf(path,src["n"],src["m"],max_literals=200000)
    if rows!=src["rows"] or not old.all_model_ok(rows,src["n"],src["model"]):
        raise AssertionError("Original transformed full SAT assignment invalid")
    begin=perf_counter()
    picked=policy(rows,src["n"],arm)
    analysis_s=perf_counter()-begin
    if arm=="e12b_support_index" and picked["decision"]["choice"]!=pre["frozen_candidate_decision"]:
        raise AssertionError("Candidate decision diverged from preworker lock")
    if arm=="cadical195_original":
        from pysat.solvers import Solver
        with Solver(name="cadical195",bootstrap_with=rows) as slv:
            stamp=perf_counter();sat=slv.solve();solver_s=perf_counter()-stamp
            found=slv.get_model() if sat is True else None
    else:
        import pycryptosat
        slv=pycryptosat.Solver(threads=1)
        for eq in picked["equations"]:slv.add_xor_clause(eq["variables"],bool(eq["rhs"]))
        for clause in picked["cnf_clauses"]:slv.add_clause(clause)
        stamp=perf_counter();sat,ans=slv.solve();solver_s=perf_counter()-stamp
        found=([i if bool(ans[i]) else -i for i in range(1,src["n"]+1)]
                if sat is True and ans is not None and len(ans)>src["n"] else None)
    if sat is False:raise AssertionError("UNSAT impossible on complete-model-verified original SAT")
    if sat is True:
        if found is None or not old.original_model_replay(rows,src["n"],found):
            raise AssertionError("Returned SAT model violates original exact variant CNF")
        status=SAT
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {"status":status,"case":case,"variant":variant_name,"arm":arm,
        "original_source_SHA256":src["base_sha"],
        "transformed_original_CNF_SHA256":src["sha"],
        "complete_model_SHA256":src["model_sha"],
        "preworker_source_lock_SHA256":locksha,
        "predecision":picked.get("decision",{}),
        "selected_source_exact_XOR_count":len(picked["equations"]),
        "effective_representation":picked["choice"],
        "full_source_analysis_wall_s":analysis_s,"solver_wall_s":solver_s,
        "full_cold_inner_wall_s":perf_counter()-began,
        "full_cold_CPU_s":process_time(),
        "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "original_complete_SAT_model_replay":"PASS",
        "external_independent_custodian":False,
        "production_C023_main":"UNCHANGED"}

def matrix(case,lockpath,out):
    frozen();lock,locksha=checked_lock(lockpath)
    receipts=[]
    for name in VARIANTS:
        source_name=variant(case,name)
        assert source_name["sha"]==lock["sources"][case][name]["transformed_original_CNF_SHA256"]
        for rep in range(REPS):
            order=list(ARMS)
            random.Random(BASE_SEED+101*IDS.index(case)+79*VARIANTS.index(name)+rep).shuffle(order)
            for arm in order:
                began=perf_counter()
                cmd=[sys.executable,str(Path(__file__).resolve()),"--child","--case",case,
                    "--variant",name,"--arm",arm,"--source-lock",str(lockpath),
                    "--expected-sha",source_name["sha"]]
                try:
                    p=subprocess.run(cmd,text=True,capture_output=True,check=False,timeout=WALL)
                    if p.returncode:
                        outcome=old.classify_nonzero_exit(p.returncode)
                        outcome["status"]=outcome.get("verdict","UNSUPPORTED_FAIL")
                        outcome["exit_code"]=p.returncode
                        outcome["stderr_tail"]=p.stderr[-700:]
                    else:outcome=json.loads(p.stdout)
                except subprocess.TimeoutExpired:
                    outcome={"status":"UNKNOWN_WALL_TIMEOUT"}
                receipts.append({"variant":name,"repeat":rep,"arm":arm,
                    "randomized_arm_order":order,
                    "full_cold_child_wall_s":perf_counter()-began,"outcome":outcome})
                print("E12B_CHILD",case,name,rep,arm,outcome.get("status"),
                      round(receipts[-1]["full_cold_child_wall_s"],4),flush=True)
    if len(receipts)!=30 or any(x["outcome"].get("status") not in ALLOWED for x in receipts):
        raise AssertionError("Missing children or unexpected SAT failure")
    for r in receipts:
        o=r["outcome"]
        if o["status"]==SAT and (o["preworker_source_lock_SHA256"]!=locksha
              or o["original_complete_SAT_model_replay"]!="PASS"):
            raise AssertionError("SAT evidence not bound to preworker complete model")
    result={"schema":"JANUS-TIME-SAT-004E12B-30-FROZEN-COLD-COST-ORIGINAL-VM-V1",
        "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "original_HEAD":os.getenv("GITHUB_SHA","LOCAL"),
        "original_runner_name":os.getenv("RUNNER_NAME","LOCAL"),
        "original_os":os.getenv("E12B_OS","LOCAL"),
        "case":case,"family":source(case)["family"],
        "original_source_SHA256":source(case)["sha"],
        "full_model_SHA256":source(case)["model_sha"],
        "preworker_lock_SHA256":locksha,
        "prereg_git_blob":PREREG_BLOB,
        "repeats":2,"variants":3,"arms":5,"cold_children":30,
        "CPU":CPU,"WALL":WALL,"MEM":MEM,"external_independent_sources":0,
        "production_main":"UNCHANGED",
        "records":receipts}
    out.mkdir(parents=True,exist_ok=True)
    (out/(case+"__"+os.getenv("E12B_OS","LOCAL")+".json")).write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("E12B_WORKER_PASS",case,sum(x["outcome"]["status"]==SAT for x in receipts),flush=True)

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--preflight",action="store_true")
    cli.add_argument("--child",action="store_true")
    cli.add_argument("--case",choices=IDS)
    cli.add_argument("--variant",choices=VARIANTS)
    cli.add_argument("--arm",choices=ARMS)
    cli.add_argument("--source-lock",type=Path)
    cli.add_argument("--expected-sha",default="")
    cli.add_argument("--out",type=Path)
    x=cli.parse_args()
    if x.preflight:
        if x.out is None:raise SystemExit("--out needed")
        preflight(x.out)
    elif x.child:
        if None in (x.case,x.variant,x.arm) or x.source_lock is None:
            raise SystemExit("--case/--variant/--arm/--source-lock required")
        frozen()
        print(json.dumps(child(x.case,x.variant,x.arm,x.source_lock,x.expected_sha),sort_keys=True))
    else:
        if x.case is None or x.source_lock is None or x.out is None:
            raise SystemExit("--case/--source-lock/--out needed")
        matrix(x.case,x.source_lock,x.out)
