from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47a2_dense_bipolar_core_obstruction_probe as r47a2


def post_subsumption_gain(formula, var: int):
    before = r33.canonical_formula(formula)
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(before, int(var))
    if not pos or not neg:
        return None
    base = tuple(c for c in before if var not in c and -var not in c)
    pool = r33.canonical_formula(list(base) + list(resolvents))
    transformed = r42.subsumption_minimize(pool)
    c0 = len(before)
    c1 = len(transformed)
    return {
        "var": int(var),
        "p": len(pos),
        "n": len(neg),
        "raw_unique_resolvents": len(resolvents),
        "pool_clauses": len(pool),
        "post_subsumption_clauses": c1,
        "gain": c0 - c1,
        "pair_checks": pair_checks,
        "transformed": transformed,
    }


def first_certified_post_subsumption_descent(formula):
    before = r33.canonical_formula(formula)
    checked = 0
    for var in r33.variables(before):
        row = post_subsumption_gain(before, int(var))
        checked += 1
        if row is None or row["gain"] <= 0:
            continue
        cert = r45a.exact_dp_record(before, int(var))
        replay = r45a.independent_dp_replay(before, cert)
        envelope = r45a.polynomial_envelope(before, cert)
        after = r33.canonical_formula(cert["transformed"])
        return {
            "selected_var": int(var),
            "variables_checked": checked,
            "gain": row["gain"],
            "before_CLV": list(r33.measure(before)),
            "after_CLV": list(r33.measure(after)),
            "strict_descent": r33.measure(after) < r33.measure(before),
            "independent_replay_pass": bool(replay["pass"]),
            "polynomial_envelope_pass": bool(envelope["pass"]),
            "raw_unique_resolvents": row["raw_unique_resolvents"],
            "removed_parent_clauses": row["p"] + row["n"],
        }
    return {"selected_var": None, "variables_checked": checked}


def run():
    formula = r47a2.FROZEN
    fast = first_certified_post_subsumption_descent(formula)
    old = r45a.select_macro(formula)
    selected = old.get("selected") or old.get("selected_macro") or old.get("macro")
    if selected is None and isinstance(old.get("candidates"), list):
        accepted = [x for x in old["candidates"] if x.get("accepted")]
        selected = min(accepted, key=lambda x: tuple(x.get("selection_key", []))) if accepted else None
    out = {
        "input_CLV": list(r33.measure(formula)),
        "post_subsumption_first_descent": fast,
        "legacy_full_macro_has_selection": selected is not None,
        "legacy_selected_var": None if selected is None else selected.get("var"),
        "firewall": {
            "R47A_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
