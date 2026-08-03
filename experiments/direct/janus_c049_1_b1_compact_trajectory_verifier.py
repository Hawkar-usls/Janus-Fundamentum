from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
from functools import lru_cache


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def basis(rows):
    pivots = {}
    for raw in rows:
        x = int(raw)
        if x < 0:
            raise ValueError("negative vector")
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                for q, y in list(pivots.items()):
                    if q != p and ((y >> p) & 1):
                        pivots[q] = y ^ x
                break
    for p in sorted(pivots):
        row = pivots[p]
        for q in sorted(pivots, reverse=True):
            if q != p and ((pivots[q] >> p) & 1):
                pivots[q] ^= row
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def normalize(raw, theta):
    if theta < 0:
        raise ValueError("negative ambient dimension")
    value = int(raw["value"])
    if value < 0:
        raise ValueError("negative lambda")
    limit = 1 << theta
    left_raw = tuple(int(v) for v in raw["left"])
    right_raw = tuple(int(v) for v in raw["right"])
    if any(v < 0 or v >= limit for v in left_raw + right_raw):
        raise ValueError("vector outside B")
    return (basis(left_raw), basis(right_raw), value)


def contains(big, small):
    return basis(big + small) == basis(big)


def validate(raw, theta):
    if theta < 0:
        raise ValueError("negative ambient dimension")
    if not raw:
        raise ValueError("empty trajectory")
    seq = tuple(normalize(item, theta) for item in raw)
    if seq[0][1] != seq[-1][0]:
        raise ValueError("endpoint condition")
    for a, b in zip(seq, seq[1:]):
        if not contains(b[0], a[0]):
            raise ValueError("left not increasing")
        if not contains(a[1], b[1]):
            raise ValueError("right not decreasing")
    return seq


def encode(seq):
    return [{"left": list(a), "right": list(b), "value": c} for a, b, c in seq]


def seq_digest(seq):
    return digest(encode(seq))


def interval_legal(seq, i, j):
    if j - i <= 1 or seq[i][:2] != seq[j][:2]:
        return False
    lo, hi = seq[i][2], seq[j][2]
    values = [item[2] for item in seq[i + 1 : j]]
    return (
        lo <= hi and all(lo <= value <= hi for value in values)
    ) or (
        lo >= hi and all(lo >= value >= hi for value in values)
    )


def compact_left(raw_seq, with_trace=False):
    seq = list(raw_seq)
    trace = []
    while True:
        changed = False
        for i in range(1, len(seq)):
            if seq[i - 1] != seq[i]:
                continue
            before = len(seq)
            removed = [seq[i]]
            del seq[i]
            trace.append(
                {
                    "rule": "duplicate",
                    "start": i - 1,
                    "end": i,
                    "before_length": before,
                    "removed_entries": encode(removed),
                    "after_length": len(seq),
                    "after_digest": seq_digest(seq),
                }
            )
            changed = True
            break
        if changed:
            continue
        for i in range(len(seq)):
            for j in range(i + 2, len(seq)):
                if not interval_legal(seq, i, j):
                    continue
                before = len(seq)
                removed = seq[i + 1 : j]
                del seq[i + 1 : j]
                trace.append(
                    {
                        "rule": "interval",
                        "start": i,
                        "end": j,
                        "before_length": before,
                        "removed_entries": encode(removed),
                        "after_length": len(seq),
                        "after_digest": seq_digest(seq),
                    }
                )
                changed = True
                break
            if changed:
                break
        if not changed:
            return (tuple(seq), trace) if with_trace else tuple(seq)


def compact_reverse(raw_seq):
    seq = list(raw_seq)
    while True:
        changed = False
        for i in range(len(seq) - 1, 0, -1):
            if seq[i - 1] == seq[i]:
                del seq[i - 1]
                changed = True
                break
        if changed:
            continue
        for j in range(len(seq) - 1, 1, -1):
            for i in range(j - 2, -1, -1):
                if interval_legal(seq, i, j):
                    del seq[i + 1 : j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def replay_trace(input_seq, trace):
    seq = list(input_seq)
    for step in trace:
        assert step["before_length"] == len(seq)
        rule = step["rule"]
        i, j = int(step["start"]), int(step["end"])
        assert 0 <= i < len(seq)
        assert i < j < len(seq)

        if rule == "duplicate":
            assert j == i + 1
            assert seq[i] == seq[j]
            removed = [seq[j]]
            del seq[j]
        elif rule == "interval":
            assert interval_legal(seq, i, j)
            removed = seq[i + 1 : j]
            del seq[i + 1 : j]
        else:
            raise AssertionError("unknown trace rule")

        assert encode(removed) == step["removed_entries"]
        assert step["after_length"] == len(seq)
        assert step["after_digest"] == seq_digest(seq)
    return tuple(seq)


def width(seq):
    return max(item[2] for item in seq)


def random_basis(rng, theta):
    vectors = [1 << i for i in range(theta)]
    for _ in range(max(1, 5 * theta)):
        if theta < 2:
            break
        i, j = rng.sample(range(theta), 2)
        if rng.randrange(2):
            vectors[i], vectors[j] = vectors[j], vectors[i]
        else:
            vectors[i] ^= vectors[j]
    return vectors


def fixture(rng, theta, k, index):
    if theta == 0:
        return (
            "zero_boundary",
            [
                {"left": [], "right": [], "value": rng.randrange(k + 1)}
                for _ in range(rng.randrange(1, 18))
            ],
        )
    vectors = [1 << i for i in range(theta)] if index % 2 == 0 else random_basis(rng, theta)
    mode = "coordinate_flag" if index % 2 == 0 else "transformed_flag"
    raw = []
    for cut in range(theta + 1):
        for _ in range(rng.randrange(1, 8)):
            raw.append(
                {
                    "left": vectors[:cut],
                    "right": vectors[cut:],
                    "value": rng.randrange(k + 1),
                }
            )
    return mode, raw


def regenerate_audit_records():
    rng = random.Random(49101)
    records = []
    for theta in range(5):
        for k in range(6):
            for index in range(4):
                mode, raw = fixture(rng, theta, k, index)
                source = validate(raw, theta)
                output, trace = compact_left(source, with_trace=True)
                payload = {
                    "theta": theta,
                    "k": k,
                    "index": index,
                    "mode": mode,
                    "input": encode(source),
                    "output": encode(output),
                    "trace": trace,
                    "input_width": width(source),
                    "output_width": width(output),
                    "idempotent": compact_left(output) == output,
                    "width_preserved": width(source) == width(output),
                    "length_bound": len(output) <= (2 * theta + 1) * (2 * k + 1),
                }
                payload["case_digest"] = digest(payload)
                records.append(
                    {
                        "theta": theta,
                        "k": k,
                        "index": index,
                        "mode": mode,
                        "input_length": len(source),
                        "output_length": len(output),
                        "input_width": width(source),
                        "output_width": width(output),
                        "trace_steps": len(trace),
                        "idempotent": payload["idempotent"],
                        "width_preserved": payload["width_preserved"],
                        "length_bound": payload["length_bound"],
                        "case_digest": payload["case_digest"],
                    }
                )
    return records


def all_scalar_reductions(seq):
    seq = tuple(seq)
    outputs = []
    for i in range(1, len(seq)):
        if seq[i - 1] == seq[i]:
            outputs.append(seq[:i] + seq[i + 1 :])
    for i in range(len(seq)):
        for j in range(i + 2, len(seq)):
            a, b = seq[i], seq[j]
            interior = seq[i + 1 : j]
            if (
                a <= b and all(a <= x <= b for x in interior)
            ) or (
                a >= b and all(a >= x >= b for x in interior)
            ):
                outputs.append(seq[: i + 1] + seq[j:])
    return tuple(outputs)


@lru_cache(maxsize=None)
def scalar_normal_forms(seq):
    next_steps = all_scalar_reductions(seq)
    if not next_steps:
        return frozenset({seq})
    result = set()
    for next_seq in next_steps:
        result.update(scalar_normal_forms(next_seq))
    return frozenset(result)


def exhaustive_scalar_confluence():
    checked = 0
    for k in range(4):
        alphabet = range(k + 1)
        for length in range(1, 7):
            for seq in itertools.product(alphabet, repeat=length):
                assert len(scalar_normal_forms(seq)) == 1
                checked += 1
    return checked


def main(path):
    with open(path, encoding="utf-8") as handle:
        artifact = json.load(handle)

    assert artifact["artifact"] == "C049.1-JANUS-COMPACT-B-TRAJECTORY-B1"
    assert artifact["source"] == "Jeong-Kim-Oum arXiv:1507.02184v4 Section 3.1"
    assert artifact["p_vs_np"] == "OPEN"

    claimed_integrity = artifact["integrity"]
    unsigned = dict(artifact)
    unsigned.pop("integrity")
    assert claimed_integrity == digest(unsigned)

    regenerated = regenerate_audit_records()
    assert artifact["audit_records_digest"] == digest(regenerated)

    verified = []
    for case in artifact["proof_cases"]:
        claimed_case_digest = case["case_digest"]
        unsigned_case = dict(case)
        unsigned_case.pop("case_digest")
        assert claimed_case_digest == digest(unsigned_case)

        theta, k = int(case["theta"]), int(case["k"])
        source = validate(case["input"], theta)
        output = validate(case["output"], theta)
        replayed = replay_trace(source, case["trace"])
        alternate = compact_reverse(source)

        assert replayed == output
        assert alternate == output
        assert compact_reverse(output) == output
        assert width(source) == width(output)
        assert case["input_width"] == width(source)
        assert case["output_width"] == width(output)
        assert case["width_preserved"] is True
        assert case["idempotent"] is True
        assert len(output) <= (2 * theta + 1) * (2 * k + 1)
        assert case["length_bound"] is True

        verified.append(
            {
                "theta": theta,
                "k": k,
                "index": case["index"],
                "mode": case["mode"],
                "input_length": len(source),
                "output_length": len(output),
                "trace_steps": len(case["trace"]),
                "case_digest": claimed_case_digest,
            }
        )

    for control in artifact["invalid_controls"]:
        observed = None
        try:
            validate(control["input"], int(control["ambient_dim"]))
        except ValueError as error:
            observed = str(error)
        assert observed == control["error"] == control["observed"]
        assert control["passed"] is True

    summary = artifact["summary"]
    assert summary["audit_cases"] == len(regenerated) == 120
    assert summary["audit_failures"] == 0
    assert summary["proof_cases"] == len(verified) == 2
    assert summary["invalid_control_failures"] == 0
    assert summary["transformed_cases"] > 0
    assert summary["audit_trace_steps"] == sum(record["trace_steps"] for record in regenerated)
    assert summary["proof_trace_steps"] == sum(item["trace_steps"] for item in verified)

    exhaustive_count = exhaustive_scalar_confluence()
    print(
        json.dumps(
            {
                "audit_cases": len(regenerated),
                "proof_cases": len(verified),
                "replayed_proof_steps": summary["proof_trace_steps"],
                "exhaustive_scalar_sequences": exhaustive_count,
                "semantic_digest": digest(verified),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verifier FROZEN.json")
    main(sys.argv[1])
