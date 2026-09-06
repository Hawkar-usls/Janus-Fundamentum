from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25h_micro_rup_restart_broader_1212_polynomial_ledger_audit as r50g25h


def run():
    out = r50g25h.run()
    hist = out["micro_RUP_successful_strengthenings_unique_histogram"]
    authoritative_total = sum(int(k) * int(v) for k, v in hist.items())
    out["aggregate_micro_ledger"]["RUP_successful_strengthenings"] = authoritative_total
    out["interpretation_contract"]["aggregate_RUP_successful_strengthenings_derived_from_authoritative_histogram"] = True
    out["seal"] = {
        "authoritative_RUP_successful_strengthenings_total": authoritative_total,
        "derivation": "sum(int(strengthenings_per_state) * unique_state_count)",
        "histogram": hist,
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
