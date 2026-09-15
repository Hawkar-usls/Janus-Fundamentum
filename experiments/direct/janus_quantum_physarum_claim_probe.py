#!/usr/bin/env python3
"""Fail-closed probe for the legacy JANUS "Quantum-P=NP" candidate.

The candidate under test is:

    |psi> = H^n |0^n>
    U     = product_i CNOT(i, i+1)
    |psi> = U |psi>
    y     = Sort(|psi>)

The probe tests only this concrete candidate.  It does not decide P versus NP.
It also runs a small Physarum-inspired obstruction router using the legacy
parameters agent_count=50, decay_rate=0.95, growth_rate=1.2.  That router is a
hypothesis/attention mechanism, not a proof rule.
"""

from __future__ import annotations

from collections import Counter
from math import comb, sqrt

AGENT_COUNT = 50
DECAY_RATE = 0.95
GROWTH_RATE = 1.2


def uniform_state(n: int) -> tuple[complex, ...]:
    amp = 1.0 / sqrt(2**n)
    return tuple(complex(amp, 0.0) for _ in range(2**n))


def bits_of(index: int, n: int) -> list[int]:
    return [(index >> (n - 1 - j)) & 1 for j in range(n)]


def index_of(bits: list[int]) -> int:
    out = 0
    for bit in bits:
        out = (out << 1) | bit
    return out


def cnot_chain_permutation(index: int, n: int) -> int:
    bits = bits_of(index, n)
    for i in range(n - 1):
        bits[i + 1] ^= bits[i]
    return index_of(bits)


def apply_cnot_chain(state: tuple[complex, ...], n: int) -> tuple[complex, ...]:
    out = [0j] * len(state)
    for index, amplitude in enumerate(state):
        out[cnot_chain_permutation(index, n)] += amplitude
    return tuple(out)


def max_state_delta(left: tuple[complex, ...], right: tuple[complex, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right)) if left else 0.0


def sorted_measurement_distribution(n: int) -> dict[str, float]:
    """If Sort means 'measure then sort bits', derive its exact distribution.

    The result depends only on Hamming weight, hence only on n, not on a language
    L or an input predicate.  This interpretation is deliberately separated
    from the undefined operation Sort(|psi>) on an unmeasured state vector.
    """
    denominator = 2**n
    result = {}
    for ones in range(n + 1):
        label = "0" * (n - ones) + "1" * ones
        result[label] = comb(n, ones) / denominator
    return result


def quantum_probe(max_n: int = 10) -> list[dict[str, object]]:
    rows = []
    for n in range(1, max_n + 1):
        before = uniform_state(n)
        after = apply_cnot_chain(before, n)
        delta = max_state_delta(before, after)
        assert delta < 1e-12
        rows.append(
            {
                "n": n,
                "max_amplitude_delta": delta,
                "state_unchanged": True,
                "sort_after_measure_distribution": sorted_measurement_distribution(n),
            }
        )
    return rows


def physarum_obstruction_router() -> dict[str, object]:
    """Route attention toward the shortest surviving obstruction explanations.

    This intentionally uses Physarum-like reinforce/decay dynamics only to rank
    already-valid logical obstructions.  It cannot manufacture proof validity.
    """
    paths = {
        "NO_LANGUAGE_DEPENDENCE": (
            "CLAIM",
            "HADAMARD_PREP",
            "CNOT_CHAIN",
            "NO_L_OR_X_PREDICATE_COUPLING",
            "SPECIFIC_CANDIDATE_REJECTED",
        ),
        "SORT_UNDEFINED_OR_LANGUAGE_BLIND": (
            "CLAIM",
            "HADAMARD_PREP",
            "CNOT_CHAIN",
            "SORT_GATE",
            "SPECIFIC_CANDIDATE_REJECTED",
        ),
        "FORMULA_SCOPE_DEFECT": (
            "CLAIM",
            "P_NP_FORMULA",
            "FIXED_N_AND_UNSPECIFIED_L",
            "REPAIR_REQUIRED",
            "SPECIFIC_CANDIDATE_REJECTED",
        ),
    }

    conductivity: Counter[tuple[str, str]] = Counter()
    for path in paths.values():
        for edge in zip(path, path[1:]):
            conductivity[edge] = 1.0

    path_hits: Counter[str] = Counter()
    ordered_names = sorted(paths)
    for step in range(AGENT_COUNT):
        # All three are valid obstructions. Prefer shorter routes; deterministic
        # round-robin breaks equal-length ties without claiming epistemic weight.
        min_len = min(len(paths[name]) for name in ordered_names)
        candidates = [name for name in ordered_names if len(paths[name]) == min_len]
        chosen = candidates[step % len(candidates)]
        path_hits[chosen] += 1

        for edge in list(conductivity):
            conductivity[edge] *= DECAY_RATE
        for edge in zip(paths[chosen], paths[chosen][1:]):
            conductivity[edge] *= GROWTH_RATE

    top_edges = sorted(conductivity.items(), key=lambda item: (-item[1], item[0]))[:8]
    return {
        "agent_count": AGENT_COUNT,
        "decay_rate": DECAY_RATE,
        "growth_rate": GROWTH_RATE,
        "path_hits": dict(path_hits),
        "top_edges": [(list(edge), value) for edge, value in top_edges],
        "boundary": "Physarum routing ranks obstruction paths; logical validity was established independently.",
    }


def main() -> None:
    rows = quantum_probe(10)
    router = physarum_obstruction_router()

    print("JANUS_QUANTUM_PHYSARUM_CLAIM_PROBE = COMPLETE")
    print("STATE_TOPOLOGY = 𓂸 -> 𓨍 -> 𓇠 -> 𓆇 -> 𓨍 -> 𓂺")
    print("QUANTUM_PREP = H^n |0^n> = uniform computational-basis superposition")
    print("CNOT_CHAIN_EFFECT = BASIS_PERMUTATION")
    print("UNIFORM_STATE_AFTER_CNOT_CHAIN = UNCHANGED")
    print("MAX_TESTED_N = 10")
    print(f"MAX_OBSERVED_AMPLITUDE_DELTA = {max(row['max_amplitude_delta'] for row in rows)}")
    print("LANGUAGE_DEPENDENCE_IN_H_CNOT_PIPELINE = ABSENT")
    print("SORT_ON_UNMEASURED_STATE = NOT_SPECIFIED_AS_A_VALID_QUANTUM_OPERATION")
    print("SORT_AFTER_MEASUREMENT = LANGUAGE_BLIND_HAMMING_WEIGHT_COMPRESSION")
    print("SPECIFIC_H_CNOT_SORT_P_EQ_NP_CANDIDATE = REFUTED_AS_UNIVERSAL_LANGUAGE_DECIDER")
    print("P_VS_NP = OPEN")
    print("SEED_𓇠 = PROBLEM_DEPENDENT_INFORMATION_MUST_ENTER_BEFORE_DECISION")
    print("CHILD_𓆇 = PHYSARUM_OR_Q_HEURISTIC_MAY_PROPOSE_STRUCTURE_BUT_EXACT_VERIFIER_MUST_CERTIFY_IT")
    print(f"PHYSARUM_PATH_HITS = {router['path_hits']}")
    print("claim_boundary = this rejects the concrete legacy candidate only; it is not a P!=NP result")


if __name__ == "__main__":
    main()
