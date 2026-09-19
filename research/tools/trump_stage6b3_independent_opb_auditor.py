#!/usr/bin/env python3
"""Independent Stage6B.3 PB24 semantic OPB auditor.

This implementation does not import or reuse the generator. Starting from the
canonical-CNF audit receipt and frozen boundary k, it independently reconstructs
the expected D/W0/W1/W2 mapping, exact PB24 constraint sequence, exact PB24
header fields, and intsize.

It verifies the emitted OPB byte-level semantics before RoundingSat may run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HEADER_RE = re.compile(
    r"^\*\s+#variable=\s*(\d+)\s+#constraint=\s*(\d+)\s+"
    r"#equal=\s*(\d+)\s+intsize=\s*(\d+)\s*$"
)
TERM_RE = re.compile(r"([+-]?\d+)\s+(x\d+)")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_mapping(vars_):
    out = {}
    n = 1
    for v in vars_:
        out[str(v)] = {
            "D": f"x{n}",
            "W0": f"x{n+1}",
            "W1": f"x{n+2}",
            "W2": f"x{n+3}",
        }
        n += 4
    return out


def constraint(terms, relation, rhs):
    return {
        "terms": [(int(c), str(n)) for c, n in terms],
        "relation": relation,
        "rhs": int(rhs),
    }


def constraint_intsize(c):
    magnitude = abs(int(c["rhs"])) + sum(abs(int(coeff)) for coeff, _ in c["terms"])
    return max(1, magnitude.bit_length())


def expected_from_audit(audit):
    if audit["status"] != "CANONICALIZATION_AUDIT_PASS":
        raise ValueError("canonicalization audit not PASS")
    if audit["complementary_pair_clause_count"] != 0:
        raise ValueError("complementary pair guard violated")

    vars_ = list(audit["variable_set"])
    mp = independent_mapping(vars_)
    exp = []

    # Equality constraints are unchanged.
    for v in vars_:
        m = mp[str(v)]
        exp.append(constraint(
            [(1, m[s]) for s in ("D", "W0", "W1", "W2")],
            "=",
            1,
        ))

    # Frozen semantic A <= 2 represented exactly as -A >= -2.
    for clause in audit["canonical_clauses"]:
        terms = []
        for lit in clause:
            m = mp[str(abs(lit))]
            terms.append((-1, m["W1"]))
            terms.append((-2, m["W2"] if lit > 0 else m["W0"]))
        exp.append(constraint(terms, ">=", -2))

    # Frozen semantic sum(D) <= k represented as -sum(D) >= -k.
    exp.append(constraint(
        [(-1, mp[str(v)]["D"]) for v in vars_],
        ">=",
        -int(audit["boundary_k"]),
    ))

    n_vars = 4 * len(vars_)
    n_constraints = len(exp)
    n_equal = sum(1 for c in exp if c["relation"] == "=")
    intsize = max(constraint_intsize(c) for c in exp) if exp else 1
    return mp, exp, {
        "variable": n_vars,
        "constraint": n_constraints,
        "equal": n_equal,
        "intsize": intsize,
    }


def parse_constraint(line):
    s = line.strip()
    if not s.endswith(";"):
        raise ValueError(f"missing semicolon: {line!r}")
    s = s[:-1].strip()

    if ">=" in s:
        lhs, rhs = s.rsplit(">=", 1)
        rel = ">="
    elif "=" in s:
        lhs, rhs = s.rsplit("=", 1)
        rel = "="
    elif "<=" in s:
        lhs, rhs = s.rsplit("<=", 1)
        rel = "<="
    else:
        raise ValueError(f"no supported relation: {line!r}")

    terms = [(int(c), n) for c, n in TERM_RE.findall(lhs)]
    residue = TERM_RE.sub("", lhs).strip()
    if residue not in ("", "0"):
        raise ValueError(f"unparsed lhs residue {residue!r}")
    return constraint(terms, rel, int(rhs.strip()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audit")
    ap.add_argument("opb")
    ap.add_argument("generator_receipt")
    ap.add_argument("output")
    ns = ap.parse_args()

    audit = json.loads(Path(ns.audit).read_text(encoding="utf-8"))
    gen = json.loads(Path(ns.generator_receipt).read_text(encoding="utf-8"))
    opbp = Path(ns.opb)
    text = opbp.read_text(encoding="utf-8")
    lines = text.splitlines()

    comment_lines = [line for line in lines if line.startswith("*")]
    body = [line for line in lines if line.strip() and not line.startswith("*")]
    objective_lines = [line for line in body if line.lstrip().startswith(("min:", "max:"))]

    mp, exp, expected_header = expected_from_audit(audit)

    parsed_header = None
    header_parse_error = None
    if len(comment_lines) != 1:
        header_parse_error = f"EXPECTED_EXACTLY_ONE_PB24_HEADER_GOT_{len(comment_lines)}"
    else:
        m = HEADER_RE.fullmatch(comment_lines[0])
        if not m:
            header_parse_error = "PB24_HEADER_SHAPE_MISMATCH"
        else:
            parsed_header = {
                "variable": int(m.group(1)),
                "constraint": int(m.group(2)),
                "equal": int(m.group(3)),
                "intsize": int(m.group(4)),
            }

    parsed = []
    parse_error = None
    try:
        parsed = [parse_constraint(line) for line in body if line not in objective_lines]
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"

    failures = []
    if header_parse_error:
        failures.append({"kind": "HEADER_PARSE_ERROR", "detail": header_parse_error})
    elif parsed_header != expected_header:
        failures.append({
            "kind": "PB24_HEADER_VALUE_MISMATCH",
            "actual": parsed_header,
            "expected": expected_header,
        })

    if objective_lines:
        failures.append({"kind": "OBJECTIVE_PRESENT", "lines": objective_lines})
    if parse_error:
        failures.append({"kind": "CONSTRAINT_PARSE_ERROR", "detail": parse_error})

    expected_variable_names = {
        name for states in mp.values() for name in states.values()
    }
    actual_variable_names = {
        name for c in parsed for _, name in c["terms"]
    } if not parse_error else set()

    if not parse_error and actual_variable_names != expected_variable_names:
        failures.append({
            "kind": "SERIALIZED_VARIABLE_SET_MISMATCH",
            "missing": sorted(
                expected_variable_names - actual_variable_names,
                key=lambda x: int(x[1:]),
            ),
            "extra": sorted(
                actual_variable_names - expected_variable_names,
                key=lambda x: int(x[1:]),
            ),
        })

    if not parse_error and parsed != exp:
        first = None
        for i in range(max(len(parsed), len(exp))):
            actual = parsed[i] if i < len(parsed) else None
            expected = exp[i] if i < len(exp) else None
            if actual != expected:
                first = {
                    "constraint_index": i,
                    "actual": actual,
                    "expected": expected,
                }
                break
        failures.append({
            "kind": "EXACT_CONSTRAINT_SEQUENCE_MISMATCH",
            "first_difference": first,
            "actual_count": len(parsed),
            "expected_count": len(exp),
        })

    independently_recomputed_intsize = (
        max(constraint_intsize(c) for c in parsed) if parsed else 1
    ) if not parse_error else None
    if (
        parsed_header is not None
        and independently_recomputed_intsize is not None
        and parsed_header["intsize"] != independently_recomputed_intsize
    ):
        failures.append({
            "kind": "INTSIZE_RECOMPUTATION_MISMATCH",
            "header_intsize": parsed_header["intsize"],
            "independently_recomputed_intsize": independently_recomputed_intsize,
        })

    # Generator metadata is checked only after independent reconstruction; it is
    # never used to define expected PB semantics.
    metadata_checks = {
        "mapping_matches": gen.get("mapping") == mp,
        "raw_hash_matches": gen.get("raw_cnf_sha256") == audit["raw_cnf_sha256"],
        "canonical_hash_matches": (
            gen.get("canonical_cnf_sha256") == audit["canonical_cnf_sha256"]
        ),
        "boundary_k_matches": gen.get("boundary_k") == audit["boundary_k"],
        "PB_variable_count_matches": gen.get("PB_variable_count") == expected_header["variable"],
        "constraint_count_matches": gen.get("constraint_count") == expected_header["constraint"],
        "equality_count_matches": gen.get("equality_count") == expected_header["equal"],
        "intsize_matches": gen.get("intsize") == expected_header["intsize"],
        "objective_absent": gen.get("objective_present") is False,
        "unauthorized_preprocessing_absent": (
            gen.get("unauthorized_preprocessing_applied") is False
        ),
    }
    for name, ok in metadata_checks.items():
        if not ok:
            failures.append({"kind": "GENERATOR_RECEIPT_MISMATCH", "field": name})

    coefficient_occurrence_count = (
        sum(len(c["terms"]) for c in parsed) if not parse_error else None
    )

    out = {
        "schema": "janus.trump.stage6b3.independent_pb24_semantic_audit.v2",
        "repair_prereg_commit": "4e6325491f1a862e7405c65dffde9d6bdd71b9d3",
        "index": audit["index"],
        "boundary_k": audit["boundary_k"],
        "PB24_SEMANTIC_AUDIT": "PASS" if not failures else "FAIL",
        "status": "OPB_SEMANTIC_AUDIT_PASS" if not failures else "INFRASTRUCTURE_ERROR",
        "raw_cnf_sha256": audit["raw_cnf_sha256"],
        "canonical_cnf_sha256": audit["canonical_cnf_sha256"],
        "OPB_sha256": sha(opbp),
        "expected_header": expected_header,
        "parsed_header": parsed_header,
        "intsize_independently_recomputed": independently_recomputed_intsize,
        "PB_variable_count": expected_header["variable"],
        "constraint_count": len(parsed) if not parse_error else None,
        "equality_count": expected_header["equal"],
        "coefficient_occurrence_count": coefficient_occurrence_count,
        "objective_present": bool(objective_lines),
        "exact_variable_mapping_verified": (
            not parse_error and actual_variable_names == expected_variable_names
        ),
        "exact_constraint_sequence_verified": (
            not parse_error and parsed == exp
        ),
        "qhorn_relation_rewrite_verified": (
            not parse_error
            and all(c["relation"] == ">=" for c in parsed[len(audit["variable_set"]):-1])
        ),
        "deletion_boundary_verified": (
            not parse_error and bool(parsed) and parsed[-1] == exp[-1]
        ),
        "canonical_cnf_hash_unchanged": gen.get("canonical_cnf_sha256") == audit["canonical_cnf_sha256"],
        "boundary_k_unchanged": gen.get("boundary_k") == audit["boundary_k"],
        "no_unauthorized_preprocessing_verified": not failures,
        "generator_metadata_cross_checks": metadata_checks,
        "failures": failures,
    }

    Path(ns.output).parent.mkdir(parents=True, exist_ok=True)
    Path(ns.output).write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "index": out["index"],
        "boundary_k": out["boundary_k"],
        "PB24_SEMANTIC_AUDIT": out["PB24_SEMANTIC_AUDIT"],
        "status": out["status"],
        "OPB_sha256": out["OPB_sha256"],
        "PB_variable_count": out["PB_variable_count"],
        "constraint_count": out["constraint_count"],
        "equality_count": out["equality_count"],
        "intsize": out["parsed_header"]["intsize"] if out["parsed_header"] else None,
    }, sort_keys=True))

    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
