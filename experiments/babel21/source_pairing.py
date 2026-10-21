#!/usr/bin/env python3
"""BABEL21 original SCL126_flip16 rational source proof + anti-residual pairing.

Uses immutable BABEL8 integer Krylov polynomial when present. Never upgrades
a conditional lift without an independently verified exact source identity.
"""
import argparse,json,gzip,hashlib
from pathlib import Path
from janus_babel8_krylov_verify import input_data,normal,verify
from janus_babel10_degree_scan import frozen_instances

def verify_source(base,seed):
    assert base=="SCL126_flip16"
    docpath=Path(f"babel21_{base}_seed{seed}_source_phi.json.gz")
    with gzip.open(docpath,"rt") as f:phi=json.load(f)
    candidates=[]
    for path in sorted(Path(".").glob("*.json")):
        if path.stat().st_size>4000000:continue
        try:
            obj=json.loads(path.read_text())
        except (UnicodeDecodeError,json.JSONDecodeError):continue
        if isinstance(obj,dict) and isinstance(obj.get("polynomial_coefficients_low_to_high"),list):
            candidates.append((path,obj.get("flipped_base_edge_index"),obj.get("format")))
    print("BABEL21_SOURCE_PROOF_CANDIDATES",[(p.name,b,f) for p,b,f in candidates],flush=True)
    suitable=[]
    for path,flip,fmt in candidates:
        if fmt=="BABEL8_INTEGER_KRYLOV_DEGREE4_CERTIFICATE_V1" and (flip is None or flip==16):
            suitable.append(path)
    if not suitable:
        result={"gate":"BABEL21_SOURCE_PROOF_PAIRING","base":base,"seed":seed,
         "status":"SOURCE_PROOF_DOCUMENT_NOT_PRESENT_IN_ARCHIVE",
         "rational_cover_degree4_existence":"NOT_PROVED"}
    else:
        sourcepath=suitable[0]
        verified=verify(sourcepath)
        assert verified["status"]=="BABEL8_EXACT_DEGREE4_RATIONAL_SOS_PASS"
        document=json.loads(sourcepath.read_text())
        poly=document["polynomial_coefficients_low_to_high"]
        rows,labels,basis,eq,origins=input_data(16)
        assert rows==frozen_instances()["SCL126_flip16"]
        v=[0]*32768
        for idx,k in enumerate(reversed(poly[1:])):
            v=normal(v,eq)
            v[0]+=k
        check=normal(v,eq)
        assert check[0]==-poly[0] and not any(check[1:])
        sign=-1 if poly[0]>0 else 1
        D=abs(poly[0])
        # Source certificate is one coefficient per distinct source-generator signature.
        coefficients={}
        for a,b,c,d in eq:
            k=sign*(v[a]+v[b]+v[c]+v[d])
            if k:
                coefficients[origins[(a,b,c,d)]]=k
        outputs=[]
        for component in phi["annihilator_representatives"]:
            P={(r,p):int(k) for r,p,k in component["source_phi_response"]}
            # For any source row-product representation of a given Fourier column
            # the response agrees because equal-source-column syzygies are annihilated.
            dot=sum(k*P.get(rp,0) for rp,k in coefficients.items())
            outputs.append({"component":component["component"],
                            "source_certificate_pairing":str(dot),
                            "target_compatible":dot==0,
                            "source_phi_nonzero":len(P)})
            print("BABEL21_EXACT_SOURCE_PAIRING",base,seed,json.dumps(outputs[-1],sort_keys=True),flush=True)
        result={"gate":"BABEL21_SOURCE_PROOF_PAIRING","base":base,"seed":seed,
         "status":"EXACT_KRYLOV_SOURCE_CERTIFICATE_VERIFIED",
         "source_proof_path":sourcepath.name,
         "source_proof_sha256":hashlib.sha256(sourcepath.read_bytes()).hexdigest(),
         "source_normal_operator_distinct_generator_count":len(eq),
         "source_certificate_nonzero_multiplier_count":len(coefficients),
         "source_normalization_digits":len(str(D)),
         "all_residual_directions_target_compatible":all(x["target_compatible"] for x in outputs),
         "remaining_components":outputs,
         "cover_degree4_existence_proved_by_target_test":all(x["target_compatible"] for x in outputs),
         "explicit_cover_coefficients_reconstructed":False,
         "P_vs_NP_proved":False}
    output=Path(f"babel21_{base}_seed{seed}_source_pairing.json")
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("BABEL21_SOURCE_PAIRING_VERDICT",json.dumps({k:v for k,v in result.items() if k!="remaining_components"},sort_keys=True),flush=True)
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--base",default="SCL126_flip16");a.add_argument("--seed",type=int,default=20)
    args=a.parse_args();verify_source(args.base,args.seed)
