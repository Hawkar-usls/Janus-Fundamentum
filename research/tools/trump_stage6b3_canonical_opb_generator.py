#!/usr/bin/env python3
"""Stage6B.3 canonical PB24 OPB generator.

Consumes only a PASS canonical-CNF audit object. Uses standard OPB xN variable
names and emits an explicit mapping back to D/W0/W1/W2 states.

This is a serialization-only repair under the frozen Stage6B.3 contract:
  * the canonical CNF, variable mapping, boundary k, semantic constraints,
    and deterministic constraint order are unchanged;
  * semantic A <= b constraints are serialized exactly as -A >= -b;
  * the PB24 header is computed from the exact final serialized constraints.

No objective, no optimization, no preprocessing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def file_sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def state_mapping(vars_):
    mapping = {}
    next_id = 1
    for v in vars_:
        mapping[str(v)] = {}
        for state in ("D", "W0", "W1", "W2"):
            mapping[str(v)][state] = f"x{next_id}"
            next_id += 1
    return mapping


def normalized_constraint(terms, relation, rhs):
    """Keep exact serialized coefficient occurrences and deterministic order."""
    return {
        "terms": [(int(c), str(n)) for c, n in terms],
        "relation": relation,
        "rhs": int(rhs),
    }


def term(coeff, name):
    coeff = int(coeff)
    sign = "+" if coeff >= 0 else "-"
    return f"{sign}{abs(coeff)} {name}"


def serialize_constraint(c):
    terms = c["terms"]
    lhs = " ".join(term(coeff, name) for coeff, name in terms) if terms else "0"
    return f"{lhs} {c['relation']} {c['rhs']} ;"


def constraint_intsize(c):
    magnitude = abs(int(c["rhs"])) + sum(abs(int(coeff)) for coeff, _ in c["terms"])
    # PB24 definition: 1 + floor(log2(magnitude)); frozen minimum handling = 1.
    return max(1, magnitude.bit_length())


def emit(audit):
    if audit["status"] != "CANONICALIZATION_AUDIT_PASS":
        raise ValueError(f"canonicalization status is {audit['status']}")
    if audit["complementary_pair_clause_count"] != 0:
        raise ValueError("complementary pair guard violated")

    vars_ = list(audit["variable_set"])
    clauses = audit["canonical_clauses"]
    k = int(audit["boundary_k"])
    mp = state_mapping(vars_)

    constraints = []
    coefficient_occurrences = 0

    # Frozen exactly-one semantics; equality is serialized unchanged.
    for v in vars_:
        m = mp[str(v)]
        names = [m["D"], m["W0"], m["W1"], m["W2"]]
        terms = [(1, n) for n in names]
        constraints.append(normalized_constraint(terms, "=", 1))
        coefficient_occurrences += len(terms)

    # Frozen q-Horn semantics A <= 2, serialized exactly as -A >= -2.
    for clause in clauses:
        semantic_terms = []
        for lit in clause:
            m = mp[str(abs(lit))]
            semantic_terms.append((1, m["W1"]))
            semantic_terms.append((2, m["W2"] if lit > 0 else m["W0"]))
        wire_terms = [(-coeff, name) for coeff, name in semantic_terms]
        constraints.append(normalized_constraint(wire_terms, ">=", -2))
        coefficient_occurrences += len(wire_terms)

    # Frozen deletion semantics sum D_x <= k, serialized as -sum D_x >= -k.
    deletion_terms = [(-1, mp[str(v)]["D"]) for v in vars_]
    constraints.append(normalized_constraint(deletion_terms, ">=", -k))
    coefficient_occurrences += len(deletion_terms)

    variable_count = 4 * len(vars_)
    constraint_count = len(constraints)
    equality_count = sum(1 for c in constraints if c["relation"] == "=")
    intsize = max(constraint_intsize(c) for c in constraints) if constraints else 1

    if equality_count != len(vars_):
        raise AssertionError("PB24 equality count must equal original variable count")

    header = (
        f"* #variable= {variable_count} #constraint= {constraint_count} "
        f"#equal= {equality_count} intsize= {intsize}\n"
    )
    lines = [serialize_constraint(c) for c in constraints]
    body = header + "\n".join(lines) + "\n"

    return body, {
        "schema": "janus.trump.stage6b3.canonical_pb24_opb_generation_receipt.v2",
        "repair_prereg_commit": "4e6325491f1a862e7405c65dffde9d6bdd71b9d3",
        "index": audit["index"],
        "boundary_k": k,
        "raw_cnf_sha256": audit["raw_cnf_sha256"],
        "canonical_cnf_sha256": audit["canonical_cnf_sha256"],
        "mapping": mp,
        "original_variable_set": vars_,
        "PB_variable_count": variable_count,
        "constraint_count": constraint_count,
        "equality_count": equality_count,
        "intsize": intsize,
        "coefficient_occurrence_count": coefficient_occurrences,
        "exactly_one_constraint_count": len(vars_),
        "canonical_clause_constraint_count": len(clauses),
        "deletion_boundary_constraint_count": 1,
        "wire_relation_policy": {
            "exactly_one": "=",
            "qhorn_semantic_leq_2": "NEGATED_GE_NEG2",
            "deletion_semantic_leq_k": "NEGATED_GE_NEGK",
        },
        "serialized_constraints": constraints,
        "objective_present": False,
        "unauthorized_preprocessing_applied": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audit")
    ap.add_argument("opb")
    ap.add_argument("receipt")
    ns = ap.parse_args()

    audit = json.loads(Path(ns.audit).read_text(encoding="utf-8"))
    opb, receipt = emit(audit)
    opbp = Path(ns.opb)
    rp = Path(ns.receipt)
    opbp.parent.mkdir(parents=True, exist_ok=True)
    rp.parent.mkdir(parents=True, exist_ok=True)
    opbp.write_text(opb, encoding="utf-8")
    receipt["OPB_sha256"] = file_sha(opbp)
    receipt["OPB_bytes"] = opbp.stat().st_size
    rp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "index": receipt["index"],
        "k": receipt["boundary_k"],
        "OPB_sha256": receipt["OPB_sha256"],
        "PB_variable_count": receipt["PB_variable_count"],
        "constraint_count": receipt["constraint_count"],
        "equality_count": receipt["equality_count"],
        "intsize": receipt["intsize"],
        "coefficient_occurrence_count": receipt["coefficient_occurrence_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
