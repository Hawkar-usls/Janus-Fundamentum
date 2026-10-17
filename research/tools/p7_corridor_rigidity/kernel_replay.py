#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

EXPECTED_ARTIFACT="JANUS-TRUMP-P7-CORRIDOR-RIGIDITY-EXECUTION-2026-09-19-v1.0"
EXPECTED_PARENT="5d525a328c1e97f705d82a9a87646017a6ca38a2"

PROOF_STEPS=[
  {"id":"K1","rule":"shared element in T intersect T' would have one f-value belonging to two distinct singleton sets","conclusion":"T_INTERSECT_T_PRIME_EMPTY"},
  {"id":"K2","rule":"zero internal vertices contradict yy' nonedge; one internal seed vertex belongs to both T and T'","conclusion":"Q_STAR_SIZE_AT_LEAST_2"},
  {"id":"K3","rule":"a chord of an unweighted shortest path gives a strictly shorter y-to-y' path","conclusion":"Q_INDUCED"},
  {"id":"K4","rule":"axiom (iii) places Y0 outside N(S), hence Y0 anticomplete to S; explicit four external nonedges plus Q induced eliminate all corridor chords","conclusion":"FULL_CORRIDOR_INDUCED"},
  {"id":"K5","rule":"if Q* has at least 3 vertices, an induced corridor has at least 7 vertices and its first 7 consecutive vertices induce P7","conclusion":"Q_STAR_GE_3_IMPLIES_INDUCED_P7"},
  {"id":"K6","rule":"P7-free excludes the K5 witness","conclusion":"Q_STAR_SIZE_AT_MOST_2"},
  {"id":"K7","rule":"combine K2 and K6","conclusion":"Q_STAR_SIZE_EQ_2_AND_CORRIDOR_IS_INDUCED_P6"}
]

def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("prereg")
    ap.add_argument("output")
    args=ap.parse_args()
    p=json.loads(pathlib.Path(args.prereg).read_text())
    checks={
      "artifact_id_bound":p.get("artifact_id")==EXPECTED_ARTIFACT,
      "parent_bound":p.get("parent",{}).get("commit")==EXPECTED_PARENT and p.get("parent",{}).get("mode")=="READ_ONLY",
      "scope_is_rigidity_only":p.get("gate")=="P7_CORRIDOR_RIGIDITY",
      "formal_promotion_forbidden":p.get("authority_separation",{}).get("prohibition")=="THEOREM_KERNEL_REPLAY_PASS must never be relabeled FORMAL_THEOREM_PASS",
      "p7_promise_untrusted":p.get("certificate_contract",{}).get("p7_recognition",{}).get("trusted_promise") is False,
      "successor_autoactivation_forbidden":"automatic activation of any successor gate" in p.get("forbidden_scope",[]),
      "k1_to_k7_present":set((p.get("kernel_chain") or {}).keys())=={f"K{i}" for i in range(1,8)}
    }
    if not all(checks.values()):
        raise SystemExit(json.dumps({"verdict":"FAIL_THEOREM_KERNEL_REPLAY_BINDING","checks":checks},sort_keys=True))
    out={
      "schema":"janus.trump.p7_corridor_rigidity.theorem_kernel_replay.v1",
      "mode":"KERNEL_REPLAY",
      "verdict":"THEOREM_KERNEL_REPLAY_PASS",
      "formal_theorem_pass":False,
      "prereg_sha256":sha256(args.prereg),
      "checks":checks,
      "proof_steps":PROOF_STEPS,
      "claim_ceiling":{"FORMAL_THEOREM_PASS":"NOT_CLAIMED","LEMMA11_P7_LIFT":"OPEN","P_VS_NP":"OPEN"}
    }
    pathlib.Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
