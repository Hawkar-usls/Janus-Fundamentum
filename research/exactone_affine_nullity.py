#!/usr/bin/env python3
"""JANUS Exact-One affine-kernel enumerator (proof-carrying, bounded nullity).

High primal width and arbitrarily many cycles are allowed. Exact-One implies
an affine equation over GF(2), but the converse is false. We enumerate ONLY
the free coordinates of that necessary affine system and test *every*
candidate against original Exact-One clauses. Never call this a general
polynomial SAT algorithm; worst-case nullity may be n. No Rowan API calls.

All UNSAT results carry independently checkable parity-lineage or a
complete bounded enumeration of violated original clauses.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

from exactone_parity_preprocessor import validate, digest, solution_set

SCHEMA = "janus.fundamentum.exactone_affine_nullity_v1"
MAX_FREE_DIMENSION = 10


def parity_clause(clause):
    """EXACTLY-ONE(literals) implies XOR(literals)=1, even if repeated."""
    mask, rhs = 0, 1
    for lit in clause:
        mask ^= 1 << (abs(lit)-1)
        rhs ^= int(lit < 0)
    return mask, rhs


def row_system(case):
    n, clauses = validate(case)
    out = []
    for ci,c in enumerate(clauses):
        mask, rhs = parity_clause(c)
        out.append((mask,rhs,1 << ci))
    return out


def _rref(case):
    """Canonical low-bit-pivot RREF with original-clause XOR lineages."""
    n, _ = validate(case)
    basis = {}
    contradiction = None
    for mask,rhs,lineage in row_system(case):
        for pivot in sorted(basis):
            if (mask >> pivot) & 1:
                bm,br,bl = basis[pivot]
                mask,rhs,lineage = mask ^ bm, rhs ^ br, lineage ^ bl
        if mask == 0:
            if rhs:
                contradiction = lineage
                break
            continue
        pivot = (mask & -mask).bit_length()-1
        basis[pivot] = (mask,rhs,lineage)
    if contradiction is not None:
        return {"contradiction": contradiction, "rows": [], "free": []}
    # Each row is already reduced against all lower indexed pivots.
    for pivot in sorted(basis,reverse=True):
        bm,br,bl = basis[pivot]
        for other in sorted(basis):
            if other != pivot and (basis[other][0] >> pivot) & 1:
                a,b,c = basis[other]
                basis[other] = a ^ bm,b ^ br,c ^ bl
    rows = [
        {"pivot":p+1,"mask_hex":hex(mask),"rhs":rhs,
         "sources":_source_indices(lin)}
        for p,(mask,rhs,lin) in sorted(basis.items())
    ]
    free = [v for v in range(1,n+1) if (v-1) not in basis]
    return {"contradiction":None,"rows":rows,"free":free}


def _source_indices(lineage):
    result = []
    while lineage:
        lsb = lineage & -lineage
        result.append(lsb.bit_length()-1)
        lineage ^= lsb
    return result


def _candidate_from_rref(rows, free_vars, assignment_index):
    # Lexicographic free-vector bit order: first free coordinate is LSB.
    values = {var: (assignment_index >> i) & 1
              for i,var in enumerate(free_vars)}
    free_mask = sum(values[var] << (var-1) for var in free_vars)
    for row in rows:
        mask = int(row["mask_hex"],16)
        value = row["rhs"] ^ ((mask & free_mask).bit_count() & 1)
        values[row["pivot"]] = value
    return values


def _first_violated_clause(case, values):
    for i,clause in enumerate(case["clauses"]):
        if sum(values[abs(l)] ^ int(l<0) for l in clause) != 1:
            return i
    return None


def _template(case,free_limit):
    return {
        "schema":SCHEMA, "input_sha256":digest(case),
        "max_free_dimension":free_limit,
        "status":None,
        "parity_rank":None,
        "nullity":None,
        "free_variables":[],
        "rref_rows":[],
        "xor_contradiction_sources":None,
        "candidate_rejections":[],
        "winning_candidate_index":None,
        "witness":None,
        "exact_one_check":"EACH_CANDIDATE_IN_ORIGINAL_SIGNED_CLAUSES",
        "worst_case_bound":"O(poly(L) + 2^k * poly(L)), k = XOR nullity",
        "restricted_poly_time_only":True,
        "general_polynomial_exactone_solver":False,
        "rowan_api_calls":0,
        "p_vs_np":"OPEN",
    }


def solve(case,max_free_dimension=4):
    n,clauses=validate(case)
    if (type(max_free_dimension) is not int or max_free_dimension<0
        or max_free_dimension>MAX_FREE_DIMENSION):
        raise ValueError("FREE_DIMENSION_CAP")
    out=_template(case,max_free_dimension)
    rref=_rref(case)
    if rref["contradiction"] is not None:
        out.update(status="UNSAT_XOR",parity_rank=None,nullity=None,
                   xor_contradiction_sources=_source_indices(rref["contradiction"]))
    else:
        rows,free=rref["rows"],rref["free"]
        out.update(parity_rank=len(rows), nullity=len(free),
                   free_variables=free,rref_rows=rows)
        if len(free)>max_free_dimension:
            out["status"]="OPEN_NULLITY_CAP"
        else:
            for i in range(1 << len(free)):
                values=_candidate_from_rref(rows,free,i)
                violated=_first_violated_clause(case,values)
                if violated is None:
                    out.update(status="SAT",winning_candidate_index=i,
                               witness={str(k):v for k,v in sorted(values.items())})
                    break
                out["candidate_rejections"].append(violated)
            if out["status"] is None:
                out["status"]="UNSAT_EXACTONE"
    out["result_sha256"]=digest(out)
    return out


def _independent_xor_sources(case, indices):
    """Verifier reconstructs XOR equation, no call to solver _rref()."""
    mask=0
    rhs=0
    for i in indices:
        m,b=parity_clause(case["clauses"][i])
        mask ^= m
        rhs ^= b
    return mask,rhs


def verify(case,answer):
    """Independent exact proof replay; checks every rejecting candidate."""
    try:
        n,clauses=validate(case)
        if not isinstance(answer,dict) or answer.get("schema")!=SCHEMA:
            return False
        temp=dict(answer)
        recorded_hash=temp.pop("result_sha256",None)
        if recorded_hash!=digest(temp) or answer["input_sha256"]!=digest(case):
            return False
        cap=answer["max_free_dimension"]
        if type(cap) is not int or not 0<=cap<=MAX_FREE_DIMENSION:
            return False
        template=_template(case,cap)
        for key in ("general_polynomial_exactone_solver","restricted_poly_time_only",
                    "rowan_api_calls","p_vs_np","exact_one_check","worst_case_bound"):
            if answer.get(key)!=template[key]:
                return False
        status=answer["status"]
        if status=="UNSAT_XOR":
            sources=answer["xor_contradiction_sources"]
            if (not isinstance(sources,list) or not sources
                or any(type(i) is not int or i<0 or i>=len(clauses) for i in sources)
                or len(sources)!=len(set(sources))):
                return False
            return (_independent_xor_sources(case,sources)==(0,1)
                    and answer["rref_rows"]==[] and answer["free_variables"]==[]
                    and answer["parity_rank"] is None and answer["nullity"] is None
                    and answer["witness"] is None
                    and answer["winning_candidate_index"] is None
                    and answer["candidate_rejections"]==[])
        if status not in ("SAT","UNSAT_EXACTONE","OPEN_NULLITY_CAP"):
            return False
        rows,free=answer["rref_rows"],answer["free_variables"]
        rank=answer["parity_rank"]
        if (not isinstance(rows,list) or not isinstance(free,list)
            or rank!=len(rows) or type(rank) is not int or len(rows)>n
            or answer["nullity"]!=len(free) or rank+len(free)!=n):
            return False
        pivots=[]
        pivotmask=0
        for row in rows:
            if not isinstance(row,dict) or set(row)!={"pivot","mask_hex","rhs","sources"}:
                return False
            p,hexstr,rhs,sources=(row["pivot"],row["mask_hex"],row["rhs"],row["sources"])
            if (type(p) is not int or p<1 or p>n or p in pivots
                or type(rhs) is not int or rhs not in (0,1)
                or type(hexstr) is not str):
                return False
            mask=int(hexstr,16)
            if mask<=0 or mask>>(n) or (mask & (1<<(p-1)))==0:
                return False
            if (not isinstance(sources,list) or not sources or len(set(sources))!=len(sources)
                or any(type(i) is not int or i<0 or i>=len(clauses) for i in sources)):
                return False
            if _independent_xor_sources(case,sources)!=(mask,rhs):
                return False
            pivots.append(p)
            pivotmask |= 1<<(p-1)
        if pivots!=sorted(pivots):
            return False
        if free != [i for i in range(1,n+1) if i not in pivots]:
            return False
        # Check reduced row-echelon property, so these rows exactly describe
        # all solutions of the original XOR relaxation.
        for row in rows:
            mask=int(row["mask_hex"],16)
            if (mask & pivotmask) != 1<<(row["pivot"]-1):
                return False
        # Rank cannot be faked with an incomplete independent row subset:
        # every original equation must be implied by these claimed rows.
        for m,b,_ in row_system(case):
            for row in rows:
                if (m>>(row["pivot"]-1)) & 1:
                    m ^= int(row["mask_hex"],16)
                    b ^= row["rhs"]
            if m or b:
                return False
        if answer["xor_contradiction_sources"] is not None:
            return False
        rejections=answer["candidate_rejections"]
        if not isinstance(rejections,list):
            return False
        if status=="OPEN_NULLITY_CAP":
            return (len(free)>cap and rejections==[]
                    and answer["witness"] is None
                    and answer["winning_candidate_index"] is None)
        if len(free)>cap or len(rejections)>(1<<len(free)):
            return False
        for i,recorded_violation in enumerate(rejections):
            if type(recorded_violation) is not int or recorded_violation<0 or recorded_violation>=len(clauses):
                return False
            values=_candidate_from_rref(rows,free,i)
            if _first_violated_clause(case,values)!=recorded_violation:
                return False
        if status=="UNSAT_EXACTONE":
            return (len(rejections)==1<<len(free)
                    and answer["witness"] is None
                    and answer["winning_candidate_index"] is None)
        i=answer["winning_candidate_index"]
        if (type(i) is not int or i!=len(rejections) or i>=1<<len(free)):
            return False
        values=_candidate_from_rref(rows,free,i)
        if _first_violated_clause(case,values) is not None:
            return False
        return (answer["witness"]=={str(k):v for k,v in sorted(values.items())}
                and len(values)==n)
    except (ValueError,KeyError,TypeError,OverflowError,IndexError,AssertionError):
        return False


def full_pair_fan(leaves,unsat=False):
    """Primal clique K_(leaves+1), so width grows with the number of leaves.

    Hub x1 plus all unordered pairs of leaf variables. For leaves >=4 the
    affine nullity is one, independent of the clique width.
    """
    if type(leaves) is not int or leaves<4:
        raise ValueError("MIN_LEAVES")
    clauses=[[1,i,j] for i in range(2,leaves+2) for j in range(i+1,leaves+2)]
    if unsat:
        # All leaves equal in the XOR relaxation, this triple forces them
        # to one, but every hub/pair clause then violates EXACT-ONE.
        clauses.append([2,3,4])
    return {"n":leaves+1,"clauses":clauses}


def self_test():
    rng=random.Random(20261028)
    controls=[
        {"n":1,"clauses":[[1]]},
        {"n":1,"clauses":[[-1]]},
        {"n":1,"clauses":[[1,1,1]]},
        {"n":1,"clauses":[[1],[-1]]},
        {"n":4,"clauses":[]},
        {"n":3,"clauses":[[1,2,3]]},
        {"n":4,"clauses":[[1,2,3],[1,2,4],[-1,3,4]]},
    ]
    for _ in range(500):
        n=rng.randint(1,8)
        clauses=[]
        for __ in range(rng.randint(0,12)):
            k=rng.choice((1,3))
            clauses.append([
                (v if rng.randrange(2) else -v)
                for v in (rng.randint(1,n) for ___ in range(k))])
        controls.append({"n":n,"clauses":clauses})
    statuses={}
    for case in controls:
        result=solve(case,max_free_dimension=4)
        assert verify(case,result),("CERTIFICATE_REPLAY_REJECT",case,result)
        exact=solution_set(case)
        if result["status"]=="SAT":
            vals={int(k):v for k,v in result["witness"].items()}
            bits=sum(v<<(k-1) for k,v in vals.items())
            assert bits in exact
        elif result["status"].startswith("UNSAT"):
            assert not exact
        else:
            assert result["status"]=="OPEN_NULLITY_CAP"
        statuses[result["status"]]=statuses.get(result["status"],0)+1

    high_sat=full_pair_fan(65)
    high_unsat=full_pair_fan(65,unsat=True)
    sat=solve(high_sat,4)
    unsat=solve(high_unsat,4)
    assert sat["status"]=="SAT" and verify(high_sat,sat)
    assert sat["nullity"]==1
    assert unsat["status"]=="UNSAT_EXACTONE" and verify(high_unsat,unsat)
    assert unsat["nullity"]==0
    # Every variable pair is co-present in some cubic clause. This means a
    # primal clique on all 66 variables and hence treewidth >=65.
    cooccur=set()
    for c in high_sat["clauses"]:
        ids=[abs(x) for x in c]
        for a,b in itertools.combinations(ids,2):
            cooccur.add((min(a,b),max(a,b)))
    assert len(cooccur)==65*66//2
    assert len(high_sat["clauses"])==65*64//2

    opened=solve({"n":16,"clauses":[]},4)
    assert opened["status"]=="OPEN_NULLITY_CAP" and verify({"n":16,"clauses":[]},opened)

    # A rehashed but forged violation cannot certify UNSAT.
    tamper=solve({"n":1,"clauses":[[1,1,1]]},4)
    assert tamper["status"]=="UNSAT_EXACTONE"
    tamper["candidate_rejections"][0]=999999
    tamper["result_sha256"]=digest({k:v for k,v in tamper.items() if k!="result_sha256"})
    assert not verify({"n":1,"clauses":[[1,1,1]]},tamper)

    return {
        "schema":"janus.fundamentum.exactone_affine_nullity_selftest_v1",
        "status":"PASS",
        "independent_small_reference_cases":len(controls),
        "status_counts":statuses,
        "high_width_primal_clique_vertices":66,
        "high_width_proved_treewidth_lower_bound":65,
        "high_width_sat":{"status":sat["status"],"nullity":sat["nullity"]},
        "high_width_unsat":{"status":unsat["status"],"nullity":unsat["nullity"]},
        "all_pair_hub_cubic_clauses":len(high_sat["clauses"]),
        "open_when_large_nullity":"PASS",
        "rehashed_forged_unsat":"REJECTED",
        "complexity":"O(poly(L)+2^k * poly(L)), k = XOR nullity",
        "universal_polynomial_solver":False,
        "p_vs_np":"OPEN",
    }


def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test",action="store_true")
    g.add_argument("--input",type=Path)
    p.add_argument("--max-free-dimension",type=int,default=4)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    if a.self_test:
        result=self_test()
    else:
        case=json.loads(a.input.read_text(encoding="utf-8"))
        result=solve(case,a.max_free_dimension)
        if not verify(case,result):
            raise RuntimeError("AFFINE_NULLITY_CERTIFICATE_REJECTED")
    payload=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if a.output:
        a.output.write_text(payload,encoding="utf-8")
    print(payload)


if __name__=="__main__":
    main()
