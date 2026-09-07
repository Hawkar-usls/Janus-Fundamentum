from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

POLICY_ID = "TRUMP_PROOF_STATE_MACHINE_V1_0"

ALLOWED_UNGUARDED = {
    ("NO_WITNESS", "WITNESS_FOUND"),
    ("WITNESS_FOUND", "WITNESS_VERIFIED"),
    ("HYPOTHESIS", "EMPIRICAL_PASS"),
    ("HYPOTHESIS", "COUNTEREXAMPLE_FOUND"),
    ("EMPIRICAL_PASS", "COUNTEREXAMPLE_FOUND"),
    ("COUNTEREXAMPLE_FOUND", "CLAIM_REFUTED"),
    ("COUNTEREXAMPLE_FOUND", "COUNTEREXAMPLE_VERIFIED"),
    ("NO_SEARCH", "NO_COUNTEREXAMPLE_FOUND_ON_FROZEN_DOMAIN"),
    ("NO_SEARCH", "COUNTEREXAMPLE_FOUND"),
    ("NO_COUNTEREXAMPLE_FOUND_ON_FROZEN_DOMAIN", "COUNTEREXAMPLE_FOUND"),
    ("UNTRACKED", "REPLAYABLE"),
    ("REPLAYABLE", "ARTIFACT_HASHED"),
    ("ARTIFACT_HASHED", "FAIL_CLOSED_VERIFIED"),
    ("FAIL_CLOSED_VERIFIED", "DUAL_LEDGER_SEALED"),
    ("UNTESTED", "LOCAL_EXACTNESS"),
    ("LOCAL_EXACTNESS", "RECONSTRUCTION_VERIFIED"),
    ("NO_COMPLEXITY_CERTIFICATE", "EMPIRICAL_POLY_RUNTIME"),
    ("NO_COMPLEXITY_CERTIFICATE", "LOCAL_POLY_BOUND"),
    ("UNSPECIFIED_DOMAIN", "FINITE_DOMAIN"),
    ("FINITE_DOMAIN", "FROZEN_FAMILY_COVERAGE"),
    ("UNSPECIFIED_DOMAIN", "UNIVERSAL_DOMAIN_SPECIFIED"),
    ("HYPOTHESIS", "PROOF_CANDIDATE"),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path):
    raw = path.read_bytes()
    return json.loads(raw), sha256_bytes(raw)


def validate(policy: dict, manifest: dict) -> dict:
    violations = []
    notes = []

    if policy.get("policy_id") != POLICY_ID:
        violations.append({"kind": "POLICY_ID_DRIFT", "observed": policy.get("policy_id")})
    if manifest.get("policy_id") != POLICY_ID:
        violations.append({"kind": "MANIFEST_POLICY_ID_DRIFT", "observed": manifest.get("policy_id")})

    required = policy["promotion_manifest_contract"]["required_fields"]
    for field in required:
        if field not in manifest:
            violations.append({"kind": "MISSING_REQUIRED_MANIFEST_FIELD", "field": field})

    certs = manifest.get("certificates", [])
    cert_by_id = {}
    valid_types = set(policy.get("certificate_types", []))
    for cert in certs:
        cid = cert.get("id")
        if not cid or cid in cert_by_id:
            violations.append({"kind": "INVALID_OR_DUPLICATE_CERTIFICATE_ID", "id": cid})
            continue
        cert_by_id[cid] = cert
        if cert.get("type") not in valid_types:
            violations.append({"kind": "UNKNOWN_CERTIFICATE_TYPE", "id": cid, "type": cert.get("type")})
        for f in ("uri_or_path", "sha256_or_commit"):
            if not cert.get(f):
                violations.append({"kind": "INCOMPLETE_CERTIFICATE", "id": cid, "field": f})

    forbidden = {(r["from"], r["to"]): r for r in policy.get("forbidden_direct_promotions", [])}
    guards = {r["to"]: set(r["requires_all"]) for r in policy.get("guarded_promotions", [])}
    passed_promotions = []

    for i, promo in enumerate(manifest.get("requested_promotions", [])):
        src = promo.get("from")
        dst = promo.get("to")
        scope = promo.get("scope")
        refs = promo.get("certificate_refs", [])
        if not src or not dst or not scope or not isinstance(refs, list):
            violations.append({"kind": "MALFORMED_PROMOTION", "index": i})
            continue

        if (src, dst) in forbidden:
            violations.append({
                "kind": "FORBIDDEN_DIRECT_PROMOTION",
                "index": i,
                "from": src,
                "to": dst,
                "reason": forbidden[(src, dst)]["reason"],
            })
            continue

        referenced = []
        missing_refs = []
        for ref in refs:
            if ref not in cert_by_id:
                missing_refs.append(ref)
            else:
                referenced.append(cert_by_id[ref])
        if missing_refs:
            violations.append({"kind": "UNKNOWN_CERTIFICATE_REFERENCE", "index": i, "refs": missing_refs})
            continue

        if dst in guards:
            got_types = {c.get("type") for c in referenced}
            missing_types = sorted(guards[dst] - got_types)
            if missing_types:
                violations.append({
                    "kind": "MISSING_PROMOTION_GUARD_CERTIFICATES",
                    "index": i,
                    "to": dst,
                    "missing_types": missing_types,
                })
                continue
            if "INDEPENDENT_VERIFICATION_RECEIPT" in guards[dst]:
                iv = [c for c in referenced if c.get("type") == "INDEPENDENT_VERIFICATION_RECEIPT"]
                if not iv or not all(c.get("independent") is True for c in iv):
                    violations.append({"kind": "INDEPENDENCE_GUARD_FAILED", "index": i, "to": dst})
                    continue
        elif (src, dst) not in ALLOWED_UNGUARDED:
            violations.append({"kind": "UNKNOWN_PROMOTION_FAIL_CLOSED", "index": i, "from": src, "to": dst})
            continue

        passed_promotions.append({"index": i, "from": src, "to": dst, "scope": scope})

    events = manifest.get("events", [])
    event_types = [str(e.get("type")) if isinstance(e, dict) else str(e) for e in events]
    claims = manifest.get("output_claims", [])
    claim_strings = [json.dumps(c, sort_keys=True) if isinstance(c, dict) else str(c) for c in claims]

    has_counterexample = any(x in {"COUNTEREXAMPLE_FOUND", "COUNTEREXAMPLE_VERIFIED"} for x in event_types)
    if has_counterexample:
        for claim in claim_strings:
            if "GLOBAL_CLAIM_PROVED" in claim or "UNIVERSAL_COVERAGE_PROVED" in claim:
                violations.append({"kind": "COUNTEREXAMPLE_CONFLICTS_WITH_GLOBAL_POSITIVE_CLAIM", "claim": claim})

    if "UNKNOWN_RESOURCE_LIMIT" in event_types:
        for claim in claim_strings:
            if "NEGATIVE_RESULT" in claim or "COUNTEREXAMPLE_FOUND" in claim or "PROVED" in claim:
                violations.append({"kind": "RESOURCE_LIMIT_ILLEGAL_PROMOTION", "claim": claim})

    theorem_targets = {"SAT_IN_P_PROVED", "P_EQ_NP_PROVED"}
    passed_targets = {p["to"] for p in passed_promotions}
    fw = manifest.get("firewall", {})
    if "SAT_IN_P_PROVED" not in passed_targets and fw.get("SAT_IN_P") != "NOT_PROVED":
        violations.append({"kind": "SAT_IN_P_FIREWALL_DRIFT", "observed": fw.get("SAT_IN_P")})
    if "P_EQ_NP_PROVED" not in passed_targets and fw.get("P_VS_NP") != "OPEN":
        violations.append({"kind": "P_VS_NP_FIREWALL_DRIFT", "observed": fw.get("P_VS_NP")})
    if not theorem_targets.intersection(passed_targets) and fw.get("TRUMP_finished") is not False:
        violations.append({"kind": "TRUMP_FINISHED_PREMATURE", "observed": fw.get("TRUMP_finished")})

    return {
        "validator": "TRUMP_PROOF_STATE_MACHINE_VALIDATOR_V1",
        "policy_id": POLICY_ID,
        "gate": manifest.get("gate"),
        "status": "PASS" if not violations else "FAIL_CLOSED",
        "promotion_count_requested": len(manifest.get("requested_promotions", [])),
        "promotion_count_passed": len(passed_promotions),
        "passed_promotions": passed_promotions,
        "violation_count": len(violations),
        "violations": violations,
        "notes": notes,
        "interpretation": "PASS_MEANS_ONLY_CLAIMS_DO_NOT_EXCEED_SUPPLIED_CERTIFICATES__NOT_A_SCIENTIFIC_PROOF",
    }


def self_test(policy: dict) -> dict:
    base = {
        "policy_id": POLICY_ID,
        "gate": "SELF_TEST",
        "events": [],
        "requested_promotions": [],
        "certificates": [],
        "output_claims": [],
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
    }

    cases = []

    m = dict(base)
    m["requested_promotions"] = [{"from": "SAT_MODEL_FOUND", "to": "P_EQ_NP_PROVED", "scope": "SELF_TEST", "certificate_refs": []}]
    r = validate(policy, m)
    cases.append({"name": "sat_model_cannot_promote_to_p_eq_np", "expected": "FAIL_CLOSED", "observed": r["status"]})

    m = dict(base)
    m["events"] = [{"type": "UNKNOWN_RESOURCE_LIMIT"}]
    m["output_claims"] = ["NEGATIVE_RESULT"]
    r = validate(policy, m)
    cases.append({"name": "resource_limit_is_not_negative", "expected": "FAIL_CLOSED", "observed": r["status"]})

    m = dict(base)
    m["requested_promotions"] = [{"from": "HYPOTHESIS", "to": "EMPIRICAL_PASS", "scope": "FROZEN_DOMAIN", "certificate_refs": []}]
    m["output_claims"] = ["LOCAL_FINITE_PASS_ONLY"]
    r = validate(policy, m)
    cases.append({"name": "local_empirical_pass_allowed", "expected": "PASS", "observed": r["status"]})

    required = policy["guarded_promotions"]
    poly_req = next(x["requires_all"] for x in required if x["to"] == "ASYMPTOTIC_POLYNOMIAL_BOUND_PROVED")
    certs = []
    refs = []
    for i, typ in enumerate(poly_req):
        cid = f"c{i}"
        refs.append(cid)
        certs.append({
            "id": cid,
            "type": typ,
            "uri_or_path": f"selftest/{cid}",
            "sha256_or_commit": "0" * 64,
            "independent": True if typ == "INDEPENDENT_VERIFICATION_RECEIPT" else False,
        })
    m = dict(base)
    m["certificates"] = certs
    m["requested_promotions"] = [{"from": "LOCAL_POLY_BOUND", "to": "ASYMPTOTIC_POLYNOMIAL_BOUND_PROVED", "scope": "DECLARED_UNIVERSAL_DOMAIN", "certificate_refs": refs}]
    r = validate(policy, m)
    cases.append({"name": "guarded_poly_promotion_with_full_bundle_allowed", "expected": "PASS", "observed": r["status"]})

    failures = [c for c in cases if c["expected"] != c["observed"]]
    return {"status": "PASS" if not failures else "FAIL", "cases": cases, "failure_count": len(failures), "failures": failures}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", type=Path, required=True)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    policy, policy_sha = load_json(args.policy)

    if args.self_test:
        result = self_test(policy)
        result["policy_sha256"] = policy_sha
    else:
        if args.manifest is None:
            raise SystemExit("--manifest required unless --self-test")
        manifest, manifest_sha = load_json(args.manifest)
        result = validate(policy, manifest)
        result["policy_sha256"] = policy_sha
        result["manifest_sha256"] = manifest_sha

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
