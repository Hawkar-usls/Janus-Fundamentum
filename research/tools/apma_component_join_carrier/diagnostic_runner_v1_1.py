from __future__ import annotations

import json
import traceback

from research.tools.apma_component_join_carrier import component_join_carrier as c


def run_stage(name, fn, statuses):
    try:
        value = fn()
        if isinstance(value, dict):
            status = value.get("status") or value.get("ok") or "DICT_RETURN"
        else:
            status = type(value).__name__
        statuses[name] = {"completed": True, "summary": status}
        return value, None
    except Exception as exc:
        statuses[name] = {"completed": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
        return None, {
            "first_failed_stage": name,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
        }


def main() -> None:
    statuses = {}
    failed = None
    stages = [
        ("SOURCE_GUARD", c.source_guard),
        ("POSITIVE_OVERWIDTH_COMPONENT_JOIN", lambda: c.explain_overwidth_component_join(c.positive_multi_relation_k20())),
        ("EMPTY_CONDITIONAL_JOIN_CONTROL", lambda: c.explain_overwidth_component_join(c.empty_conditional_join_control())),
        ("ALPHA_CYCLE_CONTROL", lambda: c.explain_overwidth_component_join(c.alpha_cycle_control())),
        ("NO_FULL_CUT_ANCHOR_UNIT_CONTROL", c.no_anchor_unit_control),
        ("INJECTED_HINT_CONTROL", lambda: c.explain_overwidth_component_join(c.injected_hint_control())),
        ("TAMPERED_PROVENANCE_CONTROL", c.tampered_control),
    ]
    for name, fn in stages:
        _, failed = run_stage(name, fn, statuses)
        if failed is not None:
            break
    out = {
        "artifact_id": "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-V1-1-STAGED-DIAGNOSTIC-2026-09-15",
        "authority": "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION",
        "frozen_candidate_blob": "89f5d591d4d553bb26489908a79f2c739f62b756",
        "completed_stage_statuses": statuses,
        "first_failed_stage": None if failed is None else failed["first_failed_stage"],
        "exception_type": None if failed is None else failed["exception_type"],
        "exception_message": None if failed is None else failed["exception_message"],
        "traceback": None if failed is None else failed["traceback"],
        "scientific_effect": "NONE",
    }
    print(json.dumps(out, sort_keys=True))
    if failed is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
