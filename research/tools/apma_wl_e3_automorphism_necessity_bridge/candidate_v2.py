from __future__ import annotations

import json
from typing import Any

from research.tools.apma_wl_e3_automorphism_necessity_bridge import candidate as v1


def corrected_guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(v1.ROOT)): v1.blob(p) == h for p, h in v1.EXPECTED.items()}
    pre = json.loads(v1.PREREG.read_text())
    review = json.loads(v1.REVIEW.read_text())
    parent = json.loads(v1.PARENT.read_text())
    scientific = parent.get('scientific_outcome', {})
    checks = {
        'authority_bindings': all(bindings.values()),
        'prereg_frozen': pre.get('status') == 'FROZEN_BEFORE_BRIDGE_IMPLEMENTATION_OR_EXECUTION',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_WL_E3_NECESSITY_BRIDGE_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
        'parent_execution_verified': parent.get('execution_verdict') == 'PASS_INDEPENDENT_ONE_SHOT_EXECUTION_AND_EXACT_RECOMPUTATION',
        'parent_both_route_classes': scientific.get('route_coverage_outcome') == 'PANEL_CONTAINS_BOTH_PORTFOLIO_OPEN_AND_PORTFOLIO_CLOSED',
        'parent_all_four_wl_survive': scientific.get('wl_replication_outcome') == 'ALL_FOUR_FROZEN_WL_FEATURES_SURVIVE',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings, 'binding_correction': 'PARENT_SCIENTIFIC_OUTCOME_CONTAINER_ONLY'}


def main() -> dict[str, Any]:
    old_guard = v1.guard
    try:
        v1.guard = corrected_guard
        out = v1.main()
    finally:
        v1.guard = old_guard
    out['implementation_note'] = 'V2_CORRECTS_ONLY_PARENT_JSON_CONTAINER_BINDING_FROM_SUMMARY_TO_SCIENTIFIC_OUTCOME__NO_SCIENTIFIC_CLAIM_OR_TEST_CHANGED'
    return out


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
