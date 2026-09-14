from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable

PREREG = Path("research/TRUMP_CONNECTED_MIXED_CARRIER_SCHAEFER_BARRIER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB_SHA1 = "1b86e6f4be243ad64dc5933721cbead89ec81046"
PREREG_COMMIT = "8c8d9458a3d3f672b10285210164e183111de859"

Relation = set[tuple[int, ...]]

OR2: Relation = {(0, 1), (1, 0), (1, 1)}
EVEN_XOR3: Relation = {(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)}
GAMMA = [OR2, EVEN_XOR3]


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def coord_binary(a: tuple[int, ...], b: tuple[int, ...], f: Callable[[int, int], int]) -> tuple[int, ...]:
    return tuple(f(x, y) for x, y in zip(a, b))


def coord_ternary(a: tuple[int, ...], b: tuple[int, ...], c: tuple[int, ...], f: Callable[[int, int, int], int]) -> tuple[int, ...]:
    return tuple(f(x, y, z) for x, y, z in zip(a, b, c))


def closed_binary(rel: Relation, f: Callable[[int, int], int]) -> bool:
    return all(coord_binary(a, b, f) in rel for a in rel for b in rel)


def closed_ternary(rel: Relation, f: Callable[[int, int, int], int]) -> bool:
    return all(coord_ternary(a, b, c, f) in rel for a in rel for b in rel for c in rel)


def all_zero(rel: Relation) -> tuple[int, ...]:
    return tuple(0 for _ in next(iter(rel)))


def all_one(rel: Relation) -> tuple[int, ...]:
    return tuple(1 for _ in next(iter(rel)))


def is_0_valid(language: list[Relation]) -> bool:
    return all(all_zero(r) in r for r in language)


def is_1_valid(language: list[Relation]) -> bool:
    return all(all_one(r) in r for r in language)


def is_horn(language: list[Relation]) -> bool:
    return all(closed_binary(r, lambda x, y: x & y) for r in language)


def is_dual_horn(language: list[Relation]) -> bool:
    return all(closed_binary(r, lambda x, y: x | y) for r in language)


def maj(x: int, y: int, z: int) -> int:
    return (x & y) | (x & z) | (y & z)


def minority(x: int, y: int, z: int) -> int:
    return x ^ y ^ z


def is_bijunctive(language: list[Relation]) -> bool:
    return all(closed_ternary(r, maj) for r in language)


def is_affine(language: list[Relation]) -> bool:
    return all(closed_ternary(r, minority) for r in language)


def main() -> None:
    p = root() / PREREG
    prereg = json.loads(p.read_text(encoding="utf-8"))

    combined = {
        "0_valid": is_0_valid(GAMMA),
        "1_valid": is_1_valid(GAMMA),
        "horn": is_horn(GAMMA),
        "dual_horn": is_dual_horn(GAMMA),
        "bijunctive": is_bijunctive(GAMMA),
        "affine": is_affine(GAMMA),
    }

    witness_checks = {
        "C1_OR2_excludes_00": (0, 0) not in OR2,
        "C2_EVEN_XOR3_excludes_111": (1, 1, 1) not in EVEN_XOR3,
        "C3_AND_witness": coord_binary((0, 1, 1), (1, 0, 1), lambda x, y: x & y) == (0, 0, 1) and (0, 0, 1) not in EVEN_XOR3,
        "C4_OR_witness": coord_binary((0, 1, 1), (1, 0, 1), lambda x, y: x | y) == (1, 1, 1) and (1, 1, 1) not in EVEN_XOR3,
        "C5_majority_witness": coord_ternary((0, 1, 1), (1, 0, 1), (1, 1, 0), maj) == (1, 1, 1) and (1, 1, 1) not in EVEN_XOR3,
        "C6_minority_witness": coord_ternary((0, 1), (1, 0), (1, 1), minority) == (0, 0) and (0, 0) not in OR2,
    }

    native_checks = {
        "OR2_is_bijunctive": is_bijunctive([OR2]),
        "EVEN_XOR3_is_affine": is_affine([EVEN_XOR3]),
    }

    prereg_guard = (
        git_blob_sha1(p) == PREREG_BLOB_SHA1
        and prereg.get("status") == "FROZEN_BEFORE_CHECKER_IMPLEMENTATION"
        and prereg.get("artifact_id") == "JANUS-TRUMP-CONNECTED-MIXED-CARRIER-SCHAEFER-BARRIER-PREREGISTRATION-2026-09-15-v1.0"
    )

    checks = {
        "prereg_source_guard": prereg_guard,
        "relation_OR2_exact": sorted("".join(map(str, t)) for t in OR2) == ["01", "10", "11"],
        "relation_EVEN_XOR3_exact": sorted("".join(map(str, t)) for t in EVEN_XOR3) == ["000", "011", "101", "110"],
        "each_native_relation_individually_tractable_class": all(native_checks.values()),
        "all_six_combined_tractable_classes_excluded": not any(combined.values()),
        "explicit_exclusion_witnesses": all(witness_checks.values()),
        "external_theorem_provenance_bound": prereg.get("external_theorem", {}).get("modern_source", "").startswith("Jonsson, Lagerkvist, Osipov"),
        "connected_component_implication_recorded": "connected" in prereg.get("proof_target", {}).get("C8_connected_reduction", "").lower(),
        "p_vs_np_firewall_open": prereg.get("mandatory_firewalls", {}).get("P_VS_NP") == "OPEN",
    }

    verdict = "PASS_SCHAEFER_MIXED_CARRIER_BARRIER" if all(checks.values()) else "FAIL_RELATION_CLASSIFICATION"
    out = {
        "artifact_id": "JANUS-TRUMP-CONNECTED-MIXED-CARRIER-SCHAEFER-BARRIER-CHECK-2026-09-15-v1.0",
        "prereg_commit": PREREG_COMMIT,
        "relations": {
            "OR2": sorted("".join(map(str, t)) for t in OR2),
            "EVEN_XOR3": sorted("".join(map(str, t)) for t in EVEN_XOR3),
        },
        "native_classes": native_checks,
        "combined_language_classification": combined,
        "exclusion_witnesses": witness_checks,
        "checks": checks,
        "classification_consequence": "By the preregistered source-bound Schaefer dichotomy, SAT({OR2,EVEN_XOR3}) is NP-complete because the combined language is in none of the six tractable classes.",
        "algorithmic_consequence": "A polynomial exact mechanism covering every connected instance of this mixed language would, together with ordinary connected-component decomposition, put this NP-complete language in P and therefore imply P=NP.",
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_CLAIMED",
            "P_NOT_EQUAL_NP": "NOT_CLAIMED",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "meaning": "Unrestricted connected composition of sealed tractable carriers is not a routine closure property; additional structure must be exploited unless one is explicitly attacking the P-vs-NP barrier."
        },
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
