#!/usr/bin/env python3
import argparse, collections, fnmatch, hashlib, json, re, subprocess
from pathlib import Path

CONCEPTS = {
  "SHARED_DAG_REUSE": ["proof dag", "shared dag", "hash-cons", "hash cons", "formula-caching", "formula caching", "cache hit", "reuse", "memoization"],
  "CERTIFICATE_PORTFOLIO": ["certificate portfolio", "tractable portfolio", "portfolio-guided", "portfolio guided", "proof-carrying tractable portfolio", "candidate portfolio"],
  "CERTIFICATE_DISCOVERY_COMPLEXITY": ["certificate discovery", "discovery complexity", "discovery budget", "candidate discovery", "layout discovery", "vtree discovery"],
  "CONTEXT_PROJECTION": ["context projection", "projection discovery", "reaching context", "projected residual", "projection"],
  "INTERFACE_BOUNDARY_WIDTH": ["interface width", "cut width", "boundary", "separator", "trellis", "support overlap", "semantic support overlap"],
  "CERTIFIED_CONGRUENCE": ["certified interface congruence", "congruence", "same certified message", "safe merge", "equivalence certificate"],
  "PARTITION_REFINEMENT": ["partition refinement", "separating continuation", "refinement"],
  "OFFSET_POSITION_AWARE": ["affine offset", "offset-aware", "offset aware", "distinguished functional", "coset", "augmented affine", "consistency signature"],
  "SYMBOLIC_FACTOR_REPRESENTATION": ["symbolic factor", "structured vtree factor", "factor construction", "factor node", "resolution product factor", "or-forest", "or forest"],
  "CAPABILITY_RELATIVE_OPEN": ["capability digest", "capability stale", "open_portfolio_exhausted", "open_cut_width", "capability"],
  "SCALAR_SUMMARY_LOSS": ["local summary", "fixed-radius", "fixed radius", "best_square_gap", "near4", "scalar summary", "summary insufficiency"],
  "RECOMPUTE_VS_REUSE": ["independent powmod", "powmod probes", "incremental group", "bsgs", "recompute", "reuse", "group multiplications"],
  "REPRESENTATION_BLOWUP": ["representation blow", "serialized", "serialization", "or-forest", "obdd nodes", "exponential leaves", "certificate volume"],
  "PAID_ACCOUNTING": ["work ledger", "charged", "total compute", "donor cost", "budget", "memory ledger", "certificate cap"],
  "UNKNOWN_OPEN_DISCIPLINE": ["unknown_resource_limit", "unknown_timeout", "open_", "not a lower bound", "does not imply", "not hardness"],
  "CROSS_CLASS_COMPOSITION": ["cross-class composition", "cross class composition", "composition", "gemini", "dual-core", "dual core"],
  "PIPPI_EXPERIENCE_REUSE": ["pippi", "pit stop", "learning ecology", "experience reuse", "delayed learning"],
  "EXACT_FULL_TYPED_STATE": ["full exact", "typed", "canonical", "operands", "provenance", "witness", "certificate"],
}

PREDEFINED_FINDINGS = [
  {"id":"F01_LOCAL_SUMMARY_REPEATED","concepts":["SCALAR_SUMMARY_LOSS","EXACT_FULL_TYPED_STATE"],"historical_markers":["C022"],"factor_markers":["UNIFIED_V0","GEMINI_V1"],"classification":"DUPLICATED_BARRIER","claim":"The late best_square_gap/NEAR4 scalar handoff repeats the earlier local-summary insufficiency pattern: an advisory feature was allowed to stand in for the full exact relation interface.","action":"Keep scalar summaries ranking-only; retain full typed relation nodes and require exact projectable consequences."},
  {"id":"F02_RECOMPUTE_REUSE_RECURS","concepts":["SHARED_DAG_REUSE","RECOMPUTE_VS_REUSE"],"historical_markers":["C032_C047","THEOREM_39100"],"factor_markers":["SHOR_V2","GEMINI_V1"],"classification":"DUPLICATED_BARRIER","claim":"Representation sharing/reuse recurs as the same barrier in theorem OR-forest serialization and in factoring where BSGS dominates independent exponent recomputation.","action":"Centralize modular powers, gcd chains, factors and projections in one charged content-addressed arithmetic DAG."},
  {"id":"F03_DISCOVERY_NOT_VERIFICATION","concepts":["CERTIFICATE_PORTFOLIO","CERTIFICATE_DISCOVERY_COMPLEXITY"],"historical_markers":["C026","C032_C047"],"factor_markers":["SHOR_V1","SHOR_V2","GEMINI_V1"],"classification":"RESTORE_NOW","claim":"Factoring has the same discovery/verification asymmetry already isolated by C026: factors, orders and congruences are cheap to verify, while discovering the right certificate language dominates.","action":"Use a frozen exact certificate-language portfolio with capability-bound OPEN terminals."},
  {"id":"F04_PROJECTION_WAS_REPLACED_BY_HINTING","concepts":["CONTEXT_PROJECTION","SCALAR_SUMMARY_LOSS"],"historical_markers":["C027","C032_C047"],"factor_markers":["GEMINI_V1","UNIFIED_V0"],"classification":"RESTORE_NOW","claim":"Late factoring passed hints/bases where old JANUS required an exact context projection. NEAR4 changed coordinates but certified no future-state reduction and produced 0/13 compression.","action":"Every nonterminal certificate must project to a replayable restriction/equivalence/refinement or terminate NO_TRACTABLE_PROJECTION."},
  {"id":"F05_LIVE_BOUNDARY_RECURS","concepts":["INTERFACE_BOUNDARY_WIDTH","PAID_ACCOUNTING"],"historical_markers":["C028","C032_C047"],"factor_markers":["GEMINI_V1","UNIFIED_V0"],"classification":"RESTORE_NOW","claim":"C028/C047 repeatedly show that future-relevant boundary information, not total history, is the productive parameter. Factoring currently lacks an exact arithmetic live-interface recurrence.","action":"Measure an arithmetic interface profile now; seek a scalar width only after proving an exact recurrence."},
  {"id":"F06_CONGRUENCE_REFINEMENT_LOST","concepts":["CERTIFIED_CONGRUENCE","PARTITION_REFINEMENT"],"historical_markers":["C032_C047"],"factor_markers":["GEMINI_V1","UNIFIED_V0"],"classification":"RESTORE_NOW","claim":"C035/C036 had a stronger state discipline than late factoring: merge only under certified future-message congruence and split only with a replayable separating continuation.","action":"Port certified equivalence/refinement to arithmetic proof states; absent a certificate, preserve distinct states."},
  {"id":"F07_SYMBOLIC_FACTOR_CROSS_BRANCH","concepts":["SYMBOLIC_FACTOR_REPRESENTATION","SHARED_DAG_REUSE","REPRESENTATION_BLOWUP"],"historical_markers":["C032_C047","THEOREM_39100"],"factor_markers":["UNIFIED_V0"],"classification":"RETEST_WITH_NEW_CONTEXT","claim":"C039 symbolic factors and the later 39100 resolution-product factor solve the same representation problem at different layers: preserve exact factor structure without materializing its expansion.","action":"Make symbolic exact arithmetic factors first-class DAG nodes and test whether factoring relations admit similarly reusable compact factor objects."},
  {"id":"F08_CAPABILITY_LIFECYCLE","concepts":["CAPABILITY_RELATIVE_OPEN","UNKNOWN_OPEN_DISCIPLINE"],"historical_markers":["C032_C047"],"factor_markers":["SHOR_V2","GEMINI_V1","UNIFIED_V0"],"classification":"RESTORE_NOW","claim":"OPEN/UNKNOWN receipts should be capability-relative. Adding a representation/projection language can make an old OPEN stale for a successor without changing the historical result.","action":"Bind every future OPEN to a capability digest and introduce CAPABILITY_STALE_FOR_SUCCESSOR as metadata only."},
  {"id":"F09_OFFSET_POSITION_LOSS","concepts":["OFFSET_POSITION_AWARE","EXACT_FULL_TYPED_STATE"],"historical_markers":["C032_C047"],"factor_markers":["UNIFIED_V0"],"classification":"RESTORE_NOW","claim":"C046 proves shape-only state is unsound in an affine setting. The analogous factoring lesson is to retain full relation position/operands/offsets rather than labels such as NEAR4.","action":"Bind full operands and consistency signatures to arithmetic messages; labels remain advisory."},
  {"id":"F10_DUAL_CORE_DETOUR","concepts":["CROSS_CLASS_COMPOSITION","CONTEXT_PROJECTION"],"historical_markers":["C032_C047"],"factor_markers":["SHOR_V2","GEMINI_V1"],"classification":"KEEP_DEAD","claim":"Naive dual-core GEMINI repeated a weaker architecture than old cross-class interface composition: two solvers running independently produced compute tax and 0 measured synergy.","action":"Keep independent dual-core execution dead; compose certificate languages over one proof state instead."},
  {"id":"F11_PIPPI_HALF_MISSING","concepts":["PIPPI_EXPERIENCE_REUSE","PAID_ACCOUNTING"],"historical_markers":["C032_C047"],"factor_markers":["SHOR_V2","GEMINI_V1","UNIFIED_V0"],"classification":"RETEST_WITH_NEW_CONTEXT","claim":"Recent factoring retained excellent frozen falsification/accounting but mostly used static runners; the paid experience-reuse half of JANUS was not structurally integrated into representation/language selection.","action":"After the shared proof state exists, let Pippi rank future operator/language choices from prior paid exact utility only; never current-episode self-promote."},
  {"id":"F12_INTERFACE_THEOREM_STILL_OPEN","concepts":["INTERFACE_BOUNDARY_WIDTH","CERTIFICATE_DISCOVERY_COMPLEXITY"],"historical_markers":["C032_C047"],"factor_markers":["UNIFIED_V0"],"classification":"OPEN_THEOREM","claim":"The recurring surviving theorem is not yet polynomial factoring but discovery of a bounded exact future interface under a charged representation portfolio.","action":"Do not name a factoring width from empirical metrics; first prove an exact state recurrence and then study whether its maximum interface is poly(log N)."}
]

def sh(cmd): return subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT)
def matched(path,patterns): return any(fnmatch.fnmatch(path,p) for p in patterns)
def git_paths(ref,patterns): return sorted({p for p in sh(["git","ls-tree","-r","--name-only",ref]).splitlines() if matched(p,patterns)})
def read_git(ref,path): return sh(["git","show",f"{ref}:{path}"])
def fs_paths(root,patterns):
    root=Path(root);out=[]
    if not root.exists():return out
    for p in root.rglob('*'):
        if p.is_file():
            rel=p.relative_to(root).as_posix()
            if matched(rel,patterns):out.append(rel)
    return sorted(set(out))
def count_terms(text,terms):
    low=text.lower();return sum(low.count(t.lower()) for t in terms)

def audit(manifest_path,output_path):
    manifest=json.loads(Path(manifest_path).read_text());sources=[];errors=[]
    for group in manifest['source_groups']:
        try:
            if group.get('filesystem_root'):
                root=Path(group['filesystem_root']);paths=fs_paths(root,group['include']);reader=lambda p,root=root:(root/p).read_text(errors='replace')
            elif group['ref']=='WORKTREE':
                paths=[]
                for pattern in group['include']:
                    paths.extend(p.as_posix() for p in Path('.').glob(pattern) if p.is_file())
                paths=sorted(set(paths));reader=lambda p:Path(p).read_text(errors='replace')
            else:
                paths=git_paths(group['ref'],group['include']);reader=lambda p,ref=group['ref']:read_git(ref,p)
            for path in paths:
                try:text=reader(path)
                except Exception as e:errors.append({"group":group['id'],"path":path,"error":str(e)});continue
                data=text.encode('utf-8','replace');hits={c:count_terms(text,terms) for c,terms in CONCEPTS.items()};hits={k:v for k,v in hits.items() if v}
                cycles=["C"+x.zfill(3) for x in sorted(set(re.findall(r'\bC0?([0-9]{2})\b',text,re.I)))]
                sources.append({"id":group['id']+":"+path,"group":group['id'],"role":group['role'],"repo":group['repo'],"ref":group['ref'],"path":path,"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),"concept_hits":hits,"cycles":cycles})
        except Exception as e:errors.append({"group":group['id'],"error":str(e)})
    concept_docs=collections.defaultdict(list);concept_groups=collections.defaultdict(set);concept_roles=collections.defaultdict(set)
    graph_nodes=[];graph_edges=[]
    for s in sources:
        graph_nodes.append({"id":"SRC:"+s['id'],"type":"SOURCE","group":s['group'],"role":s['role'],"path":s['path'],"sha256":s['sha256']})
        for c,n in s['concept_hits'].items():
            concept_docs[c].append(s['id']);concept_groups[c].add(s['group']);concept_roles[c].add(s['role']);graph_edges.append({"from":"SRC:"+s['id'],"to":"CONCEPT:"+c,"type":"MENTIONS","weight":n})
    for c in CONCEPTS:graph_nodes.append({"id":"CONCEPT:"+c,"type":"MECHANISM_OR_BARRIER"})
    pair_sources=collections.defaultdict(set);pair_groups=collections.defaultdict(set);pair_roles=collections.defaultdict(set)
    for s in sources:
        cs=sorted(s['concept_hits'])
        for i,a in enumerate(cs):
            for b in cs[i+1:]:
                pair=(a,b);pair_sources[pair].add(s['id']);pair_groups[pair].add(s['group']);pair_roles[pair].add(s['role'])
    spider=[]
    for (a,b),ss in pair_sources.items():
        groups=sorted(pair_groups[(a,b)]);roles=sorted(pair_roles[(a,b)])
        if len(groups)>=2:
            cross=("historical_mechanism" in roles or "historical_lineage" in roles) and "factor_pre_v1" in roles
            spider.append({"a":a,"b":b,"support_sources":len(ss),"support_groups":groups,"roles":roles,"cross_era":cross});graph_edges.append({"from":"CONCEPT:"+a,"to":"CONCEPT:"+b,"type":"CO_OCCURS_ACROSS_SOURCES","weight":len(ss),"groups":groups})
    spider.sort(key=lambda x:(x['cross_era'],len(x['support_groups']),x['support_sources']),reverse=True)
    role_counts=collections.defaultdict(lambda:collections.Counter())
    for s in sources:
        for c,n in s['concept_hits'].items():role_counts[c][s['role']]+=n
    lifecycle=[]
    for c in CONCEPTS:
        hist=role_counts[c]['historical_mechanism']+role_counts[c]['historical_lineage'];pre=role_counts[c]['factor_pre_v1'];cur=role_counts[c]['current_v1']
        if hist and not pre and cur:state='DROPPED_THEN_RESTORED_IN_V1'
        elif hist and pre and cur:state='SURVIVED_AND_RESTORED_EXPLICITLY'
        elif hist and not pre and not cur:state='HISTORICAL_NOT_PORTED'
        elif hist and pre and not cur:state='PRESENT_PRE_V1_NOT_EXPLICIT_IN_RESTORATION'
        else:state='NO_CLEAR_LIFECYCLE_SIGNAL'
        lifecycle.append({"concept":c,"historical_hits":hist,"factor_pre_v1_hits":pre,"current_v1_hits":cur,"state":state})
    findings=[]
    for f in PREDEFINED_FINDINGS:
        ev=[s['id'] for s in sources if any(m in s['group'] or m in s['path'] for m in f['historical_markers']+f['factor_markers']) and any(c in s['concept_hits'] for c in f['concepts'])]
        supported=[c for c in f['concepts'] if concept_docs.get(c)];status='SUPPORTED_ASSOCIATION' if len(supported)==len(f['concepts']) and ev else 'INSUFFICIENT_CORPUS_SUPPORT'
        findings.append({**f,"status":status,"evidence_sources":ev[:24],"evidence_source_count":len(ev)})
    inventory_digest=hashlib.sha256('\n'.join(sorted(s['sha256'] for s in sources)).encode()).hexdigest();by_role=collections.Counter(s['role'] for s in sources);by_group=collections.Counter(s['group'] for s in sources)
    result={"schema":"JANUS/TOPA-SPIDER/SPIRAL-AUDIT-RESULT/v1.0","status":"COMPLETE" if sources else "UNKNOWN_NO_SOURCES","manifest_sha256":hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest(),"source_inventory":{"count":len(sources),"bytes":sum(s['bytes'] for s in sources),"sha256_multiset_digest":inventory_digest,"by_role":dict(by_role),"by_group":dict(by_group),"errors":errors},"governance":{"association_is_not_proof":True,"audit_may_rank_but_not_certify_arithmetic":True,"same_episode_authority_promotion":False,"negative_receipts_preserved":True},"concept_support":{c:{"documents":len(concept_docs[c]),"groups":sorted(concept_groups[c]),"roles":sorted(concept_roles[c]),"total_hits":sum(s['concept_hits'].get(c,0) for s in sources)} for c in CONCEPTS},"concept_lifecycle":lifecycle,"predefined_findings":findings,"spider_top_cross_source_connections":spider[:60],"graph":{"nodes":graph_nodes,"edges":graph_edges},"sources":sources,"scientific_boundary":{"this_is_evidence_graph_association_not_proof":True,"polynomial_time_factoring":False,"P_VS_NP":"OPEN"}}
    Path(output_path).parent.mkdir(parents=True,exist_ok=True);Path(output_path).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({"status":result['status'],"sources":len(sources),"bytes":result['source_inventory']['bytes'],"inventory_digest":inventory_digest,"supported_findings":sum(f['status']=='SUPPORTED_ASSOCIATION' for f in findings),"lifecycle":dict(collections.Counter(x['state'] for x in lifecycle)),"top_connections":spider[:12]},indent=2,ensure_ascii=False))
    if not sources:raise SystemExit(2)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',default='research/TOPA_SPIDER_SPIRAL_AUDIT_SOURCE_MANIFEST_2026-08-29.json');ap.add_argument('--output',default='artifacts/TOPA_SPIDER_SPIRAL_AUDIT_RESULT_2026-08-29.json');a=ap.parse_args();audit(a.manifest,a.output)
