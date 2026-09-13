from __future__ import annotations
import copy, json, tempfile
from pathlib import Path
from q_boundary_independent_checker import check, REPO, CERT_REL, RECEIPT_REL


def rejected(cert_dir, obj):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "receipt.json"
        path.write_text(json.dumps(obj), encoding="utf-8")
        try:
            result = check(cert_dir, path)
        except Exception:
            return True
        return result["status"] == "FAIL_BINDING_OR_CHECKER"


def main():
    cert_dir = REPO / CERT_REL
    base = json.loads((REPO / RECEIPT_REL).read_text(encoding="utf-8"))
    cases = []

    x = copy.deepcopy(base)
    x["boundaries"][0]["live_node_count"] += 1
    cases.append(("LIVE_COUNT_PLUS_ONE", rejected(cert_dir, x)))

    x = copy.deepcopy(base)
    x["boundaries"][100]["live_output_scalar_slots"] += 1
    cases.append(("SCALAR_SLOT_SUM_PLUS_ONE", rejected(cert_dir, x)))

    x = copy.deepcopy(base)
    x["boundaries"][200]["live_nodes"][0]["coordinate_support_size"] -= 1
    cases.append(("SUPPORT_SIZE_MINUS_ONE", rejected(cert_dir, x)))

    x = copy.deepcopy(base)
    x["boundaries"][300]["q_node_id"] += 1
    cases.append(("Q_NODE_ID_SHIFT", rejected(cert_dir, x)))

    x = copy.deepcopy(base)
    x["certificate_digest"] = "0" * 64
    cases.append(("CERTIFICATE_DIGEST_CORRUPTION", rejected(cert_dir, x)))

    status = "PASS_ALL_CORRUPTIONS_REJECTED" if all(ok for _, ok in cases) else "FAIL_CORRUPTION_ACCEPTED"
    print(json.dumps({
        "schema": "TRUMP_EXACT_BERKOWITZ_Q_BOUNDARY_CORRUPTION_TESTS_V1",
        "status": status,
        "cases": [{"name": name, "rejected": ok} for name, ok in cases],
    }, sort_keys=True))
    raise SystemExit(0 if status.startswith("PASS") else 1)


if __name__ == "__main__":
    main()
