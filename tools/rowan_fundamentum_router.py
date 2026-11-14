#!/usr/bin/env python3
"""Offline Rowan × JANUS Fundamentum capability router.

This does not import Rowan, use network, submit code, or spend credits.
It prevents treating Rowan's documented scientific APIs as generic compute.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

POLICY = Path(__file__).resolve().parents[1] / "research/ROWAN_FUNDAMENTUM_CAPABILITY_POLICY_v1.json"
SHA40 = re.compile(r"^[a-f0-9]{40}$")
SHA64 = re.compile(r"^[a-f0-9]{64}$")
ALLOWED = {"schema", "task_id", "task_class", "execute", "max_credits",
           "source_repo", "source_commit", "input_sha256", "scientific_goal"}


def route(policy: dict, req: dict) -> dict:
    """A planning decision, never a provider authorization."""
    issue = []
    if not isinstance(req, dict):
        req = {}
        issue.append("INVALID_REQUEST")
    if req.get("schema") != "janus.fundamentum.rowan_request.v1":
        issue.append("INVALID_SCHEMA")
    if set(req) - ALLOWED:
        issue.append("UNSUPPORTED_FIELDS_OR_CODE_PAYLOAD")
    if not isinstance(req.get("task_id"), str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", req["task_id"]):
        issue.append("INVALID_TASK_ID")
    if req.get("execute") is not False:
        issue.append("EXECUTION_IS_DENIED")
    if type(req.get("max_credits")) is not int or req["max_credits"] != 0:
        issue.append("CREDIT_SPEND_IS_DENIED")
    kinds = policy["classes"]
    kind = req.get("task_class")
    if not isinstance(kind, str) or kind not in kinds:
        issue.append("UNKNOWN_TASK_CLASS")
    origin = req.get("source_repo")
    if origin != "Hawkar-usls/Janus-Fundamentum":
        issue.append("INVALID_SOURCE")
    if not isinstance(req.get("source_commit"), str) or not SHA40.fullmatch(req["source_commit"]):
        issue.append("UNPINNED_SOURCE_COMMIT")
    if not isinstance(req.get("input_sha256"), str) or not SHA64.fullmatch(req["input_sha256"]):
        issue.append("INVALID_INPUT_DIGEST")
    if not isinstance(req.get("scientific_goal"), str) or not 8 <= len(req["scientific_goal"]) <= 300:
        issue.append("MISSING_SCIENTIFIC_GOAL")
    record = kinds.get(kind, {})
    if issue:
        disposition = "BLOCKED"
    elif kind == "MOLECULAR_PKA":
        disposition = "PLAN_ONLY_EXISTING_ADAPTER_NO_REMOTE_CALL"
    elif kind == "PHYSICAL_CSP_ANALOG":
        disposition = "RESEARCH_HOLD_NO_PHYSICAL_OR_FORMAL_EQUIVALENCE"
    else:
        disposition = "NOT_ROUTABLE_TO_ROWAN"
    return {
        "schema": "janus.fundamentum.rowan_routing_receipt.v1",
        "task_id": req.get("task_id"),
        "task_class": kind,
        "classification": record.get("classification", "UNKNOWN"),
        "destination": record.get("destination", "NONE"),
        "disposition": disposition,
        "issues": sorted(issue),
        "provider_called": False,
        "provider_job_submitted": False,
        "provider_credits_spent": 0,
        "cross_repository_write": False,
        "physics_or_chemistry_proved_np_claim": False,
        "p_vs_np": "OPEN",
    }


def self_test(policy: dict) -> None:
    template = {
        "schema":"janus.fundamentum.rowan_request.v1",
        "task_id":"case-1",
        "task_class":"MOLECULAR_PKA",
        "execute":False,
        "max_credits":0,
        "source_repo":"Hawkar-usls/Janus-Fundamentum",
        "source_commit":"a"*40,
        "input_sha256":"b"*64,
        "scientific_goal":"Predict pKa for an independently selected molecular validation control."
    }
    ok = route(policy, template)
    assert ok["disposition"] == "PLAN_ONLY_EXISTING_ADAPTER_NO_REMOTE_CALL"
    assert not ok["provider_called"]
    cases = [
        ({"task_class":"GENERAL_COMPUTE"}, "NOT_ROUTABLE_TO_ROWAN"),
        ({"task_class":"PROOF_VERIFICATION"}, "NOT_ROUTABLE_TO_ROWAN"),
        ({"task_class":"EXACT_ONE_SAT"}, "NOT_ROUTABLE_TO_ROWAN"),
        ({"task_class":"MOLECULAR_OTHER"}, "NOT_ROUTABLE_TO_ROWAN"),
        ({"task_class":"PHYSICAL_CSP_ANALOG"}, "RESEARCH_HOLD_NO_PHYSICAL_OR_FORMAL_EQUIVALENCE"),
        ({"execute":True}, "BLOCKED"),
        ({"max_credits":1}, "BLOCKED"),
        ({"source_commit":"main"}, "BLOCKED"),
        ({"input_sha256":"invalid"}, "BLOCKED"),
        ({"code":"print('hello')"}, "BLOCKED"),
        ({"task_class":"container_shell"}, "BLOCKED"),
        ({"source_repo":"untrusted/other"}, "BLOCKED"),
    ]
    for patch, status in cases:
        request=copy.deepcopy(template)
        request.update(patch)
        got=route(policy,request)
        assert got["disposition"] == status, (patch,got)
        assert not got["provider_called"] and got["provider_credits_spent"]==0
    print(json.dumps({"self_test":"PASS","cases":len(cases)+1,
                      "scope":"OFFLINE_ONLY","rowan_compute_calls":0}))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--policy", type=Path, default=POLICY)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--request", type=Path)
    args=ap.parse_args()
    policy=json.loads(args.policy.read_text(encoding="utf-8"))
    assert policy["schema"]=="janus.fundamentum.rowan_capability_gate.v1"
    if args.self_test:
        self_test(policy)
        return 0
    try:
        req=json.loads(args.request.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        print(json.dumps({"disposition":"BLOCKED","issues":["REQUEST_UNREADABLE_OR_INVALID"]}))
        return 2
    verdict=route(policy,req)
    print(json.dumps(verdict,ensure_ascii=False,indent=2,sort_keys=True))
    return 2 if verdict["disposition"]=="BLOCKED" else 0


if __name__=="__main__":
    raise SystemExit(main())
