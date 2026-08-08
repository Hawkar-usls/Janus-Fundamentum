#!/usr/bin/env python3
"""Fundamentum multidirectional frontier v1.3.

Search authority is the immutable pre-frontier B5.4 evidence tree.  The report
separates declared research priority from repository evidence.  Text hits are
never mathematical proofs and no target is promoted to ACTIVE from registry
metadata alone.
"""
from __future__ import annotations

import argparse, hashlib, json, re, subprocess
from pathlib import Path
from typing import Dict, List, Tuple

SCHEMA = "janus.fundamentum.multidirectional_frontier_report.v1.3"
REGISTRY_SCHEMA = "janus.fundamentum.research_target_registry.v1"
BASE_COMMIT = "e7663ed9be87ebd37bfa51c01501e74c9d5b2603"
SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt"}
MAX_BYTES = 2_000_000
PROOF_CLASSES = {"AUDIT", "EXECUTABLE", "WORKFLOW", "SPEC_OR_CERT"}
RELATION_WEIGHT = {
    "MAIN": 100, "VERY_HIGH": 80, "HIGH": 65, "DIRECT_CONTINUATION": 85,
    "VERY_INTERESTING": 60, "MEDIUM": 40, "MEDIUM_FAR": 25,
    "ARCHITECTURALLY_POSSIBLE_MATHEMATICALLY_FAR": 5,
}


def cbytes(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def ohash(v):
    return hashlib.sha256(cbytes(v)).hexdigest()

def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])

def marker_count(text: str, marker: str) -> int:
    rx = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(marker) + r"(?![A-Za-z0-9_])", re.I)
    return sum(1 for _ in rx.finditer(text))

def surface_class(rel: str) -> str:
    if rel.startswith("experiments/direct/audits/"):
        return "AUDIT"
    if rel.startswith(".github/workflows/"):
        return "WORKFLOW"
    if rel.startswith("experiments/direct/") and rel.endswith(".py"):
        return "EXECUTABLE"
    if rel.startswith("experiments/direct/") and rel.endswith(".json"):
        return "SPEC_OR_CERT"
    return "NARRATIVE_OR_OTHER"

def base_corpus(root: Path) -> Tuple[List[Tuple[str, str, str]], str]:
    raw = git(root, "ls-tree", "-r", "--name-only", "-z", BASE_COMMIT)
    rels = sorted(x.decode() for x in raw.split(b"\0") if x)
    rows = []
    h = hashlib.sha256(BASE_COMMIT.encode())
    for rel in rels:
        if Path(rel).suffix.lower() not in SUFFIXES:
            continue
        try:
            data = git(root, "show", f"{BASE_COMMIT}:{rel}")
        except subprocess.CalledProcessError:
            continue
        if len(data) > MAX_BYTES:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        cls = surface_class(rel)
        rows.append((rel, text, cls))
        h.update(rel.encode()); h.update(b"\0"); h.update(hashlib.sha256(data).digest())
    return rows, h.hexdigest()

def closure(edges, start):
    g: Dict[str, List[str]] = {}
    for a, b in edges:
        g.setdefault(a, []).append(b)
    seen, q, out = {start}, [start], []
    while q:
        cur = q.pop(0)
        for nxt in sorted(g.get(cur, [])):
            if nxt not in seen:
                seen.add(nxt); out.append(nxt); q.append(nxt)
    return out

def declared_priority(target, surface_count, occurrences, can_pneqnp):
    return RELATION_WEIGHT.get(target["relation"], 0) + min(surface_count, 20)*3 + min(occurrences, 50) + (20 if can_pneqnp else 0)

def route_class(target, proof_surface_count, any_surface_count):
    if target["fundamentum_status"] == "DOMAIN_BRIDGE_NOT_ESTABLISHED":
        return "DOMAIN_BRIDGE_REQUIRED"
    if proof_surface_count:
        return "PROOF_BEARING_ROUTE_SURFACE_FOUND_REQUIRES_THEOREM"
    if any_surface_count:
        return "NARRATIVE_ROUTE_SURFACE_ONLY_REQUIRES_THEOREM"
    return "NO_PRE_FRONTIER_ROUTE_SURFACE_FOUND"

def validate_registry(r):
    assert r["schema"] == REGISTRY_SCHEMA and len(r["targets"]) == 23
    assert r["policy"]["preferred_outcome"] is None and r["policy"]["route_search_is_not_proof"] is True
    assert r["base_binding"]["b5_4_evidence_head"] == BASE_COMMIT
    assert r["base_binding"]["current_ceiling"]["P_VS_NP"] == "OPEN"
    assert r["base_binding"]["current_ceiling"]["B5_COMPLETE"] is False

def build(root: Path, registry: dict) -> dict:
    validate_registry(registry)
    corpus, corpus_digest = base_corpus(root)
    edges = registry["explicit_implications"]
    results = []
    for t in registry["targets"]:
        all_paths, proof_paths = set(), set()
        marker_rows, total_occ, proof_occ, proof_marker_coverage = [], 0, 0, 0
        class_paths = {k:set() for k in ["AUDIT","EXECUTABLE","WORKFLOW","SPEC_OR_CERT","NARRATIVE_OR_OTHER"]}
        for marker in t["search_markers"]:
            paths, ppaths, occ, pocc = [], [], 0, 0
            for rel, text, cls in corpus:
                n = marker_count(text, marker)
                if not n: continue
                occ += n; paths.append(rel); all_paths.add(rel); class_paths[cls].add(rel)
                if cls in PROOF_CLASSES:
                    pocc += n; ppaths.append(rel); proof_paths.add(rel)
            if pocc: proof_marker_coverage += 1
            total_occ += occ; proof_occ += pocc
            marker_rows.append({"marker":marker,"occurrences":occ,"surface_count":len(paths),"proof_occurrences":pocc,"proof_surface_count":len(ppaths),"surfaces":paths[:10],"proof_surfaces":ppaths[:10]})
        pos, neg = closure(edges, t["positive_terminal"]), closure(edges, t["negative_terminal"])
        can = "P_NOT_EQUALS_NP" in pos or "P_NOT_EQUALS_NP" in neg
        proof_class_count = sum(bool(class_paths[c]) for c in PROOF_CLASSES)
        evidence_key = [proof_class_count, len(proof_paths), proof_marker_coverage, proof_occ]
        results.append({
            "id":t["id"], "level":t["level"], "question":t["question"], "relation":t["relation"],
            "positive_terminal":t["positive_terminal"], "negative_terminal":t["negative_terminal"],
            "fundamentum_status":t["fundamentum_status"], "route_classification":route_class(t,len(proof_paths),len(all_paths)),
            "repository_surface_count":len(all_paths), "marker_occurrences":total_occ,
            "proof_bearing_surface_count":len(proof_paths), "proof_bearing_occurrences":proof_occ,
            "proof_bearing_class_count":proof_class_count, "proof_marker_coverage":proof_marker_coverage,
            "surface_class_counts":{c:len(class_paths[c]) for c in sorted(class_paths)},
            "repository_surfaces":sorted(all_paths)[:20], "proof_bearing_surfaces":sorted(proof_paths)[:20],
            "marker_results":marker_rows, "positive_implication_closure":pos, "negative_implication_closure":neg,
            "can_reach_p_not_np_by_explicit_implication":can,
            "declared_priority_score":declared_priority(t,len(all_paths),total_occ,can),
            "evidence_rank_key":evidence_key, "next_bridge":t["next_bridge"], "proof_status":"NOT_PROVED_BY_THIS_SEARCH"
        })
    evidence_ranked = sorted(results, key=lambda x:(-x["evidence_rank_key"][0],-x["evidence_rank_key"][1],-x["evidence_rank_key"][2],-x["evidence_rank_key"][3],x["id"]))
    priority_ranked = sorted(results, key=lambda x:(-x["declared_priority_score"],x["id"]))
    a3_ranked = [x["id"] for x in evidence_ranked if x["level"] == "A3"]
    body = {
        "schema":SCHEMA, "registry_schema":registry["schema"], "registry_semantic_sha256":ohash(registry),
        "corpus_commit":BASE_COMMIT, "corpus_semantic_sha256":corpus_digest, "scanned_surface_count":len(corpus),
        "search_policy":{
            "route_search_is_not_proof":True, "preferred_outcome":None,
            "corpus_authority":"immutable pre-frontier B5.4 evidence tree",
            "marker_matching":"case-insensitive literal with ASCII identifier boundaries",
            "active_route_from_relation_metadata_forbidden":True,
            "declared_priority_separated_from_evidence_ranking":True,
            "proof_bearing_classes":sorted(PROOF_CLASSES)
        },
        "target_count":len(results), "targets":results,
        "declared_priority_ranking":[x["id"] for x in priority_ranked],
        "evidence_ranking":[x["id"] for x in evidence_ranked],
        "a3_evidence_ranking":a3_ranked,
        "selected_a3_candidate":a3_ranked[0] if a3_ranked else None,
        "global_terminal":"OPEN",
        "claim_ceiling":{"ANY_A0_A4_TARGET_RESOLVED":False,"P_VS_NP":"OPEN","B5_COMPLETE":False,"POLYNOMIAL_RUNTIME":"NOT_ESTABLISHED","ALL_INPUT_TERMINATION":"NOT_ESTABLISHED"}
    }
    body["report_semantic_sha256"] = ohash(body)
    return body

def self_test():
    assert marker_count("NC NCX XNC _NC nc", "NC") == 2
    assert surface_class("experiments/direct/audits/x.json") == "AUDIT"
    assert surface_class("experiments/direct/x.py") == "EXECUTABLE"
    assert surface_class(".github/workflows/x.yml") == "WORKFLOW"
    assert route_class({"fundamentum_status":"OPEN"},1,1) == "PROOF_BEARING_ROUTE_SURFACE_FOUND_REQUIRES_THEOREM"
    print("FRONTIER_V1_3_SELF_TEST = PASS")
    print("PRE_FRONTIER_CORPUS_AUTHORITY = PASS")
    print("RELATION_TO_ACTIVE_ROUTE_PROMOTION = FORBIDDEN")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--registry",default="research_targets/FUNDAMENTUM_RESEARCH_TARGET_REGISTRY_V1.json"); ap.add_argument("--output",default="artifacts/fundamentum_multidirectional_frontier_v13.json"); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: self_test(); return
    root=Path(a.root).resolve(); r=json.loads((root/a.registry).read_text(encoding="utf-8")); report=build(root,r)
    out=(root/a.output).resolve(); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"CORPUS_COMMIT = {report['corpus_commit']}"); print(f"SCANNED_SURFACE_COUNT = {report['scanned_surface_count']}")
    print("EVIDENCE_TOP10 = "+",".join(report["evidence_ranking"][:10])); print("A3_EVIDENCE_RANKING = "+",".join(report["a3_evidence_ranking"])); print(f"SELECTED_A3_CANDIDATE = {report['selected_a3_candidate']}")
    for row in sorted(report["targets"],key=lambda x:x["id"]):
        print(f"TARGET {row['id']} | proof_surfaces={row['proof_bearing_surface_count']} | proof_classes={row['proof_bearing_class_count']} | marker_coverage={row['proof_marker_coverage']} | class={row['route_classification']}")
    print(f"REPORT_SEMANTIC_SHA256 = {report['report_semantic_sha256']}"); print("GLOBAL_TERMINAL = OPEN")
if __name__ == "__main__": main()
