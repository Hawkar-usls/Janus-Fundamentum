#!/usr/bin/env python3
"""Independent full Fourier coefficient replay for BABEL20 SCL21 certificates."""
import gzip,json,hashlib
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from noncover_scout import synthesize,valid
from janus_babel6_transfer import xor_labels

def verify(path):
    with gzip.open(path,"rt",encoding="utf-8") as f:record=json.load(f)
    assert record["format"]=="BABEL20_FULL_Q_SCL21_EXACT_MEMBERSHIP_CENSUS_V1"
    assert record["test_count"]==20
    output=[]
    for doc in record["cases"]:
        rows=synthesize(doc["seed"])
        assert valid(rows) and len(rows)==21
        sha=hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest()
        assert sha==doc["incidence_sha256"]
        labels,Q,d=xor_labels(rows)
        assert d==doc["nullity"] and doc["sat_count"]==0
        if doc["status"]=="FULL_Q_DEGREE2_EXPLICIT_POSITIVE_PASS":
            sums=defaultdict(Fraction)
            terms=doc["coefficient_terms"]
            assert len(terms)==doc["nonzero_terms"]
            for r,u,value in terms:
                assert 0<=r<21 and u in Q
                v=Fraction(value)
                assert v
                for j in (u,*(u^labels[a] for a in rows[r])):
                    sums[j]+=v
            assert {k:v for k,v in sums.items() if v}=={0:Fraction(1)},("replay failed",doc["seed"])
            verdict="EXACT_Q_ALL_FOURIER_COEFFICIENTS_PASS"
        elif doc["status"]=="FULL_Q_DEGREE2_EXACT_NEGATIVE_PASS":
            h={q:Fraction(v) for q,v in doc["left_kernel"]}
            assert h.get(0)==1
            for r,row in enumerate(rows):
                for u in Q:
                    assert sum(h.get(q,0) for q in (u,*(u^labels[a] for a in row)))==0
            verdict="EXACT_Q_ALL_GENERATOR_NULLSPACE_PASS"
        else:
            raise AssertionError(("unexpected unknown result",doc["seed"]))
        output.append({"seed":doc["seed"],"verdict":verdict,"num_terms":doc.get("nonzero_terms")})
        print("BABEL20_INDEPENDENT_SCL21_PASS",doc["seed"],verdict,flush=True)
    result={"gate":"BABEL20_INDEPENDENT_SCL21_Q_REPLAY",
      "cases_verified":len(output),"exact_positive":sum(v["verdict"]=="EXACT_Q_ALL_FOURIER_COEFFICIENTS_PASS" for v in output),
      "exact_negative":sum(v["verdict"]=="EXACT_Q_ALL_GENERATOR_NULLSPACE_PASS" for v in output),
      "all_exact_Q_checks_pass":True,
      "certificate_file_sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest(),
      "results":output}
    Path("babel20_SCL21_independent_replay.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("BABEL20_INDEPENDENT_SCL21_SUMMARY",json.dumps({k:v for k,v in result.items() if k!="results"},sort_keys=True),flush=True)
if __name__=="__main__":verify("babel20_SCL21_full_rational_census.json.gz")
