#!/usr/bin/env python3
"""TIME-SAT-004A: archive **exact** two GitHub Actions artifact ZIP byte streams.

An accepted archive MUST match the known original Actions artifact ZIP SHA256
AND inside JSON sha, source run/head/seed, three original-CNF/DRUP digests,
and an independent deterministic RUP replay on BOTH original artifacts.
Never regenerate missing original evidence from a seed or silently accept
mismatched source. This script does not write into C023/main.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from janus_time_sat_003_drup_witness import verify_drup

RUN_ID=41315201470
SOURCE_HEAD="9fec44ab9b5a876ef9a8b9b85d1bf0fbd42596c3"
SOURCE_TEST_MERGE_SHA="cac6ae986274ebe912bc70b0c594147fa29b7caa"
GENERATOR_SEED=20261101003
MANIFEST="5c65a017c8dd732029030dbee64bd66a98ca9c98e9a29df1a58027733cca90aa"
ARCHIVES={
  "ubuntu-22.04":{
    "artifact_id":13087185767,
    "zip_sha256":"6c2fef395c4b0e9adb6e6799011dc26a6a4bf0ce3b019119e1ea9194f03896e4",
    "json_sha256":"3d15be1b48aa01e091b2b02c45a5715e9247300d5497475896ebe168abaadfd3",
    "json_name":"time-sat-003-ubuntu-22.04.json",
  },
  "ubuntu-24.04":{
    "artifact_id":13087505475,
    "zip_sha256":"64774ad2324a0356386133bd6cca3398a8f2df18e1d002e940b3a86d110de1fb",
    "json_sha256":"c46d9b2146fc2b774789ac07add8832134c9534e062d57765b40eaa8e1709f73",
    "json_name":"time-sat-003-ubuntu-24.04.json",
  },
}
EXPECTED_PROOFS={
  128:("2b503f4a2dddc95baed1a96fa31b2fc1a36206dd97ca56a892aefaef3e184a8c",8),
  220:("5e6713aa0b9026ef0947a165ddb7e387679202e82de2097a6dd3551b6c69359f",8),
  240:("a9195bcaaa5eb8c4c407397a5d0a162c093416bb2396210159869d2dd865bca2",12),
}


def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def stable_json(obj)->bytes:
    return (json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()


def parse_archive(host,path:Path,receipt:dict):
    raw=path.read_bytes()
    if digest(raw)!=receipt["zip_sha256"]:
        raise AssertionError("ARTIFACT_ZIP_SHA256_MISMATCH "+host)
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if names!=[receipt["json_name"]]:
            raise AssertionError("UNEXPECTED_ZIP_MEMBERS "+host)
        payload=z.read(names[0])
    if digest(payload)!=receipt["json_sha256"]:
        raise AssertionError("ARTIFACT_INNER_JSON_SHA256_MISMATCH "+host)
    obj=json.loads(payload)
    prov=obj["provenance"]
    if (str(prov.get("github_run_id"))!=str(RUN_ID) or
        prov["github_sha"]!=SOURCE_TEST_MERGE_SHA or
        prov["new_generator_seed"]!=GENERATOR_SEED or
        prov["new_manifest_sha256"]!=MANIFEST):
        raise AssertionError("WRONG_TESTED_SOURCE "+host)
    observations={}
    for n,(expected_hash,additions) in EXPECTED_PROOFS.items():
        case=next((x for x in obj["new_controls"]
                   if x["id"]==f"NEW_UNSAT_CORE_{n}"),None)
        if case is None:
            raise AssertionError("MISSING_UNSAT_CNF_OR_PROOF "+str(n))
        cnf=case["original_cnf_for_independent_replay"]
        proof=case["unit_proof"].get("raw_drup_lines")
        if not isinstance(cnf,list) or not isinstance(proof,list):
            raise AssertionError("ORIGINAL_CNF_AND_FULL_DRUP_REQUIRED "+str(n))
        rcpt=verify_drup(cnf,proof,timeout_seconds=20,max_steps=15000,
                         max_resident_clauses=30000)
        if rcpt.evidence_sha256!=expected_hash or rcpt.additions_checked!=additions:
            raise AssertionError("ORIGINAL_PROOF_HASH_OR_ADDITIONS_MISMATCH "+str(n))
        if case["unit_proof"]["certificate_sha256"]!=expected_hash:
            raise AssertionError("SOURCE_REPORTED_PROOF_HASH_MISMATCH")
        actual_n=max(abs(lit) for row in cnf for lit in row)
        if actual_n>n:
            raise AssertionError("BAD_SOURCE_VARIABLE_BOUND")
        # Explicit n comes from original generator name; DIMACS may have
        # unused variables. Text is derived from (never used to replace) raw
        # preserved original proof zip.
        dimacs="p cnf %d %d\n"%(n,len(cnf))
        dimacs+="".join(" ".join(map(str,row))+" 0\n" for row in cnf)
        drup="\n".join(proof)+"\n"
        observations[str(n)]={
            "name":case["id"],"original_source_CNF_rows":len(cnf),
            "drup_lines":len(proof),"rup_additions":rcpt.additions_checked,
            "rup_deletions_ignored":rcpt.deletions_ignored,
            "proof_with_original_input_SHA256":rcpt.evidence_sha256,
            "dimacs_sha256":digest(dimacs.encode()),
            "drup_file_sha256":digest(drup.encode()),
            "dimacs":dimacs,"drup":drup,
        }
    return obj,observations


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip-22",type=Path,required=True)
    p.add_argument("--zip-24",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    location={"ubuntu-22.04":a.zip_22,"ubuntu-24.04":a.zip_24}
    validated={}
    source_cases={}
    for host,source_zip in location.items():
        receipt=ARCHIVES[host]
        original,proofs=parse_archive(host,source_zip,receipt)
        validated[host]={"original_gitHub_artifact_id":receipt["artifact_id"],
                         "original_zip_sha256":receipt["zip_sha256"],
                         "original_json_sha256":receipt["json_sha256"],
                         "source_json_member":receipt["json_name"],
                         "original_zip_size_bytes":source_zip.stat().st_size,
                         "proofs":{
                          k:{key:value for key,value in v.items()
                             if key not in ("dimacs","drup")}
                          for k,v in proofs.items()},
                         "original_resource_measurements":
                           {x["id"]:x["isolated_peak_rss"]
                            for x in original["new_controls"]},
                         "original_science_aggregates":original["aggregates"]}
        source_cases[host]=proofs
    # Both cloud hosts must literally agree on every archived original
    # CNF and every original DRUP text, not just declared digest.
    for key in map(str,EXPECTED_PROOFS):
        if source_cases["ubuntu-22.04"][key]["dimacs"]!=source_cases["ubuntu-24.04"][key]["dimacs"]:
            raise AssertionError("TWO_HOST_ORIGINAL_CNF_DISAGREEMENT "+key)
        if source_cases["ubuntu-22.04"][key]["drup"]!=source_cases["ubuntu-24.04"][key]["drup"]:
            raise AssertionError("TWO_HOST_ORIGINAL_DRUP_DISAGREEMENT "+key)
    base=a.output
    base.mkdir(parents=True,exist_ok=True)
    outputs={}
    for host,source_zip in location.items():
        dest=base/"original_artifacts"/("time-sat-003-"+host+".zip")
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source_zip,dest)
        outputs[str(dest.relative_to(base))]=digest(dest.read_bytes())
    for key,data in source_cases["ubuntu-24.04"].items():
        folder=base/"proofs"/("n"+key)
        folder.mkdir(parents=True,exist_ok=True)
        for suffix,payload in (("cnf",data["dimacs"]),("drup",data["drup"])):
            dest=folder/("original."+suffix)
            dest.write_text(payload,encoding="ascii")
            outputs[str(dest.relative_to(base))]=digest(dest.read_bytes())
    manifest={
      "schema":"JANUS-TIME-SAT-004A-EXACT-ARTIFACT-EVIDENCE-20261101-v1",
      "source_run_id":RUN_ID,
      "source_pr_head_sha":SOURCE_HEAD,
      "source_ci_checkout_sha":SOURCE_TEST_MERGE_SHA,
      "synthetic_not_hidden":True,
      "baseline_and_witness_same_administrative_trust":True,
      "generator_seed":GENERATOR_SEED,
      "generator_manifest_sha256":MANIFEST,
      "all_sha_against_original_raw_ZIP":"PASS",
      "all_original_source_CNF_and_DRUP_REPLAY":"PASS",
      "two_hosts_original_input_and_proof_byte_agreement":"PASS",
      "GitHub_original_artifact_expiration_utc":"2026-12-01T14:14:57Z",
      "source_original_URL":"https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41315201470",
      "hosts":validated,"stored_sha256":outputs,
      "restriction":"Original binary artifacts retained unmodified; extracted DIMACS and DRUP are convenience views derived solely from those bytes. Not a hard SAT claim or independent external Witness."
    }
    (base/"manifest.json").write_bytes(stable_json(manifest))
    print(json.dumps({"status":"ORIGINAL_ARTIFACT_AND_PROOF_ARCHIVE_PASS",
                       "sha_replay":"PASS","files":len(outputs)+1,
                       "source_run_id":RUN_ID,
                       "host_zips":{k:v["original_zip_sha256"] for k,v in validated.items()},
                       "proofs":{k:v["proof_with_original_input_SHA256"] for k,v in validated["ubuntu-24.04"]["proofs"].items()},
                       "output":str(base)},sort_keys=True))

if __name__=="__main__":
    main()
