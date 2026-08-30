#!/usr/bin/env python3
import csv
import hashlib
import io
import json
import math
import random
import statistics
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

TARGET = {
    "url": "https://raw.githubusercontent.com/BROOKELAB/Viral-dynamics-modeling/8d71ca82ac453a4b3c3c13d61a7174fbed4bdf8d/Data/data_samples.csv",
    "git_blob_sha": "a4b5cd9e06af494c859f9fefab194a703500af01",
}
PREREG_COMMIT = "f4a85baaa4de6433947649dddae0650863a26fea"
SCHEMA_COMMIT = "0a2272e6c6e67333436773d9e64116a1592fb146"
SEED = 31031
N_PERM = 1000
MIN_TRANSITIONS = 30
MIN_SUBJECTS = 10
PASS_GAIN = 0.10
PASS_P = 0.01
FAIL_P = 0.05
TOL = 1e-9


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def fetch_target():
    with urllib.request.urlopen(TARGET["url"], timeout=30) as r:
        data = r.read()
    got = git_blob_sha(data)
    if got != TARGET["git_blob_sha"]:
        raise RuntimeError(f"target blob mismatch: {got} != {TARGET['git_blob_sha']}")
    return data


def finite_float(x):
    if x is None:
        return None
    s = str(x).strip()
    if not s or s.upper() in {"NA", "NAN", "NULL", "NONE"}:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def load_unique_rows(data: bytes):
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    grouped = defaultdict(list)
    for raw in rows:
        sid = str(raw.get("Ind", "")).strip()
        time = finite_float(raw.get("Time"))
        if not sid or time is None:
            continue
        grouped[(sid, time)].append(raw)
    unique = {}
    ambiguous = []
    for key, vals in grouped.items():
        if len(vals) == 1:
            r = vals[0]
            unique[key] = {
                "subject": key[0],
                "time": key[1],
                "nasal": finite_float(r.get("Nasal_CN")),
                "saliva": finite_float(r.get("Saliva_Ct")),
                "culture": finite_float(r.get("Virus_pos_days")),
            }
        else:
            ambiguous.append({"subject": key[0], "time": key[1], "raw_rows": len(vals)})
    return unique, {
        "input_rows": len(rows),
        "subject_time_keys": len(grouped),
        "unique_subject_time_keys": len(unique),
        "ambiguous_subject_time_keys": len(ambiguous),
        "ambiguous_examples": ambiguous[:10],
    }


def lookup(unique, sid, target_time):
    # Exact numeric time equality, bound at tolerance 1e-9.
    direct = unique.get((sid, target_time))
    if direct is not None:
        return direct
    hits = [v for (s, t), v in unique.items() if s == sid and abs(t - target_time) <= TOL]
    return hits[0] if len(hits) == 1 else None


def construct_endpoint(unique, modality):
    transitions = []
    for (sid, t), cur in sorted(unique.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        nxt = lookup(unique, sid, t + 1.0)
        if nxt is None or cur["culture"] is None:
            continue
        if modality == "nasal":
            current = cur["nasal"]
            future = nxt["nasal"]
            boundary = 48.0
        elif modality == "saliva":
            current = cur["saliva"]
            future = nxt["saliva"]
            boundary = 47.0
        else:
            raise ValueError(modality)
        if current is None or future is None:
            continue
        if current >= boundary or future >= boundary:
            continue
        transitions.append({
            "subject": sid,
            "time": float(t),
            "current": float(current),
            "culture": float(cur["culture"]),
            "outcome": float(future - current),
        })
    return transitions


def fit_predict(train, test, enriched, culture_override=None):
    def features(row, idx=None):
        c = row["culture"] if culture_override is None else culture_override[idx]
        base = [1.0, row["current"], row["time"]]
        if enriched:
            base.append(c)
        return base

    X = []
    y = []
    for i, r in train:
        X.append(features(r, i))
        y.append(r["outcome"])
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    preds = []
    for i, r in test:
        preds.append(float(np.dot(np.asarray(features(r, i), dtype=float), beta)))
    return preds


def loso_predictions(transitions, enriched, culture_override=None):
    subjects = sorted({r["subject"] for r in transitions})
    indexed = list(enumerate(transitions))
    predictions = [None] * len(transitions)
    fold_info = []
    for sid in subjects:
        test = [(i, r) for i, r in indexed if r["subject"] == sid]
        train = [(i, r) for i, r in indexed if r["subject"] != sid]
        if len(train) < (4 if enriched else 3):
            fold_info.append({"subject": sid, "status": "UNSCORABLE_TRAIN_TOO_SMALL", "n_test": len(test)})
            continue
        preds = fit_predict(train, test, enriched, culture_override=culture_override)
        for (i, _), p in zip(test, preds):
            predictions[i] = p
        fold_info.append({"subject": sid, "status": "SCORED", "n_test": len(test), "n_train": len(train)})
    return predictions, fold_info


def mae(transitions, predictions):
    vals = [abs(r["outcome"] - p) for r, p in zip(transitions, predictions) if p is not None]
    return float(statistics.fmean(vals)) if vals else None, len(vals)


def endpoint_analysis(transitions):
    subjects = sorted({r["subject"] for r in transitions})
    eligibility = {"n_transitions": len(transitions), "n_subjects": len(subjects)}
    if len(transitions) < MIN_TRANSITIONS or len(subjects) < MIN_SUBJECTS:
        return {
            "eligibility": eligibility,
            "terminal": "EVIDENCE_INSUFFICIENT",
            "reason": "frozen minimum transitions/subjects not reached",
        }

    pred_a, folds_a = loso_predictions(transitions, enriched=False)
    pred_b, folds_b = loso_predictions(transitions, enriched=True)
    mae_a, n_a = mae(transitions, pred_a)
    mae_b, n_b = mae(transitions, pred_b)
    if mae_a is None or mae_b is None or mae_a <= 0 or n_a != len(transitions) or n_b != len(transitions):
        return {
            "eligibility": eligibility,
            "terminal": "EVIDENCE_INSUFFICIENT",
            "reason": "not all frozen LOSO predictions were scoreable or baseline MAE nonpositive",
            "folds_A": folds_a,
            "folds_B": folds_b,
        }

    observed_gain = (mae_a - mae_b) / mae_a
    rng = random.Random(SEED)
    base_culture = [r["culture"] for r in transitions]
    null_gains = []
    for _ in range(N_PERM):
        perm = list(base_culture)
        rng.shuffle(perm)
        pred_perm, _ = loso_predictions(transitions, enriched=True, culture_override=perm)
        m_perm, n_perm = mae(transitions, pred_perm)
        if m_perm is None or n_perm != len(transitions):
            raise RuntimeError("permutation fold became unscorable")
        null_gains.append((mae_a - m_perm) / mae_a)
    p = (1 + sum(g >= observed_gain for g in null_gains)) / (N_PERM + 1)

    if observed_gain >= PASS_GAIN and p <= PASS_P:
        terminal = "PASS"
    elif observed_gain <= 0 or p > FAIL_P:
        terminal = "FAIL"
    else:
        terminal = "EVIDENCE_INSUFFICIENT"

    return {
        "eligibility": eligibility,
        "terminal": terminal,
        "MAE_A": mae_a,
        "MAE_B": mae_b,
        "relative_MAE_gain": observed_gain,
        "permutation_p": p,
        "null_gain_summary": {
            "iterations": len(null_gains),
            "min": min(null_gains),
            "median": float(statistics.median(null_gains)),
            "mean": float(statistics.fmean(null_gains)),
            "max": max(null_gains),
            "count_ge_observed": sum(g >= observed_gain for g in null_gains),
        },
        "culture_distribution": {
            "min": min(base_culture),
            "median": float(statistics.median(base_culture)),
            "max": max(base_culture),
            "counts": dict(sorted(Counter(str(x) for x in base_culture).items())),
        },
        "folds_A": folds_a,
        "folds_B": folds_b,
    }


def main():
    data = fetch_target()
    unique, row_meta = load_unique_rows(data)
    nasal = construct_endpoint(unique, "nasal")
    saliva = construct_endpoint(unique, "saliva")

    primary = endpoint_analysis(nasal)
    secondary = endpoint_analysis(saliva)
    result = {
        "experiment_id": "C031_INFECTIOUS_STATE_FUTURE_INFORMATION_GAIN_RESULT_v1",
        "prereg_commit": PREREG_COMMIT,
        "schema_binding_commit": SCHEMA_COMMIT,
        "status": "COMPUTATION_COMPLETE",
        "input_integrity": {
            "git_blob_sha": git_blob_sha(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        },
        "row_binding": row_meta,
        "primary_nasal_endpoint": primary,
        "secondary_saliva_endpoint": secondary,
        "frozen_thresholds": {
            "PASS_gain": PASS_GAIN,
            "PASS_p": PASS_P,
            "FAIL_gain_nonpositive": True,
            "FAIL_p_above": FAIL_P,
            "min_transitions": MIN_TRANSITIONS,
            "min_subjects": MIN_SUBJECTS,
            "permutations": N_PERM,
            "seed": SEED,
        },
        "claim_ceiling": {
            "predictive_information_gain_tested": True,
            "causation": False,
            "scientific_novelty": False,
            "independent_replication": False,
            "scientific_breakthrough": False,
            "outreach": "BLOCKED",
        },
    }
    Path("out").mkdir(exist_ok=True)
    out = Path("out/C031_INFECTIOUS_STATE_FUTURE_INFORMATION_GAIN_RESULT.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    compact = {
        "primary": {k: primary.get(k) for k in ["terminal", "eligibility", "MAE_A", "MAE_B", "relative_MAE_gain", "permutation_p"]},
        "secondary": {k: secondary.get(k) for k in ["terminal", "eligibility", "MAE_A", "MAE_B", "relative_MAE_gain", "permutation_p"]},
        "ambiguous_subject_time_keys": row_meta["ambiguous_subject_time_keys"],
    }
    print("C031_COMPACT=" + json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
