#!/usr/bin/env python3
"""JUXTAPOSE R5: learn only from proof checks already required to solve tasks.

No transformer, no Markov transition model, no extra training proof probes for
the passive arms. 45 naturally solved original training SAT CNFs per seed,
then 30 new SHA-frozen original OOD CNFs. Source-bound exact resolution DAG +
independent replay + independent UP/XOR coefficient-rank reference.

A model scores PROPOSALS only. Never use a predicted XOR as a valid theorem.
This is internal synthetic research, not full SAT solver wall timing or
independent laboratory validation.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import argparse,json,math,random,subprocess,sys
from pathlib import Path
from time import perf_counter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as exact
import janus_juxtapose_r5_new_sources as fresh
from janus_juxtapose_markov_r4_benchmark import source_context,verified_pivot

PROTOCOL=HERE/"JUXTAPOSE_R5_PASSIVE_LEARNING_PROTOCOL_20261115.json"
PROTOCOL_BLOB="ead8ea24e34c76315c2eaaf03af88b80bc8554ec"
MANIFEST=HERE/"JUXTAPOSE_R5_NEW_ORIGINAL_SHA_MANIFEST_20261115.json"
MANIFEST_BLOB="ced5af3ff248b3b24db3dead72ee4aa947d4a750"
SEEDS=(2026111591,2026111592,2026111593,2026111594)
TRAIN=45
HOLDOUT=30
ARMS=("PASSIVE_COST_AWARE","PASSIVE_JUXTAPOSE_HISTORY",
      "ACTIVE_TWO_LABELS_REFERENCE","COST_GEOMETRY_NO_MEMORY",
      "STATIC_NUMERIC","SEEDED_RANDOM")
TRAINABLE=("PASSIVE_COST_AWARE","PASSIVE_JUXTAPOSE_HISTORY",
           "ACTIVE_TWO_LABELS_REFERENCE")
SCHEMA="JANUS-JUXTAPOSE-R5-ON-POLICY-ZERO-EXTRA-LABEL-TRAINED-V1"

def blob(path):
    return subprocess.run(["git","hash-object",str(path)],text=True,
                          check=True,capture_output=True).stdout.strip()

def frozen():
    if blob(PROTOCOL)!=PROTOCOL_BLOB or blob(MANIFEST)!=MANIFEST_BLOB:
        raise AssertionError("PRECOMMITTED_R5_PROTOCOL_OR_ORIGINAL_SHA_CHANGED")
    p=json.loads(PROTOCOL.read_text())
    m=json.loads(MANIFEST.read_text())
    if (p["schema"]!="JANUS-JUXTAPOSE-R5-PASSIVE-NO-EXTRA-PROOFS-FROZEN-V1"
        or p["preregistered_seeds"]!=list(SEEDS)
        or p["training_cases_per_seed"]!=TRAIN
        or p["test_cases_per_seed"]!=HOLDOUT
        or p["test_variables"]!=16
        or p["algorithms"]!=list(ARMS)):
        raise AssertionError("PREDECLARED_R5_METRICS_OR_ALGORITHMS_DRIFT")
    if m!=fresh.manifest() or m["original_source_count"]!=120:
        raise AssertionError("ORIGINAL_CNF_SHA_MANIFEST_MISMATCH")
    return {(x["seed"],x["slot"]):x for x in m["items"]}

def trained_score(f,history):
    key=exact.model_key(f)
    positives,n=history.get(key,(0,0))
    return (positives+1)/(n+2)

def choose_next(arm,pending,features,history):
    if arm=="STATIC_NUMERIC":
        return min(pending)
    if arm=="PASSIVE_JUXTAPOSE_HISTORY" or arm=="ACTIVE_TWO_LABELS_REFERENCE":
        return max(pending,key=lambda p:exact.trained_rank(features[p-1],history))
    if arm=="COST_GEOMETRY_NO_MEMORY":
        return max(pending,key=lambda p:(int(features[p-1]["eligible"]),
                                        -features[p-1]["pair_work"],
                                        features[p-1]["priority"]))
    if arm=="PASSIVE_COST_AWARE":
        def score(p):
            f=features[p-1]
            hits,n=history.get(exact.model_key(f),(0,0))
            historical=(hits+1)/(n+4)
            confidence=n/(n+4)
            predictor=confidence*historical+(1-confidence)*0.25
            return (int(f["eligible"]),
                    int(round(predictor*1_000_000/math.sqrt(1+f["pair_work"]))),
                    f["priority"])
        return max(pending,key=score)
    raise AssertionError("unsupported candidate policy")

class State:
    def __init__(self,arm):
        self.arm=arm
        self.history={}
        self.records=[]
        self.train_probes=0
        self.extra_training_probes=0
        self.train_pairwork=0
        self.test_probes=0
        self.test_pairwork=0
        self.train_seconds=0.0
        self.test_seconds=0.0
        self.train_positive=0
        self.test_positive=0
        self.training_sha=[]
        self.test_sha=[]
    def checkpoint(self):
        m={
            "schema":"JANUS-JUXTAPOSE-R5-PAST-ONLY-VERIFIED-PIVOT-MEMORY-V1",
            "algorithm":self.arm,
            "source_sha_training":self.training_sha,
            "memory":[{"features":k,"positives":v[0],"verified_total":v[1]}
                      for k,v in sorted(self.history.items())],
            "no_holdout_learning":True,
            "positive_labels_only_from_exact_original_source_resolution":True,
            "no_transformer_or_markov":True,
            "promotion_authority":False,
        }
        d=sha256(json.dumps(m,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        return m,d

def solve_source(state,seed,index,phase,source,context):
    n,rows=source["n"],source["rows"]
    known,up,features=context
    start=perf_counter()
    # Candidate ordering can depend ONLY on source features and previously
    # learned results. It cannot peek at any current exact proof.
    history=state.history
    available=set(range(1,n+1))
    observed={}
    steps=[]
    random_order=list(range(1,n+1))
    random.Random(seed^(index*9941+281)).shuffle(random_order)
    while available:
        pivot=(random_order[len(steps)] if state.arm=="SEEDED_RANDOM"
               else choose_next(state.arm,available,features,history))
        available.remove(pivot)
        outcome=verified_pivot(rows,n,pivot,known,up)
        observed[pivot]=outcome
        steps.append({"pivot":pivot,"proof":outcome["status"],
                      "rank_over_UP":outcome["rank_delta_over_UP"],
                      "pairs":outcome["pair_work"]})
        if outcome["rank_delta_over_UP"]>0:
            if outcome["status"]!="EXACT_SOURCE_PROOF_REPLAY_PASS":
                raise AssertionError("UNVERIFIED_POSITIVE_RANK")
            break
    normal_elapsed=perf_counter()-start
    extra=[]
    extra_elapsed=0.0
    if phase=="TRAIN" and state.arm=="ACTIVE_TWO_LABELS_REFERENCE":
        # Historical R4 two-label training design: select two source-feature
        # pivots, but here charge only unique extra proofs beyond the natural
        # task search. Never let current labels determine source scoring.
        choices=sorted(range(1,n+1),
                       key=lambda p:exact.trained_rank(features[p-1],history),
                       reverse=True)
        target1=choices[0]
        eligible=[p for p in range(1,n+1) if p!=target1]
        target2=eligible[random.Random(seed+index*4001).randrange(len(eligible))]
        t=perf_counter()
        for pivot in (target1,target2):
            if pivot not in observed:
                out=verified_pivot(rows,n,pivot,known,up)
                observed[pivot]=out
                extra.append({"pivot":pivot,"status":out["status"],
                              "rank_over_UP":out["rank_delta_over_UP"],
                              "pairs":out["pair_work"]})
        extra_elapsed=perf_counter()-t
    natural_probes=len(steps)
    natural_pairs=sum(x["pairs"] for x in steps)
    extra_probes=len(extra)
    extra_pairs=sum(x["pairs"] for x in extra)
    if phase=="TRAIN":
        state.train_probes+=natural_probes+extra_probes
        state.extra_training_probes+=extra_probes
        state.train_pairwork+=natural_pairs+extra_pairs
        state.train_seconds+=normal_elapsed+extra_elapsed
        state.train_positive+=int(any(x["rank_over_UP"]>0 for x in steps))
        # Delayed training: this source's observed exact result can influence
        # NEXT source only, never change candidate ranking mid-solve.
        if state.arm in TRAINABLE:
            for pivot,out in observed.items():
                if out["status"]!="EXACT_SOURCE_PROOF_REPLAY_PASS":
                    continue # Unsupported/abstaining is UNKNOWN, not negative.
                key=exact.model_key(features[pivot-1])
                h,total=state.history.get(key,(0,0))
                state.history[key]=(h+int(out["rank_delta_over_UP"]>0),total+1)
        state.training_sha.append(source["source_logical_sha256"])
    else:
        state.test_probes+=natural_probes
        state.test_pairwork+=natural_pairs
        state.test_seconds+=normal_elapsed
        state.test_positive+=int(any(x["rank_over_UP"]>0 for x in steps))
        state.test_sha.append(source["source_logical_sha256"])
    evidence={
        "phase":phase,"seed":seed,"slot_or_training_index":index,
        "original_source_sha256":source["source_logical_sha256"],
        "family_REPORT_ONLY":source["family"],
        "original_CNF_model_exactly_verified":True,
        "first_source_entailed_positive_hit":int(any(x["rank_over_UP"]>0 for x in steps)),
        "natural_search_probes":natural_probes,
        "additional_training_probes_charged":extra_probes,
        "natural_pairwork":natural_pairs,
        "extra_training_pairwork":extra_pairs,
        "exact_replay_and_order_wall_seconds":normal_elapsed+extra_elapsed,
        "all_root_proof_attempts":steps,
        "all_extra_train_proof_attempts":extra,
        "negative_and_abstain_retained":True,
        "XOR_inventory_complete":"NOT_CLAIMED"
    }
    state.records.append(evidence)
    return evidence

def run_seed(seed,manifest):
    original_seed=exact.SEED
    exact.SEED=seed
    try:
        states={arm:State(arm) for arm in ARMS}
        prepare_seconds=0.0
        for index in range(TRAIN+HOLDOUT):
            phase="TRAIN" if index<TRAIN else "FROZEN_HOLDOUT"
            if phase=="TRAIN":
                training_case=exact.source_case(index)
                source={**training_case,
                        "source_logical_sha256":training_case["original_source_logical_sha256"]}
                # exact source_case() checks model against original clauses
            else:
                slot=index-TRAIN
                source=fresh.generate(seed,slot)
                lock=manifest[(seed,slot)]
                if (lock["source_logical_sha256"]!=source["source_logical_sha256"]
                    or lock["family"]!=source["family"] or lock["n"]!=source["n"]):
                    raise AssertionError("UNFROZEN_SOURCE_OR_CNF_SHA_MISMATCH")
            t=perf_counter()
            known,up=source_context(source["rows"],source["n"])
            features=[exact.feature(source["rows"],p)
                      for p in range(1,source["n"]+1)]
            prepare_seconds+=perf_counter()-t
            before={arm:state.checkpoint()[1] for arm,state in states.items()} if phase=="FROZEN_HOLDOUT" else {}
            results={arm:solve_source(state,seed,index,phase,source,
                                     (known,up,features))
                     for arm,state in states.items()}
            if len(set(x["first_source_entailed_positive_hit"] for x in results.values()))!=1:
                raise AssertionError("SAME_CNF_EXACT_HIT_COVERAGE_DIFFERENT")
            if phase=="FROZEN_HOLDOUT":
                for arm,state in states.items():
                    if state.checkpoint()[1]!=before[arm]:
                        raise AssertionError("HOLDOUT_LEARNING_OR_MEMORY_MUTATION")
        summary={}
        snapshots={}
        checks=[]
        all_train=set()
        all_test=set()
        for arm,state in states.items():
            mem,sha=state.checkpoint()
            snapshots[arm]={"sha256":sha,"model":mem}
            all_train.update(state.training_sha)
            all_test.update(state.test_sha)
            checks.append((state.train_positive,state.test_positive))
            summary[arm]={
                "train_original_task_exact_probes_plus_extra":state.train_probes,
                "train_unique_extra_oracle_probes":state.extra_training_probes,
                "holdout_exact_probes":state.test_probes,
                "train_plus_holdout_exact_probes":state.train_probes+state.test_probes,
                "train_pair_work":state.train_pairwork,
                "holdout_pair_work":state.test_pairwork,
                "train_plus_holdout_pair_work":state.train_pairwork+state.test_pairwork,
                "verified_train_positive_cases":state.train_positive,
                "verified_holdout_positive_cases":state.test_positive,
                "train_elapsed_search_replay_seconds":state.train_seconds,
                "holdout_elapsed_search_replay_seconds":state.test_seconds,
                "measured_full_search_train_plus_holdout_seconds":state.train_seconds+state.test_seconds,
                "model_memory_verified_observations":sum(n for _,n in state.history.values()),
                "model_memory_feature_buckets":len(state.history),
                "memory_sha256":sha,
            }
            if arm in ("PASSIVE_COST_AWARE","PASSIVE_JUXTAPOSE_HISTORY") and state.extra_training_probes:
                raise AssertionError("PASSIVE_LEARNER_REQUESTED_EXTRA_LABELS")
        if len(set(checks))!=1:
            raise AssertionError("ON_POLICY_ARMS_CHANGED_SOURCE_POSITIVE_COVERAGE")
        if all_test.intersection(all_train):
            raise AssertionError("TRAIN_AND_TEST_ORIGINAL_SOURCE_SHA_OVERLAP")
        if len(all_test)!=HOLDOUT:
            raise AssertionError("NONUNIQUE_HOLDOUT_CNF")
        return {"seed":seed,"holdout_source_shas":sorted(all_test),
                "train_source_shas":sorted(all_train),
                "all_arms_uses_exact_original_CNF_proof_replay":True,
                "frozen_holdout_memory_unchanged":True,
                "same_math_proof_coverage_all_arms":True,
                "shared_CNF_source_context_preprocessing_wall_seconds":prepare_seconds,
                "summary":summary,"memory":snapshots,
                "records":{arm:state.records for arm,state in states.items()}}
    finally:
        exact.SEED=original_seed

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--memory-dir",type=Path)
    a=ap.parse_args()
    fixed=frozen()
    t=perf_counter()
    reports=[run_seed(seed,fixed) for seed in SEEDS]
    combined_test={sha for report in reports for sha in report["holdout_source_shas"]}
    if len(combined_test)!=120 or combined_test!={x["source_logical_sha256"] for x in fixed.values()}:
        raise AssertionError("UNREGISTERED_OR_REUSED_FUTURE_CNF")
    if a.memory_dir:
        a.memory_dir.mkdir(parents=True,exist_ok=True)
        for report in reports:
            for arm,v in report["memory"].items():
                (a.memory_dir/f"{report['seed']}_{arm}.json").write_text(
                    json.dumps(v["model"],sort_keys=True,indent=2)+"\n")
    result={
        "schema":SCHEMA,
        "protocol_blob":PROTOCOL_BLOB,
        "original_SHA_source_manifest_blob":MANIFEST_BLOB,
        "preregistered_seeds":list(SEEDS),
        "all_120_OOD_CNF_SHA_distinct_and_frozen":True,
        "no_extra_source_probes_for_passive_training":True,
        "training_and_holdout_each_exact_root_replay":True,
        "full_SAT_solver_timing":"NOT_MEASURED",
        "external_independent_witness":"NONE",
        "scientific_level":"SAME_ADMIN_SYNTHETIC_PROSPECTIVE_INTERNAL",
        "R6":"R6_FROZEN_SCIENCE_GATE_NOT_PASSED",
        "production_C023":"UNCHANGED",
        "total_experiment_wall_seconds":perf_counter()-t,
        "reports":reports
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":"JUXTAPOSE_R5_PASSIVE_ZERO_EXTRA_TRAIN_LABELS_TESTED",
        "source_manifest_blob":MANIFEST_BLOB,
        "summary":[{"seed":r["seed"],
            "arms":{arm:{
                  "train_probes":v["train_original_task_exact_probes_plus_extra"],
                  "extra_train_probes":v["train_unique_extra_oracle_probes"],
                  "holdout_probes":v["holdout_exact_probes"],
                  "total_probes":v["train_plus_holdout_exact_probes"],
                  "total_pairs":v["train_plus_holdout_pair_work"],
                  "test_hits":v["verified_holdout_positive_cases"],
                  "model_sha":v["memory_sha256"]}
                   for arm,v in r["summary"].items()}}
                   for r in reports]},sort_keys=True))
if __name__=="__main__":
    main()
