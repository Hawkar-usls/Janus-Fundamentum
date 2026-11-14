#!/usr/bin/env python3
"""Verify a Lapis Rowan candidate against a local original Rowan receipt.

Offline only. SHA hashes are integrity checks, not provider authentication.
Do not submit science claims, execute generated code, or contact Rowan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

CANDIDATE_SCHEMA = "janus.lapis.rowan_fundamentum_candidate.v1"
MANIFEST_SCHEMA = "janus.lapis.rowan_translation_manifest.v1"
IR_SCHEMA = "janus.lapis.algorithm_ir.v1"
RESEARCH = "janus.rowan.research_receipt.v1"
BBC1 = "janus.rowan.bbc1.stratified_8_mutant_pilot.v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
MAX_BYTES = 512_000


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load(path: Path) -> dict:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("OVERSIZE_INPUT")
    raw=path.read_bytes()
    if len(raw)>MAX_BYTES:
        raise ValueError("OVERSIZE_INPUT")
    return json.loads(raw.decode("utf-8"))


def verify(bundle: Path, source: Path) -> dict:
    issues=[]
    try:
        c=load(bundle/"candidate.json")
        ir=load(bundle/"algorithm_ir.json")
        m=load(bundle/"manifest.json")
        raw=load(source)
        brief=(bundle/"brief.txt").read_bytes()
        if len(brief)>5000:
            raise ValueError("BRIEF_OVERSIZE")
    except (OSError, UnicodeError, ValueError, TypeError):
        return result(["MISSING_INVALID_OR_OVERSIZED_INPUT"])
    if not all(isinstance(x,dict) for x in (c,ir,m,raw)):
        return result(["EXPECTED_JSON_OBJECTS"])
    for schema,value,name in ((CANDIDATE_SCHEMA,c,"CANDIDATE"),
                               (MANIFEST_SCHEMA,m,"MANIFEST"),
                               (IR_SCHEMA,ir,"IR")):
        if value.get("schema")!=schema: issues.append("INVALID_"+name+"_SCHEMA")
    if set(c)!={"schema","source","facts","hypothesis_candidate","for_fundamentum"}:
        issues.append("UNEXPECTED_CANDIDATE_FIELDS")
    src=c.get("source",{})
    facts=c.get("facts",{})
    policy=c.get("for_fundamentum",{})
    hypothesis=c.get("hypothesis_candidate",{})
    if not all(isinstance(x,dict) for x in (src,facts,policy,hypothesis)):
        return result(issues+["INVALID_CANDIDATE_SHAPE"])
    try:
        original=sha(canonical(raw))
        if m.get("source_receipt_canonical_sha256")!=original or src.get("receipt_sha256")!=original:
            issues.append("SOURCE_RECEIPT_HASH_MISMATCH")
        if src.get("schema_id")!=raw.get("schema_id") or src.get("repository")!="Hawkar-usls/Janus":
            issues.append("SOURCE_IDENTITY_MISMATCH")
        expected_adapter="integrations/rowan" if raw.get("schema_id")==RESEARCH else "integrations/tranception_rowan"
        if src.get("adapter")!=expected_adapter:
            issues.append("SOURCE_ADAPTER_MISMATCH")
        if m.get("candidate_sha256")!=sha(canonical(c)):
            issues.append("CANDIDATE_INTEGRITY_FAILURE")
        if m.get("algorithm_ir_sha256")!=sha(canonical(ir)):
            issues.append("IR_INTEGRITY_FAILURE")
        if m.get("brief_sha256")!=sha(brief):
            issues.append("BRIEF_INTEGRITY_FAILURE")
    except (TypeError,ValueError,OverflowError):
        issues.append("INVALID_CANONICALIZATION")
    if m.get("status")!="OFFLINE_TRANSLATION_ONLY" or m.get("rowan_api_calls")!=0 or m.get("credits_spent_by_translator")!=0:
        issues.append("TRANSLATOR_EXTERNAL_EFFECT_CLAIM")
    if m.get("proof_authority") is not False or m.get("independent_authentication") is not False:
        issues.append("UNSUPPORTED_PROOF_OR_AUTH_CLAIM")
    if (policy.get("proof_or_exact_sat_witness") is not False
        or policy.get("P_VS_NP")!="OPEN"
        or policy.get("scientific_status")!="UNVERIFIED"
        or policy.get("rowan_credits_spent_by_translation")!=0
        or policy.get("rowan_job_created_by_translation") is not False
        or policy.get("independent_source_authentication") is not False):
        issues.append("FUNDAMENTUM_AUTHORITY_DRIFT")
    if hypothesis.get("status")!="UNTESTED" or hypothesis.get("category")!="EMPIRICAL_FALSIFICATION_PROPOSAL":
        issues.append("HYPOTHESIS_PROMOTION")
    algorithm=ir.get("algorithm",{})
    boundary=ir.get("scientific_boundary",{})
    if not isinstance(algorithm,dict) or not isinstance(boundary,dict):
        issues.append("INVALID_ALGORITHM_IR")
    else:
        steps=algorithm.get("steps")
        if (algorithm.get("mode")!="explicit_contract"
            or not isinstance(steps,list) or len(steps)!=2
            or any(not isinstance(s,dict) or s.get("operator")!="ANNOTATE" for s in steps)
            or boundary.get("P_VS_NP")!="OPEN"
            or boundary.get("heuristic_translation_is_proof") is not False):
            issues.append("IR_SEMANTICS_ESCALATION")
        try:
            ir_without_hash=dict(ir)
            h=ir_without_hash.pop("algorithm_sha256",None)
            if sha(canonical(ir_without_hash))!=h:
                issues.append("IR_INTERNAL_DIGEST_MISMATCH")
        except (TypeError,ValueError,OverflowError):
            issues.append("INVALID_IR_INTERNAL_DIGEST")
    # Verify the translation hasn't changed the numerical Rowan observation.
    if raw.get("schema_id")==RESEARCH:
        fields={"source_class","source_input_sha256","case_id","event",
                "workflow_uuid","method","data_status","values",
                "provider_reported_credits","scientific_note"}
        if set(facts)!=fields or facts.get("source_class")!="ROWAN_PKA":
            issues.append("PKA_FIELDS_MISMATCH")
        else:
            pred=raw.get("result")
            gathered=raw.get("event")=="ROWAN_RESULT_COLLECTED_UNVERIFIED"
            expected={"strongest_acid_pka":pred.get("strongest_acid_pka"),
                      "strongest_base_pka":pred.get("strongest_base_pka")} if gathered and isinstance(pred,dict) else {
                      "strongest_acid_pka":None,"strongest_base_pka":None}
            if (facts.get("values")!=expected
                or facts.get("source_input_sha256")!=raw.get("input_sha256")
                or facts.get("case_id")!=raw.get("case_id")
                or facts.get("event")!=raw.get("event")
                or facts.get("workflow_uuid")!=raw.get("workflow_uuid")
                or facts.get("method")!=raw.get("provider",{}).get("method")):
                issues.append("PKA_VALUE_OR_ID_MISMATCH")
    elif raw.get("schema_id")==BBC1:
        fields={"source_class","source_commit","source_sha256","data_status",
                "ready_count","expected_count","wildtype","samples","scientific_note"}
        if set(facts)!=fields or facts.get("source_class")!="ROWAN_BBC1_STRATIFIED":
            issues.append("BBC1_FIELDS_MISMATCH")
        else:
            cases=raw.get("pilot_cases",[])
            samples=facts.get("samples",[])
            if (not isinstance(cases,list) or not isinstance(samples,list) or len(cases)!=8 or len(samples)!=8
                or facts.get("source_commit")!=raw.get("source_commit")
                or facts.get("source_sha256")!=raw.get("source_sha256")
                or facts.get("expected_count")!=8):
                issues.append("BBC1_INPUT_ID_MISMATCH")
            else:
                for x,y in zip(cases,samples):
                    if (not isinstance(x,dict) or not isinstance(y,dict)
                        or y.get("mutation")!=x.get("mutation")
                        or y.get("state")!=x.get("provider_state")):
                        issues.append("BBC1_SAMPLE_MISMATCH")
                        break
                    if y["state"]=="PROVIDER_RESULT_RETURNED" and (
                        y.get("ptm")!=x.get("ptm") or y.get("avg_lddt")!=x.get("avg_lddt")):
                        issues.append("BBC1_SCORE_MISMATCH")
                        break
    else:
        issues.append("UNSUPPORTED_ROWAN_RECEIPT")
    return result(sorted(set(issues)))


def result(issues):
    return {"schema":"janus.fundamentum.lapis_rowan_admission_gate.v1",
            "status":"BLOCKED" if issues else "STRUCTURALLY_VALID_UNAUTHENTICATED",
            "issues":sorted(set(issues)),
            "source_authenticated":False,
            "rowan_api_calls":0,
            "provider_credits_spent":0,
            "proof_or_sat_authority":False,
            "p_vs_np":"OPEN"}


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle",type=Path,required=True)
    ap.add_argument("--source-receipt",type=Path,required=True)
    a=ap.parse_args()
    verdict=verify(a.bundle,a.source_receipt)
    print(json.dumps(verdict,ensure_ascii=False,indent=2))
    return 0 if verdict["status"]!="BLOCKED" else 2


if __name__=="__main__":
    raise SystemExit(main())
