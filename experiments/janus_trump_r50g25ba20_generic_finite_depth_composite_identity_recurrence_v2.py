from __future__ import annotations
import argparse, json
from pathlib import Path
import janus_trump_r50g25ba20_generic_finite_depth_composite_identity_recurrence as base


def corrected_all2_affine_certificate():
    S=(2,-2);D=(5,0)
    C=(67*D[0]-2*S[0]-2,67*D[1]-1-2*S[1]-2-1)
    L=(163*D[0]-3*S[0]-4,163*D[1]-2-3*S[1]-4-2)
    V=(20*D[0],20*D[1]);N=(C[0]+L[0]+V[0],C[1]+L[1]+V[1])
    expected={"D":(5,0),"C":(329,0),"L":(805,-2),"V":(100,0),"n_struct":(1234,-2)}
    return {"S_prev":S,"D":D,"C":C,"L":L,"V":V,"n_struct":N,"expected":expected,
            "projected_clauses":"2^h","projected_width":"h+1",
            "exponential_relation":"2^h = 2^((n_struct+2)/1234)",
            "pass":D==expected["D"] and C==expected["C"] and L==expected["L"] and V==expected["V"] and N==expected["n_struct"]}


def run():
    base.all2_affine_certificate=corrected_all2_affine_certificate
    r=base.run()
    r["implementation_version"]="BA20_V2_PRE_RUN_AFFINE_TRANSCRIPTION_CORRECTED"
    r["implementation_hardening_commit"]="50a013bb8262c80b951f70fc27eec0105f1ca7ae"
    r["initial_implementation_commit_preserved"]="6e895880f2cebeddd0ee72d6b90704d62434bc67"
    return r


def main(out):
    r=run();Path(out).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("BA20_V2_FALSIFIERS="+json.dumps(r["falsifiers"],sort_keys=True))
    print("BA20_V2_FAILED_BUILDER_OBLIGATIONS="+json.dumps(r["failed_builder_obligations"],sort_keys=True))
    print("BA20_V2_ALL2="+json.dumps(r["all2_exponential_witness"],sort_keys=True))
    if r["falsifiers"] or r["failed_builder_obligations"]:raise SystemExit("BA20 v2 builder scientific obligation failure")

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args();main(a.out)
