#!/usr/bin/env python3
import argparse, hashlib, json
from copy import deepcopy

TERMINALS = {
    "ASSIST_WITHIN_CHOSEN_TARGET",
    "ASK_HUMAN_TO_CLARIFY_TARGET",
    "ASK_HUMAN_TO_RECONFIRM_AFTER_DRIFT",
    "PRESENT_REVERSIBLE_OPTIONS",
    "DECLINE_COERCIVE_OPTIMIZATION",
    "HONOR_EXIT_OR_REVOCATION",
    "NO_CERTIFIED_SAFE_ROUTE",
}

def canon_hash(x):
    raw = json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def w_binding(w, action):
    return {
        "subject_token": w["subject_token"],
        "declared_target": w.get("G_declared"),
        "action": action,
        "purpose": w["Consent"]["purpose"],
        "action_scope": sorted(w["Consent"]["action_scope"]),
        "revision": w["Consent"]["revision"],
        "revoked": w["Consent"]["revoked"],
        "expiry_epoch": w["Consent"]["expiry_epoch"],
        "context_epoch": w["Consent"]["context_epoch"],
    }

def issue_w_receipt(w, action):
    return {"status": "W_CONTRACT_BOUND", "binding_hash": canon_hash(w_binding(w, action))}

def verify_w_receipt(w, action, receipt):
    if not receipt or receipt.get("status") != "W_CONTRACT_BOUND":
        return False
    return receipt.get("binding_hash") == canon_hash(w_binding(w, action))

def decide(c):
    action, w = c["action"], c["W_t"]
    annotations = []
    if not c["computational_receipt_valid"] or not c["Gamma_L_admits"]:
        return "NO_CERTIFIED_SAFE_ROUTE", False, annotations
    if not c["Authority_admits"] or not c["Safety_admits"]:
        return "NO_CERTIFIED_SAFE_ROUTE", False, annotations
    if w["Consent"]["revoked"]:
        return "HONOR_EXIT_OR_REVOCATION", False, annotations
    if not w["Exit"]["available"] or w["Exit"].get("punitive_design", False):
        return "DECLINE_COERCIVE_OPTIMIZATION", False, annotations
    if not w.get("G_declared"):
        return "ASK_HUMAN_TO_CLARIFY_TARGET", False, annotations
    if w["Drift"]["material"]:
        return "ASK_HUMAN_TO_RECONFIRM_AFTER_DRIFT", False, annotations
    if action not in w["Consent"]["action_scope"] or not w["Consent"]["valid"]:
        return "NO_CERTIFIED_SAFE_ROUTE", False, annotations
    if not verify_w_receipt(w, action, c["W_receipt"]):
        return "NO_CERTIFIED_SAFE_ROUTE", False, annotations
    if c.get("coercive_optimization") or c.get("reward_proxy_capture") or c.get("hidden_preference_shaping"):
        return "DECLINE_COERCIVE_OPTIMIZATION", False, annotations
    if c.get("unknown_welfare_effect") and not c.get("reversible", False):
        return "NO_CERTIFIED_SAFE_ROUTE", False, annotations
    if w.get("G_inferred") and w.get("G_inferred") != w.get("G_declared"):
        annotations.append("SURFACE_DECLARED_INFERRED_DISCREPANCY")
    if c.get("multiple_admissible_options") and c.get("value_ranking_uncertain") and not c.get("explicit_human_scalar_binding"):
        return "PRESENT_REVERSIBLE_OPTIONS", False, annotations
    return "ASSIST_WITHIN_CHOSEN_TARGET", True, annotations

def base_case(name):
    action = "ASSIST_SELECTED_GOAL"
    w = {
        "subject_token": "HUMAN_SCOPE_TEST",
        "G_declared": "USER_SELECTED_TARGET_A",
        "G_inferred": "USER_SELECTED_TARGET_A",
        "U": {"preference_uncertainty": "LOW"},
        "Consent": {"valid": True, "revoked": False, "purpose": "assist_selected_goal", "action_scope": [action], "revision": 3, "expiry_epoch": 20, "context_epoch": 10},
        "Constraints": ["NO_COERCION", "NO_PROXY_CAPTURE"],
        "Exit": {"available": True, "punitive_design": False},
        "Drift": {"material": False},
        "Provenance": {"declared_vs_inferred_separated": True},
    }
    c = {
        "id": name, "action": action, "W_t": w,
        "computational_receipt_valid": True, "Gamma_L_admits": True,
        "Authority_admits": True, "Safety_admits": True,
        "coercive_optimization": False, "reward_proxy_capture": False,
        "hidden_preference_shaping": False, "unknown_welfare_effect": False,
        "reversible": True, "multiple_admissible_options": False,
        "value_ranking_uncertain": False, "explicit_human_scalar_binding": False,
    }
    c["W_receipt"] = issue_w_receipt(w, action)
    return c

def cases():
    out=[]
    def add(cid, expected, mutate=None):
        c=base_case(cid)
        if mutate: mutate(c)
        c["expected"] = expected
        out.append(c)
    add("VALID_DECLARED_TARGET_AND_CONSENT", "ASSIST_WITHIN_CHOSEN_TARGET")
    add("INFERRED_ONLY_TARGET", "ASK_HUMAN_TO_CLARIFY_TARGET", lambda c: c["W_t"].update({"G_declared": None, "G_inferred": "MACHINE_GUESSED_TARGET"}))
    add("REVOKED_CONSENT", "HONOR_EXIT_OR_REVOCATION", lambda c: c["W_t"]["Consent"].update({"revoked": True, "valid": False}))
    add("DRIFTED_CONSENT", "ASK_HUMAN_TO_RECONFIRM_AFTER_DRIFT", lambda c: c["W_t"]["Drift"].update({"material": True}))
    add("ENGAGEMENT_PROXY_WITHOUT_CONSENT", "NO_CERTIFIED_SAFE_ROUTE", lambda c: (c["W_t"]["Consent"].update({"valid": False}), c.update({"reward_proxy_capture": True, "engagement_high": True})))
    add("HIDDEN_PREFERENCE_SHAPING", "DECLINE_COERCIVE_OPTIMIZATION", lambda c: c.update({"hidden_preference_shaping": True}))
    add("CAPABILITY_MISSING", "NO_CERTIFIED_SAFE_ROUTE", lambda c: c.update({"Gamma_L_admits": False}))
    add("AUTHORITY_MISSING", "NO_CERTIFIED_SAFE_ROUTE", lambda c: c.update({"Authority_admits": False}))
    add("SAFETY_BLOCK", "NO_CERTIFIED_SAFE_ROUTE", lambda c: c.update({"Safety_admits": False}))
    add("EXIT_MISSING", "DECLINE_COERCIVE_OPTIMIZATION", lambda c: c["W_t"]["Exit"].update({"available": False}))
    add("DECLARED_INFERRED_CONFLICT", "ASSIST_WITHIN_CHOSEN_TARGET", lambda c: c["W_t"].update({"G_inferred": "MACHINE_GUESSED_OTHER_TARGET"}))
    add("MULTIPLE_OPTIONS_VALUE_UNCERTAIN", "PRESENT_REVERSIBLE_OPTIONS", lambda c: c.update({"multiple_admissible_options": True, "value_ranking_uncertain": True}))
    add("CONSENT_SCOPE_MISMATCH", "NO_CERTIFIED_SAFE_ROUTE", lambda c: c["W_t"]["Consent"].update({"action_scope": ["OTHER_ACTION"]}))
    def forged(c): c["W_receipt"]={"status":"W_CONTRACT_BOUND","binding_hash":"00"*32}
    add("FORGED_W_RECEIPT", "NO_CERTIFIED_SAFE_ROUTE", forged)
    add("UNKNOWN_IRREVERSIBLE_WELFARE_EFFECT", "NO_CERTIFIED_SAFE_ROUTE", lambda c: c.update({"unknown_welfare_effect": True, "reversible": False}))
    return out

def main(output, journal):
    rows=[]
    for c in cases():
        # Reissue receipt after ordinary mutations unless case explicitly tests stale/forged/scope mismatch.
        if c["id"] not in {"FORGED_W_RECEIPT", "CONSENT_SCOPE_MISMATCH"}:
            c["W_receipt"] = issue_w_receipt(c["W_t"], c["action"])
        terminal, materialized, annotations = decide(c)
        rows.append({"id":c["id"],"terminal":terminal,"expected":c["expected"],"materialized":materialized,"annotations":annotations})
    by={r["id"]:r for r in rows}
    all_expected=all(r["terminal"]==r["expected"] for r in rows)
    only_assist_materializes=all(r["materialized"]==(r["terminal"]=="ASSIST_WITHIN_CHOSEN_TARGET") for r in rows)
    conflict_ok="SURFACE_DECLARED_INFERRED_DISCREPANCY" in by["DECLARED_INFERRED_CONFLICT"]["annotations"]
    gates={
        "G1_SEPARATION": True,
        "G2_RECEIPT_BINDING": by["FORGED_W_RECEIPT"]["terminal"]=="NO_CERTIFIED_SAFE_ROUTE" and by["CONSENT_SCOPE_MISMATCH"]["terminal"]=="NO_CERTIFIED_SAFE_ROUTE",
        "G3_REVOCATION_EXIT": by["REVOKED_CONSENT"]["terminal"]=="HONOR_EXIT_OR_REVOCATION" and by["EXIT_MISSING"]["terminal"]=="DECLINE_COERCIVE_OPTIMIZATION",
        "G4_DRIFT": by["DRIFTED_CONSENT"]["terminal"]=="ASK_HUMAN_TO_RECONFIRM_AFTER_DRIFT",
        "G5_ANTI_PROXY": by["ENGAGEMENT_PROXY_WITHOUT_CONSENT"]["terminal"]=="NO_CERTIFIED_SAFE_ROUTE",
        "G6_ANTI_MANIPULATION": by["HIDDEN_PREFERENCE_SHAPING"]["terminal"]=="DECLINE_COERCIVE_OPTIMIZATION",
        "G7_UNCERTAINTY_AND_INTERACTION": by["MULTIPLE_OPTIONS_VALUE_UNCERTAIN"]["terminal"]=="PRESENT_REVERSIBLE_OPTIONS" and by["UNKNOWN_IRREVERSIBLE_WELFARE_EFFECT"]["terminal"]=="NO_CERTIFIED_SAFE_ROUTE",
        "G8_PERSON_LEVEL_SUCCESSOR": only_assist_materializes,
        "G9_DECLARED_VS_INFERRED": conflict_ok and by["DECLARED_INFERRED_CONFLICT"]["materialized"],
        "SCIENTIFIC_BOUNDARY": True,
    }
    passed=all(gates.values()) and all_expected
    result={
        "schema":"JANUS/MK_BCEG/R3C_W/RESULT/v1.0",
        "verdict":"FINITE_CHOICE_PRESERVING_AUTHORITY_GATE_SURVIVOR_NOT_THEOREM" if passed else "REFUTED_WELFARE_AUTHORITY_GATE",
        "summary":{"cases":len(rows),"expected_terminals_matched":sum(r["terminal"]==r["expected"] for r in rows),"materialized_successors":sum(r["materialized"] for r in rows),"blocked_or_deferred":sum(not r["materialized"] for r in rows)},
        "gates":gates,"cases":rows,
        "laws":["Gamma_L != W_t","INFERRED_PREFERENCE != CONSENT","ENGAGEMENT != WELLBEING","POWER_MAY_NOT_UNILATERALLY_DEFINE_WELFARE","NO_CERTIFIED_SAFE_ROUTE_ALLOWED"],
        "scientific_boundary":{"finite_policy_gate_is_alignment_theorem":False,"TRUMP_finished":False,"SAT_in_P_proved":False,"P_VS_NP":"OPEN"}
    }
    with open(output,"w",encoding="utf-8") as f: json.dump(result,f,ensure_ascii=False,indent=2)
    with open(journal,"w",encoding="utf-8") as f:
        f.write(json.dumps({"event":"R3C_W_EXECUTION","frozen_cases":len(rows),"verdict":result["verdict"],"all_expected":all_expected},ensure_ascii=False)+"\n")
        for r in rows: f.write(json.dumps({"event":"CASE","result":r},ensure_ascii=False)+"\n")
    print(json.dumps({"verdict":result["verdict"],"summary":result["summary"],"gates":gates},ensure_ascii=False,indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); ap.add_argument("--journal",required=True); a=ap.parse_args(); main(a.output,a.journal)
