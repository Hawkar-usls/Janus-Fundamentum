from __future__ import annotations

import argparse
import json
import random

from janus_c049_1_b1_compact_trajectory_core import (
    compactify,
    encode,
    stable_digest,
    validate_trajectory,
    width,
)


def random_basis(rng: random.Random, theta: int) -> list[int]:
    basis = [1 << i for i in range(theta)]
    for _ in range(max(1, 5 * theta)):
        if theta < 2:
            break
        i, j = rng.sample(range(theta), 2)
        if rng.randrange(2):
            basis[i], basis[j] = basis[j], basis[i]
        else:
            basis[i] ^= basis[j]
    return basis


def fixture(rng: random.Random, theta: int, k: int, index: int) -> tuple[str, list[dict]]:
    if theta == 0:
        return (
            "zero_boundary",
            [
                {"left": [], "right": [], "value": rng.randrange(k + 1)}
                for _ in range(rng.randrange(1, 18))
            ],
        )

    basis = [1 << i for i in range(theta)] if index % 2 == 0 else random_basis(rng, theta)
    mode = "coordinate_flag" if index % 2 == 0 else "transformed_flag"
    raw: list[dict] = []
    for cut in range(theta + 1):
        left = basis[:cut]
        right = basis[cut:]
        for _ in range(rng.randrange(1, 8)):
            raw.append(
                {
                    "left": left,
                    "right": right,
                    "value": rng.randrange(k + 1),
                }
            )
    return mode, raw


def invalid_controls() -> list[dict]:
    return [
        {"name": "empty", "ambient_dim": 1, "input": [], "error": "empty trajectory"},
        {
            "name": "negative_lambda",
            "ambient_dim": 1,
            "input": [{"left": [], "right": [], "value": -1}],
            "error": "negative lambda",
        },
        {
            "name": "outside_vector_even_if_it_cancels",
            "ambient_dim": 2,
            "input": [{"left": [4, 4], "right": [], "value": 0}],
            "error": "vector outside B",
        },
        {
            "name": "endpoint_mismatch",
            "ambient_dim": 2,
            "input": [
                {"left": [], "right": [1], "value": 0},
                {"left": [2], "right": [], "value": 0},
            ],
            "error": "endpoint condition",
        },
        {
            "name": "left_not_increasing",
            "ambient_dim": 2,
            "input": [
                {"left": [1], "right": [3], "value": 0},
                {"left": [], "right": [1], "value": 1},
                {"left": [3], "right": [], "value": 0},
            ],
            "error": "left not increasing",
        },
        {
            "name": "right_not_decreasing",
            "ambient_dim": 2,
            "input": [
                {"left": [], "right": [1, 2], "value": 0},
                {"left": [1], "right": [], "value": 1},
                {"left": [1, 2], "right": [1], "value": 0},
            ],
            "error": "right not decreasing",
        },
    ]


def build() -> dict:
    rng = random.Random(49101)
    audit_records: list[dict] = []
    proof_cases: list[dict] = []

    for theta in range(5):
        for k in range(6):
            for index in range(4):
                mode, raw = fixture(rng, theta, k, index)
                source = validate_trajectory(raw, theta)
                compact, trace = compactify(source)
                input_width = width(source)
                output_width = width(compact)

                payload = {
                    "theta": theta,
                    "k": k,
                    "index": index,
                    "mode": mode,
                    "input": encode(source),
                    "output": encode(compact),
                    "trace": trace,
                    "input_width": input_width,
                    "output_width": output_width,
                }
                payload.update(
                    {
                        "idempotent": compactify(compact)[0] == compact,
                        "width_preserved": input_width == output_width,
                        "length_bound": len(compact)
                        <= (2 * theta + 1) * (2 * k + 1),
                    }
                )
                payload["case_digest"] = stable_digest(payload)

                audit_records.append(
                    {
                        "theta": theta,
                        "k": k,
                        "index": index,
                        "mode": mode,
                        "input_length": len(source),
                        "output_length": len(compact),
                        "input_width": input_width,
                        "output_width": output_width,
                        "trace_steps": len(trace),
                        "idempotent": payload["idempotent"],
                        "width_preserved": payload["width_preserved"],
                        "length_bound": payload["length_bound"],
                        "case_digest": payload["case_digest"],
                    }
                )
                # One complete certificate for every (theta,k) pair.
                if index == 1:
                    proof_cases.append(payload)

    controls: list[dict] = []
    for control in invalid_controls():
        observed = None
        try:
            validate_trajectory(control["input"], control["ambient_dim"])
        except ValueError as error:
            observed = str(error)
        controls.append({**control, "observed": observed, "passed": observed == control["error"]})

    summary = {
        "audit_cases": len(audit_records),
        "audit_failures": sum(
            not (
                record["idempotent"]
                and record["width_preserved"]
                and record["length_bound"]
            )
            for record in audit_records
        ),
        "audit_trace_steps": sum(record["trace_steps"] for record in audit_records),
        "proof_cases": len(proof_cases),
        "proof_trace_steps": sum(len(case["trace"]) for case in proof_cases),
        "transformed_cases": sum(record["mode"] == "transformed_flag" for record in audit_records),
        "invalid_controls": len(controls),
        "invalid_control_failures": sum(not control["passed"] for control in controls),
    }

    artifact = {
        "artifact": "C049.1-JANUS-COMPACT-B-TRAJECTORY-B1",
        "source": "Jeong-Kim-Oum arXiv:1507.02184v4 Section 3.1",
        "status": "B1_COMPACTIFICATION_IMPLEMENTED_B2_PENDING",
        "audit_records": audit_records,
        "audit_records_digest": stable_digest(audit_records),
        "proof_cases": proof_cases,
        "invalid_controls": controls,
        "summary": summary,
        "p_vs_np": "OPEN",
    }
    artifact["integrity"] = stable_digest(artifact)
    return artifact


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(build(), handle, indent=2, sort_keys=True)
        handle.write("\n")
