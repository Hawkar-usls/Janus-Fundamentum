#!/usr/bin/env python3
"""Stage6B.3 canonical CNF audit.

Scientific role: deterministic provenance/canonicalization layer only.

Allowed transformation:
  remove duplicate occurrences of the same literal within a clause, preserving
  the first occurrence and original clause order.

Forbidden here:
  tautology removal, complementary-pair simplification, BCP, subsumption,
  pure-literal elimination, variable elimination, or any other preprocessing.

If any clause contains both x and -x, the target is marked
CANONICALIZATION_REQUIRES_SEPARATE_PREREG and no B.3 OPB may be generated.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

BOUNDARIES={1:24,2:31,3:25,4:28,5:22,6:27,7:22,9:31,10:31,11:31,12:31,13:31,14:31}


def jbytes(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode("utf-8")


def sha_obj(obj):
    return hashlib.sha256(jbytes(obj)).hexdigest()


def canonicalize_clause(raw):
    seen=set()
    canonical=[]
    removed=[]
    for pos,lit in enumerate(raw):
        if lit in seen:
            removed.append({"position":pos,"literal":lit})
        else:
            seen.add(lit)
            canonical.append(lit)
    comp=sorted({abs(l) for l in canonical if -l in seen})
    return canonical,removed,comp


def audit_one(row,index):
    raw=row["residual_formula"]
    transformed=[]
    canonical=[]
    duplicate_occurrences=0
    clauses_with_duplicates=[]
    complementary_indices=[]
    complementary_details=[]

    for ci,clause in enumerate(raw):
        can,removed,comp=canonicalize_clause(clause)
        canonical.append(can)
        duplicate_occurrences += len(removed)
        if removed:
            clauses_with_duplicates.append(ci)
            transformed.append({
              "clause_index":ci,
              "raw_clause":clause,
              "canonical_clause":can,
              "removed_duplicate_occurrences":removed,
              "raw_clause_sha256":sha_obj(clause),
              "canonical_clause_sha256":sha_obj(can)
            })
        if comp:
            complementary_indices.append(ci)
            complementary_details.append({
              "clause_index":ci,
              "variables_with_both_polarities":comp,
              "raw_clause":clause,
              "canonical_clause":can
            })

    variables=sorted({abs(l) for c in raw for l in c})
    status=("CANONICALIZATION_REQUIRES_SEPARATE_PREREG"
            if complementary_indices else "CANONICALIZATION_AUDIT_PASS")

    return {
      "schema":"janus.trump.stage6b3.canonical_cnf_audit.v1",
      "index":index,
      "boundary_k":BOUNDARIES[index],
      "family":row.get("family"),
      "source_residual_hash":row.get("residual_hash"),
      "status":status,
      "raw_cnf_sha256":sha_obj(raw),
      "canonical_cnf_sha256":sha_obj(canonical),
      "raw_clause_count":len(raw),
      "canonical_clause_count":len(canonical),
      "raw_literal_occurrence_count":sum(len(c) for c in raw),
      "canonical_literal_occurrence_count":sum(len(c) for c in canonical),
      "duplicate_literal_occurrence_count":duplicate_occurrences,
      "clauses_containing_duplicates":clauses_with_duplicates,
      "duplicate_transformation_receipts":transformed,
      "complementary_pair_clause_count":len(complementary_indices),
      "complementary_pair_clause_indices":complementary_indices,
      "complementary_pair_details":complementary_details,
      "variable_set":variables,
      "variable_count":len(variables),
      "canonical_clauses":canonical,
      "allowed_transformation_only":"REMOVE_DUPLICATE_LITERAL_OCCURRENCES_PRESERVE_FIRST_OCCURRENCE_AND_CLAUSE_ORDER",
      "unauthorized_preprocessing_applied":False
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("outdir")
    ap.add_argument("--indices",default="1,2,3,4,5,6,7,9,10,11,12,13,14")
    ns=ap.parse_args()

    data=json.loads(Path(ns.source).read_text(encoding="utf-8"))
    outdir=Path(ns.outdir); outdir.mkdir(parents=True,exist_ok=True)
    indices=[int(x) for x in ns.indices.split(",") if x.strip()]
    summary=[]
    for i in indices:
        obj=audit_one(data["residuals"][i],i)
        p=outdir/f"r50g25x_{i:02d}.canonical.json"
        p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        summary.append({
          "index":i,
          "status":obj["status"],
          "raw_cnf_sha256":obj["raw_cnf_sha256"],
          "canonical_cnf_sha256":obj["canonical_cnf_sha256"],
          "duplicate_literal_occurrence_count":obj["duplicate_literal_occurrence_count"],
          "complementary_pair_clause_count":obj["complementary_pair_clause_count"]
        })
        print(json.dumps(summary[-1],sort_keys=True),flush=True)
    (outdir/"summary.json").write_text(json.dumps({
      "schema":"janus.trump.stage6b3.canonical_cnf_audit_summary.v1",
      "rows":summary
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
