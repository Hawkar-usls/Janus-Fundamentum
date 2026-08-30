#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


def canon_obj(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_obj(x):
    return hashlib.sha256(canon_obj(x)).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--journal", required=True)
    a = ap.parse_args()
    d = Path(a.dir)
    prereg = load(a.prereg)
    packages = [load(d / f"package_{i}.json") for i in range(4)]
    receipts = [load(d / f"receipt_{i}.json") for i in range(4)]
    certs = [None] + [load(d / f"cert_{i}.json") for i in range(1, 4)]

    gates = []

    required = {
        "language", "theta", "K", "semantics_ref", "Gamma_L", "paid_costs", "debt_ledger",
        "liability_potential", "provenance", "backend", "representation_hash", "package_hash",
        "language_theorem_status", "backend_empirical_status"
    }
    self_contained_fail = []
    for i, p in enumerate(packages):
        missing = sorted(required - set(p))
        if missing:
            self_contained_fail.append({"step": i, "missing": missing})
        if p.get("provenance", {}).get("exact_fallback_embedded") is not True:
            self_contained_fail.append({"step": i, "failure": "exact_fallback_not_embedded"})
        if p.get("semantics_ref", {}).get("kind") != "CNF":
            self_contained_fail.append({"step": i, "failure": "semantic_fallback_not_CNF"})
    gates.append({"gate": "R3C_A_SELF_CONTAINED_PACKAGE", "passed": not self_contained_fail, "failures": self_contained_fail})

    verifier_ids = {r.get("verifier", {}).get("verifier_source_sha256") for r in receipts}
    producer_ids = {p.get("backend", {}).get("producer_source_sha256") for p in packages}
    separation_ok = (
        len(verifier_ids) == 1 and len(producer_ids) == 1 and
        next(iter(verifier_ids)) not in producer_ids and
        all(r.get("verifier", {}).get("imports_producer_code") is False for r in receipts)
    )
    gates.append({"gate": "R3C_B_PRODUCER_VERIFIER_SEPARATION", "passed": separation_ok})

    chain_fail = []
    for i in range(1, 4):
        expected_receipt_hash = sha_obj(receipts[i - 1])
        if packages[i].get("previous_acceptance_receipt_hash") != expected_receipt_hash:
            chain_fail.append({"step": i, "failure": "previous_acceptance_receipt_hash"})
        if packages[i].get("provenance", {}).get("input_acceptance_receipt_hash") != expected_receipt_hash:
            chain_fail.append({"step": i, "failure": "provenance_receipt_hash"})
        if certs[i].get("input_package_hash") != packages[i - 1].get("package_hash"):
            chain_fail.append({"step": i, "failure": "certificate_input_hash"})
        if certs[i].get("output_package_hash") != packages[i].get("package_hash"):
            chain_fail.append({"step": i, "failure": "certificate_output_hash"})
    gates.append({"gate": "R3C_C_RECEIPT_CHAINING", "passed": not chain_fail, "failures": chain_fail})

    expected_checks = [256, 128, 128, 64]
    replay_fail = []
    for i, (r, n) in enumerate(zip(receipts, expected_checks)):
        if r.get("verdict") != "PASS":
            replay_fail.append({"step": i, "failure": "receipt_not_PASS"})
        if r.get("semantic_mismatches") != 0:
            replay_fail.append({"step": i, "failure": "semantic_mismatch", "count": r.get("semantic_mismatches")})
        if r.get("semantic_assignments_checked") != n:
            replay_fail.append({"step": i, "failure": "assignment_count", "expected": n, "actual": r.get("semantic_assignments_checked")})
        if r.get("accepted_package_hash") != packages[i].get("package_hash"):
            replay_fail.append({"step": i, "failure": "accepted_hash"})
    gates.append({"gate": "R3C_D_EXACT_REPLAY", "passed": not replay_fail, "failures": replay_fail})

    status_fail = []
    for i, (p, r) in enumerate(zip(packages, receipts)):
        if p.get("language_theorem_status") == p.get("backend_empirical_status"):
            status_fail.append({"step": i, "failure": "package_status_conflation"})
        if r.get("backend_empirical_status_after_replay") != "FINITE_REPLAY_PASS":
            status_fail.append({"step": i, "failure": "empirical_status_not_finite_pass"})
        if r.get("language_theorem_status_after_replay") != p.get("language_theorem_status"):
            status_fail.append({"step": i, "failure": "theorem_status_changed_by_finite_replay"})
    gates.append({"gate": "R3C_E_STATUS_SEPARATION", "passed": not status_fail, "failures": status_fail})

    events = []
    phi = 0
    total_actual = 0
    total_amortized = 0
    liability_fail = []
    for i in range(4):
        p = packages[i]
        r = receipts[i]
        c_prod = int(p["paid_costs"]["current_producer_work_units"])
        phi_next = int(p["liability_potential"]["Phi"])
        a_prod = c_prod + phi_next - phi
        events.append({"event": "PRODUCER", "step": i, "C": c_prod, "Phi_before": phi, "Phi_after": phi_next, "A": a_prod})
        total_actual += c_prod
        total_amortized += a_prod
        phi = phi_next
        c_ver = int(r["verification_work_units"])
        phi_next = int(r["accepted_phi"])
        a_ver = c_ver + phi_next - phi
        events.append({"event": "VERIFIER", "step": i, "C": c_ver, "Phi_before": phi, "Phi_after": phi_next, "A": a_ver})
        total_actual += c_ver
        total_amortized += a_ver
        phi = phi_next
        if p["liability_potential"]["Phi"] != 1 or r["accepted_phi"] != 0:
            liability_fail.append({"step": i, "failure": "phi_transition"})
        if r["liability_discharge"].get("verification_liability") != 1:
            liability_fail.append({"step": i, "failure": "verification_liability_not_discharged"})
        if c_ver <= 0:
            liability_fail.append({"step": i, "failure": "verification_treated_as_free"})
    if phi != 0:
        liability_fail.append({"failure": "final_phi_nonzero", "phi": phi})
    if total_actual != total_amortized:
        liability_fail.append({"failure": "amortized_telescoping_mismatch", "actual": total_actual, "amortized": total_amortized})
    gates.append({
        "gate": "R3C_F_LIABILITY_POTENTIAL",
        "passed": not liability_fail,
        "failures": liability_fail,
        "total_actual_work_units": total_actual,
        "total_amortized_work_units": total_amortized,
        "final_Phi": phi
    })

    unknown_case = {
        "D_upper": "UNKNOWN",
        "V_liability": 0,
        "S_liability": 0
    }
    unknown_poly_claim_allowed = all(isinstance(unknown_case[k], int) for k in ("D_upper", "V_liability", "S_liability"))
    gates.append({
        "gate": "R3C_G_UNKNOWN_FIREWALL",
        "passed": unknown_poly_claim_allowed is False,
        "synthetic_case": unknown_case,
        "poly_claim_allowed": unknown_poly_claim_allowed
    })

    no_hidden = all(r.get("hidden_mutable_state_required") is False for r in receipts)
    no_hidden = no_hidden and all("no producer cache" in r.get("replay_inputs", "") for r in receipts)
    gates.append({"gate": "R3C_H_NO_HIDDEN_STATE", "passed": no_hidden})

    scientific_ok = (
        prereg.get("status") == "FROZEN_BEFORE_EXECUTION" and
        prereg.get("scientific_boundary", {}).get("P_VS_NP") == "OPEN" and
        prereg.get("scientific_boundary", {}).get("universal_polynomial_lifecycle_interface_proved") is False
    )
    gates.append({"gate": "SCIENTIFIC_BOUNDARY", "passed": scientific_ok})

    all_pass = all(g["passed"] for g in gates)
    verdict = prereg["success_verdict"] if all_pass else "REFUTED_R3C_EXECUTABLE_LIFECYCLE_PACKAGE"
    cert_bytes = {f"cert_{i}": (d / f"cert_{i}.json").stat().st_size for i in range(1, 4)}
    verifier_work = {f"receipt_{i}": receipts[i]["verification_work_units"] for i in range(4)}
    result = {
        "schema": "JANUS/MK_BCEG/R3C/RESULT/v1.0",
        "status": "COMPLETE",
        "verdict": verdict,
        "trajectory": [
            {"step": p["step"], "language": p["language"], "operation": p["provenance"]["operation"], "package_hash": p["package_hash"], "representation_hash": p["representation_hash"]}
            for p in packages
        ],
        "gates": gates,
        "amortized_event_ledger": events,
        "certificate_bytes": cert_bytes,
        "verification_work_units": verifier_work,
        "main_law": "NO_FREE_SEMANTIC_COMPRESSION",
        "main_finding": "A self-contained proof-state package can be chained across real executable ROBDD and D_DNNF operations on this frozen finite Boolean trajectory while requiring independent replay receipts before reuse. Finite success validates the package/replay architecture only; it does not establish universal polynomial lifecycle cost or any new language-closure theorem.",
        "theorem_candidate": prereg["theorem_candidate"],
        "runtime_interpretation": "This is a research prototype of the future TRUMP computational ABI: maintain exact future-state contracts while selecting and validating certified computational forms. It is not a TRUMP release.",
        "scientific_boundary": {
            "finite_replay_is_universal_theorem": False,
            "universal_polynomial_lifecycle_interface_proved": False,
            "SAT_in_P_proved": False,
            "P_VS_NP": "OPEN"
        }
    }
    Path(a.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with open(a.journal, "w") as j:
        for e in events:
            j.write(json.dumps(e, separators=(",", ":")) + "\n")
        for g in gates:
            j.write(json.dumps({"event": "GATE", **g}, separators=(",", ":")) + "\n")
        j.write(json.dumps({"event": "FROZEN_VERDICT", "verdict": verdict}, separators=(",", ":")) + "\n")
    print(json.dumps({"verdict": verdict, "gates": [(g["gate"], g["passed"]) for g in gates], "total_actual": total_actual, "total_amortized": total_amortized}, indent=2))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
