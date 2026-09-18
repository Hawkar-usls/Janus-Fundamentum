from __future__ import annotations

import hashlib
import json
import secrets
import sys
from pathlib import Path

PAIR=[1,2]
BOUNDARY=[3,4]
PREREG_BLOB="a7247977e8834a751522275f2592bdeb35ca2abb"

# Opaque public IDs intentionally do not encode semantic class.
MAPPING={
    "CHAL_001":"XNOR_CORRELATED",
    "CHAL_002":"UNARY_POSITIVE_CONTROL",
    "CHAL_003":"XOR_CORRELATED",
    "CHAL_004":"CONJUNCTION_CONTROL",
}

RELATIONS={
    "UNARY_POSITIVE_CONTROL":{
        "true_beta":[(1,0),(1,1)],
        "expected_semantic_class":"R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS",
        "expected_candidate_verdict":"FAIL_UNARY_FACTORIZATION",
        "expected_correlated":False,
    },
    "CONJUNCTION_CONTROL":{
        "true_beta":[(1,1)],
        "expected_semantic_class":"R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS",
        "expected_candidate_verdict":"FAIL_UNARY_FACTORIZATION",
        "expected_correlated":False,
    },
    "XOR_CORRELATED":{
        "true_beta":[(0,1),(1,0)],
        "expected_semantic_class":"R_C_CORRELATED",
        "expected_candidate_verdict":"PASS_LOCAL_EXACT_INTERFACE_NONTRIVIAL_CORRELATED",
        "expected_correlated":True,
    },
    "XNOR_CORRELATED":{
        "true_beta":[(0,0),(1,1)],
        "expected_semantic_class":"R_C_CORRELATED",
        "expected_candidate_verdict":"PASS_LOCAL_EXACT_INTERFACE_NONTRIVIAL_CORRELATED",
        "expected_correlated":True,
    },
}

def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def rows_for(cell_var,true_beta):
    rows=[]
    for x in (0,1):
        for b1,b2 in true_beta:
            rows.append([x,b1,b2])
    return rows

def bundle(specimen_id, class_id):
    meta=RELATIONS[class_id]
    constraints=[
        {"scope":[1,3,4],"allowed":rows_for(1,meta["true_beta"])},
        {"scope":[2,3,4],"allowed":rows_for(2,meta["true_beta"])},
    ]
    payload={
        "format":"MANTEQUILLA_PHASE_IIB_WAVE1_CONTROLLED_REDUCED_CSP_v1",
        "source":{
            "source_id":specimen_id,
            "evidence_class":"CONTROLLED_MECHANISM_CHALLENGE_EVIDENCE"
        },
        "preprocessing":{
            "controlled_challenge":True,
            "reduced_variables":4,
            "reduced_constraints":2
        },
        "frozen_witness":{
            "cell":PAIR,
            "group":"S_2",
            "generator_transposition":PAIR,
            "expected_local_constraint_count":2,
            "expected_boundary_variables":BOUNDARY,
            "authority":"PHASE_IIB_WAVE1_PREREG_BLOB:"+PREREG_BLOB
        },
        "firewall":{
            "natural_discovery_evidence":False,
            "ground_truth_relation_not_in_public_bundle":True,
            "candidate_may_read_only_this_bundle":True
        },
        "reduced_csp":{
            "variables":[1,2,3,4],
            "constraints":constraints
        }
    }
    out=dict(payload)
    out["payload_sha256"]=sha(payload)
    return out

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: prepare_challenges.py OUTPUT_DIR")
    root=Path(sys.argv[1])
    pub=root/"public"
    priv=root/"private"
    pub.mkdir(parents=True,exist_ok=True)
    priv.mkdir(parents=True,exist_ok=True)

    gt={"wave":"PHASE_IIB_WAVE1","boundary_order":BOUNDARY,"specimens":{}}
    bundle_hashes={}
    for sid in sorted(MAPPING):
        cid=MAPPING[sid]
        b=bundle(sid,cid)
        p=pub/f"{sid}.json"
        p.write_text(json.dumps(b,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        bundle_hashes[sid]=b["payload_sha256"]
        meta=RELATIONS[cid]
        truth={"00":False,"01":False,"10":False,"11":False}
        for beta in meta["true_beta"]:
            truth["".join(map(str,beta))]=True
        gt["specimens"][sid]={
            "class_id":cid,
            "truth_table":truth,
            "expected_semantic_class":meta["expected_semantic_class"],
            "expected_candidate_verdict":meta["expected_candidate_verdict"],
            "expected_correlated":meta["expected_correlated"]
        }

    salt=secrets.token_hex(32)
    private={"salt":salt,"ground_truth":gt}
    commitment=sha(private)
    (priv/"ground_truth.json").write_text(json.dumps(private,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    receipt={
        "artifact_id":"JANUS-TRUMP-WALL-MANTEQUILLA-PHASE-IIB-WAVE1-CONTROLLED-CHALLENGE-COMMITMENT-v1",
        "prereg_blob":PREREG_BLOB,
        "public_bundle_payload_sha256":bundle_hashes,
        "ground_truth_commitment_sha256":commitment,
        "ground_truth_revealed_to_constructor":False,
        "all_four_bundles_built_before_candidate_execution":True
    }
    (pub/"commitment.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"bundle_hashes":bundle_hashes,"ground_truth_commitment_sha256":commitment},sort_keys=True))

if __name__=="__main__":
    main()
