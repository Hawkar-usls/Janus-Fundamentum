#!/usr/bin/env python3
import csv, hashlib, io, json, math, statistics, urllib.request
from collections import defaultdict
from pathlib import Path

PRIMARY = {
    "name": "gradlab_CtTrajectories",
    "url": "https://raw.githubusercontent.com/gradlab/CtTrajectories/f02192d0ad38cb5e1c2009fb16b139166ae99d86/data/ct_dat_clean.csv",
    "git_blob_sha": "6e85916e210e4e434631e7d3f7b11398ea1800bf",
    "subject": "Person.ID", "offset": "Date.Index", "ct": "CT.Mean"
}
REPLICATION = {
    "name": "skissler_CtTrajectories_B117",
    "url": "https://raw.githubusercontent.com/skissler/CtTrajectories_B117/9a5b14eeb01d7c4b26eec80932d28eb3e9349ca1/data/ct_dat_refined.csv",
    "git_blob_sha": "14c727f5e7e858635bb1c43bce17032ac4726811",
    "subject": "PersonIDClean", "offset": "TestDateIndex", "ct": "CtT1"
}
OFFSETS = list(range(1,8))
MIN_MATCHED = 10
MEDIAN_THRESHOLD = 1.0
P_THRESHOLD = 0.01
TOL = 1e-9


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def fetch(spec):
    with urllib.request.urlopen(spec["url"], timeout=30) as r:
        data = r.read()
    got = git_blob_sha(data)
    if got != spec["git_blob_sha"]:
        raise RuntimeError(f"blob mismatch for {spec['name']}: {got} != {spec['git_blob_sha']}")
    return data


def finite_float(x):
    if x is None: return None
    s = str(x).strip()
    if not s or s.upper() in {"NA","NAN","NULL","NONE"}: return None
    try: v = float(s)
    except ValueError: return None
    return v if math.isfinite(v) else None


def binom_cdf(k,n):
    return sum(math.comb(n,j) for j in range(0,k+1)) / (2**n)


def binom_sf_inclusive(k,n):
    return sum(math.comb(n,j) for j in range(k,n+1)) / (2**n)


def sign_p(values):
    nz = [x for x in values if abs(x) > 1e-12]
    n = len(nz)
    if n == 0: return 1.0, 0, 0, 0
    pos = sum(x > 0 for x in nz)
    neg = n - pos
    p = min(1.0, 2 * min(binom_cdf(pos,n), binom_sf_inclusive(pos,n)))
    return p, n, pos, neg


def parse_pairs(data, spec):
    text = data.decode("utf-8-sig")
    rows = csv.DictReader(io.StringIO(text))
    by_subject_offset = defaultdict(list)
    input_rows = 0
    finite_rows = 0
    for row in rows:
        input_rows += 1
        sid = row.get(spec["subject"])
        off = finite_float(row.get(spec["offset"]))
        ct = finite_float(row.get(spec["ct"]))
        if sid is None or off is None or ct is None: continue
        finite_rows += 1
        by_subject_offset[(str(sid), off)].append(ct)
    collapsed = {}
    duplicate_keys = 0
    for key, vals in by_subject_offset.items():
        if len(vals) > 1: duplicate_keys += 1
        collapsed[key] = statistics.median(vals)
    subjects = sorted(set(k[0] for k in collapsed))
    return collapsed, subjects, {"input_rows":input_rows,"finite_rows":finite_rows,"subjects_with_finite_ct":len(subjects),"duplicate_subject_offset_keys":duplicate_keys}


def exact_lookup(collapsed, sid, target):
    hits = [v for (s,o),v in collapsed.items() if s == sid and abs(o-target) <= TOL]
    if not hits: return None
    return statistics.median(hits)


def analyze(data, spec):
    collapsed, subjects, meta = parse_pairs(data,spec)
    per_offset = []
    first = None
    for d in OFFSETS:
        residuals = []
        for sid in subjects:
            pre = exact_lookup(collapsed,sid,-float(d))
            post = exact_lookup(collapsed,sid,float(d))
            if pre is not None and post is not None:
                residuals.append(post-pre)
        n = len(residuals)
        med = statistics.median(residuals) if residuals else None
        p, n_nonzero, pos, neg = sign_p(residuals)
        passes = bool(n >= MIN_MATCHED and med is not None and abs(med) >= MEDIAN_THRESHOLD and p <= P_THRESHOLD)
        rec = {
            "offset_day":d,"n_matched":n,"median_R_ct":med,"sign_test_p":p if residuals else None,
            "n_nonzero":n_nonzero,"positive_R":pos,"negative_R":neg,"criterion_pass":passes
        }
        per_offset.append(rec)
        if first is None and passes:
            first = rec.copy()
    return {"dataset":spec["name"],"meta":meta,"per_offset":per_offset,"first_break":first}


def direction(rec):
    if rec is None or rec["median_R_ct"] is None: return None
    return "NEGATIVE" if rec["median_R_ct"] < 0 else ("POSITIVE" if rec["median_R_ct"] > 0 else "ZERO")


def main():
    primary_bytes = fetch(PRIMARY)
    repl_bytes = fetch(REPLICATION)
    primary = analyze(primary_bytes,PRIMARY)
    repl = analyze(repl_bytes,REPLICATION)
    pf = primary["first_break"]
    rf = repl["first_break"]
    if pf is None:
        repl_verdict = "NOT_EVALUABLE_PRIMARY_NO_FIRST_BREAK"
    elif rf is None:
        repl_verdict = "UNKNOWN_REPLICATION_NO_QUALIFYING_FIRST_BREAK"
    else:
        same_dir = direction(pf) == direction(rf)
        near = abs(pf["offset_day"] - rf["offset_day"]) <= 2
        repl_verdict = "PASS" if same_dir and near else "FAIL"
    result = {
      "experiment_id":"C030_META_REGISTRY_FIRST_BREAK_VIRAL_TRAJECTORY_RESULT_v1",
      "prereg_commit":"88fe44a3ea23031134e10fe2ae9dbfc7bc8e8da8",
      "schema_binding_commit":"c2f1754931df809185fc1ea8128d879e82232b50",
      "status":"COMPUTATION_COMPLETE",
      "input_integrity":{
        "primary_git_blob_sha":git_blob_sha(primary_bytes),
        "primary_sha256":hashlib.sha256(primary_bytes).hexdigest(),
        "replication_git_blob_sha":git_blob_sha(repl_bytes),
        "replication_sha256":hashlib.sha256(repl_bytes).hexdigest()
      },
      "frozen_rule":{"offsets":OFFSETS,"min_matched":MIN_MATCHED,"median_abs_threshold_ct":MEDIAN_THRESHOLD,"sign_p_threshold":P_THRESHOLD},
      "primary":primary,
      "replication":repl,
      "replication_verdict":repl_verdict,
      "directional_prediction_primary": "HIT" if direction(pf)=="NEGATIVE" else ("MISS" if pf is not None else "UNKNOWN"),
      "claim_ceiling":{
        "observable_computed":True,"scientific_novelty":False,"mechanism_identified":False,"scientific_breakthrough":False,
        "reason":"Novelty/material consequence and independent replication require separate post-result gates."
      }
    }
    Path("out").mkdir(exist_ok=True)
    out = Path("out/C030_META_REGISTRY_FIRST_BREAK_RESULT.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
    compact = {
      "primary_first_break":pf,"primary_direction":direction(pf),"replication_first_break":rf,"replication_direction":direction(rf),
      "replication_verdict":repl_verdict,"primary_meta":primary["meta"],"replication_meta":repl["meta"]
    }
    print("C030_COMPACT="+json.dumps(compact,sort_keys=True))

if __name__ == "__main__": main()
