#!/usr/bin/env python3
"""R5 SCL-native Cooperative Moment Gearbox with exact LOG_KERNEL.

Independent all-n correctness contract for legal SCL matrices:
- mandatory deterministic exact-one/GF2 propagation;
- degree <=3 exact-rational moment bound on #111-row violations;
- zero moment upper bound can soundly refute a cube;
- LOG_KERNEL exact affine enumeration iff 2^d<=n^c, fixed c<=3;
- remaining cubes split exactly and saved on UNKNOWN_RESOURCE_LIMIT.

No all-n polytime decision theorem: only bounded per-invocation work.
Importable testable frontiers; Python 3.11+ standard library.
"""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from r5_cooperative_scl_coverage_20261015 import (
    choose_branch, fingerprint, gf2_consequences,
    local_consequences, validate_scl, valid_witness, fixtures
)
from r5_fixed_degree_moment_expert_20261015 import (
    log_kernel, moment_bounds
)


def certified_cube_bound(rows,cube,degree):
    return moment_bounds(rows,cube,degree)["bound"]


def certified_frontier_mass(rows,frontier,degree):
    return sum(certified_cube_bound(rows,cube,degree)
               for cube in frontier)


def solve(rows, node_budget=80, moment_degree=3, log_kernel_exponent=1,
          checkpoint=None,resume=None):
    rows=validate_scl(rows)
    n=len(rows)
    if not 0<=moment_degree<=3 or not 0<=log_kernel_exponent<=3:
        raise ValueError("fixed moment_degree and log exponent must be 0..3")
    if node_budget<0:
        raise ValueError("node_budget must be nonnegative")
    fuel=min(node_budget,4*n*n)
    if resume:
        rec=json.loads(Path(resume).read_text(encoding="utf-8"))
        if (rec.get("version")!=1 or
            rec.get("sha256")!=fingerprint(rows) or
            rec.get("moment_degree")!=moment_degree or
            rec.get("log_kernel_exponent")!=log_kernel_exponent):
            raise ValueError("checkpoint graph, version or policy mismatch")
        frontier=[tuple(pair) for pair in rec["frontier"]]
        if len(frontier)>n+1:
            raise ValueError("frontier cannot be a valid depth-first stack")
        for zero,one in frontier:
            if zero<0 or one<0 or zero&one or (zero|one)>>n:
                raise ValueError("invalid checkpoint cube")
        prior=rec["total_visited"]
    else:
        frontier=[(0,0)]
        prior=0
    original=certified_frontier_mass(rows,frontier,moment_degree) if n%3==0 else 0
    event_log=[]
    stats={
        "n":n,"sha256":fingerprint(rows),
        "initial_certified_U":original,
        "visited_this_call":0,
        "previous_visited":prior,
        "moment_degree":moment_degree,
        "kernel_exponent":log_kernel_exponent,
        "certified_shrinks":0,
        "exact_split":0,
        "exact_one_forced":0,
        "gf2_forced":0,
        "moment_zero_cubes":0,
        "kernel_refuted":0,
        "kernel_declines":0,
        "kernel_words_checked":0,
        "proof_events":event_log,
    }
    if n%3:
        stats.update(verdict="UNSAT",reason="3*|x|=n impossible")
        return stats

    def emit(event):
        event_log.append(event)
        del event_log[:-16]

    verdict=None
    witness=None
    while frontier and stats["visited_this_call"]<fuel:
        cube=frontier.pop()
        stats["visited_this_call"]+=1
        ub=certified_cube_bound(rows,cube,moment_degree)
        if ub==0:
            # Moment dual is a full upper-bound proof for this cube.
            stats["moment_zero_cubes"]+=1
            emit({"expert":"MOMENT_ZERO","cube":cube,"U":0})
            continue
        kind,new,_=local_consequences(rows,cube)
        if kind=="CONFLICT":
            emit({"expert":"EXACT_ONE_CONFLICT","cube":cube})
            continue
        if kind=="FORCED":
            assert local_consequences(rows,cube)[1]==new
            assert certified_cube_bound(rows,new,moment_degree)<=ub
            frontier.append(new)
            stats["exact_one_forced"]+=1
            emit({"expert":"EXACT_ONE","U_before":ub,
                  "U_after":certified_cube_bound(rows,new,moment_degree)})
            continue
        kind,new,d=gf2_consequences(rows,cube)
        if kind=="CONFLICT":
            emit({"expert":"GF2_CONFLICT","cube":cube})
            continue
        if kind=="FORCED":
            assert gf2_consequences(rows,cube)[1]==new
            assert certified_cube_bound(rows,new,moment_degree)<=ub
            frontier.append(new)
            stats["gf2_forced"]+=1
            emit({"expert":"GF2","U_before":ub,
                  "U_after":certified_cube_bound(rows,new,moment_degree)})
            continue
        # LOG_KERNEL is a bounded POLYNOMIAL expert (c is fixed <=3).
        kernel=log_kernel(rows,cube,log_kernel_exponent)
        if kernel["status"]=="SAT":
            assert valid_witness(rows,kernel["witness"])
            stats["kernel_words_checked"]+=kernel["checked"]
            witness=kernel["witness"]
            verdict="SAT"
            emit({"expert":"LOG_KERNEL_SAT","checked":kernel["checked"]})
            break
        if kernel["status"]=="UNSAT_CUBE":
            assert log_kernel(rows,cube,log_kernel_exponent)["status"]=="UNSAT_CUBE"
            stats["kernel_words_checked"]+=kernel["checked"]
            stats["kernel_refuted"]+=1
            emit({"expert":"LOG_KERNEL_UNSAT","checked":kernel["checked"]})
            continue
        stats["kernel_declines"]+=1
        v=choose_branch(rows,cube)
        low=(cube[0]|1<<v,cube[1])
        high=(cube[0],cube[1]|1<<v)
        U_low=certified_cube_bound(rows,low,moment_degree)
        U_high=certified_cube_bound(rows,high,moment_degree)
        if U_low+U_high>ub:
            raise AssertionError("sound fixed-dual potential must be subadditive under exact split")
        if (U_low+U_high)*n<=ub*(n-1):
            stats["certified_shrinks"]+=1
        frontier.extend((high,low))
        stats["exact_split"]+=1
        emit({"expert":"BRANCH","variable":v,"U_before":ub,
              "U_after":U_low+U_high,"children":[U_low,U_high]})
    if verdict is None:
        verdict="UNSAT" if not frontier else "UNKNOWN_RESOURCE_LIMIT"
    stats["verdict"]=verdict
    stats["total_visited"]=prior+stats["visited_this_call"]
    stats["frontier_cubes"]=len(frontier)
    stats["frontier_bound"]=certified_frontier_mass(
        rows,frontier,moment_degree) if verdict!="SAT" else None
    if witness is not None:
        stats["witness_bits"]=witness
    if verdict=="UNKNOWN_RESOURCE_LIMIT" and checkpoint:
        rec={"version":1,"sha256":fingerprint(rows),
             "moment_degree":moment_degree,
             "log_kernel_exponent":log_kernel_exponent,
             "frontier":frontier,"total_visited":stats["total_visited"]}
        Path(checkpoint).write_text(json.dumps(rec,sort_keys=True),
                                    encoding="utf-8")
        stats["checkpoint_written"]=checkpoint
    return stats


def self_test():
    plane=fixtures()["AffinePlane9_SAT"]
    got=solve(plane,node_budget=4,moment_degree=1,log_kernel_exponent=3)
    assert got["verdict"]=="SAT" and valid_witness(plane,got["witness_bits"])
    assert got["initial_certified_U"]==3
    p=fixtures()["HolyerPetersen_UNSAT"]
    limited=solve(p,node_budget=1,moment_degree=3,log_kernel_exponent=1)
    assert limited["verdict"]=="UNKNOWN_RESOURCE_LIMIT"
    assert limited["initial_certified_U"]==480
    assert limited["exact_split"]==1 and limited["certified_shrinks"]==1
    assert limited["frontier_cubes"]==2 and limited["frontier_bound"]==467
    solved=solve(p,node_budget=1,moment_degree=3,log_kernel_exponent=3)
    assert solved["verdict"]=="UNSAT"
    assert solved["kernel_refuted"]==1 and solved["kernel_words_checked"]==4096
    assert solved["frontier_bound"]==0
    with TemporaryDirectory() as t:
        fp=str(Path(t)/"root.json")
        first=solve(p,node_budget=1,moment_degree=3,
                    log_kernel_exponent=1,checkpoint=fp)
        assert first["verdict"]=="UNKNOWN_RESOURCE_LIMIT"
        resumed=solve(p,node_budget=1,moment_degree=3,
                      log_kernel_exponent=1,resume=fp,checkpoint=fp)
        assert resumed["total_visited"]==2
        try:
            solve(plane,node_budget=1,moment_degree=3,
                  log_kernel_exponent=1,resume=fp)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong instance checksum accepted")
    return {
        "classification":"NATIVE_SCL_MOMENT_GEARBOX_FINITE_EXACT_CHECK",
        "AffinePlane9":{"U1":got["initial_certified_U"],"SAT":True},
        "Petersen45_moment3":{"root_U":480,"split_U":467,
                              "certified_progress":True,
                              "budget_1":"UNKNOWN"},
        "Petersen45_LOG_KERNEL_c3":{"verdict":"UNSAT",
                                   "words_checked":4096},
        "resume_check":"PASS",
        "universal_polynomial_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--fixture",choices=tuple(fixtures()))
    p.add_argument("--moment-degree",type=int,default=3)
    p.add_argument("--log-kernel-exponent",type=int,default=1)
    p.add_argument("--node-budget",type=int,default=80)
    p.add_argument("--resume")
    p.add_argument("--checkpoint")
    a=p.parse_args()
    if a.self_test:
        out=self_test()
    elif a.fixture:
        out=solve(fixtures()[a.fixture],node_budget=a.node_budget,
                  moment_degree=a.moment_degree,
                  log_kernel_exponent=a.log_kernel_exponent,
                  checkpoint=a.checkpoint,resume=a.resume)
    else:
        p.error("pass --self-test or --fixture")
    print(json.dumps(out,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
