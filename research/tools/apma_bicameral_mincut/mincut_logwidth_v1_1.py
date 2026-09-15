from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as frozen_v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-MINCUT-LOGWIDTH-V1-1-CANDIDATE-2026-09-15"
AUTHORITY = "CANDIDATE_WRAPPER__CONTROL_REPAIR_ONLY__FROZEN_V1_ENGINE_DELEGATE"
PREREG_REL = Path("research/TRUMP_BICAMERAL_MINCUT_LOGWIDTH_V1_1_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "5f252316a74cbf431ad81da8528d58669e96ffa8"
PREREG_GIT_BLOB_SHA1 = "16eafc01018bfb33da7992f8559e77de5f5ab129"
FROZEN_ENGINE_REL = Path("research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py")
FROZEN_ENGINE_GIT_BLOB_SHA1 = "c0c612676e39241b95026c15823e7af6b3da8f0d"
FIRST_FAILURE_REL = Path("research/TRUMP_BICAMERAL_MINCUT_LOGWIDTH_FIRST_RUN_FAILURE_2026-09-15.json")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    root = repo_root()
    prereg = root / PREREG_REL
    engine = root / FROZEN_ENGINE_REL
    failure = root / FIRST_FAILURE_REL
    pobj = json.loads(prereg.read_text(encoding="utf-8"))
    fobj = json.loads(failure.read_text(encoding="utf-8"))
    checks = {
        "v1_1_prereg_blob": git_blob_sha1(prereg) == PREREG_GIT_BLOB_SHA1,
        "v1_1_prereg_frozen": pobj.get("status") == "FROZEN_BEFORE_V1_1_CANDIDATE",
        "frozen_v1_engine_blob": git_blob_sha1(engine) == FROZEN_ENGINE_GIT_BLOB_SHA1,
        "v1_0_failure_preserved": fobj.get("verdict") == "FAIL_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION",
        "v1_0_failure_class_preserved": fobj.get("failure_class") == "PREREGISTERED_POSITIVE_CONTROL_OUT_OF_SCOPE__NOT_MINCUT_DISCOVERY_FAILURE",
    }
    return {"ok": all(checks.values()), "checks": checks}


def corrected_positive() -> dict:
    return {
        "variables": [0,1,2,3,4],
        "constraints": [
            {
                "id": "opaque_embedded_or2",
                "scope": [0,1,2,3],
                "allowed": [[0,1,0,0],[1,0,1,1],[1,1,1,1]],
            },
            {
                "id": "opaque_embedded_xor3",
                "scope": [0,1,2,4],
                "allowed": [[0,0,0,0],[0,1,1,0],[1,0,1,1],[1,1,0,1]],
            },
        ],
    }


def injected_hint_control() -> dict:
    raw = corrected_positive()
    raw["separator"] = [0,1,2]
    return raw


def explain_v1_1(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {
            "artifact_id": ARTIFACT_ID,
            "authority": AUTHORITY,
            "status": "HALT_SOURCE_GUARD",
            "source_guard": guard,
            "scientific_firewall": frozen_v1.firewall(),
        }
    delegated = frozen_v1.explain_with_mincut(raw)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "source_guard": guard,
        "frozen_v1_engine_artifact": frozen_v1.ARTIFACT_ID,
        "frozen_v1_engine_blob": FROZEN_ENGINE_GIT_BLOB_SHA1,
        "status": delegated.get("status"),
        "delegated": delegated,
        "scientific_firewall": delegated.get("scientific_firewall", frozen_v1.firewall()),
    }


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "positive": explain_v1_1(corrected_positive()),
        "negative_overwidth": explain_v1_1(frozen_v1.negative_overwidth_cut()),
        "negative_hint": explain_v1_1(injected_hint_control()),
        "scientific_firewall": frozen_v1.firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
