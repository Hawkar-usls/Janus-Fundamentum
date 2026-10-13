#!/usr/bin/env python3
"""R5 proof-carrying SAT/UNSAT third-ply ISAACS flower gate.

Three conditional levels total: (outer bit x0=b) -> (candidate y=c)
-> exact source-certified single-literal failed-literal closure (z=0/1).
At a *fixed depth*, proven failed assumptions on y may be added to
the outer branch and the polynomial test iterated up to n times.

This is not unrestricted recursion, and no result of UNKNOWN is
silently upgraded to UNSAT. A branch refutation certificate retains
only the source-replayed failed-literal proofs that justify each
FORCE and the terminal double-refutation, not the huge sequence of
irrelevant inconclusive checks. A separate verifier replays each
retained original-source proof and every assumption discharge.

CI launches b=0 and b=1 as independent jobs. BOTH verified negative
branches discharge x0 to prove original source UNSAT. This source
specialization is not an all-SCL polynomial-time algorithm.
"""
from __future__ import annotations
import os
from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl
from r5_universal_certified_failed_literal_boolean_closure import (
    certified_failed_literal_closure, verify_probe_certificate,
    check_original_witness,
)


def verify_three_ply_branch(rows,n,outer_bit,report):
    assert outer_bit in (0,1)
    original={0:outer_bit}
    current=dict(original)
    done=False
    for event in report["events"]:
        kind=event["kind"]
        if kind=="FORCE":
            var=event["variable"]
            refuted=event["refuted_bit"]
            assert type(var) is int and 0<=var<n and var not in current
            assert refuted in (0,1)
            assumption={**current,var:refuted}
            assert verify_probe_certificate(rows,n,assumption,event["proof"])
            assert event["proof"]["status"]=="UNSAT"
            current[var]=1-refuted
        elif kind=="BASE_UNSAT":
            assert verify_probe_certificate(rows,n,current,event["proof"])
            assert event["proof"]["status"]=="UNSAT"
            assert event is report["events"][-1]
            assert report["status"]=="UNSAT"
            done=True
        elif kind=="DOUBLE_UNSAT":
            v=event["variable"]
            assert type(v) is int and 0<=v<n and v not in current
            proofs=event["proofs"]
            assert set(proofs)=={0,1}
            for bit in (0,1):
                assumption={**current,v:bit}
                assert verify_probe_certificate(rows,n,assumption,proofs[bit])
                assert proofs[bit]["status"]=="UNSAT"
            assert event is report["events"][-1]
            assert report["status"]=="UNSAT"
            done=True
        elif kind=="SAT_WITNESS":
            assert check_original_witness(rows,n,original,event["witness"])
            assert tuple(report["witness"])==tuple(event["witness"])
            assert report["status"]=="SAT"
            assert event is report["events"][-1]
            done=True
        else:
            raise AssertionError("forged third-ply event")
        if done:break
    if report["status"] in ("UNSAT","SAT"):
        assert done
    else:
        assert report["status"]=="UNKNOWN" and not done
    assert report["derived_pins"]==current
    return True


def certified_three_ply_branch(rows,n,outer_bit,max_probe_calls=0):
    """max_probe_calls=0 means ALL allowed polynomial probes, no cap.

    A nonzero cap is only a resource fence; reaching it returns UNKNOWN,
    never a false UNSAT. No n-dependent depth recursion.
    """
    assert outer_bit in (0,1)
    current={0:outer_bit}
    events=[]
    inner_calls=0
    outer_rounds=0
    while True:
        outer_rounds+=1
        assert outer_rounds<=n+1
        root=certified_failed_literal_closure(rows,n,current)
        inner_calls+=1
        assert verify_probe_certificate(rows,n,current,root)
        if root["status"]=="UNSAT":
            events.append({"kind":"BASE_UNSAT","proof":root})
            out={"status":"UNSAT","events":tuple(events),
                 "derived_pins":dict(current),"inner_calls":inner_calls,
                 "rounds":outer_rounds}
            assert verify_three_ply_branch(rows,n,outer_bit,out)
            return out
        if root["status"]=="SAT":
            assert check_original_witness(rows,n,current,root["witness"])
            events.append({"kind":"SAT_WITNESS","witness":root["witness"]})
            out={"status":"SAT","events":tuple(events),
                 "witness":root["witness"],"derived_pins":dict(current),
                 "inner_calls":inner_calls,"rounds":outer_rounds}
            assert verify_three_ply_branch(rows,n,outer_bit,out)
            return out
        assert root["status"]=="UNKNOWN"
        added=False
        for v in range(n):
            if v in current:continue
            outcome={}
            for bit in (0,1):
                trial={**current,v:bit}
                child=certified_failed_literal_closure(rows,n,trial)
                inner_calls+=1
                assert verify_probe_certificate(rows,n,trial,child)
                if child["status"]=="SAT":
                    assert check_original_witness(rows,n,current,child["witness"])
                    events.append({"kind":"SAT_WITNESS",
                                   "witness":child["witness"]})
                    out={"status":"SAT","events":tuple(events),
                         "witness":child["witness"],
                         "derived_pins":dict(current),
                         "inner_calls":inner_calls,"rounds":outer_rounds}
                    assert verify_three_ply_branch(rows,n,outer_bit,out)
                    return out
                outcome[bit]=child
            rejects=[b for b in (0,1) if outcome[b]["status"]=="UNSAT"]
            if len(rejects)==2:
                events.append({"kind":"DOUBLE_UNSAT",
                               "variable":v,"proofs":outcome})
                out={"status":"UNSAT","events":tuple(events),
                     "derived_pins":dict(current),
                     "inner_calls":inner_calls,"rounds":outer_rounds}
                assert verify_three_ply_branch(rows,n,outer_bit,out)
                return out
            if rejects:
                rejected=rejects[0]
                events.append({"kind":"FORCE","variable":v,
                               "refuted_bit":rejected,
                               "proof":outcome[rejected]})
                current[v]=1-rejected
                print(f"THREE_PLY_OUTER_{outer_bit}_FORCE x{v}={1-rejected} "
                      f"round={outer_rounds} calls={inner_calls}",flush=True)
                added=True
                break
            if max_probe_calls and inner_calls>=max_probe_calls:
                out={"status":"UNKNOWN","reason":"RESOURCE_FENCE",
                     "events":tuple(events),"derived_pins":dict(current),
                     "inner_calls":inner_calls,"rounds":outer_rounds}
                assert verify_three_ply_branch(rows,n,outer_bit,out)
                return out
        if not added:
            out={"status":"UNKNOWN","reason":"ALL_VARIABLES_INCONCLUSIVE",
                 "events":tuple(events),"derived_pins":dict(current),
                 "inner_calls":inner_calls,"rounds":outer_rounds}
            assert verify_three_ply_branch(rows,n,outer_bit,out)
            return out


def main():
    k=int(os.environ.get("FLOWER_K","5"))
    bit=int(os.environ.get("OUTER_BIT","0"))
    assert k in (5,7) and bit in (0,1)
    rows,n,edges,idx=make_scl(flower(k))
    from r5_universal_two_ply_flower_orbit_complete_gate import (
        certify_four_edge_orbits,
    )
    orbit=certify_four_edge_orbits(edges,k)
    assert sum(map(len,orbit))==len(edges)
    ans=certified_three_ply_branch(rows,n,bit)
    print(f"FLOWER_J{k}_THREE_PLY_X0_{bit}={ans['status']} "
          f"calls={ans['inner_calls']} rounds={ans['rounds']} "
          f"stored_certificate_events={len(ans['events'])}",flush=True)
    assert verify_three_ply_branch(rows,n,bit,ans)
    if ans["status"]=="UNSAT":
        # Forgery of a retained nested source proof MUST be rejected.
        ev=list(ans["events"])
        last=dict(ev[-1])
        if last["kind"]=="DOUBLE_UNSAT":
            pp=dict(last["proofs"])
            first=dict(pp[0])
            first["status"]="SAT"
            pp[0]=first
            last["proofs"]=pp
        else:
            first=dict(last["proof"])
            first["status"]="SAT"
            last["proof"]=first
        ev[-1]=last
        fake={**ans,"events":tuple(ev)}
        try:
            verify_three_ply_branch(rows,n,bit,fake)
        except (AssertionError,KeyError):
            print(f"FLOWER_J{k}_THREE_PLY_FORGED_UNSAT_REJECTED=PASS",
                  flush=True)
        else:
            raise AssertionError("tampered source proof accepted")
    print("FIXED_THREE_PLY_WITH_POLYNOMIAL_FORCED_LITERAL_RESTARTS=YES")
    print("J5_J7_GLOBAL_ALL_SCL_POLYNOMIAL_THEOREM=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
