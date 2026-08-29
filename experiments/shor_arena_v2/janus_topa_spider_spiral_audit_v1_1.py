#!/usr/bin/env python3
import argparse, collections, json, re
from pathlib import Path
import janus_topa_spider_spiral_audit as base

EXTRA_CONCEPTS={
 "ADAPTIVE_MODE_SWITCHING":["keymaster","cold full","cold warm hot","cold","warm","hot","mode switch","fallback mode","adaptive weights"],
 "PLATEAU_MIRROR_REFLECTION":["pippi","plateau","mirror","reflection","pit stop","pit-stop"],
 "RANKING_NEVER_PRUNES_EXACT_SCOPE":["ranking may reorder","may not prune","never remove the ability to search","cold full","fallback exact","ranking only"],
 "FINGERPRINT_STATE_SPECTRUM":["fingerprint epoch","fingerprint","state spectrum","state-spectrum","spectrum meet"],
 "ASSOCIATIVE_VS_EXACT_GRAPH":["spider","association is not proof","associative graph","evidence graph","exact edge","proof dag"],
 "DELAYED_LEARNING":["delayed learning","same episode","self-promotion","self promotion","current episode","selecting authority"],
 "M2R_EXACT_RETRIEVAL":["m2r","retrieval","surgeon","memory retrieval","state spectrum"],
}
EXTRA_FINDINGS=[
 {"id":"F13_PIPPI_PLATEAU_REPRESENTATION_SWITCH","concepts":["PLATEAU_MIRROR_REFLECTION","CERTIFICATE_PORTFOLIO"],"historical_markers":["ADAPTIVE_KEYMASTER_TOPA","MAD_LAB"],"factor_markers":["UNIFIED_V1"],"classification":"RETEST_WITH_NEW_CONTEXT","claim":"Pippi plateau/mirror signals were used to react to search behavior, while factoring representation-language selection remained mostly static.","action":"Test whether a paid plateau signal may trigger a frozen next-episode representation-language switch; it may never certify a factor or prune exact scope."},
 {"id":"F14_KEYMASTER_AS_LANGUAGE_SELECTOR","concepts":["ADAPTIVE_MODE_SWITCHING","CERTIFICATE_DISCOVERY_COMPLEXITY"],"historical_markers":["ADAPTIVE_KEYMASTER_TOPA","MAD_LAB"],"factor_markers":["UNIFIED_V1"],"classification":"RETEST_WITH_NEW_CONTEXT","claim":"Keymaster already solved a mode-routing problem; the forgotten transfer is to route among exact representation/projection languages rather than only search trajectories.","action":"Generalize Keymaster to rank the frozen certificate/projection portfolio using prior-episode paid features, with COLD_FULL fallback preserving complete exact coverage."},
 {"id":"F15_SPIDER_TWO_LAYER_GRAPH","concepts":["ASSOCIATIVE_VS_EXACT_GRAPH","SHARED_DAG_REUSE"],"historical_markers":["ADAPTIVE_KEYMASTER_TOPA","MAD_LAB","C032_C047"],"factor_markers":["UNIFIED_V1"],"classification":"RESTORE_NOW","claim":"Spider relation discovery and HRain/proof-DAG reuse should be coupled but not conflated: associative edges are hypotheses, exact DAG edges are replayable semantics.","action":"Maintain two linked graph layers: advisory associative graph for candidate discovery and exact content-addressed proof DAG for state-changing operations."},
 {"id":"F16_M2R_RETRIEVE_PROJECTIONS_NOT_ONLY_HISTORY","concepts":["M2R_EXACT_RETRIEVAL","CONTEXT_PROJECTION","SHARED_DAG_REUSE"],"historical_markers":["M2R_STATE_SPECTRUM","MAD_LAB"],"factor_markers":["UNIFIED_V1"],"classification":"RETEST_WITH_NEW_CONTEXT","claim":"M2R can be more useful to Unified Kernel if retrieval keys resolve exact previously verified DAG nodes/projections under the same capability digest, not merely similar past actions.","action":"Add capability-bound exact-node/projection retrieval; similarity may rank retrieval candidates but exact semantic key and verifier replay are required for reuse."},
 {"id":"F17_FINGERPRINT_RANKS_LANGUAGE_NOT_TRUTH","concepts":["FINGERPRINT_STATE_SPECTRUM","CERTIFICATE_PORTFOLIO"],"historical_markers":["M2R_STATE_SPECTRUM","ADAPTIVE_KEYMASTER_TOPA"],"factor_markers":["UNIFIED_V1"],"classification":"RETEST_WITH_NEW_CONTEXT","claim":"State-spectrum/fingerprint machinery can characterize arithmetic states for representation-language ranking, but fingerprint similarity is not a certificate.","action":"Use fingerprints only as candidate-order features; freeze candidate scope and require exact projection/verification for authority."},
 {"id":"F18_DELAYED_LEARNING_FOR_REPRESENTATION_SELECTOR","concepts":["DELAYED_LEARNING","CERTIFICATE_PORTFOLIO"],"historical_markers":["ADAPTIVE_KEYMASTER_TOPA","META_REGISTRY"],"factor_markers":["UNIFIED_V1"],"classification":"RESTORE_NOW","claim":"ROOSTERS delayed-learning law must apply to the new representation-language selector exactly as it applies to search routing.","action":"Current episode can log utility but cannot raise current-episode language authority; updates become eligible only in future fingerprint epochs."},
 {"id":"F19_PLATEAU_SHOULD_CHANGE_LANGUAGE_NOT_BUDGET","concepts":["PLATEAU_MIRROR_REFLECTION","REPRESENTATION_BLOWUP","INTERFACE_BOUNDARY_WIDTH"],"historical_markers":["ADAPTIVE_KEYMASTER_TOPA","MAD_LAB","C032_C047"],"factor_markers":["UNIFIED_V1"],"classification":"RETEST_WITH_NEW_CONTEXT","claim":"Repeated plateau plus growing interface/representation volume is a stronger signal for changing representation language than for spending more search budget in the same language.","action":"Preregister a next-episode switch policy driven by paid plateau plus interface-profile growth; compare against same-language budget escalation."
 }
]

def norm(s):
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',s.lower())).strip()
def normalized_count_terms(text,terms):
    t=' '+norm(text)+' '
    return sum(t.count(' '+norm(x)+' ') for x in terms if norm(x))

def main(manifest,out):
    # append-only successor: patch matcher and vocabulary only for this run.
    base.count_terms=normalized_count_terms
    base.CONCEPTS.update(EXTRA_CONCEPTS)
    base.PREDEFINED_FINDINGS.extend(EXTRA_FINDINGS)
    base.audit(manifest,out)
    d=json.loads(Path(out).read_text())
    # Corrected lifecycle includes adaptive_history as prior context and normalized matching.
    rc=collections.defaultdict(lambda:collections.Counter())
    for s in d['sources']:
        for c,n in s['concept_hits'].items():rc[c][s['role']]+=n
    life=[]
    for c in base.CONCEPTS:
        prior=rc[c]['historical_mechanism']+rc[c]['historical_lineage']+rc[c]['adaptive_history']
        pre=rc[c]['factor_pre_v1'];cur=rc[c]['current_v1'];ad=rc[c]['adaptive_history']
        if prior and not pre and cur:state='PRIOR_NOT_IN_FACTOR_PRE_V1__RESTORED_OR_EXPLICIT_IN_V1'
        elif prior and pre and cur:state='SURVIVED_IN_FACTOR_AND_EXPLICIT_IN_V1'
        elif prior and not pre and not cur:state='PRIOR_NOT_PORTED_TO_FACTORING_V1'
        elif prior and pre and not cur:state='PRESENT_PRE_V1_NOT_EXPLICIT_IN_RESTORATION'
        else:state='NO_CLEAR_SIGNAL'
        life.append({'concept':c,'prior_hits':prior,'adaptive_hits':ad,'factor_pre_v1_hits':pre,'current_v1_hits':cur,'state':state})
    d['normalized_adaptive_lifecycle']=life
    d['successor_metadata']={'parent_run1_workflow':33267569610,'run1_preserved':True,'lexical_separator_normalization':True,'adaptive_history_added':True}
    Path(out).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'normalized_lifecycle':dict(collections.Counter(x['state'] for x in life)),'adaptive_findings':[{k:f.get(k) for k in ['id','classification','status','evidence_source_count']} for f in d['predefined_findings'] if f['id'].startswith('F1') and int(f['id'][1:3])>=13]},indent=2,ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',default='research/TOPA_SPIDER_SPIRAL_AUDIT_SOURCE_MANIFEST_V1_1_2026-08-29.json');ap.add_argument('--output',default='artifacts/TOPA_SPIDER_SPIRAL_AUDIT_RESULT_V1_1_2026-08-29.json');a=ap.parse_args();main(a.manifest,a.output)
