#!/usr/bin/env python3
"""Physarum R6: compare user's real Tero PhysarumNetwork, JUXTAPOSE and Markov.

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
import janus_physarum_r6_new_sources as fresh
from janus_juxtapose_markov_r4_benchmark import source_context,verified_pivot,MarkovMemory,verified_state
from janus_physarum_r6_network import SATPhysarum

PROTOCOL=HERE/"PHYSARUM_JUXTAPOSE_R6_FROZEN_PROTOCOL_20261115.json"
PROTOCOL_BLOB="1ff4651d18a2ae99af41b57194f2f4263728613c"
MANIFEST=HERE/"PHYSARUM_R6_NEW_ORIGINAL_SHA_MANIFEST_20261115.json"
MANIFEST_BLOB="1c508d11e7689fc55b21a7e9633bab86852e94fb"
SEEDS=(2026111611,2026111612,2026111613,2026111614)
TRAIN=45
HOLDOUT=30
ARMS=("JUXTAPOSE_PASSIVE","PHYSARUM_NETWORK_ONLY",
      "JUXTAPOSE_PHYSARUM_HYBRID","MARKOV_PASSIVE",
      "JUXTAPOSE_MARKOV_PASSIVE","COST_GEOMETRY_NO_MEMORY",
      "STATIC_NUMERIC","RANDOM_FIXED")
TRAINABLE=("JUXTAPOSE_PASSIVE","PHYSARUM_NETWORK_ONLY",
           "JUXTAPOSE_PHYSARUM_HYBRID","MARKOV_PASSIVE",
           "JUXTAPOSE_MARKOV_PASSIVE")
PHYSARUM_ARMS=("PHYSARUM_NETWORK_ONLY","JUXTAPOSE_PHYSARUM_HYBRID")
MARKOV_ARMS=("MARKOV_PASSIVE","JUXTAPOSE_MARKOV_PASSIVE")
SCHEMA="JANUS-PHYSARUM-JUXTAPOSE-R6-ORIGINAL-ENGINE-SAT-EXACT-PROOF-V1"

def blob(path):
    return subprocess.run(["git","hash-object",str(path)],text=True,
                          check=True,capture_output=True).stdout.strip()

def frozen():
    if blob(PROTOCOL)!=PROTOCOL_BLOB or blob(MANIFEST)!=MANIFEST_BLOB:
        raise AssertionError("PRECOMMITTED_R5_PROTOCOL_OR_ORIGINAL_SHA_CHANGED")
    p=json.loads(PROTOCOL.read_text())
    m=json.loads(MANIFEST.read_text())
    if (p["schema"]!="JANUS-PHYSARUM-JUXTAPOSE-R6-SOURCE-FROZEN-COST-STUDY-V1"
        or p["preregistered_seeds"]!=list(SEEDS)
        or p["train_cases_each"]!=TRAIN
        or p["new_test_cases_each"]!=HOLDOUT
        or p["test_formula_variables"]!=16
        or p["arms"]!=list(ARMS)):
        raise AssertionError("PREDECLARED_R5_METRICS_OR_ALGORITHMS_DRIFT")
    if m!=fresh.manifest() or m["source_count"]!=120:
        raise AssertionError("ORIGINAL_CNF_SHA_MANIFEST_MISMATCH")
    return {(x["seed"],x["slot"]):x for x in m["items"]}

def trained_score(f,history):
    key=exact.model_key(f)
    positives,n=history.get(key,(0,0))
    return (positives+1)/(n+2)

def choose_next(state,pending,features,previous):
    """All policy proposals depend only on source features and earlier proofs."""
    arm=state.arm
    if arm=="STATIC_NUMERIC":return min(pending)
    if arm=="JUXTAPOSE_PASSIVE":
        return max(pending,key=lambda p:exact.trained_rank(features[p-1],state.history))
    if arm=="COST_GEOMETRY_NO_MEMORY":
        return max(pending,key=lambda p:(int(features[p-1]["eligible"]),
                                         -features[p-1]["pair_work"],
                                         features[p-1]["priority"]))
    def jux_probability(f):
        h,n=state.history.get(exact.model_key(f),(0,0))
        return (h+1)/(n+2)
    def score(p):
        f=features[p-1]
        eligible=int(f["eligible"])
        cost=math.sqrt(1+f["pair_work"])
        jux=jux_probability(f)
        if arm=="PHYSARUM_NETWORK_ONLY":
            v=state.physarum.source_score(f)
        elif arm=="JUXTAPOSE_PHYSARUM_HYBRID":
            v=0.5*jux/cost+0.5*state.physarum.source_score(f)
        elif arm=="MARKOV_PASSIVE":
            v=state.markov.predict(previous,f)/cost
        elif arm=="JUXTAPOSE_MARKOV_PASSIVE":
            v=(2*state.markov.predict(previous,f)+jux)/(3*cost)
        else:raise AssertionError("UNKNOWN_POLICY:"+arm)
        return (eligible,int(round(v*1000000000)),f["priority"])
    return max(pending,key=score)

class State:
    def __init__(self,arm,seed):
        self.arm=arm
        self.seed=seed
        self.history={}
        self.physarum=SATPhysarum() if arm in PHYSARUM_ARMS else None
        self.markov=MarkovMemory() if arm in MARKOV_ARMS else None
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
            "schema":"JANUS-PHYSARUM-R6-PAST-ONLY-PIVOT-MEMORY-V1",
            "algorithm":self.arm,
            "source_sha_training":self.training_sha,
            "memory":[{"features":k,"positives":v[0],"verified_total":v[1]}
                      for k,v in sorted(self.history.items())],
            "no_holdout_learning":True,
            "positive_labels_only_from_exact_original_source_resolution":True,
            "no_transformer":True,
            "physarum_network_state":self.physarum.state() if self.physarum else None,
            "first_order_markov_table":self.markov.snapshot(self.seed,self.training_sha)[0] if self.markov else None,
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
    previous="START"
    available=set(range(1,n+1))
    observed={}
    steps=[]
    random_order=list(range(1,n+1))
    random.Random(seed^(index*9941+281)).shuffle(random_order)
    while available:
        pivot=(random_order[len(steps)] if state.arm=="RANDOM_FIXED"
               else choose_next(state,available,features,previous))
        available.remove(pivot)
        outcome=verified_pivot(rows,n,pivot,known,up)
        observed[pivot]=outcome
        steps.append({"pivot":pivot,"proof":outcome["status"],
                      "previous_verified_state":previous,
                      "rank_over_UP":outcome["rank_delta_over_UP"],
                      "pairs":outcome["pair_work"]})
        previous=verified_state(outcome)
        if outcome["rank_delta_over_UP"]>0:
            if outcome["status"]!="EXACT_SOURCE_PROOF_REPLAY_PASS":
                raise AssertionError("UNVERIFIED_POSITIVE_RANK")
            break
    normal_elapsed=perf_counter()-start
    # All policies learn from the existing proof search only. No purchased
    # or extra exact proof calls merely for training.
    extra=[]
    extra_elapsed=0.0
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
        # Delayed learning: updates come only AFTER the completed source
        # search. All labels are verified by the same original-CNF proof DAG.
        update_start=perf_counter()
        if state.arm in TRAINABLE:
            for step in steps:
                pivot=step["pivot"]
                out=observed[pivot]
                if out["status"]!="EXACT_SOURCE_PROOF_REPLAY_PASS":
                    continue # unsupported/abstain is UNKNOWN, not negative
                f=features[pivot-1]
                key=exact.model_key(f)
                h,total=state.history.get(key,(0,0))
                good=int(out["rank_delta_over_UP"]>0)
                state.history[key]=(h+good,total+1)
                if state.physarum:
                    state.physarum.observe_source_verified(f,bool(good))
                if state.markov:
                    state.markov.observe(step["previous_verified_state"],f,out)
        state.train_seconds+=perf_counter()-update_start
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
        states={arm:State(arm,seed) for arm in ARMS}
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
                "physarum_conductivity_graph_nodes":17 if state.physarum else 0,
                "physarum_positive_source_updates":state.physarum.verified_hit_count if state.physarum else 0,
                "markov_transition_state_count":len(state.markov.transitions) if state.markov else 0,
                "model_memory_feature_buckets":len(state.history),
                "memory_sha256":sha,
            }
            if arm in TRAINABLE and state.extra_training_probes:
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
        "physarum_source_SHA256":"e0e7a7d6f62acbae18a68141c4708f9d0006679d5e58bb95f36bc74c398dcf13",
        "ported_physarum_component":"Tero-Nakagaki pressure-flow-conductivity only, not particle swarm",
        "no_extra_source_probes_for_passive_training":True,
        "training_and_holdout_each_exact_root_replay":True,
        "full_SAT_solver_timing":"NOT_MEASURED",
        "exact_root_search_time_includes_physarum_and_markov_updates":True,
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
        "status":"PHYSARUM_R6_120_FROZEN_CNF_EIGHT_ARM_COMPARISON_COMPLETE",
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
