import itertools, json, math, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_dense_cardinality.apma_dense_cardinality import (
    compile_c023_dense_image, eval_cardinality, recognize_complete_negative_triples,
    update_cardinality,
)


def dense_source(n):
    return tuple(itertools.combinations(range(1, n+1), 3))


def encode_c023(source, n):
    horn = []
    for clause in source:
        falsity = [n + v for v in clause]
        horn.append(tuple(-v for v in falsity))
    affine = tuple((((1 << (i-1)) | (1 << (n+i-1))), 1) for i in range(1, n+1))
    return tuple(horn), affine


def eval_source(source, assignment):
    return all(any(bool(assignment[v]) for v in clause) for clause in source)


def replay_small(n, carrier):
    source = dense_source(n)
    checked = 0
    for bits in itertools.product((False, True), repeat=n):
        x = {i+1: bits[i] for i in range(n)}
        c = {n+i: not bits[i-1] for i in range(1, n+1)}
        if eval_source(source, x) != eval_cardinality(carrier, c):
            return False, checked
        checked += 1
    return True, checked


def corruption_controls(n=8):
    source = dense_source(n)
    horn, affine = encode_c023(source, n)
    source_vars = tuple(range(1, n+1))
    falsity_vars = tuple(range(n+1, 2*n+1))
    base = compile_c023_dense_image(horn, affine, source_vars, falsity_vars)
    assert base is not None
    missing = horn[:-1]
    duplicate_patch = horn[:-1] + (horn[0],)
    width_bad = horn[:-1] + ((-(n+1), -(n+2)),)
    affine_bad = affine[:-1]
    return {
        "missing_triple_rejected": compile_c023_dense_image(missing, affine, source_vars, falsity_vars) is None,
        "duplicate_patch_rejected": compile_c023_dense_image(duplicate_patch, affine, source_vars, falsity_vars) is None,
        "nonuniform_width_rejected": compile_c023_dense_image(width_bad, affine, source_vars, falsity_vars) is None,
        "missing_neq_rejected": compile_c023_dense_image(horn, affine_bad, source_vars, falsity_vars) is None,
    }


def threshold_corruption(n=6):
    source = dense_source(n)
    horn, affine = encode_c023(source, n)
    carrier = compile_c023_dense_image(horn, affine, tuple(range(1,n+1)), tuple(range(n+1,2*n+1)))
    low = dict(carrier); low["k"] = 1
    high = dict(carrier); high["k"] = 3
    c_two = {n+i: (i <= 2) for i in range(1,n+1)}
    c_three = {n+i: (i <= 3) for i in range(1,n+1)}
    return {
        "wrong_k_1_rejected_by_witness": (not eval_cardinality(low, c_two)) and eval_cardinality(carrier, c_two),
        "wrong_k_3_rejected_by_counterexample": eval_cardinality(high, c_three) and (not eval_cardinality(carrier, c_three)),
    }


def update_controls(n=10):
    source = dense_source(n)
    horn, affine = encode_c023(source, n)
    carrier = compile_c023_dense_image(horn, affine, tuple(range(1,n+1)), tuple(range(n+1,2*n+1)))
    a = {n+1: True, n+2: False, n+3: True}
    u = update_cardinality(carrier, a)
    b = {n+4: False, n+5: False}
    bad = update_cardinality(carrier, {n+1:True,n+2:True,n+3:True})
    return {
        "residual_kind": u["kind"],
        "residual_k": u.get("k"),
        "residual_variable_count": len(u.get("variables", ())),
        "false_after_three_true": bad["kind"] == "FALSE",
        "benign_second_update_kind": update_cardinality(u, b)["kind"],
    }


def captain_guard():
    text = Path(__file__).with_name('apma_dense_cardinality.py').read_text(encoding='utf-8').lower()
    forbidden = ['itertools.product', 'dpll(', 'brute', 'solve_all_assignments', 'subsets(']
    hits = [x for x in forbidden if x in text]
    return {
        "pass": not hits,
        "hits": hits,
        "rule": "candidate recognition/morph may inspect the explicit clause family but may not enumerate assignment cubes or invoke a general SAT solver",
    }


def main():
    t0 = time.perf_counter()
    sizes = []
    small_replay = []
    for n in (4,5,6,7,8,12,16,24,32,48,64):
        source = dense_source(n)
        horn, affine = encode_c023(source, n)
        carrier = compile_c023_dense_image(horn, affine, tuple(range(1,n+1)), tuple(range(n+1,2*n+1)))
        assert carrier is not None
        sizes.append({
            "n": n,
            "source_clauses": len(source),
            "expected_clauses": math.comb(n,3),
            "carrier_variables": len(carrier["variables"]),
            "carrier_k": carrier["k"],
            "carrier_json_bytes": len(json.dumps(carrier, sort_keys=True)),
        })
        if n <= 8:
            ok, checked = replay_small(n, carrier)
            small_replay.append({"n":n,"pass":ok,"assignments":checked})
    corrupt = corruption_controls()
    thresholds = threshold_corruption()
    updates = update_controls()
    guard = captain_guard()
    all_ok = guard["pass"] and all(x["pass"] for x in small_replay) and all(corrupt.values()) and all(thresholds.values()) and updates["false_after_three_true"]
    verdict = "PASS_APMA_DENSE_TRIPLES_CARDINALITY_MORPH" if all_ok else "FAIL_APMA_DENSE_TRIPLES_CARDINALITY_MORPH"
    out = {
        "schema": "JANUS_TRUMP_APMA_DENSE_TRIPLES_CARDINALITY_GATE_V1",
        "verdict": verdict,
        "morph": "COMPLETE_NEGATIVE_3_UNIFORM_HORN_TO_AT_MOST_2",
        "identity": "AND_{i<j<k}(not c_i OR not c_j OR not c_k) iff SUM_i c_i <= 2",
        "captain_obvious_guard": guard,
        "size_ladder": sizes,
        "small_truth_table_replay": small_replay,
        "corruption_controls": corrupt,
        "threshold_controls": thresholds,
        "update_controls": updates,
        "runtime_ms": round((time.perf_counter()-t0)*1000,3),
        "interpretation": "the literal-branching depth-n killer family has an exact O(n)-size cardinality carrier discoverable directly from the explicit complete triple structure",
        "limitation": "this is a scoped symmetry/cardinality morph for the complete dense-positive-triples family, not a universal APMA compiler",
        "scientific_status": {"SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN","Pi_negative_evidence_weight":0},
        "next": "search for proof-carrying threshold/cardinality motifs beyond complete symmetry and test non-symmetric dense reduction images",
    }
    print(json.dumps(out, sort_keys=True))
    if not all_ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
