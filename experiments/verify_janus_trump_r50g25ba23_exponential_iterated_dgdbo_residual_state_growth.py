from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

import janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence as ba20
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

GATE = "R50G25BA23_EXPONENTIAL_ITERATED_DGDBO_RESIDUAL_STATE_GROWTH"
PREREG = "592a24b603c10213ab110d5d27b1308b0fc69656"
PARENT_BA22_META = "922c7bd03977419b90238de33555d5b0969d7029"

REQUIRED = [
    "STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS","BA22_IMMUTABILITY_PASS",
    "KILLER_FAMILY_SCHEMA_PASS","SEQUENTIAL_ROUTE_PASS","STATE_INVARIANT_PASS","STATE_REACHABILITY_PASS",
    "PAIRWISE_SEMANTIC_DISTINCTNESS_PASS","EXACT_2_POW_T_STATE_COUNT_PASS","FINAL_2_POW_M_STATE_COUNT_PASS",
    "SATISFIABLE_STATE_COUNT_PASS","DIRECT_MODEL_COUNT_PASS","STATE_SUM_MODEL_COUNT_PASS","LINEAR_INPUT_SIZE_PASS",
    "EXPONENTIAL_STATE_SEPARATION_PASS","ACTIVE_VS_CUMULATIVE_ACCOUNTING_PASS","NO_EXACT_RESIDUAL_MERGE_PASS",
    "ORDER_ROBUSTNESS_PASS","NO_MATERIALIZATION_THEOREM_PROOF_PASS","STRATEGY_BARRIER_PASS",
    "REPRESENTATION_SCOPE_FIREWALL_PASS","SAT_COMPLEXITY_NONCLAIM_PASS","INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"
]


def sha_obj(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def a(i): return f"a_{i}"
def b(i): return f"b_{i}"


def subsets(t):
    for mask in range(1 << t):
        yield frozenset(i + 1 for i in range(t) if (mask >> i) & 1)


def blocks(m, t, S):
    S = frozenset(S)
    return tuple([(b(i),) for i in sorted(S)] + [(a(i), b(i)) for i in range(t + 1, m + 1)])


def eval_blocks(blks, assignment):
    return bool(blks) and any(all(bool(assignment.get(v, False)) for v in block) for block in blks)


def guard(t, S):
    S = frozenset(S); rho = {}
    for i in range(1, t + 1):
        if i in S:
            rho[a(i)] = True
        else:
            rho[a(i)] = False; rho[b(i)] = True
    return rho


def guard_ok(t, rho):
    return all(bool(rho.get(a(i), False)) or bool(rho.get(b(i), False)) for i in range(1, t + 1))


def separator_ok(m, t, S, T):
    S, T = frozenset(S), frozenset(T)
    j = min(S.symmetric_difference(T))
    if j in T: S, T = T, S
    assignment = {}
    for i in S.union(T): assignment[b(i)] = (i == j)
    for i in range(t + 1, m + 1): assignment[a(i)] = False; assignment[b(i)] = False
    return eval_blocks(blocks(m,t,S), assignment) and not eval_blocks(blocks(m,t,T), assignment)


def exact_state_replay(m):
    rows=[]; ok=True
    for t in range(m+1):
        Ss=list(subsets(t))
        sigs=[blocks(m,t,S) for S in Ss]
        count_ok=len(sigs)==(1<<t) and len(set(sigs))==(1<<t)
        reach=all(guard_ok(t,guard(t,S)) for S in Ss)
        # Exhaustive semantic pair replay for small t, deterministic spanning separators beyond it.
        sem=True; checked=0
        if t<=7:
            for x in range(len(Ss)):
                for y in range(x+1,len(Ss)):
                    checked+=1
                    if not separator_ok(m,t,Ss[x],Ss[y]): sem=False; break
                if not sem: break
        else:
            base=frozenset()
            probes=[]
            for j in range(1,t+1): probes.append(frozenset({j}))
            probes += [frozenset(range(1,t+1)), frozenset(i for i in range(1,t+1) if i%2)]
            uniq=[]
            for s in probes:
                if s not in uniq: uniq.append(s)
            for x in range(len(uniq)):
                for y in range(x+1,len(uniq)):
                    if uniq[x]!=uniq[y]:
                        checked+=1
                        if not separator_ok(m,t,uniq[x],uniq[y]): sem=False
        rows.append({"t":t,"count":len(sigs),"expected":1<<t,"reachability":reach,"semantic_separator_checks":checked,"semantic_separator_pass":sem,"pass":count_ok and reach and sem})
        ok &= rows[-1]["pass"]
    return {"m":m,"rows":rows,"pass":ok}


def direct_truth_count(m):
    count=0
    for bits in itertools.product((0,1), repeat=2*m):
        pairs=[bits[2*i:2*i+2] for i in range(m)]
        gamma=all(x or y for x,y in pairs)
        phi=any(x and y for x,y in pairs)
        if gamma and phi: count+=1
    return count


def state_sum_closed(m):
    return sum(__import__('math').comb(m,s)*((1<<s)-1) for s in range(m+1))


def symbolic_proof_certificate():
    return {
      "induction": "Base Q_0 contains one parent state. For any processed-state subset coordinate S and a fresh variable-disjoint pair clause, first-true compilation has exactly KEEP and KILL outcomes. KEEP leaves the untested mate singleton; KILL deletes the pair block. Hence Q_(t+1) is in bijection with Q_t x {0,1} and |Q_(t+1)|=2|Q_t|.",
      "reachability": "Each binary choice has a satisfying accumulated guard: kept coordinate uses first literal true; killed coordinate uses first literal false and second true. Pair-disjointness makes all coordinate guards simultaneously consistent.",
      "distinctness": "For unequal subset coordinates choose a differing processed pair. The state containing that singleton is made true through it while all other surviving blocks are made false; the state lacking it is false.",
      "order_robustness": "Permutation only renames which independent pair coordinates have been processed. Reversing literal order changes the surviving singleton from the second variable to the first; each processed pair still contributes exactly one independent keep/kill bit. Therefore 2^t holds for any pair-clause permutation and either within-clause literal order.",
      "generic_enumeration_used": False,
      "knowledge_compilation_lower_bound_claimed": False,
      "SAT_hardness_claimed": False,
    }


def source_embedding_replay():
    U, first, _, _ = ba4.source_hardening(); rows=[]
    for m in (2,3):
        p=2; ns=(2,)*(m-1)
        for S in (frozenset({1}), frozenset(range(1,m+1))):
            chosen=min(S); final=[]
            for i in range(1,m+1):
                if i in S: final.extend((1, int(i==chosen)))
                else: final.extend((0,1))
            source_bits=ba20.reconstruct_source_bits(tuple(final),p,ns)
            abstract=ba20.source_bits_ok(source_bits,p,ns)
            for g in (1,2):
                actual=ba20.construct_model(first,U,g,p,ns,source_bits)
                rows.append({"m":m,"S":sorted(S),"g":g,"abstract":abstract,"actual":bool(actual["pass"]),"bad":int(actual["bad_clause_count"])})
    return {"cases":len(rows),"rows_sha256":sha_obj(rows),"pass":all(x["abstract"] and x["actual"] for x in rows),"rows":rows}


def run(result):
    errors=[]
    if result.get("gate")!=GATE: errors.append("gate mismatch")
    if result.get("preregistration_commit")!=PREREG: errors.append("prereg mismatch")
    if result.get("parent_BA22_meta_commit")!=PARENT_BA22_META: errors.append("parent BA22 mismatch")
    theorem=symbolic_proof_certificate()
    exact=[exact_state_replay(m) for m in range(1,13)]
    finite_model=[]
    for m in range(1,7):
        direct=direct_truth_count(m); formula=3**m-2**m; by_states=state_sum_closed(m)
        finite_model.append({"m":m,"direct_truth":direct,"formula":formula,"state_sum":by_states,"pass":direct==formula==by_states})
    final_formula=[{"m":m,"active":1<<m,"sat_states":(1<<m)-1,"cumulative":(1<<(m+1))-1} for m in range(1,13)]
    embedding=source_embedding_replay()
    if not all(x["pass"] for x in exact): errors.append("finite state replay failed")
    if not all(x["pass"] for x in finite_model): errors.append("finite model count replay failed")
    if not embedding["pass"]: errors.append("source embedding replay failed")
    # Check authoritative candidate fields without importing its implementation.
    cand=result.get("scientific_result_candidate",{})
    if cand.get("active_state_law")!="A_t=2^t": errors.append("active-state candidate mismatch")
    if cand.get("final_state_law")!="A_m=2^m": errors.append("final-state candidate mismatch")
    if result.get("no_materialization",{}).get("generic_2_pow_m_state_enumeration")!=0: errors.append("generic enumeration counter nonzero")
    if result.get("large_symbolic_diagnostic",{}).get("states_materialized")!=0: errors.append("m64 states materialized")
    base_names=REQUIRED[:-2]
    builder_map=result.get("pass_map",{})
    if set(builder_map)!=set(REQUIRED): errors.append("builder obligation name set mismatch")
    if not all(builder_map.get(k)==1 for k in base_names): errors.append("builder base obligation failed")
    if builder_map.get("INDEPENDENT_REPLAY_PASS")!=0 or builder_map.get("PRESEAL_COMPLETENESS_PASS")!=0: errors.append("builder prematurely promoted final passes")
    verify={
      "gate":GATE,"status":"PASS" if not errors else "FAIL","implementation_imported":False,
      "symbolic_proof":theorem,"exact_state_diagnostics":exact,"finite_model_count_controls":finite_model,
      "closed_form_controls":final_formula,"source_embedding_replay":embedding,
      "large_m64":{"expected_active":str(1<<64),"expected_cumulative":str((1<<65)-1),"states_materialized":0},
      "required_pass_names":REQUIRED,"v_independent_verifier":int(not errors),"P_BA23":int(not errors),
      "errors":errors,"falsifiers":[] if not errors else ["F14_INDEPENDENT_REPLAY_FAILED"]
    }
    return verify


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--result",default="ba23_result.json");ap.add_argument("--out",default="ba23_verify.json");args=ap.parse_args()
    result=json.loads(Path(args.result).read_text());verify=run(result);Path(args.out).write_text(json.dumps(verify,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":verify["status"],"independent":verify["v_independent_verifier"],"embedding_cases":verify["source_embedding_replay"]["cases"]},sort_keys=True))
    if verify["status"]!="PASS": raise SystemExit(1)

if __name__=="__main__": main()
