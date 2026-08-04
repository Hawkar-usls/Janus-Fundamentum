#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "C049.1-B4.6.3-ROOT-FULL-SET-COMPLETENESS-RECEIPT-v1"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def verify(path: Path) -> dict:
    receipt = json.loads(path.read_text())
    supplied = receipt.pop("receipt_digest")
    if supplied != digest(receipt):
        raise AssertionError("receipt digest mismatch")
    receipt["receipt_digest"] = supplied
    if receipt["schema"] != SCHEMA:
        raise AssertionError("schema mismatch")
    for node in receipt["node_receipts"]:
        recomputed = all(check["equal"] is True for check in node["checks"].values())
        if recomputed != node["inventory_complete"]:
            raise AssertionError("node inventory completeness mismatch")
    recomputed_inventory = all(node["inventory_complete"] for node in receipt["node_receipts"])
    if recomputed_inventory != receipt["inventory_complete"]:
        raise AssertionError("outer inventory completeness mismatch")
    # Inventory equality is necessary but deliberately insufficient for a terminal.
    if receipt["semantic_up_k_replay_complete"] is not False:
        raise AssertionError("semantic up_k replay may not be asserted by inventory verifier")
    if receipt["terminal_classifier"] != "OPEN_TRAJECTORY_ENGINE_INCOMPLETE":
        raise AssertionError("inventory-only receipt promoted a terminal")
    boundary = receipt["strict_boundary"]
    if boundary["found_layout_enabled"] or boundary["no_layout_at_cap_enabled"]:
        raise AssertionError("terminal enabled before semantic replay")
    if boundary["terminal_completeness_proved"]:
        raise AssertionError("terminal completeness prematurely asserted")
    return receipt


def tamper_self_test(receipt: dict, path: Path) -> None:
    attacks = []
    a = json.loads(json.dumps(receipt)); a["inventory_complete"] = True; attacks.append(a)
    b = json.loads(json.dumps(receipt)); b["semantic_up_k_replay_complete"] = True; attacks.append(b)
    c = json.loads(json.dumps(receipt)); c["terminal_classifier"] = "NO_LAYOUT_AT_CAP_CANDIDATE"; attacks.append(c)
    d = json.loads(json.dumps(receipt)); d["strict_boundary"]["no_layout_at_cap_enabled"] = True; attacks.append(d)
    for index, attack in enumerate(attacks):
        attack.pop("receipt_digest", None)
        attack["receipt_digest"] = digest(attack)
        candidate = path.with_name(f"tamper-{index}.json")
        candidate.write_bytes(canonical_json(attack) + b"\n")
        try:
            verify(candidate)
        except AssertionError:
            continue
        raise AssertionError(f"tamper {index} accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    receipt = verify(args.receipt)
    if args.tamper_self_test:
        tamper_self_test(receipt, args.receipt)
    print("B4.6.3 root inventory receipt verifier: PASS")


if __name__ == "__main__":
    main()
