#!/usr/bin/env python3
"""BABEL-18 exact lifted-degree1 lower bound plus rank2 orbit geometry."""
import json
from collections import Counter
from pathlib import Path
from janus_babel10_exact_lower import verify_document
from janus_babel10_degree_scan import character_products,frozen_instances
from janus_babel10_lift_family import make_lift
from janus_babel6_transfer import xor_labels
from janus_babel7_degree_audit import degree_witnesses
from rank2_geometry import restriction

def run():
    doc=json.loads(Path("babel10_SCL126_flip68_EXACT_DEGREE1_OBSTRUCTION.json").read_text())
    source_lower=verify_document(doc)
    assert source_lower["status"]=="EXACT_INTEGER_DEGREE1_NONMEMBERSHIP_PASS"
    source=frozen_instances()["SCL126_flip68"]
    src_labels,source_Q,d=xor_labels(source)
    _,_,_,supports=character_products(source,1)
    valid={tuple(sorted(x)) for x in supports}
    assert len(valid)==doc["distinct_generator_count"]
    outcomes=[]
    for seed in (0,4):
        lift=make_lift(source,seed)[0]
        labels,Q,D=xor_labels(lift)
        pi,kernel=restriction(src_labels,labels,d,D)
        assert len(kernel)==2
        group={0}
        for extra in kernel:group.update({q^extra for q in list(group)})
        assert len(group)==4
        base_degree1={0,*src_labels}
        unique=set()
        for r,row in enumerate(lift):
            src_row=source[r%len(source)]
            for u in [0,*labels]:
                p=pi(u)
                assert p in base_degree1
                v=tuple(sorted([p,*(p^pi(labels[j]) for j in row)]))
                w=tuple(sorted([p,*(p^src_labels[j] for j in src_row)]))
                assert v==w and v in valid
                unique.add(v)
        assert unique==valid
        active=degree_witnesses(labels,3)
        orbits={}
        for q in active:
            orbit=min(q^k for k in group)
            orbits[orbit]=orbits.get(orbit,0)+1
        q_orbits={}
        for q in Q:
            orbit=min(q^k for k in group)
            q_orbits[orbit]=q_orbits.get(orbit,0)+1
        record={"seed":seed,
           "source_degree1_lower_verdict":source_lower["status"],
           "lifted_degree1_products_checked":len(lift)*(len(labels)+1),
           "unique_projected_source_degree1_products":len(unique),
           "character_restriction_exact":True,
           "lifted_degree1_proof_excluded":True,
           "historical_polynomial_degree_lower_bound":4,
           "character_kernel_order":len(group),
           "degree3_unique_characters":len(active),
           "degree3_rank2_orbit_count":len(orbits),
           "degree3_orbit_occupancy_histogram":{str(k):v for k,v in sorted(Counter(orbits.values()).items())},
           "degree2_character_orbits":len(q_orbits),
           "degree2_orbit_occupancy_histogram":{str(k):v for k,v in sorted(Counter(q_orbits.values()).items())},
           "degree4_upper_bound_established":False,
           "status":"EXACT_LOWER_PLUS_ORBIT_AUDIT_PASS"}
        print("BABEL18_LOWER_ORBIT",json.dumps(record,sort_keys=True),flush=True)
        outcomes.append(record)
    Path("babel18_lower_orbit_checkpoint.json").write_text(json.dumps(outcomes,sort_keys=True,indent=2)+"\n")
if __name__=="__main__":run()
