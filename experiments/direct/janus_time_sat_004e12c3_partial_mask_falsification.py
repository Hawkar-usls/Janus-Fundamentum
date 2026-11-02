#!/usr/bin/env python3
"""E12C3 falsification: incomplete XOR sign-mask blocks, mixed CNF and variable isomorphism.

Research only; same developer controls all sources. Entire original SAT model
and exact original CNF SHA sealed before workers. Never claim external blind
validation. All non-certified original clauses, masks and duplicates retained.
"""
from __future__ import annotations
import argparse,itertools,json,os,random,resource,subprocess,sys
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter,process_time
import janus_time_sat_004e12c2_width6_no_probe as c2
import janus_time_sat_004e12c1_cost_aware as c1
import janus_time_sat_004e12b_support_index as b
from janus_time_sat_004e8_model_first import planted_clause

ROOT=Path("experiments/time_sat_004_external")
PLAN=ROOT/"PREREGISTERED_004E12C3_PARTIAL_MASKS_MIXED_ISOMORPHISM_20261102.json"
BLOB="b3c8c659952a5bd73212d3bcec17976d721be8c2"
HOSTS=("ubuntu-22.04","ubuntu-24.04")
IDS=("e12c3-hyper6-full-n112","e12c3-hyper6-full-n146",
     "e12c3-hyper6-partial-n112","e12c3-hyper6-partial-n146",
     "e12c3-hyper6-mixed-low-n128","e12c3-hyper6-mixed-high-n128",
     "e12c3-hyper6-full-diluted-n128","e12c3-planted3sat-n224")
VARIANTS=("as_emitted","global_clause_literal_shuffle",
          "round_robin_support_literal_shuffle","variable_renaming_polarity_flip")
ARMS=("e12c2_certified_width5_6_no_probe","e12b_frozen_width5",
      "native_all_width3_6","raw_cms","cadical195_original")
CPU=12;WALL=18;MEM=2147483648;REPS=2
SAT=c2.SAT
ALLOWED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}
def digest(data):return sha256(data).hexdigest()

def frozen():
    h=subprocess.run(["git","hash-object",str(PLAN)],capture_output=True,text=True,check=True).stdout.strip()
    if h!=BLOB:raise AssertionError("E12C3 preregistered original source specification changed")
    q=json.loads(PLAN.read_text());r=q["compute"]
    if (tuple(x["id"] for x in q["original_source_configs"])!=IDS
        or tuple(q["representations"])!=VARIANTS
        or tuple(q["frozen_arms"])!=ARMS
        or tuple(r["OS"])!=HOSTS
        or (r["VM_jobs"],r["max_parallel"],r["source_originals"],
            r["representations"],r["arms"],r["repeats"],r["planned_cold_children"])!=
           (16,6,8,4,5,2,640)
        or (r["CPU_soft_s"],r["WALL_s"],r["AS_bytes"])!=(CPU,WALL,MEM)
        or q["scientific_gates"]["independent_external_originals"]!=0
        or q["candidate_policy"]["read_frozen_C2_source_policy_directly"] is not True
        or q["main_C023"]!="UNCHANGED"):
        raise AssertionError("E12C3 original method/limits/source gates altered")
    return q

def config(case):
    if case not in IDS:raise AssertionError("Unregistered original SAT source")
    return frozen()["original_source_configs"][IDS.index(case)]

def original(case):
    q=config(case);rng=random.Random(q["seed"]);n=q["n"]
    truth={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
    model=[i if truth[i] else -i for i in range(1,n+1)]
    supports=set()
    if q["kind"]!="planted3sat":
        while len(supports)<q["equations"]:
            supports.add(tuple(sorted(rng.sample(range(1,n+1),6))))
    supports=sorted(supports)
    if len(supports)!=q["equations"]:raise AssertionError("Original support population mismatch")
    rows=[];complete_supports=set();partial_supports=set()
    for i,support in enumerate(supports):
        rhs=sum(int(truth[v]) for v in support)%2
        block=[[v if bit==0 else -v for v,bit in zip(support,bits)]
               for bits in itertools.product((0,1),repeat=6) if sum(bits)%2!=rhs]
        if len(block)!=32:raise AssertionError("Incorrect original full source parity mask count")
        rng.shuffle(block)
        if i>=q["full_equations"]:
            removed=set(rng.sample(range(len(block)),q["omit_per_partial"]))
            block=[row for j,row in enumerate(block) if j not in removed]
            partial_supports.add(support)
        else:
            complete_supports.add(support)
        rows.extend(block)
    if len(complete_supports)!=q["full_equations"]:
        raise AssertionError("Original source full-vs-partial split drift")
    seen={tuple(sorted(row)) for row in rows}
    left=q["guard_clauses"]
    for _ in range(left*40):
        if left==0:break
        clause=planted_clause(rng,n,truth)
        if clause is None or tuple(sorted(clause)) in seen:continue
        rows.append(list(clause));seen.add(tuple(sorted(clause)));left-=1
    if left:raise AssertionError("New planted 3SAT source guard budget unmet")
    # Original duplicates retained and not used as additional XOR equations.
    for _ in range(q["duplicate_clauses"]):
        if not rows:raise AssertionError("No original clause available for duplicate")
        rows.append(list(rows[rng.randrange(len(rows))]))
    rng.shuffle(rows)
    if len(rows)>30000 or sum(map(len,rows))>140000:
        raise AssertionError("Frozen source exceeds original C2 source safety caps")
    if not b.old.all_model_ok(rows,n,model):
        raise AssertionError("Original SHA-source planted SAT model doesn't satisfy CNF")
    payload=b.old.original_cnf(n,rows)
    return {"id":case,"family":q["kind"],"n":n,"m":len(rows),
      "rows":rows,"model":model,"model_sha":digest(json.dumps(model).encode()),
      "bytes":payload,"sha":digest(payload),
      "source_complete_supports":complete_supports,
      "source_partial_supports":partial_supports,
      "source_family_is_JANUS_internal":True}

def signature(rows):return Counter(tuple(sorted(r)) for r in rows)
def variant(case,name):
    if name not in VARIANTS:raise AssertionError("Unknown original source representation")
    s=original(case);q=config(case)
    rows=[list(z) for z in s["rows"]];model=list(s["model"])
    perm=None;flips=None
    rng=random.Random(q["seed"]+100003*VARIANTS.index(name))
    if name=="global_clause_literal_shuffle":
        for row in rows:rng.shuffle(row)
        rng.shuffle(rows)
    elif name=="round_robin_support_literal_shuffle":
        groups=defaultdict(list)
        for row in rows:groups[tuple(sorted(abs(x) for x in row))].append(row)
        keys=sorted(groups);rng.shuffle(keys)
        for k in keys:
            rng.shuffle(groups[k])
            for row in groups[k]:rng.shuffle(row)
        rows=[groups[k][z] for z in range(max(map(len,groups.values())))
              for k in keys if z<len(groups[k])]
    elif name=="variable_renaming_polarity_flip":
        dest=list(range(1,s["n"]+1));rng.shuffle(dest)
        perm={i+1:dest[i] for i in range(s["n"])}
        flips={i:bool(rng.getrandbits(1)) for i in range(1,s["n"]+1)}
        rows=[[ (1 if lit>0 else -1)*(-1 if flips[abs(lit)] else 1)*perm[abs(lit)]
                for lit in row] for row in rows]
        next_model=[None]*s["n"]
        for i,old_lit in enumerate(model,1):
            j=perm[i];positive=old_lit>0
            if flips[i]:positive=not positive
            next_model[j-1]=j if positive else -j
        if any(x is None for x in next_model):
            raise AssertionError("Original bijection did not map a complete SAT model")
        model=next_model
    if name!="variable_renaming_polarity_flip" and (
        signature(rows)!=signature(s["rows"]) or model!=s["model"]):
        raise AssertionError("Exact source clause-only permutation changed SAT original")
    if name=="variable_renaming_polarity_flip":
        expected=[[ (1 if lit>0 else -1)*(-1 if flips[abs(lit)] else 1)*perm[abs(lit)]
                    for lit in row] for row in s["rows"]]
        if signature(rows)!=signature(expected) or set(perm.values())!=set(range(1,s["n"]+1)):
            raise AssertionError("Source variable-polarity mapping not bijective")
    if not b.old.all_model_ok(rows,s["n"],model):
        raise AssertionError("Complete source SAT model fails after variable-polarity isomorphism")
    payload=s["bytes"] if name=="as_emitted" else b.old.original_cnf(s["n"],rows)
    return {**s,"rows":rows,"bytes":payload,"sha":digest(payload),
      "model":model,"model_sha":digest(json.dumps(model).encode()),
      "base_sha":s["sha"],"base_model_sha":s["model_sha"],
      "variant":name,"source_isomorphism":name=="variable_renaming_polarity_flip",
      "renaming":perm,"polarity_flips":flips}

def policy(rows,n,arm):
    if arm not in ARMS:raise AssertionError("Unregistered new scientific method")
    # Reuse C2 policy EXACTLY without retuning or posthoc changes.
    return c2.policy(rows,n,arm)

def preflight(out):
    frozen();locks={};seen=set()
    for case in IDS:
        ss=original(case)
        if ss["sha"] in seen:raise AssertionError("New original source duplicate SHA")
        seen.add(ss["sha"])
        locks[case]={};choices=set()
        for v in VARIANTS:
            trial=variant(case,v);dec=policy(trial["rows"],trial["n"],ARMS[0])["decision"]["choice"]
            choices.add(dec)
            # Independent source-only exact width6 certificate must use no partial support.
            idx=c1.source_index_all_widths(trial["rows"],trial["n"])
            detected=idx["counts"].get(6,0)
            if detected!=config(case)["full_equations"]:
                raise AssertionError("False-positive exact width6 source XOR on ablated mask")
            locks[case][v]={
                "base_original_CNF_SHA256":ss["sha"],
                "base_original_complete_model_SHA256":ss["model_sha"],
                "source_variant_CNF_SHA256":trial["sha"],
                "source_variant_complete_SAT_model_SHA256":trial["model_sha"],
                "isomorphism_not_clause_reorder":trial["source_isomorphism"],
                "n":trial["n"],"m":trial["m"],
                "frozen_C2_decision":dec,
                "proof_source_exact_full_width6_equations":detected,
                "original_partial_mask_blocks_no_XOR":len(ss["source_partial_supports"]),
                "all_complete_original_clause_model_replayed":True}
        if len(choices)!=1:raise AssertionError("C2 source decision differs under equivalent CNF or bijection")
    q={"schema":"JANUS-TIME-SAT-004E12C3-SOURCE-MODEL-LOCK-PREWORKER-V1",
       "prereg_Git_blob":BLOB,"sources":locks,
       "original_SAT_inputs":8,"source_variants":32,
       "independent_outside_ADMIN_SAT_sources":0,"main_C023":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    buf=(json.dumps(q,indent=2,sort_keys=True)+"\n").encode()
    (out/"SOURCE_LOCK.json").write_bytes(buf)
    (out/"SOURCE_LOCK.sha256").write_text(digest(buf)+"  SOURCE_LOCK.json\n")
    print("E12C3_PREWORKER_SOURCE_MODEL_AND_ABLATION_PROOF_PASS",json.dumps({
       "origins":8,"models":32,"source_lock_sha256":digest(buf),
       "decisions":{case:locks[case]["as_emitted"]["frozen_C2_decision"] for case in IDS}
       },sort_keys=True))
    return q

def checked_lock(path):
    buf=path.read_bytes()
    if path.with_name("SOURCE_LOCK.sha256").read_text().strip()!=digest(buf)+"  SOURCE_LOCK.json":
        raise AssertionError("Original frozen preworker lock SHA changed")
    data=json.loads(buf)
    if (data.get("schema")!="JANUS-TIME-SAT-004E12C3-SOURCE-MODEL-LOCK-PREWORKER-V1"
        or data.get("prereg_Git_blob")!=BLOB or set(data.get("sources",{}))!=set(IDS)
        or data.get("independent_outside_ADMIN_SAT_sources")!=0
        or data.get("main_C023")!="UNCHANGED"):
        raise AssertionError("Unregistered source or preworker lock")
    return data,digest(buf)

def child(case,v,arm,lockpath,expected):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    stamp=perf_counter()
    lock,locksha=checked_lock(lockpath)
    s=variant(case,v);pin=lock["sources"][case][v]
    if ((s["base_sha"],s["base_model_sha"],s["sha"],s["model_sha"],s["n"],s["m"])!=(
            pin["base_original_CNF_SHA256"],pin["base_original_complete_model_SHA256"],
            pin["source_variant_CNF_SHA256"],pin["source_variant_complete_SAT_model_SHA256"],
            pin["n"],pin["m"]) or expected!=s["sha"]):
        raise AssertionError("Original CNF SHA or complete SAT model SHA mutated after preworker lock")
    with TemporaryDirectory() as temp:
        f=Path(temp)/"source.cnf";f.write_bytes(s["bytes"])
        shape=b.old.scan_dimacs(f)
        if (shape["n_variables"],shape["n_clauses"],shape["n_literal_occurrences"])!=(
            s["n"],s["m"],sum(map(len,s["rows"]))):
            raise AssertionError("Original exact DIMACS dimensions changed")
        rows=b.old.read_cnf(f,s["n"],s["m"],max_literals=200000)
    if rows!=s["rows"] or not b.old.all_model_ok(rows,s["n"],s["model"]):
        raise AssertionError("Full original SAT model fails after original DIMACS re-read")
    t=perf_counter();selected=policy(rows,s["n"],arm)
    index_wall_s=perf_counter()-t
    if arm==ARMS[0] and selected["decision"]["choice"]!=pin["frozen_C2_decision"]:
        raise AssertionError("C2 candidate decision flipped after preworker source lock")
    if selected["equations"]:
        indexed=c1.source_index_all_widths(rows,s["n"])
        certified={(tuple(eq["variables"]),eq["rhs"]) for eq in indexed["equations"]}
        if any((tuple(eq["variables"]),eq["rhs"]) not in certified for eq in selected["equations"]):
            raise AssertionError("Unproved partial XOR source mask passed to native solver")
    solved,assignment,solver_s=c1.run_solver(rows,s["n"],selected,arm)
    status=SAT if solved is True else "UNKNOWN_SOLVER_NO_ANSWER"
    if status==SAT and not b.old.original_model_replay(rows,s["n"],assignment):
        raise AssertionError("False SAT model for full original source")
    return {"status":status,"case":case,"variant":v,"arm":arm,
       "base_original_CNF_SHA256":s["base_sha"],
       "variant_original_CNF_SHA256":s["sha"],
       "base_original_full_SAT_model_SHA256":s["base_model_sha"],
       "variant_original_full_SAT_model_SHA256":s["model_sha"],
       "preworker_source_lock_SHA256":locksha,
       "source_exact_width6_equations_proven":pin["proof_source_exact_full_width6_equations"],
       "source_partial_masks_not_misclassified":True,
       "candidate_decision":selected["decision"]["choice"],
       "selected_source_certified_equations":len(selected["equations"]),
       "index_wall_s":index_wall_s,"native_solver_wall_s":solver_s,
       "inner_full_cold_wall_s":perf_counter()-stamp,
       "inner_cpu_s":process_time(),
       "RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       "full_original_CNF_complete_model_replay":"PASS" if status==SAT else "UNKNOWN",
       "outside_admin_SAT_source":False,"production_C023_main":"UNCHANGED"}

def matrix(case,lockpath,out):
    frozen();l,locksha=checked_lock(lockpath)
    if case not in IDS:raise AssertionError("Unregistered matrix source")
    receipts=[]
    for v in VARIANTS:
        s=variant(case,v)
        if s["sha"]!=l["sources"][case][v]["source_variant_CNF_SHA256"]:
            raise AssertionError("Matrix tried an unfrozen source CNF variant")
        for rep in range(REPS):
            arms=list(ARMS)
            random.Random(202611027300+101*IDS.index(case)+71*VARIANTS.index(v)+rep).shuffle(arms)
            for arm in arms:
                stamp=perf_counter()
                cmd=[sys.executable,str(Path(__file__).resolve()),"--child",
                     "--case",case,"--variant",v,"--arm",arm,
                     "--source-lock",str(lockpath),"--expected-sha",s["sha"]]
                try:
                    run=subprocess.run(cmd,text=True,capture_output=True,check=False,timeout=WALL)
                    if run.returncode:
                        outcome=b.old.classify_nonzero_exit(run.returncode)
                        outcome["status"]=outcome.get("verdict","UNSUPPORTED_FAIL")
                        outcome["returncode"]=run.returncode
                        outcome["stderr_tail"]=run.stderr[-700:]
                    else:outcome=json.loads(run.stdout)
                except subprocess.TimeoutExpired:
                    outcome={"status":"UNKNOWN_WALL_TIMEOUT"}
                receipts.append({"variant":v,"repeat":rep,"arm":arm,
                    "randomized_arm_order":arms,
                    "full_cold_child_wall_s":perf_counter()-stamp,
                    "outcome":outcome})
                print("E12C3_ORIGINAL_CHILD",case,v,rep,arm,
                      outcome["status"],round(receipts[-1]["full_cold_child_wall_s"],4),flush=True)
    if len(receipts)!=40 or any(x["outcome"].get("status") not in ALLOWED for x in receipts):
        raise AssertionError("Missing child or unsupported termination: original 40 source trials")
    out.mkdir(parents=True,exist_ok=True)
    original_src=original(case)
    j={"schema":"JANUS-TIME-SAT-004E12C3-40-ORIGINAL-SOURCE-FROZEN-COLD-VM-V1",
      "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
      "original_HEAD":os.getenv("GITHUB_SHA","LOCAL"),
      "original_runner_name":os.getenv("RUNNER_NAME","LOCAL"),
      "original_os":os.getenv("E12C3_OS","LOCAL"),
      "case":case,"family":config(case)["kind"],
      "original_CNF_SHA256":original_src["sha"],
      "original_complete_model_SHA256":original_src["model_sha"],
      "preworker_source_lock_SHA256":locksha,"prereg_Git_blob":BLOB,
      "cold_children":40,"CPU":CPU,"WALL":WALL,"MEM":MEM,
      "independent_external_sources":0,"C023_main":"UNCHANGED",
      "records":receipts}
    (out/(case+"__"+os.getenv("E12C3_OS","LOCAL")+".json")).write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    print("E12C3_ORIGINAL_WORKER_40_SOURCE_MODEL_RESULTS_PASS",case)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--child",action="store_true")
    p.add_argument("--case",choices=IDS)
    p.add_argument("--variant",choices=VARIANTS)
    p.add_argument("--arm",choices=ARMS)
    p.add_argument("--source-lock",type=Path)
    p.add_argument("--expected-sha",default="")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.preflight:preflight(a.out)
    elif a.child:print(json.dumps(child(a.case,a.variant,a.arm,a.source_lock,a.expected_sha),sort_keys=True))
    else:matrix(a.case,a.source_lock,a.out)
