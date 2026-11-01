#!/usr/bin/env python3
"""TIME-SAT-004D0 cheap proof-only diagnostics; NO additional SAT searches.

Same two exact SOURCE SHA as full-cost dual-runner CI #41326432087.
Separate from timing comparison; diagnostic wall seconds NOT comparable with
timed-out solving arms. Reject source mismatch. No SAT solver or external AI.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import resource
from time import perf_counter

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d_adapter import derive_binary_wedges,independently_replay_witnesses,frozen_cost
from janus_time_sat_004d_pilot import FROZEN_SHA

def run():
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(15,16))
    j=json.loads(Path("experiments/time_sat_004_external/PREREGISTERED_SATCOMP2026_PILOT_20261101.json").read_text())
    out=Path("evidence/time_sat_004d0_diagnostics")
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for candidate in j["candidates"]:
        d=FROZEN_SHA.get(candidate["hash"])
        if not d:continue
        before=perf_counter()
        origin,proof=retrieve(candidate,out)
        if proof["source_sha256"]!=d["original"]:
            raise AssertionError("independent source download sha changed")
        decoded=out/(candidate["hash"]+".cnf")
        raw=unpack_bounded(origin,decoded)
        if raw["uncompressed_sha256"]!=d["decoded"]:
            raise AssertionError("rechecked original decoded CNF differs")
        structure=scan_dimacs(decoded)
        if (structure["n_variables"],structure["n_clauses"])!=(d["n"],d["m"]):
            raise AssertionError("CNF dimensions differ")
        clauses=read_cnf(decoded,d["n"],d["m"])
        began=perf_counter()
        witnesses,visits,reason,occ=derive_binary_wedges(clauses,d["n"])
        replayed=independently_replay_witnesses(clauses,witnesses)
        forecast=frozen_cost(d["n"],d["m"],witnesses,visits,occ) if reason=="COMPLETE" else None
        proof_only_seconds=perf_counter()-began
        rows.append({
            "family":d["family"],"original_gbd_id":candidate["hash"],
            "source_sha256":proof["source_sha256"],
            "decoded_original_sha256":raw["uncompressed_sha256"],
            "dimensions":structure,
            "bounded_scan_reason":reason,
            "source_literal_occurrences_seen":visits,
            "direct_wedges_count":len(witnesses),
            "independent_original_clause_pair_witness_checks":replayed,
            "sample_witnesses":[{"literal":w[0],"original_clause_indices":[w[1],w[2]],"pivot":w[3]}
                               for w in witnesses],
            "frozen_003B_forecast":forecast,
            "proof_only_seconds_NOT_comparable_to_solver_timeout":proof_only_seconds,
            "diagnostic_process_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "total_download_and_parse_and_proof_seconds":perf_counter()-before,
        })
        print("004D0_PROBE",d["family"],reason,"witnesses",len(witnesses),
              "forecast_admit",forecast and forecast["admit"],flush=True)
        # Source byte artifacts are not rehosted here; their pinned hashes and
        # origin are maintained in 004B and available from original GBD.
        origin.unlink(missing_ok=True)
        decoded.unlink(missing_ok=True)
    if len(rows)!=2:raise AssertionError("missing frozen public control")
    result={
        "schema":"JANUS-TIME-SAT-004D0-INDEPENDENT-CHEAP-STAGE-DIAGNOSTIC-V1",
        "evidence_from_frozen_two_GBD_sources":True,
        "research_only":True,
        "separate_no_solver_proof_stage":True,
        "not_a_004D_performance_test":True,
        "not_an_external_trust_witness":True,
        "production_C023":"UNCHANGED",
        "results":rows
    }
    (out/"diagnostics.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
if __name__=="__main__":run()
