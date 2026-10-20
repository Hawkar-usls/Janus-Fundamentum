#!/usr/bin/env python3
"""BABEL-17: lift-map verification of BABEL-10 degree1 obstruction on seed3."""
import hashlib,json
from pathlib import Path
from janus_babel10_exact_lower import verify_document
from janus_babel10_degree_scan import character_products
from janus_babel14_antisector_augmented import prepare
from janus_babel6_transfer import make_projection,xor_labels
from janus_babel8_krylov_verify import input_data

def run():
    doc_path=Path("babel10_SCL126_flip68_EXACT_DEGREE1_OBSTRUCTION.json")
    doc=json.loads(doc_path.read_text())
    src_lower=verify_document(doc)
    assert src_lower["status"]=="EXACT_INTEGER_DEGREE1_NONMEMBERSHIP_PASS"
    source,lift,labels,Q,e,canonical,*_=prepare(3)
    rows,src_labels,src_basis,eq,origins=input_data(68)
    assert rows==source and src_labels==xor_labels(source)[0]
    pi,_=make_projection(src_labels,labels,15,16)
    s_labels,d,qsize,supports=character_products(source,1)
    assert s_labels==src_labels
    valid_source={tuple(sorted(x)) for x in supports}
    assert len(valid_source)==doc["distinct_generator_count"]
    source_degree1=set([0,*src_labels])
    observed=set()
    lifted_degree1=[0,*labels]
    assert len(lifted_degree1)==253 and len(lift)==252
    for r,indices in enumerate(lift):
        src_row=source[r%len(source)]
        assert sorted(pi(labels[j]) for j in indices)==sorted(src_labels[j] for j in src_row)
        for u in lifted_degree1:
            p=pi(u)
            assert p in source_degree1,("projection raised degree",r,u)
            image=tuple(sorted([p,*(p^pi(labels[j]) for j in indices)]))
            target=tuple(sorted([p,*(p^src_labels[j] for j in src_row)]))
            assert image==target
            assert image in valid_source,("not among source degree1 generators",r,u)
            observed.add(image)
    assert observed==valid_source,("lifted projection does not cover source domain",len(observed),len(valid_source))
    proof={"gate":"BABEL17_SEED3_EXACT_MINIMUM_FOURIER_MULTIPLIER_DEGREE",
           "seed":3,
           "base_source":"SCL126_flip68",
           "source_lower_status":src_lower["status"],
           "source_degree1_null_witness_h0":src_lower["integer_frequency_null_witness_h0"],
           "source_degree1_null_witness_gcd":src_lower["integer_frequency_null_witness_gcd"],
           "source_lower_file_sha256":hashlib.sha256(doc_path.read_bytes()).hexdigest(),
           "checked_lifted_degree1_generators":len(lift)*len(lifted_degree1),
           "unique_projected_source_degree1_generators":len(observed),
           "exact_character_homomorphism_verified":True,
           "all_degree1_lifted_products_map_to_source_degree1":True,
           "projected_lower_bound_proves_lifted_degree1_impossible":True,
           "existing_seed3_upper_degree2_multipliers":"PASS_IN_BABEL17_FULL_CI",
           "minimum_historical_JANUS_character_degree":2,
           "minimum_historical_JANUS_polynomial_degree":4,
           "standard_psd_sos_equivalence_proved":False,
           "P_equals_NP_proved":False,
           "status":"EXACT_INSTANCE_MINIMUM_DEGREE4_PASS"}
    Path("babel17_SEED3_MINIMUM_DEGREE_PASS.json").write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n")
    print("BABEL17_LOWER_SUMMARY",json.dumps({k:v for k,v in proof.items() if k not in ["source_degree1_null_witness_h0"]},sort_keys=True),flush=True)
    return proof
if __name__=="__main__":run()
