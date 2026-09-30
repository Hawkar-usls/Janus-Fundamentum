#!/usr/bin/env python3
"""Independent finite verifier for Backdoor-DNF certificates.

Input JSON:
{
  "formula": [[1,-2,3], ...],
  "terms": [
    {"assignment":{"1":true,"7":false}, "base":"HORN"},
    {"assignment":{"2":false}, "base":"KROM"}
  ]
}

Checks:
1. Every term is a consistent partial assignment.
2. Applying each term puts F into its declared allowed base (HORN/KROM/AUTO).
3. The DNF of terms is a tautology by exact enumeration over the union of
   variables mentioned by the terms.

This is a verifier only, not a detector. Enumeration cost is 2^u where u is
the number of distinct variables used by the certificate and is charged
explicitly in the receipt.
"""
from __future__ import annotations
import itertools, json, sys


def simplify(clauses, assignment):
    out=[]
    for clause in clauses:
        sat=False
        residual=[]
        for lit in clause:
            v=abs(lit)
            if v in assignment:
                val=assignment[v]
                if (lit>0 and val) or (lit<0 and not val):
                    sat=True
                    break
            else:
                residual.append(lit)
        if sat:
            continue
        out.append(residual)
    return out


def is_horn(F):
    return all(sum(l>0 for l in c)<=1 for c in F)


def is_krom(F):
    return all(len(c)<=2 for c in F)


def base_ok(F, base):
    b=base.upper()
    if b=="HORN":
        return is_horn(F)
    if b in ("KROM","2CNF"):
        return is_krom(F)
    if b in ("AUTO","HORN_OR_KROM","HORN+KROM"):
        return is_horn(F) or is_krom(F)
    raise ValueError(f"unsupported base {base!r}")


def term_satisfied(term, total):
    return all(total[v]==val for v,val in term.items())


def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: backdoor_dnf_verify.py certificate.json")
    data=json.load(open(sys.argv[1],encoding="utf-8"))
    F=[list(map(int,c)) for c in data["formula"]]
    parsed=[]
    term_rows=[]
    all_vars=set()

    for i,t in enumerate(data["terms"]):
        a={int(k):bool(v) for k,v in t["assignment"].items()}
        if len(a)!=len(t["assignment"]):
            raise AssertionError("duplicate/inconsistent assignment key")
        all_vars.update(a)
        R=simplify(F,a)
        ok=base_ok(R,t["base"])
        if not ok:
            raise AssertionError(("BASE_REPLAY_FAIL",i,t["base"]))
        parsed.append(a)
        term_rows.append({
            "term_index":i,
            "assigned_variables":len(a),
            "declared_base":t["base"],
            "residual_clauses":len(R),
            "base_replay":"PASS"
        })

    vars_sorted=sorted(all_vars)
    assignments_checked=0
    uncovered=None
    for bits in itertools.product((False,True),repeat=len(vars_sorted)):
        assignments_checked+=1
        total=dict(zip(vars_sorted,bits))
        if not any(term_satisfied(a,total) for a in parsed):
            uncovered=total
            break
    if uncovered is not None:
        raise AssertionError(("DNF_NOT_TAUTOLOGY",uncovered))

    print(json.dumps({
        "schema":"janus.public_backdoor_dnf_certificate_verifier.v1",
        "authority":"EXACT_FINITE_CERTIFICATE_REPLAY__NOT_A_DETECTOR",
        "term_count":len(parsed),
        "dnf_variable_count":len(vars_sorted),
        "tautology_assignments_checked":assignments_checked,
        "expected_full_enumeration":2**len(vars_sorted),
        "term_checks":term_rows,
        "verdict":"PASS_BACKDOOR_DNF_CERTIFICATE",
        "complexity_firewall":{
            "detector_runtime_not_assessed":True,
            "verification_cost":f"O(2^{len(vars_sorted)} * |F|) by direct finite replay",
            "polynomial_only_if_parameter_bound_makes_this_polynomial":True
        }
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
