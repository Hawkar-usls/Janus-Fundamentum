#!/usr/bin/env python3
"""Independent verifier for Fundamentum multidirectional frontier v1.3."""
from __future__ import annotations
import argparse, copy, hashlib, json, re, subprocess
from pathlib import Path
from typing import Dict, List

SCHEMA="janus.fundamentum.multidirectional_frontier_report.v1.3"
REGISTRY_SCHEMA="janus.fundamentum.research_target_registry.v1"
BASE_COMMIT="e7663ed9be87ebd37bfa51c01501e74c9d5b2603"
SUFFIXES={".md",".json",".py",".yml",".yaml",".txt"}; MAX_BYTES=2_000_000
PROOF_CLASSES={"AUDIT","EXECUTABLE","WORKFLOW","SPEC_OR_CERT"}
RELATION_WEIGHT={"MAIN":100,"VERY_HIGH":80,"HIGH":65,"DIRECT_CONTINUATION":85,"VERY_INTERESTING":60,"MEDIUM":40,"MEDIUM_FAR":25,"ARCHITECTURALLY_POSSIBLE_MATHEMATICALLY_FAR":5}

def cb(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def oh(v): return hashlib.sha256(cb(v)).hexdigest()
def git(root,*args): return subprocess.check_output(["git","-C",str(root),*args])
def mcount(text,marker):
    return sum(1 for _ in re.finditer(r"(?<![A-Za-z0-9_])"+re.escape(marker)+r"(?![A-Za-z0-9_])",text,re.I))
def sclass(rel):
    if rel.startswith("experiments/direct/audits/"): return "AUDIT"
    if rel.startswith(".github/workflows/"): return "WORKFLOW"
    if rel.startswith("experiments/direct/") and rel.endswith(".py"): return "EXECUTABLE"
    if rel.startswith("experiments/direct/") and rel.endswith(".json"): return "SPEC_OR_CERT"
    return "NARRATIVE_OR_OTHER"
def corpus(root):
    rels=sorted(x.decode() for x in git(root,"ls-tree","-r","--name-only","-z",BASE_COMMIT).split(b"\0") if x)
    rows=[]; h=hashlib.sha256(BASE_COMMIT.encode())
    for rel in rels:
        if Path(rel).suffix.lower() not in SUFFIXES: continue
        try: data=git(root,"show",f"{BASE_COMMIT}:{rel}")
        except subprocess.CalledProcessError: continue
        if len(data)>MAX_BYTES: continue
        try: text=data.decode("utf-8")
        except UnicodeDecodeError: continue
        rows.append((rel,text,sclass(rel))); h.update(rel.encode()); h.update(b"\0"); h.update(hashlib.sha256(data).digest())
    return rows,h.hexdigest()
def closure(edges,start):
    g:Dict[str,List[str]]={}
    for a,b in edges: g.setdefault(a,[]).append(b)
    seen={start}; q=[start]; out=[]
    while q:
        cur=q.pop(0)
        for nxt in sorted(g.get(cur,[])):
            if nxt not in seen: seen.add(nxt); out.append(nxt); q.append(nxt)
    return out
def pscore(t,s,o,can): return RELATION_WEIGHT.get(t["relation"],0)+min(s,20)*3+min(o,50)+(20 if can else 0)
def rclass(t,ps,allc):
    if t["fundamentum_status"]=="DOMAIN_BRIDGE_NOT_ESTABLISHED": return "DOMAIN_BRIDGE_REQUIRED"
    if ps: return "PROOF_BEARING_ROUTE_SURFACE_FOUND_REQUIRES_THEOREM"
    if allc: return "NARRATIVE_ROUTE_SURFACE_ONLY_REQUIRES_THEOREM"
    return "NO_PRE_FRONTIER_ROUTE_SURFACE_FOUND"
def verify(root,r,report):
    assert r["schema"]==REGISTRY_SCHEMA and len(r["targets"])==23
    assert r["base_binding"]["b5_4_evidence_head"]==BASE_COMMIT
    assert r["policy"]["preferred_outcome"] is None and r["policy"]["route_search_is_not_proof"] is True
    assert report["schema"]==SCHEMA and report["corpus_commit"]==BASE_COMMIT
    assert report["registry_semantic_sha256"]==oh(r); assert report["target_count"]==23
    assert report["global_terminal"]=="OPEN" and report["claim_ceiling"]["ANY_A0_A4_TARGET_RESOLVED"] is False
    assert report["search_policy"]["active_route_from_relation_metadata_forbidden"] is True
    assert report["search_policy"]["declared_priority_separated_from_evidence_ranking"] is True
    unhashed=copy.deepcopy(report); supplied=unhashed.pop("report_semantic_sha256"); assert supplied==oh(unhashed)
    rows,ch=corpus(root); assert report["corpus_semantic_sha256"]==ch and report["scanned_surface_count"]==len(rows)
    by={x["id"]:x for x in report["targets"]}; assert len(by)==23
    evidence=[]; priority=[]; a3=[]
    for t in r["targets"]:
        row=by[t["id"]]; allp=set(); proofp=set(); total=0; po=0; pmc=0
        cps={k:set() for k in ["AUDIT","EXECUTABLE","WORKFLOW","SPEC_OR_CERT","NARRATIVE_OR_OTHER"]}; mrows=[]
        for marker in t["search_markers"]:
            paths=[]; ppaths=[]; occ=0; pocc=0
            for rel,text,cls in rows:
                n=mcount(text,marker)
                if not n: continue
                occ+=n; paths.append(rel); allp.add(rel); cps[cls].add(rel)
                if cls in PROOF_CLASSES: pocc+=n; ppaths.append(rel); proofp.add(rel)
            if pocc: pmc+=1
            total+=occ; po+=pocc
            mrows.append({"marker":marker,"occurrences":occ,"surface_count":len(paths),"proof_occurrences":pocc,"proof_surface_count":len(ppaths),"surfaces":paths[:10],"proof_surfaces":ppaths[:10]})
        pos=closure(r["explicit_implications"],t["positive_terminal"]); neg=closure(r["explicit_implications"],t["negative_terminal"]); can="P_NOT_EQUALS_NP" in pos or "P_NOT_EQUALS_NP" in neg
        pc=sum(bool(cps[c]) for c in PROOF_CLASSES); ekey=[pc,len(proofp),pmc,po]
        assert row["marker_results"]==mrows and row["repository_surface_count"]==len(allp) and row["marker_occurrences"]==total
        assert row["proof_bearing_surface_count"]==len(proofp) and row["proof_bearing_occurrences"]==po and row["proof_bearing_class_count"]==pc and row["proof_marker_coverage"]==pmc
        assert row["surface_class_counts"]=={c:len(cps[c]) for c in sorted(cps)}
        assert row["repository_surfaces"]==sorted(allp)[:20] and row["proof_bearing_surfaces"]==sorted(proofp)[:20]
        assert row["positive_implication_closure"]==pos and row["negative_implication_closure"]==neg and row["can_reach_p_not_np_by_explicit_implication"] is can
        assert row["route_classification"]==rclass(t,len(proofp),len(allp)); assert row["declared_priority_score"]==pscore(t,len(allp),total,can); assert row["evidence_rank_key"]==ekey
        assert row["proof_status"]=="NOT_PROVED_BY_THIS_SEARCH"
        evidence.append((t["id"],ekey)); priority.append((t["id"],row["declared_priority_score"]));
        if t["level"]=="A3": a3.append((t["id"],ekey))
    er=[x[0] for x in sorted(evidence,key=lambda z:(-z[1][0],-z[1][1],-z[1][2],-z[1][3],z[0]))]
    pr=[x[0] for x in sorted(priority,key=lambda z:(-z[1],z[0]))]
    ar=[x[0] for x in sorted(a3,key=lambda z:(-z[1][0],-z[1][1],-z[1][2],-z[1][3],z[0]))]
    assert report["evidence_ranking"]==er and report["declared_priority_ranking"]==pr and report["a3_evidence_ranking"]==ar and report["selected_a3_candidate"]==(ar[0] if ar else None)
def reject(root,r,report,mut):
    b=copy.deepcopy(report); mut(b); u=copy.deepcopy(b); u.pop("report_semantic_sha256",None); b["report_semantic_sha256"]=oh(u)
    try: verify(root,r,b)
    except (AssertionError,KeyError,TypeError,ValueError): return
    raise AssertionError("tamper accepted")
def tampers(root,r,report):
    attacks=[
      lambda x:x.__setitem__("corpus_commit","HEAD"), lambda x:x.__setitem__("global_terminal","P_EQUALS_NP"),
      lambda x:x["claim_ceiling"].__setitem__("ANY_A0_A4_TARGET_RESOLVED",True), lambda x:x["search_policy"].__setitem__("active_route_from_relation_metadata_forbidden",False),
      lambda x:x["targets"][0].__setitem__("proof_status","PROVED"), lambda x:x["targets"][0].__setitem__("route_classification","ACTIVE_STRUCTURAL_ROUTE"),
      lambda x:x["targets"][0].__setitem__("proof_bearing_surface_count",x["targets"][0]["proof_bearing_surface_count"]+1),
      lambda x:x["targets"][0].__setitem__("proof_bearing_class_count",9), lambda x:x["targets"][0].__setitem__("proof_marker_coverage",99),
      lambda x:x["targets"][0].__setitem__("declared_priority_score",9999), lambda x:x["evidence_ranking"].reverse(), lambda x:x["declared_priority_ranking"].reverse(),
      lambda x:x.__setitem__("selected_a3_candidate","A0_P_VS_NP"), lambda x:x.__setitem__("corpus_semantic_sha256","0"*64),
      lambda x:x.__setitem__("registry_semantic_sha256","f"*64), lambda x:x["targets"][0]["surface_class_counts"].__setitem__("AUDIT",999),
      lambda x:x["targets"][0].__setitem__("positive_implication_closure",[]), lambda x:x["targets"][0].__setitem__("can_reach_p_not_np_by_explicit_implication",False),
      lambda x:x["targets"][0].__setitem__("repository_surfaces",[]), lambda x:x["targets"][0].__setitem__("proof_bearing_surfaces",[])
    ]
    for a in attacks: reject(root,r,report,a)
    return len(attacks)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--registry",default="research_targets/FUNDAMENTUM_RESEARCH_TARGET_REGISTRY_V1.json"); ap.add_argument("--report",required=True); ap.add_argument("--tamper-test",action="store_true"); a=ap.parse_args()
    root=Path(a.root).resolve(); r=json.loads((root/a.registry).read_text()); report=json.loads(Path(a.report).read_text()); verify(root,r,report)
    print("INDEPENDENT_FRONTIER_V1_3_REPLAY = PASS"); print("PRE_FRONTIER_CORPUS_AUTHORITY = PASS"); print("RELATION_TO_ACTIVE_ROUTE_PROMOTION = FORBIDDEN"); print("GLOBAL_TERMINAL = OPEN")
    if a.tamper_test:
        n=tampers(root,r,report); print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {n}/{n}")
if __name__=="__main__": main()
