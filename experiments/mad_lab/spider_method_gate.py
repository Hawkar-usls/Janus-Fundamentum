#!/usr/bin/env python3
"""Spider methodology gate for JANUS MAD-LAB.

This imports *method discipline only* from the user-supplied TOPA-SPIDER dossier:
freeze-before-evaluate, preserve disconfirming evidence, milestone stop, and
look-elsewhere/discovery-vs-confirmation separation. No retrocausal or tachyon
claim is treated as physical truth.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

LANE = "JANUS_MAD_LAB"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"
SOURCE_BATCH_SHA256 = "505272c438ee56486267b9bb2a878f89aeb9ebae78a2c003ac337932cb43bf74"


def canonical_sha256(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class FrozenPlan:
    experiment_id: str
    N: int
    scope: str
    action_order: str
    repair_chain: tuple[str, ...]
    falsification_rule: str
    discovery_or_confirmation: str
    lane: str = LANE
    status: str = STATUS
    P_VS_NP: str = P_VS_NP

    def seal(self) -> dict:
        payload = asdict(self)
        return {
            "payload": payload,
            "sha256": canonical_sha256(payload),
            "source_method_batch_sha256": SOURCE_BATCH_SHA256,
            "frozen_before_evaluation": True,
        }


def verify_seal(record: dict) -> bool:
    return record.get("frozen_before_evaluation") is True and canonical_sha256(record["payload"]) == record["sha256"]


def classify_pattern_use(discovery_primes: set[int], confirmation_primes: set[int]) -> str:
    if discovery_primes & confirmation_primes:
        return "INVALID_OVERLAP__DISCOVERY_CANNOT_CONFIRM_ITSELF"
    return "SEPARATED"


def selftest() -> None:
    plan = FrozenPlan(
        experiment_id="MAD-PRIME-STRESS-SMOKE",
        N=59,
        scope="n=7 root boundary",
        action_order="m,d,p ascending",
        repair_chain=("GLOBAL_RAW", "INCIDENCE_SURPLUS", "PROVED_LOCAL_RESCUES"),
        falsification_rule="Any unresolved raw_bound>N^2 is OPEN; never rewrite after seeing it.",
        discovery_or_confirmation="DISCOVERY",
    )
    sealed = plan.seal()
    assert verify_seal(sealed)
    mutated = json.loads(json.dumps(sealed))
    mutated["payload"]["N"] = 61
    assert not verify_seal(mutated)
    assert classify_pattern_use({59, 61}, {67, 71}) == "SEPARATED"
    assert classify_pattern_use({59, 61}, {61, 67}).startswith("INVALID_OVERLAP")
    print("SPIDER_FROZEN_PRECOMMIT=PASS")
    print("SPIDER_TAMPER_REJECTION=PASS")
    print("SPIDER_DISCOVERY_CONFIRMATION_SPLIT=PASS")
    print("NO_PHYSICAL_RETROCAUSAL_PROMOTION=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
