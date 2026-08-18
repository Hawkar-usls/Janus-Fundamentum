#!/usr/bin/env python3
"""JANUS full-text missing-link assembly.

ASSEMBLY ONLY. This module freezes the executable interface order and proof-carrying
stage contracts discovered by the source-first audit. It deliberately does NOT run
the promotion experiment on import and does NOT claim that Pyramid Texts encode a
modern algorithm. The next step is a separately frozen full run.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Iterable

P_VS_NP = "OPEN"
PARENT_PR = 197
PARENT_SHA = "43da4b4d8f24200aa7a0f220c18c5f94350ceebb"

FORWARD = [
    "PT350","PT351","PT352","PT353","PT354","PT355",
    "PT356","PT357","PT358","PT359","PT360","PT361","PT362","PT363","PT364","PT365","PT366",
    "PT367","PT368","PT369","PT370","PT371","PT372","PT373","PT374",
    "PT476","PT477","PT478",
    "PT220","PT221","PT222",
]
BACK = list(reversed(FORWARD))

# Modern experimental readings only. Ancient-text order is a source prompt, not an
# algorithmic provenance claim.
OPERATOR = {
    "PT350": "FIELD_CONTEXT_WITNESS",
    "PT351": "GESTATION_BINDING_WITNESS",
    "PT352": "FORMATION_WITNESS",
    "PT353": "LIVE_STATE_WITNESS",
    "PT354": "PROVISION_PAYLOAD_PLUS_RETURN",
    "PT355": "OPEN_AND_REASSEMBLE",
    "PT356": "SEEK_RECOGNIZE_AND_RECOVER_EYE",
    "PT357": "RECOGNIZE_PROTECT_AND_RESTORE_EYES",
    "PT358": "UNBIND_FETTERS",
    "PT359": "CROSS_AND_RECOVER_INJURED_EYE",
    "PT360": "TRANSIT_GATE_OPEN",
    "PT361": "ARM_HANDOFF_TO_HEAVEN",
    "PT362": "LIGHT_AND_PROTECT",
    "PT363": "PREPARE_PATH_AND_FERRY",
    "PT364": "RESTORE_SIGHT_FACE_AND_AWAKE",
    "PT365": "REESTABLISH_PRIOR_FUNCTION",
    "PT366": "SEED_LINEAGE_REGENERATE",
    "PT367": "REASSEMBLE_LIMBS_AND_CROWN",
    "PT368": "PROTECT_CARRY_AND_RETURN_HEAD",
    "PT369": "RESTORE_FORMER_STATE_SIGHT_AND_MOUTH",
    "PT370": "REUNITE_WITH_HORUS_AND_LIVE",
    "PT371": "RESTORE_PLACE_CROWN_AND_DELIVER_FROM_ENEMY",
    "PT372": "WAKE_AND_SUBDUE_CONFLICT",
    "PT373": "REASSEMBLE_AND_ESCORT_TO_IMPERISHABLE_STARS",
    "PT374": "FERRY_NAME_AND_OPEN_HEAVEN",
    "PT476": "CERTIFY_AND_ADMIT_AT_GREAT_GATE",
    "PT477": "RESTORE_AND_CONDUCT",
    "PT478": "LADDER_ASCENT",
    "PT220": "OPEN_HORIZON_AND_PREPARE_CROWN",
    "PT221": "AUTHORITY_HANDOFF",
    "PT222": "BIDIRECTIONAL_REPLAY_AND_ASSUME_AUTHORITY",
}

# Capability names are deliberately mechanical abstractions; they are not translations.
PRODUCES = {
    "PT350": ["FIELD_BOUND"],
    "PT351": ["GESTATION_BOUND"],
    "PT352": ["FORMATION_BOUND"],
    "PT353": ["LIVE_BOUND"],
    "PT354": ["PAYLOAD_BOUND", "RETURN_BOUND"],
    "PT355": ["PRIMARY_GATE_OPEN", "BODY_REASSEMBLED"],
    "PT356": ["SUBJECT_RECOGNIZED", "RECOVERY_TOKEN_RETURNED"],
    "PT357": ["IDENTITY_RECOGNIZED", "EYES_RESTORED", "PROTECTION_BOUND"],
    "PT358": ["FETTERS_REMOVED"],
    "PT359": ["CROSSING_CERTIFIED", "INJURED_EYE_ROUTE_BOUND"],
    "PT360": ["TRANSIT_GATE_OPEN"],
    "PT361": ["HANDOFF_TO_ASCENT_BOUND"],
    "PT362": ["LIGHT_BOUND", "PROTECTION_RENEWED"],
    "PT363": ["PATH_PREPARED", "FERRY_BOUND"],
    "PT364": ["SIGHT_RESTORED", "FACE_RESTORED", "AWAKE"],
    "PT365": ["PRIOR_FUNCTION_REESTABLISHED"],
    "PT366": ["LINEAGE_REGENERATED", "SON_RETURN_PATH_BOUND"],
    "PT367": ["LIMBS_REASSEMBLED", "CROWN_ELIGIBLE"],
    "PT368": ["CARRY_SUPPORT_BOUND", "HEAD_RETURNED", "BODY_PROTECTED"],
    "PT369": ["FORMER_STATE_RESTORED", "MOUTH_RESTORED", "VISION_CONFIRMED"],
    "PT370": ["REUNION_BOUND", "LIFE_CONTINUITY_BOUND"],
    "PT371": ["PLACE_RESTORED", "CROWN_BOUND", "ENEMY_RELEASED_FROM_PATH"],
    "PT372": ["AWAKE_CONFIRMED", "CONFLICT_SUBDUED"],
    "PT373": ["FULL_BODY_REASSEMBLED", "STAR_ESCORT_BOUND"],
    "PT374": ["FERRY_COMPLETE", "NAME_ANNOUNCED", "HEAVEN_GATE_OPEN"],
    "PT476": ["ADMISSION_CERTIFIED", "OFFICE_ELIGIBLE"],
    "PT477": ["RESTORATION_ROUTE_BOUND", "CONDUCT_BOUND"],
    "PT478": ["ASCENT_LADDER_BOUND", "ASCENT_COMPLETE"],
    "PT220": ["HORIZON_GATE_OPEN", "CROWN_PREPARED"],
    "PT221": ["AUTHORITY_TRANSFERRED"],
    "PT222": ["AUTHORITY_ASSUMED", "BIDIRECTIONAL_REPLAY_BOUND"],
}

# The linker only enforces predecessor commitment and local capability continuity.
# No semantic oracle is allowed to create missing capabilities.
REQUIRES = {
    "PT350": [],
    "PT351": ["FIELD_BOUND"],
    "PT352": ["GESTATION_BOUND"],
    "PT353": ["FORMATION_BOUND"],
    "PT354": ["LIVE_BOUND"],
    "PT355": ["PAYLOAD_BOUND", "RETURN_BOUND"],
    "PT356": ["PRIMARY_GATE_OPEN", "BODY_REASSEMBLED"],
    "PT357": ["SUBJECT_RECOGNIZED", "RECOVERY_TOKEN_RETURNED"],
    "PT358": ["IDENTITY_RECOGNIZED", "PROTECTION_BOUND"],
    "PT359": ["FETTERS_REMOVED", "EYES_RESTORED"],
    "PT360": ["CROSSING_CERTIFIED"],
    "PT361": ["TRANSIT_GATE_OPEN"],
    "PT362": ["HANDOFF_TO_ASCENT_BOUND"],
    "PT363": ["LIGHT_BOUND", "PROTECTION_RENEWED"],
    "PT364": ["PATH_PREPARED", "FERRY_BOUND"],
    "PT365": ["SIGHT_RESTORED", "FACE_RESTORED", "AWAKE"],
    "PT366": ["PRIOR_FUNCTION_REESTABLISHED"],
    "PT367": ["LINEAGE_REGENERATED", "SON_RETURN_PATH_BOUND"],
    "PT368": ["LIMBS_REASSEMBLED", "CROWN_ELIGIBLE"],
    "PT369": ["CARRY_SUPPORT_BOUND", "HEAD_RETURNED", "BODY_PROTECTED"],
    "PT370": ["FORMER_STATE_RESTORED", "VISION_CONFIRMED"],
    "PT371": ["REUNION_BOUND", "LIFE_CONTINUITY_BOUND"],
    "PT372": ["PLACE_RESTORED", "CROWN_BOUND"],
    "PT373": ["AWAKE_CONFIRMED", "CONFLICT_SUBDUED"],
    "PT374": ["FULL_BODY_REASSEMBLED", "STAR_ESCORT_BOUND"],
    "PT476": ["FERRY_COMPLETE", "NAME_ANNOUNCED", "HEAVEN_GATE_OPEN"],
    "PT477": ["ADMISSION_CERTIFIED"],
    "PT478": ["RESTORATION_ROUTE_BOUND", "CONDUCT_BOUND"],
    "PT220": ["ASCENT_LADDER_BOUND", "ASCENT_COMPLETE"],
    "PT221": ["HORIZON_GATE_OPEN", "CROWN_PREPARED"],
    "PT222": ["AUTHORITY_TRANSFERRED"],
}

SOURCE_LOCAL_BLOCKS = {
    "PT350_374": [f"PT{i}" for i in range(350, 375)],
    "PT476_478": ["PT476", "PT477", "PT478"],
    "PT220_222": ["PT220", "PT221", "PT222"],
}

INTENTIONAL_SEAMS = [
    {"from": "PT374", "to": "PT476", "unfilled": "PT375-PT475", "status": "SOURCE_AUDIT_REQUIRED"},
    {"from": "PT478", "to": "PT220", "status": "SYNTHETIC_NON_MONOTONIC_BRIDGE"},
]


@dataclass(frozen=True)
class StageEnvelope:
    stage: str
    operator: str
    predecessor_commitment: str
    state_anchor: str
    requires: tuple[str, ...]
    produces: tuple[str, ...]
    direction: str
    commitment: str


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def make_stage_envelope(stage: str, predecessor_commitment: str, state_anchor: str, direction: str) -> StageEnvelope:
    if stage not in OPERATOR:
        raise ValueError(f"unknown stage: {stage}")
    if direction not in {"FORWARD", "BACK"}:
        raise ValueError("direction must be FORWARD or BACK")
    body = {
        "stage": stage,
        "operator": OPERATOR[stage],
        "predecessor_commitment": predecessor_commitment,
        "state_anchor": state_anchor,
        "requires": REQUIRES[stage],
        "produces": PRODUCES[stage],
        "direction": direction,
    }
    return StageEnvelope(
        stage=stage,
        operator=OPERATOR[stage],
        predecessor_commitment=predecessor_commitment,
        state_anchor=state_anchor,
        requires=tuple(REQUIRES[stage]),
        produces=tuple(PRODUCES[stage]),
        direction=direction,
        commitment=_digest(body),
    )


def verify_envelope(envelope: StageEnvelope) -> bool:
    body = {
        "stage": envelope.stage,
        "operator": envelope.operator,
        "predecessor_commitment": envelope.predecessor_commitment,
        "state_anchor": envelope.state_anchor,
        "requires": list(envelope.requires),
        "produces": list(envelope.produces),
        "direction": envelope.direction,
    }
    return bool(
        envelope.stage in OPERATOR
        and envelope.operator == OPERATOR[envelope.stage]
        and list(envelope.requires) == REQUIRES[envelope.stage]
        and list(envelope.produces) == PRODUCES[envelope.stage]
        and envelope.commitment == _digest(body)
    )


def link_forward(initial_anchor: str) -> list[StageEnvelope]:
    """Build the proof-carrying assembly chain only; this is NOT a promotion run."""
    capabilities: set[str] = set()
    predecessor = _digest({"parent_sha": PARENT_SHA, "initial_anchor": initial_anchor})
    linked: list[StageEnvelope] = []
    for stage in FORWARD:
        missing = [cap for cap in REQUIRES[stage] if cap not in capabilities]
        if missing:
            raise RuntimeError(f"assembly capability gap before {stage}: {missing}")
        env = make_stage_envelope(stage, predecessor, initial_anchor, "FORWARD")
        if not verify_envelope(env):
            raise RuntimeError(f"invalid envelope at {stage}")
        linked.append(env)
        capabilities.update(PRODUCES[stage])
        predecessor = env.commitment
    return linked


def link_back(forward_chain: Iterable[StageEnvelope]) -> list[StageEnvelope]:
    """Bind BACK to exact FORWARD commitments in reverse order; no physical retrocausality claim."""
    forward_by_stage = {env.stage: env for env in forward_chain}
    predecessor = _digest({"forward_terminal": forward_by_stage["PT222"].commitment, "mode": "BACK"})
    linked: list[StageEnvelope] = []
    for stage in BACK:
        fwd = forward_by_stage[stage]
        # Back state anchor is the exact forward stage commitment. This makes rollback
        # a verification/reconstruction obligation rather than a free inverse oracle.
        env = make_stage_envelope(stage, predecessor, fwd.commitment, "BACK")
        if not verify_envelope(env):
            raise RuntimeError(f"invalid BACK envelope at {stage}")
        linked.append(env)
        predecessor = env.commitment
    return linked


def assembly_manifest() -> dict[str, Any]:
    return {
        "assembly_id": "JANUS-FULL-TEXT-MISSING-LINK-ASSEMBLY-2026-08-18-v1",
        "status": "ASSEMBLED_NOT_YET_PROMOTION_TESTED",
        "parent": {"pr": PARENT_PR, "sha": PARENT_SHA},
        "forward": FORWARD,
        "back": BACK,
        "source_local_blocks": SOURCE_LOCAL_BLOCKS,
        "intentional_seams": INTENTIONAL_SEAMS,
        "operator": OPERATOR,
        "requires": REQUIRES,
        "produces": PRODUCES,
        "laws": [
            "NO_PREVIOUS_STAGE_COMMITMENT => NO_NEXT_STAGE_AUTHORITY",
            "BACK_BINDS_EXACT_FORWARD_STAGE_COMMITMENT",
            "NO_RETURN_PATH => NO_ABSORPTION",
            "CAPABILITY != IDENTITY != AUTHORITY",
            "ANCIENT_TEXT != MODERN_ALGORITHM",
            "TEXTUAL_ORDER != COMPLEXITY_THEOREM",
        ],
        "P_VS_NP": P_VS_NP,
        "next_action": "FULL_FROZEN_PROMOTION_RUN_WITH_NEGATIVE_CONTROLS_NO_REORDERING",
    }


if __name__ == "__main__":
    # Intentionally assembly-only. A later run harness may import link_forward/link_back.
    print(json.dumps(assembly_manifest(), indent=2, ensure_ascii=False))
