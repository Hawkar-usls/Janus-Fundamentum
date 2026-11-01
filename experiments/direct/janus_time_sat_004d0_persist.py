#!/usr/bin/env python3
"""Pin exact original two-worker TIME-SAT-004D0 no-decision evidence.

No timeouts are accepted as SAT/UNSAT. All 32 original child jobs must be
UNKNOWN_CPU_LIMIT_SIGXCPU, as actually observed. Preserve raw ZIP + JSON,
separate normalized summary, all original per-arm wall telemetry. ZIP hashes
must match GitHub API prior to reading.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import zipfile

ORIGINAL_RUN=41326432087
SOURCE_HEAD="1c07c58ca513180453c28a87f6f520c6e790b129"
ORIGINAL={
"ubuntu-22.04":{"artifact_id":13091163305,
                "artifact_sha256":"ba8e44993e354c99d2086366619673db4bac4d1262a7cc77716b9f93dbba2b64"},
"ubuntu-24.04":{"artifact_id":13092050308,
                "artifact_sha256":"73290cee54abe215d20d93f52cb5199cb1b29aeccb2b8b9d325796e89acfed79"}
}
EXPECTED={"lights-out":"01d6fa8efd18ebfecd06af408958477b",
          "greentao":"08cf53ca00dce11f5bfc02121c9bcd33"}
ARMS={"raw","feature_only","janus_direct","janus_frozen_forecast"}
ENGINES={"cadical195","glucose4"}


def digest(b):return sha256(b).hexdigest()


def collect(inputs:dict[str,Path], out:Path):
    for host in ORIGINAL:
        if host not in inputs:raise AssertionError("missing worker original artifact")
    out.mkdir(parents=True,exist_ok=True)
    records={}
    originals={}
    checks={}
    for host,p in inputs.items():
        if host not in ORIGINAL:raise AssertionError("unexpected worker")
        raw=p.read_bytes()
        expected=ORIGINAL[host]
        if digest(raw)!=expected["artifact_sha256"]:
            raise AssertionError("ORIGINAL_ZIP_SHA_MISMATCH "+host)
        with zipfile.ZipFile(p) as z:
            names=z.namelist()
            if names!=["result.json"]:
                raise AssertionError("UNEXPECTED_ARCHIVE_MEMBERS "+str(names))
            content=z.read(names[0])
        data=json.loads(content)
        if (data.get("schema")!="JANUS-TIME-SAT-004D0-BOUNDED-LARGE-CNF-SMOKE-V1"
            or data.get("status")!="PUBLIC_EXPLORATORY_UNBLINDED"
            or data.get("cloud_run")!=str(ORIGINAL_RUN)
            or data.get("cloud_HEAD_sha")!=SOURCE_HEAD
            or data.get("repeats")!=1 or data.get("time_limit_child_CPU_seconds")!=6
            or data.get("child_RLIMIT_AS_bytes")!=2_147_483_648):
            raise AssertionError("UNEXPECTED_SOURCE_OR_RESOURCE_CAPS "+host)
        cases=data["results"]
        if len(cases)!=2:raise AssertionError("expected two frozen source cases")
        for c in cases:
            key=c["family"]
            if EXPECTED.get(key)!=c["id"]:
                raise AssertionError("WRONG_PILOT_COHORT "+key)
            if set(c["engines"])!=ENGINES:
                raise AssertionError("MISSING_CDCL_ENGINE")
            for engine,detail in c["engines"].items():
                if set(detail["arms"])!=ARMS or set(detail["randomized_order"])!=ARMS:
                    raise AssertionError("BAD_ARM_SELECTION")
                for arm,r in detail["arms"].items():
                    if r["verdict"]!="UNKNOWN_CPU_LIMIT_SIGXCPU" or r.get("return_code")!=-24:
                        raise AssertionError("INCONSISTENT_SOLVER_TERMINATION")
        dest=out/("original-"+host+".zip")
        dest.write_bytes(raw)
        (out/("original-"+host+".json")).write_bytes(content)
        originals[host]=data
        checks[host]={"artifact_id":expected["artifact_id"],
                      "original_zip_sha256":expected["artifact_sha256"],
                      "original_inner_json_sha256":digest(content),
                      "source_head":data["cloud_HEAD_sha"],
                      "full_case_runner_arms":16,
                      "CPU_SIGXCPU":16,
                      "full_child_wall_samples":[{
                           "family":c["family"],"engine":engine,"arm":arm,
                           "seconds":r["end_to_end_process_wall_seconds"],
                           "signal":r.get("process_signal")}
                           for c in cases for engine,v in c["engines"].items()
                           for arm,r in v["arms"].items()]}
    for i in range(2):
        a=originals["ubuntu-22.04"]["results"][i]
        b=originals["ubuntu-24.04"]["results"][i]
        if a["decoded_sha256"]!=b["decoded_sha256"] or a["original_sha256"]!=b["original_sha256"]:
            raise AssertionError("CROSS_HOST_SOURCE_HASH_DISAGREEMENT")
    summary={
      "schema":"JANUS-TIME-SAT-004D0-ORIGINAL-TWO-HOST-REPLAY-EVIDENCE-20261101-V1",
      "source_run_id":ORIGINAL_RUN,
      "source_exact_head_sha":SOURCE_HEAD,
      "conclusion":"DUAL_HOST_CORRECT_TEST_PASS_NO_TIMELY_SOLUTION_ANY_ARM",
      "original_artifact_archive":checks,
      "original_CNF_SHA256_cross_host":"PASS",
      "correctness_unit_tests_each_runner":{"new":"7/7 PASS","previous_004B":"6/6 PASS"},
      "full_arm_runs":32,
      "all_SAT_or_UNSAT_decisions":0,
      "UNKNOWN_CPU_LIMIT_SIGXCPU_runs":32,
      "portable_UNSAT_proofs":0,
      "test_instances":2,"test_solver_engines":2,"arms_per_engine":4,
      "repetitions":1,"confidence_interval":"NOT_ESTIMABLE_ALL_CENSORED",
      "conclusion_speedup":"NOT_DEMONSTRATED_TIME_LIMIT_CENSORED",
      "component_limitation":"JANUS binary resolution/forecast is verified as a safe preprocessor, NOT full scalable original JANUS solver",
      "external_blind":"NO_PUBLIC_COMPETITION",
      "independent_trust_admin":"NO_SAME_GITHUB",
      "production_C023":"UNCHANGED",
      "scope":"004D0 SMOKE ONLY, NOT 004D CHECKBOX",
    }
    (out/"summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("004D0_EXACT_EVIDENCE_ARCHIVE_PASS",json.dumps({
        "workers":len(checks),"total_timeouts":32,"test_families":list(EXPECTED),
        "source_run":ORIGINAL_RUN},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip-22",type=Path,required=True)
    p.add_argument("--zip-24",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    collect({"ubuntu-22.04":a.zip_22,"ubuntu-24.04":a.zip_24},a.out)
