#!/usr/bin/env python3
"""Permanent original SHA-pinned SATComp P-center source and 1524-line DRUP."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
from janus_time_sat_003_drup_witness import verify_drup
from janus_time_sat_004b_baselines import read_cnf

ID="011984fd82d62d609e776fbf5de75440"
ZIP_SHA="3f569bfcd7840cb980d2385bf4f4b76b66da2ae8c24b6014a582adf59614079a"
ORIGINAL_SHA="fa3549a5f3dd4fbd31a2ac6ccecd6a72f5a6bb5f71212d15257d3f00ab7c8d23"
CNF_SHA="0542d88497b5a7ef610e30a570e8be9088bdb343e4b54d31561b5ae47bfa906b"
PROOF_SHA="e860c2a8593099c64b0d603404c8f28b050549252f4e945e7cf7a88aaf622ada"
EXPECTED_ARTIFACT_ID=13089888230
ORIGINAL_RUN_ID=41323536441


def digest(b):return sha256(b).hexdigest()


def archive(original_zip,out):
    original_bytes=original_zip.read_bytes()
    if digest(original_bytes)!=ZIP_SHA:
        raise AssertionError("GITHUB_ACTIONS_ORIGINAL_ZIP_SHA_CHANGED")
    compressed_name=ID+".download"
    cnf_name=ID+".original.cnf"
    with zipfile.ZipFile(original_zip) as z:
        if set(z.namelist())!={compressed_name,cnf_name,"pcenter_replay.json"}:
            raise AssertionError("INVALID_ORIGINAL_ARTIFACT_MEMBERS")
        compressed=z.read(compressed_name)
        cnf=z.read(cnf_name)
        report_bytes=z.read("pcenter_replay.json")
    if digest(compressed)!=ORIGINAL_SHA or digest(cnf)!=CNF_SHA:
        raise AssertionError("GBD_ORIGINAL_SOURCE_BYTES_CHANGED")
    report=json.loads(report_bytes)
    proof=report.get("actual_proof_lines")
    if (not isinstance(proof,list) or len(proof)!=1524 or
        report["source_and_proof_digest"]!=PROOF_SHA or
        report["drup_checker_status"]!="INDEPENDENT_RUP_REPLAY_PASS"):
        raise AssertionError("SOURCE_PROOF_EXPECTATION_FAILED")
    out.mkdir(parents=True,exist_ok=True)
    (out/"original.cnf").write_bytes(cnf)
    (out/"original.download.xz").write_bytes(compressed)
    (out/"original.drup").write_text("\n".join(proof)+"\n",encoding="ascii")
    (out/"pcenter_replay.original.json").write_bytes(report_bytes)
    (out/"original-github-actions.zip").write_bytes(original_bytes)
    # Cross-check via separate trusted source parser and no-SAT-call checker.
    clauses=read_cnf(out/"original.cnf",2320,8620)
    independent=verify_drup(clauses,proof,timeout_seconds=20,
                            max_steps=5000,max_resident_clauses=20000)
    if independent.evidence_sha256!=PROOF_SHA or not independent.complete_empty_clause:
        raise AssertionError("INDEPENDENT_REPLAY_DIFFERENCE")
    file_digests={p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    manifest={
        "schema":"JANUS-TIME-SAT-004B-PCENTER-ORIGINAL-COMPETITION-DRUP-ARCHIVE-V1",
        "original_run_id":ORIGINAL_RUN_ID,
        "source_artifact_id":EXPECTED_ARTIFACT_ID,
        "original_artifact_sha256":ZIP_SHA,
        "original_gbd_id_NOT_sha256":ID,
        "original_raw_download_SHA256":ORIGINAL_SHA,
        "original_uncompressed_CNF_SHA256":CNF_SHA,
        "source_cnf_n":2320,"source_cnf_clauses":8620,
        "original_full_DRUP_lines":1524,
        "source_and_DRUP_SHA256":PROOF_SHA,
        "independent_RUP_replay":"PASS",
        "independent_RUP_additions":independent.additions_checked,
        "independent_RUP_deletions_ignored":independent.deletions_ignored,
        "empty_clause_verified":True,
        "source_catalog_label":"unknown",
        "research_conclusion":"UNSAT for this exact source CNF, not a hard-SAT advantage",
        "external_administrative_Witness":"NOT_DONE",
        "source_bytes_are_original_Github_CI_artifact":True,
        "files_SHA256":file_digests,"production_C023":"UNCHANGED"
    }
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("PCENTER_ORIGINAL_ARCHIVE_PASS",json.dumps({
        "DRUP_lines":len(proof),"additions":independent.additions_checked,
        "deletions":independent.deletions_ignored,"files":len(file_digests)+1,
        "proof_sha":PROOF_SHA},sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    archive(a.zip,a.out)
